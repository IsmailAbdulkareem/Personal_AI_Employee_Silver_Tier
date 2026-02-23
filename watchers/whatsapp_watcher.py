"""
WhatsApp Watcher for AI Employee
Monitors WhatsApp Web for urgent messages using Playwright
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

# Keywords that indicate urgency
URGENT_KEYWORDS = ['urgent', 'asap', 'invoice', 'payment', 'help', 'emergency', 
                   'deadline', 'important', 'money', 'transfer', 'bank']

class WhatsAppWatcher(BaseWatcher):
    """Watcher that monitors WhatsApp Web for urgent messages"""

    def __init__(self, vault_path: str, session_path: str = None, check_interval: int = 60):
        super().__init__(vault_path, check_interval)
        
        # Default session path
        self.session_path = Path(session_path) if session_path else Path(__file__).parent.parent / 'config' / 'whatsapp_session'
        self.processed_chats = set()
        self.last_message_time = {}
        
        # Ensure session directory exists
        self.session_path.mkdir(parents=True, exist_ok=True)

    def _scan_whatsapp_web(self, page) -> list:
        """Scan WhatsApp Web for unread messages with urgent keywords"""
        urgent_messages = []
        
        try:
            # Wait for chat list to load
            try:
                page.wait_for_selector('[data-testid="chat-list"]', timeout=10000)
            except PlaywrightTimeout:
                self.logger.warning('Chat list not found, WhatsApp Web may not be loaded')
                return []
            
            # Give it a moment to fully load
            time.sleep(2)
            
            # Find all chat items
            chat_items = page.query_selector_all('[data-testid="chat-list"] > div')
            
            self.logger.info(f'Found {len(chat_items)} chats')
            
            for idx, chat in enumerate(chat_items[:20]):  # Limit to first 20 chats
                try:
                    # Get chat name
                    name_elem = chat.query_selector('[data-testid="chat-list"] [dir="auto"]')
                    if not name_elem:
                        name_elem = chat.query_selector('span[title]')
                    chat_name = name_elem.inner_text() if name_elem else 'Unknown'
                    
                    # Get last message
                    msg_elem = chat.query_selector('span[data-testid="last-message-content"]')
                    if not msg_elem:
                        msg_elem = chat.query_selector('[data-testid="chat-list"] span[dir="auto"]')
                    
                    if not msg_elem:
                        continue
                        
                    last_message = msg_elem.inner_text().lower()
                    
                    # Check for unread indicator
                    unread_badge = chat.query_selector('[data-testid="unread-chat-msg-count"]')
                    is_unread = unread_badge is not None
                    
                    # Check for urgent keywords
                    has_urgent_keyword = any(keyword in last_message for keyword in URGENT_KEYWORDS)
                    
                    # Also check chat name for urgency
                    has_urgent_name = any(keyword in chat_name.lower() for keyword in URGENT_KEYWORDS)
                    
                    if is_unread or has_urgent_keyword or has_urgent_name:
                        # Get timestamp if available
                        time_elem = chat.query_selector('span[data-testid="chat-list-time"]')
                        timestamp = time_elem.inner_text() if time_elem else 'Unknown'
                        
                        urgent_messages.append({
                            'chat_name': chat_name,
                            'last_message': last_message,
                            'timestamp': timestamp,
                            'is_unread': is_unread,
                            'has_urgent_keyword': has_urgent_keyword or has_urgent_name,
                            'element_idx': idx
                        })
                        
                        self.logger.info(f'Found urgent chat: {chat_name} - {last_message[:50]}...')
                    
                except Exception as e:
                    self.logger.debug(f'Error processing chat {idx}: {e}')
                    continue
            
            return urgent_messages
            
        except Exception as e:
            self.logger.error(f'Error scanning WhatsApp: {e}')
            return []

    def check_for_updates(self) -> list:
        """Check WhatsApp Web for new urgent messages"""
        urgent_messages = []
        
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
                
                # Navigate to WhatsApp Web
                self.logger.info('Navigating to WhatsApp Web...')
                page.goto('https://web.whatsapp.com', wait_until='networkidle', timeout=60000)
                
                # Wait for page to load (check for main container)
                try:
                    page.wait_for_selector('[data-testid="default-user"]', timeout=30000)
                    self.logger.info('WhatsApp Web loaded successfully')
                except PlaywrightTimeout:
                    # Check if we're at the QR code page
                    qr_present = page.is_visible('[data-testid="qr-container"]')
                    if qr_present:
                        self.logger.warning('QR code scan required. Please scan QR code in WhatsApp Web.')
                        self.logger.warning(f'Session will be saved to: {self.session_path}')
                        # Wait for QR scan (up to 2 minutes)
                        try:
                            page.wait_for_selector('[data-testid="default-user"]', timeout=120000)
                            self.logger.info('QR code scanned successfully!')
                        except PlaywrightTimeout:
                            self.logger.error('QR code scan timeout. Please run again and scan the QR code.')
                            browser.close()
                            return []
                    else:
                        self.logger.warning('Could not detect WhatsApp Web main interface')
                        browser.close()
                        return []
                
                # Small delay to ensure everything is loaded
                time.sleep(3)
                
                # Scan for urgent messages
                urgent_messages = self._scan_whatsapp_web(page)
                
                # Filter out already processed messages
                new_messages = []
                for msg in urgent_messages:
                    chat_key = f"{msg['chat_name']}_{msg['timestamp']}"
                    if chat_key not in self.processed_chats:
                        new_messages.append(msg)
                        self.processed_chats.add(chat_key)
                        self.last_message_time[msg['chat_name']] = datetime.now()
                
                # Limit processed chats to avoid memory growth
                if len(self.processed_chats) > 100:
                    self.processed_chats = set(list(self.processed_chats)[-50:])
                
                browser.close()
                
        except Exception as e:
            self.logger.error(f'Error in WhatsApp watcher: {e}')
            # If it's a profile issue, suggest clearing session
            if 'profile' in str(e).lower() or 'directory' in str(e).lower():
                self.logger.error('Try deleting the session folder and re-authenticating')
        
        return new_messages

    def create_action_file(self, message: dict) -> Path:
        """Create a markdown file in Needs_Action for the WhatsApp message"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        safe_chat_name = "".join(c for c in message['chat_name'][:30] if c.isalnum() or c in ' -_').strip()
        safe_chat_name = safe_chat_name.replace(' ', '_') or 'Unknown'
        
        action_file = self.needs_action / f'WHATSAPP_{timestamp}_{safe_chat_name}.md'
        
        priority = 'high' if message['has_urgent_keyword'] else 'medium'
        
        content = f"""---
type: whatsapp
chat_name: {message['chat_name']}
message_preview: {message['last_message'][:100]}
received: {datetime.now().isoformat()}
whatsapp_timestamp: {message['timestamp']}
priority: {priority}
status: pending
is_unread: {str(message['is_unread'])}
---

# WhatsApp Message: {message['chat_name']}

## Message Details
- **Chat**: {message['chat_name']}
- **Time**: {message['timestamp']}
- **Priority**: {priority}
- **Status**: {'Unread' if message['is_unread'] else 'Read'}

## Message Content

> {message['last_message']}

---

## Urgency Analysis

{'**URGENT**: This message contains urgent keywords!' if message['has_urgent_keyword'] else '**Normal Priority**: No urgent keywords detected.'}

Detected keywords: {[kw for kw in URGENT_KEYWORDS if kw in message['last_message'].lower()]}

---

## Suggested Actions

### Immediate Actions
- [ ] Review the message content
- [ ] Determine if response is needed
- [ ] Draft response (requires approval before sending)

### Response Options
- [ ] Reply via WhatsApp (requires approval)
- [ ] Forward to email for tracking
- [ ] Schedule follow-up
- [ ] Mark as handled

### Notes
Add your response draft or notes here:


---

## Processing Log
- **Detected**: {datetime.now().isoformat()}
- **Priority**: {priority}
- **Status**: Pending review
"""
        
        action_file.write_text(content, encoding='utf-8')
        
        self.logger.info(f'Created action file for WhatsApp from {message["chat_name"]}: {action_file.name}')
        return action_file

    def run(self):
        """Start the WhatsApp watcher"""
        self.logger.info(f'Starting WhatsAppWatcher')
        self.logger.info(f'Session path: {self.session_path}')
        self.logger.info(f'Check interval: {self.check_interval} seconds')
        self.logger.info('First run will require QR code scan')
        
        self.logger.info('WhatsAppWatcher started. Monitoring for urgent messages...')
        
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
    
    watcher = WhatsAppWatcher(str(vault_path), session_path)
    watcher.run()
