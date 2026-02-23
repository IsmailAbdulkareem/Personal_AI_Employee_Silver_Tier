# Process AI Employee Tasks

Process tasks from the AI Employee vault's Needs_Action folder according to the Company Handbook guidelines.

## What this skill does

This skill enables Claude Code to act as an AI Employee by:
1. Reading tasks from the Needs_Action folder
2. Analyzing them according to Company Handbook rules
3. Creating action plans
4. Executing safe actions
5. Moving completed tasks to Done folder
6. Updating the Dashboard

## When to use this skill

Use this skill when:
- New files appear in the Needs_Action folder
- You want to process pending tasks
- You need to update the AI Employee dashboard
- You want to review and complete action items

## How it works

The skill follows this workflow:
1. **Read**: Check Needs_Action folder for pending tasks
2. **Analyze**: Review each task against Company Handbook guidelines
3. **Plan**: Create a plan in the Plans folder if needed
4. **Execute**: Perform safe actions (reading, analyzing, drafting)
5. **Approve**: For sensitive actions, create approval requests
6. **Complete**: Move finished tasks to Done folder
7. **Update**: Refresh Dashboard with current status

## Usage

```bash
# Process all pending tasks
/process-tasks

# Process with specific focus
/process-tasks --priority high

# Dry run (no file moves)
/process-tasks --dry-run
```

## Parameters

- `--priority`: Filter by priority level (high, medium, low)
- `--dry-run`: Preview actions without executing
- `--update-dashboard`: Update dashboard after processing (default: true)

## Example

When a file is dropped in the Inbox:
1. Watcher creates FILE_20260220_document.md in Needs_Action
2. Run `/process-tasks`
3. Claude reads the file, analyzes it, creates a plan
4. Executes safe actions or creates approval requests
5. Moves completed task to Done
6. Updates Dashboard with new stats

## Safety

This skill follows the Company Handbook rules:
- Never takes irreversible actions without approval
- Creates approval files for sensitive operations
- Logs all actions
- Maintains human-in-the-loop for critical decisions

## Files accessed

- `AI_Employee_Vault/Needs_Action/*.md` (read)
- `AI_Employee_Vault/Plans/*.md` (write)
- `AI_Employee_Vault/Done/*.md` (write)
- `AI_Employee_Vault/Dashboard.md` (read/write)
- `AI_Employee_Vault/Company_Handbook.md` (read)
- `AI_Employee_Vault/Pending_Approval/*.md` (write)
