# Skill: Human-in-the-Loop Approval Workflow

## Description
Manage human approval workflow for sensitive actions like sending emails, posting to social media, or making payments.

## When to Use
- Sending emails to external recipients
- Posting to LinkedIn or social media
- Financial transactions or payments
- Sharing sensitive information
- Any action requiring human oversight

## Approval File Schema

```markdown
---
type: approval_request
action: [action_type]
[relevant metadata fields]
created: [ISO timestamp]
expires: [ISO timestamp]
status: [pending|approved|rejected]
---

# Approval Request: [Clear Title]

## Action Details
[Specific details about what needs approval]

## To Approve
Move this file to `/Approved` folder.

## To Reject
Move this file to `/Rejected` folder.

---

## Processing Log
- **Created**: [timestamp]
- **Status**: pending
```

## Steps

### 1. Identify Actions Requiring Approval
```
Always require approval:
- Sending external emails
- Social media posts
- Financial transactions
- Legal/contract communications
- Sharing confidential info

Never require approval:
- Internal documentation
- Reading/analyzing content
- Moving files between vault folders
- Updating dashboard
```

### 2. Create Approval Request File
```
Location: /Pending_Approval/APPROVAL_[TYPE]_[TIMESTAMP].md

Include:
- Clear action description
- All relevant details
- Deadline if time-sensitive
- Simple approve/reject instructions
```

### 3. Wait for Human Decision
```
Monitor /Pending_Approval folder:
- File moved to /Approved → Proceed with action
- File moved to /Rejected → Log and notify
- No action by expiry → Send reminder or escalate
```

### 4. Process Approval
```
If Approved:
1. Read approval file from /Approved
2. Execute the approved action
3. Log execution details
4. Move to /Done or archive
5. Update Dashboard

If Rejected:
1. Read rejection reason if provided
2. Log rejection
3. Notify relevant parties if needed
4. Move to /Rejected archive
5. Update Dashboard
```

### 5. Handle Expiry
```
If expired without decision:
1. Check if still relevant
2. Send reminder (create Needs_Action file)
3. Or mark as expired and archive
```

## Approval Request Templates

### Email Approval
```markdown
---
type: approval_request
action: send_email
recipient: client@example.com
subject: Invoice #1234 Follow-up
created: 2026-02-23T10:30:00Z
expires: 2026-02-24T10:30:00Z
status: pending
---

# Approval Request: Send Email to Client

## Action Details
- **Type**: Send Email
- **To**: client@example.com
- **Subject**: Invoice #1234 Follow-up
- **Body Preview**: Dear Client, Following up on overdue invoice...

## Full Email Body

Dear Client,

[Full email content here]

Best regards,
AI Employee

---

## To Approve
Move this file to `/Approved` folder.

## To Reject
Move this file to `/Rejected` folder with a comment.

---

## Processing Log
- **Created**: 2026-02-23T10:30:00Z
- **Status**: Pending human approval
```

### LinkedIn Post Approval
```markdown
---
type: approval_request
action: linkedin_post
visibility: public
created: 2026-02-23T11:00:00Z
expires: 2026-02-24T11:00:00Z
status: pending
content_length: 450
---

# Approval Request: LinkedIn Post

## Action Details
- **Type**: LinkedIn Post
- **Visibility**: Public
- **Content Length**: 450 characters

## Post Content

[Full post content here]

---

## To Approve
Move this file to `/Approved` folder.

## To Reject
Move this file to `/Rejected` folder with a comment.

---

## Processing Log
- **Created**: 2026-02-23T11:00:00Z
- **Status**: Pending human approval
```

### Generic Action Approval
```markdown
---
type: approval_request
action: [action_name]
[custom fields as needed]
created: [timestamp]
expires: [timestamp]
status: pending
---

# Approval Request: [Action Title]

## Action Details
- **Type**: [Action type]
- **Description**: [What will be done]
- **Impact**: [What effect this will have]

## Details
[Full details about the action]

---

## To Approve
Move this file to `/Approved` folder.

## To Reject
Move this file to `/Rejected` folder with a comment.

---

## Processing Log
- **Created**: [timestamp]
- **Status**: Pending human approval
```

## Orchestrator Integration

### Watch Approved Folder
```python
def check_approved_actions(self):
    """Check /Approved folder for actions to execute"""
    approved = list(self.approved_folder.glob('*.md'))

    for file in approved:
        content = file.read_text()
        action_type = extract_action_type(content)

        if action_type == 'send_email':
            self.execute_email_send(file)
        elif action_type == 'linkedin_post':
            self.execute_linkedin_post(file)
        # ... other action types
```

### Update Dashboard
```markdown
## Pending Approvals
| Request | Type | Created | Expires | Status |
|---------|------|---------|---------|--------|
| APPROVAL_... | Email | 2026-02-23 | 2026-02-24 | Pending |

## Recent Approvals
- [x] APPROVAL_... - Email sent (2026-02-23)
- [ ] APPROVAL_... - Awaiting execution
```

## Best Practices

### For AI Employee
- Always err on side of caution - if unsure, request approval
- Make approval requests clear and complete
- Include all context needed for decision
- Set reasonable expiry times (24 hours standard)
- Follow up on pending approvals

### For Humans
- Review approvals daily
- Provide clear rejection reasons
- Move files promptly to avoid delays
- Add notes for future reference

## Error Handling

### Approval File Missing
```
If approval file is missing after approval:
1. Check /Approved and /Rejected folders
2. Search for file in vault
3. If truly missing, create new approval request
4. Log the incident
```

### Expired Approval
```
If approval expires:
1. Check if action is still needed
2. If yes, create reminder for human
3. If no, archive with "expired" status
4. Log and update Dashboard
```

### Action Execution Failed
```
If approved action fails:
1. Log the error details
2. Create Needs_Action file for investigation
3. Notify human via alert
4. Do not retry without re-approval
```

## Related Skills
- [[../email]] - Email sending requires approval
- [[../linkedin]] - LinkedIn posting requires approval
- [[../plan-creator]] - Plans may include approval steps
