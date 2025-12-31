"""Analytics router - FastAPI endpoints for business analytics"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from datetime import datetime, timedelta
from typing import Optional
from collections import defaultdict

from app.core.database import get_db
from app.models.call import Call, CallStatus, CallDirection
from app.models.user import User, UserRole
from app.models.campaign import Campaign
from app.schemas.analytics import (
    CallAnalyticsResponse,
    AgentPerformanceResponse,
    CampaignAnalyticsResponse,
    DashboardSummaryResponse
)
from app.dependencies import get_current_user

router = APIRouter(prefix="/api/analytics", tags=["analytics"])


@router.get("/dashboard", response_model=DashboardSummaryResponse)
async def get_dashboard_summary(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get dashboard summary with key metrics

    Args:
        db: Database session
        current_user: Authenticated user

    Returns:
        Dashboard summary with call stats, agent stats, campaign stats
    """
    # Get calls in last 24 hours
    last_24h = datetime.utcnow() - timedelta(hours=24)

    # Total calls
    total_calls_result = await db.execute(
        select(func.count(Call.id)).where(
            Call.organization_id == current_user.organization_id,
            Call.start_time >= last_24h
        )
    )
    total_calls = total_calls_result.scalar() or 0

    # Active calls
    active_calls_result = await db.execute(
        select(func.count(Call.id)).where(
            Call.organization_id == current_user.organization_id,
            Call.status == CallStatus.IN_PROGRESS
        )
    )
    active_calls = active_calls_result.scalar() or 0

    # Completed calls
    completed_calls_result = await db.execute(
        select(func.count(Call.id)).where(
            Call.organization_id == current_user.organization_id,
            Call.status == CallStatus.COMPLETED,
            Call.start_time >= last_24h
        )
    )
    completed_calls = completed_calls_result.scalar() or 0

    # Average call duration
    avg_duration_result = await db.execute(
        select(func.avg(Call.duration)).where(
            Call.organization_id == current_user.organization_id,
            Call.status == CallStatus.COMPLETED,
            Call.duration.isnot(None),
            Call.start_time >= last_24h
        )
    )
    avg_duration = avg_duration_result.scalar() or 0

    # Active campaigns
    active_campaigns_result = await db.execute(
        select(func.count(Campaign.id)).where(
            Campaign.organization_id == current_user.organization_id,
            Campaign.active == True
        )
    )
    active_campaigns = active_campaigns_result.scalar() or 0

    return {
        "total_calls_24h": total_calls,
        "active_calls": active_calls,
        "completed_calls_24h": completed_calls,
        "avg_call_duration": round(avg_duration, 2) if avg_duration else 0,
        "active_campaigns": active_campaigns,
        "completion_rate": round((completed_calls / total_calls * 100), 2) if total_calls > 0 else 0
    }


@router.get("/calls", response_model=CallAnalyticsResponse)
async def get_call_analytics(
    start_date: Optional[datetime] = Query(None, description="Start date for analytics"),
    end_date: Optional[datetime] = Query(None, description="End date for analytics"),
    group_by: str = Query("day", regex="^(hour|day|week|month)$"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get call analytics with grouping

    Args:
        start_date: Start date (defaults to 30 days ago)
        end_date: End date (defaults to now)
        group_by: Grouping period (hour, day, week, month)
        db: Database session
        current_user: Authenticated user

    Returns:
        Call analytics grouped by period
    """
    # Default date range: last 30 days
    if not end_date:
        end_date = datetime.utcnow()
    if not start_date:
        start_date = end_date - timedelta(days=30)

    # Build query
    query = select(Call).where(
        Call.organization_id == current_user.organization_id,
        Call.start_time >= start_date,
        Call.start_time <= end_date
    )

    # If agent, only show their calls
    if current_user.role == UserRole.AGENT:
        query = query.where(Call.agent_id == current_user.id)

    result = await db.execute(query)
    calls = result.scalars().all()

    # Group calls by period
    grouped = defaultdict(lambda: {
        "period": "",
        "total": 0,
        "inbound": 0,
        "outbound": 0,
        "completed": 0,
        "failed": 0,
        "total_duration": 0,
        "avg_duration": 0
    })

    for call in calls:
        # Determine period key
        date = call.start_time
        if group_by == "hour":
            key = date.strftime("%Y-%m-%d %H:00")
        elif group_by == "day":
            key = date.strftime("%Y-%m-%d")
        elif group_by == "week":
            key = f"{date.year}-W{date.isocalendar()[1]}"
        else:  # month
            key = date.strftime("%Y-%m")

        group = grouped[key]
        group["period"] = key
        group["total"] += 1

        # Direction
        if call.direction == CallDirection.INBOUND:
            group["inbound"] += 1
        else:
            group["outbound"] += 1

        # Status
        if call.status == CallStatus.COMPLETED:
            group["completed"] += 1
            if call.duration:
                group["total_duration"] += call.duration
        elif call.status == CallStatus.FAILED:
            group["failed"] += 1

    # Calculate averages
    metrics = []
    for key, group in sorted(grouped.items()):
        if group["completed"] > 0:
            group["avg_duration"] = round(group["total_duration"] / group["completed"], 2)
        group["completion_rate"] = round((group["completed"] / group["total"] * 100), 2) if group["total"] > 0 else 0
        metrics.append(group)

    # Overall summary
    total_calls = len(calls)
    completed_calls = sum(1 for c in calls if c.status == CallStatus.COMPLETED)
    total_duration = sum(c.duration for c in calls if c.duration)

    return {
        "summary": {
            "total_calls": total_calls,
            "completed_calls": completed_calls,
            "avg_duration": round(total_duration / completed_calls, 2) if completed_calls > 0 else 0,
            "completion_rate": round((completed_calls / total_calls * 100), 2) if total_calls > 0 else 0
        },
        "metrics": metrics
    }


@router.get("/agents", response_model=list[AgentPerformanceResponse])
async def get_agent_performance(
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get agent performance metrics

    Args:
        start_date: Start date
        end_date: End date
        db: Database session
        current_user: Authenticated user (must be supervisor or admin)

    Returns:
        List of agent performance metrics
    """
    # Only supervisors/admins can see all agents
    if current_user.role == UserRole.AGENT:
        # Agents can only see their own stats
        agent_ids = [current_user.id]
    else:
        # Get all agents in organization
        agents_result = await db.execute(
            select(User.id).where(
                User.organization_id == current_user.organization_id,
                User.role == UserRole.AGENT
            )
        )
        agent_ids = [row[0] for row in agents_result.fetchall()]

    # Default date range
    if not end_date:
        end_date = datetime.utcnow()
    if not start_date:
        start_date = end_date - timedelta(days=30)

    # Get agent stats
    agent_stats = []
    for agent_id in agent_ids:
        # Get agent info
        agent_result = await db.execute(
            select(User).where(User.id == agent_id)
        )
        agent = agent_result.scalar_one_or_none()
        if not agent:
            continue

        # Get calls for this agent
        calls_result = await db.execute(
            select(Call).where(
                Call.agent_id == agent_id,
                Call.start_time >= start_date,
                Call.start_time <= end_date
            )
        )
        calls = calls_result.scalars().all()

        total_calls = len(calls)
        completed_calls = sum(1 for c in calls if c.status == CallStatus.COMPLETED)
        total_duration = sum(c.duration for c in calls if c.duration)

        agent_stats.append({
            "agent_id": agent.id,
            "agent_name": f"{agent.first_name} {agent.last_name}",
            "total_calls": total_calls,
            "completed_calls": completed_calls,
            "avg_duration": round(total_duration / completed_calls, 2) if completed_calls > 0 else 0,
            "completion_rate": round((completed_calls / total_calls * 100), 2) if total_calls > 0 else 0
        })

    return agent_stats


@router.get("/campaigns", response_model=list[CampaignAnalyticsResponse])
async def get_campaign_analytics(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get campaign analytics

    Args:
        db: Database session
        current_user: Authenticated user

    Returns:
        List of campaign metrics
    """
    # Get all campaigns
    campaigns_result = await db.execute(
        select(Campaign).where(
            Campaign.organization_id == current_user.organization_id
        )
    )
    campaigns = campaigns_result.scalars().all()

    campaign_stats = []
    for campaign in campaigns:
        # Get calls for this campaign
        calls_result = await db.execute(
            select(Call).where(Call.campaign_id == campaign.id)
        )
        calls = calls_result.scalars().all()

        total_calls = len(calls)
        completed_calls = sum(1 for c in calls if c.status == CallStatus.COMPLETED)

        campaign_stats.append({
            "campaign_id": campaign.id,
            "campaign_name": campaign.name,
            "total_calls": total_calls,
            "completed_calls": completed_calls,
            "active": campaign.active,
            "completion_rate": round((completed_calls / total_calls * 100), 2) if total_calls > 0 else 0
        })

    return campaign_stats
