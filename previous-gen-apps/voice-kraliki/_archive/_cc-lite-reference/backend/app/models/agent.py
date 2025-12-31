"""Agent model - SQLAlchemy 2.0"""

from datetime import datetime
from typing import Optional
import enum
from sqlalchemy import String, DateTime, JSON, Integer, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class AgentStatus(str, enum.Enum):
    """Agent status"""
    OFFLINE = "OFFLINE"
    AVAILABLE = "AVAILABLE"
    BUSY = "BUSY"
    BREAK = "BREAK"
    TRAINING = "TRAINING"


class Agent(Base):
    """Agent model - extends User"""

    __tablename__ = "agents"

    id: Mapped[str] = mapped_column(String(30), primary_key=True)
    user_id: Mapped[str] = mapped_column(String(30), ForeignKey("users.id", ondelete="CASCADE"), unique=True)
    status: Mapped[AgentStatus] = mapped_column(SQLEnum(AgentStatus), default=AgentStatus.OFFLINE)
    max_capacity: Mapped[int] = mapped_column(Integer, default=1)
    current_load: Mapped[int] = mapped_column(Integer, default=0)
    skills: Mapped[list[str]] = mapped_column(JSON, default=list)
    language: Mapped[str] = mapped_column(String(10), default="en")
    extra_metadata: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    # user: Mapped["User"] = relationship(back_populates="agent")

    def __repr__(self) -> str:
        return f"<Agent {self.user_id} ({self.status})>"

    @property
    def is_available(self) -> bool:
        """Check if agent is available for calls"""
        return self.status == AgentStatus.AVAILABLE and self.current_load < self.max_capacity

    @property
    def capacity_percentage(self) -> float:
        """Get current capacity usage as percentage"""
        if self.max_capacity == 0:
            return 0.0
        return (self.current_load / self.max_capacity) * 100
