# Skill: LinkedIn Engagement and Posting

## Description
Monitor LinkedIn for opportunities, create engaging posts, and manage professional networking activities.

## When to Use
- LinkedIn opportunity detected (LINKEDIN_*.md files in Needs_Action)
- Business update needs to be shared
- Engagement with potential clients needed
- Regular content posting for visibility

## Steps

### 1. Read LinkedIn Action File
```
1. Locate LINKEDIN_POST_*.md or LINKEDIN_MSG_*.md in /Needs_Action
2. Review the matched keywords and opportunity type
3. Assess the engagement potential
```

### 2. Categorize Opportunity
```
- **Sales Lead**: Keywords (hiring, need help, looking for, RFP)
- **Networking**: Connection requests, collaboration offers
- **Engagement**: Posts worth commenting on for visibility
- **Message**: Direct messages requiring response
```

### 3. Create Engagement Strategy
```
For Posts:
- Determine if comment adds value
- Draft insightful comment (not promotional)
- Consider connection request if relevant

For Messages:
- Assess urgency and intent
- Draft professional response
- Schedule call/meeting if needed

For Sales Leads:
- Create action plan for outreach
- Draft personalized message
- Submit for approval
```

### 4. Create Post Content (if applicable)
```
1. Identify business goal or update to share
2. Draft post following LinkedIn best practices:
   - Hook in first 2-3 lines
   - Clear, valuable message
   - Call-to-action if appropriate
   - Relevant hashtags (3-5)
3. Use linkedin_mcp:draft_post for review
4. Submit for approval via linkedin_mcp:create_post
```

### 5. Execute Engagement
```
For Comments:
1. Draft comment in action file
2. Get approval if sensitive/promotional
3. Post via browser or approved workflow

For Messages:
1. Draft response
2. Get approval
3. Send via LinkedIn

For Posts:
1. Create approval request via MCP
2. Wait for approval
3. Post when approved
```

### 6. Log and Track
```
1. Record engagement in action file
2. Note any follow-ups needed
3. Move to /Done
4. Update Dashboard metrics
```

## MCP Tools Used
- `linkedin_mcp:create_post` - Create post with approval workflow
- `linkedin_mcp:schedule_post` - Schedule posts for later
- `linkedin_mcp:draft_post` - Create drafts for review
- `linkedin_mcp:get_analytics` - Get post performance (when available)

## Approval Required
**YES** - All LinkedIn posts require human approval:
- Public posts about business
- Responses to sensitive topics
- Connection messages to prospects
- Any content representing the business

## Post Content Guidelines

### Good Post Structure
```
[HOOK - Grab attention in 1-2 lines]

[VALUE - Share insight, story, or lesson]

[TAKEAWAY - Clear point or lesson]

[CTA - Optional call-to-action]

[HASHTAGS - 3-5 relevant tags]
```

### Example: Service Announcement
```
Just helped a client save 20 hours/week with automation.

The secret? Start with the repetitive tasks that drain your energy.

Here's my 3-step framework:
1. Identify the bottleneck
2. Map the workflow
3. Implement the solution

What's one task you wish you could automate?

#automation #productivity #business
```

### Example: Engagement Comment
```
Great insights, [Name]! I've found that [add specific value/insight].

One thing that's worked well for us is [brief example]. Thanks for sharing!
```

## Response Templates

### Connection Request Acceptance
```
Hi [Name],

Thanks for connecting! I see you're [their role/industry].

I specialize in [your value prop]. Always happy to connect with fellow professionals.

Best,
[Your Name]
```

### Sales Lead Response
```
Hi [Name],

I noticed your post about [their need]. This is exactly what we help with.

We've helped similar [their industry] companies [specific result].

Would you be open to a quick 15-min chat to explore if there's a fit?

Best,
[Your Name]
```

## Best Practices

### Do's
- Post consistently (2-3x per week)
- Add genuine value in comments
- Personalize connection requests
- Respond to comments on your posts
- Share authentic stories and lessons

### Don'ts
- Overly promotional content
- Generic copy-paste messages
- Engagement bait ("Like this if...")
- Controversial topics (politics, religion)
- Posting without approval

## Error Handling
- **Post Failed**: Check content length (max 3000 chars)
- **Approval Pending**: Wait for human approval in /Approved
- **Session Expired**: Re-login to LinkedIn in watcher
- **Rate Limited**: Wait 24 hours before next action

## Related Skills
- [[../approval-workflow]] - For approval process
- [[../email]] - For follow-up email communication
- [[../plan-creator]] - For complex campaigns
