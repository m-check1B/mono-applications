"""
Voice by Kraliki - Usage Model
Track API usage (minutes) for billing and limits.
"""

from datetime import UTC, datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.database import Base


class UsageRecord(Base):
    """Usage record for API calls (voice minutes)."""

    __tablename__ = "usage_records"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)

    # Type of service: voice_minutes, tokens, etc.
    service_type = Column(String(50), default="voice_minutes", nullable=False)

    # Quantity (for voice_minutes, this is duration in seconds)
    quantity = Column(Integer, default=0, nullable=False)

    # Reference to conversation or call
    reference_id = Column(String(100), nullable=True)

    # Timestamp
    timestamp = Column(DateTime, default=lambda: datetime.now(UTC), nullable=False)

    # Relationships
    user = relationship("User")
