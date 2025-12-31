# Backend - FastAPI + Python

Stack 2026 compliant backend using FastAPI, UV, and Pydantic.

## Technology Stack

- **Framework:** FastAPI 0.115+
- **Runtime:** Python 3.11+
- **Package Manager:** UV (Rust-based, 10-100x faster than pip)
- **Validation:** Pydantic v2 with Settings
- **Testing:** pytest with asyncio support
- **Documentation:** Auto-generated OpenAPI/Swagger

## Quick Start

### Install Dependencies

```bash
# UV will automatically create a virtual environment
uv sync --all-extras
```

### Run Development Server

```bash
# With hot reload
uv run uvicorn app.main:app --reload

# Or use the helper script
../scripts/dev-backend.sh
```

The server will start at:
- API: http://localhost:8000
- Interactive docs: http://localhost:8000/docs
- OpenAPI spec: http://localhost:8000/openapi.json
- Health check: http://localhost:8000/health

### Run Tests

```bash
# Run all tests
uv run pytest tests/ -v

# Run with coverage
uv run pytest tests/ --cov=app

# Or use the helper script
../scripts/test-backend.sh
```

## Project Structure

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py              # Application factory and FastAPI app
│   ├── config/
│   │   ├── __init__.py
│   │   └── settings.py      # Pydantic settings management
│   ├── providers/
│   │   ├── __init__.py
│   │   ├── base.py         # Abstract protocols & types
│   │   ├── openai.py       # OpenAI Realtime API provider
│   │   └── gemini.py       # Gemini Live API provider
│   ├── sessions/
│   │   ├── __init__.py
│   │   ├── manager.py      # Session orchestration
│   │   └── models.py       # Session data models
│   └── streaming/
│       ├── __init__.py
│       └── websocket.py    # WebSocket handlers
├── tests/
│   ├── __init__.py
│   └── test_health.py       # Health endpoint tests
├── pyproject.toml           # UV project configuration
├── .python-version          # Python version for UV
└── .env.example             # Example environment variables
```

## Configuration

Configuration is managed via Pydantic Settings in `app/config/settings.py`.

### Environment Variables

Create a `.env` file based on `.env.example`:

```bash
# Application
APP_NAME="Operator Demo Backend"
VERSION="0.1.0"
ENVIRONMENT="development"

# Server
HOST="0.0.0.0"
PORT=8000
DEBUG=true
PUBLIC_URL="https://api.example.com" # optional, used for telephony stream URLs

# CORS
CORS_ORIGINS='["http://localhost:3000", "http://localhost:5173"]'

# Security
SECRET_KEY="your-secret-key-change-in-production"
JWT_EXPIRATION_MINUTES=1440
JWT_KEYS_DIR="keys"

# Authentication cookies
AUTH_COOKIE_NAME="auth_token"
REFRESH_COOKIE_NAME="refresh_token"
AUTH_COOKIE_DOMAIN=".verduona.dev"
AUTH_COOKIE_SECURE=true
AUTH_COOKIE_SAMESITE="lax"
AUTH_COOKIE_PATH="/"

# Database
DATABASE_URL="postgresql://user:password@host:5432/operator_demo"

# External Services (placeholder)
OPENAI_API_KEY=""
GEMINI_API_KEY=""
DEEPGRAM_API_KEY=""
TWILIO_ACCOUNT_SID=""
TWILIO_AUTH_TOKEN=""
TELNYX_API_KEY=""
TELNYX_PUBLIC_KEY=""

# Logging
LOG_LEVEL="INFO"
```

## API Endpoints

### Core Endpoints

- `GET /` - Root endpoint with API information
- `GET /health` - Health check endpoint
- `GET /docs` - Interactive API documentation (Swagger UI)
- `GET /redoc` - Alternative API documentation (ReDoc)

### Provider Management ✅

- `GET /api/v1/providers` - List available AI providers and capabilities

### Session Management ✅

- `POST /api/v1/sessions` - Create new conversation session
- `GET /api/v1/sessions/{session_id}` - Get session details
- `GET /api/v1/sessions` - List all sessions (optional status filter)
- `POST /api/v1/sessions/{session_id}/start` - Start session & connect to provider
- `POST /api/v1/sessions/{session_id}/end` - End session & cleanup

### WebSocket Streaming ✅

- `WS /ws/sessions/{session_id}` - Real-time audio/text streaming (primary)
- `WS /api/v1/sessions/{session_id}/stream` - Legacy alias for backwards compatibility

# Authentication Endpoints ✅

- `POST /api/v1/auth/register` - Register and receive signed Ed25519 JWT (HTTP-only cookies)
- `POST /api/v1/auth/login` - Authenticate existing user
- `GET /api/v1/auth/me` - Retrieve current user profile from cookie/Authorization header
- `POST /api/v1/auth/refresh` - Refresh access token using refresh cookie
- `POST /api/v1/auth/logout` - Clear authentication cookies

### Provider Settings & Telephony ✅

- `GET /api/v1/settings/provider` - Retrieve persisted provider defaults
- `PUT /api/v1/settings/provider` - Update provider defaults
- `POST /api/v1/telephony/outbound` - Initiate outbound call (creates session, returns stream URL/TwiML, registers call SID)
-  • Request fields: `to_number` (required), `from_number` (optional – falls back to provider settings), `telephony_provider` (optional), `metadata` (optional map persisted on the session)
- `POST /api/v1/telephony/webhooks/{provider}` - Handle inbound webhook events (provision session and acknowledge lifecycle events)

### Future Endpoints (Planned)

- `POST /api/calls` - Initiate outbound call (Twilio/Telnyx)

## Development Guidelines

### Adding New Routes

1. Create router module in `app/routers/`
2. Define Pydantic models for request/response
3. Register router in `app/main.py`
4. Add tests in `tests/`

Example:

```python
# app/routers/sessions.py
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter(prefix="/api/sessions", tags=["sessions"])

class Session(BaseModel):
    id: str
    status: str

@router.get("/", response_model=list[Session])
async def list_sessions():
    return []
```

### Adding Tests

```python
# tests/test_sessions.py
def test_list_sessions(client):
    response = client.get("/api/sessions")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
```

### Code Style

- Follow PEP 8 conventions
- Use type hints for all functions
- Document functions with docstrings
- Keep functions focused and small

## UV Commands Reference

```bash
# Install dependencies
uv sync

# Install with dev dependencies
uv sync --all-extras

# Add new package
uv add package-name

# Add dev package
uv add --dev package-name

# Update all packages
uv sync --upgrade

# Run Python script
uv run python script.py

# Run command in venv
uv run <command>
```

## Testing

### Running Tests

```bash
# All tests
uv run pytest

# Specific test file
uv run pytest tests/test_health.py

# With verbose output
uv run pytest -v

# With coverage
uv run pytest --cov=app --cov-report=html

# Watch mode (requires pytest-watch)
uv run ptw
```

### Writing Tests

Use pytest with FastAPI's TestClient:

```python
import pytest
from fastapi.testclient import TestClient
from app.main import create_app

@pytest.fixture
def client():
    app = create_app()
    return TestClient(app)

def test_endpoint(client):
    response = client.get("/endpoint")
    assert response.status_code == 200
```

## Deployment

### Production Configuration

1. Set `ENVIRONMENT=production` in `.env`
2. Set `DEBUG=false`
3. Use a secure `SECRET_KEY`
4. Configure proper CORS origins
5. Set up database connection
6. Configure external service credentials

### Running in Production

```bash
# Using uvicorn directly
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4

# Using gunicorn with uvicorn workers
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker
```

## Troubleshooting

### UV Installation Issues

If UV is not installed:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### Virtual Environment Issues

```bash
# Remove and recreate venv
rm -rf .venv
uv sync
```

### Import Errors

Ensure you're running commands with `uv run`:

```bash
uv run python script.py  # Correct
python script.py         # May fail
```

## Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Pydantic Documentation](https://docs.pydantic.dev/)
- [UV Documentation](https://docs.astral.sh/uv/)
- [pytest Documentation](https://docs.pytest.org/)
- [Stack 2026 Standards](/home/adminmatej/github/stack-2026/)
