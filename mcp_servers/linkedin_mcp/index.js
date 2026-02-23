#!/usr/bin/env node
/**
 * LinkedIn MCP Server
 * Provides LinkedIn posting capabilities for Claude Code agents
 * 
 * Capabilities:
 * - create_post(content, visibility) - Creates a draft post file for approval
 * - schedule_post(content, scheduled_time) - Schedules a post (requires approval)
 * - get_analytics(post_id) - Get post analytics
 * - draft_post(content) - Create a draft post for review
 * 
 * Note: This server creates approval request files for human-in-the-loop workflow.
 * Direct LinkedIn API integration requires LinkedIn API credentials.
 */

import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import { z } from "zod";
import { writeFileSync, mkdirSync, existsSync } from 'fs';
import { join, dirname } from 'path';
import { fileURLToPath } from 'url';
import { datetime } from 'datetime';

const __dirname = dirname(fileURLToPath(import.meta.url));

// Configuration paths
const VAULT_PATH = join(__dirname, '..', '..', 'AI_Employee_Vault_Silver');
const PENDING_APPROVAL_PATH = join(VAULT_PATH, 'Pending_Approval');

// Ensure directories exist
if (!existsSync(PENDING_APPROVAL_PATH)) {
  mkdirSync(PENDING_APPROVAL_PATH, { recursive: true });
}

/**
 * Create the MCP server
 */
const server = new McpServer({
  name: "linkedin-mcp-server",
  version: "1.0.0",
  description: "LinkedIn posting and engagement for AI Employee"
});

/**
 * Create post tool - creates approval request for human review
 */
server.tool(
  "create_post",
  "Create a LinkedIn post (requires human approval before posting)",
  {
    content: z.string().describe("The post content (max 3000 characters)"),
    visibility: z.enum(['public', 'connections', 'group']).default('public').describe("Post visibility")
  },
  async ({ content, visibility }) => {
    try {
      const timestamp = new Date().toISOString().replace(/[:.]/g, '-').slice(0, -5);
      const approvalFile = `APPROVAL_LINKEDIN_${timestamp}.md`;
      const approvalPath = join(PENDING_APPROVAL_PATH, approvalFile);

      // Truncate content for preview
      const preview = content.length > 200 ? content.slice(0, 200) + '...' : content;

      const approvalContent = `---
type: approval_request
action: linkedin_post
visibility: ${visibility}
created: ${new Date().toISOString()}
expires: ${new Date(Date.now() + 24 * 60 * 60 * 1000).toISOString()}
status: pending
content_length: ${content.length}
---

# LinkedIn Post Approval Request

## Post Details
- **Action**: Create LinkedIn Post
- **Visibility**: ${visibility}
- **Content Length**: ${content.length} characters
- **Created**: ${new Date().toISOString()}

## Post Content

${content}

---

## To Approve
1. Review the post content above
2. Move this file to \`/Approved\` folder to proceed with posting
3. Or move to \`/Rejected\` to cancel

## To Reject
Move this file to \`/Rejected\` folder with a comment explaining why.

---

## Processing Log
- **Request Created**: ${new Date().toISOString()}
- **Status**: Pending human approval
`;

      writeFileSync(approvalPath, approvalContent, 'utf-8');

      return {
        content: [
          {
            type: "text",
            text: `LinkedIn post approval request created: ${approvalFile}\n\nPreview: "${preview}"\n\nPlease review and move the file from Pending_Approval to Approved when ready to post.`
          }
        ]
      };
    } catch (error) {
      return {
        content: [
          {
            type: "text",
            text: `Failed to create post approval request: ${error.message}`
          }
        ],
        isError: true
      };
    }
  }
);

/**
 * Schedule post tool - creates approval request for scheduled posting
 */
server.tool(
  "schedule_post",
  "Schedule a LinkedIn post for later (requires human approval)",
  {
    content: z.string().describe("The post content"),
    scheduled_time: z.string().describe("ISO 8601 formatted date/time for posting (e.g., 2026-02-24T09:00:00Z)"),
    visibility: z.enum(['public', 'connections', 'group']).default('public').describe("Post visibility")
  },
  async ({ content, scheduled_time, visibility }) => {
    try {
      const timestamp = new Date().toISOString().replace(/[:.]/g, '-').slice(0, -5);
      const approvalFile = `APPROVAL_LINKEDIN_SCHEDULED_${timestamp}.md`;
      const approvalPath = join(PENDING_APPROVAL_PATH, approvalFile);

      const scheduledDate = new Date(scheduled_time);
      const preview = content.length > 200 ? content.slice(0, 200) + '...' : content;

      const approvalContent = `---
type: approval_request
action: linkedin_post_scheduled
visibility: ${visibility}
scheduled_time: ${scheduled_time}
created: ${new Date().toISOString()}
expires: ${scheduled_time}
status: pending
content_length: ${content.length}
---

# Scheduled LinkedIn Post Approval Request

## Post Details
- **Action**: Schedule LinkedIn Post
- **Visibility**: ${visibility}
- **Scheduled For**: ${scheduledDate.toLocaleString()}
- **Content Length**: ${content.length} characters
- **Created**: ${new Date().toISOString()}

## Post Content

${content}

---

## To Approve
1. Review the post content and scheduled time
2. Move this file to \`/Approved\` folder to confirm scheduling
3. Or move to \`/Rejected\` to cancel

## To Reject
Move this file to \`/Rejected\` folder with a comment explaining why.

---

## Processing Log
- **Request Created**: ${new Date().toISOString()}
- **Scheduled For**: ${scheduled_time}
- **Status**: Pending human approval
`;

      writeFileSync(approvalPath, approvalContent, 'utf-8');

      return {
        content: [
          {
            type: "text",
            text: `Scheduled LinkedIn post approval request created: ${approvalFile}\n\nScheduled for: ${scheduledDate.toLocaleString()}\nPreview: "${preview}"`
          }
        ]
      };
    } catch (error) {
      return {
        content: [
          {
            type: "text",
            text: `Failed to create scheduled post approval request: ${error.message}`
          }
        ],
        isError: true
      };
    }
  }
);

/**
 * Get analytics tool - placeholder for future LinkedIn API integration
 */
server.tool(
  "get_analytics",
  "Get analytics for a LinkedIn post (placeholder - requires LinkedIn API)",
  {
    post_id: z.string().describe("LinkedIn post ID")
  },
  async ({ post_id }) => {
    // Placeholder - LinkedIn API integration would go here
    return {
      content: [
        {
          type: "text",
          text: `Analytics for post ${post_id}:\n\nNote: LinkedIn API integration not yet configured.\n\nTo enable analytics:\n1. Set up LinkedIn API credentials\n2. Configure OAuth for LinkedIn API access\n3. Implement analytics fetching in the MCP server\n\nFor now, you can manually check post performance on LinkedIn.`
        }
      ]
    };
  }
);

/**
 * Draft post tool - creates a draft without approval workflow
 */
server.tool(
  "draft_post",
  "Create a draft LinkedIn post for review (no approval workflow)",
  {
    content: z.string().describe("The post content"),
    notes: z.string().optional().describe("Optional notes about the post")
  },
  async ({ content, notes }) => {
    try {
      const timestamp = new Date().toISOString().replace(/[:.]/g, '-').slice(0, -5);
      const draftFile = `DRAFT_LINKEDIN_${timestamp}.md`;
      const draftsPath = join(VAULT_PATH, 'Plans');
      
      if (!existsSync(draftsPath)) {
        mkdirSync(draftsPath, { recursive: true });
      }

      const draftContent = `---
type: linkedin_draft
created: ${new Date().toISOString()}
status: draft
content_length: ${content.length}
${notes ? `notes: ${notes}` : ''}
---

# LinkedIn Post Draft

## Created
${new Date().toISOString()}

## Content

${content}

${notes ? `\n## Notes\n${notes}\n` : ''}
---
## Next Steps
- [ ] Review content
- [ ] Edit if needed
- [ ] Submit for approval using create_post tool
- [ ] Post to LinkedIn
`;

      const draftPath = join(draftsPath, draftFile);
      writeFileSync(draftPath, draftContent, 'utf-8');

      return {
        content: [
          {
            type: "text",
            text: `LinkedIn post draft created: ${draftFile}\n\nSaved to Plans folder for review.`
          }
        ]
      };
    } catch (error) {
      return {
        content: [
          {
            type: "text",
            text: `Failed to create draft: ${error.message}`
          }
        ],
        isError: true
      };
    }
  }
);

/**
 * Start the server
 */
async function main() {
  const transport = new StdioServerTransport();
  await server.connect(transport);
  console.error("LinkedIn MCP Server running on stdio");
}

main().catch((error) => {
  console.error("Fatal error:", error);
  process.exit(1);
});
