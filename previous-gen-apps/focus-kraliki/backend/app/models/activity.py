"""
Activity Model - Team activity feed.
"""

from sqlalchemy import Column, String, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from datetime import datetime

from app.core.database import Base


class Activity(Base):
    """Activity log entry for team feed."""
    __tablename__ = "activity"

    id = Column(String, primary_key=True, index=True)

    # Activity type: task_created, task_completed, comment_added, etc.
    activityType = Column(String, nullable=False, index=True)

    # Actor
    userId = Column(String, ForeignKey("user.id"), nullable=False)
    workspaceId = Column(String, ForeignKey("workspace.id"), nullable=True, index=True)

    # Target (polymorphic)
    targetType = Column(String, nullable=False)  # task, project, knowledge, comment
    targetId = Column(String, nullable=False)
    targetTitle = Column(String, nullable=True)  # Denormalized for feed display

    # Additional context
    extra_data = Column(JSON, nullable=True)  # Extra data (old/new values, etc.)

    createdAt = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)

    # Relationships
    user = relationship("User", backref="activities")


# Activity types
ACTIVITY_TYPES = {
    "task_created": "created task",
    "task_updated": "updated task",
    "task_completed": "completed task",
    "task_assigned": "assigned task to",
    "project_created": "created project",
    "comment_added": "commented on",
    "knowledge_captured": "captured",
    "goal_set": "set goal",
    "member_joined": "joined workspace",
}
