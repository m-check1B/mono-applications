"""
Calendar Event Model
Database schema for calendar events and Google Calendar integration
"""

from sqlalchemy import Column, String, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base, JSONBCompat


class Event(Base):
    """
    Calendar event model supporting both local and Google Calendar synced events.

    Attributes:
        id: Primary key
        user_id: Foreign key to user who owns the event
        title: Event title/summary
        description: Event description/notes
        title_i18n: Multilingual title ({"en": "Meeting", "cs": "Schůzka"})
        description_i18n: Multilingual description
        start_time: Event start datetime
        end_time: Event end datetime
        all_day: Whether event is all-day
        google_event_id: Google Calendar event ID (for sync)
        google_calendar_id: Which Google Calendar (primary, work, etc.)
        task_id: Optional link to task (task deadline → calendar event)
        location: Event location
        attendees: List of attendees (emails)
        color: Event color (hex code)
        reminder_minutes: Minutes before event to send reminder
        created_at: When event was created
        updated_at: When event was last updated
    """
    __tablename__ = "events"

    id = Column(String, primary_key=True, index=True)
    user_id = Column(String, ForeignKey("user.id"), nullable=False)

    # Event details
    title = Column(String, nullable=False)
    description = Column(String, nullable=True)
    title_i18n = Column(JSONBCompat, nullable=True)  # {"en": "Meeting", "cs": "Schůzka"}
    description_i18n = Column(JSONBCompat, nullable=True)

    # Timing
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=False)
    all_day = Column(Boolean, default=False, nullable=False)

    # Google Calendar sync
    google_event_id = Column(String, nullable=True, index=True)
    google_calendar_id = Column(String, nullable=True)  # "primary", "work@company.com", etc.

    # Task integration
    task_id = Column(String, ForeignKey("task.id"), nullable=True)

    # Additional details
    location = Column(String, nullable=True)
    attendees = Column(JSONBCompat, nullable=True)  # ["email1@example.com", "email2@example.com"]
    color = Column(String, nullable=True)  # Hex color code
    reminder_minutes = Column(String, nullable=True)  # "15,30,60" (multiple reminders)

    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    user = relationship("User", back_populates="events")
    task = relationship("Task", back_populates="events")
