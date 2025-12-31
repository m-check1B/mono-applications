"""Pydantic schemas for Voice by Kraliki API"""

from app.schemas.user import (
    UserCreate, UserUpdate, UserLogin, UserResponse, UserWithToken,
    TokenResponse, TokenRefresh
)
from app.schemas.call import CallCreate, CallUpdate, CallResponse, CallList
from app.schemas.campaign import CampaignCreate, CampaignUpdate, CampaignResponse, CampaignMetricResponse
from app.schemas.agent import AgentCreate, AgentUpdate, AgentResponse, AgentStatusUpdate

__all__ = [
    # User schemas
    "UserCreate", "UserUpdate", "UserLogin", "UserResponse", "UserWithToken",
    "TokenResponse", "TokenRefresh",
    # Call schemas
    "CallCreate", "CallUpdate", "CallResponse", "CallList",
    # Campaign schemas
    "CampaignCreate", "CampaignUpdate", "CampaignResponse", "CampaignMetricResponse",
    # Agent schemas
    "AgentCreate", "AgentUpdate", "AgentResponse", "AgentStatusUpdate",
]
