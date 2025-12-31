"""Shift management and performance tracking models."""

from datetime import UTC, datetime, time
from enum import Enum
from typing import Any

from pydantic import BaseModel
from sqlalchemy import (
    JSON,
    Boolean,
    Column,
    Date,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    Time,
)
from sqlalchemy.orm import relationship

from app.database import Base


class ShiftStatus(str, Enum):
    """Shift status enumeration."""
    SCHEDULED = "scheduled"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    NO_SHOW = "no_show"


class Shift(Base):
    """Shift model for agent scheduling."""

    __tablename__ = "shifts"

    id = Column(Integer, primary_key=True, index=True)
    agent_id = Column(Integer, ForeignKey("agent_profiles.id", ondelete="CASCADE"), nullable=False)
    team_id = Column(Integer, ForeignKey("teams.id"), nullable=True)

    # Schedule
    shift_date = Column(Date, nullable=False, index=True)
    start_time = Column(Time, nullable=False)
    end_time = Column(Time, nullable=False)
    timezone = Column(String(50), default="UTC", nullable=False)

    # Status
    status = Column(String(50), default=ShiftStatus.SCHEDULED, nullable=False)

    # Actual times (for tracking)
    actual_start_time = Column(DateTime, nullable=True)
    actual_end_time = Column(DateTime, nullable=True)
    clock_in_time = Column(DateTime, nullable=True)
    clock_out_time = Column(DateTime, nullable=True)

    # Break tracking
    break_duration_minutes = Column(Integer, default=0, nullable=False)
    actual_break_minutes = Column(Integer, default=0, nullable=False)

    # Configuration
    is_recurring = Column(Boolean, default=False, nullable=False)
    recurrence_pattern = Column(JSON, nullable=True)  # {"frequency": "weekly", "days": ["monday", "tuesday"]}

    # Notes
    notes = Column(Text, nullable=True)
    cancellation_reason = Column(Text, nullable=True)

    # Metadata
    custom_metadata = Column("metadata", JSON, default=dict, nullable=False)

    # Timestamps
    created_at = Column(DateTime, default=lambda: datetime.now(UTC), nullable=False)
    updated_at = Column(DateTime, default=lambda: datetime.now(UTC), onupdate=lambda: datetime.now(UTC), nullable=False)

    # Relationships
    agent = relationship("AgentProfile", back_populates="shifts")
    team = relationship("Team")

    def __repr__(self):
        return f"<Shift(id={self.id}, agent_id={self.agent_id}, date={self.shift_date})>"


class AgentPerformance(Base):
    """Agent performance tracking model."""

    __tablename__ = "agent_performance"

    id = Column(Integer, primary_key=True, index=True)
    agent_id = Column(Integer, ForeignKey("agent_profiles.id", ondelete="CASCADE"), nullable=False)
    team_id = Column(Integer, ForeignKey("teams.id"), nullable=True)

    # Time period
    period_date = Column(Date, nullable=False, index=True)
    period_type = Column(String(20), default="daily", nullable=False)  # daily, weekly, monthly

    # Call metrics
    total_calls = Column(Integer, default=0, nullable=False)
    answered_calls = Column(Integer, default=0, nullable=False)
    missed_calls = Column(Integer, default=0, nullable=False)
    outbound_calls = Column(Integer, default=0, nullable=False)
    inbound_calls = Column(Integer, default=0, nullable=False)

    # Time metrics (in seconds)
    total_talk_time = Column(Integer, default=0, nullable=False)
    total_hold_time = Column(Integer, default=0, nullable=False)
    total_wait_time = Column(Integer, default=0, nullable=False)
    total_after_call_work = Column(Integer, default=0, nullable=False)
    total_idle_time = Column(Integer, default=0, nullable=False)

    # Average times (in seconds)
    average_handle_time = Column(Integer, nullable=True)
    average_talk_time = Column(Integer, nullable=True)
    average_speed_to_answer = Column(Integer, nullable=True)

    # Quality metrics
    customer_satisfaction_score = Column(Float, nullable=True)  # CSAT 0-5
    net_promoter_score = Column(Float, nullable=True)  # NPS -100 to 100
    quality_score = Column(Float, nullable=True)  # QA score 0-100
    first_call_resolution_rate = Column(Float, nullable=True)  # FCR 0-1

    # Productivity metrics
    calls_per_hour = Column(Float, nullable=True)
    occupancy_rate = Column(Float, nullable=True)  # (talk + hold + ACW) / (total logged in time)
    utilization_rate = Column(Float, nullable=True)  # (talk time) / (total logged in time)

    # Schedule adherence
    scheduled_hours = Column(Float, default=0, nullable=False)
    actual_hours = Column(Float, default=0, nullable=False)
    adherence_percentage = Column(Float, nullable=True)

    # Disposition tracking
    dispositions = Column(JSON, default=dict, nullable=False)  # {"interested": 10, "not_interested": 5}

    # Metadata
    custom_metadata = Column("metadata", JSON, default=dict, nullable=False)

    # Timestamps
    created_at = Column(DateTime, default=lambda: datetime.now(UTC), nullable=False)
    updated_at = Column(DateTime, default=lambda: datetime.now(UTC), onupdate=lambda: datetime.now(UTC), nullable=False)

    # Relationships
    agent = relationship("AgentProfile", back_populates="performance_records")
    team = relationship("Team")

    def __repr__(self):
        return f"<AgentPerformance(agent_id={self.agent_id}, date={self.period_date})>"


class TeamPerformance(Base):
    """Team performance tracking model."""

    __tablename__ = "team_performance"

    id = Column(Integer, primary_key=True, index=True)
    team_id = Column(Integer, ForeignKey("teams.id", ondelete="CASCADE"), nullable=False)

    # Time period
    period_date = Column(Date, nullable=False, index=True)
    period_type = Column(String(20), default="daily", nullable=False)

    # Team metrics
    total_agents = Column(Integer, default=0, nullable=False)
    active_agents = Column(Integer, default=0, nullable=False)
    agents_on_call = Column(Integer, default=0, nullable=False)

    # Call metrics
    total_calls = Column(Integer, default=0, nullable=False)
    calls_answered = Column(Integer, default=0, nullable=False)
    calls_abandoned = Column(Integer, default=0, nullable=False)
    average_wait_time_seconds = Column(Integer, nullable=True)
    service_level_percentage = Column(Float, nullable=True)  # % calls answered within target

    # Quality metrics
    average_csat = Column(Float, nullable=True)
    average_quality_score = Column(Float, nullable=True)
    average_fcr_rate = Column(Float, nullable=True)

    # Productivity metrics
    total_handle_time_seconds = Column(Integer, default=0, nullable=False)
    average_handle_time_seconds = Column(Integer, nullable=True)
    occupancy_rate = Column(Float, nullable=True)

    # Metadata
    custom_metadata = Column("metadata", JSON, default=dict, nullable=False)

    # Timestamps
    created_at = Column(DateTime, default=lambda: datetime.now(UTC), nullable=False)
    updated_at = Column(DateTime, default=lambda: datetime.now(UTC), onupdate=lambda: datetime.now(UTC), nullable=False)

    # Relationships
    team = relationship("Team")

    def __repr__(self):
        return f"<TeamPerformance(team_id={self.team_id}, date={self.period_date})>"


# Pydantic models for API
class ShiftBase(BaseModel):
    """Base shift model."""
    shift_date: datetime
    start_time: time
    end_time: time
    timezone: str = "UTC"
    break_duration_minutes: int = 0
    is_recurring: bool = False
    recurrence_pattern: dict[str, Any] | None = None
    notes: str | None = None


class ShiftCreate(ShiftBase):
    """Shift creation model."""
    agent_id: int
    team_id: int | None = None


class ShiftUpdate(BaseModel):
    """Shift update model."""
    shift_date: datetime | None = None
    start_time: time | None = None
    end_time: time | None = None
    status: ShiftStatus | None = None
    actual_start_time: datetime | None = None
    actual_end_time: datetime | None = None
    clock_in_time: datetime | None = None
    clock_out_time: datetime | None = None
    actual_break_minutes: int | None = None
    notes: str | None = None
    cancellation_reason: str | None = None


class ShiftResponse(ShiftBase):
    """Shift response model."""
    id: int
    agent_id: int
    team_id: int | None = None
    status: ShiftStatus
    actual_start_time: datetime | None = None
    actual_end_time: datetime | None = None
    clock_in_time: datetime | None = None
    clock_out_time: datetime | None = None
    actual_break_minutes: int
    cancellation_reason: str | None = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class AgentPerformanceBase(BaseModel):
    """Base agent performance model."""
    period_date: datetime
    period_type: str = "daily"


class AgentPerformanceCreate(AgentPerformanceBase):
    """Agent performance creation model."""
    agent_id: int
    team_id: int | None = None


class AgentPerformanceResponse(AgentPerformanceBase):
    """Agent performance response model."""
    id: int
    agent_id: int
    team_id: int | None = None
    total_calls: int
    answered_calls: int
    missed_calls: int
    total_talk_time: int
    average_handle_time: int | None = None
    customer_satisfaction_score: float | None = None
    quality_score: float | None = None
    first_call_resolution_rate: float | None = None
    calls_per_hour: float | None = None
    occupancy_rate: float | None = None
    adherence_percentage: float | None = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class TeamPerformanceResponse(BaseModel):
    """Team performance response model."""
    id: int
    team_id: int
    period_date: datetime
    period_type: str
    total_agents: int
    active_agents: int
    total_calls: int
    calls_answered: int
    calls_abandoned: int
    average_wait_time_seconds: int | None = None
    service_level_percentage: float | None = None
    average_csat: float | None = None
    average_quality_score: float | None = None
    occupancy_rate: float | None = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ClockInRequest(BaseModel):
    """Clock in request model."""
    shift_id: int


class ClockOutRequest(BaseModel):
    """Clock out request model."""
    shift_id: int
    notes: str | None = None


class PerformanceMetrics(BaseModel):
    """Performance metrics aggregation model."""
    agent_id: int
    period_start: datetime
    period_end: datetime
    total_calls: int
    average_handle_time: float
    customer_satisfaction: float
    quality_score: float
    adherence_score: float
    productivity_score: float
