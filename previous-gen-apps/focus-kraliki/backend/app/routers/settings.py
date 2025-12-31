from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
import httpx

from app.core.security import get_current_user
from app.core.database import get_db
from app.models.user import User

router = APIRouter(prefix="/settings", tags=["settings"])

class OpenRouterKeyRequest(BaseModel):
    apiKey: str

class UsageStatsResponse(BaseModel):
    usageCount: int
    isPremium: bool
    remainingUsage: int | None
    hasCustomKey: bool

@router.post("/openrouter-key")
async def save_openrouter_key(
    key_data: OpenRouterKeyRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Save user's OpenRouter API key for BYOK"""
    current_user.openRouterApiKey = key_data.apiKey
    db.commit()
    return {"success": True, "message": "API key saved successfully"}

@router.delete("/openrouter-key")
async def delete_openrouter_key(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Remove user's OpenRouter API key"""
    current_user.openRouterApiKey = None
    db.commit()
    return {"success": True, "message": "API key removed"}

@router.post("/test-openrouter-key")
async def test_openrouter_key(key_data: OpenRouterKeyRequest):
    """Test if OpenRouter API key is valid"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                "https://openrouter.ai/api/v1/models",
                headers={"Authorization": f"Bearer {key_data.apiKey}"},
                timeout=10.0
            )
            if response.status_code == 200:
                return {"success": True, "message": "API key is valid"}
            else:
                return {"success": False, "message": f"API key validation failed: {response.status_code}"}
    except Exception as e:
        return {"success": False, "message": f"Error testing key: {str(e)}"}

@router.get("/usage-stats", response_model=UsageStatsResponse)
async def get_usage_stats(current_user: User = Depends(get_current_user)):
    """Get user's AI usage statistics"""
    remaining = None if current_user.isPremium or current_user.openRouterApiKey else max(0, 100 - current_user.usageCount)

    return UsageStatsResponse(
        usageCount=current_user.usageCount,
        isPremium=current_user.isPremium,
        remainingUsage=remaining,
        hasCustomKey=current_user.openRouterApiKey is not None
    )
