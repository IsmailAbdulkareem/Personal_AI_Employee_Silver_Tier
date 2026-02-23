# WhatsApp Watcher Setup Guide

This guide will help you set up the WhatsApp Watcher for your AI Employee.

## ⚠️ Important Notice

This watcher uses **WhatsApp Web** automation via Playwright. Be aware of:
- WhatsApp's Terms of Service
- Rate limiting (don't check too frequently)
- Privacy considerations

## Prerequisites

- Python 3.13+
- WhatsApp account with phone number
- Chromium browser (will be installed automatically)

## Step 1: Install Dependencies

```bash
cd Personal_AI_Employee_Silver_Tier/watchers
pip install -r requirements.txt

# Install Playwright browsers
playwright install chromium
```

## Step 2: First-Time Authentication

Run the WhatsApp Watcher:

```bash
python watchers/whatsapp_watcher.py
```

On first run:
1. The watcher will launch WhatsApp Web in headless mode
2. You'll see a message: "QR code scan required"
3. To scan the QR code, you have two options:

### Option A: Use the Session Folder
1. Run the watcher once to create the session folder
2. Open WhatsApp Web manually in your browser: https://web.whatsapp.com
3. Scan the QR code with your phone
4. The session will be saved and the watcher can use it

### Option B: Temporary Headed Mode
For debugging, you can modify the watcher to show the browser:

```python
# In whatsapp_watcher.py, change:
browser = p.chromium.launch_persistent_context(
    str(self.session_path),
    headless=False,  # Change to False to see the browser
    ...
)
```

## Step 3: Test the Watcher

1. Send yourself a WhatsApp message with "urgent" or "payment"
2. The watcher should detect it within 60 seconds
3. Check `AI_Employee_Vault_Silver/Needs_Action/` for a new file

## How It Works

1. **Session Persistence**: The watcher uses a persistent Chromium profile
2. **QR Code**: Only needed once, then the session is saved
3. **Keyword Detection**: Only messages with urgent keywords create action files
4. **Duplicate Prevention**: Already-processed messages are tracked

## Urgent Keywords

The watcher looks for these keywords (case-insensitive):
- urgent
- asap
- invoice
- payment
- help
- emergency
- deadline
- important
- money
- transfer
- bank

You can customize these in `whatsapp_watcher.py`:

```python
URGENT_KEYWORDS = ['urgent', 'asap', 'invoice', 'payment', 
                   'help', 'emergency', 'deadline', 'important', 
                   'money', 'transfer', 'bank', 'your_keyword']
```

## Troubleshooting

### "QR code scan required" every time
- Session may not be saving properly
- Check that `config/whatsapp_session/` folder exists and is writable
- Try running with `headless=False` to debug

### "Chat list not found"
- WhatsApp Web may not be fully loaded
- Increase timeout in the code
- Check your internet connection

### Browser crashes
- Close any other Chromium/Chrome instances
- Delete the session folder and re-authenticate
- Try with `headless=False` to see what's happening

### No messages detected
- Ensure messages are unread or contain urgent keywords
- Check that WhatsApp Web is working in your browser
- Verify the watcher is running

## Session Management

### Location
```
Personal_AI_Employee_Silver_Tier/config/whatsapp_session/
```

### Clear Session
To log out and re-authenticate:
```bash
rm -rf config/whatsapp_session
```

### Backup Session
To backup your authenticated session:
```bash
cp -r config/whatsapp_session config/whatsapp_session_backup
```

## Security Notes

- **Never commit** the `whatsapp_session/` folder to Git
- This folder is already in `.gitignore`
- The session contains access to your WhatsApp
- Keep your computer secure

## Performance Tips

### Adjust Check Interval
```python
# In whatsapp_watcher.py constructor:
super().__init__(vault_path, check_interval=60)  # Check every 60 seconds
```

Recommended: 60-120 seconds (don't check too frequently)

### Limit Chat Scanning
```python
# In _scan_whatsapp_web method:
for idx, chat in enumerate(chat_items[:20]):  # Limit to first 20 chats
```

## Running in Background

### Linux/Mac
```bash
nohup python watchers/whatsapp_watcher.py &
```

### Windows (PowerShell)
```powershell
Start-Process python -ArgumentList "watchers/whatsapp_watcher.py" -WindowStyle Hidden
```

## Integration with Orchestrator

The WhatsApp Watcher integrates with the main orchestrator:

```bash
# Run alongside other watchers
python watchers/filesystem_watcher.py &
python watchers/gmail_watcher.py &
python watchers/whatsapp_watcher.py &
```

## Next Steps

After WhatsApp Watcher is working:
1. Test with different urgent keywords
2. Customize keyword list for your needs
3. Set up LinkedIn Watcher
4. Configure MCP servers for responses

---

For more information, see [SILVER_TIER_PLAN.md](../SILVER_TIER_PLAN.md)
