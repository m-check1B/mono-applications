"""
Analytics and Metrics Models

Models for tracking, aggregating, and analyzing system metrics.
Supports time-series data, aggregations, and performance alerting.
"""

from datetime import UTC, datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field
from sqlalchemy import (
    JSON,
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    Interval,
    Numeric,
    String,
    Text,
)
from sqlalchemy.orm import relationship

from app.database import Base

# ============================================================================
# Enums
# ============================================================================

class MetricType(str, Enum):
    """Type of metric being tracked"""
    CALL = "call"  # Call-related metrics (duration, wait time, etc.)
    AGENT = "agent"  # Agent performance metrics
    CAMPAIGN = "campaign"  # Campaign effectiveness metrics
    SYSTEM = "system"  # System performance metrics
    QUALITY = "quality"  # Quality assurance metrics
    BUSINESS = "business"  # Business KPIs


class AggregationType(str, Enum):
    """Type of aggregation applied to metrics"""
    SUM = "sum"
    AVERAGE = "average"
    MIN = "min"
    MAX = "max"
    COUNT = "count"
    MEDIAN = "median"
    PERCENTILE_95 = "percentile_95"
    PERCENTILE_99 = "percentile_99"


class TimeGranularity(str, Enum):
    """Time granularity for metric aggregation"""
    MINUTE = "minute"
    HOUR = "hour"
    DAY = "day"
    WEEK = "week"
    MONTH = "month"
    QUARTER = "quarter"
    YEAR = "year"


class AlertSeverity(str, Enum):
    """Severity level of performance alerts"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class AlertStatus(str, Enum):
    """Status of an alert"""
    ACTIVE = "active"
    ACKNOWLEDGED = "acknowledged"
    RESOLVED = "resolved"
    MUTED = "muted"


# ============================================================================
# Database Models
# ============================================================================

class Metric(Base):
    """
    Individual metric data points

    Stores time-series metric data for various system components.
    Designed for high-volume writes and efficient time-based queries.
    """
    __tablename__ = "metrics"

    id = Column(Integer, primary_key=True, index=True)

    # Metric identification
    metric_type = Column(String(50), nullable=False, index=True)  # MetricType enum
    metric_name = Column(String(100), nullable=False, index=True)
    metric_category = Column(String(50), nullable=True)  # Subcategory for organization

    # Metric value
    value = Column(Numeric(precision=20, scale=6), nullable=False)
    unit = Column(String(50), nullable=True)  # e.g., "seconds", "count", "percentage"

    # Context and metadata
    team_id = Column(Integer, ForeignKey("teams.id"), nullable=True, index=True)
    agent_id = Column(Integer, ForeignKey("agent_profiles.id"), nullable=True, index=True)
    campaign_id = Column(Integer, ForeignKey("campaigns.id"), nullable=True, index=True)
    call_id = Column(Integer, ForeignKey("active_calls.id"), nullable=True, index=True)

    # Additional context
    tags = Column(JSON, default=dict)  # Flexible tagging for filtering
    dimensions = Column(JSON, default=dict)  # Dimensional data (region, dept, etc.)
    custom_metadata = Column("metadata", JSON, default=dict)  # Additional metadata

    # Timestamp
    timestamp = Column(DateTime, nullable=False, default=lambda: datetime.now(UTC), index=True)

    # Soft delete
    is_deleted = Column(Boolean, default=False)
    deleted_at = Column(DateTime, nullable=True)

    # Relationships
    team = relationship("Team", foreign_keys=[team_id])
    agent = relationship("AgentProfile", foreign_keys=[agent_id])
    campaign = relationship("Campaign", foreign_keys=[campaign_id])
    call = relationship("ActiveCall", foreign_keys=[call_id])

    # Indexes for efficient time-series queries
    __table_args__ = (
        Index('idx_metric_type_timestamp', 'metric_type', 'timestamp'),
        Index('idx_metric_name_timestamp', 'metric_name', 'timestamp'),
        Index('idx_team_timestamp', 'team_id', 'timestamp'),
        Index('idx_agent_timestamp', 'agent_id', 'timestamp'),
        Index('idx_campaign_timestamp', 'campaign_id', 'timestamp'),
    )


class MetricAggregation(Base):
    """
    Pre-computed metric aggregations

    Stores aggregated metrics over time windows for faster analytics queries.
    Computed periodically to avoid real-time calculation overhead.
    """
    __tablename__ = "metric_aggregations"

    id = Column(Integer, primary_key=True, index=True)

    # Aggregation identification
    metric_type = Column(String(50), nullable=False, index=True)
    metric_name = Column(String(100), nullable=False, index=True)
    aggregation_type = Column(String(50), nullable=False)  # AggregationType enum
    granularity = Column(String(50), nullable=False)  # TimeGranularity enum

    # Aggregated values
    value = Column(Numeric(precision=20, scale=6), nullable=False)
    count = Column(Integer, nullable=False)  # Number of data points in aggregation
    min_value = Column(Numeric(precision=20, scale=6), nullable=True)
    max_value = Column(Numeric(precision=20, scale=6), nullable=True)

    # Time window
    window_start = Column(DateTime, nullable=False, index=True)
    window_end = Column(DateTime, nullable=False, index=True)

    # Context
    team_id = Column(Integer, ForeignKey("teams.id"), nullable=True, index=True)
    agent_id = Column(Integer, ForeignKey("agent_profiles.id"), nullable=True, index=True)
    campaign_id = Column(Integer, ForeignKey("campaigns.id"), nullable=True, index=True)

    # Dimensional filters
    dimensions = Column(JSON, default=dict)

    # Metadata
    computed_at = Column(DateTime, nullable=False, default=lambda: datetime.now(UTC))
    is_partial = Column(Boolean, default=False)  # Indicates incomplete aggregation

    # Relationships
    team = relationship("Team", foreign_keys=[team_id])
    agent = relationship("AgentProfile", foreign_keys=[agent_id])
    campaign = relationship("Campaign", foreign_keys=[campaign_id])

    __table_args__ = (
        Index('idx_agg_type_window', 'metric_type', 'metric_name', 'window_start', 'window_end'),
        Index('idx_agg_granularity_window', 'granularity', 'window_start'),
    )


class PerformanceAlert(Base):
    """
    Performance and threshold alerts

    Tracks alerts generated when metrics cross defined thresholds.
    Supports notification, acknowledgment, and resolution tracking.
    """
    __tablename__ = "performance_alerts"

    id = Column(Integer, primary_key=True, index=True)

    # Alert identification
    alert_type = Column(String(50), nullable=False, index=True)
    alert_name = Column(String(200), nullable=False)
    severity = Column(String(50), nullable=False, default=AlertSeverity.WARNING.value)
    status = Column(String(50), nullable=False, default=AlertStatus.ACTIVE.value, index=True)

    # Alert details
    metric_type = Column(String(50), nullable=False)
    metric_name = Column(String(100), nullable=False)
    threshold_value = Column(Numeric(precision=20, scale=6), nullable=False)
    actual_value = Column(Numeric(precision=20, scale=6), nullable=False)
    threshold_operator = Column(String(20), nullable=False)  # "greater_than", "less_than", etc.

    # Message and description
    message = Column(Text, nullable=False)
    description = Column(Text, nullable=True)
    recommended_actions = Column(JSON, default=list)

    # Context
    team_id = Column(Integer, ForeignKey("teams.id"), nullable=True, index=True)
    agent_id = Column(Integer, ForeignKey("agent_profiles.id"), nullable=True, index=True)
    campaign_id = Column(Integer, ForeignKey("campaigns.id"), nullable=True, index=True)

    # Alert lifecycle
    triggered_at = Column(DateTime, nullable=False, default=lambda: datetime.now(UTC), index=True)
    acknowledged_at = Column(DateTime, nullable=True)
    acknowledged_by_id = Column(Integer, ForeignKey("agent_profiles.id"), nullable=True)
    resolved_at = Column(DateTime, nullable=True)
    resolved_by_id = Column(Integer, ForeignKey("agent_profiles.id"), nullable=True)

    # Notification tracking
    notifications_sent = Column(JSON, default=list)  # List of notification channels used
    notification_count = Column(Integer, default=0)
    last_notification_at = Column(DateTime, nullable=True)

    # Metadata
    custom_metadata = Column("metadata", JSON, default=dict)
    tags = Column(JSON, default=list)

    # Relationships
    team = relationship("Team", foreign_keys=[team_id])
    agent = relationship("AgentProfile", foreign_keys=[agent_id])
    campaign = relationship("Campaign", foreign_keys=[campaign_id])
    acknowledged_by = relationship("AgentProfile", foreign_keys=[acknowledged_by_id])
    resolved_by = relationship("AgentProfile", foreign_keys=[resolved_by_id])

    __table_args__ = (
        Index('idx_alert_status_triggered', 'status', 'triggered_at'),
        Index('idx_alert_severity_status', 'severity', 'status'),
    )


class MetricThreshold(Base):
    """
    Configurable metric thresholds for alerting

    Defines threshold rules that trigger performance alerts.
    Supports dynamic threshold configuration per team/campaign.
    """
    __tablename__ = "metric_thresholds"

    id = Column(Integer, primary_key=True, index=True)

    # Threshold identification
    name = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True, index=True)

    # Metric target
    metric_type = Column(String(50), nullable=False)
    metric_name = Column(String(100), nullable=False)

    # Threshold rules
    threshold_value = Column(Numeric(precision=20, scale=6), nullable=False)
    operator = Column(String(20), nullable=False)  # "gt", "lt", "eq", "gte", "lte"
    severity = Column(String(50), nullable=False, default=AlertSeverity.WARNING.value)

    # Evaluation settings
    evaluation_window = Column(Interval, nullable=True)  # Time window to evaluate
    consecutive_violations = Column(Integer, default=1)  # How many violations before alerting

    # Context filters
    team_id = Column(Integer, ForeignKey("teams.id"), nullable=True, index=True)
    campaign_id = Column(Integer, ForeignKey("campaigns.id"), nullable=True, index=True)
    dimension_filters = Column(JSON, default=dict)

    # Notification settings
    notification_channels = Column(JSON, default=list)  # ["email", "sms", "webhook"]
    notification_recipients = Column(JSON, default=list)
    cooldown_minutes = Column(Integer, default=60)  # Min time between alerts

    # Metadata
    created_at = Column(DateTime, nullable=False, default=lambda: datetime.now(UTC))
    updated_at = Column(DateTime, nullable=False, default=lambda: datetime.now(UTC), onupdate=lambda: datetime.now(UTC))
    created_by_id = Column(Integer, ForeignKey("agent_profiles.id"), nullable=True)

    # Relationships
    team = relationship("Team", foreign_keys=[team_id])
    campaign = relationship("Campaign", foreign_keys=[campaign_id])
    created_by = relationship("AgentProfile", foreign_keys=[created_by_id])


# ============================================================================
# Pydantic Schemas
# ============================================================================

class MetricCreate(BaseModel):
    """Schema for creating a metric"""
    metric_type: MetricType
    metric_name: str
    metric_category: str | None = None
    value: float
    unit: str | None = None
    team_id: int | None = None
    agent_id: int | None = None
    campaign_id: int | None = None
    call_id: int | None = None
    tags: dict[str, Any] = Field(default_factory=dict)
    dimensions: dict[str, Any] = Field(default_factory=dict)
    metadata: dict[str, Any] = Field(default_factory=dict)
    timestamp: datetime | None = None


class MetricResponse(BaseModel):
    """Schema for metric response"""
    id: int
    metric_type: str
    metric_name: str
    value: float
    unit: str | None
    timestamp: datetime
    team_id: int | None
    agent_id: int | None
    campaign_id: int | None
    tags: dict[str, Any]

    class Config:
        from_attributes = True


class MetricAggregationResponse(BaseModel):
    """Schema for metric aggregation response"""
    id: int
    metric_type: str
    metric_name: str
    aggregation_type: str
    granularity: str
    value: float
    count: int
    min_value: float | None
    max_value: float | None
    window_start: datetime
    window_end: datetime

    class Config:
        from_attributes = True


class PerformanceAlertResponse(BaseModel):
    """Schema for performance alert response"""
    id: int
    alert_type: str
    alert_name: str
    severity: str
    status: str
    metric_type: str
    metric_name: str
    threshold_value: float
    actual_value: float
    message: str
    triggered_at: datetime
    acknowledged_at: datetime | None
    resolved_at: datetime | None

    class Config:
        from_attributes = True


class MetricThresholdCreate(BaseModel):
    """Schema for creating a metric threshold"""
    name: str
    description: str | None = None
    metric_type: MetricType
    metric_name: str
    threshold_value: float
    operator: str  # "gt", "lt", "eq", "gte", "lte"
    severity: AlertSeverity = AlertSeverity.WARNING
    team_id: int | None = None
    campaign_id: int | None = None
    notification_channels: list = Field(default_factory=list)
    notification_recipients: list = Field(default_factory=list)
    cooldown_minutes: int = 60


class MetricThresholdResponse(BaseModel):
    """Schema for metric threshold response"""
    id: int
    name: str
    description: str | None
    is_active: bool
    metric_type: str
    metric_name: str
    threshold_value: float
    operator: str
    severity: str
    notification_channels: list
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
