"""
Campaign API routes for managing call campaign scripts.
"""

from typing import Any

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

from .execution import ExecutionContext, ScriptExecutor
from .models import Campaign, CampaignType
from .service import CampaignService

router = APIRouter(prefix="/campaigns", tags=["campaigns"])

# Initialize the campaign service
campaign_service = CampaignService()


# Pydantic models for execution API
class ExecutionStartRequest(BaseModel):
    campaign_id: int
    session_id: str | None = None


class ExecutionResponseRequest(BaseModel):
    session_id: str
    response: Any


class ExecutionSessionResponse(BaseModel):
    session_id: str
    campaign_id: int
    current_step: str
    step_index: int
    state: str
    collected_data: dict[str, Any]
    execution_history: list[dict[str, Any]]
    disposition: str | None = None
    error_message: str | None = None


# In-memory session storage (in production, use Redis or database)
execution_sessions: dict[str, ExecutionContext] = {}


@router.get("/", response_model=list[Campaign])
async def get_all_campaigns():
    """Get all available campaigns."""
    try:
        campaigns = campaign_service.get_all_campaigns()
        return campaigns
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/summary")
async def get_campaign_summary():
    """Get a summary of available campaigns."""
    try:
        summary = campaign_service.get_campaign_summary()
        return summary
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{campaign_id}", response_model=Campaign)
async def get_campaign(campaign_id: int):
    """Get a specific campaign by ID."""
    try:
        campaign = campaign_service.get_campaign(campaign_id)
        if campaign is None:
            raise HTTPException(status_code=404, detail="Campaign not found")
        return campaign
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/type/{campaign_type}", response_model=list[Campaign])
async def get_campaigns_by_type(campaign_type: CampaignType):
    """Get campaigns by type (outbound/inbound)."""
    try:
        campaigns = campaign_service.get_campaigns_by_type(campaign_type)
        return campaigns
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/language/{language}", response_model=list[Campaign])
async def get_campaigns_by_language(language: str):
    """Get campaigns by language code."""
    try:
        campaigns = campaign_service.get_campaigns_by_language(language)
        return campaigns
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/category/{category}", response_model=list[Campaign])
async def get_campaigns_by_category(category: str):
    """Get campaigns by category."""
    try:
        campaigns = campaign_service.get_campaigns_by_category(category)
        return campaigns
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/search", response_model=list[Campaign])
async def search_campaigns(q: str = Query(..., description="Search query")):
    """Search campaigns by title or campaign name."""
    try:
        campaigns = campaign_service.search_campaigns(q)
        return campaigns
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/reload")
async def reload_campaigns():
    """Force reload of all campaigns from disk."""
    try:
        campaign_service.reload_campaigns()
        return {"message": "Campaigns reloaded successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Script Execution Endpoints

@router.post("/execution/start")
async def start_script_execution(request: ExecutionStartRequest):
    """Start executing a campaign script."""
    try:
        # Get the campaign
        campaign = campaign_service.get_campaign(request.campaign_id)
        if campaign is None:
            raise HTTPException(status_code=404, detail="Campaign not found")

        # Create executor and start execution
        executor = ScriptExecutor(campaign)
        context = executor.start_execution()

        # Override session ID if provided
        if request.session_id:
            context.session_id = request.session_id

        # Store session
        execution_sessions[context.session_id] = context

        # Execute first step
        result = executor.execute_step(context)

        return {
            "session": ExecutionSessionResponse(
                session_id=context.session_id,
                campaign_id=context.campaign_id,
                current_step=context.current_step,
                step_index=context.step_index,
                state=context.state.value,
                collected_data=context.collected_data,
                execution_history=context.execution_history,
                disposition=context.disposition,
                error_message=context.error_message
            ),
            "result": {
                "success": result.success,
                "message": result.message,
                "data_to_collect": result.data_to_collect,
                "next_step": result.next_step,
                "should_end_call": result.should_end_call,
                "should_transfer": result.should_transfer,
                "transfer_details": result.transfer_details,
                "disposition": result.disposition,
                "error": result.error
            }
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/execution/respond")
async def process_execution_response(request: ExecutionResponseRequest):
    """Process a customer response in script execution."""
    try:
        # Get session
        if request.session_id not in execution_sessions:
            raise HTTPException(status_code=404, detail="Execution session not found")

        context = execution_sessions[request.session_id]

        # Get campaign and executor
        campaign = campaign_service.get_campaign(context.campaign_id)
        if campaign is None:
            raise HTTPException(status_code=404, detail="Campaign not found")

        executor = ScriptExecutor(campaign)

        # Process response
        result = executor.process_response(context, request.response)

        # Update session
        execution_sessions[request.session_id] = context

        return {
            "session": ExecutionSessionResponse(
                session_id=context.session_id,
                campaign_id=context.campaign_id,
                current_step=context.current_step,
                step_index=context.step_index,
                state=context.state.value,
                collected_data=context.collected_data,
                execution_history=context.execution_history,
                disposition=context.disposition,
                error_message=context.error_message
            ),
            "result": {
                "success": result.success,
                "message": result.message,
                "data_to_collect": result.data_to_collect,
                "next_step": result.next_step,
                "should_end_call": result.should_end_call,
                "should_transfer": result.should_transfer,
                "transfer_details": result.transfer_details,
                "disposition": result.disposition,
                "error": result.error
            }
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/execution/{session_id}")
async def get_execution_session(session_id: str):
    """Get current execution session state."""
    try:
        if session_id not in execution_sessions:
            raise HTTPException(status_code=404, detail="Execution session not found")

        context = execution_sessions[session_id]

        return ExecutionSessionResponse(
            session_id=context.session_id,
            campaign_id=context.campaign_id,
            current_step=context.current_step,
            step_index=context.step_index,
            state=context.state.value,
            collected_data=context.collected_data,
            execution_history=context.execution_history,
            disposition=context.disposition,
            error_message=context.error_message
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/execution/{session_id}")
async def end_execution_session(session_id: str):
    """End an execution session."""
    try:
        if session_id not in execution_sessions:
            raise HTTPException(status_code=404, detail="Execution session not found")

        # Remove session
        del execution_sessions[session_id]

        return {"message": "Execution session ended successfully"}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/execution")
async def list_execution_sessions():
    """List all active execution sessions."""
    try:
        sessions = []
        for session_id, context in execution_sessions.items():
            sessions.append(ExecutionSessionResponse(
                session_id=context.session_id,
                campaign_id=context.campaign_id,
                current_step=context.current_step,
                step_index=context.step_index,
                state=context.state.value,
                collected_data=context.collected_data,
                execution_history=context.execution_history,
                disposition=context.disposition,
                error_message=context.error_message
            ))

        return {"sessions": sessions, "total": len(sessions)}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
