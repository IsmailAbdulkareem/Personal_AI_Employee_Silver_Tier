#!/usr/bin/env python3
"""
AI Employee Task Processor Skill
Processes tasks from Needs_Action folder according to Company Handbook
"""
import sys
import argparse
from pathlib import Path
from datetime import datetime

def main():
    parser = argparse.ArgumentParser(description='Process AI Employee tasks')
    parser.add_argument('--priority', choices=['high', 'medium', 'low'],
                       help='Filter by priority level')
    parser.add_argument('--dry-run', action='store_true',
                       help='Preview actions without executing')
    parser.add_argument('--update-dashboard', action='store_true', default=True,
                       help='Update dashboard after processing')

    args = parser.parse_args()

    # Get vault path
    vault_path = Path(__file__).parent.parent.parent.parent / 'AI_Employee_Vault'

    # Build the prompt for Claude
    prompt = f"""You are an AI Employee processing tasks from your vault.

**Vault Location**: {vault_path}

**Your Mission**: Process all tasks in the Needs_Action folder according to the Company Handbook guidelines.

**Instructions**:
1. Read the Company_Handbook.md to understand your operating rules
2. Check all files in the Needs_Action/ folder
3. For each task:
   - Analyze what action is needed
   - Check if it requires approval (per handbook)
   - If safe to execute: do it and move to Done/
   - If needs approval: create file in Pending_Approval/
   - If complex: create a plan in Plans/ folder
4. Update Dashboard.md with current statistics
5. Log your actions

**Priority Filter**: {args.priority if args.priority else 'all'}
**Mode**: {'DRY RUN (preview only)' if args.dry_run else 'EXECUTE'}

**Safety Rules**:
- Never delete files without approval
- Never send external communications without approval
- Always log your actions
- Follow the Company Handbook guidelines

Begin processing now.
"""

    print(prompt)
    return 0

if __name__ == '__main__':
    sys.exit(main())
