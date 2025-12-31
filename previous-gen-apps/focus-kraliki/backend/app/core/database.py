from sqlalchemy import create_engine, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.types import TypeDecorator
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)


class JSONBCompat(TypeDecorator):
    """
    A JSONB-compatible type that falls back to JSON for SQLite.
    Uses PostgreSQL JSONB when available, plain JSON otherwise.
    """
    impl = JSON
    cache_ok = True

    def load_dialect_impl(self, dialect):
        if dialect.name == 'postgresql':
            from sqlalchemy.dialects.postgresql import JSONB
            return dialect.type_descriptor(JSONB())
        return dialect.type_descriptor(JSON())

if settings.DATABASE_URL.strip().lower().startswith("sqlite"):
    engine = create_engine(
        settings.DATABASE_URL,
        connect_args={"check_same_thread": False}
    )
else:
    engine = create_engine(
        settings.DATABASE_URL,
        pool_pre_ping=True,
        pool_size=10,
        max_overflow=20
    )

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    """Database dependency for FastAPI routes with error handling"""
    db = SessionLocal()
    try:
        yield db
    except SQLAlchemyError as e:
        logger.error(f"Database error occurred: {e}")
        db.rollback()
        raise
    except Exception as e:
        logger.error(f"Unexpected error in database session: {e}")
        db.rollback()
        raise
    finally:
        try:
            db.close()
        except Exception as e:
            logger.error(f"Error closing database session: {e}")
