"""
Speak by Kraliki - Auth Schemas
"""

from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, ConfigDict, EmailStr


class LoginRequest(BaseModel):
    """Login request schema."""
    email: EmailStr
    password: str


class RegisterRequest(BaseModel):
    """Registration request schema."""
    email: EmailStr
    password: str
    first_name: str
    last_name: str
    company_name: str


class TokenResponse(BaseModel):
    """JWT token response."""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int


class UserResponse(BaseModel):
    """User response schema."""
    id: UUID
    email: str
    first_name: str
    last_name: str
    role: str
    company_id: UUID
    department_id: UUID | None
    is_active: bool
    is_verified: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class RefreshRequest(BaseModel):
    """Token refresh request."""
    refresh_token: str


class MagicLinkRequest(BaseModel):
    """Request for employee magic link."""
    token: str
