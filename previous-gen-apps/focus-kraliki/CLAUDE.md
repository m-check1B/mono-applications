# Focus by Kraliki Project Memory

> ⛔ **SECURITY: DEV SERVER ON INTERNET. NEVER bind to `0.0.0.0`. Always use `127.0.0.1`. See `/github/CLAUDE.md`.**

AI-first task orchestration platform with self-hosted semantic search integration.

**Skill:** See `SKILL.md` for agentskills.io format capabilities and usage documentation.

Baseline: **Python 3.13 + uv** (for backend/agents) and Node 24 LTS/pnpm 10+ (frontend).

========================================
ONE PRODUCT / ONE ENGINE / MANY TEMPLATES
Focus is a module inside Kraliki Swarm; standalone is optional.
========================================

## Project Overview

- AI orchestration platform for task management and agent coordination
- Tech stack: Svelte frontend, FastAPI backend, Python ii-agent system
- See @README.md for complete setup and architecture details
- See @docs/DEVELOPER_GUIDE.md for development guidelines

## Code Style & Conventions

- **Python**: Follow PEP 8, use type hints, 4-space indentation
- **TypeScript/Svelte**: 2-space indentation, prefer const over let
- **Import organization**: Group stdlib, third-party, then local imports
- **Naming**: camelCase for JS/TS, snake_case for Python

## Development Commands

```bash
# Backend (uv handles venv + deps; run from repo root)
PYTHONPATH=backend uv run -- uvicorn app.main:app --app-dir backend --reload

# Frontend
cd frontend && npm run dev

# ii-agent
uv run --project ii-agent python -m ii_agent.main

# Docker services (mgrep)
docker compose -f docker-compose.mgrep.yml up -d
```

## Semantic Search Integration (mgrep)

### Quick Setup
```bash
# Index documentation to workspace mgrep (port 8001)
python3 scripts/index-docs.py

# Watch for documentation changes and auto-index
python3 scripts/watch-docs.py
```

**Note:** Focus-Kraliki uses the workspace mgrep infrastructure (port 8001) shared across all projects. The docker-compose.mgrep.yml file is available for running a standalone mgrep instance (port 8002) if needed, but default integration uses workspace mgrep.

### Quick Usage
- Use `/mgrep "query"` for semantic code search
- Self-hosted stack running on localhost (ports 8001, 7997, 6335)
- Documentation indexed in store: `focus_kraliki_docs`
- See @MGREP_SELF_HOSTED_SETUP.md for complete setup guide
- See @mgrep-backend/README.md for API reference

### Search Examples
```bash
# Search documentation
curl -X POST http://localhost:8001/v1/stores/search \
  -H 'Content-Type: application/json' \
  -d '{"query": "how to authenticate users", "store_identifiers": ["focus_kraliki_docs"]}'

# Or use mgrep wrapper
bash /home/adminmatej/github/tools/mgrep-selfhosted/scripts/mgrep-wrapper.sh "authentication" focus_kraliki_docs
```

### Quick Usage
- Use `/mgrep "query"` for semantic code search
- Self-hosted stack running on localhost (ports 8001, 7997, 6337)
- Documentation indexed in store: `focus_kraliki_docs`
- See @MGREP_SELF_HOSTED_SETUP.md for complete setup guide
- See @mgrep-backend/README.md for API reference

### Search Examples
```bash
# Search documentation
curl -X POST http://localhost:8001/v1/stores/search \
  -H 'Content-Type: application/json' \
  -d '{"query": "how to authenticate users", "store_identifiers": ["focus_kraliki_docs"]}'

# Or use the mgrep wrapper
bash /home/adminmatej/github/tools/mgrep-selfhosted/scripts/mgrep-wrapper.sh "authentication" focus_kraliki_docs
```

### When to Use
- **mgrep**: Natural language queries ("where do we handle auth?")
- **grep/glob**: Exact symbols, regex patterns, known names

### API Endpoints
- Search: `POST http://localhost:8001/v1/stores/search`
- Upload: `POST http://localhost:8001/v1/stores/:storeId/files`
- List stores: `GET http://localhost:8001/v1/stores`

### Test Integration
```bash
# Run test queries to verify integration
./scripts/test-mgrep.sh

# This tests common task queries:
# - how to authenticate users
# - database schema setup
# - calendar sync google oauth
# - how to run tests
# - ai agent configuration
# - deployment to production
```

### Service Status
```bash
# Check workspace mgrep (used by focus-kraliki)
docker ps | grep mgrep

# Check workspace mgrep logs
docker logs mgrep-backend --tail 50
docker logs mgrep-infinity --tail 50
docker logs mgrep-qdrant --tail 50

# Check focus-kraliki mgrep (standalone, if used)
docker compose -f docker-compose.mgrep.yml ps
docker logs focus-kraliki-mgrep-backend --tail 50
```

## Git Workflow

- Main branch: `develop`
- Feature branches: `feature/description`
- Commit format: Descriptive present tense ("Add feature X", "Fix bug Y")
- Include emoji: 🤖 Generated with [Claude Code](https://claude.com/claude-code)

## Architecture Notes

- AI-first validation approach (see @docs/AI_FIRST_VALIDATION.md)
- Agent swarm methodology (see @docs/SWARM_METHODOLOGY_EXPERIENCE_REPORT.md)
- Offline inference capabilities (see @docs/OFFLINE_INFERENCE_STRATEGY.md)
- Track-based development structure (see @docs/TRACK_3_ARCHITECTURE.md)

## Custom Tools & Slash Commands

Available slash commands in `.claude/commands/`:
- `/flow-nexus:*` - Flow Nexus integrations (9 variants)
- `/mgrep` - Semantic code search

See `~/.claude/commands/` for all available commands.

## Testing & Quality

- Test command: `PYTHONPATH=backend uv run -- pytest backend/tests`
- See @docs/TESTING_COVERAGE_REPORT.md for coverage details
- See @docs/QUALITY_TESTING_DELIVERABLES.md for test strategy

## Important Constraints

- **Security**: Never commit .env files or secrets
- **Performance**: Mgrep runs on CPU mode (slower but works everywhere)
- **Privacy**: All mgrep processing is 100% local, no cloud APIs
- **Dependencies**: Mgrep requires Docker and ~10GB disk for models
- **Scripts**:
  - `scripts/index-docs.py` - Index documentation files to workspace mgrep (port 8001)
  - `scripts/watch-docs.py` - Watch docs directory for changes and auto-index to workspace mgrep
  - `scripts/setup-mgrep.sh` - Start standalone mgrep services (port 8002) and index docs (alternative to workspace mgrep)

## Troubleshooting

### Mgrep Issues
```bash
# Restart services
docker compose -f docker-compose.mgrep.yml restart

# Check logs
docker logs focus-kraliki-infinity --tail 50
docker logs focus-kraliki-qdrant --tail 50
docker logs focus-kraliki-mgrep-backend --tail 50

# Reset everything
docker compose -f docker-compose.mgrep.yml down -v && rm -rf data/

# Reindex documentation
python3 scripts/index-docs.py
```

### Port Conflicts
- Workspace mgrep ports: 8001 (backend), 7997 (infinity), 6335-6336 (qdrant) - Used by Focus-Kraliki
- Focus by Kraliki standalone mgrep ports (if using docker-compose.mgrep.yml): 8002 (backend), 7998 (infinity), 6339-6340 (qdrant)
- Backend API: 8000 (may conflict with other services)
- Default: Focus-Kraliki uses workspace mgrep on port 8001

## Platform 2026 Packages

This application uses shared packages from platform-2026:

```bash
# Install platform packages
pip install -e ../../../platform-2026/packages/auth-core
pip install -e ../../../platform-2026/packages/ai-core[anthropic,openai,gemini]
pip install -e ../../../platform-2026/packages/calendar-core[google]
```

| Package | Purpose |
|---------|---------|
| **auth-core** | Ed25519 JWT authentication |
| **ai-core** | Multi-model AI (Claude, GPT, Gemini) |
| **calendar-core** | Google Calendar two-way sync with OAuth |

## Port Assignment

- **Backend API**: 8000 (production default)
- **Frontend**: 5173 (dev), 4173 (preview)
- See `/github/platform-2026/docs/DEPLOYMENT_GUIDE.md` for port management

## Documentation Structure

```
docs/
├── AI_FIRST_*.md - AI-first methodology
├── TRACK_*.md - Development tracks
├── SWARM_*.md - Swarm execution docs
├── *_GUIDE.md - User and developer guides
└── *_SUMMARY.md - Completion summaries
```

---

*Last updated: 2025-12-25*
*For detailed mgrep setup, see @MGREP_SELF_HOSTED_SETUP.md*
