# Quick Start Guide - CC-Lite 2026 Development

**Get productive in 15 minutes or less!**

---

**Headless note (2025-12-29):** Voice by Kraliki now runs as a backend-only service. The legacy `frontend/` folder is kept for reference; current UIs live under `/applications/*-template`. Use backend-only steps unless you are working on template UI.

---

## 🚀 Prerequisites Check

```bash
# Check your environment (run these commands)
docker --version          # Need: 20.10+
docker compose version    # Need: 2.0+
node --version           # Need: 20+
python --version         # Need: 3.11+
git --version            # Need: 2.30+
```

---

## ⚡ Option 1: Docker Quick Start (Recommended)

### Step 1: Clone and Setup (2 minutes)
```bash
# Clone the repository
git clone git@github.com:m-check1B/cc-lite-2026.git
cd cc-lite-2026

# Switch to develop branch
git checkout develop

# Environment is pre-configured with test API keys!
ls -la .env  # Already has test credentials
```

### Step 2: Start Everything (3 minutes)
```bash
# Start all services with one command
docker compose -f docker-compose.prod.yml up -d

# Wait for services to be healthy
docker compose -f docker-compose.prod.yml ps

# Check logs if needed
docker compose -f docker-compose.prod.yml logs -f backend
```

### Step 3: Access the Application (instant)
```
🌐 Frontend:    http://localhost:3000
📡 Backend API: http://localhost:8000
📚 API Docs:    http://localhost:8000/docs
🗄️ Database:    PostgreSQL on :5432
💾 Cache:       Redis on :6379
```

### Step 4: Test Login
```
Email: testuser@example.com
Password: test123
```

---

## 💻 Option 2: Local Development Quick Start

### Backend Setup (5 minutes)
```bash
# Navigate to backend
cd backend

# Install uv if you don't have it
pip install uv

# Install dependencies
uv sync

# Run development server
uv run uvicorn app.main:app --reload --port 8000

# Backend is now running at http://localhost:8000
```

### Frontend Setup (5 minutes)
```bash
# New terminal - navigate to frontend
cd frontend

# Install pnpm if you don't have it
npm install -g pnpm

# Install dependencies
pnpm install

# Run development server
pnpm dev

# Frontend is now running at http://localhost:3000
```

### Database Setup (3 minutes)
```bash
# Start only the database services
docker compose -f docker-compose.prod.yml up -d postgres redis qdrant

# Or use your local PostgreSQL and update .env
DATABASE_URL=postgresql://postgres:password@localhost:5432/cc_lite_2026
```

---

## 🎯 Start Developing Features

### Quick Feature Addition Template

#### 1. Backend: Add New API Endpoint (5 minutes)
```python
# backend/app/features/my_feature/router.py
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db

router = APIRouter(prefix="/my-feature", tags=["My Feature"])

@router.get("/items")
async def get_items(db: AsyncSession = Depends(get_db)):
    return {"items": ["item1", "item2"]}

# Add to backend/app/main.py
from app.features.my_feature import router as my_feature_router
app.include_router(my_feature_router, prefix="/api/v1")
```

#### 2. Frontend: Add New Page (5 minutes)
```svelte
<!-- frontend/src/routes/my-feature/+page.svelte -->
<script lang="ts">
  import { onMount } from 'svelte';

  let items = [];

  onMount(async () => {
    const response = await fetch('/api/v1/my-feature/items');
    items = await response.json();
  });
</script>

<div class="container mx-auto p-4">
  <h1 class="text-2xl font-bold mb-4">My Feature</h1>
  {#each items as item}
    <div class="p-2 border rounded mb-2">{item}</div>
  {/each}
</div>
```

#### 3. Test Your Feature
```bash
# Test backend endpoint
curl http://localhost:8000/api/v1/my-feature/items

# Visit frontend page
open http://localhost:3000/my-feature
```

---

## 🛠️ Common Development Tasks

### Add a Database Model
```python
# backend/app/models/my_model.py
from sqlalchemy import Column, String, UUID
from app.database import Base
import uuid

class MyModel(Base):
    __tablename__ = "my_table"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)

# Create migration
alembic revision --autogenerate -m "Add my_table"
alembic upgrade head
```

### Add a WebSocket Handler
```python
# backend/app/websocket/my_handler.py
from fastapi import WebSocket

async def my_websocket_handler(websocket: WebSocket):
    await websocket.accept()
    await websocket.send_json({"message": "Connected"})

    while True:
        data = await websocket.receive_json()
        await websocket.send_json({"echo": data})
```

### Add a Frontend Component
```svelte
<!-- frontend/src/lib/components/MyComponent.svelte -->
<script lang="ts">
  export let title: string;
  export let value: number = 0;
</script>

<div class="card p-4 shadow-md">
  <h3 class="text-lg font-semibold">{title}</h3>
  <p class="text-2xl">{value}</p>
</div>

<!-- Use in any page -->
<script>
  import MyComponent from '$lib/components/MyComponent.svelte';
</script>

<MyComponent title="Active Calls" value={42} />
```

---

## 📁 Project Structure Quick Reference

```
cc-lite-2026/
├── backend/
│   ├── app/
│   │   ├── main.py           # FastAPI app entry
│   │   ├── auth/             # Authentication (Ed25519 JWT)
│   │   ├── models/           # SQLAlchemy models
│   │   ├── schemas/          # Pydantic schemas
│   │   ├── services/         # Business logic
│   │   ├── api/              # API routes
│   │   └── websocket/        # WebSocket handlers
│   └── tests/                # Backend tests
│
├── frontend/
│   ├── src/
│   │   ├── routes/           # SvelteKit pages
│   │   ├── lib/
│   │   │   ├── api/         # API client
│   │   │   ├── components/  # Reusable components
│   │   │   └── stores/      # Svelte stores
│   │   └── app.html         # HTML template
│   └── tests/               # Frontend tests
│
├── docker-compose.prod.yml   # Production stack
├── .env                     # Environment (pre-configured!)
└── docs/                    # Documentation
```

---

## 🔥 Hot Reload Development

Both backend and frontend support hot reload:

### Backend Hot Reload
```python
# Changes to Python files auto-reload with uvicorn --reload
# Just save your file and the server restarts!
```

### Frontend Hot Reload
```typescript
// Vite provides instant HMR (Hot Module Replacement)
// Changes appear immediately in the browser!
```

---

## 🧪 Quick Testing

### Run Backend Tests
```bash
cd backend
uv run pytest tests/ -v

# Run specific test
uv run pytest tests/test_auth.py -v

# With coverage
uv run pytest --cov=app tests/
```

### Run Frontend Tests
```bash
cd frontend
pnpm test

# Run in watch mode
pnpm test:watch
```

### Manual API Testing
```bash
# Use the interactive API docs
open http://localhost:8000/docs

# Or use curl
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"testuser@example.com","password":"test123"}'
```

---

## 🐛 Quick Debugging

### Check Service Status
```bash
# Docker services
docker compose -f docker-compose.prod.yml ps

# Logs
docker compose -f docker-compose.prod.yml logs backend
docker compose -f docker-compose.prod.yml logs frontend

# Database connection
docker exec -it cc-lite-postgres psql -U postgres -d cc_lite_2026 -c "SELECT 1;"
```

### Common Issues & Fixes

**Port Already in Use**
```bash
# Find and kill process on port
lsof -i :8000  # or :3000
kill -9 <PID>
```

**Database Connection Failed**
```bash
# Ensure PostgreSQL is running
docker compose -f docker-compose.prod.yml up -d postgres

# Check connection string in .env
cat .env | grep DATABASE_URL
```

**Module Import Errors**
```bash
# Backend: Reinstall dependencies
cd backend && uv sync

# Frontend: Clear cache and reinstall
cd frontend && rm -rf node_modules && pnpm install
```

---

## 🎯 Week 1: Campaign Management Quick Start

Ready to implement the first feature? Here's your checklist:

### 1. Create Campaign Model (10 minutes)
```bash
# Copy from TECHNICAL_IMPLEMENTATION_GUIDE.md
# Location: backend/app/models/campaign.py
```

### 2. Add Campaign API (15 minutes)
```bash
# Copy from TECHNICAL_IMPLEMENTATION_GUIDE.md
# Location: backend/app/api/v1/campaigns.py
```

### 3. Create Campaign UI (20 minutes)
```bash
# Copy from TECHNICAL_IMPLEMENTATION_GUIDE.md
# Location: frontend/src/routes/campaigns/+page.svelte
```

### 4. Test Everything
```bash
# Create a campaign via API
curl -X POST http://localhost:8000/api/v1/campaigns \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{"name":"Test Campaign","type":"outbound"}'

# View in UI
open http://localhost:3000/campaigns
```

---

## 📚 Essential Commands Cheat Sheet

```bash
# Docker Operations
docker compose -f docker-compose.prod.yml up -d      # Start all
docker compose -f docker-compose.prod.yml down       # Stop all
docker compose -f docker-compose.prod.yml restart    # Restart
docker compose -f docker-compose.prod.yml logs -f    # View logs

# Git Workflow
git checkout develop                    # Switch to develop
git pull origin develop                 # Get latest
git checkout -b feature/my-feature     # New feature branch
git add . && git commit -m "feat: add" # Commit
git push origin feature/my-feature     # Push branch

# Database Operations
docker exec -it cc-lite-postgres psql -U postgres -d cc_lite_2026
\dt                                     # List tables
SELECT * FROM users;                    # Query data
\q                                      # Exit

# Quick Monitoring
curl http://localhost:8000/health      # Backend health
curl http://localhost:3000/api/health  # Frontend health
```

---

## 🚢 Deploy to Production

```bash
# Quick production deployment
./scripts/deploy.sh production

# Or manual steps
docker compose -f docker-compose.prod.yml build
docker compose -f docker-compose.prod.yml up -d
```

---

## 💡 Pro Tips

1. **Use API Docs**: http://localhost:8000/docs for testing endpoints
2. **Watch Logs**: Keep `docker compose logs -f` running in a terminal
3. **Database GUI**: Use TablePlus/DBeaver to connect to PostgreSQL
4. **VS Code Extensions**: Install Python, Svelte, and Prettier extensions
5. **Git Hooks**: Run `./scripts/setup-hooks.sh` for pre-commit checks

---

## 🆘 Getting Help

- **Documentation**: See `/docs` folder
- **API Reference**: http://localhost:8000/docs
- **Planning Docs**:
  - [APP_EXPANSION_PLAN.md](./APP_EXPANSION_PLAN.md)
  - [TECHNICAL_IMPLEMENTATION_GUIDE.md](./TECHNICAL_IMPLEMENTATION_GUIDE.md)
  - [FEATURE_DEPENDENCIES.md](./FEATURE_DEPENDENCIES.md)

---

**You're ready to build! 🚀** Start with Week 1 Campaign Management features.
