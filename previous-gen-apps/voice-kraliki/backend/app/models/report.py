"""
Report Models

Models for report generation, templates, scheduling, and distribution.
Supports multiple report types, formats, and automated delivery.
"""

from datetime import UTC, datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field
from sqlalchemy import JSON, Boolean, Column, DateTime, ForeignKey, Index, Integer, String, Text
from sqlalchemy.orm import relationship

from app.database import Base

# ============================================================================
# Enums
# ============================================================================

class ReportType(str, Enum):
    """Type of report"""
    DAILY_SUMMARY = "daily_summary"
    AGENT_PERFORMANCE = "agent_performance"
    CAMPAIGN_EFFECTIVENESS = "campaign_effectiveness"
    QUALITY_ASSURANCE = "quality_assurance"
    CALL_ANALYTICS = "call_analytics"
    CUSTOM = "custom"


class ReportFormat(str, Enum):
    """Output format for reports"""
    PDF = "pdf"
    CSV = "csv"
    EXCEL = "excel"
    JSON = "json"
    HTML = "html"


class ReportStatus(str, Enum):
    """Status of report generation"""
    PENDING = "pending"
    GENERATING = "generating"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class ScheduleFrequency(str, Enum):
    """Frequency for scheduled reports"""
    HOURLY = "hourly"
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    YEARLY = "yearly"
    CUSTOM = "custom"


class DeliveryMethod(str, Enum):
    """Method for report delivery"""
    EMAIL = "email"
    SLACK = "slack"
    WEBHOOK = "webhook"
    FTP = "ftp"
    S3 = "s3"
    DOWNLOAD = "download"


# ============================================================================
# Database Models
# ============================================================================

class ReportTemplate(Base):
    """
    Report template definitions

    Defines reusable report templates with configuration for
    data sources, filters, visualizations, and layout.
    """
    __tablename__ = "report_templates"

    id = Column(Integer, primary_key=True, index=True)

    # Template identification
    name = Column(String(200), nullable=False, unique=True)
    description = Column(Text, nullable=True)
    report_type = Column(String(50), nullable=False, index=True)  # ReportType enum
    is_public = Column(Boolean, default=False)  # Available to all teams
    is_active = Column(Boolean, default=True, index=True)

    # Template configuration
    configuration = Column(JSON, nullable=False)  # Template-specific config
    """
    Configuration structure:
    {
        "data_sources": [
            {"type": "metrics", "filters": {...}, "aggregations": [...]}
        ],
        "sections": [
            {
                "title": "Summary",
                "widgets": [
                    {"type": "chart", "chart_type": "bar", "metric": "...", "options": {...}}
                ]
            }
        ],
        "filters": {
            "date_range": "last_7_days",
            "team_ids": [],
            "campaign_ids": []
        },
        "layout": {"orientation": "portrait", "page_size": "A4"}
    }
    """

    # Default settings
    default_format = Column(String(20), default=ReportFormat.PDF.value)
    default_filters = Column(JSON, default=dict)

    # Ownership and permissions
    team_id = Column(Integer, ForeignKey("teams.id"), nullable=True, index=True)
    created_by_id = Column(Integer, ForeignKey("agent_profiles.id"), nullable=True)

    # Metadata
    version = Column(Integer, default=1)
    tags = Column(JSON, default=list)
    created_at = Column(DateTime, nullable=False, default=lambda: datetime.now(UTC))
    updated_at = Column(DateTime, nullable=False, default=lambda: datetime.now(UTC), onupdate=lambda: datetime.now(UTC))

    # Relationships
    team = relationship("Team", foreign_keys=[team_id])
    created_by = relationship("AgentProfile", foreign_keys=[created_by_id])
    reports = relationship("Report", back_populates="template")
    schedules = relationship("ReportSchedule", back_populates="template")


class Report(Base):
    """
    Generated reports

    Stores generated report instances with their data, files, and metadata.
    Supports multiple output formats and distribution tracking.
    """
    __tablename__ = "reports"

    id = Column(Integer, primary_key=True, index=True)

    # Report identification
    name = Column(String(200), nullable=False)
    report_type = Column(String(50), nullable=False, index=True)
    template_id = Column(Integer, ForeignKey("report_templates.id"), nullable=True, index=True)

    # Report generation
    status = Column(String(50), nullable=False, default=ReportStatus.PENDING.value, index=True)
    format = Column(String(20), nullable=False, default=ReportFormat.PDF.value)

    # Report data and filters
    filters = Column(JSON, default=dict)  # Filters used to generate report
    parameters = Column(JSON, default=dict)  # Additional parameters
    date_range_start = Column(DateTime, nullable=True, index=True)
    date_range_end = Column(DateTime, nullable=True, index=True)

    # Generated content
    file_path = Column(String(500), nullable=True)  # Path to generated file
    file_size_bytes = Column(Integer, nullable=True)
    file_url = Column(String(500), nullable=True)  # Download URL (signed)
    expires_at = Column(DateTime, nullable=True)  # When file expires

    # Report data (for JSON/API access)
    report_data = Column(JSON, nullable=True)  # Structured report data
    summary = Column(JSON, default=dict)  # Key metrics summary

    # Context
    team_id = Column(Integer, ForeignKey("teams.id"), nullable=True, index=True)
    campaign_id = Column(Integer, ForeignKey("campaigns.id"), nullable=True, index=True)

    # Generation tracking
    requested_by_id = Column(Integer, ForeignKey("agent_profiles.id"), nullable=True)
    requested_at = Column(DateTime, nullable=False, default=lambda: datetime.now(UTC), index=True)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)

    # Error handling
    error_message = Column(Text, nullable=True)
    retry_count = Column(Integer, default=0)

    # Distribution tracking
    delivered_to = Column(JSON, default=list)  # List of delivery recipients
    delivery_status = Column(JSON, default=dict)  # Status per delivery method

    # Metadata
    custom_metadata = Column("metadata", JSON, default=dict)
    tags = Column(JSON, default=list)

    # Soft delete
    is_deleted = Column(Boolean, default=False)
    deleted_at = Column(DateTime, nullable=True)

    # Relationships
    template = relationship("ReportTemplate", back_populates="reports")
    team = relationship("Team", foreign_keys=[team_id])
    campaign = relationship("Campaign", foreign_keys=[campaign_id])
    requested_by = relationship("AgentProfile", foreign_keys=[requested_by_id])

    __table_args__ = (
        Index('idx_report_status_requested', 'status', 'requested_at'),
        Index('idx_report_team_type', 'team_id', 'report_type', 'requested_at'),
    )


class ReportSchedule(Base):
    """
    Automated report scheduling

    Configures automated report generation and distribution.
    Supports recurring schedules with flexible delivery options.
    """
    __tablename__ = "report_schedules"

    id = Column(Integer, primary_key=True, index=True)

    # Schedule identification
    name = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True, index=True)

    # Report configuration
    template_id = Column(Integer, ForeignKey("report_templates.id"), nullable=False, index=True)
    format = Column(String(20), nullable=False, default=ReportFormat.PDF.value)
    filters = Column(JSON, default=dict)  # Filters to apply
    parameters = Column(JSON, default=dict)  # Additional parameters

    # Schedule configuration
    frequency = Column(String(50), nullable=False)  # ScheduleFrequency enum
    cron_expression = Column(String(100), nullable=True)  # For custom schedules

    # Time configuration
    hour = Column(Integer, nullable=True)  # Hour to run (0-23)
    day_of_week = Column(Integer, nullable=True)  # Day of week (0-6, Monday=0)
    day_of_month = Column(Integer, nullable=True)  # Day of month (1-31)
    timezone = Column(String(50), default="UTC")

    # Delivery configuration
    delivery_methods = Column(JSON, default=list)  # List of DeliveryMethod values
    delivery_config = Column(JSON, default=dict)
    """
    Delivery config structure:
    {
        "email": {
            "recipients": ["user@example.com"],
            "subject": "Weekly Report",
            "body_template": "..."
        },
        "slack": {
            "channel": "#reports",
            "message_template": "..."
        },
        "webhook": {
            "url": "https://example.com/webhook",
            "headers": {...}
        }
    }
    """

    # Context
    team_id = Column(Integer, ForeignKey("teams.id"), nullable=True, index=True)

    # Schedule tracking
    last_run_at = Column(DateTime, nullable=True)
    last_status = Column(String(50), nullable=True)  # Last execution status
    last_report_id = Column(Integer, ForeignKey("reports.id"), nullable=True)
    next_run_at = Column(DateTime, nullable=True, index=True)
    run_count = Column(Integer, default=0)
    failure_count = Column(Integer, default=0)

    # Ownership
    created_by_id = Column(Integer, ForeignKey("agent_profiles.id"), nullable=True)

    # Metadata
    created_at = Column(DateTime, nullable=False, default=lambda: datetime.now(UTC))
    updated_at = Column(DateTime, nullable=False, default=lambda: datetime.now(UTC), onupdate=lambda: datetime.now(UTC))

    # Relationships
    template = relationship("ReportTemplate", back_populates="schedules")
    team = relationship("Team", foreign_keys=[team_id])
    created_by = relationship("AgentProfile", foreign_keys=[created_by_id])
    last_report = relationship("Report", foreign_keys=[last_report_id])

    __table_args__ = (
        Index('idx_schedule_active_next_run', 'is_active', 'next_run_at'),
    )


class ReportWidget(Base):
    """
    Reusable report widgets/visualizations

    Defines individual visualization components that can be
    used across multiple report templates.
    """
    __tablename__ = "report_widgets"

    id = Column(Integer, primary_key=True, index=True)

    # Widget identification
    name = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    widget_type = Column(String(50), nullable=False)  # "chart", "table", "metric", "text"
    is_public = Column(Boolean, default=False)

    # Widget configuration
    configuration = Column(JSON, nullable=False)
    """
    Configuration structure:
    {
        "data_source": {
            "type": "metrics",
            "metric_name": "call_duration",
            "aggregation": "average",
            "filters": {...}
        },
        "visualization": {
            "type": "line_chart",
            "x_axis": "timestamp",
            "y_axis": "value",
            "options": {...}
        },
        "styling": {
            "colors": [...],
            "size": {"width": 400, "height": 300}
        }
    }
    """

    # Default settings
    default_time_range = Column(String(50), default="last_7_days")

    # Ownership
    team_id = Column(Integer, ForeignKey("teams.id"), nullable=True)
    created_by_id = Column(Integer, ForeignKey("agent_profiles.id"), nullable=True)

    # Metadata
    tags = Column(JSON, default=list)
    created_at = Column(DateTime, nullable=False, default=lambda: datetime.now(UTC))
    updated_at = Column(DateTime, nullable=False, default=lambda: datetime.now(UTC), onupdate=lambda: datetime.now(UTC))

    # Relationships
    team = relationship("Team", foreign_keys=[team_id])
    created_by = relationship("AgentProfile", foreign_keys=[created_by_id])


# ============================================================================
# Pydantic Schemas
# ============================================================================

class ReportTemplateCreate(BaseModel):
    """Schema for creating a report template"""
    name: str
    description: str | None = None
    report_type: ReportType
    configuration: dict[str, Any]
    default_format: ReportFormat = ReportFormat.PDF
    is_public: bool = False
    team_id: int | None = None
    tags: list = Field(default_factory=list)


class ReportTemplateResponse(BaseModel):
    """Schema for report template response"""
    id: int
    name: str
    description: str | None
    report_type: str
    is_public: bool
    is_active: bool
    default_format: str
    version: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ReportCreate(BaseModel):
    """Schema for creating/requesting a report"""
    name: str
    report_type: ReportType
    template_id: int | None = None
    format: ReportFormat = ReportFormat.PDF
    filters: dict[str, Any] = Field(default_factory=dict)
    parameters: dict[str, Any] = Field(default_factory=dict)
    date_range_start: datetime | None = None
    date_range_end: datetime | None = None
    team_id: int | None = None
    campaign_id: int | None = None


class ReportResponse(BaseModel):
    """Schema for report response"""
    id: int
    name: str
    report_type: str
    status: str
    format: str
    file_url: str | None
    file_size_bytes: int | None
    expires_at: datetime | None
    requested_at: datetime
    completed_at: datetime | None
    summary: dict[str, Any]

    class Config:
        from_attributes = True


class ReportScheduleCreate(BaseModel):
    """Schema for creating a report schedule"""
    name: str
    description: str | None = None
    template_id: int
    format: ReportFormat = ReportFormat.PDF
    frequency: ScheduleFrequency
    cron_expression: str | None = None
    hour: int | None = None
    day_of_week: int | None = None
    day_of_month: int | None = None
    timezone: str = "UTC"
    delivery_methods: list = Field(default_factory=list)
    delivery_config: dict[str, Any] = Field(default_factory=dict)
    filters: dict[str, Any] = Field(default_factory=dict)
    team_id: int | None = None


class ReportScheduleResponse(BaseModel):
    """Schema for report schedule response"""
    id: int
    name: str
    description: str | None
    is_active: bool
    template_id: int
    frequency: str
    delivery_methods: list
    last_run_at: datetime | None
    next_run_at: datetime | None
    run_count: int
    failure_count: int
    created_at: datetime

    class Config:
        from_attributes = True
