from pydantic import BaseModel, EmailStr
from typing import Optional, List, Dict, Any
from datetime import datetime

from app.models.workspace import WorkspaceRole


class WorkspaceBase(BaseModel):
    name: str
    description: Optional[str] = None
    color: Optional[str] = None


class WorkspaceCreate(WorkspaceBase):
    settings: Optional[Dict[str, Any]] = None


class WorkspaceUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    color: Optional[str] = None
    settings: Optional[Dict[str, Any]] = None


class WorkspaceResponse(WorkspaceBase):
    id: str
    ownerId: str
    createdAt: datetime
    updatedAt: datetime
    settings: Optional[Dict[str, Any]] = None
    memberCount: Optional[int] = 0

    class Config:
        from_attributes = True


class WorkspaceListResponse(BaseModel):
    workspaces: List[WorkspaceResponse]
    activeWorkspaceId: Optional[str] = None


class WorkspaceMemberResponse(BaseModel):
    id: str
    workspaceId: str
    userId: str
    role: WorkspaceRole
    email: Optional[str] = None
    name: Optional[str] = None

    class Config:
        from_attributes = True


class WorkspaceMemberCreate(BaseModel):
    email: EmailStr
    role: WorkspaceRole = WorkspaceRole.MEMBER


class WorkspaceMemberUpdate(BaseModel):
    role: Optional[WorkspaceRole] = None
    permissions: Optional[Dict[str, Any]] = None


class WorkspaceSwitchRequest(BaseModel):
    workspaceId: str
