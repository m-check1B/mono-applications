"""Call Routing Engine Models.

Manages routing rules, conditions, and call distribution strategies.
"""

from datetime import UTC, datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel
from sqlalchemy import (
    JSON,
    Boolean,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import relationship

from app.database import Base


class CallRoutingStrategy(str, Enum):
    """Call routing strategies."""
    SKILL_BASED = "skill_based"  # Match based on agent skills
    LEAST_BUSY = "least_busy"  # Agent with fewest active calls
    LONGEST_IDLE = "longest_idle"  # Agent idle the longest
    ROUND_ROBIN = "round_robin"  # Equal distribution
    PRIORITY = "priority"  # Based on caller priority
    LANGUAGE = "language"  # Match caller language
    VIP = "vip"  # VIP customer routing
    CUSTOM = "custom"  # Custom condition-based


class ConditionOperator(str, Enum):
    """Condition operators for routing rules."""
    EQUALS = "equals"
    NOT_EQUALS = "not_equals"
    CONTAINS = "contains"
    STARTS_WITH = "starts_with"
    ENDS_WITH = "ends_with"
    GREATER_THAN = "greater_than"
    LESS_THAN = "less_than"
    IN_LIST = "in_list"
    NOT_IN_LIST = "not_in_list"
    MATCHES_REGEX = "matches_regex"


class TargetType(str, Enum):
    """Routing target types."""
    AGENT = "agent"  # Specific agent
    TEAM = "team"  # Team/group
    QUEUE = "queue"  # Call queue
    VOICEMAIL = "voicemail"  # Voicemail box
    EXTERNAL = "external"  # External phone number
    IVR = "ivr"  # IVR flow


class RoutingRule(Base):
    """Call routing rule definition."""
    __tablename__ = "routing_rules"

    id = Column(Integer, primary_key=True, index=True)
    campaign_id = Column(Integer, ForeignKey("campaigns.id", ondelete="CASCADE"), nullable=True)
    team_id = Column(Integer, ForeignKey("teams.id", ondelete="CASCADE"), nullable=True)

    # Rule metadata
    name = Column(String(200), nullable=False, index=True)
    description = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)

    # Priority (lower number = higher priority)
    priority = Column(Integer, default=100, nullable=False, index=True)

    # Strategy
    strategy = Column(String(50), nullable=False, default=CallRoutingStrategy.SKILL_BASED.value)

    # Conditions (JSON array of condition objects)
    # Structure: [{ field, operator, value, logic: "AND"|"OR" }]
    conditions = Column(JSON, default=list, nullable=False)

    # Time-based routing
    business_hours_only = Column(Boolean, default=False, nullable=False)
    active_hours = Column(JSON, default=dict, nullable=False)  # { day: [start, end] }
    timezone = Column(String(50), default="UTC", nullable=False)

    # Fallback handling
    fallback_enabled = Column(Boolean, default=True, nullable=False)
    fallback_rule_id = Column(Integer, ForeignKey("routing_rules.id", ondelete="SET NULL"), nullable=True)
    fallback_action = Column(String(50), nullable=True)  # "voicemail", "ivr", "queue"

    # Load balancing settings
    max_wait_time_seconds = Column(Integer, default=300, nullable=False)
    enable_load_balancing = Column(Boolean, default=True, nullable=False)
    load_balance_threshold = Column(Integer, default=3, nullable=False)  # Max calls per agent

    # Analytics
    total_calls_routed = Column(Integer, default=0, nullable=False)
    successful_routes = Column(Integer, default=0, nullable=False)
    failed_routes = Column(Integer, default=0, nullable=False)
    average_route_time_ms = Column(Float, default=0.0, nullable=False)

    # Metadata
    custom_metadata = Column("metadata", JSON, default=dict, nullable=False)

    # Timestamps
    created_at = Column(DateTime, default=lambda: datetime.now(UTC), nullable=False)
    updated_at = Column(DateTime, default=lambda: datetime.now(UTC), onupdate=lambda: datetime.now(UTC), nullable=False)
    last_used_at = Column(DateTime, nullable=True)

    # Relationships
    targets = relationship("RoutingTarget", back_populates="rule", cascade="all, delete-orphan")
    logs = relationship("RoutingLog", back_populates="rule", cascade="all, delete-orphan")

    __table_args__ = (
        Index("ix_routing_rules_active_priority", "is_active", "priority"),
    )

    def __repr__(self):
        return f"<RoutingRule(id={self.id}, name={self.name}, strategy={self.strategy})>"


class RoutingTarget(Base):
    """Routing target definition."""
    __tablename__ = "routing_targets"

    id = Column(Integer, primary_key=True, index=True)
    rule_id = Column(Integer, ForeignKey("routing_rules.id", ondelete="CASCADE"), nullable=False, index=True)

    # Target details
    target_type = Column(String(50), nullable=False)
    target_id = Column(String(100), nullable=False)  # ID of agent/team/queue/etc
    target_name = Column(String(200), nullable=True)

    # Weighted routing (for load balancing)
    weight = Column(Integer, default=1, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)

    # Skill requirements (for skill-based routing)
    required_skills = Column(JSON, default=list, nullable=False)
    min_skill_level = Column(Integer, default=1, nullable=False)

    # Language requirements
    required_languages = Column(JSON, default=list, nullable=False)

    # Priority level
    priority = Column(Integer, default=100, nullable=False)

    # Metadata
    custom_metadata = Column("metadata", JSON, default=dict, nullable=False)

    # Timestamps
    created_at = Column(DateTime, default=lambda: datetime.now(UTC), nullable=False)

    # Relationships
    rule = relationship("RoutingRule", back_populates="targets")

    def __repr__(self):
        return f"<RoutingTarget(id={self.id}, type={self.target_type}, target={self.target_id})>"


class RoutingLog(Base):
    """Audit log for routing decisions."""
    __tablename__ = "routing_logs"

    id = Column(Integer, primary_key=True, index=True)
    rule_id = Column(Integer, ForeignKey("routing_rules.id", ondelete="SET NULL"), nullable=True, index=True)
    call_sid = Column(String(100), nullable=False, index=True)

    # Call details
    caller_phone = Column(String(50), nullable=True)
    caller_priority = Column(Integer, nullable=True)
    campaign_id = Column(Integer, nullable=True)

    # Routing decision
    matched_rule_name = Column(String(200), nullable=True)
    strategy_used = Column(String(50), nullable=True)
    target_type = Column(String(50), nullable=True)
    target_id = Column(String(100), nullable=True)
    target_name = Column(String(200), nullable=True)

    # Conditions evaluated
    conditions_evaluated = Column(JSON, default=list, nullable=False)
    conditions_result = Column(Boolean, nullable=True)

    # Timing
    route_start_time = Column(DateTime, nullable=False, default=lambda: datetime.now(UTC), index=True)
    route_end_time = Column(DateTime, nullable=True)
    route_duration_ms = Column(Integer, nullable=True)

    # Result
    success = Column(Boolean, nullable=False)
    failure_reason = Column(String(500), nullable=True)

    # Fallback
    fallback_used = Column(Boolean, default=False, nullable=False)
    fallback_target = Column(String(200), nullable=True)

    # Metadata
    custom_metadata = Column("metadata", JSON, default=dict, nullable=False)

    # Relationships
    rule = relationship("RoutingRule", back_populates="logs")

    __table_args__ = (
        Index("ix_routing_logs_call_time", "call_sid", "route_start_time"),
    )

    def __repr__(self):
        return f"<RoutingLog(id={self.id}, call_sid={self.call_sid}, success={self.success})>"


# ===== Pydantic Models =====

class RoutingCondition(BaseModel):
    """Routing condition definition."""
    field: str  # Field to evaluate (e.g., "caller_phone", "campaign_id", "time_of_day")
    operator: ConditionOperator
    value: Any
    logic: str = "AND"  # AND or OR with next condition


class RoutingRuleBase(BaseModel):
    """Base routing rule model."""
    name: str
    description: str | None = None
    is_active: bool = True
    priority: int = 100
    strategy: CallRoutingStrategy
    conditions: list[RoutingCondition] = []
    business_hours_only: bool = False
    active_hours: dict[str, list[str]] = {}
    timezone: str = "UTC"
    fallback_enabled: bool = True
    fallback_action: str | None = None
    max_wait_time_seconds: int = 300
    enable_load_balancing: bool = True
    load_balance_threshold: int = 3


class RoutingRuleCreate(RoutingRuleBase):
    """Routing rule creation model."""
    campaign_id: int | None = None
    team_id: int | None = None
    fallback_rule_id: int | None = None


class RoutingRuleUpdate(BaseModel):
    """Routing rule update model."""
    name: str | None = None
    description: str | None = None
    is_active: bool | None = None
    priority: int | None = None
    strategy: CallRoutingStrategy | None = None
    conditions: list[RoutingCondition] | None = None
    fallback_enabled: bool | None = None
    fallback_action: str | None = None


class RoutingRuleResponse(RoutingRuleBase):
    """Routing rule response model."""
    id: int
    campaign_id: int | None = None
    team_id: int | None = None
    fallback_rule_id: int | None = None
    total_calls_routed: int
    successful_routes: int
    failed_routes: int
    average_route_time_ms: float
    created_at: datetime
    updated_at: datetime
    last_used_at: datetime | None = None

    class Config:
        from_attributes = True


class RoutingTargetBase(BaseModel):
    """Base routing target model."""
    target_type: TargetType
    target_id: str
    target_name: str | None = None
    weight: int = 1
    is_active: bool = True
    required_skills: list[str] = []
    min_skill_level: int = 1
    required_languages: list[str] = []
    priority: int = 100


class RoutingTargetCreate(RoutingTargetBase):
    """Routing target creation model."""
    rule_id: int


class RoutingTargetResponse(RoutingTargetBase):
    """Routing target response model."""
    id: int
    rule_id: int
    created_at: datetime

    class Config:
        from_attributes = True


class RoutingLogResponse(BaseModel):
    """Routing log response model."""
    id: int
    rule_id: int | None = None
    call_sid: str
    caller_phone: str | None = None
    matched_rule_name: str | None = None
    strategy_used: str | None = None
    target_type: str | None = None
    target_id: str | None = None
    target_name: str | None = None
    route_start_time: datetime
    route_end_time: datetime | None = None
    route_duration_ms: int | None = None
    success: bool
    failure_reason: str | None = None
    fallback_used: bool
    fallback_target: str | None = None

    class Config:
        from_attributes = True


class RouteCallRequest(BaseModel):
    """Request to route a call."""
    call_sid: str
    caller_phone: str | None = None
    caller_priority: int | None = None
    campaign_id: int | None = None
    required_skills: list[str] = []
    preferred_language: str | None = None
    metadata: dict[str, Any] = {}


class RouteCallResponse(BaseModel):
    """Response from call routing."""
    success: bool
    rule_used: str | None = None
    strategy: str | None = None
    target_type: str | None = None
    target_id: str | None = None
    target_name: str | None = None
    route_time_ms: int
    fallback_used: bool = False
    message: str | None = None
