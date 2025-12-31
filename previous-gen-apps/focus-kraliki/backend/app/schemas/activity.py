"""Activity schemas."""

from pydantic import BaseModel
from typing import Optional, Dict, Any, List
from datetime import datetime


class ActivityResponse(BaseModel):
    id: str
    activityType: str
    activityLabel: str  # Human-readable label
    userId: str
    userName: Optional[str] = None
    workspaceId: Optional[str] = None
    targetType: str
    targetId: str
    targetTitle: Optional[str] = None
    extraData: Optional[Dict[str, Any]] = None
    createdAt: datetime

    class Config:
        from_attributes = True


class ActivityFeedResponse(BaseModel):
    activities: List[ActivityResponse]
    hasMore: bool
    nextCursor: Optional[str] = None
