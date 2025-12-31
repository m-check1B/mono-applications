"""Dashboard router - FastAPI endpoints for dashboard metrics"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from datetime import datetime, timedelta
from app.core.database import get_db
from app.dependencies import get_current_user
from app.core.logger import get_logger
from app.models.user import User, UserStatus
from app.models.call import Call, CallStatus
from app.models.agent import Agent, AgentStatus
from app.models.campaign import Campaign

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])
logger = get_logger(__name__)


@router.get("/overview", response_model=dict)
async def get_dashboard_overview(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get dashboard overview with all key metrics

    **Protected**: Requires authentication
    """
    try:
        org_id = current_user.organization_id

        # Active calls
        active_calls_stmt = (
            select(Call)
            .where(
                Call.organization_id == org_id,
                Call.status.in_([CallStatus.IN_PROGRESS, CallStatus.RINGING, CallStatus.ON_HOLD])
            )
            .order_by(Call.start_time.desc())
            .limit(25)
        )
        active_calls_result = await db.execute(active_calls_stmt)
        active_calls = active_calls_result.scalars().all()

        # Recent calls
        recent_calls_stmt = (
            select(Call)
            .where(Call.organization_id == org_id)
            .order_by(Call.start_time.desc())
            .limit(25)
        )
        recent_calls_result = await db.execute(recent_calls_stmt)
        recent_calls = recent_calls_result.scalars().all()

        # Team members
        members_stmt = select(User).where(User.organization_id == org_id)
        members_result = await db.execute(members_stmt)
        members = members_result.scalars().all()

        # Call statistics
        total_calls_stmt = select(func.count(Call.id)).where(Call.organization_id == org_id)
        total_calls_result = await db.execute(total_calls_stmt)
        total_calls = total_calls_result.scalar() or 0

        completed_calls_stmt = select(func.count(Call.id)).where(
            Call.organization_id == org_id,
            Call.status == CallStatus.COMPLETED
        )
        completed_calls_result = await db.execute(completed_calls_stmt)
        completed_calls = completed_calls_result.scalar() or 0

        # Average duration
        avg_duration_stmt = select(func.avg(Call.duration)).where(
            Call.organization_id == org_id,
            Call.duration.isnot(None)
        )
        avg_duration_result = await db.execute(avg_duration_stmt)
        avg_duration = avg_duration_result.scalar() or 0

        # Agent handled calls
        agent_handled_stmt = select(func.count(Call.id)).where(
            Call.organization_id == org_id,
            Call.agent_id.isnot(None)
        )
        agent_handled_result = await db.execute(agent_handled_stmt)
        agent_handled = agent_handled_result.scalar() or 0

        # Missed calls
        missed_calls_stmt = select(func.count(Call.id)).where(
            Call.organization_id == org_id,
            Call.status == CallStatus.NO_ANSWER
        )
        missed_calls_result = await db.execute(missed_calls_stmt)
        missed_calls = missed_calls_result.scalar() or 0

        # Active agent IDs
        active_agent_ids = {call.agent_id for call in active_calls if call.agent_id}

        # Map member status
        def map_member_status(user_status: UserStatus) -> str:
            if user_status in [UserStatus.ACTIVE, UserStatus.AVAILABLE]:
                return "available"
            elif user_status == UserStatus.BREAK:
                return "break"
            else:
                return "offline"

        # Format members
        formatted_members = [
            {
                "id": member.id,
                "email": member.email,
                "firstName": member.first_name,
                "lastName": member.last_name,
                "role": member.role.value if member.role else None,
                "status": map_member_status(member.status) if member.status else "offline",
                "department": member.department,
                "phoneExtension": member.phone_extension,
                "isOnCall": member.id in active_agent_ids,
                "updatedAt": member.updated_at.isoformat() if member.updated_at else None,
                "lastLoginAt": member.last_login_at.isoformat() if member.last_login_at else None,
            }
            for member in members
        ]

        # Format active calls
        formatted_active_calls = [
            {
                "id": call.id,
                "fromNumber": call.from_number,
                "toNumber": call.to_number,
                "status": call.status.value,
                "startTime": call.start_time.isoformat(),
                "agentId": call.agent_id,
                "direction": call.direction.value,
                "metadata": call.extra_metadata,
            }
            for call in active_calls
        ]

        # Format recent calls
        formatted_recent_calls = [
            {
                "id": call.id,
                "fromNumber": call.from_number,
                "toNumber": call.to_number,
                "status": call.status.value,
                "startTime": call.start_time.isoformat(),
                "endTime": call.end_time.isoformat() if call.end_time else None,
                "duration": call.duration,
                "agentId": call.agent_id,
                "direction": call.direction.value,
            }
            for call in recent_calls
        ]

        # Stats
        available_members = sum(1 for m in formatted_members if m["status"] == "available")
        on_call_members = sum(1 for m in formatted_members if m["isOnCall"])
        on_break_members = sum(1 for m in formatted_members if m["status"] == "break")

        return {
            "activeCalls": formatted_active_calls,
            "recentCalls": formatted_recent_calls,
            "members": formatted_members,
            "stats": {
                "totalCalls": total_calls,
                "completedCalls": completed_calls,
                "missedCalls": missed_calls,
                "agentHandledCalls": agent_handled,
                "averageDuration": round(float(avg_duration or 0), 2),
                "availableMembers": available_members,
                "onCallMembers": on_call_members,
                "onBreakMembers": on_break_members,
            },
        }

    except Exception as e:
        logger.error(f"Error getting dashboard overview: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve dashboard overview"
        )


@router.get("/stats", response_model=dict)
async def get_dashboard_stats(
    days: int = 7,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get dashboard statistics for specified time period

    **Protected**: Requires authentication
    """
    try:
        org_id = current_user.organization_id
        start_date = datetime.utcnow() - timedelta(days=days)

        # Calls in period
        calls_stmt = select(Call).where(
            Call.organization_id == org_id,
            Call.start_time >= start_date
        )
        calls_result = await db.execute(calls_stmt)
        calls = calls_result.scalars().all()

        # Calculate stats
        total = len(calls)
        completed = sum(1 for c in calls if c.status == CallStatus.COMPLETED)
        missed = sum(1 for c in calls if c.status == CallStatus.NO_ANSWER)

        durations = [c.duration for c in calls if c.duration]
        avg_duration = sum(durations) / len(durations) if durations else 0

        # Daily breakdown
        daily_stats = {}
        for call in calls:
            date_key = call.start_time.date().isoformat()
            if date_key not in daily_stats:
                daily_stats[date_key] = {
                    "date": date_key,
                    "total": 0,
                    "completed": 0,
                    "missed": 0,
                    "avgDuration": 0,
                }

            daily_stats[date_key]["total"] += 1
            if call.status == CallStatus.COMPLETED:
                daily_stats[date_key]["completed"] += 1
            if call.status == CallStatus.NO_ANSWER:
                daily_stats[date_key]["missed"] += 1

        return {
            "period": f"last_{days}_days",
            "summary": {
                "totalCalls": total,
                "completedCalls": completed,
                "missedCalls": missed,
                "averageDuration": round(avg_duration, 2),
                "completionRate": round((completed / total * 100) if total > 0 else 0, 2),
            },
            "daily": sorted(daily_stats.values(), key=lambda x: x["date"]),
        }

    except Exception as e:
        logger.error(f"Error getting dashboard stats: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve dashboard statistics"
        )


@router.get("/agent-performance", response_model=dict)
async def get_agent_performance(
    days: int = 7,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get agent performance metrics

    **Protected**: Requires authentication
    """
    try:
        org_id = current_user.organization_id
        start_date = datetime.utcnow() - timedelta(days=days)

        # Get calls with agents
        calls_stmt = select(Call).where(
            Call.organization_id == org_id,
            Call.start_time >= start_date,
            Call.agent_id.isnot(None)
        )
        calls_result = await db.execute(calls_stmt)
        calls = calls_result.scalars().all()

        # Group by agent
        agent_stats = {}
        for call in calls:
            agent_id = call.agent_id
            if agent_id not in agent_stats:
                agent_stats[agent_id] = {
                    "agentId": agent_id,
                    "totalCalls": 0,
                    "completedCalls": 0,
                    "totalDuration": 0,
                    "durations": [],
                }

            agent_stats[agent_id]["totalCalls"] += 1
            if call.status == CallStatus.COMPLETED:
                agent_stats[agent_id]["completedCalls"] += 1
            if call.duration:
                agent_stats[agent_id]["totalDuration"] += call.duration
                agent_stats[agent_id]["durations"].append(call.duration)

        # Calculate final metrics
        performance = []
        for agent_id, stats in agent_stats.items():
            durations = stats["durations"]
            performance.append({
                "agentId": agent_id,
                "totalCalls": stats["totalCalls"],
                "completedCalls": stats["completedCalls"],
                "completionRate": round(
                    (stats["completedCalls"] / stats["totalCalls"] * 100) if stats["totalCalls"] > 0 else 0,
                    2
                ),
                "averageDuration": round(
                    (sum(durations) / len(durations)) if durations else 0,
                    2
                ),
            })

        # Sort by total calls
        performance.sort(key=lambda x: x["totalCalls"], reverse=True)

        return {
            "period": f"last_{days}_days",
            "agents": performance,
        }

    except Exception as e:
        logger.error(f"Error getting agent performance: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve agent performance"
        )
