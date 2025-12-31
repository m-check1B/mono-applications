"""
Database configuration and session management
SQLAlchemy 2.0 with async support
"""

from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base
from sqlalchemy.pool import NullPool
from sqlalchemy import text

from app.core.config import settings
from app.core.logger import get_logger

logger = get_logger(__name__)

# Create async engine
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,  # Log SQL queries in debug mode
    future=True,
    poolclass=NullPool if "sqlite" in settings.DATABASE_URL else None,
)

# Create async session factory
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)

# Base class for models
Base = declarative_base()


async def init_db() -> None:
    """Initialize database - create tables"""
    try:
        async with engine.begin() as conn:
            # In production, use Alembic migrations instead
            if settings.DEBUG:
                await conn.run_sync(Base.metadata.create_all)
                logger.info("Database tables created (debug mode)")
            else:
                # Just verify connection in production
                await conn.execute(text("SELECT 1"))
                logger.info("Database connection verified")
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        raise


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency for getting database sessions
    Usage: db: AsyncSession = Depends(get_db)
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def close_db() -> None:
    """Close database connection pool"""
    await engine.dispose()
    logger.info("Database connections closed")
