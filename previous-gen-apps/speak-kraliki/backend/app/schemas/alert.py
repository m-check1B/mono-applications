"""
Speak by Kraliki - Alert Schemas
"""

from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, ConfigDict, Field


class AlertResponse(BaseModel):
    """Alert response schema."""
    id: UUID
    company_id: UUID
    conversation_id: UUID | None
    type: str
    severity: str
    department_id: UUID | None
    department_name: str | None = None
    description: str
    trigger_keywords: str | None
    is_read: bool
    is_resolved: bool
    created_at: datetime
    read_at: datetime | None
    resolved_at: datetime | None
    # Related action
    action_id: UUID | None = None

    model_config = ConfigDict(from_attributes=True)


class AlertUpdate(BaseModel):
    """Update alert request."""
    is_read: bool | None = None
    is_resolved: bool | None = None


class AlertTypeInfo(BaseModel):
    """Alert type information."""
    type: str
    label: str
    description: str
    severity: str

    @classmethod
    def get_all_types(cls) -> list["AlertTypeInfo"]:
        return [
            cls(
                type="flight_risk",
                label="Flight Risk",
                description="Employee may be looking to leave",
                severity="high"
            ),
            cls(
                type="burnout",
                label="Burnout",
                description="Signs of exhaustion or overwhelm",
                severity="high"
            ),
            cls(
                type="toxic_manager",
                label="Toxic Manager",
                description="Negative feedback about management",
                severity="high"
            ),
            cls(
                type="team_conflict",
                label="Team Conflict",
                description="Multiple people report similar issues",
                severity="medium"
            ),
            cls(
                type="low_engagement",
                label="Low Engagement",
                description="Consistently low sentiment over time",
                severity="medium"
            ),
            cls(
                type="sentiment_drop",
                label="Sentiment Drop",
                description="Department sentiment dropped significantly",
                severity="medium"
            ),
        ]
