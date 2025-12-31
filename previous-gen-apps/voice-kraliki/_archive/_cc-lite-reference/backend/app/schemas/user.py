"""Pydantic schemas for User endpoints"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, Field, ConfigDict

from app.models.user import UserRole, UserStatus, AuthProvider


# Base schemas
class UserBase(BaseModel):
    """Base user schema"""
    email: EmailStr
    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)
    role: UserRole = UserRole.AGENT
    department: Optional[str] = None
    phone_extension: Optional[str] = None


# Request schemas
class UserCreate(UserBase):
    """Schema for creating a new user"""
    password: str = Field(..., min_length=8, max_length=100)
    username: Optional[str] = None
    organization_id: Optional[str] = None


class UserUpdate(BaseModel):
    """Schema for updating a user"""
    first_name: Optional[str] = Field(None, min_length=1, max_length=100)
    last_name: Optional[str] = Field(None, min_length=1, max_length=100)
    department: Optional[str] = None
    phone_extension: Optional[str] = None
    skills: Optional[list[str]] = None
    avatar: Optional[str] = None
    preferences: Optional[dict] = None


class UserLogin(BaseModel):
    """Schema for user login"""
    email: EmailStr
    password: str


# Response schemas
class UserResponse(UserBase):
    """Schema for user response"""
    id: str
    username: Optional[str] = None
    status: UserStatus
    auth_provider: AuthProvider
    email_verified: bool
    skills: list[str] = []
    avatar: Optional[str] = None
    organization_id: Optional[str] = None
    created_at: datetime
    last_login_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class UserWithToken(BaseModel):
    """Schema for login response with token"""
    user: UserResponse
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class TokenResponse(BaseModel):
    """Schema for token response"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class TokenRefresh(BaseModel):
    """Schema for token refresh"""
    refresh_token: str
