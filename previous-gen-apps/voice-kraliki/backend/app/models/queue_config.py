"""Queue configuration models for advanced routing and SLA management."""

from datetime import UTC, datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field
from sqlalchemy import JSON, Boolean, Column, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from app.database import Base


class RoutingStrategy(str, Enum):
    """Queue routing strategy."""
    FIFO = "fifo"  # First In First Out
    PRIORITY = "priority"  # Priority-based
    SKILL_BASED = "skill_based"  # Skills matching
    LONGEST_IDLE = "longest_idle"  # Agent idle time
    ROUND_ROBIN = "round_robin"  # Equal distribution
    LEAST_OCCUPIED = "least_occupied"  # Lowest call volume


class QueueConfig(Base):
    """Queue configuration for advanced routing."""
    __tablename__ = "queue_configs"

    id = Column(Integer, primary_key=True, index=True)
    team_id = Column(Integer, ForeignKey("teams.id", ondelete="CASCADE"), nullable=True)
    campaign_id = Column(Integer, ForeignKey("campaigns.id", ondelete="CASCADE"), nullable=True)

    # Configuration
    name = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)

    # Routing strategy
    routing_strategy = Column(String(50), default=RoutingStrategy.FIFO, nullable=False)
    priority_weight = Column(Float, default=1.0, nullable=False)  # 0-1 for priority influence

    # Capacity limits
    max_queue_size = Column(Integer, default=100, nullable=False)
    max_wait_time_seconds = Column(Integer, default=300, nullable=False)  # 5 minutes

    # SLA targets
    sla_answer_time_seconds = Column(Integer, default=20, nullable=False)  # Answer within 20s
    sla_target_percentage = Column(Float, default=0.80, nullable=False)  # 80% of calls

    # Overflow handling
    overflow_enabled = Column(Boolean, default=False, nullable=False)
    overflow_queue_id = Column(Integer, ForeignKey("queue_configs.id", ondelete="SET NULL"), nullable=True)
    overflow_threshold = Column(Integer, default=10, nullable=False)  # Calls before overflow

    # Skill requirements
    require_skills_match = Column(Boolean, default=False, nullable=False)
    skill_match_threshold = Column(Float, default=0.70, nullable=False)  # 70% match required

    # Advanced features
    enable_callback = Column(Boolean, default=True, nullable=False)
    callback_wait_threshold = Column(Integer, default=180, nullable=False)  # 3 minutes

    enable_estimated_wait = Column(Boolean, default=True, nullable=False)
    enable_position_announcements = Column(Boolean, default=True, nullable=False)

    # Music/announcements
    music_on_hold_url = Column(String(500), nullable=True)
    announcement_urls = Column(JSON, default=list, nullable=False)  # List of announcement URLs

    # Business hours
    business_hours = Column(JSON, default=dict, nullable=False)  # Day -> hours mapping
    timezone = Column(String(50), default="UTC", nullable=False)

    # Metadata
    custom_metadata = Column("metadata", JSON, default=dict, nullable=False)

    # Timestamps
    created_at = Column(DateTime, default=lambda: datetime.now(UTC), nullable=False)
    updated_at = Column(DateTime, default=lambda: datetime.now(UTC), onupdate=lambda: datetime.now(UTC), nullable=False)

    # Relationships
    overflow_queue = relationship("QueueConfig", remote_side=[id], foreign_keys=[overflow_queue_id])

    def __repr__(self):
        return f"<QueueConfig(id={self.id}, name={self.name}, strategy={self.routing_strategy})>"


class QueueSLAMetric(Base):
    """SLA metrics tracking for queues."""
    __tablename__ = "queue_sla_metrics"

    id = Column(Integer, primary_key=True, index=True)
    queue_config_id = Column(Integer, ForeignKey("queue_configs.id", ondelete="CASCADE"), nullable=False)
    team_id = Column(Integer, ForeignKey("teams.id", ondelete="CASCADE"), nullable=True)

    # Time period
    period_start = Column(DateTime, nullable=False, index=True)
    period_end = Column(DateTime, nullable=False)

    # Call volumes
    total_calls = Column(Integer, default=0, nullable=False)
    answered_calls = Column(Integer, default=0, nullable=False)
    abandoned_calls = Column(Integer, default=0, nullable=False)

    # SLA performance
    calls_within_sla = Column(Integer, default=0, nullable=False)
    sla_compliance_percentage = Column(Float, default=0.0, nullable=False)

    # Wait times
    average_wait_seconds = Column(Float, default=0.0, nullable=False)
    max_wait_seconds = Column(Integer, default=0, nullable=False)
    median_wait_seconds = Column(Float, default=0.0, nullable=False)

    # Answer times
    average_answer_seconds = Column(Float, default=0.0, nullable=False)

    # Abandonment
    abandon_rate_percentage = Column(Float, default=0.0, nullable=False)
    average_abandon_time_seconds = Column(Float, default=0.0, nullable=False)

    # Service level
    service_level_20s = Column(Float, default=0.0, nullable=False)  # % answered in 20s
    service_level_30s = Column(Float, default=0.0, nullable=False)  # % answered in 30s
    service_level_60s = Column(Float, default=0.0, nullable=False)  # % answered in 60s

    # Agent metrics
    average_handle_time_seconds = Column(Float, default=0.0, nullable=False)
    occupancy_percentage = Column(Float, default=0.0, nullable=False)

    # Timestamps
    created_at = Column(DateTime, default=lambda: datetime.now(UTC), nullable=False)

    def __repr__(self):
        return f"<QueueSLAMetric(id={self.id}, compliance={self.sla_compliance_percentage}%)>"


# ===== Pydantic Models =====

class QueueConfigBase(BaseModel):
    """Base queue configuration model."""
    name: str
    description: str | None = None
    is_active: bool = True
    routing_strategy: RoutingStrategy = RoutingStrategy.FIFO
    priority_weight: float = 1.0
    max_queue_size: int = 100
    max_wait_time_seconds: int = 300
    sla_answer_time_seconds: int = 20
    sla_target_percentage: float = 0.80
    overflow_enabled: bool = False
    overflow_threshold: int = 10
    require_skills_match: bool = False
    skill_match_threshold: float = 0.70
    enable_callback: bool = True
    callback_wait_threshold: int = 180
    enable_estimated_wait: bool = True
    enable_position_announcements: bool = True
    business_hours: dict[str, Any] = Field(default_factory=dict)
    timezone: str = "UTC"


class QueueConfigCreate(QueueConfigBase):
    """Queue configuration creation model."""
    team_id: int | None = None
    campaign_id: int | None = None


class QueueConfigUpdate(BaseModel):
    """Queue configuration update model."""
    name: str | None = None
    description: str | None = None
    is_active: bool | None = None
    routing_strategy: RoutingStrategy | None = None
    priority_weight: float | None = None
    max_queue_size: int | None = None
    max_wait_time_seconds: int | None = None
    sla_answer_time_seconds: int | None = None
    sla_target_percentage: float | None = None
    overflow_enabled: bool | None = None
    overflow_threshold: int | None = None
    require_skills_match: bool | None = None
    skill_match_threshold: float | None = None


class QueueConfigResponse(QueueConfigBase):
    """Queue configuration response model."""
    id: int
    team_id: int | None = None
    campaign_id: int | None = None
    overflow_queue_id: int | None = None
    music_on_hold_url: str | None = None
    announcement_urls: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class QueueSLAMetricResponse(BaseModel):
    """Queue SLA metrics response model."""
    id: int
    queue_config_id: int
    team_id: int | None = None
    period_start: datetime
    period_end: datetime
    total_calls: int
    answered_calls: int
    abandoned_calls: int
    calls_within_sla: int
    sla_compliance_percentage: float
    average_wait_seconds: float
    max_wait_seconds: int
    median_wait_seconds: float
    average_answer_seconds: float
    abandon_rate_percentage: float
    average_abandon_time_seconds: float
    service_level_20s: float
    service_level_30s: float
    service_level_60s: float
    average_handle_time_seconds: float
    occupancy_percentage: float
    created_at: datetime

    class Config:
        from_attributes = True
