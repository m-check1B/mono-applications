"""
User Progress Model
Tracks which lessons a user has completed
"""

from datetime import datetime, timezone
from sqlalchemy import Column, String, DateTime, JSON
from sqlalchemy.dialects.sqlite import JSON as SQLiteJSON

from app.core.database import Base


def utcnow():
    return datetime.now(timezone.utc)


class UserProgress(Base):
    """Track user progress through courses."""

    __tablename__ = "user_progress"

    # For now, use a simple user_id (will integrate with Zitadel SSO later)
    user_id = Column(String, primary_key=True)
    course_slug = Column(String, primary_key=True)

    # List of completed lesson IDs
    completed_lessons = Column(JSON, default=list)

    # Current lesson ID
    current_lesson = Column(String, nullable=True)

    # Timestamps
    started_at = Column(DateTime, default=utcnow)
    last_activity = Column(DateTime, default=utcnow, onupdate=utcnow)
    completed_at = Column(DateTime, nullable=True)

    def __repr__(self):
        return f"<UserProgress user={self.user_id} course={self.course_slug}>"
