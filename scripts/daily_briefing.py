#!/usr/bin/env python3
"""
Daily Briefing Generator for AI Employee
Generates a daily CEO briefing at scheduled times (default 8:00 AM)

Usage:
    python daily_briefing.py [vault_path]

Schedule with cron (Linux/Mac):
    0 8 * * * cd /path/to/Silver_Tier && python scripts/daily_briefing.py

Schedule with Task Scheduler (Windows):
    schtasks /create /tn "AI_Employee_Daily_Briefing" /tr "python C:\path\to\scripts\daily_briefing.py" /sc daily /st 08:00
"""

import sys
import logging
from pathlib import Path
from datetime import datetime, timedelta
from collections import defaultdict

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('DailyBriefing')


class DailyBriefingGenerator:
    """Generates daily CEO briefing reports"""

    def __init__(self, vault_path: str):
        self.vault_path = Path(vault_path)
        self.briefings_path = self.vault_path / 'Briefings'
        self.needs_action = self.vault_path / 'Needs_Action'
        self.done = self.vault_path / 'Done'
        self.pending_approval = self.vault_path / 'Pending_Approval'
        self.approved = self.vault_path / 'Approved'
        self.plans = self.vault_path / 'Plans'
        self.logs = self.vault_path / 'Logs'
        self.dashboard = self.vault_path / 'Dashboard.md'

        # Ensure briefings directory exists
        self.briefings_path.mkdir(parents=True, exist_ok=True)

    def get_files_by_date(self, folder: Path, days_back: int = 1) -> list:
        """Get files modified in the last N days"""
        if not folder.exists():
            return []

        cutoff = datetime.now() - timedelta(days=days_back)
        files = []

        for f in folder.glob('*.md'):
            try:
                mtime = datetime.fromtimestamp(f.stat().st_mtime)
                if mtime >= cutoff:
                    files.append(f)
            except Exception as e:
                logger.debug(f'Error checking file {f}: {e}')

        return files

    def analyze_action_files(self, files: list) -> dict:
        """Analyze action files and categorize them"""
        categories = defaultdict(list)

        for f in files:
            content = f.read_text(encoding='utf-8').lower()

            if 'type: email' in content:
                categories['emails'].append(f)
            elif 'type: whatsapp' in content:
                categories['whatsapp'].append(f)
            elif 'type: linkedin' in content:
                categories['linkedin'].append(f)
            elif 'type: approval' in content:
                categories['approvals'].append(f)
            else:
                categories['other'].append(f)

        return categories

    def get_priority_items(self, files: list) -> list:
        """Extract high priority items"""
        priority_items = []

        for f in files:
            content = f.read_text(encoding='utf-8')
            if 'priority: high' in content.lower():
                # Extract subject or title
                for line in content.split('\n')[:20]:
                    if 'subject:' in line.lower() or '#' in line:
                        title = line.split(':', 1)[-1].strip().strip('#').strip()
                        priority_items.append((f.name, title))
                        break

        return priority_items

    def generate_briefing(self) -> Path:
        """Generate the daily briefing report"""
        today = datetime.now()
        date_str = today.strftime('%Y-%m-%d')
        timestamp = today.strftime('%Y-%m-%d_%H%M')

        # Gather data
        needs_action_files = self.get_files_by_date(self.needs_action, days_back=1)
        pending_approval_files = list(self.pending_approval.glob('*.md')) if self.pending_approval.exists() else []
        recent_done = self.get_files_by_date(self.done, days_back=1)
        active_plans = [f for f in self.plans.glob('*.md') if 'status: in_progress' in f.read_text().lower()] if self.plans.exists() else []

        # Analyze
        na_categories = self.analyze_action_files(needs_action_files)
        priority_items = self.get_priority_items(needs_action_files + pending_approval_files)

        # Count stats
        total_pending = len(needs_action_files)
        total_approvals = len(pending_approval_files)
        completed_today = len(recent_done)
        active_plans_count = len(active_plans)

        # Generate briefing content
        briefing_content = f"""---
type: daily_briefing
date: {date_str}
generated: {today.isoformat()}
priority: high
status: ready
---

# Daily CEO Briefing
## {today.strftime('%A, %B %d, %Y')}

---

## Executive Summary

Good morning! Here's your daily briefing for **{date_str}**.

**Quick Stats:**
- 📬 Pending Actions: {total_pending}
- ⏳ Awaiting Approval: {total_approvals}
- ✅ Completed Yesterday: {completed_today}
- 📋 Active Plans: {active_plans_count}

---

## 🔴 High Priority Items

"""

        if priority_items:
            for filename, title in priority_items[:10]:
                briefing_content += f"- [ ] **{title}**\n"
        else:
            briefing_content += "*No high priority items detected.*\n"

        briefing_content += f"""
---

## 📥 Needs Action

### Overview
- **Emails**: {len(na_categories['emails'])}
- **WhatsApp Messages**: {len(na_categories['whatsapp'])}
- **LinkedIn Items**: {len(na_categories['linkedin'])}
- **Other**: {len(na_categories['other'])}

"""

        if na_categories['emails']:
            briefing_content += "### Emails\n"
            for f in na_categories['emails'][:5]:
                content = f.read_text(encoding='utf-8')
                subject = self._extract_field(content, 'subject') or f.name
                from_field = self._extract_field(content, 'from') or 'Unknown'
                briefing_content += f"- [ ] `{subject}` (From: {from_field})\n"
            briefing_content += "\n"

        if na_categories['whatsapp']:
            briefing_content += "### WhatsApp Messages\n"
            for f in na_categories['whatsapp'][:5]:
                content = f.read_text(encoding='utf-8')
                chat = self._extract_field(content, 'chat_name') or f.name
                briefing_content += f"- [ ] `{chat}`\n"
            briefing_content += "\n"

        if na_categories['linkedin']:
            briefing_content += "### LinkedIn Items\n"
            for f in na_categories['linkedin'][:5]:
                content = f.read_text(encoding='utf-8')
                author = self._extract_field(content, 'author') or self._extract_field(content, 'from') or f.name
                briefing_content += f"- [ ] `{author}`\n"
            briefing_content += "\n"

        if not needs_action_files:
            briefing_content += "*No items need action at this time.*\n\n"

        briefing_content += f"""---

## ⏳ Pending Approvals

"""

        if pending_approval_files:
            for f in pending_approval_files[:5]:
                content = f.read_text(encoding='utf-8')
                action = self._extract_field(content, 'action') or 'Unknown'
                created = self._extract_field(content, 'created') or 'Unknown'
                briefing_content += f"- [ ] **{action}** (Created: {created})\n"
        else:
            briefing_content += "*No pending approvals.*\n"

        briefing_content += f"""

---

## ✅ Recently Completed

"""

        if recent_done:
            for f in recent_done[:5]:
                briefing_content += f"- [x] {f.name}\n"
        else:
            briefing_content += "*No recent completions.*\n"

        briefing_content += f"""

---

## 📋 Active Plans

"""

        if active_plans:
            for f in active_plans[:5]:
                content = f.read_text(encoding='utf-8')
                # Extract title from first # heading
                title = f.name
                for line in content.split('\n'):
                    if line.startswith('# '):
                        title = line[2:].strip()
                        break
                briefing_content += f"- [ ] {title}\n"
        else:
            briefing_content += "*No active plans.*\n"

        briefing_content += f"""

---

## 📊 Today's Focus

### Recommended Priorities
1. Address high priority items listed above
2. Review and action pending approvals
3. Process new emails and messages
4. Update active plans

### Suggested Actions
- [ ] Review this briefing and set priorities
- [ ] Clear pending approvals
- [ ] Process urgent communications
- [ ] Update plans with progress

---

## 📈 System Status

| Component | Status |
|-----------|--------|
| File Watcher | {'✅ Running' if self.needs_action.exists() else '⚠️ Check'} |
| Gmail Watcher | ⚙️ Configured |
| WhatsApp Watcher | ⚙️ Configured |
| LinkedIn Watcher | ⚙️ Configured |
| MCP Servers | ⚙️ Available |

---

## 📝 Notes

_Add your notes, priorities, and focus areas for today below:_



---

*Briefing generated by AI Employee at {today.strftime('%H:%M')}*
"""

        # Write briefing file
        briefing_file = self.briefings_path / f'DAILY_BRIEFING_{timestamp}.md'
        briefing_file.write_text(briefing_content, encoding='utf-8')

        logger.info(f'Daily briefing generated: {briefing_file.name}')

        # Also create a Needs_Action file to alert user
        alert_file = self.needs_action / f'BRIEFING_{timestamp}.md'
        alert_content = f"""---
type: daily_briefing_alert
date: {date_str}
priority: high
status: pending
---

# Daily Briefing Ready

## {today.strftime('%A, %B %d, %Y')}

Your daily briefing has been generated and is ready for review.

**Location:** `Briefings/{briefing_file.name}`

### Quick Stats
- Pending Actions: {total_pending}
- Awaiting Approval: {total_approvals}
- Completed Today: {completed_today}

---

## Action Required
- [ ] Review the full briefing in the Briefings folder
- [ ] Set priorities for the day
- [ ] Address high-priority items

---

*Click on the file path above to open the full briefing.*
"""
        alert_file.write_text(alert_content, encoding='utf-8')

        return briefing_file

    def _extract_field(self, content: str, field: str) -> str:
        """Extract a field from markdown frontmatter"""
        for line in content.split('\n')[:30]:
            if line.lower().startswith(f'{field}:'):
                return line.split(':', 1)[1].strip()
        return None

    def run(self):
        """Generate the daily briefing"""
        logger.info('Starting daily briefing generation...')
        briefing_file = self.generate_briefing()
        logger.info(f'Briefing saved to: {briefing_file}')
        return briefing_file


if __name__ == '__main__':
    # Get vault path from command line or use default
    if len(sys.argv) > 1:
        vault_path = sys.argv[1]
    else:
        vault_path = Path(__file__).parent.parent / 'AI_Employee_Vault_Silver'

    generator = DailyBriefingGenerator(str(vault_path))
    generator.run()
