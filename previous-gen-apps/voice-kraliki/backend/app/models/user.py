"""User model for authentication and authorization."""

from datetime import UTC, datetime
from enum import Enum

from pydantic import BaseModel, EmailStr
from sqlalchemy import JSON, Boolean, Column, DateTime, Integer, String
from sqlalchemy import Enum as SQLEnum
from sqlalchemy.orm import relationship

from app.database import Base


class UserRole(str, Enum):
    """User roles for authorization."""

    USER = "USER"
    ADMIN = "ADMIN"
    AGENT = "AGENT"
    SUPERVISOR = "SUPERVISOR"
    ANALYST = "ANALYST"


class Permission(str, Enum):
    """Permissions for fine-grained access control."""

    # User management
    USER_READ = "user:read"
    USER_WRITE = "user:write"
    USER_DELETE = "user:delete"

    # Session management
    SESSION_READ = "session:read"
    SESSION_WRITE = "session:write"
    SESSION_DELETE = "session:delete"

    # Campaign management
    CAMPAIGN_READ = "campaign:read"
    CAMPAIGN_WRITE = "campaign:write"
    CAMPAIGN_DELETE = "campaign:delete"

    # Provider management
    PROVIDER_READ = "provider:read"
    PROVIDER_WRITE = "provider:write"
    PROVIDER_DELETE = "provider:delete"

    # Analytics
    ANALYTICS_READ = "analytics:read"
    ANALYTICS_WRITE = "analytics:write"

    # System administration
    SYSTEM_ADMIN = "system:admin"
    SYSTEM_MONITOR = "system:monitor"


class User(Base):
    """User model for authentication and authorization."""

    __tablename__ = "users"

    # UUID stored as string (36 chars: 8-4-4-4-12 with hyphens)
    id = Column(String(36), primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    full_name = Column(String(255), nullable=False)
    password_hash = Column(String(255), nullable=False)
    organization = Column(String(255), nullable=True)
    role = Column(SQLEnum(UserRole, name="userrole"), default=UserRole.AGENT, nullable=False)

    # Status and metadata
    is_active = Column(Boolean, default=True, nullable=False)
    is_verified = Column(Boolean, default=False, nullable=False)
    last_login_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(UTC), nullable=False)
    updated_at = Column(DateTime, default=lambda: datetime.now(UTC), onupdate=lambda: datetime.now(UTC), nullable=False)

    # Profile and preferences
    phone_number = Column(String(20), nullable=True)
    avatar_url = Column(String(500), nullable=True)
    timezone = Column(String(50), default="UTC", nullable=False)
    language = Column(String(10), default="en", nullable=False)
    preferences = Column(JSON, default=dict, nullable=False)
    permissions = Column(JSON, default=list, nullable=False)

    # Security
    failed_login_attempts = Column(Integer, default=0, nullable=False)
    locked_until = Column(DateTime, nullable=True)
    password_changed_at = Column(DateTime, default=lambda: datetime.now(UTC), nullable=False)
    two_factor_enabled = Column(Boolean, default=False, nullable=False)
    two_factor_secret = Column(String(255), nullable=True)

    # Email verification
    email_verification_token = Column(String(255), nullable=True)
    email_verification_token_expires = Column(DateTime, nullable=True)

    # Password reset
    password_reset_token = Column(String(255), nullable=True)
    password_reset_token_expires = Column(DateTime, nullable=True)

    # Billing
    stripe_customer_id = Column(String(255), nullable=True, index=True)
    stripe_subscription_id = Column(String(255), nullable=True, index=True)
    is_premium = Column(Boolean, default=False, nullable=False)

    # Relationships
    sessions = relationship("CallSession", back_populates="user", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<User(id={self.id}, email={self.email}, role={self.role})>"


# Pydantic models for API
class UserBase(BaseModel):
    """Base user model."""

    email: EmailStr
    full_name: str
    phone_number: str | None = None
    timezone: str = "UTC"
    language: str = "en"


class UserCreate(UserBase):
    """User creation model."""

    password: str
    role: UserRole = UserRole.AGENT


class UserUpdate(BaseModel):
    """User update model."""

    full_name: str | None = None
    phone_number: str | None = None
    timezone: str | None = None
    language: str | None = None
    is_active: bool | None = None
    role: UserRole | None = None
    preferences: dict | None = None
    permissions: list[str] | None = None


class UserResponse(UserBase):
    """User response model."""

    id: str
    role: UserRole
    is_active: bool
    is_verified: bool
    last_login_at: datetime | None = None
    created_at: datetime
    updated_at: datetime
    avatar_url: str | None = None
    two_factor_enabled: bool
    permissions: list[str]
    is_premium: bool
    stripe_customer_id: str | None = None
    stripe_subscription_id: str | None = None

    class Config:
        from_attributes = True


class UserLogin(BaseModel):
    """User login model."""

    email: EmailStr
    password: str
    remember_me: bool = False


class UserPasswordChange(BaseModel):
    """Password change model."""

    current_password: str
    new_password: str


class UserPasswordReset(BaseModel):
    """Password reset model."""

    email: EmailStr


class UserPasswordResetConfirm(BaseModel):
    """Password reset confirmation model."""

    token: str
    new_password: str


class UserTwoFactorSetup(BaseModel):
    """Two-factor setup model."""

    secret: str
    qr_code: str
    backup_codes: list[str]


class UserTwoFactorVerify(BaseModel):
    """Two-factor verification model."""

    code: str
