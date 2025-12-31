import enum
from datetime import datetime

from sqlalchemy import (
    Column,
    String,
    DateTime,
    Float,
    JSON,
    ForeignKey,
    Text,
    Enum as SQLEnum,
)
from sqlalchemy.orm import relationship

from app.core.database import Base


class CommandSource(str, enum.Enum):
    """Source of the command execution"""
    ASSISTANT_VOICE = "assistant_voice"
    ASSISTANT_TEXT = "assistant_text"
    DETERMINISTIC_API = "deterministic_api"
    II_AGENT = "ii_agent"
    WORKFLOW = "workflow"
    DIRECT_API = "direct_api"


class CommandStatus(str, enum.Enum):
    """Status of command execution"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class CommandHistory(Base):
    """
    Command history tracking for all user actions in Focus by Kraliki.

    This table provides a unified timeline of user commands across:
    - Voice/text assistant interactions
    - Deterministic API calls (task creation, updates, etc.)
    - II-Agent orchestrated executions
    - Workflow executions

    It answers the question: "What did I work on last week?"
    """

    __tablename__ = "command_history"

    id = Column(String, primary_key=True)
    userId = Column(String, ForeignKey("user.id"), nullable=False, index=True)

    # Command classification
    source = Column(SQLEnum(CommandSource), nullable=False, index=True)
    command = Column(Text, nullable=False)  # The natural language or API command
    intent = Column(String, nullable=True, index=True)  # Parsed intent (create_task, update_task, etc.)

    # Execution details
    status = Column(SQLEnum(CommandStatus), nullable=False, default=CommandStatus.PENDING, index=True)
    startedAt = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)
    completedAt = Column(DateTime, nullable=True)
    durationMs = Column(Float, nullable=True)  # Execution duration in milliseconds

    # Context and results
    context = Column(JSON, nullable=True)  # Additional context (workspace, project, etc.)
    result = Column(JSON, nullable=True)  # Execution result (created task ID, updated fields, etc.)
    error = Column(JSON, nullable=True)  # Error details if failed

    # Relations to other entities
    telemetryId = Column(String, ForeignKey("request_telemetry.id"), nullable=True)  # Link to routing telemetry
    agentSessionId = Column(String, nullable=True)  # II-Agent session UUID if applicable
    conversationId = Column(String, ForeignKey("ai_conversation.id"), nullable=True)  # Link to AI conversation

    # Metadata
    model = Column(String, nullable=True)  # AI model used (if applicable)
    confidence = Column(Float, nullable=True)  # Confidence score (if applicable)
    command_metadata = Column(JSON, nullable=True)  # Additional metadata (renamed from 'metadata' to avoid SQLAlchemy reserved word conflict)

    # Relationships
    user = relationship("User", backref="command_history")
    telemetry = relationship("RequestTelemetry", backref="commands")
    conversation = relationship("AIConversation", backref="commands")
