from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime


class WorkflowStep(BaseModel):
    step: int
    action: str
    estimatedMinutes: int
    dependencies: List[int] = []
    type: str = "manual"  # manual or automated


class WorkflowTemplateCreate(BaseModel):
    name: str
    description: Optional[str] = None
    category: Optional[str] = None
    icon: Optional[str] = None
    steps: List[Dict[str, Any]]
    tags: List[str] = []
    isPublic: bool = False
    isSystem: bool = False


class WorkflowTemplateUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    icon: Optional[str] = None
    steps: Optional[List[Dict[str, Any]]] = None
    tags: Optional[List[str]] = None
    isPublic: Optional[bool] = None


class WorkflowTemplateResponse(BaseModel):
    id: str
    userId: Optional[str]
    name: str
    description: Optional[str]
    category: Optional[str]
    icon: Optional[str]
    steps: List[Dict[str, Any]]
    totalEstimatedMinutes: Optional[int]
    tags: List[str]
    isPublic: bool
    isSystem: bool
    usageCount: int
    createdAt: datetime

    class Config:
        from_attributes = True


class WorkflowListResponse(BaseModel):
    templates: List[WorkflowTemplateResponse]
    total: int


class WorkflowExecuteRequest(BaseModel):
    templateId: str
    customTitle: Optional[str] = None
    priority: Optional[int] = None
    startDate: Optional[str] = None
    additionalTags: List[str] = []


class WorkflowExecuteResponse(BaseModel):
    success: bool
    message: str
    parentTaskId: str
    createdTasks: List[Dict[str, Any]]
    totalTasks: int
