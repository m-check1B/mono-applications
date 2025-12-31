import enum
from datetime import datetime

from sqlalchemy import (
    Column,
    String,
    DateTime,
    Float,
    Integer,
    JSON,
    ForeignKey,
    Enum as SQLEnum,
)
from sqlalchemy.orm import relationship

from app.core.database import Base


class TelemetrySource(str, enum.Enum):
    ENHANCE_INPUT = "enhance_input"
    ORCHESTRATE_TASK = "orchestrate_task"


class TelemetryRoute(str, enum.Enum):
    UNKNOWN = "unknown"
    DETERMINISTIC = "deterministic"
    ORCHESTRATED = "orchestrated"


class WorkflowDecisionStatus(str, enum.Enum):
    APPROVED = "approved"
    REVISE = "revise"
    REJECTED = "rejected"


class RequestTelemetry(Base):
    """Telemetry for hybrid routing decisions."""

    __tablename__ = "request_telemetry"

    id = Column(String, primary_key=True)
    userId = Column(String, ForeignKey("user.id"), nullable=False, index=True)
    source = Column(SQLEnum(TelemetrySource), nullable=False)
    intent = Column(String, nullable=True)
    detectedType = Column(String, nullable=True)
    confidence = Column(Float, nullable=True)
    workflowSteps = Column(Integer, nullable=True)
    route = Column(SQLEnum(TelemetryRoute), nullable=False, default=TelemetryRoute.UNKNOWN)
    escalationReason = Column(JSON, nullable=True)
    details = Column(JSON, nullable=True)
    decisionStatus = Column(SQLEnum(WorkflowDecisionStatus), nullable=True)
    decisionNotes = Column(JSON, nullable=True)
    decisionAt = Column(DateTime, nullable=True)
    createdAt = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", backref="request_telemetry")
