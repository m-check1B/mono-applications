---
name: voice-kraliki
description: Build, maintain, and integrate the Voice by Kraliki AI call center platform. Use when working on voice AI pipelines, telephony (Twilio/Telnyx), IVR flows, call routing, campaign management, agent/team operations, or call center analytics.
---

# Voice by Kraliki

Operate and extend the production-ready AI call center platform.

## Scope

- Focus on voice AI pipelines (OpenAI Realtime, Gemini, Deepgram) and telephony bridges (Twilio MediaStream, Telnyx Call Control).
- Implement IVR flow design, routing strategies, and queue/agent assignment logic.
- Build campaign management, contact/call list tooling, and supervisor dashboards.
- Extend analytics, reporting, alerts, and QA/recording workflows.
- Keep multilingual UX (EN, ES, CS) consistent with existing i18n patterns.

## Architecture Overview

```
Inbound/Outbound Call → Telephony (Twilio/Telnyx)
                              ↓
                    WebSocket Audio Stream
                              ↓
                    Voice AI (OpenAI/Gemini/Deepgram)
                              ↓
                    FastAPI Backend (routing, IVR logic)
                              ↓
                    Agent Desktop / Supervisor Cockpit
                              ↓
                    Analytics & Reporting
```

## Core Components

- **Campaign System**: Contact lists, call scheduling, templates
- **Voice AI**: Real-time STT/TTS with multi-provider support
- **IVR Builder**: Visual drag-and-drop flow designer (9 node types)
- **Call Routing**: 8 strategies (skill-based, round-robin, priority, etc.)
- **Team Management**: Agents, skills, availability, performance
- **Analytics**: Time-series metrics, dashboards, scheduled reports

## Tech Stack

| Layer | Technology |
|-------|------------|
| Backend | FastAPI + PostgreSQL + SQLAlchemy 2.0 |
| Frontend | SvelteKit 2.x + TypeScript + Tailwind CSS |
| Voice AI | OpenAI Realtime API, Gemini 2.5 Native Audio, Deepgram |
| Telephony | Twilio MediaStream, Telnyx Call Control |
| Vector DB | Qdrant (knowledge base search) |
| Cache | Redis |
| Auth | JWT with bcrypt |
| Design | Modern Brutalism (style-2026) |

## Key Paths

### Backend (`backend/app/`)

| Directory | Purpose |
|-----------|---------|
| `core/` | Config, database, security, JWT auth |
| `models/` | SQLAlchemy models (campaigns, teams, IVR, analytics) |
| `schemas/` | Pydantic request/response schemas |
| `routers/` | API endpoints (100+ total) |
| `services/` | Business logic, voice AI, telephony |

### Frontend (`frontend/src/`)

| Directory | Purpose |
|-----------|---------|
| `routes/dashboard/` | Main app views (28 pages total) |
| `routes/login/` | Authentication |
| `lib/api/` | REST client |
| `lib/stores/` | Svelte stores for state |
| `lib/i18n/` | Translation system (EN, ES, CS) |

## API Surface (100+ Total)

- **Auth** (4): register, login, me, logout
- **Campaigns** (12): CRUD, contacts, call lists, templates
- **Teams** (10): teams, agents, skills, assignments
- **Companies** (8): profiles, knowledge base, documents

- **IVR** (12): flows CRUD, nodes, visual builder
- **Routing** (8): rules, strategies, queue management
- **Recordings** (6): list, playback, analytics
- **Voicemail** (4): inbox, transcription, callback

- **Metrics** (8): time-series, aggregations, thresholds
- **Reports** (12): templates, generation, scheduling
- **Dashboard** (4): overview, real-time, widgets
- **Alerts** (6): performance alerts, notifications

## Key Patterns

### Multi-Provider Voice AI

Unified interface across providers:
```python
# Provider abstraction
voice_ai = get_provider(provider_type)  # openai, gemini, deepgram
response = await voice_ai.transcribe(audio_stream)
```

### Visual IVR Builder

9 node types for flow design:
- Start, End, Menu, Input, Transfer
- Condition, Webhook, Queue, Voicemail

### Call Routing Engine

8 routing strategies:
- Round-robin, Skill-based, Priority
- Least-busy, Time-based, Geographic
- Customer-history, Load-balanced

### Real-time Supervisor Cockpit

Live monitoring capabilities:
- Active calls with listen/whisper/barge
- Agent status and availability
- Queue depths and wait times
- Performance KPIs

## Development

```bash
# Backend
cd backend
uv sync
uv run uvicorn app.main:app --reload
# API Docs: http://localhost:8000/docs

# Frontend
cd frontend
pnpm install
pnpm dev
# UI: http://localhost:3000

# Docker
docker compose up -d
# Starts: PostgreSQL, Redis, Qdrant

# Database migrations
cd backend
uv run alembic revision --autogenerate -m "description"
uv run alembic upgrade head

# Tests
cd backend && uv run pytest tests/ -v
cd frontend && pnpm test && pnpm test:e2e
```

## Integration Points

- **Platform 2026**: Uses voice-core, auth-core, ai-core packages
- **Production URL**: voice.kraliki.com
- **Dev URL**: voice.verduona.dev
- **Ports**: Backend 8000/8010, Frontend 3000 (dev) / 4174 (preview)
- **mgrep**: Semantic search on port 8001

## Data Model

Key tables:
- **campaigns**: Campaign definitions and settings
- **contacts, call_lists**: Contact management
- **teams, agents, agent_skills**: Team organization
- **ivr_flows, ivr_nodes**: IVR flow definitions
- **routing_rules**: Call routing configuration
- **recordings, voicemails**: Call media
- **metrics, metric_aggregations**: Analytics data
- **reports, report_schedules**: Report management

---

*Stack 2026 Compliant | See CLAUDE.md for project-specific commands*
