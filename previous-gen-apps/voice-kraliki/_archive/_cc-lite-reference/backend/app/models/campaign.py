"""Campaign models - SQLAlchemy 2.0"""

from datetime import datetime
from typing import Optional
import enum
from sqlalchemy import String, DateTime, JSON, Boolean, ForeignKey, Enum as SQLEnum, Float, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class CampaignType(str, enum.Enum):
    """Campaign types"""
    INBOUND = "INBOUND"
    OUTBOUND = "OUTBOUND"
    TRANSFER = "TRANSFER"
    ESCALATION = "ESCALATION"


class Campaign(Base):
    """Campaign model"""

    __tablename__ = "campaigns"

    id: Mapped[str] = mapped_column(String(30), primary_key=True)
    name: Mapped[str] = mapped_column(String(255))
    description: Mapped[Optional[str]] = mapped_column(String(1000), nullable=True)
    type: Mapped[CampaignType] = mapped_column(SQLEnum(CampaignType))
    language: Mapped[str] = mapped_column(String(10), default="en")
    version: Mapped[str] = mapped_column(String(20), default="1.0.0")
    active: Mapped[bool] = mapped_column(Boolean, default=False)
    organization_id: Mapped[str] = mapped_column(String(30), ForeignKey("organizations.id", ondelete="CASCADE"))

    # JSON fields
    instructions: Mapped[dict] = mapped_column(JSON)  # Campaign script and instructions
    tools: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)  # Available tools
    voice: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)  # Voice settings
    analytics: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)  # Analytics config
    metadata_payload: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)  # Additional metadata

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    # organization: Mapped["Organization"] = relationship(back_populates="campaigns")
    # sessions: Mapped[list["ContactSession"]] = relationship(back_populates="campaign")
    # metrics: Mapped["CampaignMetric"] = relationship(back_populates="campaign", uselist=False)
    # calls: Mapped[list["Call"]] = relationship(back_populates="campaign")
    # contacts: Mapped[list["Contact"]] = relationship(back_populates="campaign")

    def __repr__(self) -> str:
        return f"<Campaign {self.name} ({self.type})>"


class CampaignMetric(Base):
    """Campaign metrics model"""

    __tablename__ = "campaign_metrics"

    id: Mapped[str] = mapped_column(String(30), primary_key=True)
    campaign_id: Mapped[str] = mapped_column(String(30), ForeignKey("campaigns.id", ondelete="CASCADE"), unique=True)
    calls_handled: Mapped[int] = mapped_column(Integer, default=0)
    successful_completions: Mapped[int] = mapped_column(Integer, default=0)
    average_handle_time: Mapped[float] = mapped_column(Float, default=0.0)
    customer_satisfaction: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    tools_used: Mapped[dict] = mapped_column(JSON, default=dict)
    error_rate: Mapped[float] = mapped_column(Float, default=0.0)
    last_used: Mapped[datetime] = mapped_column(DateTime)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    # campaign: Mapped["Campaign"] = relationship(back_populates="metrics")

    def __repr__(self) -> str:
        return f"<CampaignMetric {self.campaign_id}>"
