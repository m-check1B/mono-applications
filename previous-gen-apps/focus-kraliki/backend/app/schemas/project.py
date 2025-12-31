"""
Project Schemas - Request/Response models
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class ProjectBase(BaseModel):
    """Base project schema."""
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    color: Optional[str] = None
    icon: Optional[str] = None


class ProjectCreate(ProjectBase):
    """Schema for creating a project."""
    workspaceId: Optional[str] = None


class ProjectUpdate(BaseModel):
    """Schema for updating a project (all fields optional)."""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    color: Optional[str] = None
    icon: Optional[str] = None


class ProjectResponse(ProjectBase):
    """Schema for project response."""
    id: str
    userId: str
    workspaceId: Optional[str] = None
    taskCount: Optional[int] = 0
    createdAt: Optional[datetime] = None

    class Config:
        from_attributes = True


class ProjectListResponse(BaseModel):
    """Schema for project list response."""
    projects: List[ProjectResponse]
    total: int
