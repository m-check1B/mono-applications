"""Call state database model for persistent telephony state management.

This module provides persistent storage for call state, replacing the in-memory
dictionaries with database-backed storage that survives server restarts.
"""

from datetime import UTC, datetime
from enum import Enum

from pydantic import BaseModel
from sqlalchemy import JSON, Column, DateTime, String
from sqlalchemy import Enum as SQLEnum

from app.database import Base


class CallStatus(str, Enum):
    """Call status enumeration for tracking call lifecycle."""
    INITIATED = "initiated"
    RINGING = "ringing"
    ANSWERED = "answered"
    ON_HOLD = "on_hold"
    TRANSFERRING = "transferring"
    COMPLETED = "completed"
    FAILED = "failed"


class CallDirection(str, Enum):
    """Call direction enumeration."""
    INBOUND = "inbound"
    OUTBOUND = "outbound"


class CallState(Base):
    """Database model for persistent call state tracking.

    This model stores the mapping between telephony call IDs (call_sid) and
    internal session IDs, along with additional call metadata and state information.

    Attributes:
        call_id: Primary key - the telephony provider's call identifier (e.g., Twilio CallSid)
        session_id: Internal session UUID linked to this call
        provider: Telephony provider name (twilio, telnyx)
        direction: Call direction (inbound/outbound)
        status: Current call status
        from_number: Calling party phone number
        to_number: Called party phone number
        metadata: Additional call metadata in JSON format
        created_at: Timestamp when call was created
        updated_at: Timestamp when call was last updated
        ended_at: Timestamp when call ended (null if still active)
    """

    __tablename__ = "call_states"

    call_id = Column(String(255), primary_key=True, index=True, comment="Telephony provider call identifier")
    session_id = Column(String(255), index=True, nullable=False, comment="Internal session UUID")
    provider = Column(String(50), nullable=False, comment="Telephony provider (twilio, telnyx)")
    direction = Column(String(20), nullable=False, comment="Call direction (inbound/outbound)")
    status = Column(SQLEnum(CallStatus), nullable=False, default=CallStatus.INITIATED, comment="Current call status")
    from_number = Column(String(50), nullable=True, comment="Calling party phone number")
    to_number = Column(String(50), nullable=True, comment="Called party phone number")
    call_custom_metadata = Column("metadata", JSON, default=dict, nullable=False, comment="Additional call metadata")
    created_at = Column(DateTime, default=lambda: datetime.now(UTC), nullable=False, comment="Call creation timestamp")
    updated_at = Column(DateTime, default=lambda: datetime.now(UTC), onupdate=lambda: datetime.now(UTC), nullable=False, comment="Last update timestamp")
    ended_at = Column(DateTime, nullable=True, comment="Call end timestamp")

    def __repr__(self):
        return f"<CallState(call_id={self.call_id}, session_id={self.session_id}, status={self.status})>"


# Pydantic models for API responses
class CallStateResponse(BaseModel):
    """Response model for call state."""
    call_id: str
    session_id: str
    provider: str
    direction: str
    status: CallStatus
    from_number: str | None = None
    to_number: str | None = None
    call_metadata: dict
    created_at: datetime
    updated_at: datetime
    ended_at: datetime | None = None

    class Config:
        from_attributes = True
