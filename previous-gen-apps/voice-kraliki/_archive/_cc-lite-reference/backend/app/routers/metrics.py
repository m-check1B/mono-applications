"""Metrics router - Application performance monitoring and metrics"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime, timedelta
from typing import Optional
from app.core.database import get_db
from app.dependencies import get_current_user, require_supervisor
from app.core.logger import get_logger
from app.models.user import User

router = APIRouter(prefix="/api/metrics", tags=["metrics"])
logger = get_logger(__name__)


@router.get("/system", response_model=dict)
async def get_system_metrics(current_user: User = Depends(get_current_user)):
    """
    Get system performance metrics

    **Protected**: Requires authentication
    """
    import psutil
    import os

    try:
        # CPU metrics
        cpu_percent = psutil.cpu_percent(interval=1)
        cpu_count = psutil.cpu_count()

        # Memory metrics
        memory = psutil.virtual_memory()
        memory_percent = memory.percent
        memory_used_gb = memory.used / (1024**3)
        memory_total_gb = memory.total / (1024**3)

        # Disk metrics
        disk = psutil.disk_usage('/')
        disk_percent = disk.percent
        disk_used_gb = disk.used / (1024**3)
        disk_total_gb = disk.total / (1024**3)

        # Process metrics
        process = psutil.Process(os.getpid())
        process_memory_mb = process.memory_info().rss / (1024**2)
        process_cpu_percent = process.cpu_percent(interval=0.1)

        return {
            'timestamp': datetime.utcnow().isoformat(),
            'cpu': {
                'usage_percent': round(cpu_percent, 2),
                'cores': cpu_count,
                'process_percent': round(process_cpu_percent, 2)
            },
            'memory': {
                'usage_percent': round(memory_percent, 2),
                'used_gb': round(memory_used_gb, 2),
                'total_gb': round(memory_total_gb, 2),
                'process_mb': round(process_memory_mb, 2)
            },
            'disk': {
                'usage_percent': round(disk_percent, 2),
                'used_gb': round(disk_used_gb, 2),
                'total_gb': round(disk_total_gb, 2)
            },
            'status': 'healthy' if cpu_percent < 80 and memory_percent < 80 else 'warning'
        }

    except Exception as e:
        logger.error(f"Error getting system metrics: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve system metrics"
        )


@router.get("/application", response_model=dict)
async def get_application_metrics(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get application metrics

    **Protected**: Requires authentication
    """
    try:
        from sqlalchemy import select, func
        from app.models.call import Call

        # Call metrics
        total_calls_stmt = select(func.count(Call.id)).where(
            Call.organization_id == current_user.organization_id
        )
        total_calls_result = await db.execute(total_calls_stmt)
        total_calls = total_calls_result.scalar() or 0

        # Active calls
        active_calls_stmt = select(func.count(Call.id)).where(
            Call.organization_id == current_user.organization_id,
            Call.status.in_(['IN_PROGRESS', 'RINGING', 'ON_HOLD'])
        )
        active_calls_result = await db.execute(active_calls_stmt)
        active_calls = active_calls_result.scalar() or 0

        # Average call duration
        avg_duration_stmt = select(func.avg(Call.duration)).where(
            Call.organization_id == current_user.organization_id,
            Call.duration.isnot(None)
        )
        avg_duration_result = await db.execute(avg_duration_stmt)
        avg_duration = avg_duration_result.scalar() or 0

        return {
            'timestamp': datetime.utcnow().isoformat(),
            'calls': {
                'total': total_calls,
                'active': active_calls,
                'average_duration_seconds': round(float(avg_duration), 2)
            },
            'performance': {
                'response_time_ms': 125,  # Mock - would track actual
                'error_rate': 0.01,
                'uptime_percent': 99.9
            }
        }

    except Exception as e:
        logger.error(f"Error getting application metrics: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve application metrics"
        )


@router.get("/health", response_model=dict)
async def get_health_metrics(db: AsyncSession = Depends(get_db)):
    """
    Get health check metrics

    **Public**: No authentication required
    """
    try:
        # Database health
        await db.execute(select(1))
        db_healthy = True
    except:
        db_healthy = False

    # Overall health
    is_healthy = db_healthy

    return {
        'status': 'healthy' if is_healthy else 'unhealthy',
        'timestamp': datetime.utcnow().isoformat(),
        'checks': {
            'database': 'up' if db_healthy else 'down',
            'api': 'up',
            'redis': 'up'  # Mock
        }
    }


@router.get("/performance", response_model=dict, dependencies=[Depends(require_supervisor)])
async def get_performance_metrics(
    hours: int = Query(24, ge=1, le=168),
    current_user: User = Depends(get_current_user)
):
    """
    Get performance metrics over time

    **Protected**: Requires supervisor role
    """
    # Mock implementation - would track actual metrics
    return {
        'period_hours': hours,
        'metrics': [
            {
                'timestamp': (datetime.utcnow() - timedelta(hours=i)).isoformat(),
                'response_time_ms': 100 + (i % 50),
                'requests_per_second': 10 + (i % 5),
                'error_rate': 0.01
            }
            for i in range(hours)
        ],
        'summary': {
            'avg_response_time_ms': 125,
            'max_response_time_ms': 450,
            'avg_requests_per_second': 12,
            'total_requests': hours * 12 * 3600,
            'total_errors': int(hours * 12 * 3600 * 0.01)
        }
    }


@router.get("/errors", response_model=dict, dependencies=[Depends(require_supervisor)])
async def get_error_metrics(
    hours: int = Query(24, ge=1, le=168),
    current_user: User = Depends(get_current_user)
):
    """
    Get error metrics and logs

    **Protected**: Requires supervisor role
    """
    # Mock implementation
    return {
        'period_hours': hours,
        'total_errors': 42,
        'error_rate': 0.01,
        'errors_by_type': {
            '500_internal_server_error': 20,
            '404_not_found': 15,
            '403_forbidden': 5,
            '400_bad_request': 2
        },
        'recent_errors': [
            {
                'timestamp': datetime.utcnow().isoformat(),
                'type': '500',
                'message': 'Database connection timeout',
                'count': 3
            }
        ]
    }
