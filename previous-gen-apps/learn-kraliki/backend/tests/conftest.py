"""
Test configuration and fixtures for Learn by Kraliki
"""

import pytest
import asyncio
from typing import AsyncGenerator
from pathlib import Path
import tempfile
import shutil
import json

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.database import Base, get_db
from app.main import app
from app.services.course_service import CourseService
from app.core.config import settings


# Test database URL (in-memory SQLite)
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@pytest.fixture(scope="session")
def event_loop():
    """Create event loop for async tests."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="function")
async def test_engine():
    """Create test database engine."""
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


@pytest.fixture(scope="function")
async def test_db(test_engine) -> AsyncGenerator[AsyncSession, None]:
    """Create test database session."""
    async_session_maker = async_sessionmaker(
        test_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )

    async with async_session_maker() as session:
        yield session


@pytest.fixture(scope="function")
async def client(test_db):
    """Create test client with overridden database dependency."""
    from app.main import app

    async def override_get_db():
        yield test_db

    app.dependency_overrides[get_db] = override_get_db

    from fastapi.testclient import TestClient

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()


@pytest.fixture(scope="function")
def temp_content_dir():
    """Create temporary content directory with test courses."""
    temp_dir = tempfile.mkdtemp()

    # Create test course 1
    course1_dir = Path(temp_dir) / "getting-started"
    course1_dir.mkdir()

    course1_metadata = {
        "title": "Getting Started",
        "description": "Introduction to AI",
        "level": "beginner",
        "duration_minutes": 30,
        "is_free": True,
        "lessons": ["01-introduction.md", "02-basics.md"],
    }

    with open(course1_dir / "course.json", "w") as f:
        json.dump(course1_metadata, f)

    with open(course1_dir / "01-introduction.md", "w") as f:
        f.write("# Introduction\n\nWelcome to the course!")

    with open(course1_dir / "02-basics.md", "w") as f:
        f.write("# Basics\n\nLet's learn the basics.")

    # Create test course 2
    course2_dir = Path(temp_dir) / "ai-fundamentals"
    course2_dir.mkdir()

    course2_metadata = {
        "title": "AI Fundamentals",
        "description": "Deep dive into AI",
        "level": "intermediate",
        "duration_minutes": 60,
        "is_free": False,
        "lessons": ["01-neural-networks.md"],
    }

    with open(course2_dir / "course.json", "w") as f:
        json.dump(course2_metadata, f)

    with open(course2_dir / "01-neural-networks.md", "w") as f:
        f.write("# Neural Networks\n\nDeep learning basics.")

    # Override settings
    original_content_dir = settings.content_dir
    settings.content_dir = temp_dir

    yield temp_dir

    # Cleanup
    settings.content_dir = original_content_dir
    shutil.rmtree(temp_dir)


@pytest.fixture
def temp_content_dir_with_progress(temp_content_dir):
    """Content dir fixture with course service reloaded."""
    # Reload course service with new content dir
    from app.services.course_service import course_service

    # Force reload of content dir
    course_service.__init__()

    yield temp_content_dir


@pytest.fixture
def test_user_id():
    """Test user ID."""
    return "test-user-123"
