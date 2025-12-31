"""Team schemas - Pydantic models for team validation"""

from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from datetime import datetime


class TeamCreate(BaseModel):
    """Schema for creating a team"""
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=1000)
    supervisor_id: Optional[str] = None
    max_members: int = Field(default=10, ge=1, le=100)
    skills: Optional[list[str]] = None
    extra_metadata: Optional[dict] = None


class TeamUpdate(BaseModel):
    """Schema for updating a team"""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=1000)
    supervisor_id: Optional[str] = None
    max_members: Optional[int] = Field(None, ge=1, le=100)
    skills: Optional[list[str]] = None
    extra_metadata: Optional[dict] = None


class TeamResponse(BaseModel):
    """Schema for team response"""
    id: str
    name: str
    description: Optional[str]
    organization_id: str
    supervisor_id: Optional[str]
    max_members: int
    current_members: int
    skills: list[str]
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class TeamListResponse(BaseModel):
    """Schema for team list response with pagination"""
    teams: list[TeamResponse]
    total: int
    skip: int
    limit: int


class TeamMemberAdd(BaseModel):
    """Schema for adding a team member"""
    user_id: str
    role: str = Field(default="member", max_length=50)


class TeamMemberResponse(BaseModel):
    """Schema for team member response"""
    id: str
    team_id: str
    user_id: str
    role: str
    joined_at: datetime

    model_config = ConfigDict(from_attributes=True)
