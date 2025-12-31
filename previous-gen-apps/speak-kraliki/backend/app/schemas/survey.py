"""
Speak by Kraliki - Survey Schemas
"""

from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, ConfigDict, Field


class QuestionConfig(BaseModel):
    """Individual question configuration."""
    id: int
    question: str
    follow_up_count: int = Field(default=1, ge=0, le=3)
    required: bool = True


class SurveyCreate(BaseModel):
    """Create survey request."""
    name: str = Field(min_length=1, max_length=100)
    description: str | None = None
    frequency: str = Field(default="monthly", pattern="^(once|weekly|monthly|quarterly)$")
    questions: list[QuestionConfig] = []
    custom_system_prompt: str | None = None
    starts_at: datetime | None = None
    ends_at: datetime | None = None
    target_departments: list[UUID] | None = None


class SurveyUpdate(BaseModel):
    """Update survey request."""
    name: str | None = None
    description: str | None = None
    status: str | None = Field(default=None, pattern="^(draft|scheduled|active|paused|completed)$")
    frequency: str | None = Field(default=None, pattern="^(once|weekly|monthly|quarterly)$")
    questions: list[QuestionConfig] | None = None
    custom_system_prompt: str | None = None
    starts_at: datetime | None = None
    ends_at: datetime | None = None
    target_departments: list[UUID] | None = None


class SurveyResponse(BaseModel):
    """Survey response schema."""
    id: UUID
    company_id: UUID
    name: str
    description: str | None
    status: str
    frequency: str
    questions: list[dict]
    custom_system_prompt: str | None
    starts_at: datetime | None
    ends_at: datetime | None
    target_departments: list[UUID] | None
    created_at: datetime
    updated_at: datetime
    # Computed fields
    conversation_count: int = 0
    completion_rate: float = 0.0

    model_config = ConfigDict(from_attributes=True)


class SurveyStats(BaseModel):
    """Survey statistics."""
    total_invited: int
    total_completed: int
    total_in_progress: int
    total_skipped: int
    completion_rate: float
    avg_duration_seconds: float | None
    avg_sentiment: float | None
