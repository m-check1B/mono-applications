"""Team and agent management models."""

from datetime import UTC, datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel
from sqlalchemy import JSON, Boolean, Column, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from app.database import Base


class TeamRole(str, Enum):
    """Team role enumeration."""
    OWNER = "owner"
    MANAGER = "manager"
    SUPERVISOR = "supervisor"
    AGENT = "agent"
    VIEWER = "viewer"


class AgentStatus(str, Enum):
    """Agent status enumeration."""
    OFFLINE = "offline"
    AVAILABLE = "available"
    BUSY = "busy"
    ON_CALL = "on_call"
    BREAK = "break"
    TRAINING = "training"
    AWAY = "away"


class Team(Base):
    """Team model for hierarchical organization."""

    __tablename__ = "teams"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)

    # Hierarchy
    parent_team_id = Column(Integer, ForeignKey("teams.id"), nullable=True)
    organization_id = Column(Integer, nullable=True)  # For multi-tenant support

    # Manager
    manager_id = Column(String(36), ForeignKey("users.id"), nullable=True)

    # Configuration
    timezone = Column(String(50), default="UTC", nullable=False)
    working_hours = Column(JSON, default=dict, nullable=False)  # {"start": "09:00", "end": "17:00"}
    working_days = Column(JSON, default=list, nullable=False)  # ["monday", "tuesday", ...]

    # Metrics
    total_agents = Column(Integer, default=0, nullable=False)
    active_agents = Column(Integer, default=0, nullable=False)
    total_calls_handled = Column(Integer, default=0, nullable=False)
    average_handle_time = Column(Float, nullable=True)
    satisfaction_score = Column(Float, nullable=True)

    # Metadata
    tags = Column(JSON, default=list, nullable=False)
    custom_metadata = Column("metadata", JSON, default=dict, nullable=False)

    # Status
    is_active = Column(Boolean, default=True, nullable=False)

    # Timestamps
    created_at = Column(DateTime, default=lambda: datetime.now(UTC), nullable=False)
    updated_at = Column(DateTime, default=lambda: datetime.now(UTC), onupdate=lambda: datetime.now(UTC), nullable=False)

    # Relationships
    parent_team = relationship("Team", remote_side=[id], backref="child_teams")
    manager = relationship("User", foreign_keys=[manager_id])
    team_members = relationship("TeamMember", back_populates="team", cascade="all, delete-orphan")
    agent_profiles = relationship("AgentProfile", back_populates="team")

    def __repr__(self):
        return f"<Team(id={self.id}, name={self.name})>"


class TeamMember(Base):
    """Team membership model for many-to-many relationship."""

    __tablename__ = "team_members"

    id = Column(Integer, primary_key=True, index=True)
    team_id = Column(Integer, ForeignKey("teams.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    role = Column(String(50), default=TeamRole.AGENT, nullable=False)

    # Status
    is_active = Column(Boolean, default=True, nullable=False)

    # Timestamps
    joined_at = Column(DateTime, default=lambda: datetime.now(UTC), nullable=False)
    updated_at = Column(DateTime, default=lambda: datetime.now(UTC), onupdate=lambda: datetime.now(UTC), nullable=False)

    # Relationships
    team = relationship("Team", back_populates="team_members")
    user = relationship("User")

    def __repr__(self):
        return f"<TeamMember(team_id={self.team_id}, user_id={self.user_id}, role={self.role})>"


class AgentProfile(Base):
    """Agent profile model with detailed information."""

    __tablename__ = "agent_profiles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, unique=True)
    team_id = Column(Integer, ForeignKey("teams.id"), nullable=True)

    # Profile information
    employee_id = Column(String(50), unique=True, nullable=True)
    display_name = Column(String(200), nullable=True)
    phone_number = Column(String(20), nullable=True)
    extension = Column(String(10), nullable=True)

    # Status
    current_status = Column(String(50), default=AgentStatus.OFFLINE, nullable=False)
    status_since = Column(DateTime, default=lambda: datetime.now(UTC), nullable=False)
    last_activity_at = Column(DateTime, default=lambda: datetime.now(UTC), nullable=False)

    # Skills and capabilities
    skills = Column(JSON, default=list, nullable=False)  # ["sales", "support", "spanish"]
    languages = Column(JSON, default=list, nullable=False)  # ["en", "es"]
    max_concurrent_calls = Column(Integer, default=1, nullable=False)

    # Performance metrics
    total_calls_handled = Column(Integer, default=0, nullable=False)
    total_talk_time_seconds = Column(Integer, default=0, nullable=False)
    average_handle_time_seconds = Column(Integer, nullable=True)
    average_wait_time_seconds = Column(Integer, nullable=True)
    satisfaction_score = Column(Float, nullable=True)
    calls_today = Column(Integer, default=0, nullable=False)

    # Quality metrics
    adherence_score = Column(Float, nullable=True)  # Schedule adherence
    quality_score = Column(Float, nullable=True)  # QA score
    first_call_resolution_rate = Column(Float, nullable=True)

    # Availability
    is_available = Column(Boolean, default=False, nullable=False)
    available_for_calls = Column(Boolean, default=False, nullable=False)

    # Configuration
    auto_answer = Column(Boolean, default=False, nullable=False)
    max_call_duration_seconds = Column(Integer, nullable=True)
    preferred_campaigns = Column(JSON, default=list, nullable=False)

    # Metadata
    notes = Column(Text, nullable=True)
    custom_metadata = Column("metadata", JSON, default=dict, nullable=False)

    # Timestamps
    created_at = Column(DateTime, default=lambda: datetime.now(UTC), nullable=False)
    updated_at = Column(DateTime, default=lambda: datetime.now(UTC), onupdate=lambda: datetime.now(UTC), nullable=False)

    # Relationships
    user = relationship("User", backref="agent_profile")
    team = relationship("Team", back_populates="agent_profiles")
    shifts = relationship("Shift", back_populates="agent")
    performance_records = relationship("AgentPerformance", back_populates="agent")

    def __repr__(self):
        return f"<AgentProfile(id={self.id}, user_id={self.user_id}, status={self.current_status})>"


# Pydantic models for API
class TeamBase(BaseModel):
    """Base team model."""
    name: str
    description: str | None = None
    parent_team_id: int | None = None
    manager_id: int | None = None
    timezone: str = "UTC"
    working_hours: dict[str, str] | None = {}
    working_days: list[str] | None = []
    tags: list[str] | None = []
    metadata: dict[str, Any] | None = {}


class TeamCreate(TeamBase):
    """Team creation model."""
    pass


class TeamUpdate(BaseModel):
    """Team update model."""
    name: str | None = None
    description: str | None = None
    parent_team_id: int | None = None
    manager_id: int | None = None
    timezone: str | None = None
    working_hours: dict[str, str] | None = None
    working_days: list[str] | None = None
    tags: list[str] | None = None
    metadata: dict[str, Any] | None = None
    is_active: bool | None = None


class TeamResponse(TeamBase):
    """Team response model."""
    id: int
    total_agents: int
    active_agents: int
    total_calls_handled: int
    average_handle_time: float | None = None
    satisfaction_score: float | None = None
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class TeamMemberBase(BaseModel):
    """Base team member model."""
    team_id: int
    user_id: str
    role: TeamRole = TeamRole.AGENT


class TeamMemberCreate(TeamMemberBase):
    """Team member creation model."""
    pass


class TeamMemberUpdate(BaseModel):
    """Team member update model."""
    role: TeamRole | None = None
    is_active: bool | None = None


class TeamMemberResponse(TeamMemberBase):
    """Team member response model."""
    id: int
    is_active: bool
    joined_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class AgentProfileBase(BaseModel):
    """Base agent profile model."""
    display_name: str | None = None
    phone_number: str | None = None
    extension: str | None = None
    skills: list[str] | None = []
    languages: list[str] | None = []
    max_concurrent_calls: int = 1
    auto_answer: bool = False
    max_call_duration_seconds: int | None = None
    preferred_campaigns: list[int] | None = []
    notes: str | None = None
    metadata: dict[str, Any] | None = {}


class AgentProfileCreate(AgentProfileBase):
    """Agent profile creation model."""
    user_id: str
    team_id: int | None = None
    employee_id: str | None = None


class AgentProfileUpdate(BaseModel):
    """Agent profile update model."""
    team_id: int | None = None
    display_name: str | None = None
    phone_number: str | None = None
    extension: str | None = None
    skills: list[str] | None = None
    languages: list[str] | None = None
    max_concurrent_calls: int | None = None
    current_status: AgentStatus | None = None
    is_available: bool | None = None
    available_for_calls: bool | None = None
    auto_answer: bool | None = None
    max_call_duration_seconds: int | None = None
    preferred_campaigns: list[int] | None = None
    notes: str | None = None
    metadata: dict[str, Any] | None = None


class AgentProfileResponse(AgentProfileBase):
    """Agent profile response model."""
    id: int
    user_id: str
    team_id: int | None = None
    employee_id: str | None = None
    current_status: AgentStatus
    status_since: datetime
    last_activity_at: datetime
    total_calls_handled: int
    total_talk_time_seconds: int
    average_handle_time_seconds: int | None = None
    satisfaction_score: float | None = None
    calls_today: int
    is_available: bool
    available_for_calls: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class TeamHierarchy(BaseModel):
    """Team hierarchy model with nested structure."""
    id: int
    name: str
    description: str | None = None
    manager_id: int | None = None
    total_agents: int
    active_agents: int
    children: list["TeamHierarchy"] = []

    class Config:
        from_attributes = True


class AgentStatusUpdate(BaseModel):
    """Agent status update model."""
    status: AgentStatus
    reason: str | None = None


class AgentAssignment(BaseModel):
    """Agent assignment model."""
    agent_id: int
    team_id: int
    role: TeamRole = TeamRole.AGENT
