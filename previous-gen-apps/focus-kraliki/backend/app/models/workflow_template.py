from sqlalchemy import Column, String, Integer, DateTime, JSON, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base

class WorkflowTemplate(Base):
    __tablename__ = "workflow_template"

    id = Column(String, primary_key=True, index=True)
    userId = Column(String, ForeignKey("user.id"), nullable=True)  # null = system template

    # Template info
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    category = Column(String, nullable=True)  # productivity, development, etc.
    icon = Column(String, nullable=True)

    # Workflow definition
    steps = Column(JSON, nullable=False)  # Array of workflow steps
    """
    Example steps:
    [
        {
            "step": 1,
            "action": "Create outline",
            "estimatedMinutes": 15,
            "dependencies": [],
            "type": "manual"
        },
        {
            "step": 2,
            "action": "Write first draft",
            "estimatedMinutes": 45,
            "dependencies": [1],
            "type": "manual"
        }
    ]
    """

    # Configuration
    totalEstimatedMinutes = Column(Integer, nullable=True)
    tags = Column(JSON, default=[], nullable=False)  # JSON for SQLite compatibility (was ARRAY)
    isPublic = Column(Boolean, default=False, nullable=False)
    isSystem = Column(Boolean, default=False, nullable=False)

    # Usage stats
    usageCount = Column(Integer, default=0, nullable=False)

    # Metadata
    template_metadata = Column(JSON, nullable=True)

    createdAt = Column(DateTime, default=datetime.utcnow, nullable=False)
    updatedAt = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    user = relationship("User", back_populates="workflow_templates")
