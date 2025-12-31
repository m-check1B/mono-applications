"""pytest fixtures for Voice by Kraliki tests"""

import pytest
import asyncio
from typing import AsyncGenerator
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.pool import NullPool

from app.core import database as db
from app.core.database import Base
from app.core.config import settings
from app.main import app
from app.models.user import User, UserRole, UserStatus, AuthProvider
from app.services.auth_service import AuthService

# Test database URL (use separate test database)
TEST_DATABASE_URL = settings.DATABASE_URL.replace("/cc_lite", "/cc_lite_test")


@pytest.fixture(scope="session")
def event_loop():
    """Create event loop for async tests"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
async def engine():
    """Create test database engine"""
    engine = create_async_engine(
        TEST_DATABASE_URL,
        echo=True,
        poolclass=NullPool,
    )

    # Rewire application database layer to use the test engine/session
    db.engine = engine
    db.AsyncSessionLocal = async_sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield engine

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    await engine.dispose()


@pytest.fixture
async def db_session(engine) -> AsyncGenerator[AsyncSession, None]:
    """Create a fresh database session for each test"""
    async with db.AsyncSessionLocal() as session:
        yield session
        await session.rollback()


@pytest.fixture
async def async_client(engine) -> AsyncGenerator[AsyncClient, None]:
    """Create async HTTP client for testing"""
    async def _override_db():
        async with db.AsyncSessionLocal() as session:
            try:
                yield session
            finally:
                await session.rollback()

    app.dependency_overrides[db.get_db] = _override_db

    # Seed a default user for login tests
    async with db.AsyncSessionLocal() as session:
        result = await session.execute(
            select(User).where(User.email == "agent@test.com")
        )
        if not result.scalar_one_or_none():
            user = User(
                id="test-agent",
                email="agent@test.com",
                username="agent",
                first_name="Agent",
                last_name="Tester",
                password_hash=AuthService.hash_password("password123"),
                role=UserRole.AGENT,
                status=UserStatus.ACTIVE,
                auth_provider=AuthProvider.LOCAL,
                email_verified=True,
                organization_id="test-org",
            )
            user.skills = []
            session.add(user)
            await session.commit()

    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client

    app.dependency_overrides.pop(db.get_db, None)


@pytest.fixture(autouse=True)
def mock_password_hash(monkeypatch):
    """Stub password hashing to avoid bcrypt backend dependency during tests."""

    def _hash(password: str) -> str:
        return f"test-hash:{password}"

    def _verify(plain: str, hashed: str) -> bool:
        return hashed == f"test-hash:{plain}"

    monkeypatch.setattr(AuthService, "hash_password", staticmethod(_hash))
    monkeypatch.setattr(AuthService, "verify_password", staticmethod(_verify))

    yield


@pytest.fixture
def auth_headers(access_token: str) -> dict:
    """Create authorization headers with token"""
    return {"Authorization": f"Bearer {access_token}"}


# Sample test data fixtures
@pytest.fixture
def sample_user_data():
    """Sample user creation data"""
    return {
        "email": "test@example.com",
        "password": "TestPassword123!",
        "first_name": "Test",
        "last_name": "User",
        "role": "AGENT"
    }


@pytest.fixture
def sample_call_data():
    """Sample call creation data"""
    return {
        "from_number": "+1234567890",
        "to_number": "+0987654321",
        "direction": "OUTBOUND"
    }
