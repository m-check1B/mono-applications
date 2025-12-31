---
name: speak-kraliki
description: Voice-first employee feedback platform (Speak by Kraliki). Use when working on Speak product docs, voice conversation pipeline, survey workflows, analytics/insights, action loop features, auth, or platform-2026 integrations.
---

# Speak by Kraliki

Use this skill to navigate and extend the Speak by Kraliki app: a voice-driven employee sentiment platform built with stack-2026 standards.

## Product Summary

Capture anonymous employee feedback through AI voice conversations, then surface sentiment, topics, and action loops for leadership.

## Architecture Overview

```
Employee → Magic Link → Voice UI → WebSocket Voice Pipeline
                                   ↓
                            FastAPI Backend
                                   ↓
                Conversations + Insights + Action Loop
```

## Key Directories

```
backend/app/
├── core/        # Config, auth, database
├── models/      # SQLAlchemy models
├── schemas/     # Pydantic schemas
├── services/    # Voice AI, analysis, email
└── routers/     # API endpoints

frontend/src/
├── routes/      # v/[token], dashboard, login
└── lib/
    ├── api/     # REST client
    └── stores/  # Auth + voice state
```

## Core Flows

### Voice Conversation

1. Employee opens magic link (`/v/[token]`).
2. WebSocket connects to `/api/vop/voice/*`.
3. Gemini 2.5 Flash handles STT/TTS and conversation logic.
4. Conversation stored, insights generated, alerts triggered.

### Action Loop

1. Leadership reviews insights.
2. Issues marked heard/resolved.
3. Employees receive closure updates (when configured).

## API Surface

- **Auth**: `/api/auth/*`
- **Surveys**: `/api/vop/surveys/*`
- **Voice**: `/api/vop/voice/*`
- **Conversations**: `/api/vop/conversations/*`
- **Actions**: `/api/vop/actions/*`
- **Alerts**: `/api/vop/alerts/*`
- **Insights**: `/api/vop/insights/*`
- **Employees**: `/api/vop/employees/*`

## Development Commands

```bash
# Backend
cd backend
source .venv/bin/activate
uvicorn app.main:app --reload

# Frontend
cd frontend
npm run dev

# Docker
docker compose up -d

# Migrations
cd backend
alembic revision --autogenerate -m "description"
alembic upgrade head
```

## Integration Points

- **Platform-2026 packages**: voice-core, auth-core, events-core
- **Design system**: Modern Brutalism (style-2026)
- **Ports**: Backend 8020, Frontend 5175

## Guardrails

- Keep employee data anonymous by default.
- Enforce consent + transcript review before persistence.
- Do not bind dev services to `0.0.0.0`; use `127.0.0.1` only.

---

*See `CLAUDE.md` for project-specific conventions and commands.*
