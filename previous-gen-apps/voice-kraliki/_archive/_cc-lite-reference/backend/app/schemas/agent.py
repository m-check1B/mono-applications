"""Pydantic schemas for Agent endpoints"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict

from app.models.agent import AgentStatus


class AgentBase(BaseModel):
    """Base agent schema"""
    status: AgentStatus = AgentStatus.OFFLINE
    max_capacity: int = Field(1, ge=1, le=10)
    skills: list[str] = []
    language: str = "en"


class AgentCreate(AgentBase):
    """Schema for creating an agent"""
    user_id: str
    metadata: Optional[dict] = None


class AgentUpdate(BaseModel):
    """Schema for updating an agent"""
    status: Optional[AgentStatus] = None
    max_capacity: Optional[int] = Field(None, ge=1, le=10)
    skills: Optional[list[str]] = None
    language: Optional[str] = None
    metadata: Optional[dict] = None


class AgentResponse(AgentBase):
    """Schema for agent response"""
    id: str
    user_id: str
    current_load: int
    metadata: Optional[dict] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

    @property
    def is_available(self) -> bool:
        """Check if agent is available"""
        return self.status == AgentStatus.AVAILABLE and self.current_load < self.max_capacity

    @property
    def capacity_percentage(self) -> float:
        """Get capacity usage percentage"""
        if self.max_capacity == 0:
            return 0.0
        return (self.current_load / self.max_capacity) * 100


class AgentStatusUpdate(BaseModel):
    """Schema for quick status updates"""
    status: AgentStatus
