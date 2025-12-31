from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.schemas.user import UserProfileUpdate, UserPreferences, UserResponse
import json

router = APIRouter(prefix="/users", tags=["users"])

@router.get("/profile", response_model=UserResponse)
async def get_profile(current_user: User = Depends(get_current_user)):
    return UserResponse.model_validate(current_user)

@router.patch("/profile", response_model=UserResponse)
async def update_profile(
    profile_update: UserProfileUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    update_data = profile_update.model_dump(exclude_unset=True)

    for key, value in update_data.items():
        setattr(current_user, key, value)

    db.commit()
    db.refresh(current_user)

    return UserResponse.model_validate(current_user)

@router.get("/preferences")
async def get_preferences(
    current_user: User = Depends(get_current_user)
):
    preferences = current_user.preferences or {}
    return preferences

@router.post("/preferences")
async def update_preferences(
    preferences: UserPreferences,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Merge new preferences with existing
    current_prefs = current_user.preferences or {}
    new_prefs = preferences.model_dump(exclude_unset=True)
    current_prefs.update(new_prefs)

    current_user.preferences = current_prefs
    db.commit()

    return {"success": True, "preferences": current_prefs}
