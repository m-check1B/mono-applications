"""Pytest configuration and fixtures for backend tests.

Provides async database session fixture for integration tests.
Test isolation is achieved by clearing all tables before each test.

IMPORTANT: Environment variables MUST be set before any app imports to ensure
test isolation. This prevents tests from connecting to production databases.

Rate limiting is disabled by patching the limiter BEFORE importing app modules.
"""

import os
from functools import wraps

# Set test database URL BEFORE importing any app modules
# This ensures all modules use the test database, not production
os.environ["DATABASE_URL"] = "sqlite:///./test_db.sqlite"
os.environ["DATABASE_ASYNC_URL"] = "sqlite+aiosqlite:///./test_db.sqlite"
os.environ["REDIS_URL"] = "memory://"

# Disable rate limiting in tests by patching the limiter BEFORE any app imports
# This must happen before importing any app modules that use @limiter.limit()
def _create_noop_limiter():
    """Create a no-op limiter that doesn't require Redis."""
    from slowapi import Limiter
    from slowapi.util import get_remote_address

    def noop_limit(limit_string):
        """No-op limit decorator that just returns the function unchanged."""
        def decorator(func):
            return func
        return decorator

    # Create limiter with in-memory storage
    limiter = Limiter(key_func=get_remote_address, default_limits=[], enabled=False)
    limiter.limit = noop_limit
    return limiter

# Import and patch rate_limit module before any other app imports
import app.middleware.rate_limit as rate_limit_module
rate_limit_module.limiter = _create_noop_limiter()

import pytest
import asyncio
from typing import AsyncGenerator
from unittest.mock import patch, MagicMock
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.pool import StaticPool
from sqlalchemy import text

from app.database import Base


# Use in-memory SQLite for tests
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"
SYNC_TEST_DATABASE_URL = "sqlite:///./test_db.sqlite"


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
async def test_engine():
    """Create a test database engine."""
    engine = create_async_engine(
        TEST_DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        echo=False,
    )

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield engine

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    await engine.dispose()


async def _clear_all_tables(session: AsyncSession) -> None:
    """Clear all data from tables in correct order to handle FK constraints.

    This ensures test isolation by removing all data before each test.
    Tables are cleared in reverse dependency order.
    """
    # Get all tables from metadata, sorted to handle foreign key dependencies
    # We delete from tables with FKs first, then parent tables
    tables_to_clear = [
        # Child tables first (have foreign keys)
        "supervisor_interventions",
        "performance_alerts",
        "active_calls",
        "call_queue",
        "agent_performance",
        "team_performance",
        "shifts",
        "team_members",
        "agent_profiles",
        # Parent tables last
        "teams",
        "users",
        "companies",
        # Other tables
        "call_sessions",
        "call_transcripts",
        "call_recordings",
        "call_notes",
        "password_reset_tokens",
        "email_verification_tokens",
    ]

    # Disable FK checks for SQLite (makes deletion order less critical)
    await session.execute(text("PRAGMA foreign_keys = OFF"))

    for table_name in tables_to_clear:
        try:
            await session.execute(text(f"DELETE FROM {table_name}"))
        except Exception:
            # Table might not exist, skip it
            pass

    # Re-enable FK checks
    await session.execute(text("PRAGMA foreign_keys = ON"))
    await session.commit()


@pytest.fixture
async def db_session(test_engine) -> AsyncGenerator[AsyncSession, None]:
    """Create a test database session.

    Each test gets a clean database state by clearing all tables first.
    This ensures proper test isolation even when tests commit data.
    """
    async_session_factory = async_sessionmaker(
        test_engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autoflush=False,
    )

    async with async_session_factory() as session:
        # Clear all tables before each test for proper isolation
        await _clear_all_tables(session)
        yield session
        # Rollback any uncommitted changes after each test
        await session.rollback()


# ============ Synchronous fixtures for non-async tests ============

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session


@pytest.fixture(scope="session")
def sync_test_engine():
    """Create a synchronous test database engine for tests using sync SQLAlchemy."""
    engine = create_engine(
        SYNC_TEST_DATABASE_URL,
        connect_args={"check_same_thread": False},
        echo=False,
    )
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)
    engine.dispose()


@pytest.fixture
def sync_db_session(sync_test_engine) -> Session:
    """Create a synchronous database session for tests.

    Each test gets a clean database state by rolling back after each test.
    """
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=sync_test_engine)
    db = SessionLocal()
    try:
        yield db
    finally:
        db.rollback()
        db.close()


# Note: Rate limiter is already mocked at module load time (before app imports)
# See the _create_noop_limiter() function at the top of this file.
