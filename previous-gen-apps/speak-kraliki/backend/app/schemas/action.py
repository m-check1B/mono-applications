"""
Speak by Kraliki - Action Schemas
Action Loop v2.0: Track leadership responses to feedback
"""

from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, ConfigDict, Field


class ActionCreate(BaseModel):
    """Create action request."""
    topic: str = Field(min_length=1, max_length=200)
    description: str | None = None
    department_id: UUID | None = None  # For RBAC department scoping
    created_from_alert_id: UUID | None = None
    assigned_to: UUID | None = None
    priority: str = Field(default="medium", pattern="^(low|medium|high)$")
    visible_to_employees: bool = True
    public_message: str | None = None


class ActionUpdate(BaseModel):
    """Update action request."""
    topic: str | None = None
    description: str | None = None
    status: str | None = Field(default=None, pattern="^(new|heard|in_progress|resolved)$")
    assigned_to: UUID | None = None
    notes: str | None = None
    priority: str | None = Field(default=None, pattern="^(low|medium|high)$")
    visible_to_employees: bool | None = None
    public_message: str | None = None


class ActionResponse(BaseModel):
    """Full action response for dashboard."""
    id: UUID
    company_id: UUID
    department_id: UUID | None = None  # For RBAC department scoping
    topic: str
    description: str | None
    status: str
    created_from_alert_id: UUID | None
    assigned_to: UUID | None
    assigned_to_name: str | None = None
    notes: str | None
    public_message: str | None
    visible_to_employees: bool
    priority: str
    created_at: datetime
    updated_at: datetime
    resolved_at: datetime | None

    model_config = ConfigDict(from_attributes=True)


class ActionPublic(BaseModel):
    """Public action view for employees (Action Loop widget)."""
    id: UUID
    topic: str
    status: str
    public_message: str | None
    created_at: datetime
    resolved_at: datetime | None

    # Status labels for display
    @property
    def status_label(self) -> str:
        labels = {
            "new": "Novy",
            "heard": "Slysime vas",
            "in_progress": "Resime",
            "resolved": "Vyreseno"
        }
        return labels.get(self.status, self.status)

    model_config = ConfigDict(from_attributes=True)
