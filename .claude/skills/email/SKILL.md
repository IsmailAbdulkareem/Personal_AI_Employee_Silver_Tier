# Skill: Email Processing

## Description
Process incoming emails, draft responses, and send emails via Gmail MCP server.

## When to Use
- New email detected in Gmail (EMAIL_*.md files in Needs_Action)
- Client inquiry needs response
- Invoice/payment email received
- Any email requiring action or response

## Steps

### 1. Read Email from Needs_Action
```
1. Locate EMAIL_*.md file in /Needs_Action folder
2. Read the email metadata and content
3. Analyze urgency based on priority field and keywords
4. Identify the sender's intent and required action
```

### 2. Analyze and Categorize
```
- **Urgent**: Contains keywords (invoice, payment, urgent, ASAP)
- **Client Inquiry**: Questions about services/products
- **Informational**: FYI emails, newsletters
- **Action Required**: Requests needing response or action
```

### 3. Draft Response (if needed)
```
1. Use the "Response Draft" section in the action file
2. Write professional, helpful response
3. Include relevant context and next steps
4. Save the draft in the action file
```

### 4. Create Approval Request (for sending)
```
1. Use email_mcp:draft_email tool to create Gmail draft
   OR
2. Create approval file in /Pending_Approval with:
   - Recipient
   - Subject
   - Full email body
   - Action: send_email
```

### 5. Send After Approval
```
1. Check /Approved folder for approved email requests
2. Use email_mcp:send_email tool to send
3. Mark original email as read using email_mcp:mark_read
4. Move action file to /Done
5. Log the action
```

### 6. Log and Archive
```
1. Add processing log entry to action file
2. Move to /Done folder
3. Update Dashboard.md with completion
```

## MCP Tools Used
- `email_mcp:send_email` - Send emails directly
- `email_mcp:draft_email` - Create drafts for approval
- `email_mcp:search_emails` - Search for related emails
- `email_mcp:mark_read` - Mark processed emails as read

## Approval Required
**YES** - All external email sending requires human approval:
- Sending emails to external recipients
- Forwarding sensitive information
- Responding to legal/financial matters
- Any email with attachments

## Example Workflow

### Input: Email about invoice inquiry
```markdown
---
type: email
from: client@example.com
subject: Invoice #1234 Question
priority: high
---

Hi, I have a question about invoice #1234...
```

### Processing:
1. Read email, identify as billing inquiry
2. Draft response explaining invoice details
3. Create approval request in Pending_Approval
4. Wait for human to move to Approved
5. Send email via MCP
6. Move to Done and log

## Response Templates

### Invoice Inquiry
```
Dear [Name],

Thank you for your inquiry regarding invoice #[number].

[Provide invoice details and clarification]

Please let me know if you have any further questions.

Best regards,
[Your Name]
```

### General Inquiry
```
Dear [Name],

Thank you for reaching out.

[Address their question/concern]

I'm happy to discuss this further if needed.

Best regards,
[Your Name]
```

## Error Handling
- **Authentication Error**: Check Gmail credentials in /config
- **Send Failed**: Verify recipient email address format
- **Draft Not Found**: Re-create draft and retry
- **Token Expired**: Re-authenticate Gmail API

## Related Skills
- [[../approval-workflow]] - For approval process
- [[../plan-creator]] - For complex email tasks requiring plans
