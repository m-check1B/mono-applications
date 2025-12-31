"""Supervisor cockpit models for real-time monitoring and intervention."""

from datetime import UTC, datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel
from sqlalchemy import (
    JSON,
    Boolean,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import relationship

from app.database import Base
from app.models.call_state import CallDirection  # Reuse existing enum

# ===== Enums =====

class CallQueueStatus(str, Enum):
    """Call queue status."""
    WAITING = "waiting"
    ROUTING = "routing"
    ASSIGNED = "assigned"
    ABANDONED = "abandoned"
    ANSWERED = "answered"


class ActiveCallStatus(str, Enum):
    """Active call status for supervisor monitoring."""
    RINGING = "ringing"
    CONNECTED = "connected"
    ON_HOLD = "on_hold"
    TRANSFERRING = "transferring"
    COMPLETED = "completed"
    FAILED = "failed"


class InterventionType(str, Enum):
    """Type of supervisor intervention."""
    MONITOR = "monitor"  # Silent monitoring
    WHISPER = "whisper"  # Speak to agent only
    BARGE_IN = "barge_in"  # Join the call (3-way)
    TAKEOVER = "takeover"  # Take over the call from agent
    DISCONNECT = "disconnect"  # End the call


class AlertSeverity(str, Enum):
    """Alert severity level."""
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"


class AlertType(str, Enum):
    """Type of performance alert."""
    LONG_WAIT_TIME = "long_wait_time"
    HIGH_ABANDON_RATE = "high_abandon_rate"
    LOW_CSAT = "low_csat"
    AGENT_OFFLINE = "agent_offline"
    QUEUE_OVERFLOW = "queue_overflow"
    SLA_BREACH = "sla_breach"
    AGENT_IDLE = "agent_idle"
    CALL_DURATION_EXCEEDED = "call_duration_exceeded"


# ===== Database Models =====

class CallQueue(Base):
    """Calls waiting in queue to be answered."""
    __tablename__ = "call_queue"

    id = Column(Integer, primary_key=True, index=True)
    campaign_id = Column(Integer, ForeignKey("campaigns.id", ondelete="SET NULL"), nullable=True)
    team_id = Column(Integer, ForeignKey("teams.id", ondelete="SET NULL"), nullable=True)

    # Call information
    caller_phone = Column(String(50))
    caller_name = Column(String(200))
    direction = Column(String(20), default=CallDirection.INBOUND)
    priority = Column(Integer, default=0)  # Higher = more important

    # Queue status
    status = Column(String(50), default=CallQueueStatus.WAITING, index=True)
    queue_position = Column(Integer)
    estimated_wait_time = Column(Integer)  # Seconds

    # Timing
    queued_at = Column(DateTime, default=lambda: datetime.now(UTC), index=True)
    assigned_at = Column(DateTime, nullable=True)
    answered_at = Column(DateTime, nullable=True)
    abandoned_at = Column(DateTime, nullable=True)

    # Assignment
    assigned_agent_id = Column(Integer, ForeignKey("agent_profiles.id", ondelete="SET NULL"), nullable=True)

    # Skills/routing requirements
    required_skills = Column(JSON, default=list)
    required_language = Column(String(10), nullable=True)

    # Metadata
    caller_custom_metadata = Column("metadata", JSON, default=dict)  # Customer info, previous calls, etc.
    routing_attempts = Column(Integer, default=0)

    # Relationships
    assigned_agent = relationship("AgentProfile", foreign_keys=[assigned_agent_id])
    active_call = relationship("ActiveCall", back_populates="queue_entry", uselist=False)

    __table_args__ = (
        Index("ix_call_queue_status_priority", "status", "priority"),
        Index("ix_call_queue_team_status", "team_id", "status"),
    )


class ActiveCall(Base):
    """Currently active calls being handled by agents."""
    __tablename__ = "active_calls"

    id = Column(Integer, primary_key=True, index=True)

    # Call identification
    call_sid = Column(String(100), unique=True, index=True)  # External provider call ID
    queue_id = Column(Integer, ForeignKey("call_queue.id", ondelete="SET NULL"), nullable=True)
    campaign_id = Column(Integer, ForeignKey("campaigns.id", ondelete="SET NULL"), nullable=True)

    # Participants
    agent_id = Column(Integer, ForeignKey("agent_profiles.id", ondelete="CASCADE"), nullable=False, index=True)
    team_id = Column(Integer, ForeignKey("teams.id", ondelete="SET NULL"), nullable=True)

    # Call details
    direction = Column(String(20), default=CallDirection.INBOUND)
    caller_phone = Column(String(50))
    caller_name = Column(String(200))
    destination_phone = Column(String(50))

    # Status
    status = Column(String(50), default=ActiveCallStatus.RINGING, index=True)

    # Timing
    started_at = Column(DateTime, default=lambda: datetime.now(UTC), index=True)
    connected_at = Column(DateTime, nullable=True)
    ended_at = Column(DateTime, nullable=True)
    duration_seconds = Column(Integer, nullable=True)
    talk_time_seconds = Column(Integer, nullable=True)
    hold_time_seconds = Column(Integer, nullable=True)

    # Quality metrics
    is_on_hold = Column(Boolean, default=False)
    hold_count = Column(Integer, default=0)
    transfer_count = Column(Integer, default=0)

    # AI insights (real-time)
    current_sentiment = Column(String(20), nullable=True)  # positive, neutral, negative
    detected_intent = Column(String(100), nullable=True)
    detected_language = Column(String(10), nullable=True)
    transcription_url = Column(String(500), nullable=True)

    # Supervisor monitoring
    is_being_monitored = Column(Boolean, default=False)
    monitored_by_id = Column(String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)

    # Metadata
    call_custom_metadata = Column("metadata", JSON, default=dict)
    recording_url = Column(String(500), nullable=True)

    # Relationships
    agent = relationship("AgentProfile", foreign_keys=[agent_id])
    monitored_by = relationship("User", foreign_keys=[monitored_by_id])
    queue_entry = relationship("CallQueue", back_populates="active_call")
    interventions = relationship("SupervisorIntervention", back_populates="call")

    __table_args__ = (
        Index("ix_active_calls_agent_status", "agent_id", "status"),
        Index("ix_active_calls_team_started", "team_id", "started_at"),
    )


class SupervisorIntervention(Base):
    """Supervisor interventions on active calls."""
    __tablename__ = "supervisor_interventions"

    id = Column(Integer, primary_key=True, index=True)

    # References
    call_id = Column(Integer, ForeignKey("active_calls.id", ondelete="CASCADE"), nullable=False, index=True)
    supervisor_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    agent_id = Column(Integer, ForeignKey("agent_profiles.id", ondelete="SET NULL"), nullable=True)

    # Intervention details
    intervention_type = Column(String(50), nullable=False)
    started_at = Column(DateTime, default=lambda: datetime.now(UTC), index=True)
    ended_at = Column(DateTime, nullable=True)
    duration_seconds = Column(Integer, nullable=True)

    # Reason and notes
    reason = Column(String(500))
    notes = Column(Text, nullable=True)

    # Outcome
    was_successful = Column(Boolean, default=True)
    customer_notified = Column(Boolean, default=False)  # Was customer aware of intervention

    # Metadata
    intervention_custom_metadata = Column("metadata", JSON, default=dict)  # Relationships
    call = relationship("ActiveCall", back_populates="interventions")
    supervisor = relationship("User", foreign_keys=[supervisor_id])
    agent = relationship("AgentProfile", foreign_keys=[agent_id])

    __table_args__ = (
        Index("ix_interventions_supervisor_started", "supervisor_id", "started_at"),
    )


class SupervisorPerformanceAlert(Base):
    """Real-time performance alerts for supervisors."""
    __tablename__ = "supervisor_performance_alerts"

    id = Column(Integer, primary_key=True, index=True)

    # Alert details
    alert_type = Column(String(50), nullable=False, index=True)
    severity = Column(String(20), default=AlertSeverity.INFO, index=True)
    title = Column(String(200), nullable=False)
    message = Column(Text, nullable=False)

    # Context
    team_id = Column(Integer, ForeignKey("teams.id", ondelete="CASCADE"), nullable=True, index=True)
    agent_id = Column(Integer, ForeignKey("agent_profiles.id", ondelete="CASCADE"), nullable=True, index=True)
    call_id = Column(Integer, ForeignKey("active_calls.id", ondelete="CASCADE"), nullable=True)
    campaign_id = Column(Integer, ForeignKey("campaigns.id", ondelete="SET NULL"), nullable=True)

    # Timing
    created_at = Column(DateTime, default=lambda: datetime.now(UTC), index=True)
    acknowledged_at = Column(DateTime, nullable=True)
    resolved_at = Column(DateTime, nullable=True)

    # Status
    is_active = Column(Boolean, default=True, index=True)
    is_acknowledged = Column(Boolean, default=False)
    is_resolved = Column(Boolean, default=False)

    # Acknowledgment
    acknowledged_by_id = Column(String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    resolution_notes = Column(Text, nullable=True)

    # Threshold/trigger data
    threshold_value = Column(Float, nullable=True)
    actual_value = Column(Float, nullable=True)
    metric_name = Column(String(100), nullable=True)

    # Metadata
    alert_custom_metadata = Column("metadata", JSON, default=dict)  # Relationships
    team = relationship("Team", foreign_keys=[team_id])
    agent = relationship("AgentProfile", foreign_keys=[agent_id])
    acknowledged_by = relationship("User", foreign_keys=[acknowledged_by_id])

    __table_args__ = (
        Index("ix_alerts_active_severity", "is_active", "severity"),
        Index("ix_alerts_team_active", "team_id", "is_active"),
    )


# ===== Pydantic Schemas =====

# CallQueue Schemas
class CallQueueBase(BaseModel):
    caller_phone: str
    caller_name: str | None = None
    direction: CallDirection = CallDirection.INBOUND
    priority: int = 0
    campaign_id: int | None = None
    team_id: int | None = None
    required_skills: list[str] = []
    required_language: str | None = None


class CallQueueCreate(CallQueueBase):
    pass


class CallQueueUpdate(BaseModel):
    status: CallQueueStatus | None = None
    queue_position: int | None = None
    estimated_wait_time: int | None = None
    assigned_agent_id: int | None = None


class CallQueueResponse(CallQueueBase):
    id: int
    status: CallQueueStatus
    queue_position: int | None
    estimated_wait_time: int | None
    queued_at: datetime
    assigned_at: datetime | None
    answered_at: datetime | None
    abandoned_at: datetime | None
    assigned_agent_id: int | None
    routing_attempts: int

    class Config:
        from_attributes = True


# ActiveCall Schemas
class ActiveCallBase(BaseModel):
    call_sid: str
    agent_id: int
    direction: CallDirection = CallDirection.INBOUND
    caller_phone: str
    caller_name: str | None = None
    destination_phone: str | None = None
    campaign_id: int | None = None
    team_id: int | None = None
    queue_id: int | None = None


class ActiveCallCreate(ActiveCallBase):
    pass


class ActiveCallUpdate(BaseModel):
    status: ActiveCallStatus | None = None
    connected_at: datetime | None = None
    ended_at: datetime | None = None
    duration_seconds: int | None = None
    talk_time_seconds: int | None = None
    hold_time_seconds: int | None = None
    is_on_hold: bool | None = None
    current_sentiment: str | None = None
    detected_intent: str | None = None
    detected_language: str | None = None
    is_being_monitored: bool | None = None
    monitored_by_id: int | None = None


class ActiveCallResponse(ActiveCallBase):
    id: int
    status: ActiveCallStatus
    started_at: datetime
    connected_at: datetime | None
    ended_at: datetime | None
    duration_seconds: int | None
    talk_time_seconds: int | None
    hold_time_seconds: int | None
    is_on_hold: bool
    hold_count: int
    transfer_count: int
    current_sentiment: str | None
    detected_intent: str | None
    is_being_monitored: bool
    monitored_by_id: int | None
    call_metadata: dict[str, Any]

    class Config:
        from_attributes = True


# SupervisorIntervention Schemas
class SupervisorInterventionCreate(BaseModel):
    call_id: int
    intervention_type: InterventionType
    reason: str
    notes: str | None = None
    customer_notified: bool = False


class SupervisorInterventionUpdate(BaseModel):
    ended_at: datetime | None = None
    duration_seconds: int | None = None
    notes: str | None = None
    was_successful: bool | None = None


class SupervisorInterventionResponse(BaseModel):
    id: int
    call_id: int
    supervisor_id: str
    agent_id: int | None
    intervention_type: InterventionType
    started_at: datetime
    ended_at: datetime | None
    duration_seconds: int | None
    reason: str
    notes: str | None
    was_successful: bool
    customer_notified: bool

    class Config:
        from_attributes = True


# PerformanceAlert Schemas
class PerformanceAlertCreate(BaseModel):
    alert_type: AlertType
    severity: AlertSeverity
    title: str
    message: str
    team_id: int | None = None
    agent_id: int | None = None
    call_id: int | None = None
    campaign_id: int | None = None
    threshold_value: float | None = None
    actual_value: float | None = None
    metric_name: str | None = None
    alert_metadata: dict[str, Any] = {}


class PerformanceAlertUpdate(BaseModel):
    is_acknowledged: bool | None = None
    is_resolved: bool | None = None
    acknowledged_by_id: int | None = None
    resolution_notes: str | None = None


class PerformanceAlertResponse(BaseModel):
    id: int
    alert_type: AlertType
    severity: AlertSeverity
    title: str
    message: str
    team_id: int | None
    agent_id: int | None
    call_id: int | None
    campaign_id: int | None
    created_at: datetime
    acknowledged_at: datetime | None
    resolved_at: datetime | None
    is_active: bool
    is_acknowledged: bool
    is_resolved: bool
    acknowledged_by_id: int | None
    resolution_notes: str | None
    threshold_value: float | None
    actual_value: float | None
    metric_name: str | None
    alert_metadata: dict[str, Any]

    class Config:
        from_attributes = True


# Backward compatibility alias
PerformanceAlert = SupervisorPerformanceAlert
