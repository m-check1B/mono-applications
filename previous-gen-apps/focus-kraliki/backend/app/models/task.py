from sqlalchemy import (
    Column,
    String,
    Integer,
    Float,
    DateTime,
    JSON,
    ForeignKey,
    Enum as SQLEnum,
)
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from app.core.database import Base, JSONBCompat


class TaskStatus(str, enum.Enum):
    PENDING = "PENDING"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    ARCHIVED = "ARCHIVED"


class EnergyLevel(str, enum.Enum):
    low = "low"
    medium = "medium"
    high = "high"


class Task(Base):
    __tablename__ = "task"

    id = Column(String, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(String, nullable=True)
    title_i18n = Column(JSONBCompat, nullable=True)  # {'en': 'Task', 'cs': 'Úkol'}
    description_i18n = Column(
        JSONBCompat, nullable=True
    )  # {'en': 'Description', 'cs': 'Popis'}
    status = Column(SQLEnum(TaskStatus), default=TaskStatus.PENDING, nullable=False)
    priority = Column(Integer, default=1, nullable=False)
    dueDate = Column(DateTime, nullable=True)
    completedAt = Column(DateTime, nullable=True)
    estimatedMinutes = Column(Integer, nullable=True)
    actualMinutes = Column(Float, nullable=True)
    energyRequired = Column(
        SQLEnum(EnergyLevel), default=EnergyLevel.low, nullable=False
    )
    tags = Column(JSON, default=[], nullable=False)  # JSON for SQLite compatibility (was ARRAY)
    parentTaskId = Column(String, ForeignKey("task.id"), nullable=True)
    projectId = Column(String, ForeignKey("project.id"), nullable=True)
    userId = Column(String, ForeignKey("user.id"), nullable=True)
    workspaceId = Column(String, ForeignKey("workspace.id"), nullable=True)
    assignedUserId = Column(String, ForeignKey("user.id"), nullable=True)
    aiInsights = Column(JSON, nullable=True)
    urgencyScore = Column(Float, nullable=True)
    google_calendar_id = Column(String, nullable=True, index=True)  # For calendar sync
    linear_id = Column(String, nullable=True, index=True)  # Linear issue ID for sync
    createdAt = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    user = relationship("User", back_populates="tasks", foreign_keys=[userId])
    assignee = relationship("User", foreign_keys=[assignedUserId])
    project = relationship("Project", back_populates="tasks")
    workspace = relationship("Workspace", back_populates="tasks")
    parent = relationship("Task", remote_side=[id], backref="subtasks")
    events = relationship("Event", back_populates="task")
    time_entries = relationship("TimeEntry", back_populates="task")


class Project(Base):
    __tablename__ = "project"

    id = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    name_i18n = Column(JSONBCompat, nullable=True)  # {'en': 'Project', 'cs': 'Projekt'}
    description_i18n = Column(
        JSONBCompat, nullable=True
    )  # {'en': 'Description', 'cs': 'Popis'}
    color = Column(String, nullable=True)
    icon = Column(String, nullable=True)
    userId = Column(String, ForeignKey("user.id"), nullable=False)
    workspaceId = Column(String, ForeignKey("workspace.id"), nullable=True)
    createdAt = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    user = relationship("User", back_populates="projects")
    tasks = relationship("Task", back_populates="project")
    time_entries = relationship("TimeEntry", back_populates="project")
    workspace = relationship("Workspace", back_populates="projects")
