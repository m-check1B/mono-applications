# Focus MCP Server

Exposes Focus capabilities to Kraliki agents via Model Context Protocol (MCP).

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Run server
FOCUS_API_URL=http://127.0.0.1:8000 \
FOCUS_MCP_TOKEN=your-jwt-token \
python server.py
```

## Tools

| Tool | Description |
|------|-------------|
| `focus_get_tasks` | Get tasks by status/priority/project |
| `focus_create_task` | Create a new task |
| `focus_update_task` | Update task status/notes |
| `focus_get_daily_plan` | Get Brain's daily plan |
| `focus_ask_brain` | Ask Brain a question |
| `focus_log_work` | Log time entry |
| `focus_get_projects` | Get active projects |
| `focus_capture` | AI-first capture (idea/note/task) |
| `focus_search` | Search Focus data |

## Resources

| URI | Description |
|-----|-------------|
| `focus://tasks/{id}` | Task details |
| `focus://projects/{id}` | Project with tasks |
| `focus://brain/context` | AI context |
| `focus://brain/priorities` | Prioritized tasks |
| `focus://knowledge/{id}` | Knowledge item |
| `focus://summary` | All items summary |

## Claude Code Integration

Add to `.claude/settings.json`:

```json
{
  "mcpServers": {
    "focus": {
      "command": "python",
      "args": ["/path/to/mcp-server/server.py"],
      "env": {
        "FOCUS_API_URL": "http://127.0.0.1:8000",
        "FOCUS_MCP_TOKEN": "${FOCUS_TOKEN}"
      }
    }
  }
}
```

## Agent Permissions

| Agent Type | Scopes |
|------------|--------|
| builder | read:tasks, update:tasks, create:tasks |
| caretaker | read:* |
| business | read:goals, read:projects |
| orchestrator | * (full access) |
