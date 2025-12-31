"""Comment schemas."""

from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class CommentCreate(BaseModel):
    content: str
    taskId: Optional[str] = None
    projectId: Optional[str] = None
    knowledgeItemId: Optional[str] = None
    mentions: Optional[List[str]] = None


class CommentUpdate(BaseModel):
    content: str


class CommentResponse(BaseModel):
    id: str
    content: str
    taskId: Optional[str] = None
    projectId: Optional[str] = None
    knowledgeItemId: Optional[str] = None
    userId: str
    userName: Optional[str] = None
    mentions: Optional[List[str]] = None
    createdAt: datetime
    updatedAt: Optional[datetime] = None

    class Config:
        from_attributes = True
