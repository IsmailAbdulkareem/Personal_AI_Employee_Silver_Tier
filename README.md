# AI Employee - Silver Tier

A local-first autonomous AI Employee built with Claude Code, MCP servers, and an Obsidian vault for intelligent task management, email processing, LinkedIn engagement, and business automation.

## Overview

Silver Tier builds upon Bronze Tier foundations by adding:
- **Multiple Watchers**: Gmail, WhatsApp, and LinkedIn monitoring
- **MCP Servers**: Email sending and LinkedIn posting capabilities
- **Human-in-the-Loop**: Approval workflow for sensitive actions
- **Plan Creation**: Claude reasoning loop for complex task planning
- **Scheduled Operations**: Daily briefings and weekly audits
- **Agent Skills**: Documented reusable AI capabilities

## Features

### Silver Tier Additions
- ✅ All Bronze Tier features
- ✅ Gmail Watcher for email monitoring
- ✅ WhatsApp Watcher for urgent messages
- ✅ LinkedIn Watcher for engagement opportunities
- ✅ Email MCP server (send/draft/search emails)
- ✅ LinkedIn MCP server (create posts with approval)
- ✅ Human-in-the-loop approval workflow
- ✅ Plan.md creator for complex tasks
- ✅ Daily CEO briefing (scheduled)
- ✅ Weekly business audit (scheduled)
- ✅ 5 Agent Skills documented

## Architecture

```
Personal_AI_Employee_Silver_Tier/
├── AI_Employee_Vault_Silver/
│   ├── Dashboard.md                    # Real-time status dashboard
│   ├── Company_Handbook.md             # Operating rules
│   ├── Business_Goals.md               # Q1 2026 objectives
│   ├── Inbox/                          # Drop zone for new items
│   ├── Needs_Action/                   # Pending tasks
│   ├── Plans/                          # Action plans
│   ├── Pending_Approval/               # Awaiting human approval
│   ├── Approved/                       # Approved actions
│   ├── Rejected/                       # Rejected actions
│   ├── Done/                           # Completed tasks
│   ├── Logs/                           # Audit logs
│   └── Briefings/                      # Daily/Weekly reports
│
├── watchers/
│   ├── base_watcher.py                 # Base class
│   ├── filesystem_watcher.py           # File monitoring
│   ├── gmail_watcher.py                # Gmail monitoring
│   ├── whatsapp_watcher.py             # WhatsApp monitoring
│   ├── linkedin_watcher.py             # LinkedIn monitoring
│   └── requirements.txt                # Python dependencies
│
├── mcp_servers/
│   ├── email_mcp/                      # Email operations
│   │   ├── index.js
│   │   └── package.json
│   └── linkedin_mcp/                   # LinkedIn posting
│       ├── index.js
│       └── package.json
│
├── .claude/skills/                     # Agent Skills for Claude Code
│   ├── email/
│   ├── linkedin/
│   ├── plan-creator/
│   ├── approval-workflow/
│   └── weekly-audit/
│
├── scripts/
│   ├── daily_briefing.py               # Daily CEO briefing
│   ├── weekly_audit.py                 # Weekly business audit
│   └── setup_mcp_servers.sh            # MCP setup script
│
├── orchestrator.py                     # Silver Tier orchestrator
└── README.md                           # This file
```

## Setup Instructions

### Prerequisites

- Python 3.13+
- Node.js 18+
- Claude Code installed and configured
- Gmail API credentials (for email features)
- Obsidian (optional, for viewing the vault)

### Installation

1. **Install Python dependencies**
   ```bash
   cd watchers
   pip install -r requirements.txt
   ```

2. **Install MCP server dependencies**
   ```bash
   bash scripts/setup_mcp_servers.sh
   ```

3. **Configure Gmail API** (optional, for email features)
   - See `config/GMAIL_SETUP.md`
   - Download Gmail API credentials from Google Cloud Console
   - Place credentials in `config/gmail_credentials.json`

4. **Configure MCP servers in Claude Code**
   - Add MCP server paths to your Claude Code settings

### Running the System

#### Quick Start

1. **Start the Orchestrator**
   ```bash
   python orchestrator.py
   ```

2. **Start individual watchers** (in separate terminals)
   ```bash
   python watchers/filesystem_watcher.py
   python watchers/gmail_watcher.py    # Requires Gmail setup
   python watchers/whatsapp_watcher.py # First run needs QR scan
   python watchers/linkedin_watcher.py # First run needs login
   ```

3. **Test with a file**
   ```bash
   echo "Test task for Silver Tier" > AI_Employee_Vault_Silver/Inbox/test_task.txt
   ```

## Usage Examples

### Email Processing
1. Gmail Watcher detects new email
2. Creates action file in `Needs_Action/EMAIL_*.md`
3. Claude processes email using `email_skill.md`
4. Drafts response (requires approval)
5. Sends after human approval

### LinkedIn Engagement
1. LinkedIn Watcher finds opportunity post
2. Creates action file in `Needs_Action/LINKEDIN_*.md`
3. Claude drafts engagement strategy
4. Creates post via MCP (requires approval)
5. Posts when approved

### Approval Workflow
1. Sensitive action detected (email send, post create)
2. Approval request created in `Pending_Approval/`
3. Human reviews and moves to `Approved/` or `Rejected/`
4. Orchestrator processes approved actions
5. Action executed and logged

### Daily Briefing
- Runs automatically at 8:00 AM (configure via cron/Task Scheduler)
- Generates briefing in `Briefings/DAILY_BRIEFING_*.md`
- Creates alert in `Needs_Action/`
- Includes pending items, priorities, and stats

### Weekly Audit
- Runs automatically on Sundays at 8:00 PM
- Generates comprehensive audit in `Briefings/WEEKLY_AUDIT_*.md`
- Analyzes metrics, bottlenecks, opportunities
- Provides recommendations for next week

## Scheduling Setup

### Linux/Mac (Cron)

```bash
# Edit crontab
crontab -e

# Add these lines:
# Daily briefing at 8:00 AM
0 8 * * * cd /path/to/Silver_Tier && python scripts/daily_briefing.py

# Weekly audit on Sundays at 8:00 PM
0 20 * * 0 cd /path/to/Silver_Tier && python scripts/weekly_audit.py
```

### Windows (Task Scheduler)

```powershell
# Daily briefing at 8:00 AM
schtasks /create /tn "AI_Employee_Daily_Briefing" /tr "python C:\path\to\scripts\daily_briefing.py" /sc daily /st 08:00

# Weekly audit on Sundays at 8:00 PM
schtasks /create /tn "AI_Employee_Weekly_Audit" /tr "python C:\path\to\scripts\weekly_audit.py" /sc weekly /d SUN /st 20:00
```

## Silver Tier Checklist

| Requirement | Status |
|-------------|--------|
| All Bronze Tier requirements | ✅ Complete |
| Two or more Watcher scripts | ✅ Complete (File, Gmail, WhatsApp, LinkedIn) |
| LinkedIn auto-posting | ✅ Complete (with approval workflow) |
| Claude reasoning loop (Plan.md) | ✅ Complete |
| One working MCP server | ✅ Complete (Email, LinkedIn) |
| Human-in-the-loop approval | ✅ Complete |
| Basic scheduling | ✅ Complete (Daily briefing, Weekly audit) |
| All AI functionality as Agent Skills | ✅ Complete (5 skills) |

## Agent Skills

| Skill | Location | Description |
|-------|----------|-------------|
| Email Processing | `.claude/skills/email/` | Process and send emails |
| LinkedIn Engagement | `.claude/skills/linkedin/` | LinkedIn engagement and posting |
| Plan Creator | `.claude/skills/plan-creator/` | Create action plans for complex tasks |
| Approval Workflow | `.claude/skills/approval-workflow/` | Human-in-the-loop approvals |
| Weekly Audit | `.claude/skills/weekly-audit/` | Weekly business analysis |

## MCP Servers

### Email MCP Server
- `send_email(to, subject, body, cc?, bcc?)`
- `draft_email(to, subject, body)`
- `search_emails(query, max_results)`
- `mark_read(message_id)`

### LinkedIn MCP Server
- `create_post(content, visibility)` - Creates approval request
- `schedule_post(content, scheduled_time)` - Schedule with approval
- `draft_post(content)` - Create draft for review
- `get_analytics(post_id)` - Get post analytics (placeholder)

## Security Considerations

1. **Credentials**: Never commit API keys or tokens
2. **Session Files**: WhatsApp/LinkedIn sessions are gitignored
3. **Approval Required**: All external communications need approval
4. **Audit Logs**: All actions logged with timestamps
5. **Data Privacy**: All data stays local in the vault

## Troubleshooting

**Watcher not detecting files:**
- Ensure the watcher is running
- Check folder permissions
- Verify vault path is correct

**Gmail authentication failed:**
- Check `config/gmail_credentials.json` exists
- Delete `config/gmail_token.json` and re-authenticate
- Ensure Gmail API scopes are correct

**WhatsApp/LinkedIn session issues:**
- Delete session folder in `config/` and re-authenticate
- Ensure Playwright browsers are installed: `playwright install`

**MCP server not working:**
- Run `bash scripts/setup_mcp_servers.sh`
- Check Node.js version (18+)
- Verify MCP paths in Claude Code settings

## Resources

- [Hackathon Documentation](Personal%20AI%20Employee%20Hackathon%200_%20Building%20Autonomous%20FTEs%20in%202026.md)
- [SILVER_TIER_PLAN.md](SILVER_TIER_PLAN.md) - Implementation plan
- [Gmail API Documentation](https://developers.google.com/gmail/api)
- [LinkedIn API Documentation](https://learn.microsoft.com/en-us/linkedin/)
- [MCP Server Specification](https://modelcontextprotocol.io/)

## License

MIT

---
*AI Employee Silver Tier - From Foundation to Functional Assistant*
