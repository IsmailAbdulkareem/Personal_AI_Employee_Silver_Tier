#!/bin/bash
# Setup MCP Servers for AI Employee Silver Tier
# This script installs and configures all MCP servers

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
MCP_DIR="$PROJECT_DIR/mcp_servers"

echo "========================================"
echo "AI Employee Silver Tier - MCP Server Setup"
echo "========================================"
echo ""

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed."
    echo "Please install Node.js from https://nodejs.org/"
    exit 1
fi

echo "✅ Node.js found: $(node --version)"

# Check if npm is installed
if ! command -v npm &> /dev/null; then
    echo "❌ npm is not installed."
    echo "Please install npm (comes with Node.js)"
    exit 1
fi

echo "✅ npm found: $(npm --version)"
echo ""

# Setup Email MCP Server
echo "----------------------------------------"
echo "Setting up Email MCP Server..."
echo "----------------------------------------"
EMAIL_MCP_DIR="$MCP_DIR/email_mcp"

if [ -d "$EMAIL_MCP_DIR" ]; then
    cd "$EMAIL_MCP_DIR"
    
    echo "Installing dependencies..."
    npm install
    
    echo "✅ Email MCP Server installed"
else
    echo "❌ Email MCP directory not found: $EMAIL_MCP_DIR"
fi

echo ""

# Setup LinkedIn MCP Server
echo "----------------------------------------"
echo "Setting up LinkedIn MCP Server..."
echo "----------------------------------------"
LINKEDIN_MCP_DIR="$MCP_DIR/linkedin_mcp"

if [ -d "$LINKEDIN_MCP_DIR" ]; then
    cd "$LINKEDIN_MCP_DIR"
    
    echo "Installing dependencies..."
    npm install
    
    echo "✅ LinkedIn MCP Server installed"
else
    echo "❌ LinkedIn MCP directory not found: $LINKEDIN_MCP_DIR"
fi

echo ""
echo "========================================"
echo "MCP Server Setup Complete!"
echo "========================================"
echo ""
echo "Next Steps:"
echo "1. Configure Gmail API credentials:"
echo "   - See config/GMAIL_SETUP.md"
echo "   - Place credentials in config/gmail_credentials.json"
echo ""
echo "2. Configure MCP servers in Claude Code settings:"
echo "   - Add MCP server paths to ~/.claude/settings.json"
echo ""
echo "3. Test MCP servers:"
echo "   - cd mcp_servers/email_mcp && npm start"
echo "   - cd mcp_servers/linkedin_mcp && npm start"
echo ""
echo "========================================"
