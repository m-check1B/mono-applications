# HW-026: MCP OAuth Setup for Gemini & OpenCode

**Priority:** Medium
**Blocks:** Gemini/OpenCode agents using Linear directly
**Created:** 2025-12-22

## What's Needed

Both Gemini CLI and OpenCode now have Linear MCP configured, but need OAuth authentication (requires browser).

### For Gemini:
```bash
cd /home/adminmatej/github
gemini  # Start interactive session, it will prompt for OAuth
```

### For OpenCode:
```bash
opencode mcp auth linear
```

## Configuration Already Done

**Gemini** (`/github/.gemini/settings.json`):
```json
{
  "mcpServers": {
    "linear": {
      "httpUrl": "https://mcp.linear.app/mcp"
    }
  }
}
```

**OpenCode** (`~/.config/opencode/opencode.json`):
```json
{
  "mcp": {
    "linear": {
      "type": "remote",
      "url": "https://mcp.linear.app/mcp",
      "enabled": true,
      "oauth": { "scope": "read write" }
    }
  }
}
```

## Workaround

Until OAuth is set up, Gemini/OpenCode agents can still:
- Use blackboard_bridge.py for coordination
- Use memory.py for persistence
- Do file-based work (editing, coding)
- Be delegated tasks via ./delegate.sh

Just no direct Linear API access.
