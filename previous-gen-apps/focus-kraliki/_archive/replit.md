# Focus Lite - Replit Setup

## Project Overview
Focus Lite is an AI-first productivity system built with SvelteKit (frontend) and FastAPI (backend), now running on Replit with ii-agent integration for advanced AI capabilities.

**Architecture:**
- **Frontend**: SvelteKit 2.0 on port 5000 (0.0.0.0)
- **Backend**: FastAPI on port 3017 (127.0.0.1)
- **ii-agent**: Intelligent agent service on port 8765 (127.0.0.1)
- **Database**: Replit PostgreSQL (auto-connected via DATABASE_URL)
- **AI Provider**: OpenRouter (6 models via Replit AI Integrations)
- **Event System**: In-memory mode (Redis/RabbitMQ not required)

## Quick Start

The application starts automatically via the "Focus Lite" workflow. All three services run concurrently:
- **Frontend** accessible via Replit webview
- **Backend API** docs at http://127.0.0.1:3017/docs (internal only)
- **ii-agent** WebSocket server at http://127.0.0.1:8765 (internal only)

## Configuration Changes for Replit

### Frontend (vite.config.ts)
```typescript
server: {
  port: 5000,
  host: '0.0.0.0',           // Required for Replit
  strictPort: true,
  allowedHosts: true,         // CRITICAL: Allows Replit proxy
  hmr: {
    clientPort: 443           // Required for HMR through proxy
  }
}
```

### Backend (config.py)
- Made AI API keys optional (ANTHROPIC_API_KEY, OPENAI_API_KEY)
- Enabled in-memory events: `USE_INMEMORY_EVENTS=True`
- Added JWT_SECRET default for quick setup
- DATABASE_URL automatically uses Replit PostgreSQL

### Database Models
Fixed SQLAlchemy reserved keyword conflicts:
- `voice_recording.metadata` → `record_metadata`
- `workflow_template.metadata` → `template_metadata`

## Environment Variables

**Required (via Replit Secrets or .env):**
- `DATABASE_URL` - Auto-set by Replit PostgreSQL

**AI Integration (Automatically Configured):**
- `AI_INTEGRATIONS_OPENROUTER_API_KEY` - OpenRouter API via Replit AI Integrations
- `AI_INTEGRATIONS_OPENROUTER_BASE_URL` - OpenRouter base URL
- Models: Grok-4-Fast, Grok-Code-Fast-1, Gemini-2.5-Flash, GLM-4.6, Kimi-K2-Thinking, Polaris-Alpha
- `JWT_SECRET` - Custom JWT secret (has safe default)

**Other optional services:**
- `DEEPGRAM_API_KEY` - Voice transcription
- `GEMINI_API_KEY` - Google AI
- `TWILIO_*` / `TELNYX_*` - Telephony

## File Structure

```
/
├── backend/              # FastAPI backend
│   ├── app/             # Application code
│   │   ├── main.py      # Entry point
│   │   ├── core/        # Config, database, security
│   │   ├── models/      # SQLAlchemy models
│   │   ├── routers/     # API endpoints (now using OpenRouter)
│   │   └── schemas/     # Pydantic schemas
│   └── .env             # Backend environment
├── frontend/            # SvelteKit frontend
│   ├── src/
│   │   ├── routes/      # Pages
│   │   └── lib/         # Components, stores
│   └── .env             # Frontend environment
├── ii-agent/            # Intelligent agent framework
│   ├── src/             # Agent source code
│   ├── data/            # SQLite database & file storage
│   └── .env             # Agent configuration
├── start.sh             # Startup script (all three services)
└── replit.md            # This file
```

## ii-agent Integration

**What is ii-agent?**
- Open-source intelligent assistant framework (3K+ GitHub stars)
- Capabilities: Code generation, research, web browsing, file editing, PDF/audio/video processing
- WebSocket-based for real-time interactions
- Uses OpenRouter models via Replit AI Integrations

**API Endpoints:**
- `GET /api/settings` - Get agent configuration
- `POST /api/settings` - Update agent configuration
- `GET /api/sessions/{device_id}` - List sessions
- `GET /api/sessions/{session_id}/events` - Get session events
- `POST /api/upload` - Upload files to workspace
- `WS /ws` - WebSocket for real-time agent interactions

**Storage:**
- Database: SQLite at `ii-agent/data/ii_agent.db`
- Workspace: `ii-agent/data/workspace/`
- Both are persistent when deployed to Replit

## Deployment

Focus Lite is configured for **Autoscale deployment** on Replit:

### Production Configuration
- **Deployment Type**: Autoscale
- **Build Command**: `bash -c "pip install -r backend/requirements.txt && cd frontend && pnpm install --frozen-lockfile && pnpm build"`
- **Run Command**: `bash scripts/start-production.sh`
- **Exposed Port**: 5000 (frontend with proxy to backend)
- **Health Check**: `GET /` returns 200 OK from SvelteKit

### SvelteKit Adapter
- Uses **@sveltejs/adapter-node** for production builds
- Build output in `frontend/build/` directory
- Runs as standalone Node.js server

### Production Start Script
The `scripts/start-production.sh` script:
- Starts FastAPI backend on `0.0.0.0:3017` (production mode, no reload)
- Starts SvelteKit frontend on `0.0.0.0:${PORT:-5000}` using `node build/index.js`
- Respects platform-assigned PORT for autoscale deployments
- Handles graceful shutdown with SIGTERM/SIGINT traps
- Exports PYTHONPATH and BACKEND_URL for proper configuration

### API Routing in Production
The frontend uses **server-side proxy** (via SvelteKit hooks) to route `/api/*` requests:
- Browser → Frontend (port 5000) → Server Hook Proxy → Backend (port 3017)
- Proxy preserves `/api` prefix and supports streaming (SSE/chat)
- Only port 5000 is publicly exposed
- Backend remains internal for security

### Required Secrets for Deployment
Set these in the **Deployments pane** (not just Secrets pane):
- `DATABASE_URL` - PostgreSQL connection string
- `JWT_SECRET` - JWT token signing secret (optional, has default)
- `ANTHROPIC_API_KEY` - Claude AI (optional)
- `OPENAI_API_KEY` - GPT-4 AI (optional)

### Health Endpoints
- Frontend: `GET /` → 200 OK (SvelteKit app)
- Backend: `GET /api/health` → `{"status": "healthy"}`

### Development vs Production

**Development** (`start.sh`):
- Uses `uvicorn --reload` for hot reloading
- Uses `pnpm dev` with HMR
- Backend on `127.0.0.1:3017` (localhost only)

**Production** (`scripts/start-production.sh`):
- Uses `uvicorn` without reload (stable)
- Uses `node build/index.js` (adapter-node output)
- Backend on `0.0.0.0:3017` (network accessible)
- Frontend on `0.0.0.0:${PORT:-5000}` (respects platform port)

## Known Limitations

1. **Redis/RabbitMQ**: Not available - uses in-memory event system
2. **Migrations**: Alembic migrations disabled - tables created via SQLAlchemy metadata
3. **Voice features**: Require optional API keys (DEEPGRAM, GEMINI, OPENAI)

## Troubleshooting

**"Blocked request" error:**
- Ensure `allowedHosts: true` in `frontend/vite.config.ts`

**Backend connection error:**
- Check backend is running on port 3017
- Verify DATABASE_URL is set

**HMR not working:**
- Confirm `hmr.clientPort: 443` in vite.config.ts

## Development

To modify the project:
1. Edit files - HMR will auto-reload frontend
2. Backend auto-reloads on file changes (uvicorn --reload)
3. Both services restart when workflow restarts

## Original Documentation

See archived documentation in:
- `README.md` - Full project documentation
- `docs/` - Architecture, backend, frontend guides
- `_archive/` - Previous React/TypeScript implementation
