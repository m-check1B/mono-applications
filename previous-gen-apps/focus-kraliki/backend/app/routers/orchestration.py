from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Dict, Any, Optional
from pydantic import BaseModel

from app.core.database import get_db
from app.routers.auth import get_current_user
from app.models.user import User
from app.services.n8n_client import get_n8n_client
from app.services.workspace_service import WorkspaceService

router = APIRouter(prefix="/orchestration", tags=["orchestration"])

class OrchestrationRequest(BaseModel):
    context: Dict[str, Any] = {}

class OrchestrationResponse(BaseModel):
    success: bool
    message: str
    data: Optional[Dict[str, Any]] = None

@router.post("/{flow_id}", response_model=OrchestrationResponse)
async def trigger_orchestration(
    flow_id: str,
    request: OrchestrationRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Trigger a specific n8n orchestration flow.
    
    This is the primary bridge between Focus by Kraliki (Web/Voice by Kraliki) and n8n.
    """
    # 1. Get workspace settings (for BYO n8n)
    workspace_id = current_user.activeWorkspaceId
    workspace_settings = None
    if workspace_id:
        workspace_settings = WorkspaceService.get_settings(workspace_id, db)
    
    # 2. Initialize n8n client
    client = get_n8n_client(workspace_settings)
    
    # 3. Trigger flow
    try:
        # Add user context to the request
        context = {
            **request.context,
            "user_id": current_user.id,
            "workspace_id": workspace_id,
            "triggered_at": "now"
        }
        
        result = await client.orchestrate_flow(flow_id, context)
        
        return OrchestrationResponse(
            success=True,
            message=f"Flow '{flow_id}' triggered successfully",
            data=result
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to trigger orchestration flow: {str(e)}"
        )
