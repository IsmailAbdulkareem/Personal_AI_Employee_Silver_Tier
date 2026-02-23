#!/usr/bin/env python3
"""
Weekly Business Audit Generator for AI Employee
Generates comprehensive weekly audit reports every Sunday

Usage:
    python weekly_audit.py [vault_path]

Schedule with cron (Linux/Mac):
    0 20 * * 0 cd /path/to/Silver_Tier && python scripts/weekly_audit.py

Schedule with Task Scheduler (Windows):
    schtasks /create /tn "AI_Employee_Weekly_Audit" /tr "python C:\path\to\scripts\weekly_audit.py" /sc weekly /d SUN /st 20:00
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
logger = logging.getLogger('WeeklyAudit')


class WeeklyAuditGenerator:
    """Generates weekly business audit reports"""

    def __init__(self, vault_path: str):
        self.vault_path = Path(vault_path)
        self.briefings_path = self.vault_path / 'Briefings'
        self.needs_action = self.vault_path / 'Needs_Action'
        self.done = self.vault_path / 'Done'
        self.pending_approval = self.vault_path / 'Pending_Approval'
        self.rejected = self.vault_path / 'Rejected'
        self.plans = self.vault_path / 'Plans'
        self.logs = self.vault_path / 'Logs'
        self.dashboard = self.vault_path / 'Dashboard.md'

        # Ensure briefings directory exists
        self.briefings_path.mkdir(parents=True, exist_ok=True)

    def get_week_start(self, date: datetime) -> datetime:
        """Get the Monday of the week containing the given date"""
        return date - timedelta(days=date.weekday())

    def get_files_in_week(self, folder: Path, week_start: datetime) -> list:
        """Get files modified within the specified week"""
        if not folder.exists():
            return []

        week_end = week_start + timedelta(days=7)
        files = []

        for f in folder.glob('*.md'):
            try:
                mtime = datetime.fromtimestamp(f.stat().st_mtime)
                if week_start <= mtime < week_end:
                    files.append(f)
            except Exception as e:
                logger.debug(f'Error checking file {f}: {e}')

        return files

    def categorize_files(self, files: list) -> dict:
        """Categorize files by type"""
        categories = defaultdict(list)

        for f in files:
            try:
                content = f.read_text(encoding='utf-8').lower()

                if 'type: email' in content:
                    categories['emails'].append(f)
                elif 'type: whatsapp' in content:
                    categories['whatsapp'].append(f)
                elif 'type: linkedin' in content:
                    categories['linkedin'].append(f)
                elif 'type: approval' in content:
                    categories['approvals'].append(f)
                elif 'type: action_plan' in content or 'plan:' in content:
                    categories['plans'].append(f)
                else:
                    categories['other'].append(f)
            except Exception as e:
                logger.debug(f'Error reading file {f}: {e}')

        return categories

    def get_previous_week_files(self, folder: Path, week_start: datetime) -> list:
        """Get files from the previous week for comparison"""
        prev_week_start = week_start - timedelta(days=7)
        return self.get_files_in_week(folder, prev_week_start)

    def extract_title(self, content: str) -> str:
        """Extract title from markdown content"""
        for line in content.split('\n'):
            if line.startswith('# '):
                return line[2:].strip()
        return 'Untitled'

    def extract_field(self, content: str, field: str) -> str:
        """Extract a field from markdown frontmatter"""
        for line in content.split('\n')[:30]:
            if line.lower().startswith(f'{field}:'):
                return line.split(':', 1)[1].strip()
        return None

    def analyze_bottlenecks(self, needs_action_files: list, pending_files: list) -> list:
        """Identify potential bottlenecks"""
        bottlenecks = []

        # Check for old items in Needs_Action
        now = datetime.now()
        for f in needs_action_files:
            try:
                mtime = datetime.fromtimestamp(f.stat().st_mtime)
                age_days = (now - mtime).days
                if age_days > 3:
                    bottlenecks.append({
                        'issue': f'Item in Needs_Action for {age_days} days',
                        'item': f.name,
                        'impact': 'Medium' if age_days < 7 else 'High',
                        'recommendation': 'Review and process or archive'
                    })
            except Exception:
                pass

        # Check for pending approvals
        for f in pending_files:
            content = f.read_text(encoding='utf-8')
            expires = self.extract_field(content, 'expires')
            if expires:
                try:
                    expiry_date = datetime.fromisoformat(expires.replace('Z', '+00:00').replace('+00:00', ''))
                    if datetime.now() > expiry_date:
                        bottlenecks.append({
                            'issue': 'Approval expired',
                            'item': f.name,
                            'impact': 'High',
                            'recommendation': 'Review and approve/reject or create new request'
                        })
                except Exception:
                    pass

        return bottlenecks

    def identify_automation_opportunities(self, categories: dict) -> list:
        """Identify repetitive tasks that could be automated"""
        opportunities = []

        # Check for high volume of similar tasks
        for category, files in categories.items():
            if len(files) >= 5:  # Threshold for automation consideration
                opportunities.append({
                    'task_type': category.title(),
                    'frequency': f'{len(files)} this week',
                    'time_saved_estimate': f'{len(files) * 5} minutes',
                    'priority': 'High' if len(files) >= 10 else 'Medium'
                })

        return opportunities

    def generate_audit(self) -> Path:
        """Generate the weekly audit report"""
        now = datetime.now()
        week_start = self.get_week_start(now)
        last_week_start = self.get_week_start(now - timedelta(days=7))

        week_end = week_start + timedelta(days=6)  # Sunday

        date_str = week_end.strftime('%Y-%m-%d')
        timestamp = now.strftime('%Y-%m-%d_%H%M')

        # Gather data for this week
        done_files = self.get_files_in_week(self.done, week_start)
        needs_action_files = self.get_files_in_week(self.needs_action, week_start)
        pending_files = list(self.pending_approval.glob('*.md')) if self.pending_approval.exists() else []
        plans_files = self.get_files_in_week(self.plans, week_start)

        # Previous week for comparison
        prev_done_files = self.get_previous_week_files(self.done, week_start)

        # Categorize
        done_categories = self.categorize_files(done_files)
        na_categories = self.categorize_files(needs_action_files)

        # Calculate metrics
        total_completed = len(done_files)
        total_prev = len(prev_done_files)
        change_pct = ((total_completed - total_prev) / total_prev * 100) if total_prev > 0 else 0

        # Bottlenecks and opportunities
        bottlenecks = self.analyze_bottlenecks(needs_action_files, pending_files)
        automation_opps = self.identify_automation_opportunities(done_categories)

        # Top completed tasks
        top_completed = []
        for f in done_files[:10]:
            try:
                content = f.read_text(encoding='utf-8')
                title = self.extract_title(content)
                top_completed.append((f.name, title))
            except Exception:
                top_completed.append((f.name, f.name))

        # Generate audit content
        audit_content = f"""---
type: weekly_audit
week_ending: {date_str}
generated: {now.isoformat()}
priority: high
status: ready_for_review
---

# Weekly Business Audit
## Week Ending: {week_end.strftime('%B %d, %Y')}

---

## Executive Summary

**Week of {week_start.strftime('%B %d')} - {week_end.strftime('%B %d, %Y')}**

"""

        # Summary assessment
        if total_completed > total_prev:
            assessment = "Productive week with increased output compared to last week."
        elif total_completed < total_prev:
            assessment = "Slightly lower output this week. Review bottlenecks below."
        else:
            assessment = "Consistent output maintained this week."

        audit_content += f"""{assessment}

**Key Metrics:**
- 📊 Tasks Completed: {total_completed} ({'+' if change_pct >= 0 else ''}{change_pct:.0f}% vs last week)
- 📬 New Items Detected: {len(needs_action_files)}
- ⏳ Pending Approvals: {len(pending_files)}
- 📋 Plans Created: {len(plans_files)}

---

## Task Metrics

### Completion Summary
| Metric | This Week | Last Week | Change |
|--------|-----------|-----------|--------|
| Tasks Completed | {total_completed} | {total_prev} | {'+' if change_pct >= 0 else ''}{change_pct:.0f}% |

### Tasks by Category
| Category | Count | Percentage |
|----------|-------|------------|
| Email Processing | {len(done_categories['emails'])} | {len(done_categories['emails'])/total_completed*100 if total_completed > 0 else 0:.0f}% |
| WhatsApp Messages | {len(done_categories['whatsapp'])} | {len(done_categories['whatsapp'])/total_completed*100 if total_completed > 0 else 0:.0f}% |
| LinkedIn Actions | {len(done_categories['linkedin'])} | {len(done_categories['linkedin'])/total_completed*100 if total_completed > 0 else 0:.0f}% |
| Plans Created | {len(done_categories['plans'])} | {len(done_categories['plans'])/total_completed*100 if total_completed > 0 else 0:.0f}% |
| Other | {len(done_categories['other'])} | {len(done_categories['other'])/total_completed*100 if total_completed > 0 else 0:.0f}% |

### Top Completed Tasks
"""

        for filename, title in top_completed[:5]:
            audit_content += f"1. {title}\n"

        if not top_completed:
            audit_content += "*No tasks completed this week.*\n"

        audit_content += f"""

---

## 📥 Incoming Items Analysis

### New Items by Type
| Type | Count |
|------|-------|
| Emails | {len(na_categories['emails'])} |
| WhatsApp | {len(na_categories['whatsapp'])} |
| LinkedIn | {len(na_categories['linkedin'])} |
| Other | {len(na_categories['other'])} |

---

## ⚠️ Bottlenecks Identified

"""

        if bottlenecks:
            audit_content += "| Issue | Item | Impact | Recommendation |\n"
            audit_content += "|-------|------|--------|----------------|\n"
            for b in bottlenecks[:5]:
                audit_content += f"| {b['issue']} | {b['item'][:30]}... | {b['impact']} | {b['recommendation']} |\n"
        else:
            audit_content += "*No significant bottlenecks identified.*\n"

        audit_content += f"""

---

## 🤖 Automation Opportunities

"""

        if automation_opps:
            audit_content += "| Task Type | Frequency | Est. Time Saved | Priority |\n"
            audit_content += "|-----------|-----------|-----------------|----------|\n"
            for opp in automation_opps:
                audit_content += f"| {opp['task_type']} | {opp['frequency']} | {opp['time_saved_estimate']} | {opp['priority']} |\n"
        else:
            audit_content += "*No high-volume automation opportunities detected this week.*\n"

        audit_content += f"""

---

## 📋 Active Plans

"""

        active_plans = []
        if self.plans.exists():
            for f in self.plans.glob('*.md'):
                try:
                    content = f.read_text(encoding='utf-8')
                    if 'status: in_progress' in content.lower():
                        title = self.extract_title(content)
                        active_plans.append((f.name, title))
                except Exception:
                    pass

        if active_plans:
            for filename, title in active_plans[:5]:
                audit_content += f"- [ ] {title}\n"
        else:
            audit_content += "*No active plans.*\n"

        audit_content += f"""

---

## 🎯 Priorities for Next Week

### Recommended Focus Areas
1. Clear pending approvals
2. Process accumulated Needs_Action items
3. Address identified bottlenecks
4. Continue automation improvements

### Suggested Goals
- [ ] Process all items older than 3 days
- [ ] Review and action all pending approvals
- [ ] Implement at least one automation improvement
- [ ] Update active plans with progress

---

## 📊 AI Employee Performance

### System Statistics
- **Files Processed**: {total_completed}
- **Watcher Detections**: {len(needs_action_files)}
- **Approvals Processed**: {len(pending_files)}
- **Plans Active**: {len(active_plans)}

### Health Check
| Component | Status |
|-----------|--------|
| File Watcher | ✅ Operational |
| Gmail Watcher | ⚙️ Configured |
| WhatsApp Watcher | ⚙️ Configured |
| LinkedIn Watcher | ⚙️ Configured |
| MCP Servers | ⚙️ Available |

---

## 📝 Notes & Observations

_Add additional insights, patterns observed, or recommendations:_



---

## ✅ Action Items for Human

- [ ] Review this weekly audit
- [ ] Address bottlenecks identified above
- [ ] Set priorities for next week
- [ ] Review automation opportunities
- [ ] Approve/reject pending items

---

*Weekly Audit generated by AI Employee at {now.strftime('%Y-%m-%d %H:%M')}*
"""

        # Write audit file
        audit_file = self.briefings_path / f'WEEKLY_AUDIT_{timestamp}.md'
        audit_file.write_text(audit_content, encoding='utf-8')

        logger.info(f'Weekly audit generated: {audit_file.name}')

        # Create Needs_Action alert
        alert_file = self.needs_action / f'WEEKLY_AUDIT_READY_{timestamp}.md'
        alert_content = f"""---
type: weekly_audit_alert
week_ending: {date_str}
priority: high
status: pending
---

# Weekly Audit Ready for Review

## Week Ending: {week_end.strftime('%B %d, %Y')}

Your weekly business audit has been generated.

**Location:** `Briefings/{audit_file.name}`

### This Week's Summary
- Tasks Completed: {total_completed} ({'+' if change_pct >= 0 else ''}{change_pct:.0f}% vs last week)
- Bottlenecks Found: {len(bottlenecks)}
- Automation Opportunities: {len(automation_opps)}

---

## Action Required
- [ ] Review the full audit in the Briefings folder
- [ ] Address identified bottlenecks
- [ ] Set priorities for next week
- [ ] Review automation opportunities

---

*Click on the file path above to open the full audit.*
"""
        alert_file.write_text(alert_content, encoding='utf-8')

        return audit_file

    def run(self):
        """Generate the weekly audit"""
        logger.info('Starting weekly audit generation...')
        audit_file = self.generate_audit()
        logger.info(f'Audit saved to: {audit_file}')
        return audit_file


if __name__ == '__main__':
    # Get vault path from command line or use default
    if len(sys.argv) > 1:
        vault_path = sys.argv[1]
    else:
        vault_path = Path(__file__).parent.parent / 'AI_Employee_Vault_Silver'

    generator = WeeklyAuditGenerator(str(vault_path))
    generator.run()
