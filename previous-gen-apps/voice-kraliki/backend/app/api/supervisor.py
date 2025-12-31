"""Supervisor cockpit API endpoints."""


from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.jwt_auth import get_current_user
from app.database import get_db
from app.models.supervisor import (
    ActiveCallCreate,
    ActiveCallResponse,
    ActiveCallStatus,
    ActiveCallUpdate,
    AlertSeverity,
    CallQueueCreate,
    CallQueueResponse,
    CallQueueStatus,
    CallQueueUpdate,
    PerformanceAlertCreate,
    PerformanceAlertResponse,
    SupervisorInterventionCreate,
    SupervisorInterventionResponse,
)
from app.models.user import User
from app.services.supervisor import SupervisorService

router = APIRouter(prefix="/api/supervisor", tags=["supervisor"])


# ===== Call Queue Endpoints =====

@router.post("/queue", response_model=CallQueueResponse)
async def add_to_queue(
    queue_data: CallQueueCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Add a call to the queue."""
    service = SupervisorService()
    return await service.add_to_queue(db, queue_data)


@router.get("/queue", response_model=list[CallQueueResponse])
async def get_queue(
    team_id: int | None = Query(None),
    status: CallQueueStatus | None = Query(None),
    limit: int = Query(100, le=500),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get call queue entries."""
    service = SupervisorService()
    return await service.get_queue_entries(db, team_id, status, limit)


@router.put("/queue/{queue_id}", response_model=CallQueueResponse)
async def update_queue_entry(
    queue_id: int,
    update_data: CallQueueUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update a queue entry."""
    service = SupervisorService()
    result = await service.update_queue_entry(db, queue_id, update_data)
    if not result:
        raise HTTPException(status_code=404, detail="Queue entry not found")
    return result


@router.post("/queue/{queue_id}/assign/{agent_id}", response_model=CallQueueResponse)
async def assign_to_agent(
    queue_id: int,
    agent_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Assign a queued call to an agent."""
    service = SupervisorService()
    result = await service.assign_to_agent(db, queue_id, agent_id)
    if not result:
        raise HTTPException(status_code=404, detail="Queue entry not found")
    return result


@router.get("/queue/statistics")
async def get_queue_statistics(
    team_id: int | None = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get queue statistics."""
    service = SupervisorService()
    return await service.get_queue_statistics(db, team_id)


# ===== Active Calls Endpoints =====

@router.post("/calls", response_model=ActiveCallResponse)
async def create_active_call(
    call_data: ActiveCallCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create an active call record."""
    service = SupervisorService()
    return await service.create_active_call(db, call_data)


@router.get("/calls", response_model=list[ActiveCallResponse])
async def get_active_calls(
    team_id: int | None = Query(None),
    agent_id: int | None = Query(None),
    status: ActiveCallStatus | None = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get active calls with optional filters."""
    service = SupervisorService()
    return await service.get_active_calls(db, team_id, agent_id, status)


@router.get("/calls/{call_id}", response_model=ActiveCallResponse)
async def get_active_call(
    call_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a specific active call."""
    service = SupervisorService()
    result = await service.get_active_call(db, call_id)
    if not result:
        raise HTTPException(status_code=404, detail="Call not found")
    return result


@router.get("/calls/by-sid/{call_sid}", response_model=ActiveCallResponse)
async def get_call_by_sid(
    call_sid: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get active call by external call SID."""
    service = SupervisorService()
    result = await service.get_call_by_sid(db, call_sid)
    if not result:
        raise HTTPException(status_code=404, detail="Call not found")
    return result


@router.put("/calls/{call_id}", response_model=ActiveCallResponse)
async def update_active_call(
    call_id: int,
    update_data: ActiveCallUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update an active call."""
    service = SupervisorService()
    result = await service.update_active_call(db, call_id, update_data)
    if not result:
        raise HTTPException(status_code=404, detail="Call not found")
    return result


# ===== Agent Monitoring Endpoints =====

@router.get("/agents/live-status")
async def get_agent_live_status(
    team_id: int | None = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get live status of all agents."""
    service = SupervisorService()
    return await service.get_agent_live_status(db, team_id)


# ===== Intervention Endpoints =====

@router.post("/interventions", response_model=SupervisorInterventionResponse)
async def start_intervention(
    intervention_data: SupervisorInterventionCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Start a supervisor intervention on a call."""
    service = SupervisorService()
    try:
        return await service.start_intervention(db, intervention_data, current_user.id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/interventions/{intervention_id}/end", response_model=SupervisorInterventionResponse)
async def end_intervention(
    intervention_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """End a supervisor intervention."""
    service = SupervisorService()
    result = await service.end_intervention(db, intervention_id)
    if not result:
        raise HTTPException(status_code=404, detail="Intervention not found or already ended")
    return result


@router.get("/interventions", response_model=list[SupervisorInterventionResponse])
async def get_interventions(
    supervisor_id: int | None = Query(None),
    agent_id: int | None = Query(None),
    call_id: int | None = Query(None),
    limit: int = Query(100, le=500),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get supervisor interventions with filters."""
    service = SupervisorService()
    return await service.get_interventions(db, supervisor_id, agent_id, call_id, limit)


# ===== Performance Alerts Endpoints =====

@router.post("/alerts", response_model=PerformanceAlertResponse)
async def create_alert(
    alert_data: PerformanceAlertCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a performance alert."""
    service = SupervisorService()
    return await service.create_alert(db, alert_data)


@router.get("/alerts", response_model=list[PerformanceAlertResponse])
async def get_active_alerts(
    team_id: int | None = Query(None),
    agent_id: int | None = Query(None),
    severity: AlertSeverity | None = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get active performance alerts."""
    service = SupervisorService()
    return await service.get_active_alerts(db, team_id, agent_id, severity)


@router.post("/alerts/{alert_id}/acknowledge", response_model=PerformanceAlertResponse)
async def acknowledge_alert(
    alert_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Acknowledge a performance alert."""
    service = SupervisorService()
    result = await service.acknowledge_alert(db, alert_id, current_user.id)
    if not result:
        raise HTTPException(status_code=404, detail="Alert not found")
    return result


@router.post("/alerts/{alert_id}/resolve", response_model=PerformanceAlertResponse)
async def resolve_alert(
    alert_id: int,
    resolution_notes: str | None = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Resolve a performance alert."""
    service = SupervisorService()
    result = await service.resolve_alert(db, alert_id, resolution_notes)
    if not result:
        raise HTTPException(status_code=404, detail="Alert not found")
    return result


# ===== Dashboard Endpoints =====

@router.get("/dashboard/stats")
async def get_dashboard_stats(
    team_id: int | None = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get real-time dashboard statistics."""
    service = SupervisorService()
    return await service.get_dashboard_stats(db, team_id)
