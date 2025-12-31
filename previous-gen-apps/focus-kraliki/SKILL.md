---
name: focus-kraliki
description: AI-First Productivity System with task orchestration, voice processing, and shadow analysis. Use when working on productivity features, AI chat interfaces, task management, voice-to-task conversion, workflow automation, or Jungian shadow work integrations.
---

# Focus by Kraliki

AI-first productivity system combining high-reasoning AI (Claude + GPT-4), Jungian shadow analysis, flow memory, and voice processing into a unified task orchestration platform.

## When to Use This Skill

- Building or modifying AI chat interfaces with markdown rendering
- Implementing task management features (CRUD, filters, priorities)
- Working on voice-to-task conversion or audio processing
- Adding workflow automation or template generation
- Implementing shadow analysis (Jungian psychology features)
- Working on flow memory or context persistence
- Integrating with ii-agent orchestrator
- Building knowledge layer or file search features
- Adding analytics, billing, or usage tracking

## Architecture Overview

```
User Input → AI Chat / Voice Interface → Intent Detection
                                              ↓
                              FastAPI (deterministic routing)
                                              ↓
                        Task CRUD / Knowledge / Analytics
                                              ↓
                    [Complex tasks] → ii-agent Orchestrator
                                              ↓
                              Multi-AI Collaboration
                              (Claude + GPT-4 + Gemini)
```

### Hybrid Execution Model

- **Deterministic path**: Task CRUD, scheduling, knowledge management, analytics, voice capture
- **ii-agent path**: Multi-app automation, deep research, complex orchestration
- Escalation via `/agent` + `/agent-tools` endpoints

## Tech Stack

| Layer | Technology |
|-------|------------|
| Backend | FastAPI + PostgreSQL + SQLAlchemy 2.0 |
| Frontend | SvelteKit 2.0 + Tailwind CSS |
| AI | Claude 3.5 Sonnet, GPT-4, Gemini 2.5 Flash |
| Voice | Gemini Native Audio, OpenAI Realtime, Deepgram |
| Auth | JWT with bcrypt |
| Cache | Redis (flow memory, AI response caching) |
| Design | Modern Brutalism (style-2026) |

## Key Components

### Backend (`backend/app/`)

| Directory | Purpose |
|-----------|---------|
| `core/` | Config, database, security, JWT auth |
| `models/` | SQLAlchemy models (tasks, users, knowledge, workflows) |
| `schemas/` | Pydantic request/response schemas |
| `routers/` | API endpoints (120+ total) |
| `services/` | Business logic, AI integration |

### Frontend (`frontend/src/`)

| Directory | Purpose |
|-----------|---------|
| `routes/dashboard/` | Main app views |
| `routes/login/` | Authentication |
| `lib/api/` | REST client (68+ endpoints) |
| `lib/stores/` | Svelte stores for state |

### ii-agent (`ii-agent/`)

| Component | Purpose |
|-----------|---------|
| `ii_agent/main.py` | Agent orchestrator entry |
| `ii_agent/tools/` | Tool definitions |
| `ii_agent/prompts/` | Agent prompts |

## API Endpoints (120+ Total)

### Core APIs
- **Auth** (4): register, login, me, logout
- **Tasks** (9): Full CRUD + stats + search
- **AI** (18): chat, parsing, orchestration, insights, memory
- **AI Streaming** (2): SSE streaming chat
- **Knowledge** (12): items CRUD, categories, search

### Advanced APIs
- **Voice** (6): providers, transcribe, process, to-task
- **Workflow** (9): templates CRUD, execute, generate
- **Shadow** (4): analysis, insights, acknowledgment, unlock
- **Agent Tools** (10): tool discovery, execution
- **File Search** (6): upload, index, search stores
- **Swarm** (22): Task intelligence & cognitive analytics

### Support APIs
- **Workspaces** (8): CRUD, members, permissions
- **Analytics** (8): usage stats, insights, reports
- **Billing** (5): credits, usage, invoices
- **Settings** (4): user settings, BYOK configuration

## Key Patterns

### AI-First Validation

Input validation happens through AI understanding rather than rigid form rules:
1. Natural language input accepted
2. AI extracts intent and entities
3. Structured data created from understanding

### Flow Memory System

Persistent context across sessions:
- Redis-based storage
- Context windows preserved
- AI response caching
- Cross-session continuity

### Shadow Analysis (30-Day Progressive Unlock)

Jungian psychology integration:
1. Daily productivity patterns analyzed
2. Unconscious blockers surfaced
3. Progressive insights unlocked over 30 days
4. User acknowledgment and integration

### Voice Processing Pipeline

```
Audio Input → Transcription (Deepgram/Gemini)
                    ↓
            Intent Detection
                    ↓
            Entity Extraction
                    ↓
            Task/Action Creation
```

## Development

```bash
# Start development servers
./dev-start.sh
# Backend: http://localhost:8000
# Frontend: http://localhost:5173
# API Docs: http://localhost:8000/docs

# Stop development
./dev-stop.sh

# Production mode
./prod-start.sh  # 4 workers
./prod-stop.sh

# Backend only (manual)
cd backend
PYTHONPATH=backend uv run -- uvicorn app.main:app --app-dir backend --reload

# Frontend only (manual)
cd frontend && pnpm dev

# ii-agent
uv run --project ii-agent python -m ii_agent.main

# Database migrations
cd backend
alembic revision --autogenerate -m "description"
alembic upgrade head

# Tests
./test_e2e.sh  # Playwright E2E
cd backend && pytest  # Unit tests
```

## Integration Points

- **Platform 2026**: Uses auth-core, ai-core, calendar-core packages
- **Beta URL**: focus.verduona.dev
- **Ports**: Backend 8000, Frontend 5173 (dev) / 4173 (prod)
- **mgrep**: Semantic search on ports 8001, 7997, 6335

## Design System

Modern Brutalism (style-2026):
- Zero border radius (sharp corners)
- 2px bold borders
- 4px offset drop shadows
- High contrast (black/white + neon accents)
- JetBrains Mono typography
- Uppercase labels, instant state changes

## Key Features

| Feature | Description |
|---------|-------------|
| **AI Chat** | Claude + GPT-4 with markdown & syntax highlighting |
| **Voice Interface** | Natural speech to task conversion |
| **Shadow Work** | Jungian psychology with 30-day unlock |
| **Flow Memory** | Persistent context across sessions |
| **Workflow Automation** | AI-generated reusable templates |
| **Knowledge Layer** | Advanced knowledge management |
| **File Search** | Gemini-powered semantic search |
| **Analytics** | Usage insights and reports |

---

*See CLAUDE.md for project-specific commands and conventions*
