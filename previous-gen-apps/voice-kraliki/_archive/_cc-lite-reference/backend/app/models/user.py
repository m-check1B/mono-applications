"""
User model - SQLAlchemy 2.0
Migrated from Prisma schema
"""

from datetime import datetime
from typing import Optional
from sqlalchemy import String, Boolean, DateTime, JSON, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
import enum

from app.core.database import Base


class UserRole(str, enum.Enum):
    """User roles"""
    ADMIN = "ADMIN"
    SUPERVISOR = "SUPERVISOR"
    AGENT = "AGENT"
    CUSTOMER = "CUSTOMER"


class UserStatus(str, enum.Enum):
    """User status"""
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"
    SUSPENDED = "SUSPENDED"


class AuthProvider(str, enum.Enum):
    """Authentication providers"""
    LOCAL = "LOCAL"
    GOOGLE = "GOOGLE"
    MICROSOFT = "MICROSOFT"


class User(Base):
    """User model"""

    __tablename__ = "users"

    # Primary fields
    id: Mapped[str] = mapped_column(String(30), primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    username: Mapped[Optional[str]] = mapped_column(String(50), unique=True, nullable=True)

    # Authentication
    first_name: Mapped[str] = mapped_column(String(100))
    last_name: Mapped[str] = mapped_column(String(100))
    password_hash: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    role: Mapped[UserRole] = mapped_column(SQLEnum(UserRole), default=UserRole.AGENT)
    status: Mapped[UserStatus] = mapped_column(SQLEnum(UserStatus), default=UserStatus.ACTIVE)
    auth_provider: Mapped[AuthProvider] = mapped_column(SQLEnum(AuthProvider), default=AuthProvider.LOCAL)

    # OAuth
    google_id: Mapped[Optional[str]] = mapped_column(String(255), unique=True, nullable=True)
    google_profile: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    email_verified: Mapped[bool] = mapped_column(Boolean, default=False)

    # Profile
    skills: Mapped[Optional[list]] = mapped_column(JSON, nullable=True)  # ARRAY type
    department: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    phone_extension: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    avatar: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    preferences: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    organization_id: Mapped[Optional[str]] = mapped_column(String(30), nullable=True)

    # Payment fields (Polar integration)
    polar_customer_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    subscription_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    subscription_status: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    subscribed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    subscription_end_date: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    # BYOK (Bring Your Own Keys) - encrypted JSON
    api_keys: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    last_activity_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    # Relationships
    # TODO: Add relationships when other models are created
    # organization: Mapped[Optional["Organization"]] = relationship(back_populates="users")
    # team_members: Mapped[list["TeamMember"]] = relationship(back_populates="user")
    # sessions: Mapped[list["UserSession"]] = relationship(back_populates="user")
    # agent_calls: Mapped[list["Call"]] = relationship(foreign_keys="Call.agent_id", back_populates="agent")

    def __repr__(self) -> str:
        return f"<User {self.email} ({self.role})>"

    @property
    def full_name(self) -> str:
        """Get user's full name"""
        return f"{self.first_name} {self.last_name}".strip()

    def is_admin(self) -> bool:
        """Check if user is admin"""
        return self.role == UserRole.ADMIN

    def is_supervisor(self) -> bool:
        """Check if user is supervisor"""
        return self.role == UserRole.SUPERVISOR

    def is_agent(self) -> bool:
        """Check if user is agent"""
        return self.role == UserRole.AGENT
