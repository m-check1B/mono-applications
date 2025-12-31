"""Agent router - Additional agent-specific operations (complements agents.py)"""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timedelta
from app.core.database import get_db
from app.dependencies import get_current_user
from app.core.logger import get_logger
from app.models.user import User

router = APIRouter(prefix="/api/agent", tags=["agent-operations"])
logger = get_logger(__name__)


@router.get("/my-stats", response_model=dict)
async def get_my_stats(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get current agent's statistics"""
    from sqlalchemy import select, func
    from app.models.call import Call, CallStatus

    # Get agent's calls today
    today = datetime.utcnow().date()
    stmt = select(Call).where(
        Call.agent_id == current_user.id,
        func.date(Call.start_time) == today
    )
    result = await db.execute(stmt)
    calls_today = result.scalars().all()

    completed = sum(1 for c in calls_today if c.status == CallStatus.COMPLETED)
    total_duration = sum(c.duration for c in calls_today if c.duration) or 0
    avg_duration = total_duration / completed if completed > 0 else 0

    return {
        'agent_id': current_user.id,
        'today': {
            'total_calls': len(calls_today),
            'completed_calls': completed,
            'total_duration_seconds': total_duration,
            'average_duration_seconds': round(avg_duration, 2)
        },
        'current_status': current_user.status.value if current_user.status else 'offline'
    }


@router.get("/leaderboard", response_model=dict)
async def get_leaderboard(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get agent leaderboard"""
    # Mock leaderboard
    return {
        'period': 'today',
        'leaderboard': [
            {'agent_id': 'agent1', 'name': 'John Doe', 'calls': 45, 'completion_rate': 0.92},
            {'agent_id': 'agent2', 'name': 'Jane Smith', 'calls': 42, 'completion_rate': 0.95},
            {'agent_id': current_user.id, 'name': f'{current_user.first_name} {current_user.last_name}', 'calls': 38, 'completion_rate': 0.89}
        ]
    }
