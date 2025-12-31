"""
Speak by Kraliki - Usage Model
Track API usage (minutes) for billing and limits.
"""

import uuid
from datetime import datetime
from sqlalchemy import String, DateTime, Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID

from app.core.database import Base


class UsageRecord(Base):
    """Usage record for API calls (voice minutes)."""

    __tablename__ = "vop_usage_records"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )
    company_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("companies.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    
    # Type of service: voice_minutes, tokens, etc.
    service_type: Mapped[str] = mapped_column(String(50), default="voice_minutes")
    
    # Quantity (for voice_minutes, this is duration in seconds)
    quantity: Mapped[int] = mapped_column(Integer, default=0)
    
    # Reference to conversation or call
    reference_id: Mapped[str | None] = mapped_column(String(100))
    
    # Timestamp
    timestamp: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Relationships
    company = relationship("Company")
