#!/usr/bin/env python3
"""
Initialize the Focus by Kraliki database.

This script creates all tables from SQLAlchemy models and stamps the database
to the latest migration version.
"""
import sys
from pathlib import Path

# Add backend directory to path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

from sqlalchemy import create_engine
from app.core.config import settings
from app.core.database import Base

# Import all models so they're registered with Base.metadata
from app.models.user import User
from app.models.item_type import ItemType
from app.models.knowledge_item import KnowledgeItem
from app.models.task import Task
from app.models.event import Event
from app.models.time_entry import TimeEntry
from app.models.ai_conversation import AIConversation
from app.models.session import Session
from app.models.shadow_profile import ShadowProfile
from app.models.voice_recording import VoiceRecording
from app.models.workflow_template import WorkflowTemplate

def init_database():
    """Create all database tables from models."""
    print(f"Connecting to database: {settings.DATABASE_URL}")

    engine = create_engine(settings.DATABASE_URL)

    print("Creating all tables...")
    Base.metadata.create_all(bind=engine)

    print("✅ Database tables created successfully!")
    print("\nNext steps:")
    print("1. Run: alembic stamp 008  # Stamp database to latest migration")
    print("2. Start the backend: uvicorn app.main:app --reload")

if __name__ == "__main__":
    init_database()
