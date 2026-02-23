#!/usr/bin/env node
/**
 * Email MCP Server
 * Provides email capabilities for Claude Code agents
 * 
 * Capabilities:
 * - send_email(to, subject, body, cc?, bcc?)
 * - draft_email(to, subject, body)
 * - search_emails(query, max_results)
 * - mark_read(message_id)
 */

import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import { z } from "zod";
import { google } from 'googleapis';
import { readFileSync, existsSync } from 'fs';
import { join, dirname } from 'path';
import { fileURLToPath } from 'url';

const __dirname = dirname(fileURLToPath(import.meta.url));

// Configuration paths
const CONFIG_DIR = join(__dirname, '..', '..', 'config');
const CREDENTIALS_PATH = join(CONFIG_DIR, 'gmail_credentials.json');
const TOKEN_PATH = join(CONFIG_DIR, 'gmail_token.json');

// Gmail API scopes
const SCOPES = ['https://www.googleapis.com/auth/gmail.send', 'https://www.googleapis.com/auth/gmail.compose', 'https://www.googleapis.com/auth/gmail.readonly'];

let gmailService = null;
let oauth2Client = null;

/**
 * Load or create OAuth2 client
 */
function getOAuth2Client() {
  if (oauth2Client) {
    return oauth2Client;
  }

  if (!existsSync(CREDENTIALS_PATH)) {
    throw new Error(`Credentials file not found: ${CREDENTIALS_PATH}. Please add Gmail API credentials.`);
  }

  const credentials = JSON.parse(readFileSync(CREDENTIALS_PATH, 'utf-8'));
  
  oauth2Client = new google.auth.OAuth2(
    credentials.web.client_id,
    credentials.web.client_secret,
    credentials.web.redirect_uris[0]
  );

  // Load existing token
  if (existsSync(TOKEN_PATH)) {
    const token = JSON.parse(readFileSync(TOKEN_PATH, 'utf-8'));
    oauth2Client.setCredentials(token);
  }

  return oauth2Client;
}

/**
 * Get Gmail service with authentication
 */
async function getGmailService() {
  if (gmailService) {
    return gmailService;
  }

  const auth = getOAuth2Client();
  
  // Check if token needs refresh
  if (!auth.credentials.access_token) {
    throw new Error('No Gmail token found. Please authenticate first.');
  }

  gmailService = google.gmail({ version: 'v1', auth });
  return gmailService;
}

/**
 * Create the MCP server
 */
const server = new McpServer({
  name: "email-mcp-server",
  version: "1.0.0",
  description: "Gmail email operations for AI Employee"
});

/**
 * Send email tool
 */
server.tool(
  "send_email",
  "Send an email via Gmail",
  {
    to: z.string().email().describe("Recipient email address"),
    subject: z.string().describe("Email subject"),
    body: z.string().describe("Email body content"),
    cc: z.string().optional().describe("CC recipients (comma-separated)"),
    bcc: z.string().optional().describe("BCC recipients (comma-separated)")
  },
  async ({ to, subject, body, cc, bcc }) => {
    try {
      const service = await getGmailService();
      
      // Create email message
      const message = createEmailMessage(to, subject, body, cc, bcc);
      
      // Send email
      const response = await service.users.messages.send({
        userId: 'me',
        requestBody: {
          raw: message
        }
      });

      return {
        content: [
          {
            type: "text",
            text: `Email sent successfully! Message ID: ${response.data.id}`
          }
        ]
      };
    } catch (error) {
      return {
        content: [
          {
            type: "text",
            text: `Failed to send email: ${error.message}`
          }
        ],
        isError: true
      };
    }
  }
);

/**
 * Draft email tool (creates draft without sending)
 */
server.tool(
  "draft_email",
  "Create an email draft without sending (for approval workflow)",
  {
    to: z.string().email().describe("Recipient email address"),
    subject: z.string().describe("Email subject"),
    body: z.string().describe("Email body content"),
    cc: z.string().optional().describe("CC recipients (comma-separated)")
  },
  async ({ to, subject, body, cc }) => {
    try {
      const service = await getGmailService();
      
      // Create email message
      const message = createEmailMessage(to, subject, body, cc);
      
      // Create draft
      const response = await service.users.drafts.create({
        userId: 'me',
        requestBody: {
          message: {
            raw: message
          }
        }
      });

      return {
        content: [
          {
            type: "text",
            text: `Email draft created! Draft ID: ${response.data.id}. Review in Gmail drafts folder.`
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
 * Search emails tool
 */
server.tool(
  "search_emails",
  "Search Gmail for messages matching a query",
  {
    query: z.string().describe("Gmail search query (e.g., 'is:unread', 'from:client', 'subject:invoice')"),
    max_results: z.number().default(10).describe("Maximum number of results to return")
  },
  async ({ query, max_results }) => {
    try {
      const service = await getGmailService();
      
      const response = await service.users.messages.list({
        userId: 'me',
        q: query,
        maxResults: max_results
      });

      const messages = response.data.messages || [];
      
      if (messages.length === 0) {
        return {
          content: [
            {
              type: "text",
              text: "No messages found matching your query."
            }
          ]
        };
      }

      // Get details for each message
      const details = [];
      for (const msg of messages.slice(0, 5)) { // Limit details to 5
        const detail = await service.users.messages.get({
          userId: 'me',
          id: msg.id,
          format: 'metadata',
          metadataHeaders: ['From', 'To', 'Subject', 'Date']
        });
        
        const headers = detail.data.payload.headers;
        details.push({
          id: msg.id,
          from: headers.find(h => h.name === 'From')?.value || 'Unknown',
          subject: headers.find(h => h.name === 'Subject')?.value || 'No Subject',
          date: headers.find(h => h.name === 'Date')?.value || 'Unknown'
        });
      }

      return {
        content: [
          {
            type: "text",
            text: `Found ${messages.length} messages.\n\nRecent messages:\n${details.map(d => `- [${d.date}] ${d.from}: ${d.subject} (ID: ${d.id})`).join('\n')}`
          }
        ]
      };
    } catch (error) {
      return {
        content: [
          {
            type: "text",
            text: `Failed to search emails: ${error.message}`
          }
        ],
        isError: true
      };
    }
  }
);

/**
 * Mark email as read tool
 */
server.tool(
  "mark_read",
  "Mark an email as read",
  {
    message_id: z.string().describe("Gmail message ID to mark as read")
  },
  async ({ message_id }) => {
    try {
      const service = await getGmailService();
      
      await service.users.messages.modify({
        userId: 'me',
        id: message_id,
        requestBody: {
          removeLabelIds: ['UNREAD']
        }
      });

      return {
        content: [
          {
            type: "text",
            text: `Message ${message_id} marked as read.`
          }
        ]
      };
    } catch (error) {
      return {
        content: [
          {
            type: "text",
            text: `Failed to mark as read: ${error.message}`
          }
        ],
        isError: true
      };
    }
  }
);

/**
 * Helper function to create RFC2822 email message
 */
function createEmailMessage(to, subject, body, cc, bcc) {
  const lines = [
    `To: ${to}`,
    `Subject: ${subject}`,
    `MIME-Version: 1.0`,
    `Content-Type: text/plain; charset="UTF-8"`,
    `Content-Transfer-Encoding: 7bit`,
    ``
  ];

  if (cc) {
    lines.splice(1, 0, `CC: ${cc}`);
  }

  lines.push(body);

  const message = lines.join('\n');
  return Buffer.from(message).toString('base64').replace(/\+/g, '-').replace(/\//g, '_').replace(/=+$/, '');
}

/**
 * Start the server
 */
async function main() {
  const transport = new StdioServerTransport();
  await server.connect(transport);
  console.error("Email MCP Server running on stdio");
}

main().catch((error) => {
  console.error("Fatal error:", error);
  process.exit(1);
});
