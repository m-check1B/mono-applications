# Voice by Kraliki Python Backend

**Stack 2026 Compliant** - Python 3.11+ + FastAPI + SQLAlchemy + PostgreSQL

## 🚀 Quick Start

```bash
# Install dependencies
pip install -r requirements.txt
# OR with Poetry
poetry install

# Setup environment
cp .env.example .env
# Edit .env with your configuration

# Run development server
uvicorn app.main:app --reload --host 127.0.0.1 --port 3010

# Run with Python
python -m app.main

# Run tests
pytest
pytest --cov=app
```

## 📁 Project Structure

```
backend-python/
├── app/
│   ├── main.py              # FastAPI application entry point
│   ├── core/                # Core functionality
│   │   ├── config.py        # Application configuration
│   │   ├── database.py      # SQLAlchemy setup
│   │   └── logger.py        # Structured logging
│   ├── models/              # SQLAlchemy models
│   │   └── user.py          # User model (example)
│   ├── schemas/             # Pydantic schemas (TODO)
│   ├── routers/             # API endpoints (TODO)
│   ├── services/            # Business logic (TODO)
│   ├── middleware/          # FastAPI middleware (TODO)
│   └── utils/               # Utilities (TODO)
├── alembic/                 # Database migrations (TODO)
├── tests/                   # pytest tests (TODO)
├── requirements.txt         # Python dependencies
├── pyproject.toml           # Poetry configuration
└── .env.example             # Environment template
```

## 🔧 Technology Stack

- **Python**: 3.11+
- **Framework**: FastAPI 0.110+
- **Database**: PostgreSQL 15+ with SQLAlchemy 2.0+
- **Migrations**: Alembic
- **Validation**: Pydantic 2.0+
- **Authentication**: python-jose (JWT)
- **Testing**: pytest + pytest-asyncio
- **Logging**: structlog

## 📚 API Documentation

Once running, visit:
- **Swagger UI**: http://127.0.0.1:3010/docs
- **ReDoc**: http://127.0.0.1:3010/redoc

## 🧪 Testing

```bash
# Run all tests
pytest

# With coverage
pytest --cov=app --cov-report=html

# Specific test file
pytest tests/test_auth.py -v

# Watch mode (requires pytest-watch)
ptw -- -v
```

## 📖 Development Guide

See [PYTHON_MIGRATION_GUIDE.md](../docs/PYTHON_MIGRATION_GUIDE.md) for detailed migration information.

### Adding a New Endpoint

1. Create Pydantic schema in `app/schemas/`
2. Create SQLAlchemy model in `app/models/`
3. Create router in `app/routers/`
4. Register router in `app/main.py`
5. Write tests in `tests/`

Example:

```python
# app/routers/items.py
from fastapi import APIRouter, Depends
from app.schemas.item import ItemCreate, ItemResponse

router = APIRouter(prefix="/api/items", tags=["items"])

@router.post("/", response_model=ItemResponse)
async def create_item(item: ItemCreate):
    return await item_service.create(item)
```

## 🔐 Security

- JWT authentication with `python-jose`
- Password hashing with `passlib[bcrypt]`
- CORS middleware configured
- Secret key validation in production
- Environment-based configuration

## 📝 Environment Variables

See `.env.example` for all available configuration options.

Required for production:
- `CC_LITE_SECRET_KEY` - Application secret
- `DATABASE_URL` - PostgreSQL connection string
- `JWT_SECRET` - JWT signing key (or uses SECRET_KEY)

## 🚀 Deployment

```bash
# Production server with Gunicorn + Uvicorn workers
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:3010

# Docker
docker build -t cc-lite-backend .
docker run -p 3010:3010 cc-lite-backend
```

## 📊 Current Status

**Phase 1: Foundation** ✅ COMPLETED
- [x] Directory structure created
- [x] FastAPI application setup
- [x] Database configuration
- [x] Structured logging
- [x] Sample User model
- [x] Dependencies configured

**Phase 2: Database Models** 🚧 IN PROGRESS
- [ ] All Prisma models converted to SQLAlchemy
- [ ] Alembic migrations setup

**Phase 3-8**: See [PYTHON_MIGRATION_GUIDE.md](../docs/PYTHON_MIGRATION_GUIDE.md)

## 🔗 References

- [FastAPI Docs](https://fastapi.tiangolo.com/)
- [SQLAlchemy 2.0 Docs](https://docs.sqlalchemy.org/)
- [Pydantic V2 Docs](https://docs.pydantic.dev/2.0/)
- [Stack 2026 Standards](/home/adminmatej/github/stack-2026/)
