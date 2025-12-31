"""
Agent Session Model - Tracks II-Agent execution sessions
"""

from datetime import datetime
import enum

from sqlalchemy import (
    Column,
    String,
    DateTime,
    JSON,
    ForeignKey,
    Enum as SQLEnum,
    Integer,
    Float,
    Text,
)
from sqlalchemy.orm import relationship

from app.core.database import Base


class AgentSessionStatus(str, enum.Enum):
    """Status of an II-Agent session."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class AgentSessionEventType(str, enum.Enum):
    """Types of events during II-Agent execution."""
    STARTED = "started"
    TOOL_CALL = "tool_call"
    PROGRESS_UPDATE = "progress_update"
    ERROR = "error"
    COMPLETED = "completed"


class AgentSession(Base):
    """
    Represents an II-Agent execution session.

    This model tracks agent sessions minted from the Focus by Kraliki backend,
    capturing the goals, context, execution state, and telemetry data.
    """

    __tablename__ = "agent_session"

    id = Column(String, primary_key=True)
    userId = Column(String, ForeignKey("user.id"), nullable=False, index=True)
    telemetryId = Column(String, ForeignKey("request_telemetry.id"), nullable=True, index=True)

    # Session metadata
    sessionUuid = Column(String, unique=True, nullable=False, index=True)
    status = Column(SQLEnum(AgentSessionStatus), nullable=False, default=AgentSessionStatus.PENDING)

    # Goals and context
    goal = Column(Text, nullable=False)  # Natural language goal
    structuredGoal = Column(JSON, nullable=True)  # Parsed goal with steps
    context = Column(JSON, nullable=True)  # User context (tasks, projects, etc.)
    escalationReason = Column(JSON, nullable=True)  # Why was this escalated to agent

    # Execution tracking
    toolCallCount = Column(Integer, default=0, nullable=False)
    lastToolCall = Column(String, nullable=True)
    lastToolCallAt = Column(DateTime, nullable=True)
    progressPercent = Column(Float, nullable=True)
    currentStep = Column(String, nullable=True)

    # Results
    result = Column(JSON, nullable=True)  # Final result from agent
    errorMessage = Column(Text, nullable=True)

    # Timestamps
    startedAt = Column(DateTime, nullable=True)
    completedAt = Column(DateTime, nullable=True)
    createdAt = Column(DateTime, default=datetime.utcnow, nullable=False)
    updatedAt = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    user = relationship("User", backref="agent_sessions")
    telemetry = relationship("RequestTelemetry", backref="agent_sessions")
    events = relationship("AgentSessionEvent", back_populates="session", cascade="all, delete-orphan")


class AgentSessionEvent(Base):
    """
    Tracks individual events during II-Agent execution.

    This captures tool calls, progress updates, errors, and other
    execution events for observability and debugging.
    """

    __tablename__ = "agent_session_event"

    id = Column(String, primary_key=True)
    sessionId = Column(String, ForeignKey("agent_session.id"), nullable=False, index=True)

    # Event details
    eventType = Column(SQLEnum(AgentSessionEventType), nullable=False, index=True)
    eventData = Column(JSON, nullable=True)  # Event-specific payload

    # Tool call tracking (when eventType = TOOL_CALL)
    toolName = Column(String, nullable=True, index=True)
    toolInput = Column(JSON, nullable=True)
    toolOutput = Column(JSON, nullable=True)
    toolError = Column(Text, nullable=True)
    toolDurationMs = Column(Integer, nullable=True)

    # Timestamps
    createdAt = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    session = relationship("AgentSession", back_populates="events")
