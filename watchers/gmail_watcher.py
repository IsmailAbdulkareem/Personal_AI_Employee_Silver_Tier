"""
Gmail Watcher for AI Employee
Monitors Gmail for unread/important messages and creates action files
"""
import os
import base64
from pathlib import Path
from datetime import datetime
from email import message_from_bytes
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
import sys

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent))
from base_watcher import BaseWatcher

# Gmail API scopes
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly', 
          'https://www.googleapis.com/auth/gmail.labels']

# Keywords that indicate urgency
URGENT_KEYWORDS = ['urgent', 'asap', 'invoice', 'payment', 'help', 'emergency', 
                   'deadline', 'important', 'action required', 'respond']

class GmailWatcher(BaseWatcher):
    """Watcher that monitors Gmail for important/unread messages"""

    def __init__(self, vault_path: str, credentials_path: str = None, token_path: str = None):
        super().__init__(vault_path, check_interval=120)  # Check every 2 minutes
        
        # Default paths for credentials and token
        self.credentials_path = credentials_path or str(Path(__file__).parent.parent / 'config' / 'gmail_credentials.json')
        self.token_path = token_path or str(Path(__file__).parent.parent / 'config' / 'gmail_token.json')
        
        self.service = None
        self.processed_ids = set()
        self.label_id_map = {}
        
        # Ensure config directory exists
        Path(self.credentials_path).parent.mkdir(exist_ok=True)

    def authenticate(self) -> bool:
        """Authenticate with Gmail API"""
        creds = None
        
        # Load existing token if available
        if os.path.exists(self.token_path):
            creds = Credentials.from_authorized_user_file(self.token_path, SCOPES)
        
        # Refresh or create new credentials
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                try:
                    creds.refresh(Request())
                except Exception as e:
                    self.logger.error(f'Failed to refresh credentials: {e}')
                    return False
            else:
                if not os.path.exists(self.credentials_path):
                    self.logger.error(f'Credentials file not found: {self.credentials_path}')
                    self.logger.error('Please download Gmail API credentials from Google Cloud Console')
                    return False
                
                try:
                    flow = InstalledAppFlow.from_client_secrets_file(
                        self.credentials_path, SCOPES)
                    creds = flow.run_local_server(port=0, open_browser=False)
                    self.logger.info('Gmail authentication successful!')
                except Exception as e:
                    self.logger.error(f'Authentication failed: {e}')
                    return False
            
            # Save the credentials for next time
            try:
                with open(self.token_path, 'w') as token:
                    token.write(creds.to_json())
                self.logger.info(f'Token saved to: {self.token_path}')
            except Exception as e:
                self.logger.error(f'Failed to save token: {e}')
        
        # Build the Gmail service
        self.service = build('gmail', 'v1', credentials=creds)
        
        # Build label ID map
        self._build_label_map()
        
        return True

    def _build_label_map(self):
        """Build a map of label names to IDs"""
        try:
            results = self.service.users().labels().list(userId='me').execute()
            labels = results.get('labels', [])
            self.label_id_map = {label['name']: label['id'] for label in labels}
        except Exception as e:
            self.logger.error(f'Failed to build label map: {e}')

    def _get_label_id(self, label_name: str) -> str:
        """Get label ID by name"""
        return self.label_id_map.get(label_name)

    def check_for_updates(self) -> list:
        """Check for new unread/important emails"""
        if not self.service:
            if not self.authenticate():
                return []
        
        try:
            # Search for unread messages, optionally filter by importance
            # Using 'is:unread' to get only unread messages
            results = self.service.users().messages().list(
                userId='me',
                q='is:unread',
                maxResults=10
            ).execute()
            
            messages = results.get('messages', [])
            new_messages = []
            
            for message in messages:
                if message['id'] not in self.processed_ids:
                    # Get full message details
                    msg_details = self.service.users().messages().get(
                        userId='me', 
                        id=message['id'],
                        format='metadata',
                        metadataHeaders=['From', 'To', 'Subject', 'Date']
                    ).execute()
                    
                    new_messages.append(msg_details)
            
            return new_messages
            
        except Exception as e:
            self.logger.error(f'Error checking Gmail: {e}')
            # Try to re-authenticate on error
            if 'unauthorized' in str(e).lower() or 'token' in str(e).lower():
                if os.path.exists(self.token_path):
                    os.remove(self.token_path)
                    self.logger.info('Token removed, will re-authenticate on next check')
            return []

    def _extract_email_content(self, msg_details: dict) -> dict:
        """Extract full email content including body"""
        try:
            # Get full message with body
            message = self.service.users().messages().get(
                userId='me',
                id=msg_details['id'],
                format='full'
            ).execute()
            
            # Extract headers
            headers = {h['name']: h['value'] for h in message['payload']['headers']}
            
            # Extract body
            body = ''
            if 'parts' in message['payload']:
                # Multipart message
                for part in message['payload']['parts']:
                    if part['mimeType'] == 'text/plain' and 'data' in part['body']:
                        body_data = part['body']['data']
                        body = base64.urlsafe_b64decode(body_data).decode('utf-8', errors='ignore')
                        break
                    elif part['mimeType'] == 'text/html' and 'data' in part['body'] and not body:
                        body_data = part['body']['data']
                        body = base64.urlsafe_b64decode(body_data).decode('utf-8', errors='ignore')
            elif 'body' in message['payload'] and 'data' in message['payload']['body']:
                # Simple message
                body_data = message['payload']['body']['data']
                body = base64.urlsafe_b64decode(body_data).decode('utf-8', errors='ignore')
            
            # Truncate long bodies
            if len(body) > 2000:
                body = body[:2000] + '... [truncated]'
            
            return {
                'id': message['id'],
                'from': headers.get('From', 'Unknown'),
                'to': headers.get('To', 'Unknown'),
                'subject': headers.get('Subject', 'No Subject'),
                'date': headers.get('Date', 'Unknown'),
                'body': body,
                'snippet': message.get('snippet', '')
            }
            
        except Exception as e:
            self.logger.error(f'Error extracting email content: {e}')
            return {
                'id': msg_details['id'],
                'from': 'Unknown',
                'subject': 'Error reading email',
                'body': f'Could not extract content: {e}',
                'snippet': ''
            }

    def _calculate_priority(self, email: dict) -> str:
        """Calculate priority based on keywords and sender"""
        subject_lower = email['subject'].lower()
        from_lower = email['from'].lower()
        body_lower = email['body'].lower()
        
        # Check for urgent keywords
        for keyword in URGENT_KEYWORDS:
            if keyword in subject_lower or keyword in body_lower:
                return 'high'
        
        # Check if from important contacts (customize as needed)
        important_domains = ['client', 'company', 'business']  # Add your important contacts
        for domain in important_domains:
            if domain in from_lower:
                return 'high'
        
        return 'medium'

    def create_action_file(self, email: dict) -> Path:
        """Create a markdown file in Needs_Action for the email"""
        # Get full email content
        full_email = self._extract_email_content(email)
        
        # Calculate priority
        priority = self._calculate_priority(full_email)
        
        # Create filename with timestamp and sanitized subject
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        safe_subject = "".join(c for c in full_email['subject'][:30] if c.isalnum() or c in ' -_').strip()
        safe_subject = safe_subject.replace(' ', '_') or 'No_Subject'
        
        action_file = self.needs_action / f'EMAIL_{timestamp}_{safe_subject}.md'
        
        # Extract sender name
        sender = full_email['from']
        if '<' in sender:
            sender_name = sender.split('<')[0].strip()
            sender_email = sender.split('<')[1].strip('>')
        else:
            sender_name = sender
            sender_email = ''
        
        content = f"""---
type: email
message_id: {full_email['id']}
from: {full_email['from']}
from_name: {sender_name}
from_email: {sender_email}
to: {full_email['to']}
subject: {full_email['subject']}
received: {datetime.now().isoformat()}
original_date: {full_email['date']}
priority: {priority}
status: pending
labels: []
---

# Email: {full_email['subject']}

## Sender Information
- **From**: {full_email['from']}
- **To**: {full_email['to']}
- **Date**: {full_email['date']}

## Email Content

{full_email['body'] if full_email['body'] else full_email['snippet']}

---

## Suggested Actions

### Immediate Actions
- [ ] Read and understand the email
- [ ] Determine urgency and required response
- [ ] Draft response (requires approval before sending)

### Response Options
- [ ] Reply with information
- [ ] Forward to relevant party
- [ ] Schedule follow-up
- [ ] Archive after processing

### Notes
Add your response draft or notes here:


---

## Processing Log
- **Detected**: {datetime.now().isoformat()}
- **Priority**: {priority}
- **Status**: Pending review
"""
        
        action_file.write_text(content, encoding='utf-8')
        self.processed_ids.add(full_email['id'])
        
        self.logger.info(f'Created action file for email from {sender_name}: {action_file.name}')
        return action_file

    def mark_as_read(self, message_id: str) -> bool:
        """Mark an email as read"""
        try:
            if not self.service:
                if not self.authenticate():
                    return False
            
            self.service.users().messages().modify(
                userId='me',
                id=message_id,
                body={'removeLabelIds': ['UNREAD']}
            ).execute()
            return True
        except Exception as e:
            self.logger.error(f'Failed to mark email as read: {e}')
            return False

    def run(self):
        """Start the Gmail watcher"""
        self.logger.info(f'Starting GmailWatcher')
        self.logger.info(f'Credentials path: {self.credentials_path}')
        self.logger.info(f'Token path: {self.token_path}')
        self.logger.info(f'Check interval: {self.check_interval} seconds')
        
        # Authenticate on startup
        if not self.authenticate():
            self.logger.error('Failed to authenticate. Please ensure Gmail credentials are configured.')
            self.logger.error('Waiting for credentials file to be added...')
            # Wait and retry authentication every 5 minutes
            while not self.authenticate():
                time.sleep(300)
        
        self.logger.info('GmailWatcher started successfully. Monitoring for new emails...')
        
        # Call parent run method which has the main loop
        super().run()


if __name__ == '__main__':
    import time
    
    # Get vault path from command line or use default
    if len(sys.argv) > 1:
        vault_path = sys.argv[1]
    else:
        # Default to AI_Employee_Vault_Silver in parent directory
        vault_path = Path(__file__).parent.parent / 'AI_Employee_Vault_Silver'
    
    # Get credentials path from command line or use default
    credentials_path = sys.argv[2] if len(sys.argv) > 2 else None
    
    watcher = GmailWatcher(str(vault_path), credentials_path)
    watcher.run()
