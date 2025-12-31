Docs Hub: `ocelot-platform/docs/INDEX.md`
# Voice by Kraliki Configuration

> Start here
- Platform docs hub: `ocelot-platform/docs/INDEX.md`
- Voice by Kraliki roadmap: `ocelot-platform/docs/roadmaps/cc-lite/ROADMAP.md`
- AI-first guide: `stack-2026/AI_FIRST_SOFTWARE_DEVELOPMENT.md`

## 📚 Primary Documentation Reference

**Key file**: `/stack-2026/STACK_2026_INDEX.md` is your primary entry point for all Stack 2026 documentation.

**AI-First Development**: See `/stack-2026/AI_FIRST_SOFTWARE_DEVELOPMENT.md` for complete PRD → Tasks → Execute workflow.

---

## 🎯 Tech Stack (Stack 2026 - Python Backend)

**Backend**: Python 3.11+ + FastAPI + SQLAlchemy + PostgreSQL
**Frontend**: SvelteKit 2.0 + TypeScript + Tailwind CSS
**API**: REST (FastAPI auto-generated OpenAPI docs)
**Database**: PostgreSQL 15+ with Alembic migrations

## 🎯 Development Best Practices

### Core Requirements:
1. **Test Everything** - Every feature must have tests (pytest + Playwright)
2. **Track Performance** - Monitor all metrics
3. **Handle Errors** - Comprehensive error handling
4. **Secure by Default** - Follow security best practices
5. **Document Changes** - Keep documentation updated

### Pre-Deployment Checklist:
- [ ] All tests pass (pytest unit, integration, Playwright e2e)
- [ ] Performance metrics acceptable
- [ ] Error handling implemented
- [ ] Documentation updated
- [ ] Security review completed
- [ ] Alembic migrations generated and tested

## 🚨🔒 **CRITICAL SECURITY GUIDELINES**

### **⛔ MANDATORY SECRETS MANAGEMENT**
**Date**: 2025-09-27
**Status**: CRITICAL - IMMEDIATE COMPLIANCE REQUIRED
**Severity**: SECURITY AUDIT FINDINGS - HARDCODED SECRETS DETECTED

### 🔴 ZERO-TOLERANCE RULES

**NEVER commit to git:**
- `.env`, `.env.production`, `.env.local`
- Any file with actual passwords, API keys, or tokens
- JWT secrets, database passwords, OAuth secrets

**ALWAYS use:**
- `.env.production.template` with `CHANGE_ME` placeholders
- Docker secrets for production
- Secret managers (Vault, AWS Secrets Manager)

### 🚨 Security Audit Findings to Fix

1. **Hardcoded secrets in production configs** - CRITICAL
2. **127.0.0.1 bindings break container networking** - HIGH
3. **Demo users enabled in production template** - HIGH
4. **⛔ REDIS SECURITY (Hetzner/German Authorities)** - CRITICAL: Redis MUST be on internal network ONLY (`internal: true`), NEVER expose port 6379 to host, require strong password (32+ chars), disable dangerous commands. See `/ocelot-platform/docs/REDIS_SECURITY.md`
4. **CSP too permissive (unsafe-inline/eval)** - MEDIUM

### 📋 Required Security Practices

```bash
# Generate secrets properly
openssl rand -base64 32  # JWT secrets
openssl rand -hex 32      # Cookie secrets
openssl rand -base64 24   # Passwords

# Use Docker secrets
docker secret create jwt_secret jwt_secret.txt

# Container networking fix
HOST=0.0.0.0         # In containers
REDIS_HOST=redis     # Use service names, not 127.0.0.1
DB_HOST=postgres     # Use service names, not localhost
```

### ⚠️ Production Checklist
- [ ] All secrets use `CHANGE_ME` in templates
- [ ] `SEED_DEMO_USERS=false` in production
- [ ] `ENABLE_DEBUG_LOGGING=false` in production
- [ ] Container networking uses service names
- [ ] Secrets stored in Docker secrets or vault
- [ ] SSL/TLS properly configured
- [ ] CSP headers tightened

**See**: [SECRETS_MANAGEMENT_POLICY.md](./docs/security/SECRETS_MANAGEMENT_POLICY.md)

---


# CLAUDE.md - CC Light Application

## 🤖 AI-First Development (MANDATORY)

**See**: `/stack-2026/AI_FIRST_SOFTWARE_DEVELOPMENT.md` for complete workflow

**Quick Start**:
1. Create PRD: Reference `/github/ai-dev-tasks/create-prd.md`
2. Generate Tasks: Reference `/github/ai-dev-tasks/generate-tasks.md`
3. Execute: One sub-task at a time with verification

**Agent Instructions**: Use explicit STEP-by-STEP pattern with tool names, absolute paths, complete code

**External Reference**: `/github/ai-dev-tasks/` (read-only)

---

## 📦 Package Manager
**Use `pnpm`** for all package management:
- `pnpm install` - Install dependencies
- `pnpm dev` - Start development
- `pnpm build` - Build for production

## 🐍 Python Runtime (AI Agents & Backend)
**MANDATORY**: Use `uv` for all Python execution:
- `uv run script.py` - Execute scripts in isolated sandbox
- `uv pip install package` - Install dependencies (10-100x faster)
- `uv venv` - Create virtual environments

**FORBIDDEN**: Direct `python`, `pip`, or `python -m venv`
**WHY**: Instant sandboxing, global caching, reproducible environments
**POLICY**: See `/stack-2026/policies/UV_PYTHON_POLICY.md`

**Examples**:
```bash
# ❌ FORBIDDEN (slow, pollutes global env)
python backend/app/main.py
pip install fastapi

# ✅ REQUIRED (fast, isolated, cached)
uv run backend/app/main.py
uv pip install fastapi
```

## 🔧 Core Packages

This app includes bundled packages in `/vendor/packages/`:
- `@unified/auth-core` - Authentication
- `@unified/ui` - UI components
- `@unified/telephony` - Phone/VoIP features
- `@stack-2025/bug-report-core` - Bug reporting
- And more utility packages

## 🎯 CRITICAL DEVELOPMENT RESOURCE

**MANDATORY READING**: https://callminer.com/blog/the-future-of-ai-call-center-automation-in-2024-and-beyond

This CallMiner analysis is our **NORTH STAR** for feature development. All AI features, automation capabilities, and roadmap decisions MUST align with the industry trends and insights from this resource.

**See**: [docs/AI_CALL_CENTER_FUTURE_2025.md](./docs/AI_CALL_CENTER_FUTURE_2025.md) for our implementation roadmap based on this analysis.

## 🎯 Application Overview

CC Light is a lightweight call center application built with modern web technologies. This is a **standalone application** ready for deployment.

## 📁 Project Structure

```
cc-lite/
├── backend/             # Fastify + tRPC API (renamed from server/)
│   ├── trpc/           # 11 tRPC routers
│   ├── services/       # Business logic
│   └── index.ts        # Server entry point
├── frontend/           # SvelteKit UI (renamed from frontend-svelte-kit/)
│   ├── src/
│   │   ├── routes/    # SvelteKit routes
│   │   └── lib/       # Components & utilities
│   └── static/
├── prisma/             # Database schema
├── tests/              # Playwright E2E tests
├── vendor/packages/    # Bundled Stack 2026 packages
└── docs/               # Documentation
```

## 🐳 Docker Deployment

**Production deployments should use Docker containers** for best reliability and scalability.

### Why Docker + PM2 (Not Just PM2)
- **Docker**: Manages entire stack (PostgreSQL, Redis, RabbitMQ, Nginx)
- **PM2**: Manages Node.js processes inside containers
- **Together**: Production-grade reliability with minimal overhead (3-5%)

### Required Implementation
```yaml
# docker compose.production.yml is MANDATORY
services:
  app:
    build: .
    command: pm2-runtime start ecosystem.config.js
    restart: always
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:3900/health"]
```

### Deployment Hierarchy
1. **Development**: `pnpm dev` (local)
2. **Staging**: `docker compose up` (Docker)
3. **Production**: `docker compose -f docker compose.production.yml up -d` (Docker + PM2)

**Cost**: Hetzner VM + Docker = $27/month vs AWS = $535/month (20x savings)

See [Docker Deployment Policy](./docs/DOCKER_DEPLOYMENT_POLICY.md) for full details.

## 🚀 Quick Start

```bash
# Install dependencies
pnpm install

# Setup database
pnpm prisma migrate dev

# Start development
pnpm dev:all          # Both frontend and backend
pnpm dev:frontend     # SvelteKit on port 5173
pnpm dev:backend      # Fastify on port 3010

# Production build
pnpm build
```

## 📋 Technical Architecture

### Package Usage
```typescript
// Authentication
import { verifyToken, createToken } from '@unified/auth-core';

// UI Components
import { Button } from '@unified/ui';

// Telephony
import { TwilioProvider } from '@unified/telephony';
```

### Migration Status (TypeScript → Python Backend)
- 🚧 **Migrating to Python 3.11+ + FastAPI**
- ✅ **SvelteKit 2.0** frontend (keeping)
- ✅ **PostgreSQL** database (keeping)
- 🔄 **Prisma → SQLAlchemy + Alembic**
- 🔄 **tRPC → FastAPI REST** (OpenAPI auto-docs)
- ✅ **Playwright** testing (keeping)
- 🔄 **Telephony** → Python libraries

### Migration TODO
- [ ] Create Python backend structure (backend/app/)
- [ ] Migrate Prisma schema to SQLAlchemy models
- [ ] Convert 11 tRPC routers to FastAPI endpoints
- [ ] Migrate authentication to Python JWT (python-jose)
- [ ] Port telephony services to Python (Twilio Python SDK)
- [ ] Update SvelteKit frontend to REST API
- [ ] Setup Alembic migrations
- [ ] Port tests to pytest

## 🔧 Technology Stack (Stack 2026 Aligned)

### Backend (`/backend`) - **Migrating to Python**
- **Language**: Python 3.11+
- **Framework**: FastAPI 0.110+
- **API**: REST with auto-generated OpenAPI docs
- **Database**: PostgreSQL 15+
- **ORM**: SQLAlchemy 2.0+
- **Migrations**: Alembic
- **Validation**: Pydantic 2.0+
- **Auth**: python-jose (JWT)
- **Telephony**: Twilio Python SDK, Deepgram SDK
- **AI**: OpenAI Python SDK, Anthropic SDK
- **Testing**: pytest, pytest-asyncio

### Frontend (`/frontend`) - **Keeping SvelteKit**
- **Framework**: SvelteKit 2.0
- **Language**: TypeScript
- **UI**: Tailwind CSS
- **State**: Svelte stores
- **API Client**: fetch (REST endpoints)
- **Routing**: SvelteKit file-based routing
- **Testing**: Playwright (all browsers)

## 📋 Development Guidelines (Python Backend)

### API Development
All endpoints use FastAPI with automatic OpenAPI documentation:
```python
# ✅ REQUIRED: Use FastAPI routers with Pydantic schemas
from fastapi import APIRouter, Depends
from pydantic import BaseModel

router = APIRouter(prefix="/api/calls", tags=["calls"])

class CallCreate(BaseModel):
    phone_number: str
    campaign_id: str

@router.post("/", response_model=CallResponse)
async def create_call(
    call_data: CallCreate,
    current_user: User = Depends(get_current_user)
):
    return await call_service.create(call_data)
```

### Database Models
Use SQLAlchemy 2.0 declarative models:
```python
# ✅ REQUIRED: SQLAlchemy models with proper relationships
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime

class Call(Base):
    __tablename__ = "calls"

    id: Mapped[str] = mapped_column(primary_key=True)
    from_number: Mapped[str]
    to_number: Mapped[str]
    status: Mapped[str]
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)

    # Relationships
    agent: Mapped["User"] = relationship(back_populates="calls")
```

### Testing Requirements
Backend tests use pytest, E2E tests use Playwright:
```python
# ✅ Backend unit tests with pytest
import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_create_call(async_client: AsyncClient, auth_headers):
    response = await async_client.post(
        "/api/calls",
        json={"phone_number": "+1234567890", "campaign_id": "test"},
        headers=auth_headers
    )
    assert response.status_code == 200
    assert response.json()["status"] == "queued"
```

```typescript
// ✅ E2E tests with Playwright (kept as-is)
test('call center workflow', async ({ page }) => {
  // Test on Chrome, Firefox, Safari, Mobile
});
```

## 🧪 Testing

```bash
# Backend tests (Python)
cd backend
pytest                    # All tests
pytest -v                 # Verbose
pytest --cov=app          # With coverage
pytest -k "test_auth"     # Specific tests

# E2E tests with Playwright
pnpm test:e2e

# Integration tests
pytest tests/integration/
```

## 🔄 Current Implementation Status

### ✅ Completed
- [x] Migrated to SvelteKit frontend
- [x] Reorganized to backend/frontend structure
- [x] Created @unified/telephony package
- [x] Implemented 11 tRPC routers
- [x] Fixed authentication flow
- [x] Restored operator dashboard
- [x] Fixed supervisor cockpit
- [x] Added Playwright tests with user agents
- [x] All tests passing on all browsers

### 🚧 In Progress
- [ ] Complete SvelteKit UI migration
- [ ] Update all tRPC client calls in frontend
- [ ] Full @unified/auth-core integration
- [ ] Production Twilio credentials

### 📊 Features Working

#### Authentication
- ✅ Login page with demo accounts
- ✅ Role-based routing
- ✅ Mock JWT tokens
- ✅ Session management

#### Dashboards
- ✅ **Supervisor Dashboard** (`/supervisor`)
  - Active calls monitoring
  - Live transcription view
  - Queue management
  
- ✅ **Operator Dashboard** (`/operator`)
  - Agent status controls
  - Call queue display
  - Performance metrics
  - Quick actions

#### API Endpoints (tRPC)
- ✅ auth.router.ts - Authentication
- ✅ agents.router.ts - Agent management
- ✅ calls.router.ts - Call handling
- ✅ campaigns.router.ts - Campaign management
- ✅ conversations.router.ts - Chat/messaging
- ✅ notifications.router.ts - Alerts
- ✅ reports.router.ts - Analytics
- ✅ settings.router.ts - Configuration
- ✅ supervisors.router.ts - Supervisor functions
- ✅ teams.router.ts - Team management
- ✅ webhooks.router.ts - External integrations

## 🔒 Security

- JWT authentication with mock tokens
- Role-based access control (ADMIN, SUPERVISOR, AGENT)
- Webhook signature verification
- Environment-based configuration

## 📝 Test Accounts

### Universal Test Account (MANDATORY)
```yaml
Email: test.assistant@stack2025.com
Password: Stack2025!Test@Assistant#Secure$2024
User ID: 550e8400-e29b-41d4-a716-446655440000
Role: TESTER_UNIVERSAL
Tier: CORPORATE (all features)
```

**CRITICAL**: Always use the universal test account for:
- ✅ Cross-app testing
- ✅ Feedback loops  
- ✅ SSO validation
- ✅ BYOK testing
- ✅ Public URL testing

### Legacy Test Accounts (Local Only)
```typescript
// Admin Account (local dev only)
email: 'admin@cc-light.local'
password: process.env.DEFAULT_ADMIN_PASSWORD

// Supervisor Account (local dev only)
email: 'supervisor@cc-light.local'
password: process.env.DEFAULT_SUPERVISOR_PASSWORD

// Agent Account (local dev only)
email: 'agent1@cc-light.local'
password: process.env.DEFAULT_AGENT_PASSWORD
```

## 🎯 Next Steps

Based on CallMiner analysis, prioritize:
1. **AI Transcription** - Real-time call transcription
2. **Sentiment Analysis** - Detect customer emotions
3. **Agent Assist** - Real-time suggestions
4. **Conversation Intelligence** - Extract insights
5. **Predictive Analytics** - Forecast outcomes

---

## 🤖 AI Agent Instructions (CRITICAL)

### How to Get AI Agents to Write ACTUAL Code (Not Specs)

**Problem**: AI agents create beautiful specifications but **0 actual files**

**Solution**: Use **EXPLICIT step-by-step instructions** with tool names

### ❌ WRONG (Results in Specifications Only)
```
"Implement Czech + English i18n for the frontend"
```
→ Result: 10-page specification document, 0 files created

### ✅ CORRECT (Results in Real Code)
```
STEP 1: Use Bash tool to run:
  cd /home/adminmatej/github/applications/cc-lite/frontend
  pnpm add -D sveltekit-i18n

STEP 2: Use Write tool to create /home/.../src/lib/i18n/index.ts with this EXACT code:
  [paste complete code here]

STEP 3: Use Bash tool to verify file exists:
  ls -lh /home/.../src/lib/i18n/index.ts

STEP 4: Use Write tool to create /home/.../src/routes/+layout.ts with this code:
  [paste complete code here]
```

### Agent Instruction Template

```markdown
## Task: [Feature Name]

**CRITICAL**: You MUST write actual files, not specifications. Use Write/Edit/Bash tools explicitly.

### Step-by-step Instructions

**STEP 1: [Action]**
1a. Use Bash tool to run:
```bash
cd /path/to/app
[exact command]
```

**STEP 2: [Create File]**
2a. Use Write tool to create `/absolute/path/to/file.ts`:
```typescript
[complete file contents - no placeholders]
```

**STEP 3: [Verify]**
3a. Use Bash tool to verify:
```bash
ls -lh /absolute/path/to/file.ts
```

**STEP 4: [Documentation]**
4a. Use Write tool to create `/path/IMPLEMENTATION_COMPLETE.md`:
```markdown
# Feature Implementation Complete

## Files Created
1. /path/file1.ts (size)
2. /path/file2.ts (size)

## Verification
[paste ls output here]
```

### Success Criteria
- [ ] All files created (not specs)
- [ ] Files verified with ls commands
- [ ] Dependencies installed
- [ ] Documentation created
- [ ] No errors encountered

### Return Format
Provide:
1. List of files created with sizes (from ls -lh)
2. Command outputs (npm install, etc.)
3. File verification results
4. Any errors encountered
```

### Key Principles

1. **Always specify tool names**: "Use Write tool", "Use Bash tool", "Use Edit tool"
2. **Always use absolute paths**: `/home/adminmatej/github/...` not `./`
3. **Always provide complete code**: No `[add your code here]` placeholders
4. **Always verify with ls**: After every file creation
5. **Always document**: Create summary with actual file sizes

### Proven Success Pattern (Week 3-4)

Using this pattern, we achieved:
- ✅ 66 files created (real code)
- ✅ ~13,500 lines of working code
- ✅ 0 errors
- ✅ 100% success rate

**vs Previous Attempt** (vague instructions):
- ❌ 47 specifications created
- ❌ 0 actual files
- ❌ 10,000 lines of documentation
- ❌ 0% implementation

### Example: Real Agent Prompt That Worked

```markdown
## Week 3-4 Task: Czech + English i18n

**CRITICAL**: You MUST write actual files, not specifications.

**STEP 1: Install i18n**
1a. Use Bash tool to run:
```bash
cd /home/adminmatej/github/applications/cc-lite/frontend
pnpm add -D sveltekit-i18n
```

**STEP 2: Create i18n store**
2a. Use Write tool to create `/home/adminmatej/github/applications/cc-lite/frontend/src/lib/i18n/index.ts`:
```typescript
import { derived, writable } from 'svelte/store';

export const locale = writable('en');

export const translations = {
  en: {
    'nav.dashboard': 'Dashboard',
    'nav.calls': 'Calls'
  },
  cs: {
    'nav.dashboard': 'Přehled',
    'nav.calls': 'Hovory'
  }
};

export const t = derived(locale, ($locale) => (key: string) => {
  return translations[$locale]?.[key] || key;
});
```

**STEP 3: Verify**
3a. Use Bash tool:
```bash
ls -lh /home/adminmatej/github/applications/cc-lite/frontend/src/lib/i18n/index.ts
```
```

**Result**: File created successfully with exact code! ✅

---

**Remember**:
- This is an independent repository
- Always check CallMiner resource for feature priorities
- Use Stack 2026 packages, never custom implementations
- Test everything with Playwright across all browsers
- **Use explicit agent instructions with tool names for all AI tasks**
