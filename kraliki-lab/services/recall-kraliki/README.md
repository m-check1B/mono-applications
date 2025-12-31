# Recall by Kraliki 🎯

**Instant recall of every decision, insight, and learning**

Persistent knowledge system for AI-powered businesses. Capture every decision, insight, learning - and recall them instantly across sessions.

========================================
ONE PRODUCT / ONE ENGINE / MANY TEMPLATES
Recall is an internal memory module for Kraliki Swarm.
========================================

## 🎯 What is Recall by Kraliki?

Recall by Kraliki is a hybrid knowledge graph system that solves the "AI amnesia" problem - when AI assistants forget everything between sessions. It combines:

- **Markdown storage** with wikilinks (Obsidian-compatible)
- **Hybrid search** (keyword + semantic via GLM 4.6)
- **Knowledge graph** visualization
- **Auto-categorization** and pattern detection
- **MCP integration** for Claude Code
- **Cross-session persistence**

## 🏗️ Architecture

```
recall-kraliki/
├── backend/         # FastAPI + GLM 4.6 API
├── frontend/        # SvelteKit 2.0 UI
├── memory/          # Markdown knowledge base
│   ├── decisions/
│   ├── insights/
│   ├── ideas/
│   ├── learnings/
│   ├── customers/
│   ├── competitors/
│   └── research/
└── mcp-server/      # MCP server for Claude Code
```

## 🚀 Quick Start

### 1. Environment Setup

```bash
# Copy .env.example to .env
cp .env.example .env

# Edit .env and add your ZhipuAI API key
# ZHIPUAI_API_KEY=your-api-key-here
```

### 2. Backend Setup

```bash
cd backend

# Create virtual environment
python3 -m venv .venv

# Activate virtual environment
source .venv/bin/activate  # Linux/Mac
# or
.venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt

# Run backend server
uvicorn app.main:app --reload --host 127.0.0.1 --port 3020
```

**Backend URLs:**
- API: http://127.0.0.1:3020
- Interactive docs: http://127.0.0.1:3020/docs
- Health check: http://127.0.0.1:3020/health

### 3. Frontend Setup

```bash
cd frontend

# Install dependencies
pnpm install

# Run development server
pnpm dev --host 127.0.0.1 --port 5176
```

**Frontend URL:** http://127.0.0.1:5176

### 4. Usage

- **Search**: Navigate to frontend homepage to search knowledge base
- **Capture**: Go to `/capture` to save new items
- **Recent**: Browse `/recent` for latest captures
- **Graph**: View `/graph` for knowledge connections

## 🤖 MCP Integration (Claude Code)

Add to your Claude Code settings (`~/.config/claude-code/settings.json`):

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

**Available MCP Tools:**
- `recall_search`: Search knowledge base
- `recall_capture`: Save new items
- `recall_get`: Get specific item
- `recall_recent`: Browse recent items
- `recall_patterns`: Detect patterns with AI

See `mcp-server/README.md` for detailed MCP documentation.

## 💡 Core Features

### Phase 1 (Internal Use - Q1 2026)
- ✅ Markdown storage with wikilinks
- ✅ Basic search (keyword + semantic)
- ✅ MCP integration
- ✅ Auto-categorization (GLM 4.6)
- ✅ Knowledge graph visualization

### Phase 2 (Closed Beta - Q2-Q3 2026)
- 🔮 Team collaboration
- 🔮 Advanced pattern detection
- 🔮 Proactive insight surfacing
- 🔮 Custom taxonomies
- 🔮 Export/import

### Phase 3 (Public Launch - Q3 2026)
- 🔮 Multi-user SaaS
- 🔮 API access
- 🔮 Third-party integrations
- 🔮 Self-hosted option
- 🔮 White-label capability

## 📊 Tech Stack

| Layer | Technology |
|-------|------------|
| Frontend | SvelteKit 2.0 + TypeScript + Tailwind |
| Backend | FastAPI + SQLAlchemy |
| AI | GLM 4.6 API (ZhipuAI) |
| Storage | Markdown + wikilinks |
| Search | Hybrid (keyword + semantic) |
| MCP | FastMCP framework |

## 🎯 Use Cases

**For AI Consultancies:**
- Never lose client context between sessions
- Searchable decision history
- Pattern detection across projects

**For Professional Services:**
- Institutional knowledge preservation
- Team-wide knowledge sharing
- Client relationship management

**For Development Teams:**
- Architecture decision records
- Technical learnings database
- Project retrospectives

## 💰 Pricing (Future)

- **Solo**: $29/month
- **Professional**: $99/month (1-3 users)
- **Business**: $299/month (unlimited users)
- **Enterprise**: Custom (self-hosted, white-label)

## 📈 Status

**Current Phase**: Internal incubation (Q1 2026)
- Using for Ocelot business operations
- Building case study with real metrics
- Iterating based on actual usage

**Target**: Public launch Q3 2026

## 🤝 Related Projects

- **Kraliki Platform**: `/applications/kraliki-swarm` (swarm control)
- **Voice by Kraliki**: Call center AI (legacy Voice by Kraliki)
- **Focus by Kraliki**: Planning & project management

## 📄 License

Proprietary - Internal use only during incubation phase

---

**Built with ❤️ in Prague by Ocelot Intelligence**
