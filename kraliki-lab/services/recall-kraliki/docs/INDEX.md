# Recall by Kraliki Documentation

**Complete documentation for Recall by Kraliki persistent knowledge system.**

## Quick Navigation

### 🚀 Getting Started
- **[GETTING-STARTED.md](GETTING-STARTED.md)** - 5-minute quick start guide
  - Start the system
  - Capture your first item
  - Search and find
  - Daily workflow

### 📖 User Guide
- **[USER-GUIDE.md](USER-GUIDE.md)** - Complete user manual
  - Core concepts
  - Capture workflows (5 types)
  - Search strategies
  - Knowledge graph
  - Advanced features
  - Best practices

### 🔧 Troubleshooting
- **[TROUBLESHOOTING.md](TROUBLESHOOTING.md)** - Solutions to common issues
  - Backend issues
  - Frontend issues
  - Search problems
  - Capture problems
  - Graph issues
  - Dark mode issues
  - Performance
  - MCP server

### 🤖 Technical Documentation
- **[CLAUDE.md](CLAUDE.md)** - AI assistant development guide
  - Stack 2026 compliance
  - Architecture overview
  - Development commands
  - Repository structure

## Documentation by Role

### For Users (Non-Technical)
1. Start with [GETTING-STARTED.md](GETTING-STARTED.md)
2. Bookmark key workflows from [USER-GUIDE.md](USER-GUIDE.md)
3. Keep [TROUBLESHOOTING.md](TROUBLESHOOTING.md) handy

### For Developers
1. Read [CLAUDE.md](CLAUDE.md) for architecture
2. Check [../README.md](../README.md) for setup
3. Review [TEST-RESULTS.md](../TEST-RESULTS.md) for testing

### For Business Stakeholders
1. Read [GETTING-STARTED.md](GETTING-STARTED.md) → "Daily Workflow"
2. Review [USER-GUIDE.md](USER-GUIDE.md) → "Best Practices"
3. Check [../TOP-LEVEL-BUSINESS-PLAN.md](../../ocelot-business/TOP-LEVEL-BUSINESS-PLAN.md)

## Quick Reference

### Common Tasks

**Capture a decision:**
```markdown
# Decision: [Title]

## Context
[What led to this?]

## Decision
[What we decided]

## Related
- [[category/id|description]]
```

**Search for something:**
1. Open http://127.0.0.1:5176
2. Type query
3. Select search type (hybrid recommended)
4. Click Search

**View knowledge graph:**
1. Click "Graph" in navigation
2. Filter by category if needed
3. Look for patterns and connections

**Enable dark mode:**
1. Click 🌙 button (top right)
2. Theme persists automatically

### File Locations

```
recall-kraliki/
├── backend/              # FastAPI backend
│   ├── app/
│   │   ├── main.py      # API server
│   │   ├── api/         # Routes (search, capture, graph)
│   │   └── services/    # GLM 4.6, storage
│   └── memory/          # YOUR DATA (markdown files)
│       ├── decisions/
│       ├── insights/
│       ├── ideas/
│       └── ...
├── frontend/            # SvelteKit UI
│   └── src/
│       ├── routes/      # Pages
│       └── lib/         # Components
├── mcp-server/          # Claude Code integration
│   └── server.py
└── docs/                # Documentation (you are here)
    ├── INDEX.md         # This file
    ├── GETTING-STARTED.md
    ├── USER-GUIDE.md
    ├── TROUBLESHOOTING.md
    └── CLAUDE.md
```

### URLs

- **Frontend:** http://127.0.0.1:5176
- **Backend API:** http://127.0.0.1:3020
- **API Docs:** http://127.0.0.1:3020/docs
- **Health Check:** http://127.0.0.1:3020/health

### Categories

| Category | Use For |
|----------|---------|
| decisions | Strategic choices, architectural decisions |
| insights | Key discoveries, research findings |
| ideas | New concepts, feature ideas |
| learnings | Technical lessons, bug fixes |
| customers | Customer feedback, use cases |
| competitors | Competitor analysis |
| research | Market research, data |
| sessions | Daily summaries, meeting notes |

### Search Types

| Type | Use When | Speed | Accuracy |
|------|----------|-------|----------|
| Keyword | Exact match needed | Fast | High (exact) |
| Semantic | Conceptual search | Slow | High (meaning) |
| Hybrid | Most queries | Medium | Best overall |

## Learning Path

### Day 1: Basics
1. ✅ Read [GETTING-STARTED.md](GETTING-STARTED.md)
2. ✅ Capture 5 items
3. ✅ Search for them
4. ✅ Enable dark mode

### Week 1: Building Knowledge
1. ✅ Capture 10 items/day
2. ✅ Use auto-categorize
3. ✅ Add wikilinks to 3+ items
4. ✅ Check knowledge graph

### Month 1: Advanced Usage
1. ✅ Create index items
2. ✅ Use pattern detection
3. ✅ Weekly reviews
4. ✅ Configure MCP in Claude Code

## Support

**Questions?**
1. Check [TROUBLESHOOTING.md](TROUBLESHOOTING.md)
2. Search docs: `grep -r "your question" docs/`
3. Create issue: https://github.com/m-check1B/recall-kraliki/issues

**Feedback?**
- Feature requests: GitHub Issues
- Bug reports: GitHub Issues
- Documentation improvements: Pull Requests welcome

## Updates

**Version:** 0.1.0
**Last Updated:** 2025-10-06
**Status:** Phase 1 - Internal Use

**Changelog:**
- 2025-10-06: Initial release
  - ✅ Backend (FastAPI + GLM 4.6)
  - ✅ Frontend (SvelteKit 2.0)
  - ✅ Dark mode
  - ✅ Hybrid search
  - ✅ Knowledge graph
  - ✅ MCP server
  - ✅ Complete documentation

**Coming Soon:**
- Pattern detection UI
- Enhanced graph visualization (D3.js)
- Mobile-responsive improvements
- Export/import features
- Team collaboration (Phase 2)

---

**Ready to start?** → [GETTING-STARTED.md](GETTING-STARTED.md)
