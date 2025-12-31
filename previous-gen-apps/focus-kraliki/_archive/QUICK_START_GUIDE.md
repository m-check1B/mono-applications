# Focus Lite - Quick Start Developer Guide

**Get up and running in 5 minutes!**

---

## 🚀 Prerequisites

Ensure you have the following installed:
- **Node.js 18+** and **pnpm 8+**
- **Python 3.11+** and **uv** (Python package manager)
- **PostgreSQL 15+** or **Docker**
- **Redis 7+** or **Docker**

---

## 📦 One-Command Setup

```bash
# Clone and setup everything
git clone https://github.com/your-org/focus-lite.git
cd focus-lite
./scripts/setup.sh

# Start everything
./scripts/start.sh
```

Visit: **http://localhost:5175** 🎉

---

## 🛠️ Manual Setup (Step by Step)

### 1️⃣ Database Setup

```bash
# Using Docker (Recommended)
docker run --name focuslite-db \
  -e POSTGRES_USER=postgres \
  -e POSTGRES_PASSWORD=password \
  -e POSTGRES_DB=focuslite \
  -p 5432:5432 \
  -d postgres:15

# Redis for caching
docker run --name focuslite-redis \
  -p 6379:6379 \
  -d redis:7-alpine
```

### 2️⃣ Backend Setup

```bash
# Navigate to backend
cd backend

# Create virtual environment with uv
uv venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
uv pip install -r requirements.txt

# Setup environment
cp .env.example .env
# Edit .env with your API keys

# Run database migrations
alembic upgrade head

# Start backend server
uvicorn app.main:app --reload --host 127.0.0.1 --port 3018
```

Backend API: **http://127.0.0.1:3018/docs** (Swagger UI)

### 3️⃣ Frontend Setup

```bash
# In a new terminal
cd frontend

# Install dependencies
pnpm install

# Setup environment
cp .env.example .env

# Start dev server
pnpm dev -- --host 127.0.0.1 --port 5175
```

Frontend: **http://localhost:5175**

---

## 🔑 Environment Variables

### Backend (.env)
```env
# Database
DATABASE_URL=postgresql://postgres:password@localhost:5432/focuslite

# Redis
REDIS_URL=redis://localhost:6379/0

# JWT (Ed25519)
JWT_PRIVATE_KEY_PATH=./keys/jwt_private.pem
JWT_PUBLIC_KEY_PATH=./keys/jwt_public.pem

# AI Services
ANTHROPIC_API_KEY=your_claude_key
OPENAI_API_KEY=your_openai_key
DEEPGRAM_API_KEY=your_deepgram_key

# Google OAuth (optional)
GOOGLE_CLIENT_ID=your_client_id
GOOGLE_CLIENT_SECRET=your_client_secret

# Security
JWT_SECRET=your-secret-key-min-32-chars
```

### Frontend (.env)
```env
PUBLIC_API_URL=http://127.0.0.1:3018
PUBLIC_WS_URL=ws://127.0.0.1:3018/ws
```

---

## 🧪 Running Tests

```bash
# Backend tests
cd backend
uv run pytest tests/ -v --cov=app

# Frontend tests
cd frontend
pnpm test
pnpm test:e2e

# Full test suite
./scripts/test.sh
```

---

## 📝 Development Workflow

### 1. Create Feature Branch
```bash
git checkout -b feature/your-feature-name
```

### 2. Backend Development
```bash
cd backend

# Create new router
touch app/routers/your_feature.py

# Create models
touch app/models/your_model.py

# Create migration
alembic revision --autogenerate -m "Add your feature"
alembic upgrade head

# Test your changes
uv run pytest tests/ -v
```

### 3. Frontend Development
```bash
cd frontend

# Create new route
mkdir src/routes/your-feature
touch src/routes/your-feature/+page.svelte

# Create components
touch src/lib/components/YourComponent.svelte

# Create stores
touch src/lib/stores/yourStore.ts

# Type check
pnpm check

# Test
pnpm test
```

### 4. Commit & Push
```bash
git add .
git commit -m "feat: add your feature"
git push origin feature/your-feature-name
```

---

## 🏗️ Project Structure

```
focus-lite/
├── backend/          # FastAPI backend
│   ├── app/         # Application code
│   │   ├── core/    # Core functionality
│   │   ├── models/  # Database models
│   │   ├── routers/ # API endpoints
│   │   └── services/# Business logic
│   └── tests/       # Backend tests
│
├── frontend/        # SvelteKit frontend
│   ├── src/         # Source code
│   │   ├── lib/     # Shared code
│   │   ├── routes/  # Pages
│   │   └── app.css  # Global styles
│   └── tests/       # Frontend tests
│
├── docs/            # Documentation
├── scripts/         # Utility scripts
└── infra/           # Deployment configs
```

---

## 🔥 Common Commands

### Backend
```bash
# Start server
uvicorn app.main:app --reload

# Create migration
alembic revision --autogenerate -m "Description"

# Apply migrations
alembic upgrade head

# Run tests
uv run pytest tests/ -v

# Format code
black app/ tests/

# Lint
ruff app/ tests/
```

### Frontend
```bash
# Dev server
pnpm dev

# Build
pnpm build

# Preview build
pnpm preview

# Type check
pnpm check

# Format
pnpm format

# Lint
pnpm lint
```

---

## 🐛 Debugging

### Backend Debugging
```python
# Add breakpoints
import pdb; pdb.set_trace()

# Or use VS Code debugger with launch.json:
{
  "name": "FastAPI",
  "type": "python",
  "request": "launch",
  "module": "uvicorn",
  "args": ["app.main:app", "--reload"],
  "jinja": true
}
```

### Frontend Debugging
```javascript
// Use browser DevTools
console.log('Debug:', variable);

// Or VS Code debugger
debugger;

// SvelteKit specific
import { dev } from '$app/environment';
if (dev) console.log('Dev only log');
```

---

## 📚 Key Files to Know

### Backend
- `app/main.py` - FastAPI app entry point
- `app/core/config.py` - Configuration
- `app/core/database.py` - Database setup
- `app/routers/` - API endpoints
- `app/models/` - SQLAlchemy models

### Frontend
- `src/routes/+layout.svelte` - Root layout
- `src/lib/api/client.ts` - API client
- `src/lib/stores/` - Svelte stores
- `src/app.css` - Global styles
- `vite.config.ts` - Build config

---

## 🚢 Production Build

```bash
# Build everything
./scripts/build.sh

# Or manually:

# Backend
cd backend
pip install -r requirements.txt

# Frontend
cd frontend
pnpm build

# Docker
docker-compose up --build
```

---

## 🆘 Getting Help

### Documentation
- **API Docs**: http://127.0.0.1:3018/docs
- **Project Docs**: `/docs/README.md`
- **Architecture**: `/docs/ARCHITECTURE.md`

### Troubleshooting

**Database connection issues?**
```bash
# Check PostgreSQL is running
pg_isready -h localhost -p 5432

# Check Redis
redis-cli ping
```

**Port already in use?**
```bash
# Kill process on port
lsof -ti:3018 | xargs kill -9  # Backend
lsof -ti:5175 | xargs kill -9  # Frontend
```

**Dependencies issues?**
```bash
# Backend - reinstall
cd backend
rm -rf .venv
uv venv .venv
source .venv/bin/activate
uv pip install -r requirements.txt

# Frontend - reinstall
cd frontend
rm -rf node_modules pnpm-lock.yaml
pnpm install
```

---

## 🎯 Next Steps

1. **Read the documentation**
   - [Architecture Guide](./docs/ARCHITECTURE.md)
   - [Backend Guide](./docs/BACKEND.md)
   - [Frontend Guide](./docs/FRONTEND.md)

2. **Explore the codebase**
   - Check existing routers in `backend/app/routers/`
   - Look at components in `frontend/src/lib/components/`
   - Review stores in `frontend/src/lib/stores/`

3. **Start implementing!**
   - Check tasks in [docs/CLAUDE.md](./docs/CLAUDE.md) for current development priorities
   - Follow the phase guides in `/docs/implementation/`
   - Run tests frequently

---

## 🎉 You're Ready!

Start the servers and begin coding:

```bash
# Terminal 1 - Backend
cd backend && uvicorn app.main:app --reload

# Terminal 2 - Frontend
cd frontend && pnpm dev

# Terminal 3 - Your code editor
code .
```

**Happy coding!** 🚀

---

**Questions?** Check the [docs](./docs) or open an issue!

**Last Updated**: November 10, 2025
**Version**: 2.1.0