
from fastapi import APIRouter, HTTPException

from .simple_models import ExecutionRequest, ExecutionResponse, ResponseRequest, SimpleCampaign
from .simple_service import SimpleCampaignService

router = APIRouter(prefix="/simple-campaigns", tags=["simple-campaigns"])
campaign_service = SimpleCampaignService()


@router.get("/", response_model=list[SimpleCampaign])
async def get_all_campaigns():
    """Get all available campaigns"""
    return campaign_service.get_all_campaigns()


@router.get("/{campaign_id}", response_model=SimpleCampaign)
async def get_campaign(campaign_id: int):
    """Get a specific campaign by ID"""
    campaign = campaign_service.get_campaign_by_id(campaign_id)
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    return campaign


@router.post("/start", response_model=ExecutionResponse)
async def start_campaign_execution(request: ExecutionRequest):
    """Start executing a campaign"""
    response = campaign_service.start_execution(request.campaign_id)
    if not response:
        raise HTTPException(status_code=404, detail="Campaign not found or has no steps")
    return response


@router.post("/respond", response_model=ExecutionResponse)
async def process_response(request: ResponseRequest):
    """Process a response and get next step"""
    response = campaign_service.process_response(request.session_id, request.response)
    if not response:
        raise HTTPException(status_code=404, detail="Session not found or inactive")
    return response


@router.get("/session/{session_id}")
async def get_session(session_id: str):
    """Get session details"""
    session = campaign_service.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return session


@router.post("/session/{session_id}/stop")
async def stop_session(session_id: str):
    """Stop an active session"""
    success = campaign_service.stop_session(session_id)
    if not success:
        raise HTTPException(status_code=404, detail="Session not found")
    return {"message": "Session stopped successfully"}
