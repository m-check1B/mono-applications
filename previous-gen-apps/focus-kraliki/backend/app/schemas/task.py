from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from app.models.task import TaskStatus, EnergyLevel

class TaskBase(BaseModel):
    title: str
    description: Optional[str] = None
    priority: int = 1
    dueDate: Optional[datetime] = None
    estimatedMinutes: Optional[int] = None
    energyRequired: Optional[EnergyLevel] = EnergyLevel.low
    tags: List[str] = []
    projectId: Optional[str] = None
    workspaceId: Optional[str] = None
    assignedUserId: Optional[str] = None

class TaskCreate(TaskBase):
    pass

class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[TaskStatus] = None
    priority: Optional[int] = None
    dueDate: Optional[datetime] = None
    tags: Optional[List[str]] = None
    actualMinutes: Optional[float] = None
    energyRequired: Optional[EnergyLevel] = None
    workspaceId: Optional[str] = None
    assignedUserId: Optional[str] = None

class TaskResponse(TaskBase):
    id: str
    status: TaskStatus
    userId: Optional[str]
    completedAt: Optional[datetime]
    aiInsights: Optional[dict] = None
    urgencyScore: Optional[float] = None
    createdAt: datetime

    class Config:
        from_attributes = True

class TaskListResponse(BaseModel):
    tasks: List[TaskResponse]
    total: int

class ProjectCreate(BaseModel):
    name: str
    description: Optional[str] = None
    color: Optional[str] = None
    icon: Optional[str] = None

class ProjectResponse(BaseModel):
    id: str
    name: str
    description: Optional[str]
    color: Optional[str]
    icon: Optional[str]
    userId: str
    workspaceId: Optional[str] = None

    class Config:
        from_attributes = True
