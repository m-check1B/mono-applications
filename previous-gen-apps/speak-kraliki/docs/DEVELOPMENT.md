# Development Guide

## Prerequisites

- Python 3.13+
- Node.js 22+
- PostgreSQL 17+
- Docker (optional)

## Quick Start

### 1. Clone Repository

```bash
git clone https://github.com/yourorg/speak-kraliki.git
cd speak-kraliki
```

### 2. Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# .venv\Scripts\activate   # Windows

# Install dependencies
pip install -r requirements.txt

# Copy environment file
cp .env.example .env
# Edit .env with your values
```

### 3. Database Setup

```bash
# Using Docker
docker run -d --name speak-kraliki-db \
    -e POSTGRES_USER=vop \
    -e POSTGRES_PASSWORD=vop \
    -e POSTGRES_DB=vop \
    -p 127.0.0.1:5432:5432 \
    postgres:17-alpine

# Or use existing PostgreSQL
createdb vop
```

### 4. Run Migrations

```bash
cd backend
alembic upgrade head
```

### 5. Start Backend

```bash
cd backend
uvicorn app.main:app --reload --port 8000
```

API available at http://localhost:8000
Swagger docs at http://localhost:8000/docs

### 6. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

Frontend available at http://localhost:5173

## Project Structure

```
speak-kraliki/
├── backend/
│   ├── app/
│   │   ├── core/           # Configuration, auth, database
│   │   │   ├── config.py   # Settings from environment
│   │   │   ├── auth.py     # JWT authentication
│   │   │   └── database.py # SQLAlchemy async setup
│   │   ├── models/         # Database models
│   │   │   ├── user.py     # HR/CEO users
│   │   │   ├── employee.py # Employee records
│   │   │   ├── survey.py   # Survey definitions
│   │   │   ├── conversation.py
│   │   │   ├── alert.py
│   │   │   └── action.py
│   │   ├── schemas/        # Pydantic schemas
│   │   ├── services/       # Business logic
│   │   │   ├── ai_conversation.py
│   │   │   ├── analysis.py
│   │   │   └── email.py
│   │   └── routers/        # API endpoints
│   │       ├── auth.py
│   │       ├── surveys.py
│   │       ├── voice.py
│   │       └── ...
│   ├── tests/              # Test suite
│   ├── alembic/            # Migrations
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── routes/         # SvelteKit pages
│   │   │   ├── +page.svelte
│   │   │   ├── login/
│   │   │   ├── dashboard/
│   │   │   └── v/[token]/  # Employee voice interface
│   │   └── lib/
│   │       ├── api/        # API client
│   │       ├── stores/     # Svelte stores
│   │       └── components/
│   ├── static/
│   └── package.json
└── docs/                   # Documentation
```

## Environment Variables

### Backend (.env)

```bash
# Database
DATABASE_URL=postgresql+asyncpg://vop:vop@localhost:5432/vop

# Security
SECRET_KEY=dev-secret-key-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=15
REFRESH_TOKEN_EXPIRE_DAYS=7

# AI (get from Google AI Studio)
GEMINI_API_KEY=your-api-key

# Email (optional for development)
RESEND_API_KEY=re_xxxx
RESEND_FROM_EMAIL=noreply@localhost

# URLs
FRONTEND_URL=http://localhost:5173
```

### Frontend

Environment variables are in `frontend/.env`:

```bash
PUBLIC_API_URL=http://localhost:8000
```

## Development Workflow

### Running Tests

```bash
cd backend

# Run all tests
pytest

# With coverage
pytest --cov=app --cov-report=html

# Specific test file
pytest tests/test_auth.py

# Specific test
pytest tests/test_auth.py::test_login_success -v
```

### Creating Migrations

```bash
cd backend

# Auto-generate migration
alembic revision --autogenerate -m "add new field"

# Apply migrations
alembic upgrade head

# Rollback one step
alembic downgrade -1
```

### Code Style

**Python:**
- PEP 8 compliant
- Type hints required
- Use async/await for database operations

**TypeScript/Svelte:**
- 2-space indentation
- Prefer const over let
- Use TypeScript strict mode

### Linting

```bash
# Backend
cd backend
ruff check .
ruff format .

# Frontend
cd frontend
npm run lint
npm run format
```

## API Development

### Adding a New Endpoint

1. Create schema in `backend/app/schemas/`:

```python
# schemas/feature.py
from pydantic import BaseModel

class FeatureCreate(BaseModel):
    name: str
    description: str | None = None

class FeatureResponse(BaseModel):
    id: uuid.UUID
    name: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
```

2. Create router in `backend/app/routers/`:

```python
# routers/feature.py
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(prefix="/features", tags=["features"])

@router.post("/", response_model=FeatureResponse)
async def create_feature(
    data: FeatureCreate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user)
):
    # Implementation
    pass
```

3. Register router in `backend/app/main.py`:

```python
from app.routers import feature
app.include_router(feature.router, prefix="/api")
```

## Frontend Development

### Adding a New Page

1. Create route directory:

```bash
mkdir -p frontend/src/routes/new-page
```

2. Create page component:

```svelte
<!-- frontend/src/routes/new-page/+page.svelte -->
<script lang="ts">
  import { onMount } from 'svelte';
  import { api } from '$lib/api';

  let data = $state<any>(null);

  onMount(async () => {
    data = await api.get('/features');
  });
</script>

<div class="container">
  <h1>New Page</h1>
  {#if data}
    <pre>{JSON.stringify(data, null, 2)}</pre>
  {/if}
</div>
```

### Using Stores

```typescript
// lib/stores/feature.ts
import { writable } from 'svelte/store';

interface Feature {
  id: string;
  name: string;
}

function createFeatureStore() {
  const { subscribe, set, update } = writable<Feature[]>([]);

  return {
    subscribe,
    load: async () => {
      const response = await fetch('/api/features');
      const data = await response.json();
      set(data);
    },
    add: (feature: Feature) => {
      update(features => [...features, feature]);
    }
  };
}

export const features = createFeatureStore();
```

## Debugging

### Backend

```python
# Add to any async function
import logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

async def some_function():
    logger.debug("Debug message")
```

### Frontend

```typescript
// Browser console
console.log('Debug:', data);

// Svelte reactive debugging
$effect(() => {
  console.log('State changed:', someState);
});
```

### Database Queries

```python
# Enable SQLAlchemy echo
# In database.py
engine = create_async_engine(
    settings.database_url,
    echo=True  # Logs all SQL
)
```

## Common Tasks

### Reset Database

```bash
# Drop and recreate
dropdb vop && createdb vop
cd backend && alembic upgrade head
```

### Clear Test Data

```python
# In Python shell
from app.core.database import get_db
from app.models import *

async with get_db() as db:
    await db.execute("TRUNCATE companies CASCADE")
    await db.commit()
```

### Generate API Client Types

```bash
cd frontend
# Generate from OpenAPI spec
npx openapi-typescript http://localhost:8000/openapi.json -o src/lib/api/types.ts
```

## IDE Setup

### VS Code Extensions

- Python (ms-python.python)
- Svelte for VS Code (svelte.svelte-vscode)
- Tailwind CSS IntelliSense (bradlc.vscode-tailwindcss)
- ESLint (dbaeumer.vscode-eslint)
- Ruff (charliermarsh.ruff)

### VS Code Settings

```json
{
  "python.defaultInterpreterPath": "${workspaceFolder}/backend/.venv/bin/python",
  "python.analysis.typeCheckingMode": "basic",
  "[python]": {
    "editor.defaultFormatter": "charliermarsh.ruff"
  },
  "[svelte]": {
    "editor.defaultFormatter": "svelte.svelte-vscode"
  }
}
```

## Troubleshooting

### Port already in use

```bash
# Find process
lsof -i :8000

# Kill it
kill -9 <PID>
```

### Module not found

```bash
# Ensure virtual environment is activated
source backend/.venv/bin/activate

# Reinstall dependencies
pip install -r requirements.txt
```

### Database connection refused

```bash
# Check PostgreSQL is running
docker ps | grep postgres

# Or check system service
systemctl status postgresql
```

### CORS errors

Verify `FRONTEND_URL` in backend `.env` matches your frontend origin.
