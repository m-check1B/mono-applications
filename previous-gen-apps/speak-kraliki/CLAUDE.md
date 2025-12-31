# Speak by Kraliki - Project Memory

> ⛔ **SECURITY: DEV SERVER ON INTERNET. NEVER bind to `0.0.0.0`. Always use `127.0.0.1`. See `/github/CLAUDE.md`.**

AI Voice Employee Intelligence Platform (formerly Speak by Kraliki)

**Skill Reference:** See `SKILL.md` for capabilities, architecture, and integration details.

========================================
TEMPLATE-FIRST DELIVERY
Speak is delivered via Kraliki Swarm templates by default.
Standalone app is optional when UX or compliance requires it.
========================================

## Project Overview

Voice-first employee feedback platform using AI conversations to capture authentic sentiment. Built with stack-2026 standards.

**Tech Stack:**
- Backend: FastAPI + PostgreSQL + Ed25519 JWT
- Frontend: SvelteKit 5 + Tailwind CSS 4
- AI: Gemini 2.5 Flash
- Design: Modern Brutalism (style-2026)

## Key Directories

```
backend/app/
├── core/        # Config, auth, database
├── models/      # 8 SQLAlchemy models
├── schemas/     # Pydantic schemas
├── services/    # AI conversation, analysis, email
└── routers/     # API endpoints

frontend/src/
├── routes/      # Pages (v/[token], dashboard, login)
└── lib/
    ├── api/     # API client
    └── stores/  # Auth, voice stores
```

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

# Database migrations
cd backend
alembic revision --autogenerate -m "description"
alembic upgrade head
```

## API Structure

- `/api/auth/*` - Authentication
- `/api/speak/surveys/*` - Survey management
- `/api/speak/voice/*` - Voice/WebSocket interface
- `/api/speak/conversations/*` - Conversation data
- `/api/speak/actions/*` - Action Loop
- `/api/speak/alerts/*` - Automated alerts
- `/api/speak/insights/*` - Analytics
- `/api/speak/employees/*` - Employee management

## Key Features

1. **Trust Layer** - Consent screen + transcript review
2. **Voice Pipeline** - WebSocket + Gemini STT/TTS
3. **Action Loop** - CEO marks issues as heard/resolved
4. **Analytics** - Sentiment, topics, alerts

## Design Patterns

- Multi-tenant (company_id on all tables)
- Magic links for employee access
- Anonymous IDs protect identity
- Soft deletes for employees

## Testing

```bash
cd backend
# IMPORTANT: Use venv python directly to ensure correct packages
.venv/bin/python -m pytest tests/ -v
```

## Notes

- Employee conversations are 100% anonymous
- Managers only see aggregated data
- Employees can redact transcript parts
- GDPR: Right to delete all data

## Platform 2026 Packages

This application uses shared packages from platform-2026:

```bash
# Install platform packages
pip install -e ../../../platform-2026/packages/voice-core[all]
pip install -e ../../../platform-2026/packages/auth-core
pip install -e ../../../platform-2026/packages/events-core[rabbitmq]
```

| Package | Purpose |
|---------|---------|
| **voice-core** | Gemini 2.5 Flash for voice conversations |
| **auth-core** | Ed25519 JWT authentication |
| **events-core** | Event bus for survey events, conversation tracking |

## Port Assignment

- **Backend API**: 8020 (production default)
- **Frontend**: 5175 (dev)
- See `/github/platform-2026/docs/DEPLOYMENT_GUIDE.md` for port management

## Events Published

```python
# Survey events
survey.created
survey.sent
survey.closed

# Conversation events
conversation.started
conversation.completed

# Response events
response.received
action.created
action.resolved
alert.triggered
```

---

*Part of the GitHub workspace at /home/adminmatej/github*
*See parent @../../../CLAUDE.md for workspace conventions*
