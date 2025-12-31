"""
Speak by Kraliki - API Routers
"""

from app.routers.auth import router as auth_router
from app.routers.surveys import router as surveys_router
from app.routers.conversations import router as conversations_router
from app.routers.voice import router as voice_router
from app.routers.actions import router as actions_router
from app.routers.alerts import router as alerts_router
from app.routers.insights import router as insights_router
from app.routers.employees import router as employees_router
from app.routers.telephony import router as telephony_router
from app.routers.usage import router as usage_router
from app.routers.billing import router as billing_router

__all__ = [
    "auth_router",
    "surveys_router",
    "conversations_router",
    "voice_router",
    "actions_router",
    "alerts_router",
    "insights_router",
    "employees_router",
    "telephony_router",
    "usage_router",
    "billing_router",
]
