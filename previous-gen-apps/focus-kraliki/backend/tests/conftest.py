"""
Pytest Configuration and Fixtures
Provides test database, async client, auth helpers
"""

import os
import sys
import time
from pathlib import Path

from dotenv import load_dotenv

# Standard test user password - use this in all tests that need to login
TEST_USER_PASSWORD = "testpassword123"

# Add backend directory to Python path
backend_dir = Path(__file__).parent.parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

# Load environment variables from backend/.env so local devs don't have to export manually.
load_dotenv(backend_dir / ".env")
# Ensure deterministic timezone for time-based tests (JWT exp, etc.)
os.environ.setdefault("TZ", "UTC")
if hasattr(time, "tzset"):
    time.tzset()
# Disable external event publishing during tests for speed/stability
os.environ.setdefault("SKIP_EVENT_PUBLISH", "1")
# Skip DB init in module.py - tests use their own db fixture
os.environ.setdefault("SKIP_DB_INIT", "1")
# Provide dummy API keys so provider calls can be mocked without errors.
if not os.environ.get("GEMINI_API_KEY"):
    os.environ["GEMINI_API_KEY"] = "test-gemini-key"
if not os.environ.get("ANTHROPIC_API_KEY"):
    os.environ["ANTHROPIC_API_KEY"] = "test-anthropic-key"
if not os.environ.get("GLM_API_KEY"):
    os.environ["GLM_API_KEY"] = "test-glm-key"
if not os.environ.get("OPENROUTER_API_KEY"):
    os.environ["OPENROUTER_API_KEY"] = "test-openrouter-key"
# Default to SQLite unless explicitly opting into Postgres test runs.
if os.environ.get("USE_POSTGRES_TESTS") != "1":
    test_db_url = os.environ.get("TEST_DATABASE_URL", "")
    if test_db_url.startswith("postgresql"):
        os.environ["TEST_DATABASE_URL"] = "sqlite:///./test_focus_kraliki.db"
    main_db_url = os.environ.get("DATABASE_URL", "")
    if main_db_url.startswith("postgresql"):
        os.environ["DATABASE_URL"] = "sqlite:///./test_focus_kraliki.db"

from pytest_asyncio_compat import ensure_pytest_asyncio_compat  # type: ignore

ensure_pytest_asyncio_compat()

import pytest
import asyncio
from typing import Generator, AsyncGenerator, Optional
from types import SimpleNamespace
from httpx import AsyncClient, ASGITransport
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session
from fastapi.testclient import TestClient

from app.module import create_standalone_app
from app.core.database import Base, get_db
from app.core.security_v2 import get_password_hash, generate_id as generate_id_fn
from app.core.ed25519_auth import ed25519_auth

# Import all models so their tables are registered with Base.metadata
from app.models.user import User
from app.models.task import Task, Project  # Project is defined in task.py
from app.models.session import Session
from app.models.event import Event
from app.models.time_entry import TimeEntry
from app.models.voice_recording import VoiceRecording
from app.models.workflow_template import WorkflowTemplate
from app.models.ai_conversation import AIConversation
from app.models.shadow_profile import ShadowProfile
from app.models.item_type import ItemType
from app.models.knowledge_item import KnowledgeItem
from app.models.workspace import Workspace, WorkspaceMember
from app.models.command_history import CommandHistory
from app.models.agent_session import AgentSession
from app.models.file_search_document import FileSearchDocument
from app.models.file_search_store import FileSearchStore
from app.models.request_telemetry import RequestTelemetry
from app.models.comment import Comment
from app.models.activity import Activity


TEST_DATABASE_URL = os.environ.get("TEST_DATABASE_URL", "sqlite:///./test_focus_kraliki.db")


engine = create_engine(TEST_DATABASE_URL, pool_pre_ping=True)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="session")
def event_loop():
    """Create event loop for async tests."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session", autouse=True)
def setup_test_db():
    """
    Create all tables once for the entire test session.
    """
    # Clean up first
    if engine.url.drivername.startswith("postgresql"):
        with engine.connect() as conn:
            conn.execute(text("DROP SCHEMA IF EXISTS public CASCADE"))
            conn.execute(text("CREATE SCHEMA public"))
            conn.execute(text("GRANT ALL ON SCHEMA public TO public"))
            conn.commit()
    else:
        # For SQLite and others
        Base.metadata.drop_all(bind=engine)
    
    # Create all tables
    Base.metadata.create_all(bind=engine)
    yield
    # No cleanup at the end to allow inspection if needed, or add it back later

@pytest.fixture(scope="function")
def db() -> Generator[Session, None, None]:
    """
    Provide a database session wrapped in a transaction that rolls back after each test.
    This provides perfect isolation and is very fast.
    """
    connection = engine.connect()
    transaction = connection.begin()
    
    # Create a session bound to the connection
    session = TestingSessionLocal(bind=connection)
    
    yield session
    
    # Rollback everything at the end of the test
    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture(scope="function")
def app(db: Session):
    """
    Create FastAPI app with test database.

    Args:
        db: Test database session

    Returns:
        FastAPI app instance
    """
    app = create_standalone_app()

    # Override database dependency
    def override_get_db():
        try:
            yield db
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db

    return app


@pytest.fixture(scope="function")
def client(app) -> Generator[TestClient, None, None]:
    """
    Create test client for sync requests.

    Args:
        app: FastAPI app

    Yields:
        Test client
    """
    with TestClient(app) as c:
        yield c


@pytest.fixture(scope="function")
async def async_client(app) -> AsyncGenerator[AsyncClient, None]:
    """
    Create async client for async requests.

    Args:
        app: FastAPI app

    Yields:
        Async client
    """
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest.fixture(scope="function")
def test_user(db: Session) -> User:
    """
    Create test user in database.

    Args:
        db: Database session

    Returns:
        User object
    """
    import bcrypt

    password = bcrypt.hashpw(TEST_USER_PASSWORD.encode(), bcrypt.gensalt()).decode("utf-8")
    user = User(
        id=generate_id_fn(),
        email="test@example.com",
        username="testuser",
        firstName="Test",
        lastName="User",
        passwordHash=password,
        organizationId=generate_id_fn(),
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return user


@pytest.fixture
def generate_id():
    """Provide generate_id helper for tests that need unique IDs."""
    return generate_id_fn


@pytest.fixture(scope="function")
def test_user_2(db: Session) -> User:
    """
    Create a second test user for isolation checks.

    Args:
        db: Database session

    Returns:
        User object
    """
    import bcrypt

    password = bcrypt.hashpw(TEST_USER_PASSWORD.encode(), bcrypt.gensalt()).decode("utf-8")
    user = User(
        id=generate_id_fn(),
        email="test2@example.com",
        username="testuser2",
        firstName="Test",
        lastName="UserTwo",
        passwordHash=password,
        organizationId=generate_id_fn(),
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return user


@pytest.fixture(scope="function")
def auth_token(test_user: User) -> str:
    """
    Create valid Ed25519 JWT token for test user.

    Args:
        test_user: Test user

    Returns:
        JWT access token
    """
    return ed25519_auth.create_access_token(data={"sub": test_user.id})


@pytest.fixture(scope="function")
def auth_headers(auth_token: str) -> dict:
    """
    Create authorization headers for authenticated requests.

    Args:
        auth_token: JWT token

    Returns:
        Headers dictionary
    """
    return {"Authorization": f"Bearer {auth_token}"}


@pytest.fixture(scope="function")
def test_user_token(auth_token: str) -> str:
    """
    Backwards-compatible token fixture used by legacy tests.
    """
    return auth_token


@pytest.fixture(scope="function")
async def mock_event_publisher():
    """
    Mock event publisher for testing event publishing.

    Returns:
        Mock publisher that records published events
    """

    class MockEventPublisher:
        def __init__(self):
            self.published_events = []

        async def connect(self):
            pass

        async def disconnect(self):
            pass

        async def publish(
            self, event_type, data, organization_id, user_id=None, metadata=None, workspace_settings=None
        ):
            self.published_events.append(
                {
                    "type": event_type,
                    "data": data,
                    "organization_id": organization_id,
                    "user_id": user_id,
                    "metadata": metadata,
                }
            )

        async def publish_task_created(
            self,
            task_id: str,
            title: str,
            priority: str,
            organization_id: str,
            user_id: str,
            assignee_id: Optional[str] = None,
            project_id: Optional[str] = None,
            workspace_settings=None,
        ):
            await self.publish(
                event_type="task.created",
                data={
                    "task_id": task_id,
                    "title": title,
                    "priority": priority,
                    "assignee_id": assignee_id,
                    "project_id": project_id,
                },
                organization_id=organization_id,
                user_id=user_id,
            )

        async def publish_task_completed(
            self,
            task_id: str,
            title: str,
            organization_id: str,
            user_id: str,
            duration_minutes: Optional[int] = None,
            workspace_settings=None,
        ):
            await self.publish(
                event_type="task.completed",
                data={
                    "task_id": task_id,
                    "title": title,
                    "duration_minutes": duration_minutes,
                },
                organization_id=organization_id,
                user_id=user_id,
            )

    return MockEventPublisher()


@pytest.fixture(scope="function")
async def mock_token_blacklist():
    """
    Mock token blacklist for testing revocation.

    Returns:
        Mock blacklist that tracks revoked tokens
    """

    class MockTokenBlacklist:
        def __init__(self):
            self.revoked_tokens = set()
            self.revoked_users = set()

        async def connect(self):
            pass

        async def disconnect(self):
            pass

        async def revoke_token(self, token, exp):
            self.revoked_tokens.add(token)

        async def is_revoked(self, token):
            return token in self.revoked_tokens

        async def revoke_all_user_tokens(self, user_id):
            self.revoked_users.add(user_id)

        async def is_user_revoked(self, user_id):
            return user_id in self.revoked_users

    return MockTokenBlacklist()


@pytest.fixture(autouse=True)
def mock_ai_clients(monkeypatch):
    """
    Provide lightweight Anthropic/OpenAI clients so tests never hit real APIs.
    """

    class FakeAnthropicStream:
        def __init__(self):
            self.text_stream = ["hello ", "world"]

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            return False

    class FakeAnthropicMessages:
        def stream(self, *args, **kwargs):
            return FakeAnthropicStream()

    class FakeAnthropicClient:
        def __init__(self):
            self.messages = FakeAnthropicMessages()

    class FakeOpenAIStream(list):
        def __init__(self):
            chunk = SimpleNamespace(
                choices=[
                    SimpleNamespace(delta=SimpleNamespace(content="openai token "))
                ]
            )
            super().__init__([chunk])

    class FakeCompletions:
        def create(self, *args, **kwargs):
            return FakeOpenAIStream()

    class FakeOpenAIChat:
        def __init__(self):
            self.completions = FakeCompletions()

    class FakeOpenAIClient:
        def __init__(self):
            self.chat = FakeOpenAIChat()

    monkeypatch.setattr(
        "app.routers.ai_stream.get_claude_provider", lambda: FakeAnthropicClient()
    )
    monkeypatch.setattr(
        "app.routers.ai_stream.get_openai_provider", lambda: FakeOpenAIClient()
    )
    monkeypatch.setattr(
        "app.routers.assistant.get_anthropic_client", lambda: FakeAnthropicClient()
    )


@pytest.fixture(autouse=True)
def disable_rate_limiting():
    """Disable slowapi rate limiting during tests."""
    from app.middleware.rate_limit import limiter
    original_enabled = limiter.enabled
    limiter.enabled = False
    yield
    limiter.enabled = original_enabled
