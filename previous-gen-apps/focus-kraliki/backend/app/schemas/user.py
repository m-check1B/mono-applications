from pydantic import BaseModel, EmailStr
from typing import Optional, Dict, Any
from datetime import datetime
from app.models.user import Role, UserStatus

class UserBase(BaseModel):
    email: EmailStr
    username: Optional[str] = None
    firstName: Optional[str] = None
    lastName: Optional[str] = None

class UserCreate(UserBase):
    password: str
    name: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(UserBase):
    id: str
    role: Role
    status: UserStatus
    createdAt: datetime
    usageCount: int = 0
    isPremium: bool = False
    activeWorkspaceId: Optional[str] = None

    class Config:
        from_attributes = True

class UserWithToken(BaseModel):
    user: UserResponse
    token: str
    access_token: Optional[str] = None
    refreshToken: Optional[str] = None  # Ed25519 refresh token

class UserProfileUpdate(BaseModel):
    firstName: Optional[str] = None
    lastName: Optional[str] = None
    username: Optional[str] = None
    phoneExtension: Optional[str] = None
    department: Optional[str] = None

class UserPreferences(BaseModel):
    theme: Optional[str] = None
    workHoursStart: Optional[str] = None
    workHoursEnd: Optional[str] = None
    breakInterval: Optional[int] = None
    dailyGoal: Optional[int] = None
    notifications: Optional[Dict[str, bool]] = None
    aiSettings: Optional[Dict[str, Any]] = None

class GoogleAuthUrlRequest(BaseModel):
    state: str

class GoogleAuthUrlResponse(BaseModel):
    url: str
    csrfToken: str

class GoogleLoginRequest(BaseModel):
    idToken: str
    csrfToken: str
    state: str

class GoogleLinkRequest(BaseModel):
    idToken: str
    csrfToken: str
    state: str
