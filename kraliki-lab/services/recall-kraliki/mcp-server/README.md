# Recall by Kraliki MCP Server

MCP (Model Context Protocol) server for Claude Code integration.

## Setup

```bash
# From project root
cd mcp-server
python server.py
```

## Configure in Claude Code

Add to your Claude Code settings (`~/.config/claude-code/settings.json`):

```json
{
  "mcpServers": {
    "recall-kraliki": {
      "command": "python",
      "args": ["/home/adminmatej/github/applications/kraliki-lab/services/recall-kraliki/mcp-server/server.py"],
      "env": {
        "ZHIPUAI_API_KEY": "your-api-key-here"
      }
    }
  }
}
```

Or use absolute path from `.env`:

```json
{
  "mcpServers": {
    "recall-kraliki": {
      "command": "python",
      "args": ["/home/adminmatej/github/applications/kraliki-lab/services/recall-kraliki/mcp-server/server.py"],
      "envFile": "/home/adminmatej/github/applications/kraliki-lab/services/recall-kraliki/.env"
    }
  }
}
```

## Available Tools

### `recall_search`
Search the knowledge base using hybrid search (keyword + semantic).

**Usage in Claude Code:**
```
> Search recall for "pricing strategy decisions"
> What did we decide about GLM 4.6?
> Find insights about avatar market
```

**Parameters:**
- `query` (required): Search query
- `category` (optional): Filter by category
- `search_type` (optional): "hybrid" (default), "keyword", or "semantic"
- `limit` (optional): Max results (default: 10)

### `recall_capture`
Save new knowledge items.

**Usage in Claude Code:**
```
> Capture this decision to recall: "Use FastAPI for recall-kraliki backend"
> Save this insight: "Avatar market growing to $117B by 2034"
```

**Parameters:**
- `content` (required): Content to capture
- `category` (optional): Category
- `tags` (optional): Comma-separated tags
- `auto_categorize` (optional): Auto-categorize with AI (default: true)

### `recall_get`
Get full content of specific item.

**Usage in Claude Code:**
```
> Get recall item decisions/dec-2025-10-06-001
```

**Parameters:**
- `category` (required): Item category
- `item_id` (required): Item ID

### `recall_recent`
Get recent items.

**Usage in Claude Code:**
```
> Show recent recalls
> Show recent decisions
```

**Parameters:**
- `category` (optional): Filter by category
- `limit` (optional): Max items (default: 10)

### `recall_patterns`
Detect patterns using AI analysis.

**Usage in Claude Code:**
```
> Analyze patterns in recall
> Find patterns in decisions
```

**Parameters:**
- `category` (optional): Filter by category
- `limit` (optional): Max items to analyze (default: 100)

## Categories

- `decisions` - Strategic decisions
- `insights` - Key insights and learnings
- `ideas` - New ideas and opportunities
- `learnings` - Lessons learned
- `customers` - Customer information
- `competitors` - Competitor analysis
- `research` - Market research
- `sessions` - Session summaries

## Example Workflow

```bash
# In Claude Code session:

> Search recall for "GLM 4.6"
# Returns: Decision to use GLM 4.6 instead of local LLM

> Capture to recall: "Decision: Build recall-kraliki as a core Kraliki memory app alongside Voice by Kraliki and Focus by Kraliki"
# Saved with auto-categorization and auto-linking

> Show recent decisions
# Lists recent decision items

> Analyze patterns in recall
# AI detects: Theme "AI infrastructure decisions", Cluster "Platform architecture", etc.
```

## Architecture

```
Claude Code Session
       ↓
MCP Protocol (stdio)
       ↓
recall-kraliki MCP Server (this)
       ↓
   ┌──────┴──────┐
   ↓             ↓
Storage       GLM 4.6 API
Service       Service
   ↓
Markdown Files
(memory/)
```

## Development

Test MCP server locally:

```bash
# Run server
python server.py

# In another terminal, test with MCP client
# (or use Claude Code)
```

## Troubleshooting

**Server not connecting:**
- Check Python path in MCP config
- Verify `.env` file exists with `ZHIPUAI_API_KEY`
- Check logs: `~/.config/claude-code/logs/`

**Search returns no results:**
- Verify `memory/` directory has content
- Check category names match (lowercase)
- Try different search types

**Auto-categorization fails:**
- Verify GLM 4.6 API key is valid
- Check network connectivity
- Fall back to manual category selection
