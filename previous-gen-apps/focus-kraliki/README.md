# Focus by Kraliki - AI-First Productivity System

> **Status**: ✅ Production-Ready | **Stack**: SvelteKit 2.0 + FastAPI + PostgreSQL
> **Version**: 2.4.0 | **Last Updated**: December 25, 2025

========================================
ONE PRODUCT / ONE ENGINE / MANY TEMPLATES
Focus is a module in Kraliki Swarm; standalone is optional.
========================================

## 🎯 Overview

![Focus Dashboard Placeholder](static/images/screenshots/dashboard.png)

Focus by Kraliki is a revolutionary AI-first productivity system that combines:

- 🧠 **High Reasoning AI**: Claude 3.5 Sonnet + GPT-4 collaborative intelligence
- 🎭 **Shadow Analysis**: Jungian psychology for productivity insights with 30-day progressive unlock
- 💾 **Flow Memory System**: Persistent context across sessions
- 🎤 **Voice Processing**: Natural speech to task conversion
- ✨ **Simply In, Simply Out**: Revolutionary UI/UX philosophy
- 🎯 **Natural Language Orchestration**: Convert thoughts to structured workflows

**Delivery model:** Focus is a **module inside Kraliki Swarm** by default; standalone deployment remains optional when required.

### Hybrid Execution Model

Most day-to-day jobs (task CRUD, scheduling, knowledge management, analytics, voice capture) run through our deterministic FastAPI routers and services. When a user explicitly needs multi-app automation or deep research we escalate to the optional ii-agent orchestrator via `/agent` + `/agent-tools`. See [docs/HYBRID-EXECUTION-GUIDE.md](docs/HYBRID-EXECUTION-GUIDE.md) for routing criteria, telemetry, and escalation guidelines.

## 📁 Project Structure (Monorepo)

```
focus-kraliki/
├── backend/                 # ✅ FastAPI Backend
│   ├── app/
│   │   ├── core/           # Config, database, security
│   │   ├── models/         # SQLAlchemy models
│   │   ├── schemas/        # Pydantic schemas
│   │   ├── routers/        # API endpoints (68 total)
│   │   └── main.py         # FastAPI application
│   ├── alembic/            # Database migrations
│   ├── requirements.txt    # Python dependencies
│   ├── .env.example        # Environment template
│   └── start.sh           # Quick start script
│
├── frontend/               # ✅ SvelteKit Frontend
│   ├── src/
│   │   ├── lib/
│   │   │   ├── api/        # REST client (68 endpoints)
│   │   │   └── stores/     # Svelte stores
│   │   ├── routes/         # File-based routing
│   │   │   ├── login/      # Authentication
│   │   │   ├── register/   # Registration
│   │   │   └── dashboard/  # Main app
│   │   ├── app.css         # Global styles
│   │   └── app.html        # HTML template
│   ├── package.json        # pnpm dependencies
│   └── .env.example        # Environment template
│
├── static/                 # 📦 Shared Static Assets
│   └── (images, fonts, etc.)
│
├── docs/                   # 📚 Documentation (active)
│   ├── SCRIPTS.md          # Port management and startup guide
│   ├── DATABASE_SETUP.md   # Database setup
│   ├── AI_FIRST_AUDIT.md   # Current architecture audit
│   ├── AI_FIRST_UI_REDESIGN.md # Context panel/UI redesign
│   ├── AI_FIRST_HYBRID_UX_PLAN.md # HUD + hybrid UX plan
│   ├── HYBRID-EXECUTION-GUIDE.md  # Deterministic vs ii-agent routing
│   ├── GEMINI_FILE_SEARCH.md # File search integration
│   ├── MIGRATION_STATUS.md   # Settings migration status
│   ├── SETTINGS_MIGRATION_SUMMARY.md # Settings migration details
│   ├── COMPLETION_SUMMARY.md # Settings modernization summary
│   ├── COMMAND_HISTORY_AND_TELEMETRY.md # Telemetry model
│   └── (more under docs/)
│
├── infra/                  # 🏗️ Deployment/ops configs + infra docs
│   ├── HETZNER_DEPLOYMENT.md   # Hetzner guide
│   └── PLATFORM_INTEGRATION.md # Platform integration guide
│
├── scripts/                # 🛠️ Utility Scripts
│   ├── setup.sh            # Complete setup
│   ├── start.sh            # Start dev servers
│   ├── test.sh             # Run tests
│   ├── build.sh            # Production build
│   └── db-reset.sh         # Reset database
│
├── vendor/                 # ♻️ Shared voice/telephony providers
├── ii-agent/               # 🤖 Intelligent II Agent integration
├── tests/                  # 🧪 E2E tests (Playwright)
├── README.md               # This file
├── CLAUDE.md               # Project memory (kept at root)
├── _archive/QUICK_START_GUIDE.md    # Legacy quick start
├── _archive/TESTING_GUIDE.md        # Legacy testing guide
└── (startup scripts) dev-start.sh, dev-stop.sh, prod-start.sh, prod-stop.sh
```

## 🚀 Quick Start

### Prerequisites
- Node.js 24+ & pnpm 10+
- Python 3.13+ with uv
- PostgreSQL 15+ (or Docker)
- lsof (for port management)

> We now standardize on `uv` for Python dependency management. Install it from https://docs.astral.sh/uv/ and prefer `uv sync` over `pip install`.

### Development Mode (Recommended)

```bash
# Start development servers (auto port cleanup)
./dev-start.sh
# Backend: http://localhost:8000
# Frontend: http://localhost:5173
# API Docs: http://localhost:8000/docs

# Stop development servers
./dev-stop.sh
```

### Production Mode

```bash
# Start production servers (with build)
./prod-start.sh
# Backend: http://localhost:8000 (4 workers)
# Frontend: http://localhost:4173 (production build)

# Stop production servers
./prod-stop.sh
```

> **Important**: Always use the stop scripts before restarting to avoid port conflicts. See [docs/SCRIPTS.md](docs/SCRIPTS.md) for detailed usage.

### Manual Setup

**1. Database:**
```bash
# Using Docker (recommended)
docker run --name focus_kraliki-db \
  -e POSTGRES_USER=postgres \
  -e POSTGRES_PASSWORD=password \
  -e POSTGRES_DB=focus_kraliki \
  -p 5432:5432 \
  -d postgres:15
```

**2. Backend:**
```bash
cd backend
cp .env.example .env
# Edit .env with your API keys and database URL
alembic upgrade head
uv run uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

**3. Frontend:**
```bash
cd frontend
pnpm install
cp .env.example .env
# Edit .env: PUBLIC_API_URL=http://localhost:8000 (required, absolute URL)
pnpm dev
```

## 🧩 Platform Integration

- Python consumers can import `PlanningModule` from `ocelot_apps.focus_kraliki` to reuse core planning flows without HTTP (see `backend/ocelot_apps/focus_kraliki/module.py`).
- The repository now ships as `@ocelot-apps/focus-kraliki` via the new root `package.json`, exposing a manifest in `module/index.js` for the Ocelot platform to discover build commands and entrypoints.
- Deployment assets live under `infra/` to match Stack 2026 conventions and are referenced in the platform manifest.


## 🛠️ Technology Stack

### Frontend (SvelteKit 2.0)
- **Framework**: SvelteKit 2.0 + Svelte 4.2.7
- **Language**: TypeScript 5.0
- **Build**: Vite 5.0
- **Styling**: Tailwind CSS 3.3.6 with Modern Brutalism design system
- **Components**: bits-ui, lucide-svelte
- **Theme**: mode-watcher (light/dark/system with brutalist aesthetics)

**Why SvelteKit?**
- 60% smaller bundle (~150kb vs ~250kb)
- 2x faster development
- Simpler state management
- AI-friendly (complexity: 3/10 vs Next.js: 7.5/10)

### Backend (FastAPI)
- **Framework**: FastAPI 0.110.0
- **ORM**: SQLAlchemy 2.0.27
- **Migrations**: Alembic 1.13.1
- **Validation**: Pydantic 2.6.1
- **Database**: PostgreSQL 15+
- **AI**: Anthropic Claude, OpenAI GPT-4, Gemini 2.5 Flash Native Audio (live), OpenAI Realtime (live), Deepgram (transcription)
- **Auth**: JWT with bcrypt

**Why FastAPI?**
- 5x faster development than TypeScript
- Native AI SDK support
- Automatic OpenAPI docs
- 65% less code (32 vs 141 files)

## 🎨 Design System

### Modern Brutalism
Focus by Kraliki features a distinctive **Modern Brutalism** design system that combines:
- **Zero border radius** - Sharp, uncompromising corners
- **Bold 2px borders** - Black in light mode, white in dark mode
- **Offset drop shadows** - 4px × 4px for cards, 2px × 2px for small elements
- **High contrast colors** - Pure blacks and whites with neon accents
- **Monospace typography** - Code-like aesthetic throughout
- **Uppercase labels** - Bold, commanding text hierarchy
- **No smooth transitions** - Instant state changes for brutalist feel

### Theme Support
- **Light Mode**: White backgrounds, black borders, neon accents
- **Dark Mode**: Deep dark backgrounds (5% gray), white borders, maintained neon accents
- **System Mode**: Automatic detection with instant switching
- **CSS Variables**: Semantic color system for consistent theming

### Brutalist Utilities
```css
.brutal-border    /* 2px black/white border */
.brutal-shadow    /* 4px offset drop shadow */
.brutal-shadow-sm /* 2px offset drop shadow */
.brutal-card      /* Complete card styling */
.brutal-btn       /* Interactive button with translate effect */
```

## 💰 Sales & Revenue

Focus by Kraliki is not just a tool; it's a consulting engine.

### Strategic AI Audit (Reality Check)
The system includes a built-in audit generation engine (`/exports/audit/generate`) that:
1. **Analyzes repetitive tasks** to identify automation "Manual Tax".
2. **Consults Shadow Profile** to find psychological friction points (overthinking, perfectionism).
3. **Generates a professional PDF/MD report** using the Verduona Strategic Template.
4. **Calculates 10x ROI** based on automated versus manual cost arbitrage.

Target revenue: **€500 per audit session**.

### Core Features
- ✅ **Authentication & OAuth**: Email/password + Google OAuth (login/link/unlink)
- ✅ **Task Management**: Full CRUD with filters, search, priorities
- ✅ **AI Chat**: Claude 3.5 + GPT-4 with markdown & syntax highlighting
- ✅ **Knowledge Layer**: Advanced knowledge management and organization
- ✅ **Workspaces**: Multi-workspace support for team collaboration
- ✅ **Webhooks**: Calendar sync + ii-agent callbacks for real-time updates
- ✅ **Conflict Resolution**: Policy-based calendar sync reconciliation
- ✅ **File Search**: Gemini-powered file search and indexing
- ✅ **Agent Tools**: Comprehensive agent tools integration
- ✅ **Shadow Work**: Jungian psychology with 30-day progressive unlock
- ✅ **Voice Interface**: Gemini 2.5 Flash Native Audio + OpenAI Realtime with Deepgram transcription fallback
- ✅ **Voice Processing**: Intent detection, entity extraction, voice-to-task conversion
- ✅ **Offline Inference**: Local fallback models for privacy or low-latency mode
- ✅ **Workflow Automation**: Reusable templates with AI-generated workflows
- ✅ **Settings**: Profile, theme, preferences, notifications, BYOK (Bring Your Own Keys)
- ✅ **Analytics**: Advanced analytics and usage insights
- ✅ **Billing**: AI usage tracking and credit management
- ✅ **Theme System**: Modern Brutalism design with light/dark/system modes
- ✅ **Internationalization (i18n)**: Support for multiple languages (English and Czech included).

### Revolutionary Features
- 🎭 **Shadow Analysis**: Unconscious productivity pattern analysis
- 💾 **Flow Memory**: Redis-based persistent context across sessions
- 🧠 **AI Response Caching**: Intelligent caching for repeated queries
- ⚡ **Streaming AI**: Real-time token-by-token responses (SSE)
- 🔄 **WebSocket Updates**: Live real-time notifications
- 🎯 **Natural Orchestration**: Thoughts → structured workflows
- 🎤 **Voice Commands**: Natural speech to task conversion
- 📊 **Reality Check Audit**: AI-powered strategic ROI roadmap generation based on shadow patterns and repetitive task analysis
- 🧠 **High Reasoning**: Multi-AI collaborative problem solving
- 📝 **Markdown Chat**: Rich text formatting with code syntax highlighting

### Advanced Capabilities (Deep Dive)
- 🔐 **Google OAuth Integration**: Complete secure login and account linking/unlinking flow with Google Cloud Identity.
- ⚓ **Real-time Webhooks**: Bidirectional synchronization hooks for Google Calendar and ii-agent status callbacks for autonomous worker coordination.
- ⚖️ **Intelligent Conflict Resolution**: Multi-policy reconciliation (last-modified, source-priority, manual) for robust data synchronization across multiple providers.
- 🔌 **Offline Inference Engine**: Local fallback capability for low-latency processing and privacy-critical tasks using on-device models.

## 📊 API Endpoints (120+ Total)

### Endpoint Categories
- **Auth** (4): register, login, me, logout
- **Google OAuth** (4): url, login, link, unlink
- **Users** (4): profile, preferences management
- **Tasks** (9): Full CRUD + stats + search
- **AI** (18): chat, parsing, orchestration, insights, memory, flow context
- **AI Streaming** (2): streaming chat, test stream (Server-Sent Events)
- **Knowledge** (12): items CRUD, categories, search, AI integration
- **Workspaces** (8): CRUD, members, sharing, permissions
- **File Search** (6): upload, index, search, manage stores
- **Agent Tools** (10): tool discovery, execution, management
- **Shadow** (4): analysis, insights, acknowledgment, unlock
- **Voice** (6): providers, transcribe, process, to-task, recordings
- **Workflow** (9): templates CRUD, execute, generate, categories
- **WebSocket** (1): real-time updates (ws://)
- **Pricing** (1): model catalog
- **Billing** (5): credits, usage, invoices, payment methods
- **Analytics** (8): usage stats, insights, reports
- **Settings** (4): user settings, BYOK configuration
- **Swarm** (22): Task intelligence & cognitive analytics
- **Projects** (5): CRUD + stats
- **Events** (5): CRUD + calendar sync
- **Time Entries** (5): tracking + reports
- **AI Scheduler** (5): intelligent task scheduling

**Complete docs**: Use FastAPI docs at http://127.0.0.1:8000/docs (archived static reference: `_archive/docs/API_REFERENCE.md`)

## 📝 Development Commands

### Quick Start Scripts

```bash
# Development mode (hot reload)
./dev-start.sh        # Start backend (8000) + frontend (5173)
./dev-stop.sh         # Stop all development processes

# Production mode (optimized)
./prod-start.sh       # Build & start with 4 workers
./prod-stop.sh        # Stop all production processes
```

> **Note**: The scripts automatically clear ports and manage PIDs. See [docs/SCRIPTS.md](docs/SCRIPTS.md) for details.

### Frontend Commands

```bash
cd frontend
pnpm dev              # Start dev server (port 5173)
pnpm build            # Build for production
pnpm preview          # Preview production build (port 4173)
pnpm check            # TypeScript type checking
pnpm format           # Format code with Prettier
```

### Backend Commands

```bash
cd backend
# Development
uv run uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload

# Production
uv run uvicorn app.main:app --host 127.0.0.1 --port 8000 --workers 4

# Database migrations
alembic revision --autogenerate -m "Description"
alembic upgrade head
alembic downgrade -1

# Health check
curl http://localhost:8000/health
```

### Utility Scripts

```bash
# Database operations
./scripts/db-reset.sh         # Reset database (DANGER)
./scripts/backup.sh           # Database backup
./scripts/restore.sh <file>   # Database restore

# RabbitMQ utilities
cd backend
python scripts/check_rabbitmq.py                      # Health check
python scripts/consume_planning_events.py --routing planning.#  # Event tap

# Testing
./test_e2e.sh                 # Run E2E tests (Playwright)
cd backend && pytest          # Run unit tests
```

## 🐇 RabbitMQ Utilities

- **Health check before deploy**
  ```bash
  cd backend
  python scripts/check_rabbitmq.py
  ```
  Exits non-zero if the URL in `.env` is unreachable, which makes it suitable for CI gates.

- **Live event tap**
  ```bash
  cd backend
  python scripts/consume_planning_events.py --routing planning.#
  ```
  Prints every payload published to the `ocelot.planning` exchange so you can verify task events locally.

- **CI fallback / brokerless mode**  
  If you cannot run RabbitMQ (e.g., GitHub Actions), set `USE_INMEMORY_EVENTS=1` in the backend environment. The
  built-in in-memory bus will record events and keep API routes functional until a real broker is available.

## 🔐 Security

### ⚠️ CRITICAL: Never Bind to 0.0.0.0

**ALWAYS** use `127.0.0.1` for development. See:
- [CRITICAL-SECURITY-POLICY.md](/home/adminmatej/github/stack-2026/CRITICAL-SECURITY-POLICY.md)
- [MANDATORY-FIREWALL-SETUP.md](/home/adminmatej/github/stack-2026/security/MANDATORY-FIREWALL-SETUP.md)

### Security Features
- JWT tokens with expiration (7-day default)
- Bcrypt password hashing (12 rounds)
- SQL injection protection (SQLAlchemy ORM)
- CORS with allowed origins
- Environment variables for secrets
- Protected routes with auth middleware
- Input validation (Pydantic schemas)

## 📚 Documentation

### Getting Started & Ops
- **[Scripts Guide](docs/SCRIPTS.md)** - Port management and startup scripts
- **[Database Setup](docs/DATABASE_SETUP.md)** - Database configuration
- **[Hetzner Deployment](infra/HETZNER_DEPLOYMENT.md)** - Hetzner-specific guide
- **[Platform Integration](infra/PLATFORM_INTEGRATION.md)** - Platform integration
- **[Legacy Quick Start](./_archive/QUICK_START_GUIDE.md)** - Archived quick start
- **[Legacy Testing Guide](./_archive/TESTING_GUIDE.md)** - Archived testing doc

### Architecture & UX
- **[Hybrid Execution Guide](docs/HYBRID-EXECUTION-GUIDE.md)** - Deterministic vs ii-agent routing
- **[AI-First Hybrid UX Plan](docs/AI_FIRST_HYBRID_UX_PLAN.md)** - Current experience plan
- **[HUD Workflow Scenarios](docs/HUD_WORKFLOW_SCENARIOS.md)** - HUD validation scenarios
- **[AI-First Audit](docs/AI_FIRST_AUDIT.md)** - Architecture audit & gaps
- **[AI-First UI Redesign](docs/AI_FIRST_UI_REDESIGN.md)** - Context panel/ui redesign
- **[Track 3 Architecture](docs/TRACK_3_ARCHITECTURE.md)** - Assistant/voice unification
- **[Gap Completion Plan](docs/GAP_COMPLETION_PLAN.md)** - AI-first gap roadmap

### Data, Quality, and Telemetry
- **[Settings Migration Status](docs/MIGRATION_STATUS.md)** - Migration progress
- **[Settings Migration Summary](docs/SETTINGS_MIGRATION_SUMMARY.md)** - Before/after models/prompts
- **[Completion Summary](docs/COMPLETION_SUMMARY.md)** - Settings modernization summary
- **[Command History & Telemetry](docs/COMMAND_HISTORY_AND_TELEMETRY.md)** - Telemetry model
- **[Testing Coverage Report](docs/TESTING_COVERAGE_REPORT.md)** - Coverage status
- **[Quality & Testing Deliverables](docs/QUALITY_TESTING_DELIVERABLES.md)** - Testing plan/deliverables

### API & Integrations
- **[FastAPI Docs](http://localhost:8000/docs)** - Live interactive API docs
- **[Gemini File Search](docs/GEMINI_FILE_SEARCH.md)** - File search integration
- **[Mobile Integrations](docs/INTEGRATIONS_MOBILE_GUIDE.md)** - Mobile integration flow
- **[Offline Inference](docs/OFFLINE_INFERENCE_STRATEGY.md)** - Offline model strategy
- **[Privacy Policy](docs/PRIVACY_POLICY.md)** - Privacy commitments
- **[Archived API Reference](./_archive/docs/API_REFERENCE.md)** - Static reference (legacy)

### For Contributors
- **[Stack 2025 Compliance](#stack-2026-compliance)** - Architecture requirements

## 🧪 Testing

**Status**: ✅ Implemented

The project includes a suite of end-to-end (E2E) tests for critical user flows, built with **Playwright**.

- **Authentication**: Covers login, registration, and error handling.
- **AI Chat**: Verifies message sending, response rendering, and markdown support.
- **Task Management**: Ensures tasks can be created, updated, and deleted.
- **Navigation**: Confirms that all primary dashboard routes are accessible.

**To run tests:**
```bash
./scripts/test.sh
```

### Planned Enhancements
- **Unit Tests**: Add unit tests for frontend components (Vitest) and backend logic (pytest).
- **Integration Tests**: Expand integration tests to cover all API endpoints.
- **Coverage**: Implement code coverage reporting.


## 🚢 Deployment

### Recommended Platforms
- **Frontend**: Vercel (SvelteKit optimized)
- **Backend**: Railway (FastAPI + PostgreSQL)
- **Database**: Railway PostgreSQL or Supabase

### Environment Variables

**Frontend** (`.env`, required):
```bash
PUBLIC_API_URL=https://api.yourdomain.com
# Must include http(s) scheme
```

**Backend** (`.env`):
```bash
DATABASE_URL=postgresql://user:password@localhost:5432/focus_kraliki
ANTHROPIC_API_KEY=sk-ant-api03-...
OPENAI_API_KEY=sk-...
DEEPGRAM_API_KEY=...  # Optional (transcription only)
DEEPGRAM_MODEL=nova-2-general
GEMINI_API_KEY=
GEMINI_AUDIO_MODEL=gemini-2.5-flash-native-audio-preview-09-2025
OPENAI_REALTIME_API_KEY=
OPENAI_REALTIME_MODEL=gpt-4o-realtime-preview-2024-12-17
OPENAI_TTS_MODEL=gpt-4o-mini-tts
JWT_SECRET=your-secret-key-minimum-32-characters
SESSION_SECRET=another-secret-key-minimum-32-characters
TWILIO_ACCOUNT_SID=
TWILIO_AUTH_TOKEN=
TELNYX_API_KEY=
PORT=8000
NODE_ENV=production
ALLOWED_ORIGINS=https://your-domain.com
STATIC_FILE_BASE_URL=https://cdn.example.com  # Optional (static asset hosting)
II_AGENT_WEBHOOK_SECRET=your-webhook-secret
GOOGLE_CALENDAR_WEBHOOK_TOKEN=optional-token
```

## 📈 Performance Metrics

### Bundle Size
- **Frontend**: ~150kb gzipped (60% smaller than React)
- **Backend**: ~20MB memory footprint

### Development Speed
- **Frontend**: 2x faster than React
- **Backend**: 2.4x faster than TypeScript

### Code Metrics
- **Frontend**: 14 source files, ~2,200 lines
- **Backend**: 25 Python files, ~3,500 lines, 68 endpoints
- **Reduction**: 65% less backend code vs TypeScript

## 🎯 Recent Updates (Nov 2025)

### New Features
- ✅ **Modern Brutalism Design**: Complete redesign with bold, uncompromising aesthetics
- ✅ **Dark Mode**: Full dark mode support with brutalist styling
- ✅ **Calendar Integration**: Two-way sync with Google Calendar, supporting real-time webhooks
- ✅ **Conflict Resolution**: Smart policies (last-modified, manual, source-priority) for data sync
- ✅ **II-Agent Webhooks**: Secure event delivery for agent status updates
- ✅ **Port Management**: Automatic port cleanup and PID tracking scripts
- ✅ **Knowledge Layer**: Advanced knowledge management system
- ✅ **Workspaces**: Multi-workspace support for team collaboration
- ✅ **File Search**: Gemini-powered file search and indexing
- ✅ **Agent Tools API**: Comprehensive agent tools integration
- ✅ **Analytics**: Advanced analytics and insights
- ✅ **Billing System**: AI usage billing and credit management

### Improvements
- ✅ **Script Management**: Added dev-start.sh, dev-stop.sh, prod-start.sh, prod-stop.sh
- ✅ **Theme System**: CSS variable-based theming with semantic colors
- ✅ **Error Handling**: Brutalist-styled error and success messages
- ✅ **Documentation**: Added docs/SCRIPTS.md for port management guide

### Documentation Cleanup
- ✅ Removed outdated implementation reports and phase documents
- ✅ Consolidated documentation into clear categories
- ✅ Updated all references to current architecture and ports

## 🐛 Known Issues & Roadmap

### High Priority
- [x] Complete Google OAuth redirect flow
- [ ] Add form validation (Zod + superforms)
- [ ] Implement real-time updates (WebSocket/polling)
- [ ] Add error boundaries
- [x] Write comprehensive tests (Coverage increased to ~45%)

### Medium Priority
- [ ] PWA support (service worker)
- [ ] Push notifications
- [ ] Offline mode (IndexedDB)
- [ ] Calendar integration
- [ ] Data export (JSON/CSV/PDF)

### Low Priority
- [ ] Advanced filters
- [ ] Task templates
- [ ] Collaborative features
- [ ] Mobile app (Capacitor)

## 🤝 Contributing

### Stack 2025 Compliance

**Requirements:**
- ✅ Use **pnpm** (NOT npm/yarn)
- ✅ Use **SvelteKit** for frontend (NOT Next.js)
- ✅ Use **FastAPI** for backend (NOT Express)
- ✅ Use **TypeScript** for frontend
- ✅ Use **Python** for backend
- ✅ Use **127.0.0.1** for development
- ✅ Test before claiming completion

**Code Style:**
- Frontend: Prettier + ESLint
- Backend: Black + isort + flake8
- Commits: Conventional Commits

## 📄 License

Proprietary - All Rights Reserved

## 🎉 Success Metrics

### ✅ Achieved
- ✅ Complete monorepo structure with clear separation
- ✅ SvelteKit 2.0 frontend (14 files, 8 pages)
- ✅ FastAPI backend (32+ files, 90+ endpoints)
- ✅ 100% feature parity with original design
- ✅ 65% code reduction (backend)
- ✅ 40% smaller bundle (frontend)
- ✅ Full Stack 2025 compliance
- ✅ Revolutionary AI features with caching & flow memory
- ✅ Voice processing with intent detection & voice-to-task
- ✅ Workflow automation with AI-generated templates
- ✅ Markdown rendering & syntax highlighting in chat
- ✅ Redis-based caching & session management
- ✅ Dockerized deployment (multi-stage builds)
- ✅ CI/CD pipeline with GitHub Actions
- ✅ Integration tests for critical endpoints
- ✅ Utility scripts for all operations
- ✅ Comprehensive documentation

---

**Focus by Kraliki** - Simply In, Simply Out

**Built with Stack 2025**: SvelteKit 2.0 + FastAPI + PostgreSQL + TypeScript + Python
**Status**: ✅ Production-Ready | **Version**: 2.4.0 | **Updated**: December 25, 2025

**Quick Links**: [Docs](docs/) | [Scripts Guide](docs/SCRIPTS.md) | [API Docs](http://localhost:8000/docs) | [Legacy Quick Start](_archive/QUICK_START_GUIDE.md)
