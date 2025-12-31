"""
Database configuration and connection management
"""

import os
from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session, sessionmaker

# Database configuration - use app settings
try:
    from .config.settings import get_settings
    settings = get_settings()
    DATABASE_URL = settings.database_url
except ImportError:
    # Fallback if settings aren't available
    DATABASE_URL = os.getenv(
        "DATABASE_URL",
        "sqlite:///./test.db"
    )

# Create engine with appropriate settings based on database type
# SQLite doesn't support connection pooling the same way as PostgreSQL
if DATABASE_URL.startswith("sqlite"):
    engine = create_engine(
        DATABASE_URL,
        connect_args={"check_same_thread": False},  # Required for SQLite with threads
        echo=os.getenv("DEBUG", "false").lower() == "true"
    )
else:
    # PostgreSQL with enhanced connection pooling
    engine = create_engine(
        DATABASE_URL,
        pool_size=10,           # Maximum connections in pool
        max_overflow=20,        # Maximum overflow connections
        pool_pre_ping=True,     # Verify connections before use
        pool_recycle=300,       # Recycle connections every 5 minutes
        pool_timeout=30,        # Connection timeout in seconds
        echo=os.getenv("DEBUG", "false").lower() == "true"  # SQL logging in debug mode
    )

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create base class for models
Base = declarative_base()


def get_db() -> Generator[Session]:
    """
    Dependency to get database session
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_tables():
    """
    Create all database tables
    """
    Base.metadata.create_all(bind=engine)


def drop_tables():
    """
    Drop all database tables (use with caution!)
    """
    Base.metadata.drop_all(bind=engine)


def check_database_health() -> dict:
    """
    Check database connection pool health

    Returns:
        dict: Database health metrics including pool status
    """
    try:
        pool = engine.pool
        return {
            "status": "healthy",
            "pool_size": pool.size(),
            "checked_out": pool.checkedout(),
            "overflow": pool.overflow(),
            "checked_in": pool.checkedin()
        }
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}
