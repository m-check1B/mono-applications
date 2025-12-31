from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime

# Profile Schemas
class ShadowProfileBase(BaseModel):
    archetype: str = Field(..., description="Jungian archetype (warrior, sage, lover, creator, caregiver, explorer)")

class ShadowProfileCreate(ShadowProfileBase):
    pass

class ShadowProfileResponse(ShadowProfileBase):
    id: str
    user_id: str
    unlock_day: int
    total_days: int
    insights_data: Optional[Dict[str, Any]] = None
    patterns: Optional[Dict[str, Any]] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# Insight Schemas
class ShadowInsightBase(BaseModel):
    day: int = Field(..., ge=1, le=30)
    insight_type: str = Field(..., description="awareness, understanding, or integration")
    content: str

class ShadowInsightCreate(ShadowInsightBase):
    profile_id: str

class ShadowInsightResponse(ShadowInsightBase):
    id: str
    profile_id: str
    unlocked: bool
    unlocked_at: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True

# Analysis Request/Response
class ShadowAnalysisRequest(BaseModel):
    userId: str
    taskPatterns: List[Dict[str, Any]] = []
    timeRange: Optional[str] = "7d"

class ShadowPattern(BaseModel):
    pattern: str
    description: str
    frequency: int
    severity: str  # "low", "medium", "high"

# Daily Insight Response
class DailyInsightResponse(BaseModel):
    locked: bool
    day: int
    insight: Optional[ShadowInsightResponse] = None
    archetype: Optional[str] = None
    progress: str  # e.g., "5/30"
    message: Optional[str] = None  # For locked insights

# Progress Response
class ProgressResponse(BaseModel):
    unlock_day: int
    total_days: int
    unlocked_insights: int
    archetype: str
    completion_percentage: float

# Unlock Response
class UnlockResponse(BaseModel):
    unlocked: bool
    new_day: Optional[int] = None
    insight: Optional[ShadowInsightResponse] = None
    message: str
