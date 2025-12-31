"""Queue management API endpoints for advanced routing and configuration."""

from datetime import UTC, datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.jwt_auth import get_current_user
from app.database import get_db
from app.models.queue_config import (
    QueueConfig,
    QueueConfigCreate,
    QueueConfigResponse,
    QueueConfigUpdate,
    QueueSLAMetric,
    QueueSLAMetricResponse,
)
from app.models.supervisor import CallQueue, CallQueueStatus
from app.models.user import User
from app.services.queue_routing import QueueRoutingService

router = APIRouter(prefix="/api/queue", tags=["queue-management"])


# ===== Queue Configuration Endpoints =====

@router.post("/config", response_model=QueueConfigResponse)
async def create_queue_config(
    config_data: QueueConfigCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new queue configuration."""
    queue_config = QueueConfig(**config_data.model_dump())
    db.add(queue_config)
    await db.commit()
    await db.refresh(queue_config)
    return queue_config


@router.get("/config", response_model=list[QueueConfigResponse])
async def get_queue_configs(
    team_id: int | None = Query(None),
    campaign_id: int | None = Query(None),
    is_active: bool | None = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get queue configurations with optional filters."""
    query = select(QueueConfig)

    if team_id is not None:
        query = query.where(QueueConfig.team_id == team_id)
    if campaign_id is not None:
        query = query.where(QueueConfig.campaign_id == campaign_id)
    if is_active is not None:
        query = query.where(QueueConfig.is_active == is_active)

    result = await db.execute(query)
    return list(result.scalars().all())


@router.get("/config/{config_id}", response_model=QueueConfigResponse)
async def get_queue_config(
    config_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a specific queue configuration."""
    result = await db.execute(
        select(QueueConfig).where(QueueConfig.id == config_id)
    )
    config = result.scalar_one_or_none()

    if not config:
        raise HTTPException(status_code=404, detail="Queue configuration not found")

    return config


@router.put("/config/{config_id}", response_model=QueueConfigResponse)
async def update_queue_config(
    config_id: int,
    config_update: QueueConfigUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update a queue configuration."""
    result = await db.execute(
        select(QueueConfig).where(QueueConfig.id == config_id)
    )
    config = result.scalar_one_or_none()

    if not config:
        raise HTTPException(status_code=404, detail="Queue configuration not found")

    # Update fields
    update_data = config_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(config, field, value)

    config.updated_at = datetime.now(UTC)
    await db.commit()
    await db.refresh(config)

    return config


@router.delete("/config/{config_id}")
async def delete_queue_config(
    config_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete a queue configuration."""
    result = await db.execute(
        select(QueueConfig).where(QueueConfig.id == config_id)
    )
    config = result.scalar_one_or_none()

    if not config:
        raise HTTPException(status_code=404, detail="Queue configuration not found")

    await db.delete(config)
    await db.commit()

    return {"message": "Queue configuration deleted successfully"}


# ===== Routing Endpoints =====

@router.post("/route/{queue_id}/assign")
async def route_call_from_queue(
    queue_id: int,
    config_id: int | None = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Route a call from queue to an agent using routing strategy."""
    # Get queue entry
    result = await db.execute(
        select(CallQueue).where(CallQueue.id == queue_id)
    )
    queue_entry = result.scalar_one_or_none()

    if not queue_entry:
        raise HTTPException(status_code=404, detail="Queue entry not found")

    # Get queue config if specified
    queue_config = None
    if config_id:
        result = await db.execute(
            select(QueueConfig).where(QueueConfig.id == config_id)
        )
        queue_config = result.scalar_one_or_none()

    # Route the call
    routing_service = QueueRoutingService()
    agent = await routing_service.route_call_to_agent(db, queue_entry, queue_config)

    if not agent:
        raise HTTPException(status_code=404, detail="No available agent found")

    # Update queue entry
    queue_entry.assigned_agent_id = agent.id
    queue_entry.status = CallQueueStatus.ASSIGNED
    queue_entry.assigned_at = datetime.now(UTC)

    await db.commit()

    return {
        "queue_id": queue_id,
        "agent_id": agent.id,
        "agent_name": agent.display_name,
        "routing_strategy": queue_config.routing_strategy if queue_config else "fifo"
    }


@router.post("/positions/update")
async def update_all_queue_positions(
    team_id: int | None = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update queue positions for all waiting calls."""
    routing_service = QueueRoutingService()
    count = await routing_service.update_queue_positions(db, team_id)

    return {
        "message": "Queue positions updated",
        "entries_updated": count
    }


@router.get("/estimated-wait/{queue_id}")
async def get_estimated_wait_time(
    queue_id: int,
    config_id: int | None = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get estimated wait time for a queue entry."""
    # Get queue entry
    result = await db.execute(
        select(CallQueue).where(CallQueue.id == queue_id)
    )
    queue_entry = result.scalar_one_or_none()

    if not queue_entry:
        raise HTTPException(status_code=404, detail="Queue entry not found")

    # Get queue config if specified
    queue_config = None
    if config_id:
        result = await db.execute(
            select(QueueConfig).where(QueueConfig.id == config_id)
        )
        queue_config = result.scalar_one_or_none()

    # Calculate estimated wait
    routing_service = QueueRoutingService()
    estimated_seconds = await routing_service.calculate_estimated_wait_time(
        db, queue_entry, queue_config
    )

    return {
        "queue_id": queue_id,
        "position": queue_entry.queue_position,
        "estimated_wait_seconds": estimated_seconds,
        "estimated_wait_minutes": round(estimated_seconds / 60, 1)
    }


# ===== SLA Metrics Endpoints =====

@router.get("/sla/metrics", response_model=list[QueueSLAMetricResponse])
async def get_sla_metrics(
    queue_config_id: int | None = Query(None),
    team_id: int | None = Query(None),
    hours: int = Query(24, description="Hours to look back"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get SLA metrics for queues."""
    query = select(QueueSLAMetric)

    # Filter by time window
    start_time = datetime.now(UTC) - timedelta(hours=hours)
    query = query.where(QueueSLAMetric.period_start >= start_time)

    if queue_config_id is not None:
        query = query.where(QueueSLAMetric.queue_config_id == queue_config_id)
    if team_id is not None:
        query = query.where(QueueSLAMetric.team_id == team_id)

    query = query.order_by(QueueSLAMetric.period_start.desc())

    result = await db.execute(query)
    return list(result.scalars().all())


@router.get("/sla/current")
async def get_current_sla_performance(
    team_id: int | None = Query(None),
    config_id: int | None = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get current SLA performance metrics."""
    # Calculate metrics for last hour
    start_time = datetime.now(UTC) - timedelta(hours=1)

    # Build query for call metrics
    query = select(
        func.count(CallQueue.id).label('total_calls'),
        func.count(CallQueue.id).filter(
            CallQueue.status == CallQueueStatus.ANSWERED
        ).label('answered_calls'),
        func.count(CallQueue.id).filter(
            CallQueue.status == CallQueueStatus.ABANDONED
        ).label('abandoned_calls'),
        func.avg(
            func.extract('epoch', CallQueue.answered_at - CallQueue.queued_at)
        ).label('avg_wait_seconds')
    ).where(
        CallQueue.queued_at >= start_time
    )

    if team_id:
        query = query.where(CallQueue.team_id == team_id)

    result = await db.execute(query)
    row = result.one()

    total = row.total_calls or 0
    answered = row.answered_calls or 0
    abandoned = row.abandoned_calls or 0
    avg_wait = row.avg_wait_seconds or 0

    # Calculate abandon rate
    abandon_rate = (abandoned / total * 100) if total > 0 else 0

    # Get queue config for SLA target
    sla_target = 20  # default 20 seconds
    if config_id:
        result = await db.execute(
            select(QueueConfig).where(QueueConfig.id == config_id)
        )
        config = result.scalar_one_or_none()
        if config:
            sla_target = config.sla_answer_time_seconds

    # Calculate calls within SLA (answered within target)
    sla_query = select(func.count(CallQueue.id)).where(
        and_(
            CallQueue.queued_at >= start_time,
            CallQueue.status == CallQueueStatus.ANSWERED,
            func.extract('epoch', CallQueue.answered_at - CallQueue.queued_at) <= sla_target
        )
    )

    if team_id:
        sla_query = sla_query.where(CallQueue.team_id == team_id)

    result = await db.execute(sla_query)
    calls_within_sla = result.scalar() or 0

    # Calculate SLA compliance
    sla_compliance = (calls_within_sla / answered * 100) if answered > 0 else 0

    return {
        "period": "last_hour",
        "total_calls": total,
        "answered_calls": answered,
        "abandoned_calls": abandoned,
        "calls_within_sla": calls_within_sla,
        "sla_target_seconds": sla_target,
        "sla_compliance_percentage": round(sla_compliance, 2),
        "average_wait_seconds": round(avg_wait, 2),
        "abandon_rate_percentage": round(abandon_rate, 2)
    }


# ===== Skill-Based Routing Endpoints =====

@router.get("/available-agents")
async def get_available_agents_for_skills(
    required_skills: str = Query("", description="Comma-separated skills"),
    required_language: str | None = Query(None),
    team_id: int | None = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get available agents matching skill and language requirements."""
    routing_service = QueueRoutingService()

    skills_list = [s.strip() for s in required_skills.split(",") if s.strip()]

    agents = await routing_service._get_available_agents(
        db,
        team_id=team_id,
        required_skills=skills_list if skills_list else None,
        required_language=required_language
    )

    return {
        "available_count": len(agents),
        "agents": [
            {
                "id": agent.id,
                "display_name": agent.display_name,
                "skills": agent.skills,
                "languages": agent.languages,
                "active_calls": agent.active_calls_count,
                "max_calls": agent.max_concurrent_calls
            }
            for agent in agents
        ]
    }
