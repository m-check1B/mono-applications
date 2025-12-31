# Speak by Kraliki

**AI Voice Employee Intelligence Platform**

Zjistete, co si vasi zamestnanci opravdu mysli. Hlasove rozhovory. Anonymni zpetna vazba. Akcni vhledy.

========================================
TEMPLATE-FIRST DELIVERY
Speak is delivered as a Swarm template/channel.
Standalone app is optional when UX or compliance requires it.
========================================

## Overview

Speak by Kraliki is an AI-powered employee feedback platform that uses voice conversations instead of text surveys to capture authentic employee sentiment. The platform bypasses middle management filtering to give leadership direct insight into company culture and employee concerns.

**Delivery model:** Speak runs as a **Kraliki Swarm template/channel** by default. This repo provides the backend and optional UI for standalone deployments when required.

### Key Features

- **Voice-First Conversations** - Natural 5-7 minute AI conversations in Czech
- **100% Anonymous** - Managers never see individual responses
- **Trust Layer** - Employees can review and redact transcripts before submission
- **Action Loop** - Show employees that leadership is listening and acting
- **Real-time Analytics** - Sentiment trends, topic extraction, automated alerts

## Tech Stack

Built with [stack-2026](../../stack-2026/) standards:

**Backend:**
- FastAPI 0.121+
- PostgreSQL 17+ with SQLAlchemy 2.0
- Ed25519 JWT Authentication
- Gemini 2.5 Flash for AI conversations

**Frontend:**
- SvelteKit 2.49+ with Svelte 5
- Tailwind CSS 4.1+
- Modern Brutalism design (style-2026)

## Quick Start

### Prerequisites

- Python 3.13+
- Node.js 22+
- PostgreSQL 17+
- Docker (optional)

### Development Setup

1. **Clone and enter directory:**
   ```bash
   cd /home/adminmatej/github/applications/speak-kraliki
   ```

2. **Generate local .env (recommended):**
   ```bash
   ./scripts/generate_env.sh
   # Re-run with OVERWRITE_ENV=1 to rotate secrets
   ```

3. **Start with Docker (recommended):**
   ```bash
   docker compose up -d
   ```

4. **Or run manually:**

   Backend:
   ```bash
   cd backend
   python -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   cp .env.example .env
   # Edit .env with your settings
   uvicorn app.main:app --reload
   ```

   Frontend:
   ```bash
   cd frontend
   npm install
   npm run dev
   ```

5. **Access the application:**
   - Frontend: http://localhost:5173
   - Backend API: http://localhost:8000
   - API Docs: http://localhost:8000/docs

### Database Migrations

```bash
cd backend
alembic revision --autogenerate -m "description"
alembic upgrade head
```

### Running Tests

**IMPORTANT:** Always use the project's virtual environment for tests.

```bash
# Option 1: Use the test script (recommended)
./scripts/test.sh

# Option 2: Run pytest directly from venv
cd backend
.venv/bin/pytest tests/

# Option 3: Activate venv first
cd backend
source .venv/bin/activate
pytest tests/
```

Do NOT use system `python3 -m pytest` - it won't have the required dependencies.

## Project Structure

```
speak-kraliki/
├── backend/                    # FastAPI backend
│   ├── app/
│   │   ├── core/              # Config, auth, database
│   │   ├── models/            # SQLAlchemy models
│   │   ├── schemas/           # Pydantic schemas
│   │   ├── services/          # Business logic
│   │   ├── routers/           # API endpoints
│   │   └── main.py            # Application entry
│   ├── alembic/               # Database migrations
│   └── tests/                 # Backend tests
├── frontend/                   # SvelteKit frontend
│   ├── src/
│   │   ├── routes/            # Pages
│   │   └── lib/
│   │       ├── api/           # API client
│   │       ├── stores/        # Svelte stores
│   │       └── components/    # UI components
│   └── static/                # Static assets
├── docs/                       # Documentation
└── scripts/                    # Utility scripts
```

## API Endpoints

### Authentication
- `POST /api/auth/login` - Login
- `POST /api/auth/register` - Register company
- `POST /api/auth/refresh` - Refresh token

### Surveys
- `GET /api/speak/surveys` - List surveys
- `POST /api/speak/surveys` - Create survey
- `POST /api/speak/surveys/:id/launch` - Launch survey

### Voice Interface
- `WS /api/speak/voice/ws/:token` - WebSocket for conversation
- `GET /api/speak/employee/transcript/:token` - View transcript

### Dashboard
- `GET /api/speak/insights/overview` - Company metrics
- `GET /api/speak/alerts` - Active alerts
- `GET /api/speak/actions` - Action items

## Environment Variables

See `.env.example` in the root directory for all configuration options and `docs/SECRETS_CONFIGURATION.md` for detailed setup instructions.

**Required for production:**
- `DATABASE_URL` - PostgreSQL connection string
- `JWT_SECRET_KEY` OR `ED25519_PRIVATE_KEY` - JWT signing key
- `GEMINI_API_KEY` - Google AI API key (for voice features)

**Optional (feature-dependent):**
- `TELNYX_API_KEY`, `TELNYX_PUBLIC_KEY`, `TELNYX_CONNECTION_ID`, `TELNYX_PHONE_NUMBER` - Telnyx for voice calls
- `RESEND_API_KEY` - Email service
- `STRIPE_SECRET_KEY`, `STRIPE_WEBHOOK_SECRET` - Payments

### Production Deployment

1. **Create production secrets:**
   ```bash
   cp /home/adminmatej/github/secrets/speak-kraliki.env.template \
      /home/adminmatej/github/secrets/speak-kraliki.env
   # Edit with production values
   ```

2. **Start with Docker:**
   ```bash
   docker compose up -d
   ```

3. **The application will be available at:**
   - Production: https://speak.kraliki.com
   - Beta: https://speak.verduona.dev

For detailed secrets configuration, see `docs/SECRETS_CONFIGURATION.md`.

## Design System

Uses **Modern Brutalism** from [style-2026](../../style-2026/):
- Sharp corners (0px border-radius)
- 2px borders
- Hard offset shadows (4px 4px)
- Terminal Green (#33FF00) for accents
- JetBrains Mono font

## License

Proprietary - All rights reserved

---

Built with [Claude Code](https://claude.com/claude-code)
