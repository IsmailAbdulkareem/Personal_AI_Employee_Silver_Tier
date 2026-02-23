# Skill: Plan Creator (Claude Reasoning Loop)

## Description
Create structured action plans (Plan.md files) for complex tasks requiring multiple steps or coordination.

## When to Use
- Complex task detected in Needs_Action requiring multiple steps
- Task with dependencies or timeline considerations
- Business goal requiring structured approach
- Multi-step approval workflows
- Tasks needing resource coordination

## Steps

### 1. Assess Task Complexity
```
Evaluate if a plan is needed:
- Does this require 3+ action steps?
- Are there dependencies between steps?
- Is there a deadline or timeline?
- Does this need multiple resources/tools?
- Will this take more than 1 hour to complete?

If YES to any → Create a Plan.md
```

### 2. Create Plan.md File
```
Location: /Plans/PLAN_[YYYYMMDD]_[Task_Name].md

Use the Plan Template (see below)
```

### 3. Define Objective Clearly
```
Write a single, clear objective statement:
- What success looks like
- Measurable outcome
- Timeline if applicable
```

### 4. Gather Context
```
Include relevant background:
- Origin of the task (which action file)
- Key stakeholders
- Constraints or requirements
- Related tasks or dependencies
```

### 5. Break Down Action Steps
```
Create actionable, sequential steps:
- Use checkbox format: - [ ]
- Each step should be atomic
- Order by dependency
- Estimate time for each step if possible
```

### 6. Identify Resources
```
List what's needed:
- MCP servers required
- Files or data needed
- People to involve
- Tools or access required
```

### 7. Assess Risks
```
Identify potential issues:
- What could go wrong
- Mitigation strategies
- Fallback options
```

### 8. Define Success Criteria
```
Clear completion markers:
- Measurable outcomes
- Quality standards
- Sign-off requirements
```

## Plan.md Template

```markdown
---
type: action_plan
created: [ISO timestamp]
priority: [high|medium|low]
status: [in_progress|completed|blocked]
estimated_completion: [ISO timestamp]
source: [Original action file if applicable]
---

# Plan: [Clear, Descriptive Title]

## Objective
[Single paragraph describing what this plan achieves]

## Context
- **Origin**: [Where did this task come from]
- **Stakeholders**: [Who is involved/affected]
- **Constraints**: [Any limitations or requirements]
- **Dependencies**: [Related tasks or prerequisites]

## Action Steps
- [ ] Step 1: [First action]
- [ ] Step 2: [Second action]
- [ ] Step 3: [Continue as needed]
- [ ] Step N: [Final action]

## Timeline
| Step | Target Date | Status |
|------|-------------|--------|
| 1    | YYYY-MM-DD  | pending |
| 2    | YYYY-MM-DD  | pending |

## Resources Needed
- [ ] [Resource 1 - e.g., Email MCP server]
- [ ] [Resource 2 - e.g., Client contact info]
- [ ] [Resource 3 - e.g., Template document]

## Risks & Mitigations
| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| [Risk 1] | [High/Med/Low] | [High/Med/Low] | [How to mitigate] |
| [Risk 2] | [High/Med/Low] | [High/Med/Low] | [How to mitigate] |

## Success Criteria
- [ ] [Criterion 1 - measurable outcome]
- [ ] [Criterion 2 - quality standard]
- [ ] [Criterion 3 - sign-off requirement]

---

## Progress Log
| Date | Update | Next Step |
|------|--------|-----------|
| [Date] | [What was done] | [What's next] |

---

## Completion Summary
[To be filled when plan is complete]
- **Completed**: [Date]
- **Outcome**: [What was achieved]
- **Lessons Learned**: [Key takeaways]
```

## Example Plan

```markdown
---
type: action_plan
created: 2026-02-23T10:00:00Z
priority: high
status: in_progress
estimated_completion: 2026-02-23T16:00:00Z
source: EMAIL_20260223_100000_Client_Invoice.md
---

# Plan: Client Invoice Follow-up

## Objective
Follow up on overdue invoice #1234 from Client A and secure payment within 5 business days.

## Context
- **Origin**: Email from accounting system about overdue invoice
- **Stakeholders**: Client A (client), Finance Team (internal)
- **Constraints**: Maintain good client relationship
- **Dependencies**: Invoice details available in vault

## Action Steps
- [ ] Review invoice #1234 details and payment history
- [ ] Draft friendly reminder email
- [ ] Submit email for human approval
- [ ] Send email after approval
- [ ] Schedule follow-up reminder for 3 days
- [ ] Log all actions in client file

## Timeline
| Step | Target Date | Status |
|------|-------------|--------|
| 1    | 2026-02-23  | completed |
| 2    | 2026-02-23  | in_progress |
| 3    | 2026-02-23  | pending |
| 4    | 2026-02-23  | pending |
| 5    | 2026-02-23  | pending |
| 6    | 2026-02-28  | pending |

## Resources Needed
- [x] Email MCP server
- [x] Invoice template
- [x] Client A contact info
- [ ] Approval from human

## Risks & Mitigations
| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Client upset by reminder | Low | Medium | Keep tone professional and helpful |
| Payment delayed further | Medium | High | Offer payment plan if needed |
| Email goes to spam | Low | Medium | Follow up with phone call if no response |

## Success Criteria
- [ ] Email sent and acknowledged by client
- [ ] Payment received within 5 days
- [ ] Client relationship maintained positively

---

## Progress Log
| Date | Update | Next Step |
|------|--------|-----------|
| 2026-02-23 10:00 | Plan created, invoice reviewed | Draft email |
```

## MCP Tools Used
- None directly - this is a documentation skill
- Other MCP tools used within plan execution

## Approval Required
**NO** - Creating plans does not require approval
**YES** - Actions within plans may require approval (check individual steps)

## Plan Status Updates

### Update Progress
```
1. Read current plan from /Plans
2. Update Progress Log with date and update
3. Mark completed steps as - [x]
4. Update status field in frontmatter
5. Save plan
```

### Mark Plan Complete
```
1. Fill in Completion Summary
2. Update status to 'completed'
3. Move plan to /Done folder (optional)
4. Update Dashboard.md with completion
```

## Related Skills
- [[../approval-workflow]] - For actions requiring approval
- [[../email]] - For email-related plan steps
- [[../linkedin]] - For LinkedIn-related plan steps
