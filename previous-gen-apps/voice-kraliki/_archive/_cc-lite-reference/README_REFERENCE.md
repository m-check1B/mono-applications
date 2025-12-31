# Voice by Kraliki Reference Template

**Date:** November 10, 2025
**Status:** 📖 READ-ONLY REFERENCE
**Source:** cc-lite-OLD-template
**Purpose:** Feature patterns and implementation reference

---

## ⚠️ CRITICAL: READ-ONLY REFERENCE

This directory contains the old cc-lite codebase for **REFERENCE PURPOSES ONLY**.

### ⛔ DO NOT:
- ❌ Copy/paste code directly from here
- ❌ Merge files from this directory
- ❌ Import dependencies from here
- ❌ Use outdated patterns (Fastify, tRPC, Prisma)
- ❌ Treat this as current/production code

### ✅ DO USE FOR:
- ✅ Understanding feature requirements
- ✅ Reviewing business logic patterns
- ✅ UI/UX design inspiration
- ✅ Data model structure reference
- ✅ API endpoint patterns
- ✅ Validation rule examples

---

## 📂 Directory Structure

### Key Reference Locations

**Backend (Fastify + TypeScript - OUTDATED)**
```
_cc-lite-reference/
├── backend/
│   ├── app/
│   │   ├── routers/
│   │   │   ├── campaigns.py      ← Campaign management reference
│   │   │   ├── teams.py          ← Team management reference
│   │   │   ├── analytics.py     ← Analytics reference
│   │   │   ├── calls.py          ← Call handling reference
│   │   │   ├── agents.py         ← Agent management reference
│   │   │   └── ...
│   │   ├── models/               ← Data model reference
│   │   ├── services/             ← Business logic reference
│   │   └── schemas/              ← Validation schemas reference
│   └── tests/                    ← Test patterns reference
```

**Frontend (SvelteKit - SOME PATTERNS USEFUL)**
```
_cc-lite-reference/
├── frontend/
│   ├── src/
│   │   ├── routes/
│   │   │   ├── campaigns/       ← Campaign UI reference
│   │   │   ├── supervisor/      ← Supervisor cockpit reference
│   │   │   ├── teams/           ← Team UI reference
│   │   │   ├── analytics/       ← Analytics dashboard reference
│   │   │   └── ...
│   │   ├── lib/
│   │   │   ├── i18n/            ← i18n structure reference
│   │   │   ├── components/      ← Component patterns reference
│   │   │   └── stores/          ← State management reference
│   │   └── ...
│   └── tests/                   ← Frontend test patterns reference
```

---

## 🎯 How to Use This Reference

### Example: Implementing Campaign Management

#### ❌ WRONG APPROACH:
```bash
# DON'T DO THIS
cp _cc-lite-reference/backend/app/routers/campaigns.py \
   backend/app/campaigns/routes.py
```

#### ✅ CORRECT APPROACH:

**Step 1: Read and Understand**
```bash
# Read the reference code
cat _cc-lite-reference/backend/app/routers/campaigns.py
cat _cc-lite-reference/frontend/src/routes/campaigns/+page.svelte
```

**Step 2: Document Requirements**
```markdown
## Campaign Management Requirements (from reference)

### API Endpoints Needed:
- POST /api/campaigns - Create campaign
- GET /api/campaigns - List campaigns
- GET /api/campaigns/{id} - Get campaign details
- PUT /api/campaigns/{id} - Update campaign
- DELETE /api/campaigns/{id} - Delete campaign
- POST /api/campaigns/{id}/start - Start campaign
- POST /api/campaigns/{id}/pause - Pause campaign

### Data Model:
- Campaign: id, name, description, status, created_at, updated_at
- Contact List: id, campaign_id, contacts[]
- Call Flow: steps, conditions, actions

### Business Logic:
- Campaign scheduling (time-based, event-driven)
- Contact list management (import CSV, manual entry)
- Call flow automation (IVR, routing)
- Performance tracking (metrics, analytics)

### UI Components:
- Campaign list view (table with filters)
- Campaign detail view (tabs: info, contacts, flow, metrics)
- Campaign creation wizard (step-by-step)
- Campaign scheduler (calendar picker)
```

**Step 3: Implement Fresh in cc-lite-2026**
```python
# backend/app/campaigns/routes.py
# Implement using cc-lite-2026 patterns:
# - FastAPI router (NOT Fastify)
# - SQLAlchemy models (NOT Prisma)
# - Pydantic schemas (existing pattern)
# - Service layer (existing pattern)
# - Circuit breaker for external calls
# - Prometheus metrics for monitoring
# - Structured logging for events

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.campaigns.schemas import CampaignCreate, CampaignResponse
from app.campaigns.service import CampaignService
from app.core.patterns.circuit_breaker import circuit_breaker
from app.core.logging import get_logger

router = APIRouter(prefix="/api/campaigns", tags=["campaigns"])
logger = get_logger(__name__)
campaign_service = CampaignService()

@router.post("/", response_model=CampaignResponse)
@circuit_breaker(failure_threshold=5)
async def create_campaign(
    campaign: CampaignCreate,
    db: Session = Depends(get_db)
):
    """Create new campaign with circuit breaker protection"""
    logger.info("Creating campaign", extra={"name": campaign.name})
    result = await campaign_service.create(db, campaign)
    logger.info("Campaign created", extra={"campaign_id": result.id})
    return result
```

**Step 4: Test Thoroughly**
```bash
# Write comprehensive tests
pytest backend/tests/test_campaigns.py -v
pnpm test:e2e:campaigns

# Verify production score maintained
# Target: 90+ score (maintained from base)
```

---

## 📚 Reference Guide by Feature

### 1. Campaign Management
**Reference Files:**
- Backend: `_cc-lite-reference/backend/app/routers/campaigns.py`
- Frontend: `_cc-lite-reference/frontend/src/routes/campaigns/`
- Models: `_cc-lite-reference/backend/app/models/campaign.py`

**Key Patterns to Note:**
- Campaign CRUD operations
- Contact list import/export logic
- Call flow automation structure
- Campaign scheduling patterns
- Performance metrics collection

**Implement Using:**
- FastAPI routers (replace Fastify)
- SQLAlchemy models (replace Prisma)
- Existing circuit breaker for resilience
- Prometheus metrics for monitoring
- Structured logging for audit trail

---

### 2. Team Management
**Reference Files:**
- Backend: `_cc-lite-reference/backend/app/routers/teams.py`
- Frontend: `_cc-lite-reference/frontend/src/routes/teams/`
- Models: `_cc-lite-reference/backend/app/models/team.py`

**Key Patterns to Note:**
- Team hierarchy structure
- Agent assignment logic
- Role-based access control
- Team performance metrics

**Implement Using:**
- Existing authentication patterns (Ed25519 JWT)
- Role-based permissions (enhance existing auth)
- WebSocket for real-time updates (already built!)
- Prometheus metrics for team stats

---

### 3. Supervisor Cockpit
**Reference Files:**
- Frontend: `_cc-lite-reference/frontend/src/routes/supervisor/`
- Backend: `_cc-lite-reference/backend/app/routers/supervisors.py`

**Key Patterns to Note:**
- Real-time call monitoring UI
- Agent status tracking
- Queue management interface
- Performance dashboards

**Implement Using:**
- **HUGE ADVANTAGE**: WebSocket streaming already built!
- Real-time updates via existing WebSocket infrastructure
- SvelteKit 2.0 reactive stores
- Existing monitoring infrastructure (18 Prometheus metrics)

---

### 4. Analytics & Reporting
**Reference Files:**
- Backend: `_cc-lite-reference/backend/app/routers/analytics.py`
- Frontend: `_cc-lite-reference/frontend/src/routes/analytics/`
- Services: `_cc-lite-reference/backend/app/services/analytics.py`

**Key Patterns to Note:**
- Metrics aggregation logic
- Report generation patterns (CSV, PDF)
- Data visualization structure
- Historical trend analysis

**Implement Using:**
- **HUGE ADVANTAGE**: 18 Prometheus metrics already collecting data!
- Extend existing metrics for campaign/team-specific tracking
- Use structured logs for audit trails (already built!)
- Add export service for CSV/PDF generation

---

### 5. Multi-Language (i18n)
**Reference Files:**
- Frontend: `_cc-lite-reference/frontend/src/lib/i18n/`
- Translations: `_cc-lite-reference/frontend/src/lib/i18n/locales/`

**Key Patterns to Note:**
- i18n file structure (EN/ES/CS)
- Translation key organization
- Language switcher UI
- Language detection logic

**Implement Using:**
- SvelteKit 2.0 i18n library (svelte-intl or sveltekit-i18n)
- Modern i18n best practices
- Language persistence (localStorage)
- Dynamic language switching

---

## 🔍 Code Quality Comparison

### Old Voice by Kraliki (Reference)
| Metric | Value | Status |
|--------|-------|--------|
| Production Score | 59% | ⚠️ Low |
| Failing Tests | 10 errors | ❌ Issues |
| Backend | Fastify + TypeScript | 🔄 Migration incomplete |
| ORM | Prisma | 🔄 Being replaced |
| API | tRPC | 🔄 Being replaced |
| Coverage | 59% | ⚠️ Low |

### Voice by Kraliki (Target)
| Metric | Value | Status |
|--------|-------|--------|
| Production Score | 90/100 | ✅ Excellent |
| Failing Tests | 0 | ✅ Perfect |
| Backend | FastAPI + Python | ✅ Complete |
| ORM | SQLAlchemy | ✅ Complete |
| API | FastAPI REST | ✅ Complete |
| Coverage | 60+ tests | ✅ Good |

**Lesson:** Don't copy code quality issues. Implement fresh with better patterns!

---

## 🎓 Learning from Reference Code

### What to Learn:
1. **Feature Requirements** - What the feature needs to do
2. **Business Logic** - How the feature works conceptually
3. **Data Models** - What entities and relationships exist
4. **API Patterns** - What endpoints are needed
5. **UI/UX Flow** - How users interact with features
6. **Validation Rules** - What constraints are enforced

### What NOT to Copy:
1. ❌ **Outdated Patterns** - Fastify, tRPC, Prisma (we use FastAPI, SQLAlchemy)
2. ❌ **Code Quality Issues** - Low test coverage, failing tests
3. ❌ **Migration Debt** - Incomplete TypeScript→Python migration
4. ❌ **Missing Infrastructure** - No circuit breaker, auto-reconnection
5. ❌ **Weak Monitoring** - Limited metrics vs our 18 Prometheus metrics

---

## 📊 Feature Implementation Checklist

When implementing a feature from this reference:

### Planning Phase
- [ ] Read reference code thoroughly
- [ ] Document requirements (API, models, business logic)
- [ ] Note UI/UX patterns
- [ ] Identify validation rules
- [ ] Check for external dependencies

### Design Phase
- [ ] Design SQLAlchemy models (NOT Prisma)
- [ ] Create Pydantic schemas (validation)
- [ ] Plan FastAPI routes (NOT Fastify/tRPC)
- [ ] Design service layer (business logic)
- [ ] Plan SvelteKit 2.0 UI (latest patterns)

### Implementation Phase
- [ ] Implement using cc-lite-2026 patterns
- [ ] Leverage existing infrastructure:
  - [ ] Circuit breaker for external calls
  - [ ] Prometheus metrics for monitoring
  - [ ] Structured logging for events
  - [ ] Auto-reconnection for resilience
  - [ ] WebSocket for real-time (if needed)
- [ ] Follow Stack 2026 standards
- [ ] Maintain code quality (90+ score)

### Testing Phase
- [ ] Write unit tests (pytest)
- [ ] Write integration tests (pytest)
- [ ] Write E2E tests (Playwright)
- [ ] Verify production score maintained (90+)
- [ ] Zero failing tests (strict requirement)

### Documentation Phase
- [ ] Update API documentation
- [ ] Add code comments
- [ ] Update FEATURE_ROADMAP.md progress
- [ ] Document any deviations from reference

---

## 🚀 Quick Reference Commands

### Read Reference Code
```bash
# Backend reference
cat _cc-lite-reference/backend/app/routers/campaigns.py
cat _cc-lite-reference/backend/app/models/campaign.py

# Frontend reference
cat _cc-lite-reference/frontend/src/routes/campaigns/+page.svelte
cat _cc-lite-reference/frontend/src/lib/components/CampaignList.svelte

# Tests reference
cat _cc-lite-reference/backend/tests/test_campaigns.py
cat _cc-lite-reference/frontend/tests/campaigns.spec.ts
```

### Compare Patterns
```bash
# Old pattern (reference)
cat _cc-lite-reference/backend/app/routers/campaigns.py

# New pattern (implement here)
cat backend/app/campaigns/routes.py
```

### Search for Patterns
```bash
# Find all campaign-related files
find _cc-lite-reference -name "*campaign*" -type f

# Search for specific patterns
grep -r "campaign.create" _cc-lite-reference/backend/
grep -r "CampaignList" _cc-lite-reference/frontend/
```

---

## 📝 Implementation Examples

### Example 1: Campaign Data Model

**Reference (OLD - Prisma):**
```typescript
// _cc-lite-reference/backend/app/models/campaign.ts
model Campaign {
  id          String   @id @default(cuid())
  name        String
  status      String
  createdAt   DateTime @default(now())
  updatedAt   DateTime @updatedAt
  contacts    Contact[]
}
```

**Implementation (NEW - SQLAlchemy):**
```python
# backend/app/campaigns/models.py
from sqlalchemy import Column, String, DateTime, Enum
from sqlalchemy.orm import relationship
from app.core.database import Base
from datetime import datetime
import uuid

class Campaign(Base):
    __tablename__ = "campaigns"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, nullable=False, index=True)
    status = Column(Enum("draft", "active", "paused", "completed"), default="draft")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    contacts = relationship("Contact", back_populates="campaign", cascade="all, delete-orphan")
```

---

### Example 2: Campaign API Endpoint

**Reference (OLD - Fastify + tRPC):**
```typescript
// _cc-lite-reference/backend/app/routers/campaigns.ts
router.post('/campaigns', async (request, reply) => {
  const campaign = await prisma.campaign.create({
    data: request.body
  });
  return campaign;
});
```

**Implementation (NEW - FastAPI):**
```python
# backend/app/campaigns/routes.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.campaigns.schemas import CampaignCreate, CampaignResponse
from app.campaigns.service import CampaignService
from app.core.patterns.circuit_breaker import circuit_breaker
from app.core.logging import get_logger

router = APIRouter(prefix="/api/campaigns", tags=["campaigns"])
logger = get_logger(__name__)

@router.post("/", response_model=CampaignResponse, status_code=201)
@circuit_breaker(failure_threshold=5, timeout=60)
async def create_campaign(
    campaign: CampaignCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Create a new campaign with circuit breaker protection.

    - **name**: Campaign name (required)
    - **description**: Campaign description
    - **status**: Campaign status (draft, active, paused)
    """
    logger.info(
        "Creating campaign",
        extra={
            "user_id": current_user.id,
            "campaign_name": campaign.name
        }
    )

    try:
        service = CampaignService(db)
        result = await service.create(campaign, current_user.id)

        logger.info(
            "Campaign created successfully",
            extra={"campaign_id": result.id}
        )

        return result

    except Exception as e:
        logger.error(
            "Failed to create campaign",
            extra={"error": str(e)},
            exc_info=True
        )
        raise HTTPException(status_code=500, detail="Failed to create campaign")
```

**Improvements Over Reference:**
- ✅ Circuit breaker for resilience
- ✅ Structured logging with correlation
- ✅ Proper error handling
- ✅ Authentication integration
- ✅ OpenAPI documentation
- ✅ Pydantic validation

---

## 🎯 Success Metrics

### When Using This Reference:

**Quality Maintained:**
- Production score: 90+ (never decrease)
- Tests passing: 100% (zero failures)
- Code coverage: Increase with each feature

**Implementation Speed:**
- Understand requirements: 1 day
- Implement fresh: 3-5 days
- Test thoroughly: 2 days
- **Total per feature: 6-8 days**

**Code Quality:**
- Follow existing patterns (FastAPI, SQLAlchemy, SvelteKit 2.0)
- Leverage infrastructure (circuit breaker, metrics, logging)
- Modern best practices (Stack 2026)
- Zero technical debt

---

## 📖 Additional Resources

**Main Documentation:**
- [PROMOTION_PLAN.md](../PROMOTION_PLAN.md) - Overall promotion strategy
- [FEATURE_ROADMAP.md](../FEATURE_ROADMAP.md) - Implementation timeline
- [README.md](../README.md) - Project overview

**Implementation Guides:**
- [IMPLEMENTATION_COMPLETE.md](../IMPLEMENTATION_COMPLETE.md) - Technical details
- Backend patterns: `backend/app/` (existing code)
- Frontend patterns: `frontend/src/` (existing code)

**Testing:**
- Backend tests: `backend/tests/`
- E2E tests: `tests/` (Playwright)

---

## ⚠️ Final Reminder

**THIS IS A REFERENCE, NOT SOURCE CODE TO COPY**

- ✅ Read for understanding
- ✅ Learn patterns and requirements
- ✅ Get inspired by UI/UX
- ❌ Never copy/paste code
- ❌ Never merge files
- ❌ Never use outdated patterns

**Quality First:**
Maintain 90+ production score. Implement fresh using cc-lite-2026 patterns.

---

**Last Updated:** November 10, 2025
**Status:** READ-ONLY REFERENCE
**Use With:** [PROMOTION_PLAN.md](../PROMOTION_PLAN.md) + [FEATURE_ROADMAP.md](../FEATURE_ROADMAP.md)
