"""Scorecard API endpoints."""

from fastapi import APIRouter, Depends

from app.auth.jwt_auth import get_current_user
from app.models.scorecard import ScorecardRequest, ScorecardResponse
from app.models.user import User
from app.services.enhanced_scorecard_service import EnhancedScorecardService

router = APIRouter(prefix="/api/scorecards", tags=["scorecards"])


@router.post("/generate", response_model=ScorecardResponse)
async def generate_scorecard(
    payload: ScorecardRequest,
    current_user: User = Depends(get_current_user),
) -> ScorecardResponse:
    """Generate a scorecard for an agent transcript using AI analysis."""
    service = EnhancedScorecardService()
    return await service.generate_scorecard(payload)
