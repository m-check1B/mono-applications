"""Database configuration and session management."""
import logging
import os
from typing import AsyncGenerator, Optional

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine, AsyncEngine
from sqlalchemy.orm import DeclarativeBase

logger = logging.getLogger(__name__)

# Lazy engine/session creation - only initialize when actually needed
_engine: Optional[AsyncEngine] = None
_session_factory: Optional[async_sessionmaker] = None


def _get_database_url() -> Optional[str]:
    """Get database URL from environment, with test mode support."""
    # Allow override via TEST_DATABASE_URL for testing
    test_url = os.environ.get("TEST_DATABASE_URL")
    if test_url:
        return test_url

    db_url = os.environ.get("DATABASE_URL")
    if db_url:
        return db_url

    # Try to import from settings, but don't fail if settings can't load
    try:
        from app.core.config import settings
        return settings.database_url
    except Exception:
        return None


def get_engine() -> Optional[AsyncEngine]:
    """Get or create the async engine lazily."""
    global _engine
    if _engine is None:
        db_url = _get_database_url()
        if db_url:
            try:
                _engine = create_async_engine(
                    db_url,
                    pool_pre_ping=True,
                    echo=False,
                )
            except Exception as e:
                logger.warning(f"Could not create database engine: {e}")
    return _engine


def get_session_factory() -> Optional[async_sessionmaker]:
    """Get or create the session factory lazily."""
    global _session_factory
    if _session_factory is None:
        eng = get_engine()
        if eng is not None:
            _session_factory = async_sessionmaker(
                bind=eng,
                class_=AsyncSession,
                expire_on_commit=False,
                autocommit=False,
                autoflush=False,
            )
    return _session_factory


# Backward compatibility: These will be None if database not configured
engine = None  # Use get_engine() instead
AsyncSessionLocal = None  # Use get_session_factory() instead

class Base(DeclarativeBase):
    """Base class for SQLAlchemy models."""
    pass

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Dependency for getting async database sessions."""
    session_factory = get_session_factory()
    if session_factory is None:
        raise RuntimeError("Database not configured. Set DATABASE_URL environment variable.")
    async with session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def init_db():
    """Initialize the database (create tables)."""
    eng = get_engine()
    if eng is None:
        logger.warning("Database not configured, skipping initialization.")
        return
    try:
        async with eng.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("Database initialized successfully.")
    except Exception as e:
        logger.error(f"Error initializing database: {e}")
        # Don't raise here to allow bot to start even without DB if it's optional
