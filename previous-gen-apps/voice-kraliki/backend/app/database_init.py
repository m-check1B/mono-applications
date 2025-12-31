"""Database initialization and migration utilities.

This module provides utilities for initializing the database schema
and running migrations for the Operator Demo 2026 application.
"""

import logging
from typing import Any

from sqlalchemy import inspect, text

from app.database import Base, SessionLocal, engine

logger = logging.getLogger(__name__)


def check_table_exists(table_name: str) -> bool:
    """Check if a table exists in the database.

    Args:
        table_name: Name of the table to check

    Returns:
        bool: True if table exists, False otherwise
    """
    inspector = inspect(engine)
    return table_name in inspector.get_table_names()


def get_database_status() -> dict[str, Any]:
    """Get current database status including existing tables.

    Returns:
        dict: Database status information
    """
    try:
        inspector = inspect(engine)
        existing_tables = inspector.get_table_names()

        expected_tables = [
            "users",
            "call_sessions",
            "session_messages",
            "session_analytics",
            "provider_configs",
            "provider_health",
            "campaigns",
            "campaign_scripts",
            "call_states",  # New table
            "scenarios",
            "scenario_nodes",
            "scenario_options",
            "usage_records",
        ]

        missing_tables = [t for t in expected_tables if t not in existing_tables]

        return {
            "status": "healthy" if not missing_tables else "missing_tables",
            "existing_tables": existing_tables,
            "expected_tables": expected_tables,
            "missing_tables": missing_tables,
            "database_url": str(engine.url).split("@")[-1] if "@" in str(engine.url) else str(engine.url),
        }
    except Exception as exc:
        logger.error("Failed to get database status: %s", exc)
        return {
            "status": "error",
            "error": str(exc),
        }


def create_all_tables():
    """Create all database tables defined in the models.

    This is a simple migration approach that creates any missing tables.
    Existing tables are not modified.
    """
    try:
        # Import all models to ensure they're registered with Base
        # Note: Import models individually to avoid relationship issues

        # Import CallSession separately to handle its relationships
        try:
            pass
        except Exception as exc:
            logger.warning("Could not import CallSession with relationships: %s", exc)
            # Continue anyway - CallState doesn't depend on CallSession

        # Create all tables that don't exist
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created/verified successfully")

        # Log status
        status = get_database_status()
        logger.info("Database status: %s", status)

        return True
    except Exception as exc:
        logger.error("Failed to create database tables: %s", exc)
        return False


def initialize_database():
    """Initialize the database with tables and initial data.

    This function:
    1. Creates all tables if they don't exist
    2. Verifies database connectivity
    3. Logs the database status

    Returns:
        bool: True if initialization was successful
    """
    logger.info("Initializing database...")

    try:
        # Test database connectivity
        db = SessionLocal()
        try:
            db.execute(text("SELECT 1"))
            logger.info("Database connection verified")
        finally:
            db.close()

        # Create tables
        if not create_all_tables():
            return False

        # Get and log final status
        status = get_database_status()
        if status["status"] == "healthy":
            logger.info("Database initialization completed successfully")
            logger.info("Existing tables: %s", ", ".join(status["existing_tables"]))
        elif status["status"] == "missing_tables":
            logger.warning("Database initialization completed with missing tables: %s", status["missing_tables"])
        else:
            logger.error("Database initialization failed: %s", status.get("error"))
            return False

        return True

    except Exception as exc:
        logger.error("Database initialization failed: %s", exc)
        return False


def migrate_call_states():
    """Migrate call states table if needed.

    This function handles any specific migrations needed for the call_states table,
    such as adding new columns or updating existing data.

    Returns:
        bool: True if migration was successful
    """
    try:
        # Check if call_states table exists
        if not check_table_exists("call_states"):
            logger.info("call_states table doesn't exist yet, will be created")
            return True

        # Add any specific migration logic here
        # For example, adding new columns, updating data, etc.

        logger.info("call_states table migration completed")
        return True

    except Exception as exc:
        logger.error("Failed to migrate call_states table: %s", exc)
        return False


def drop_all_tables():
    """Drop all database tables.

    WARNING: This will delete all data! Use only for development/testing.

    Returns:
        bool: True if successful
    """
    try:
        Base.metadata.drop_all(bind=engine)
        logger.warning("All database tables dropped")
        return True
    except Exception as exc:
        logger.error("Failed to drop database tables: %s", exc)
        return False


if __name__ == "__main__":
    # Configure logging for standalone execution
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    # Initialize database
    success = initialize_database()

    if success:
        logger.info("✓ Database initialized successfully")
        status = get_database_status()
        logger.info("Database Status:")
        logger.info("  Status: %s", status['status'])
        logger.info("  Tables: %d", len(status['existing_tables']))
        for table in sorted(status['existing_tables']):
            logger.debug("    - %s", table)
        if status.get('missing_tables'):
            logger.warning("  Missing tables: %s", ', '.join(status['missing_tables']))
    else:
        logger.error("✗ Database initialization failed")
        exit(1)
