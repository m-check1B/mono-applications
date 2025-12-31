import logging

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime

from app.core.database import get_db

logger = logging.getLogger(__name__)
from app.models.user import User, AcademyStatus
from app.core.security import get_current_user, get_optional_user, generate_id

router = APIRouter(prefix="/academy", tags=["academy"])

class WaitlistEntry(BaseModel):
    email: EmailStr
    name: Optional[str] = None
    source: str = "linkedin"
    interest: str = "L1_STUDENT"

class WaitlistResponse(BaseModel):
    success: bool
    message: str

@router.post("/waitlist", response_model=WaitlistResponse)
async def join_waitlist(
    entry: WaitlistEntry,
    current_user: Optional[User] = Depends(get_optional_user),
    db: Session = Depends(get_db)
):
    """
    Join the AI Academy waitlist.
    Logs the interest, updates user status, and triggers n8n sequence.
    """
    # 1. Update user record if logged in
    if current_user:
        current_user.academyStatus = "WAITLIST"
        current_user.academyInterest = entry.interest
        db.commit()
    # For now, we'll log this to a dedicated knowledge item or just log it
    # Ideally, this should go to a 'leads' table in the future.
    
    # Trigger n8n orchestration flow for onboarding
    from app.services.n8n_client import get_n8n_client
    client = get_n8n_client()
    
    await client.orchestrate_flow("academy_waitlist_signup", {
        "email": entry.email,
        "name": entry.name,
        "source": entry.source,
        "interest": entry.interest,
        "timestamp": datetime.utcnow().isoformat()
    })
    
    return WaitlistResponse(
        success=True,
        message="You have been added to the waitlist. Protocol initiated."
    )

@router.get("/status")
async def get_academy_status():
    return {
        "active": True,
        "current_launch": "Level 1: Student",
        "price": 49.00,
        "currency": "EUR",
        "waitlist_count": 0  # Placeholder
    }
