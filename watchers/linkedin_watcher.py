"""
LinkedIn Watcher for AI Employee
Monitors LinkedIn for engagement opportunities and creates action files
"""
import time
import json
from pathlib import Path
from datetime import datetime
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout
import sys

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent))
from base_watcher import BaseWatcher

# Keywords that indicate sales/engagement opportunities
OPPORTUNITY_KEYWORDS = [
    'hiring', 'looking for', 'need help', 'recommend', 'suggestion',
    'seeking', 'opportunity', 'partnership', 'collaboration', 'freelance',
    'project', 'contract', 'service', 'solution', 'vendor', 'provider',
    'quote', 'proposal', 'budget', 'rfp', 'tender'
]

class LinkedInWatcher(BaseWatcher):
    """Watcher that monitors LinkedIn for engagement opportunities"""

    def __init__(self, vault_path: str, session_path: str = None, check_interval: int = 300):
        # LinkedIn checks less frequently to avoid rate limiting
        super().__init__(vault_path, check_interval)
        
        # Default session path
        self.session_path = Path(session_path) if session_path else Path(__file__).parent.parent / 'config' / 'linkedin_session'
        self.processed_posts = set()
        self.processed_messages = set()
        
        # Ensure session directory exists
        self.session_path.mkdir(parents=True, exist_ok=True)

    def _scan_linkedin_feed(self, page) -> list:
        """Scan LinkedIn feed for posts with opportunity keywords"""
        opportunities = []
        
        try:
            # Wait for feed to load
            try:
                page.wait_for_selector('[data-id="feed"]', timeout=15000)
            except PlaywrightTimeout:
                self.logger.warning('Feed not found, LinkedIn may not be loaded')
                return []
            
            # Give it a moment to fully load
            time.sleep(3)
            
            # Find all post containers
            post_containers = page.query_selector_all('div[data-id="feed"] ul[role="list"] > li')
            
            self.logger.info(f'Found {len(post_containers)} posts in feed')
            
            for idx, post in enumerate(post_containers[:15]):  # Limit to first 15 posts
                try:
                    # Get post text
                    text_elem = post.query_selector('span[dir="ltr"]')
                    if not text_elem:
                        continue
                    
                    post_text = text_elem.inner_text()
                    
                    # Skip very short posts
                    if len(post_text) < 50:
                        continue
                    
                    # Check for opportunity keywords
                    post_text_lower = post_text.lower()
                    matched_keywords = [kw for kw in OPPORTUNITY_KEYWORDS if kw in post_text_lower]
                    
                    if matched_keywords:
                        # Get author name
                        author_elem = post.query_selector('a[href*="/in/"] span[dir="ltr"]')
                        author = author_elem.inner_text() if author_elem else 'Unknown'
                        
                        # Get post engagement (likes, comments)
                        likes_elem = post.query_selector('button[aria-label*="Like"]')
                        comments_elem = post.query_selector('button[aria-label*="Comment"]')
                        
                        likes = likes_elem.inner_text() if likes_elem else '0'
                        comments = comments_elem.inner_text() if comments_elem else '0'
                        
                        opportunities.append({
                            'type': 'post',
                            'author': author,
                            'text': post_text[:500],  # Truncate for storage
                            'full_text': post_text,
                            'matched_keywords': matched_keywords,
                            'engagement': {'likes': likes, 'comments': comments},
                            'post_idx': idx
                        })
                        
                        self.logger.info(f'Found opportunity post by {author}: {matched_keywords}')
                    
                except Exception as e:
                    self.logger.debug(f'Error processing post {idx}: {e}')
                    continue
            
            return opportunities
            
        except Exception as e:
            self.logger.error(f'Error scanning LinkedIn feed: {e}')
            return []

    def _scan_linkedin_messages(self, page) -> list:
        """Scan LinkedIn messages for urgent communications"""
        messages = []
        
        try:
            # Navigate to messaging
            try:
                page.goto('https://www.linkedin.com/messaging/', wait_until='networkidle', timeout=30000)
                time.sleep(2)
                
                # Wait for message list
                page.wait_for_selector('[data-message-id]', timeout=10000)
            except PlaywrightTimeout:
                self.logger.warning('Could not access LinkedIn messaging')
                return []
            
            # Find conversation threads
            conversations = page.query_selector_all('ul[aria-label*="conversation"] > li')
            
            for conv in conversations[:10]:  # Limit to 10 conversations
                try:
                    # Get conversation details
                    name_elem = conv.query_selector('span[dir="ltr"]')
                    preview_elem = conv.query_selector('span[aria-hidden="true"]')
                    
                    if not name_elem:
                        continue
                    
                    name = name_elem.inner_text()
                    preview = preview_elem.inner_text() if preview_elem else ''
                    
                    # Check for urgent keywords
                    preview_lower = preview.lower()
                    matched_keywords = [kw for kw in OPPORTUNITY_KEYWORDS if kw in preview_lower]
                    
                    # Also check for urgency
                    urgent_keywords = ['urgent', 'asap', 'meeting', 'call', 'interview']
                    has_urgent = any(kw in preview_lower for kw in urgent_keywords)
                    
                    if matched_keywords or has_urgent:
                        messages.append({
                            'type': 'message',
                            'from': name,
                            'preview': preview,
                            'matched_keywords': matched_keywords,
                            'has_urgent': has_urgent
                        })
                        
                        self.logger.info(f'Found LinkedIn message from {name}: {preview[:50]}...')
                    
                except Exception as e:
                    self.logger.debug(f'Error processing conversation: {e}')
                    continue
            
            return messages
            
        except Exception as e:
            self.logger.error(f'Error scanning LinkedIn messages: {e}')
            return []

    def check_for_updates(self) -> list:
        """Check LinkedIn for new opportunities and messages"""
        all_items = []
        
        try:
            with sync_playwright() as p:
                # Launch browser with persistent context
                browser = p.chromium.launch_persistent_context(
                    str(self.session_path),
                    headless=True,
                    args=[
                        '--no-sandbox',
                        '--disable-setuid-sandbox',
                        '--disable-dev-shm-usage',
                        '--disable-accelerated-2d-canvas',
                        '--disable-gpu',
                        '--window-size=1920,1080'
                    ]
                )
                
                page = browser.pages[0] if browser.pages else browser.new_page()
                
                # Navigate to LinkedIn
                self.logger.info('Navigating to LinkedIn...')
                page.goto('https://www.linkedin.com/feed/', wait_until='networkidle', timeout=60000)
                
                # Check if logged in
                try:
                    page.wait_for_selector('[data-id="feed"]', timeout=10000)
                    self.logger.info('LinkedIn feed loaded successfully')
                except PlaywrightTimeout:
                    # Check if we're at login page
                    if 'login' in page.url.lower():
                        self.logger.error('Not logged in to LinkedIn. Please log in manually.')
                        self.logger.error(f'Session will be saved to: {self.session_path}')
                        browser.close()
                        return []
                    else:
                        self.logger.warning('Could not detect LinkedIn feed')
                        browser.close()
                        return []
                
                # Scan feed for opportunities
                feed_opportunities = self._scan_linkedin_feed(page)
                
                # Scan messages
                messages = self._scan_linkedin_messages(page)
                
                # Combine results
                all_items = feed_opportunities + messages
                
                # Filter out already processed items
                new_items = []
                for item in all_items:
                    if item['type'] == 'post':
                        item_key = f"post_{item['author']}_{item['post_idx']}"
                    else:
                        item_key = f"message_{item['from']}_{datetime.now().strftime('%Y%m%d')}"
                    
                    if item_key not in self.processed_posts and item_key not in self.processed_messages:
                        new_items.append(item)
                        if item['type'] == 'post':
                            self.processed_posts.add(item_key)
                        else:
                            self.processed_messages.add(item_key)
                
                # Limit processed items to avoid memory growth
                if len(self.processed_posts) > 100:
                    self.processed_posts = set(list(self.processed_posts)[-50:])
                if len(self.processed_messages) > 50:
                    self.processed_messages = set(list(self.processed_messages)[-25:])
                
                browser.close()
                
        except Exception as e:
            self.logger.error(f'Error in LinkedIn watcher: {e}')
        
        return new_items

    def create_action_file(self, item: dict) -> Path:
        """Create a markdown file in Needs_Action for the LinkedIn item"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        if item['type'] == 'post':
            safe_author = "".join(c for c in item['author'][:30] if c.isalnum() or c in ' -_').strip()
            safe_author = safe_author.replace(' ', '_') or 'Unknown'
            action_file = self.needs_action / f'LINKEDIN_POST_{timestamp}_{safe_author}.md'
            
            priority = 'high' if len(item['matched_keywords']) > 2 else 'medium'
            
            content = f"""---
type: linkedin_post
author: {item['author']}
detected: {datetime.now().isoformat()}
priority: {priority}
status: pending
matched_keywords: {', '.join(item['matched_keywords'])}
engagement_likes: {item['engagement']['likes']}
engagement_comments: {item['engagement']['comments']}
---

# LinkedIn Opportunity: Post by {item['author']}

## Post Details
- **Author**: {item['author']}
- **Detected**: {datetime.now().isoformat()}
- **Priority**: {priority}
- **Engagement**: {item['engagement']['likes']} likes, {item['engagement']['comments']} comments

## Matched Keywords
{', '.join(item['matched_keywords'])}

## Post Content

> {item['text']}

---

## Suggested Actions

### Engagement Options
- [ ] Like the post
- [ ] Comment with helpful insight
- [ ] Share with network
- [ ] Send connection request to author
- [ ] Draft follow-up message

### Sales Opportunity
This post may represent a business opportunity. Consider:
- Does the author need your services?
- Can you provide value in the comments?
- Should you reach out directly?

### Response Draft
Draft your comment or message here:


---

## Processing Log
- **Detected**: {datetime.now().isoformat()}
- **Priority**: {priority}
- **Status**: Pending review
"""
        
        else:  # message
            safe_from = "".join(c for c in item['from'][:30] if c.isalnum() or c in ' -_').strip()
            safe_from = safe_from.replace(' ', '_') or 'Unknown'
            action_file = self.needs_action / f'LINKEDIN_MSG_{timestamp}_{safe_from}.md'
            
            priority = 'high' if item['has_urgent'] else 'medium'
            
            content = f"""---
type: linkedin_message
from: {item['from']}
detected: {datetime.now().isoformat()}
priority: {priority}
status: pending
matched_keywords: {', '.join(item['matched_keywords']) if item['matched_keywords'] else 'none'}
has_urgent: {str(item['has_urgent'])}
---

# LinkedIn Message: {item['from']}

## Message Details
- **From**: {item['from']}
- **Detected**: {datetime.now().isoformat()}
- **Priority**: {priority}
- **Urgent**: {'Yes' if item['has_urgent'] else 'No'}

## Matched Keywords
{', '.join(item['matched_keywords']) if item['matched_keywords'] else 'None detected'}

## Message Preview

> {item['preview']}

---

## Suggested Actions

### Immediate Actions
- [ ] Read full message in LinkedIn
- [ ] Determine response needed
- [ ] Draft response (requires approval)

### Response Options
- [ ] Reply via LinkedIn (requires approval)
- [ ] Schedule call/meeting
- [ ] Forward to team member
- [ ] Archive after processing

### Response Draft
Draft your response here:


---

## Processing Log
- **Detected**: {datetime.now().isoformat()}
- **Priority**: {priority}
- **Status**: Pending review
"""
        
        action_file.write_text(content, encoding='utf-8')
        
        self.logger.info(f'Created action file for LinkedIn {item["type"]} from {item.get("author", item.get("from", "Unknown"))}: {action_file.name}')
        return action_file

    def run(self):
        """Start the LinkedIn watcher"""
        self.logger.info(f'Starting LinkedInWatcher')
        self.logger.info(f'Session path: {self.session_path}')
        self.logger.info(f'Check interval: {self.check_interval} seconds (5 min recommended)')
        self.logger.info('First run will require manual login')
        
        self.logger.info('LinkedInWatcher started. Monitoring for opportunities...')
        
        # Call parent run method which has the main loop
        super().run()


if __name__ == '__main__':
    # Get vault path from command line or use default
    if len(sys.argv) > 1:
        vault_path = sys.argv[1]
    else:
        # Default to AI_Employee_Vault_Silver in parent directory
        vault_path = Path(__file__).parent.parent / 'AI_Employee_Vault_Silver'
    
    # Get session path from command line or use default
    session_path = sys.argv[2] if len(sys.argv) > 2 else None
    
    watcher = LinkedInWatcher(str(vault_path), session_path)
    watcher.run()
