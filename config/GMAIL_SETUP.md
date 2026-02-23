# Gmail Watcher Setup Guide

This guide will help you set up the Gmail Watcher for your AI Employee.

## Prerequisites

- Python 3.13+
- Google account with Gmail
- Google Cloud Console access

## Step 1: Create a Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Click **Select a project** → **New Project**
3. Name it: `AI Employee Gmail` (or your choice)
4. Click **Create**

## Step 2: Enable Gmail API

1. In your new project, go to **APIs & Services** → **Library**
2. Search for **Gmail API**
3. Click on it and press **Enable**

## Step 3: Create OAuth 2.0 Credentials

1. Go to **APIs & Services** → **Credentials**
2. Click **Create Credentials** → **OAuth client ID**
3. If prompted, configure the **OAuth consent screen**:
   - User Type: **External**
   - App name: `AI Employee`
   - User support email: Your email
   - Developer contact: Your email
   - Click **Save and Continue**
   - Scopes: Skip this step
   - Test users: Add your Gmail address
   - Click **Save and Continue**

4. Now create the OAuth client ID:
   - Application type: **Desktop app**
   - Name: `AI Employee Gmail Watcher`
   - Click **Create**

5. Download the credentials:
   - Click the **Download** icon (down arrow) next to your new credentials
   - Save the file as `gmail_credentials.json`

## Step 4: Place Credentials in Config Folder

Move the downloaded `gmail_credentials.json` file to:

```
Personal_AI_Employee_Silver_Tier/config/gmail_credentials.json
```

## Step 5: Install Dependencies

```bash
cd Personal_AI_Employee_Silver_Tier/watchers
pip install -r requirements.txt
```

## Step 6: First-Time Authentication

Run the Gmail Watcher:

```bash
python watchers/gmail_watcher.py
```

On first run:
1. The script will display an authentication URL
2. Copy the URL and open it in your browser
3. Sign in with your Google account
4. Grant permissions to the app
5. Copy the authorization code back to the terminal
6. Press Enter

A `gmail_token.json` file will be created in the `config/` folder for future use.

## Step 7: Test the Watcher

1. Send yourself a test email with subject "Test Email"
2. The watcher should detect it within 2 minutes
3. Check `AI_Employee_Vault_Silver/Needs_Action/` for a new file

## Troubleshooting

### "Credentials file not found"
Ensure `gmail_credentials.json` is in the `config/` folder.

### "Token expired"
Delete `config/gmail_token.json` and re-run the watcher to re-authenticate.

### "Gmail API not enabled"
Go back to Google Cloud Console and enable the Gmail API.

### Watcher not detecting emails
- Check that emails are unread
- Verify the watcher is running
- Check the logs for errors

## Security Notes

- **Never commit** `gmail_credentials.json` or `gmail_token.json` to Git
- These files are already in `.gitignore`
- Keep your credentials secure
- The token file contains access to your Gmail

## Customization

### Change Check Interval

Edit `gmail_watcher.py` and modify the `check_interval` parameter:

```python
super().__init__(vault_path, check_interval=120)  # 120 seconds
```

### Add Urgent Keywords

Edit the `URGENT_KEYWORDS` list in `gmail_watcher.py`:

```python
URGENT_KEYWORDS = ['urgent', 'asap', 'invoice', 'payment', 
                   'help', 'emergency', 'deadline', 'important', 
                   'action required', 'respond', 'your_keyword']
```

### Add Important Contacts

Edit the `important_domains` list in the `_calculate_priority` method:

```python
important_domains = ['client.com', 'partner.com', 'boss @company.com']
```

## Next Steps

After Gmail Watcher is working:
1. Set up WhatsApp Watcher
2. Configure Email MCP server for sending replies
3. Test the approval workflow

---

For more information, see [SILVER_TIER_PLAN.md](../SILVER_TIER_PLAN.md)
