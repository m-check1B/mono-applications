# Focus Lite Developer Guide

> **Version**: 2.1.0
> **Last Updated**: November 14, 2025
> **Audience**: Developers, contributors, system architects

---

## Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [Development Setup](#development-setup)
3. [Project Structure](#project-structure)
4. [Backend Development](#backend-development)
5. [Frontend Development](#frontend-development)
6. [Database Schema](#database-schema)
7. [Testing](#testing)
8. [Code Style Guide](#code-style-guide)
9. [Contributing Guidelines](#contributing-guidelines)
10. [Advanced Topics](#advanced-topics)

---

## Architecture Overview

### System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        User Interface                        │
│                    (SvelteKit Frontend)                      │
│                     Port: 5175                               │
└───────────────────┬─────────────────────────────────────────┘
                    │ HTTP/WebSocket
                    ↓
┌─────────────────────────────────────────────────────────────┐
│                     Focus Lite Backend                       │
│                      (FastAPI)                               │
│                     Port: 3017                               │
├─────────────────────────────────────────────────────────────┤
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │  Auth    │  │Knowledge │  │  Tasks   │  │   AI     │   │
│  │  Layer   │  │   Hub    │  │  & Proj  │  │  Engine  │   │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘   │
└───────────────────┬─────────────────────────────────────────┘
                    │
        ┌───────────┼───────────┐
        ↓           ↓           ↓
┌──────────┐  ┌──────────┐  ┌──────────┐
│PostgreSQL│  │  Redis   │  │II-Agent  │
│   DB     │  │  Cache   │  │(Optional)│
│Port: 5432│  │Port: 6379│  │Port: 8000│
└──────────┘  └──────────┘  └──────────┘
        ↓           ↓
┌──────────┐  ┌──────────┐
│OpenRouter│  │ Deepgram │
│   API    │  │   API    │
└──────────┘  └──────────┘
```

### Technology Stack

**Frontend**
- **Framework**: SvelteKit 2.0 (file-based routing, SSR/SSG)
- **Language**: TypeScript 5.0 (strict mode)
- **Build Tool**: Vite 5.0 (HMR, fast builds)
- **Styling**: Tailwind CSS 3.3.6 (utility-first)
- **Components**: bits-ui, lucide-svelte
- **State**: Svelte stores (reactive, simple)
- **HTTP Client**: Native fetch API

**Backend**
- **Framework**: FastAPI 0.110.0 (async, auto docs)
- **Language**: Python 3.14+ (type hints required)
- **ORM**: SQLAlchemy 2.0.27 (modern async support)
- **Migrations**: Alembic 1.13.1 (version control)
- **Validation**: Pydantic 2.6.1 (runtime validation)
- **Auth**: JWT with bcrypt (secure hashing)
- **Caching**: Redis 5.0 (session + AI cache)

**Database**
- **Primary**: PostgreSQL 15+ (JSONB, full-text search)
- **Cache**: Redis 7.0 (key-value, pub/sub)

**AI Services**
- **Primary**: Anthropic Claude 3.5 Sonnet
- **Router**: OpenRouter (multi-model access)
- **Voice**: Gemini 2.5 Flash, OpenAI Realtime
- **Transcription**: Deepgram Nova 2

### Design Principles

1. **AI-First**: Intelligence baked into every feature
2. **Simplicity**: "Simply In, Simply Out" UX philosophy
3. **Type Safety**: TypeScript + Python type hints everywhere
4. **Performance**: Async/await, caching, lazy loading
5. **Security**: 127.0.0.1 binding, JWT auth, input validation
6. **Modularity**: Clean separation of concerns
7. **Testability**: Pure functions, dependency injection

---

## Development Setup

### Prerequisites

**Required**
- Node.js 18+ (for frontend)
- pnpm 8+ (NOT npm or yarn)
- Python 3.14+ (for backend)
- PostgreSQL 15+ (or Docker)
- Git

**Optional**
- Redis 7.0 (for caching, or Docker)
- Docker & Docker Compose (for services)

### Quick Setup (5 Minutes)

```bash
# 1. Clone repository
git clone https://github.com/your-org/focus-lite.git
cd focus-lite

# 2. Run automated setup
./scripts/setup.sh

# 3. Start development servers
./scripts/start.sh

# Frontend: http://127.0.0.1:5175
# Backend:  http://127.0.0.1:3017
# API Docs: http://127.0.0.1:3017/docs
```

### Manual Setup (Detailed)

**1. Database Setup**

```bash
# Option A: Docker (Recommended)
docker run --name focuslite-db \
  -e POSTGRES_USER=postgres \
  -e POSTGRES_PASSWORD=password \
  -e POSTGRES_DB=focuslite \
  -p 5432:5432 \
  -d postgres:15

# Option B: Local PostgreSQL
createdb focuslite
psql focuslite -c "CREATE USER postgres WITH PASSWORD 'password';"
```

**2. Redis Setup (Optional)**

```bash
# Docker
docker run --name focuslite-redis \
  -p 6379:6379 \
  -d redis:7-alpine

# Or use local Redis
redis-server --port 6379
```

**3. Backend Setup**

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your API keys and database URL

# Run migrations
alembic upgrade head

# Start server
./start.sh
# Or manually: uvicorn app.main:app --reload --host 127.0.0.1 --port 3017
```

**4. Frontend Setup**

```bash
cd frontend

# Install dependencies (MUST use pnpm)
pnpm install

# Configure environment
cp .env.example .env
# Edit .env with backend URL

# Start dev server
pnpm dev

# Or preview production build
pnpm build && pnpm preview
```

### Environment Variables

**Backend** (`.env`)
```bash
# Database
DATABASE_URL=postgresql://postgres:password@localhost:5432/focuslite

# Security
JWT_SECRET=your-secret-key-minimum-32-characters-long
SESSION_SECRET=another-secret-key-minimum-32-characters

# AI Services
ANTHROPIC_API_KEY=sk-ant-api03-...
OPENAI_API_KEY=sk-...
GEMINI_API_KEY=...
DEEPGRAM_API_KEY=...

# Optional: Redis
REDIS_URL=redis://localhost:6379/0

# Server
PORT=3017
HOST=127.0.0.1
ALLOWED_ORIGINS=http://127.0.0.1:5175

# Environment
NODE_ENV=development
```

**Frontend** (`.env`)
```bash
PUBLIC_API_URL=http://127.0.0.1:3017
```

---

## Project Structure

```
focus-lite/
├── backend/                 # FastAPI Backend
│   ├── app/
│   │   ├── core/           # Core utilities
│   │   │   ├── config.py   # Configuration
│   │   │   ├── database.py # Database connection
│   │   │   └── security.py # Auth & JWT
│   │   ├── models/         # SQLAlchemy models
│   │   │   ├── user.py
│   │   │   ├── task.py
│   │   │   ├── project.py
│   │   │   ├── knowledge_item.py
│   │   │   └── item_type.py
│   │   ├── schemas/        # Pydantic schemas
│   │   │   ├── auth.py
│   │   │   ├── task.py
│   │   │   └── knowledge.py
│   │   ├── routers/        # API endpoints
│   │   │   ├── auth.py
│   │   │   ├── tasks.py
│   │   │   ├── projects.py
│   │   │   ├── knowledge.py
│   │   │   ├── agent_tools.py
│   │   │   ├── agent.py
│   │   │   ├── settings.py
│   │   │   ├── ai.py
│   │   │   └── swarm_tools.py (deprecated)
│   │   ├── services/       # Business logic
│   │   │   ├── ai_service.py
│   │   │   └── knowledge_defaults.py
│   │   └── main.py         # FastAPI app
│   ├── alembic/            # Database migrations
│   │   └── versions/
│   │       ├── 006_add_knowledge_layer.py
│   │       └── 008_rename_metadata_to_item_metadata.py
│   ├── tests/              # Tests
│   │   ├── unit/
│   │   ├── integration/
│   │   └── e2e/
│   ├── requirements.txt    # Python dependencies
│   ├── .env.example
│   └── start.sh
│
├── frontend/               # SvelteKit Frontend
│   ├── src/
│   │   ├── lib/
│   │   │   ├── api/        # API clients
│   │   │   │   ├── auth.ts
│   │   │   │   ├── knowledge.ts
│   │   │   │   ├── agent.ts
│   │   │   │   └── settings.ts
│   │   │   ├── stores/     # Svelte stores
│   │   │   │   ├── auth.ts
│   │   │   │   ├── knowledge.ts
│   │   │   │   └── theme.ts
│   │   │   └── components/ # Reusable components
│   │   ├── routes/         # File-based routing
│   │   │   ├── +layout.svelte
│   │   │   ├── +page.svelte
│   │   │   ├── login/
│   │   │   ├── register/
│   │   │   ├── dashboard/
│   │   │   ├── knowledge/
│   │   │   └── agent/
│   │   ├── app.css         # Global styles
│   │   └── app.html        # HTML template
│   ├── static/             # Static assets
│   ├── package.json
│   ├── svelte.config.js
│   ├── vite.config.ts
│   └── tsconfig.json
│
├── docs/                   # Documentation
│   ├── USER_GUIDE.md
│   ├── API_REFERENCE.md
│   ├── DEVELOPER_GUIDE.md  # This file
│   └── DEPLOYMENT_GUIDE.md
│
├── scripts/                # Utility scripts
│   ├── setup.sh            # One-time setup
│   ├── start.sh            # Start dev servers
│   ├── test.sh             # Run all tests
│   ├── build.sh            # Production build
│   └── deploy.sh           # Deploy to production
│
├── infra/                  # Infrastructure
│   ├── docker/
│   ├── nginx/
│   └── systemd/
│
├── README.md               # Project overview
├── CHANGELOG.md            # Version history
└── CLAUDE.md               # AI assistant instructions
```

---

## Backend Development

### Creating a New Endpoint

**1. Define the Model** (`app/models/example.py`)

```python
from sqlalchemy import Column, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base
from datetime import datetime

class Example(Base):
    __tablename__ = "examples"

    id = Column(String, primary_key=True)
    userId = Column(String, ForeignKey("users.id"), nullable=False)
    title = Column(String, nullable=False)
    createdAt = Column(DateTime, default=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="examples")
```

**2. Create Pydantic Schemas** (`app/schemas/example.py`)

```python
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

class ExampleCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)

class ExampleUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)

class ExampleResponse(BaseModel):
    id: str
    userId: str
    title: str
    createdAt: datetime

    class Config:
        from_attributes = True  # Pydantic v2 syntax
```

**3. Create Router** (`app/routers/example.py`)

```python
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.core.security import get_current_user, generate_id
from app.models.user import User
from app.models.example import Example
from app.schemas.example import ExampleCreate, ExampleUpdate, ExampleResponse

router = APIRouter(prefix="/examples", tags=["examples"])

@router.post("/", response_model=ExampleResponse)
async def create_example(
    data: ExampleCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new example"""
    example = Example(
        id=generate_id(),
        userId=current_user.id,
        **data.model_dump()
    )
    db.add(example)
    db.commit()
    db.refresh(example)
    return ExampleResponse.model_validate(example)

@router.get("/", response_model=List[ExampleResponse])
async def list_examples(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List all examples for current user"""
    examples = db.query(Example).filter(
        Example.userId == current_user.id
    ).all()
    return [ExampleResponse.model_validate(e) for e in examples]
```

**4. Register Router** (`app/main.py`)

```python
from app.routers import example

app.include_router(example.router, prefix="/api")
```

**5. Create Migration**

```bash
cd backend
alembic revision --autogenerate -m "add examples table"
alembic upgrade head
```

### Database Migrations

**Create New Migration**
```bash
alembic revision --autogenerate -m "description"
```

**Apply Migrations**
```bash
alembic upgrade head
```

**Rollback Migration**
```bash
alembic downgrade -1
```

**View Migration History**
```bash
alembic history
```

### Authentication & Authorization

**Protecting Endpoints**

```python
from app.core.security import get_current_user
from app.models.user import User

@router.get("/protected")
async def protected_route(current_user: User = Depends(get_current_user)):
    # current_user is automatically injected
    return {"userId": current_user.id}
```

**Creating Tokens**

```python
from app.core.security import create_access_token

token = create_access_token(user_id="usr_123")
```

**Agent Tokens**

```python
from app.core.security import create_agent_token

# Creates token with 2-hour expiry and "agent" scope
agent_token = create_agent_token(user_id="usr_123")
```

### Working with AI Services

**OpenRouter Integration**

```python
from app.services.ai_service import get_openrouter_client

async def call_ai(prompt: str, user: User):
    client = get_openrouter_client(user)  # Uses BYOK if available

    response = await client.chat.completions.create(
        model="anthropic/claude-3.5-sonnet",
        messages=[
            {"role": "system", "content": "You are a helpful assistant"},
            {"role": "user", "content": prompt}
        ]
    )

    return response.choices[0].message.content
```

**Function Calling**

```python
tools = [
    {
        "type": "function",
        "function": {
            "name": "create_knowledge_item",
            "description": "Create a knowledge item",
            "parameters": {
                "type": "object",
                "properties": {
                    "typeId": {"type": "string"},
                    "title": {"type": "string"},
                    "content": {"type": "string"}
                },
                "required": ["typeId", "title"]
            }
        }
    }
]

response = await client.chat.completions.create(
    model="anthropic/claude-3.5-sonnet",
    messages=messages,
    tools=tools,
    tool_choice="auto"
)

# Handle tool calls
if response.choices[0].message.tool_calls:
    for tool_call in response.choices[0].message.tool_calls:
        function_name = tool_call.function.name
        arguments = json.loads(tool_call.function.arguments)
        # Execute function and collect result
```

---

## Frontend Development

### Creating a New Page

**1. Create Route** (`src/routes/example/+page.svelte`)

```svelte
<script lang="ts">
  import { onMount } from 'svelte';
  import { exampleStore } from '$lib/stores/example';
  import { getExamples } from '$lib/api/example';

  let examples: Example[] = [];
  let loading = true;

  onMount(async () => {
    try {
      examples = await getExamples();
    } catch (error) {
      console.error('Failed to load examples:', error);
    } finally {
      loading = false;
    }
  });
</script>

<div class="container mx-auto p-4">
  <h1 class="text-2xl font-bold mb-4">Examples</h1>

  {#if loading}
    <p>Loading...</p>
  {:else}
    <ul>
      {#each examples as example}
        <li>{example.title}</li>
      {/each}
    </ul>
  {/if}
</div>
```

**2. Create API Client** (`src/lib/api/example.ts`)

```typescript
import { getAuthHeaders } from './auth';

const API_URL = import.meta.env.PUBLIC_API_URL;

export interface Example {
  id: string;
  title: string;
  createdAt: string;
}

export async function getExamples(): Promise<Example[]> {
  const response = await fetch(`${API_URL}/api/examples`, {
    headers: getAuthHeaders()
  });

  if (!response.ok) {
    throw new Error('Failed to fetch examples');
  }

  return response.json();
}

export async function createExample(title: string): Promise<Example> {
  const response = await fetch(`${API_URL}/api/examples`, {
    method: 'POST',
    headers: getAuthHeaders(),
    body: JSON.stringify({ title })
  });

  if (!response.ok) {
    throw new Error('Failed to create example');
  }

  return response.json();
}
```

**3. Create Store** (`src/lib/stores/example.ts`)

```typescript
import { writable } from 'svelte/store';
import type { Example } from '$lib/api/example';

function createExampleStore() {
  const { subscribe, set, update } = writable<Example[]>([]);

  return {
    subscribe,
    set,
    add: (example: Example) => update(items => [...items, example]),
    remove: (id: string) => update(items => items.filter(item => item.id !== id)),
    clear: () => set([])
  };
}

export const exampleStore = createExampleStore();
```

### Component Development

**Creating Reusable Components**

```svelte
<!-- src/lib/components/Button.svelte -->
<script lang="ts">
  export let variant: 'primary' | 'secondary' = 'primary';
  export let disabled = false;
  export let onClick: () => void = () => {};

  const baseClasses = 'px-4 py-2 rounded font-medium';
  const variantClasses = {
    primary: 'bg-blue-600 text-white hover:bg-blue-700',
    secondary: 'bg-gray-200 text-gray-800 hover:bg-gray-300'
  };
</script>

<button
  class="{baseClasses} {variantClasses[variant]}"
  {disabled}
  on:click={onClick}
>
  <slot />
</button>
```

**Usage**

```svelte
<script>
  import Button from '$lib/components/Button.svelte';

  function handleClick() {
    console.log('Button clicked!');
  }
</script>

<Button variant="primary" onClick={handleClick}>
  Click Me
</Button>
```

### State Management

**Global Store Pattern**

```typescript
// src/lib/stores/auth.ts
import { writable } from 'svelte/store';

interface AuthState {
  token: string | null;
  user: User | null;
  isAuthenticated: boolean;
}

function createAuthStore() {
  const { subscribe, set, update } = writable<AuthState>({
    token: null,
    user: null,
    isAuthenticated: false
  });

  return {
    subscribe,
    login: (token: string, user: User) => {
      localStorage.setItem('token', token);
      set({ token, user, isAuthenticated: true });
    },
    logout: () => {
      localStorage.removeItem('token');
      set({ token: null, user: null, isAuthenticated: false });
    },
    initialize: () => {
      const token = localStorage.getItem('token');
      if (token) {
        // Validate token and set user
      }
    }
  };
}

export const authStore = createAuthStore();
```

---

## Database Schema

### Core Tables

**users**
```sql
CREATE TABLE users (
    id VARCHAR PRIMARY KEY,
    email VARCHAR UNIQUE NOT NULL,
    password_hash VARCHAR NOT NULL,
    is_premium BOOLEAN DEFAULT FALSE,
    usage_count INTEGER DEFAULT 0,
    openrouter_api_key VARCHAR,
    created_at TIMESTAMP DEFAULT NOW()
);
```

**item_types** (Knowledge Hub)
```sql
CREATE TABLE item_type (
    id VARCHAR PRIMARY KEY,
    user_id VARCHAR REFERENCES users(id) ON DELETE CASCADE,
    name VARCHAR NOT NULL,
    icon VARCHAR,
    color VARCHAR,
    created_at TIMESTAMP DEFAULT NOW()
);
```

**knowledge_item** (Knowledge Hub)
```sql
CREATE TABLE knowledge_item (
    id VARCHAR PRIMARY KEY,
    user_id VARCHAR REFERENCES users(id) ON DELETE CASCADE,
    type_id VARCHAR REFERENCES item_type(id) ON DELETE CASCADE,
    title VARCHAR NOT NULL,
    content TEXT,
    item_metadata JSONB,
    completed BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

**tasks**
```sql
CREATE TABLE task (
    id VARCHAR PRIMARY KEY,
    user_id VARCHAR REFERENCES users(id) ON DELETE CASCADE,
    project_id VARCHAR REFERENCES project(id),
    title VARCHAR NOT NULL,
    description TEXT,
    status VARCHAR DEFAULT 'pending',
    priority INTEGER DEFAULT 1,
    estimated_minutes INTEGER,
    due_date TIMESTAMP,
    completed_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW()
);
```

**projects**
```sql
CREATE TABLE project (
    id VARCHAR PRIMARY KEY,
    user_id VARCHAR REFERENCES users(id) ON DELETE CASCADE,
    name VARCHAR NOT NULL,
    description TEXT,
    color VARCHAR,
    icon VARCHAR,
    created_at TIMESTAMP DEFAULT NOW()
);
```

### Key Changes

**Migration 008: metadata → item_metadata**

Renamed `metadata` column to `item_metadata` to avoid SQLAlchemy reserved attribute conflict.

```python
# Before
knowledge_item.metadata = {"priority": "high"}  # ERROR: conflicts with SQLAlchemy

# After
knowledge_item.item_metadata = {"priority": "high"}  # OK
```

---

## Testing

### Backend Testing (pytest)

**Unit Test Example**

```python
# tests/unit/test_knowledge.py
import pytest
from app.models.knowledge_item import KnowledgeItem
from app.core.security import generate_id

def test_create_knowledge_item(db_session):
    item = KnowledgeItem(
        id=generate_id(),
        userId="usr_test",
        typeId="type_test",
        title="Test Item"
    )
    db_session.add(item)
    db_session.commit()

    assert item.id is not None
    assert item.title == "Test Item"
    assert item.completed == False
```

**Integration Test Example**

```python
# tests/integration/test_knowledge_endpoints.py
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_create_knowledge_item():
    # Login first
    response = client.post("/api/auth/login", json={
        "email": "test@example.com",
        "password": "password"
    })
    token = response.json()["token"]

    # Create item
    response = client.post(
        "/api/knowledge/items",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "typeId": "type_123",
            "title": "Test Item"
        }
    )

    assert response.status_code == 200
    assert response.json()["title"] == "Test Item"
```

**Running Tests**

```bash
cd backend

# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test file
pytest tests/unit/test_knowledge.py

# Run specific test
pytest tests/unit/test_knowledge.py::test_create_knowledge_item
```

### Frontend Testing (Vitest)

**Component Test Example**

```typescript
// tests/Button.test.ts
import { render, fireEvent } from '@testing-library/svelte';
import Button from '$lib/components/Button.svelte';

test('button click handler', async () => {
  let clicked = false;
  const { getByText } = render(Button, {
    props: {
      onClick: () => { clicked = true; }
    }
  });

  const button = getByText('Click Me');
  await fireEvent.click(button);

  expect(clicked).toBe(true);
});
```

**Running Tests**

```bash
cd frontend

# Run tests
pnpm test

# Watch mode
pnpm test:watch

# Coverage
pnpm test:coverage
```

---

## Code Style Guide

### Python (Backend)

**Follow PEP 8 + Black formatting**

```python
# Good
async def create_knowledge_item(
    data: KnowledgeItemCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> KnowledgeItemResponse:
    """
    Create a new knowledge item.

    Args:
        data: Item creation data
        current_user: Authenticated user
        db: Database session

    Returns:
        Created knowledge item
    """
    item = KnowledgeItem(
        id=generate_id(),
        userId=current_user.id,
        **data.model_dump()
    )
    db.add(item)
    db.commit()
    db.refresh(item)
    return KnowledgeItemResponse.model_validate(item)

# Bad
def create_knowledge_item(data,user,db):  # No types, no async
    item=KnowledgeItem(id=generate_id(),userId=user.id,**data.dict())  # No spacing
    db.add(item);db.commit()  # Multiple statements
    return item  # Wrong return type
```

**Type Hints Required**

```python
# Good
def process_items(items: List[KnowledgeItem]) -> Dict[str, int]:
    return {"count": len(items)}

# Bad
def process_items(items):
    return {"count": len(items)}
```

**Formatting**

```bash
# Format code
black app/

# Check imports
isort app/

# Lint
flake8 app/
```

### TypeScript (Frontend)

**Follow Prettier + ESLint rules**

```typescript
// Good
export async function createKnowledgeItem(
  typeId: string,
  title: string,
  content?: string
): Promise<KnowledgeItem> {
  const response = await fetch(`${API_URL}/api/knowledge/items`, {
    method: 'POST',
    headers: getAuthHeaders(),
    body: JSON.stringify({ typeId, title, content })
  });

  if (!response.ok) {
    throw new Error(`Failed to create item: ${response.statusText}`);
  }

  return response.json();
}

// Bad
export async function createKnowledgeItem(typeId,title,content) {  // No types
  const response=await fetch(API_URL+"/api/knowledge/items",{method:"POST",headers:getAuthHeaders(),body:JSON.stringify({typeId,title,content})})  // No formatting
  return response.json()  // No error handling
}
```

**Formatting**

```bash
# Format code
pnpm format

# Check types
pnpm check

# Lint
pnpm lint
```

### Commit Messages

Follow Conventional Commits:

```bash
# Good
feat: add knowledge hub with item types and items
fix: resolve metadata column conflict in knowledge_item
docs: update API reference with agent tools endpoints
refactor: extract AI service to separate module
test: add unit tests for knowledge endpoints

# Bad
update stuff
fixed bug
changes
```

---

## Contributing Guidelines

### Workflow

1. **Fork & Clone**
   ```bash
   git clone https://github.com/your-username/focus-lite.git
   cd focus-lite
   ```

2. **Create Feature Branch**
   ```bash
   git checkout -b feature/knowledge-hub-improvements
   ```

3. **Make Changes**
   - Write code following style guide
   - Add tests for new features
   - Update documentation

4. **Test**
   ```bash
   ./scripts/test.sh
   ```

5. **Commit**
   ```bash
   git add .
   git commit -m "feat: add bulk import for knowledge items"
   ```

6. **Push & Create PR**
   ```bash
   git push origin feature/knowledge-hub-improvements
   # Create pull request on GitHub
   ```

### Pull Request Guidelines

**PR Title**: Use conventional commit format

**PR Description**: Include:
- What changes were made
- Why the changes were needed
- How to test the changes
- Screenshots (for UI changes)
- Breaking changes (if any)

**Example PR**

```markdown
## Description
Adds bulk import functionality for knowledge items via CSV upload.

## Motivation
Users requested ability to import existing notes from other tools.

## Changes
- Added `/api/knowledge/import` endpoint
- Created CSV parser with validation
- Added progress tracking for large imports
- Updated frontend with upload UI

## Testing
1. Create CSV file with columns: typeId, title, content
2. Navigate to Knowledge Hub → Import
3. Upload CSV
4. Verify items are created correctly

## Screenshots
[Upload UI screenshot]

## Breaking Changes
None
```

### Code Review Checklist

- [ ] Code follows style guide
- [ ] Tests pass
- [ ] Documentation updated
- [ ] No console.log or debug code
- [ ] Type safety maintained
- [ ] Security considerations addressed
- [ ] Performance impact considered

---

## Advanced Topics

### Custom AI Models

**Adding Custom OpenRouter Models**

```python
# app/services/ai_service.py
CUSTOM_MODELS = {
    "fast": "anthropic/claude-3-haiku",
    "balanced": "anthropic/claude-3.5-sonnet",
    "powerful": "anthropic/claude-3-opus",
    "code": "openai/gpt-4-turbo",
}

def get_model_for_task(task_type: str) -> str:
    model_map = {
        "chat": "fast",
        "planning": "balanced",
        "analysis": "powerful",
        "code": "code",
    }
    return CUSTOM_MODELS[model_map.get(task_type, "balanced")]
```

### WebSocket Integration

**Backend** (`app/routers/websocket.py`)

```python
from fastapi import WebSocket
from typing import List

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    async def broadcast(self, message: dict):
        for connection in self.active_connections:
            await connection.send_json(message)

manager = ConnectionManager()

@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_json()
            await manager.broadcast(data)
    except:
        manager.active_connections.remove(websocket)
```

**Frontend** (`src/lib/api/websocket.ts`)

```typescript
export class WebSocketClient {
  private ws: WebSocket | null = null;

  connect(onMessage: (data: any) => void) {
    this.ws = new WebSocket('ws://127.0.0.1:3017/ws');

    this.ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      onMessage(data);
    };

    this.ws.onerror = (error) => {
      console.error('WebSocket error:', error);
    };
  }

  send(data: any) {
    if (this.ws?.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify(data));
    }
  }

  disconnect() {
    this.ws?.close();
  }
}
```

### Performance Optimization

**Database Query Optimization**

```python
# Bad: N+1 query problem
items = db.query(KnowledgeItem).all()
for item in items:
    item_type = db.query(ItemType).filter(ItemType.id == item.typeId).first()

# Good: Eager loading
from sqlalchemy.orm import joinedload

items = db.query(KnowledgeItem).options(
    joinedload(KnowledgeItem.item_type)
).all()
```

**Caching with Redis**

```python
import redis
import json

redis_client = redis.from_url("redis://localhost:6379/0")

def get_cached_items(user_id: str) -> Optional[List[dict]]:
    cache_key = f"knowledge_items:{user_id}"
    cached = redis_client.get(cache_key)
    if cached:
        return json.loads(cached)
    return None

def set_cached_items(user_id: str, items: List[dict], ttl: int = 300):
    cache_key = f"knowledge_items:{user_id}"
    redis_client.setex(cache_key, ttl, json.dumps(items))
```

---

## Troubleshooting

### Common Development Issues

**Port Already in Use**
```bash
# Find process using port
lsof -i :3017
# Kill process
kill -9 <PID>
```

**Database Connection Errors**
```bash
# Check PostgreSQL is running
pg_isready -h localhost -p 5432

# Reset database
./scripts/db-reset.sh
```

**Frontend Build Errors**
```bash
# Clear node_modules and reinstall
cd frontend
rm -rf node_modules
pnpm install
```

---

## Resources

- **FastAPI Docs**: https://fastapi.tiangolo.com
- **SvelteKit Docs**: https://kit.svelte.dev
- **SQLAlchemy Docs**: https://docs.sqlalchemy.org
- **Pydantic Docs**: https://docs.pydantic.dev
- **Tailwind CSS**: https://tailwindcss.com

---

**Happy Coding!** 🚀

For questions or issues, create a GitHub issue or reach out to the team.
