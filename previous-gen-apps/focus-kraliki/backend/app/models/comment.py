"""
Comment Model - Team collaboration on tasks/projects/knowledge items.
"""

from sqlalchemy import Column, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime

from app.core.database import Base


class Comment(Base):
    """Comment on any item (task, project, knowledge item)."""
    __tablename__ = "comment"

    id = Column(String, primary_key=True, index=True)
    content = Column(Text, nullable=False)

    # Polymorphic: can be on task, project, or knowledge item
    taskId = Column(String, ForeignKey("task.id"), nullable=True, index=True)
    projectId = Column(String, ForeignKey("project.id"), nullable=True, index=True)
    knowledgeItemId = Column(String, ForeignKey("knowledge_item.id"), nullable=True, index=True)

    # Author
    userId = Column(String, ForeignKey("user.id"), nullable=False)
    workspaceId = Column(String, ForeignKey("workspace.id"), nullable=True)

    # Mentions (JSON array of user IDs)
    mentions = Column(String, nullable=True)  # JSON array

    createdAt = Column(DateTime, default=datetime.utcnow, nullable=False)
    updatedAt = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", backref="comments")
    task = relationship("Task", backref="comments")
    project = relationship("Project", backref="comments")
