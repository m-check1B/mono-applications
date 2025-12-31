# Voice by Kraliki: TypeScript → Python Backend Migration Guide

**Date**: October 1, 2025
**Status**: 🚧 In Progress
**Stack**: Stack 2026 - Python 3.11+ + FastAPI + SQLAlchemy

---

## 🎯 Migration Overview

### Why Python?

Per **Stack 2026 standards**, Python backend is recommended for:
- **AI/ML Integration**: Native Python AI/ML libraries (OpenAI, Anthropic, Deepgram)
- **Telephony**: Mature Python SDKs (Twilio, Telnyx)
- **Rapid Development**: Faster prototyping and iteration
- **Team Expertise**: Better alignment with data science team

### Technology Stack

| Component | From (Old) | To (New) |
|-----------|------------|----------|
| **Backend Language** | TypeScript | Python 3.11+ |
| **Backend Framework** | Fastify | FastAPI 0.110+ |
| **API Style** | tRPC | REST (OpenAPI docs) |
| **Database ORM** | Prisma | SQLAlchemy 2.0+ |
| **Migrations** | Prisma Migrate | Alembic |
| **Validation** | Zod | Pydantic 2.0+ |
| **Auth** | JWT (jsonwebtoken) | JWT (python-jose) |
| **Frontend** | SvelteKit ✅ | SvelteKit ✅ (keeping) |
| **Database** | PostgreSQL ✅ | PostgreSQL ✅ (keeping) |
| **Testing (Backend)** | Vitest | pytest + pytest-asyncio |
| **Testing (E2E)** | Playwright ✅ | Playwright ✅ (keeping) |

---

## 📁 New Directory Structure

```
cc-lite/
├── backend-python/          # 🆕 NEW Python backend
│   ├── app/
│   │   ├── main.py          # FastAPI application
│   │   ├── core/            # Config, database, logging
│   │   ├── models/          # SQLAlchemy models
│   │   ├── schemas/         # Pydantic schemas
│   │   ├── routers/         # API endpoints
│   │   ├── services/        # Business logic
│   │   ├── middleware/      # FastAPI middleware
│   │   └── utils/           # Utilities
│   ├── alembic/             # Database migrations
│   ├── tests/               # pytest tests
│   ├── requirements.txt     # Dependencies
│   ├── pyproject.toml       # Poetry config
│   └── .env.example         # Environment template
│
├── backend/                 # 🗄️ OLD TypeScript backend (archive when done)
├── frontend/                # ✅ SvelteKit (keeping as-is)
├── prisma/                  # 🗄️ Archive when SQLAlchemy complete
└── docs/                    # Documentation
```

---

## 🔄 Migration Steps

### Phase 1: Foundation (✅ COMPLETED)

- [x] Create `backend-python/` directory structure
- [x] Setup `requirements.txt` and `pyproject.toml`
- [x] Create FastAPI application structure (`app/main.py`)
- [x] Setup database configuration (`app/core/database.py`)
- [x] Setup application config (`app/core/config.py`)
- [x] Setup structured logging (`app/core/logger.py`)
- [x] Create sample SQLAlchemy model (`app/models/user.py`)
- [x] Update CLAUDE.md with Python standards

### Phase 2: Database Models (🚧 IN PROGRESS)

- [ ] Convert all Prisma models to SQLAlchemy 2.0
  - [x] User model (sample created)
  - [ ] Organization
  - [ ] Team, TeamMember
  - [ ] Campaign, CampaignMetric
  - [ ] Call, CallMetadata
  - [ ] Contact, ContactSession
  - [ ] IVR models
  - [ ] Agent, AgentMetrics
  - [ ] UserSession
  - [ ] TokenUsage, AuditLog

- [ ] Setup Alembic for migrations
  - [ ] Initialize Alembic: `alembic init alembic`
  - [ ] Configure `alembic.ini`
  - [ ] Create initial migration from Prisma schema
  - [ ] Test migrations on dev database

### Phase 3: API Endpoints (TODO)

Convert 11 tRPC routers to FastAPI REST endpoints:

- [ ] **Authentication** (`auth.router.ts` → `routers/auth.py`)
  - [ ] POST `/api/auth/register`
  - [ ] POST `/api/auth/login`
  - [ ] POST `/api/auth/refresh`
  - [ ] POST `/api/auth/logout`
  - [ ] GET `/api/auth/me`

- [ ] **Users** (`routers/users.py`)
  - [ ] GET `/api/users`
  - [ ] GET `/api/users/{id}`
  - [ ] PUT `/api/users/{id}`
  - [ ] DELETE `/api/users/{id}`

- [ ] **Calls** (`routers/calls.py`)
  - [ ] GET `/api/calls`
  - [ ] POST `/api/calls`
  - [ ] GET `/api/calls/{id}`
  - [ ] PUT `/api/calls/{id}`

- [ ] **Campaigns** (`routers/campaigns.py`)
- [ ] **Agents** (`routers/agents.py`)
- [ ] **Teams** (`routers/teams.py`)
- [ ] **Conversations** (`routers/conversations.py`)
- [ ] **Notifications** (`routers/notifications.py`)
- [ ] **Reports** (`routers/reports.py`)
- [ ] **Settings** (`routers/settings.py`)
- [ ] **Webhooks** (`routers/webhooks.py`)

### Phase 4: Business Logic (TODO)

Port services to Python:

- [ ] **Authentication Service** (`services/auth_service.py`)
  - [ ] JWT token generation (python-jose)
  - [ ] Password hashing (passlib with bcrypt)
  - [ ] User verification
  - [ ] Session management

- [ ] **Telephony Service** (`services/telephony_service.py`)
  - [ ] Twilio integration (Twilio Python SDK)
  - [ ] Call management
  - [ ] WebSocket streams

- [ ] **AI Service** (`services/ai_service.py`)
  - [ ] OpenAI integration
  - [ ] Anthropic integration
  - [ ] Transcription (Deepgram)
  - [ ] TTS (ElevenLabs)

- [ ] **Campaign Service** (`services/campaign_service.py`)
- [ ] **Contact Service** (`services/contact_service.py`)
- [ ] **IVR Service** (`services/ivr_service.py`)

### Phase 5: Frontend Updates (TODO)

- [ ] Replace tRPC client with REST fetch calls
- [ ] Update API client in `frontend/src/lib/api/`
- [ ] Test all frontend pages
- [ ] Update error handling

### Phase 6: Testing (TODO)

- [ ] Port unit tests to pytest
  - [ ] Test auth endpoints
  - [ ] Test user CRUD
  - [ ] Test call management
  - [ ] Test campaign operations

- [ ] Update integration tests
- [ ] Verify E2E tests with Playwright still pass

### Phase 7: Deployment (TODO)

- [ ] Update Docker configuration
- [ ] Update docker compose.yml
- [ ] Update PM2 ecosystem.config.js
- [ ] Update CI/CD pipeline
- [ ] Deploy to staging
- [ ] Deploy to production

### Phase 8: Cleanup (TODO)

- [ ] Archive old TypeScript backend → `_archive/backend-typescript-2025-10-01/`
- [ ] Rename `backend-python/` → `backend/`
- [ ] Update all documentation
- [ ] Remove Prisma dependency
- [ ] Update README.md

---

## 🔧 Development Setup

### Install Python Dependencies

```bash
cd backend-python

# Using pip
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# OR using Poetry
poetry install
poetry shell
```

### Setup Database

```bash
# Copy environment file
cp .env.example .env

# Edit .env with your PostgreSQL credentials
DATABASE_URL=postgresql+asyncpg://cc_lite:password@localhost:5432/cc_lite

# Run Alembic migrations (when ready)
alembic upgrade head
```

### Run Development Server

```bash
# Using uvicorn directly
uvicorn app.main:app --reload --host 127.0.0.1 --port 3010

# OR using Python
python -m app.main

# OR using Poetry
poetry run uvicorn app.main:app --reload
```

### API Documentation

- **Swagger UI**: http://127.0.0.1:3010/docs
- **ReDoc**: http://127.0.0.1:3010/redoc

---

## 📝 Code Patterns

### FastAPI Router Example

```python
# app/routers/calls.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.models import User
from app.schemas.call import CallCreate, CallResponse
from app.services.call_service import CallService

router = APIRouter(prefix="/api/calls", tags=["calls"])

@router.post("/", response_model=CallResponse)
async def create_call(
    call_data: CallCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new outbound call"""
    call_service = CallService(db)
    return await call_service.create_call(call_data, current_user)
```

### SQLAlchemy Model Example

```python
# app/models/call.py
from sqlalchemy import String, DateTime, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base

class Call(Base):
    __tablename__ = "calls"

    id: Mapped[str] = mapped_column(String(30), primary_key=True)
    from_number: Mapped[str] = mapped_column(String(20))
    to_number: Mapped[str] = mapped_column(String(20))
    status: Mapped[str] = mapped_column(String(20))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Relationships
    agent: Mapped["User"] = relationship(back_populates="calls")
```

### Pydantic Schema Example

```python
# app/schemas/call.py
from pydantic import BaseModel, Field
from datetime import datetime

class CallCreate(BaseModel):
    phone_number: str = Field(..., min_length=10, max_length=20)
    campaign_id: str

class CallResponse(BaseModel):
    id: str
    from_number: str
    to_number: str
    status: str
    created_at: datetime

    class Config:
        from_attributes = True  # Pydantic v2 (was orm_mode in v1)
```

---

## 🧪 Testing

### pytest Example

```python
# tests/test_auth.py
import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_login_success(async_client: AsyncClient):
    response = await async_client.post(
        "/api/auth/login",
        json={"email": "agent@test.com", "password": "password123"}
    )
    assert response.status_code == 200
    assert "access_token" in response.json()
```

### Run Tests

```bash
# All tests
pytest

# With coverage
pytest --cov=app --cov-report=html

# Specific test
pytest tests/test_auth.py -v
```

---

## 🚀 Migration Timeline

| Phase | Est. Time | Status |
|-------|-----------|--------|
| Phase 1: Foundation | 2 hours | ✅ Completed |
| Phase 2: Database Models | 1 day | 🚧 In Progress |
| Phase 3: API Endpoints | 2-3 days | ⏳ Pending |
| Phase 4: Business Logic | 2-3 days | ⏳ Pending |
| Phase 5: Frontend Updates | 1 day | ⏳ Pending |
| Phase 6: Testing | 1 day | ⏳ Pending |
| Phase 7: Deployment | 1 day | ⏳ Pending |
| Phase 8: Cleanup | 0.5 days | ⏳ Pending |
| **Total** | **9-12 days** | **10% Complete** |

---

## 📚 References

- [Stack 2026 Standards](/home/adminmatej/github/stack-2026/README.md)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [SQLAlchemy 2.0 Documentation](https://docs.sqlalchemy.org/)
- [Alembic Documentation](https://alembic.sqlalchemy.org/)
- [Pydantic V2 Documentation](https://docs.pydantic.dev/2.0/)
- [focus-lite Reference](/home/adminmatej/github/applications/focus-lite/) - Python backend example
- [cli-toris Reference](/home/adminmatej/github/applications/cli-toris/) - Python backend example

---

## ❓ FAQ

### Why not keep tRPC?

tRPC is TypeScript-only. Python backends must use REST APIs. FastAPI provides:
- Auto-generated OpenAPI (Swagger) documentation
- Pydantic validation (similar to Zod)
- Better Python ecosystem integration

### Will frontend break?

No. Frontend will be updated incrementally to use REST endpoints. Old TypeScript backend stays until migration is complete.

### How to test migration progress?

Both backends can run simultaneously:
- TypeScript: Port 3010 (during migration)
- Python: Port 3011 (testing)

Switch frontend API URL to test Python backend.

---

**Next Steps**: Complete Phase 2 - Database Models
