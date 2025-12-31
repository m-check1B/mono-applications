from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field, field_validator

# Import existing campaign models
from app.campaigns.models import Campaign


class ScriptLanguage(str, Enum):
    ENGLISH = "en"
    SPANISH = "es"
    FRENCH = "fr"
    GERMAN = "de"
    CHINESE = "zh"
    JAPANESE = "ja"


class ScriptStatus(str, Enum):
    DRAFT = "draft"
    ACTIVE = "active"
    ARCHIVED = "archived"
    TESTING = "testing"


class CampaignScript(BaseModel):
    """Enhanced campaign script model that extends the existing Campaign structure."""
    id: int | None = None
    title: str = Field(..., min_length=1, max_length=255)
    description: str | None = Field(None, max_length=1000)
    campaign_data: Campaign  # Use existing Campaign model
    version: int = Field(default=1, ge=1)
    language: ScriptLanguage = Field(default=ScriptLanguage.ENGLISH)
    company_id: int = Field(..., gt=0)
    status: ScriptStatus = Field(default=ScriptStatus.DRAFT)
    is_template: bool = Field(default=False)
    tags: list[str] = Field(default_factory=list)
    usage_count: int = Field(default=0)
    success_rate: float | None = Field(None, ge=0, le=100)
    average_duration: int | None = Field(None, ge=0)  # in seconds
    created_at: datetime | None = None
    updated_at: datetime | None = None
    created_by: int | None = None
    last_used: datetime | None = None

    @field_validator('title')
    @classmethod
    def validate_title(cls, v):
        if not v or not v.strip():
            raise ValueError('Title cannot be empty')
        return v.strip()

    @field_validator('tags')
    @classmethod
    def validate_tags(cls, v):
        if len(v) > 10:
            raise ValueError('Maximum 10 tags allowed')
        return [tag.strip() for tag in v if tag.strip()]

    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class CampaignScriptCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    description: str | None = Field(None, max_length=1000)
    campaign_data: Campaign
    language: ScriptLanguage = Field(default=ScriptLanguage.ENGLISH)
    company_id: int = Field(..., gt=0)
    is_template: bool = Field(default=False)
    tags: list[str] = Field(default_factory=list)


class CampaignScriptUpdate(BaseModel):
    title: str | None = Field(None, min_length=1, max_length=255)
    description: str | None = Field(None, max_length=1000)
    campaign_data: Campaign | None = None
    language: ScriptLanguage | None = None
    status: ScriptStatus | None = None
    is_template: bool | None = None
    tags: list[str] | None = None


class CampaignScriptVersion(BaseModel):
    """Version history for campaign scripts."""
    id: int | None = None
    script_id: int = Field(..., gt=0)
    version: int = Field(..., ge=1)
    title: str
    campaign_data: Campaign
    changes_summary: str | None = Field(None, max_length=1000)
    created_at: datetime | None = None
    created_by: int | None = None

    class Config:
        from_attributes = True


class ScriptTemplate(BaseModel):
    """Template for creating new scripts."""
    id: int | None = None
    name: str = Field(..., min_length=1, max_length=255)
    description: str = Field(..., min_length=1, max_length=1000)
    category: str = Field(..., min_length=1, max_length=100)
    campaign_template: Campaign
    tags: list[str] = Field(default_factory=list)
    usage_count: int = Field(default=0)
    is_public: bool = Field(default=True)
    created_at: datetime | None = None
    created_by: int | None = None

    class Config:
        from_attributes = True


class ScriptAnalytics(BaseModel):
    """Analytics data for script performance."""
    script_id: int
    total_calls: int
    successful_calls: int
    failed_calls: int
    average_duration: float
    success_rate: float
    common_dispositions: dict[str, int]
    drop_off_points: list[dict[str, Any]]
    performance_by_time: dict[str, float]
    last_updated: datetime

    class Config:
        from_attributes = True


class ScriptSearch(BaseModel):
    """Search parameters for finding scripts."""
    query: str | None = None
    company_id: int | None = None
    language: ScriptLanguage | None = None
    status: ScriptStatus | None = None
    tags: list[str] | None = None
    is_template: bool | None = None
    min_success_rate: float | None = Field(None, ge=0, le=100)
    max_success_rate: float | None = Field(None, ge=0, le=100)
    sort_by: str = Field(default="updated_at")
    sort_order: str = Field(default="desc")
    limit: int = Field(default=20, ge=1, le=100)
    offset: int = Field(default=0, ge=0)


class ScriptValidation(BaseModel):
    """Validation result for script content."""
    is_valid: bool
    errors: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
    suggestions: list[str] = Field(default_factory=list)
    estimated_duration: int | None = None  # in seconds
    complexity_score: int | None = Field(None, ge=1, le=10)
