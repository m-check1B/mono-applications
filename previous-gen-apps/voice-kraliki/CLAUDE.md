# Voice by Kraliki - Project Memory

> ⛔ **SECURITY: DEV SERVER ON INTERNET. NEVER bind to `0.0.0.0`. Always use `127.0.0.1`. See `/github/CLAUDE.md`.**

Project-specific context for Claude Code. **Stack 2026 Compliant**.

## Project Overview

- **Stack**: Python 3.11+ (FastAPI) backend; template UIs use SvelteKit separately
- **Status**: Production-Ready (Headless backend)
- **Architecture**: Stack 2026 Compliant
- **Skill**: See @SKILL.md for agentskills.io format documentation
- See @README.md for full documentation
- Parent workspace: @../../CLAUDE.md

## Project Structure (Stack 2026)

```
voice-kraliki/
├── backend/              # Python FastAPI backend
│   ├── app/              # Application code
│   ├── migrations/       # Alembic database migrations
│   ├── tests/            # Backend tests
│   └── requirements.txt  # Python dependencies
├── frontend/             # Legacy SvelteKit UI (template source)
│   ├── src/routes/       # File-based routing
│   ├── src/lib/          # Components, stores, utils
│   ├── e2e/              # E2E tests
│   └── static/           # Static assets
├── scripts/              # Utility scripts
├── docs/                 # Documentation
│   ├── api/              # API documentation
│   ├── architecture/     # Architecture docs
│   ├── deployment/       # Deployment guides
│   ├── dev-plans/        # Development roadmaps
│   ├── reports/          # Status reports
│   ├── security/         # Security documentation
│   ├── backend/          # Backend-specific docs
│   └── frontend/         # Frontend-specific docs
├── infra/                # Infrastructure
│   ├── docker/           # Docker compose files
│   ├── traefik/          # Reverse proxy config
│   ├── nginx/            # Nginx configs
│   └── monitoring/       # Monitoring setup
├── _archive/             # Archived code and templates
├── docker-compose.yml    # Main dev compose
├── .env.example          # Environment template
└── README.md             # Project documentation
```

## Code Style & Conventions

### Python (Backend)
- Follow PEP 8, use type hints, 4-space indentation
- Import grouping: stdlib, third-party, local
- Use Pydantic for validation
- SQLAlchemy 2.0 async patterns

### TypeScript/Svelte (Template UI, legacy)
- 2-space indentation, prefer const over let
- camelCase for functions/variables
- Use Svelte stores for state management
- Tailwind CSS for styling

## Development Commands

```bash
# Backend
cd backend
uv sync                                          # Install deps
uv run uvicorn app.main:app --reload             # Dev server
uv run pytest tests/ -v                          # Tests
uv run alembic upgrade head                      # Migrations

# Frontend (legacy template source)
cd frontend
pnpm install                                     # Install deps
pnpm dev                                         # Dev server
pnpm test                                        # Unit tests
pnpm test:e2e                                    # E2E tests

# Docker
docker compose up -d                             # Start services
docker compose -f infra/docker/docker-compose.prod.yml up -d  # Production
```

## API Endpoints

- **API Docs**: http://localhost:8000/docs
- **Backend**: http://localhost:8000
- **Legacy UI**: http://localhost:3000

Key endpoints:
- `POST /api/v1/auth/login` - Authentication
- `GET /api/v1/campaigns` - Campaign management
- `GET /api/v1/teams` - Team management
- `GET /api/analytics/dashboard/overview` - Analytics

## Database

- **Type**: PostgreSQL
- **ORM**: SQLAlchemy 2.0
- **Migrations**: Alembic (in backend/migrations/)

```bash
# Migration commands
cd backend
uv run alembic revision --autogenerate -m "description"
uv run alembic upgrade head
uv run alembic downgrade -1
```

## Testing

```bash
# Backend tests
cd backend && uv run pytest tests/ -v --cov=app

# Frontend unit tests
cd frontend && pnpm test

# E2E tests
cd frontend && pnpm test:e2e
```

## Git Workflow

- Descriptive commits in present tense
- Feature branches: `feature/description`
- Never commit secrets or .env files
- Include Claude co-authoring:
  ```
  🤖 Generated with [Claude Code](https://claude.com/claude-code)

  Co-Authored-By: Claude <noreply@anthropic.com>
  ```

## Key Technologies

- **Backend**: FastAPI, SQLAlchemy, Alembic, Pydantic, JWT
- **Frontend**: SvelteKit 2.x, TypeScript, Tailwind CSS
- **AI**: OpenAI Realtime API, Gemini, Deepgram
- **Telephony**: Twilio MediaStream, Telnyx Call Control
- **Database**: PostgreSQL, Redis, Qdrant
- **Deploy**: Docker, Traefik, uv, pnpm

## Voice Core Packages

This application uses local core packages stored in `packages/`:

```bash
pip install -e packages/voice-core[telephony,transcription]
pip install -e packages/telephony-core
pip install -e packages/transcription-core
pip install -e packages/auth-core
pip install -e packages/ai-core[all]
pip install -e packages/events-core[rabbitmq]
```

| Package | Purpose |
|---------|---------|
| **voice-core** | Real-time voice AI (Gemini, OpenAI, Deepgram) + telephony (Telnyx, Twilio) |
| **auth-core** | Ed25519 JWT authentication with RBAC |
| **ai-core** | LLM provider abstraction |
| **events-core** | Event bus for call events, agent status changes |

## Port Assignment

- **Backend API**: 8010 (production default)
- **Frontend**: 3000 (dev), 4174 (preview)
- See `/github/applications/voice-kraliki/docs/deployment/DEPLOYMENT_GUIDE.md` for port management

## Troubleshooting

**Port conflicts:**
```bash
lsof -i :8000  # Backend
lsof -i :3000  # Frontend
```

**Dependency issues:**
```bash
# Backend
rm -rf backend/.venv && cd backend && uv sync

# Frontend
rm -rf frontend/node_modules && cd frontend && pnpm install
```

**Docker services:**
```bash
docker compose ps
docker compose logs -f [service]
docker compose restart [service]
```

---

*Stack 2026 Compliant - See /home/adminmatej/github/stack-2026/README.md for standards*
