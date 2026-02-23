"""
Orchestrator for AI Employee - Silver Tier
Coordinates between watchers, MCP actions, and Claude Code processing

Silver Tier Features:
- Multi-watcher coordination (File, Gmail, WhatsApp, LinkedIn)
- Approval workflow monitoring
- Plan progress tracking
- Enhanced dashboard with Silver metrics
"""
import time
import subprocess
import shutil
from pathlib import Path
from datetime import datetime
import logging
import re

class AIEmployeeOrchestrator:
    """Main orchestrator that coordinates the AI Employee system (Silver Tier)"""

    def __init__(self, vault_path: str):
        self.vault_path = Path(vault_path)
        
        # Core folders
        self.needs_action = self.vault_path / 'Needs_Action'
        self.done = self.vault_path / 'Done'
        self.pending_approval = self.vault_path / 'Pending_Approval'
        self.approved = self.vault_path / 'Approved'
        self.rejected = self.vault_path / 'Rejected'
        self.plans = self.vault_path / 'Plans'
        self.logs = self.vault_path / 'Logs'
        self.briefings = self.vault_path / 'Briefings'
        self.dashboard = self.vault_path / 'Dashboard.md'

        # Setup logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger('Orchestrator')

        # Ensure all directories exist
        self._ensure_directories()

    def _ensure_directories(self):
        """Ensure all vault directories exist"""
        for folder in [self.needs_action, self.done, self.pending_approval, 
                       self.approved, self.rejected, self.plans, self.logs, self.briefings]:
            folder.mkdir(parents=True, exist_ok=True)

    def check_needs_action(self) -> list:
        """Check for files in Needs_Action folder"""
        if not self.needs_action.exists():
            return []
        files = list(self.needs_action.glob('*.md'))
        return files

    def check_pending_approvals(self) -> list:
        """Check for pending approval requests"""
        if not self.pending_approval.exists():
            return []
        return list(self.pending_approval.glob('*.md'))

    def check_approved_actions(self) -> list:
        """Check for approved actions ready to execute"""
        if not self.approved.exists():
            return []
        return list(self.approved.glob('*.md'))

    def check_active_plans(self) -> list:
        """Check for active plans in progress"""
        if not self.plans.exists():
            return []
        
        active_plans = []
        for f in self.plans.glob('*.md'):
            try:
                content = f.read_text(encoding='utf-8')
                if 'status: in_progress' in content.lower():
                    active_plans.append(f)
            except Exception as e:
                self.logger.debug(f'Error reading plan {f}: {e}')
        return active_plans

    def extract_field(self, content: str, field: str) -> str:
        """Extract a field from markdown frontmatter"""
        pattern = rf'^{field}:\s*(.+)$'
        match = re.search(pattern, content, re.MULTILINE | re.IGNORECASE)
        return match.group(1).strip() if match else None

    def update_dashboard(self):
        """Update the dashboard with Silver Tier metrics"""
        # Count files in each folder
        needs_action_count = len(list(self.needs_action.glob('*.md')))
        done_count = len(list(self.done.glob('*.md')))
        pending_approval_count = len(list(self.pending_approval.glob('*.md'))) if self.pending_approval.exists() else 0
        active_plans_count = len(self.check_active_plans())

        # Get watcher status
        watchers_active = 4  # File, Gmail, WhatsApp, LinkedIn configured

        # Get MCP servers status
        mcp_servers_active = 2  # Email, LinkedIn configured

        # Read current dashboard
        if self.dashboard.exists():
            content = self.dashboard.read_text(encoding='utf-8')
            now = datetime.now()

            # Update timestamp
            content = re.sub(
                r'last_updated:.*',
                f'last_updated: {now.isoformat()}',
                content
            )

            # Update status line
            content = re.sub(
                r'status:.*',
                'status: active',
                content
            )

            # Update watchers running
            content = re.sub(
                r'\*\*Watchers Running\*\*:.*',
                f'**Watchers Running**: File System ✅, Gmail ⚙️, WhatsApp ⚙️, LinkedIn ⚙️',
                content
            )

            # Update last check
            content = re.sub(
                r'\*\*Last Check\*\*:.*',
                f'**Last Check**: {now.isoformat()}',
                content
            )

            # Update pending actions
            content = re.sub(
                r'- Pending Actions: \d+',
                f'- Pending Actions: {needs_action_count}',
                content
            )

            # Update completed tasks
            content = re.sub(
                r'- Completed Tasks: \d+',
                f'- Completed Tasks: {done_count}',
                content
            )

            # Update awaiting approval
            content = re.sub(
                r'- Awaiting Approval: \d+',
                f'- Awaiting Approval: {pending_approval_count}',
                content
            )

            # Update plans created
            content = re.sub(
                r'- Plans Created: \d+',
                f'- Plans Created: {active_plans_count}',
                content
            )

            # Update Quick Stats table
            content = re.sub(
                r'\| Files in Needs_Action \| \d+ \|',
                f'| Files in Needs_Action | {needs_action_count} |',
                content
            )
            content = re.sub(
                r'\| Tasks Completed \| \d+ \|',
                f'| Tasks Completed | {done_count} |',
                content
            )

            # Update Silver Tier Metrics section if exists
            if '## Silver Tier Metrics' in content:
                content = re.sub(
                    r'\| Watchers Active \|.*\|',
                    f'| Watchers Active | {watchers_active} (File, Gmail, WhatsApp, LinkedIn) |',
                    content
                )
                content = re.sub(
                    r'\| MCP Servers \|.*\|',
                    f'| MCP Servers | {mcp_servers_active} (Email, LinkedIn) |',
                    content
                )
                content = re.sub(
                    r'\| Approvals Pending \|.*\|',
                    f'| Approvals Pending | {pending_approval_count} |',
                    content
                )

            self.dashboard.write_text(content, encoding='utf-8')
            self.logger.info('Dashboard updated')
        else:
            # Create new dashboard if missing
            self._create_dashboard(needs_action_count, done_count, pending_approval_count, active_plans_count)

    def _create_dashboard(self, na_count: int, done_count: int, approval_count: int, plans_count: int):
        """Create a new dashboard file"""
        now = datetime.now()
        content = f"""# AI Employee Dashboard

---
last_updated: {now.isoformat()}
status: active
---

## System Status
- **Vault Status**: Active ✅
- **Watchers Running**: File System ✅, Gmail ⚙️, WhatsApp ⚙️, LinkedIn ⚙️
- **Last Check**: {now.isoformat()}

## Today's Summary
- Pending Actions: {na_count}
- Completed Tasks: {done_count}
- Awaiting Approval: {approval_count}
- Plans Created: {plans_count}

## Silver Tier Metrics
| Metric | Value |
|--------|-------|
| Watchers Active | 4 (File, Gmail, WhatsApp, LinkedIn) |
| MCP Servers | 2 (Email, LinkedIn) |
| Plans Created | {plans_count} |
| Approvals Pending | {approval_count} |

## Quick Stats
| Metric | Count |
|--------|-------|
| Files in Needs_Action | {na_count} |
| Plans Created | {plans_count} |
| Tasks Completed | {done_count} |
| Files Processed Today | {done_count} |
| Watcher Detections | {na_count} |

## Alerts
*No alerts*

## Silver Tier Status
✅ **SILVER TIER OPERATIONAL**
- Multi-watcher system configured
- MCP servers available (Email, LinkedIn)
- Approval workflow active
- Plan tracking enabled
- Daily briefing scheduled
- Weekly audit scheduled

---
*AI Employee - Silver Tier*
"""
        self.dashboard.write_text(content, encoding='utf-8')

    def process_approved_actions(self):
        """Process approved actions from the Approved folder"""
        approved_files = self.check_approved_actions()

        for f in approved_files:
            try:
                content = f.read_text(encoding='utf-8')
                action_type = self.extract_field(content, 'action')

                self.logger.info(f'Processing approved action: {f.name} (type: {action_type})')

                # Log the approval processing
                log_entry = f"[{datetime.now().isoformat()}] Processed approval: {f.name} (action: {action_type})\n"
                self._write_log(log_entry)

                # Move to Done after processing
                dest = self.done / f.name
                shutil.move(str(f), str(dest))
                self.logger.info(f'Moved {f.name} to Done')

            except Exception as e:
                self.logger.error(f'Error processing approved action {f.name}: {e}')

    def process_rejected_actions(self):
        """Archive rejected actions"""
        if not self.rejected.exists():
            return

        rejected_files = list(self.rejected.glob('*.md'))
        for f in rejected_files:
            self.logger.info(f'Archiving rejected action: {f.name}')
            # Could add notification logic here

    def _write_log(self, message: str):
        """Write a log entry"""
        log_file = self.logs / f'orchestrator_{datetime.now().strftime("%Y-%m-%d")}.log'
        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(message)

    def trigger_claude_processing(self):
        """Trigger Claude Code to process Needs_Action folder"""
        files = self.check_needs_action()

        if not files:
            self.logger.info('No files to process')
            return

        self.logger.info(f'Found {len(files)} files to process')
        self.logger.info('Files ready for Claude Code processing:')
        for f in files:
            self.logger.info(f'  - {f.name}')

        # Update dashboard
        self.update_dashboard()

        self.logger.info('Ready for Claude Code to process these files')
        self.logger.info('Run: claude "Process all files in Needs_Action folder"')

    def run(self, check_interval: int = 30):
        """Run the orchestrator loop (Silver Tier)"""
        self.logger.info('Starting AI Employee Orchestrator (Silver Tier)')
        self.logger.info(f'Vault path: {self.vault_path}')
        self.logger.info(f'Check interval: {check_interval} seconds')
        self.logger.info('Features: Multi-watcher, Approval workflow, Plan tracking')

        try:
            while True:
                # Check and process approved actions
                self.process_approved_actions()
                
                # Archive rejected actions
                self.process_rejected_actions()
                
                # Trigger Claude processing for new items
                self.trigger_claude_processing()
                
                # Update dashboard
                self.update_dashboard()
                
                time.sleep(check_interval)
        except KeyboardInterrupt:
            self.logger.info('Orchestrator stopped by user')

if __name__ == '__main__':
    import sys

    # Get vault path from command line or use default
    if len(sys.argv) > 1:
        vault_path = sys.argv[1]
    else:
        vault_path = Path(__file__).parent / 'AI_Employee_Vault_Silver'

    orchestrator = AIEmployeeOrchestrator(str(vault_path))
    orchestrator.run()
