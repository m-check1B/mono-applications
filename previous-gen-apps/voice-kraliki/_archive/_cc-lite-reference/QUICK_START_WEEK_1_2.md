# Quick Start Guide - Week 1-2 Implementation

**Voice by Kraliki Production Roadmap - Week 1-2 Critical Tasks**

---

## 🚀 Quick Start

### 1. Install Dependencies

```bash
cd /home/adminmatej/github/applications/cc-lite/backend
pip install -r requirements.txt
```

### 2. Start Backend (Python FastAPI)

```bash
# Development mode (port 3018)
uvicorn app.main:app --reload --host 127.0.0.1 --port 3018

# Or use the package manager
cd /home/adminmatej/github/applications/cc-lite
pnpm dev:backend
```

**Access**:
- API Docs: http://127.0.0.1:3018/docs
- ReDoc: http://127.0.0.1:3018/redoc
- Health Check: http://127.0.0.1:3018/health

### 3. Optional: Start RabbitMQ (for events)

```bash
# Using Docker
docker run -d \
  --name cc-lite-rabbitmq \
  -p 5672:5672 \
  -p 15672:15672 \
  rabbitmq:3-management

# Access management UI: http://localhost:15672
# Username: guest
# Password: guest
```

---

## 🔑 Ed25519 JWT Authentication

### First Run
On first startup, Ed25519 keys are **automatically generated**:
```
⚠️  SECURITY: Back up these keys securely!
    Private: backend/.keys/ed25519_private.pem
    Public:  backend/.keys/ed25519_public.pem
```

### Test Authentication

```python
from app.core.security import jwt_manager

# Create token
token = jwt_manager.create_access_token({
    "sub": "user_123",
    "email": "user@example.com",
    "role": "admin"
})

# Verify token
payload = jwt_manager.verify_token(token)
print(payload["sub"])  # user_123
```

### Using in API Requests

```bash
# 1. Register user
curl -X POST http://localhost:3018/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "SecurePass123!",
    "username": "testuser",
    "first_name": "Test",
    "last_name": "User",
    "role": "AGENT"
  }'

# 2. Login
curl -X POST http://localhost:3018/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "SecurePass123!"
  }'

# Response includes Ed25519-signed tokens:
{
  "access_token": "eyJhbGciOiJFZERTQSIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJFZERTQSIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user": {...}
}

# 3. Use token
curl http://localhost:3018/api/auth/me \
  -H "Authorization: Bearer <access_token>"
```

---

## 📤 Event Publishing

### Configuration

```bash
# .env
ENABLE_EVENTS=true
RABBITMQ_URL=amqp://guest:guest@localhost:5672/
```

### Publish Events

```python
from app.core.events import event_publisher

# In your route handler
@router.post("/calls/{call_id}/end")
async def end_call(call_id: str, current_user: User):
    # ... end the call ...

    # Publish event for other modules
    await event_publisher.publish_call_ended(
        call_id=call.id,
        duration=call.duration,
        outcome=call.outcome,
        transcript=call.transcript,
        organization_id=current_user.organization_id,
        user_id=current_user.id
    )

    return call
```

### Available Event Types

1. **call.started** - New call initiated
2. **call.ended** - Call completed (triggers Planning module workflows)
3. **call.transcribed** - Real-time transcript ready
4. **campaign.completed** - Campaign finished
5. **sentiment.analyzed** - Negative sentiment detected (alerts)

---

## 🔌 Platform Integration

### Import in Ocelot Platform

```python
# ocelot-platform/core/backend/gateway/router.py
from ocelot_apps.cc_lite.backend.app.module import CommsModule

# Create module in platform mode
comms = CommsModule(
    event_publisher=platform_event_publisher,
    platform_mode=True  # Trust API Gateway headers
)

# Mount at platform route
app.mount("/api/communications", comms.get_app())
```

### Platform Mode vs Standalone

**Standalone Mode** (default):
- Uses Ed25519 JWT authentication
- Runs on port 3018
- Full auth flow (register, login, refresh)

**Platform Mode**:
- Trusts API Gateway headers (X-User-Id, X-Org-Id, X-User-Role)
- No JWT verification (already done by gateway)
- Mounted as submodule

---

## 🧪 Testing

### Run Integration Tests

```bash
cd /home/adminmatej/github/applications/cc-lite/backend

# Event publishing tests (mocked RabbitMQ)
pytest tests/integration/test_event_publishing.py -v

# All tests
pytest tests/ -v

# With coverage
pytest tests/ --cov=app --cov-report=html
```

### Test Ed25519 JWT Manually

```bash
cd backend
python3 -c "
from app.core.security import jwt_manager
token = jwt_manager.create_access_token({'sub': 'test', 'email': 'test@example.com'})
print('Token:', token)
payload = jwt_manager.verify_token(token)
print('Verified:', payload)
"
```

---

## 📦 NPM Package

### Export Structure

```json
{
  "name": "@ocelot-apps/cc-lite",
  "exports": {
    ".": "./backend/app/module.py",
    "./events": "./backend/app/core/events.py",
    "./security": "./backend/app/core/security.py",
    "./components": "./frontend/src/lib/components/index.ts"
  }
}
```

### Install in Another Project

```bash
# From npm registry (when published)
npm install @ocelot-apps/cc-lite

# From local path (development)
npm install /home/adminmatej/github/applications/cc-lite
```

---

## 🛠️ Development Workflow

### 1. Start Development Environment

```bash
# Terminal 1: Backend
cd /home/adminmatej/github/applications/cc-lite
pnpm dev:backend

# Terminal 2: Frontend (SvelteKit)
pnpm dev:frontend

# Terminal 3: RabbitMQ (optional)
docker run -d -p 5672:5672 -p 15672:15672 rabbitmq:3-management
```

### 2. Make Changes

- **Backend**: Edit files in `backend/app/`
- **Auto-reload**: Uvicorn watches for changes
- **Tests**: Run `pytest` after changes

### 3. Check API Docs

Visit http://localhost:3018/docs for interactive API documentation (auto-generated by FastAPI)

---

## 🔒 Security Best Practices

### DO ✅

- ✅ Back up Ed25519 keys (`backend/.keys/*.pem`)
- ✅ Use environment variables for secrets
- ✅ Never commit `.keys/` directory
- ✅ Rotate keys every 90 days (production)
- ✅ Use HTTPS in production

### DON'T ❌

- ❌ Commit private keys to git
- ❌ Share keys in documentation
- ❌ Use same keys across environments
- ❌ Skip token verification
- ❌ Disable event publishing in production

---

## 📊 Monitoring

### Health Check

```bash
curl http://localhost:3018/health

# Response:
{
  "status": "healthy",
  "database": "connected",
  "services": {
    "telephony": "ready",
    "ai": "ready"
  }
}
```

### Event Bus Status

Check RabbitMQ management UI: http://localhost:15672
- Queues: Monitor message counts
- Exchanges: Verify `ocelot.events` topic exchange
- Connections: Check Voice by Kraliki connection

---

## 🐛 Troubleshooting

### Issue: "ModuleNotFoundError: No module named 'cryptography'"

```bash
pip install -r backend/requirements.txt
```

### Issue: "Failed to connect to RabbitMQ"

```bash
# Check RabbitMQ is running
docker ps | grep rabbitmq

# Start RabbitMQ if not running
docker run -d -p 5672:5672 -p 15672:15672 rabbitmq:3-management

# Or disable events temporarily
export ENABLE_EVENTS=false
```

### Issue: "Invalid token" errors

- Check Ed25519 keys exist: `ls backend/.keys/`
- Regenerate keys: `rm -rf backend/.keys/` (keys regenerate on startup)
- Verify token algorithm is `EdDSA` (not `HS256`)

### Issue: Port 3018 already in use

```bash
# Find process using port
lsof -i :3018

# Kill process
kill -9 <PID>

# Or use different port
uvicorn app.main:app --port 3019
```

---

## 📚 Documentation

- **Implementation Report**: `/home/adminmatej/github/applications/cc-lite/WEEK_1_2_IMPLEMENTATION_REPORT.md`
- **Roadmap**: `/home/adminmatej/github/ocelot-platform/audits/CC-LITE_PRODUCTION_ROADMAP_V2.md`
- **Security Docs**: `/home/adminmatej/github/ocelot-platform/docs/SECURITY.md`
- **API Docs**: http://localhost:3018/docs (when running)

---

## 🎯 Next Steps

1. **Complete API Migration**: Port remaining TypeScript routes to Python
2. **Database Migrations**: Set up Alembic for schema changes
3. **Mobile-First UI**: Implement PWA design system (separate agent)
4. **i18n**: Add Czech + English translations (separate agent)
5. **Production Deploy**: Docker + PM2 on Hetzner VM

---

**Status**: ✅ Week 1-2 Critical Tasks Complete
**Last Updated**: October 5, 2025
