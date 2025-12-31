"""
Time Entry Model
Database schema for time tracking on tasks
"""

from sqlalchemy import Column, String, DateTime, Integer, ForeignKey, Text, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base, JSONBCompat


class TimeEntry(Base):
    """
    Time tracking entry model for measuring time spent on tasks.

    Attributes:
        id: Primary key
        user_id: Foreign key to user who tracked time
        task_id: Foreign key to task being tracked
        project_id: Optional foreign key to project
        start_time: When timer started
        end_time: When timer stopped (null if running)
        duration_seconds: Total time in seconds (calculated on stop)
        description: Optional notes about what was done
        description_i18n: Multilingual notes
        billable: Whether time is billable (for client work)
        hourly_rate: Hourly rate if billable
        tags: Tags for categorizing time entries
        created_at: When entry was created
        updated_at: When entry was last updated
    """
    __tablename__ = "time_entries"

    id = Column(String, primary_key=True, index=True)
    user_id = Column(String, ForeignKey("user.id"), nullable=False)
    task_id = Column(String, ForeignKey("task.id"), nullable=True)
    project_id = Column(String, ForeignKey("project.id"), nullable=True)
    workspace_id = Column(String, ForeignKey("workspace.id"), nullable=True)

    # Timing
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=True)  # Null if timer is running
    duration_seconds = Column(Integer, nullable=True)  # Calculated on stop

    # Details
    description = Column(Text, nullable=True)
    description_i18n = Column(JSONBCompat, nullable=True)  # {"en": "Fixed bug", "cs": "Opravena chyba"}

    # Billing
    billable = Column(Boolean, default=False, nullable=False)
    hourly_rate = Column(Integer, nullable=True)  # In cents (e.g., 5000 = $50.00)

    # Categorization
    tags = Column(JSONBCompat, nullable=True)  # ["development", "bug-fix", "client-work"]

    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    user = relationship("User", back_populates="time_entries")
    task = relationship("Task", back_populates="time_entries")
    project = relationship("Project", back_populates="time_entries")
    workspace = relationship("Workspace", back_populates="time_entries")
