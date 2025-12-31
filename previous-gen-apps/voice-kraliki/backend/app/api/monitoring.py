"""Monitoring API endpoints for Prometheus metrics and health checks.

This module provides endpoints for:
- Prometheus metrics collection (/metrics)
- Database health checks
- Comprehensive system health checks
- Kubernetes-style readiness/liveness probes
"""

from fastapi import APIRouter, Query, Request, Response
from prometheus_client import CONTENT_TYPE_LATEST, generate_latest

from app.config.feature_flags import get_feature_flags
from app.config.settings import get_settings
from app.database import check_database_health
from app.middleware.rate_limit import (
    API_RATE_LIMIT,
    limiter,
)
from app.monitoring.health_service import (
    get_liveness,
    get_readiness,
    get_system_health,
)
from app.monitoring.prometheus_metrics import set_app_info, update_db_pool_metrics

router = APIRouter(prefix="/api/v1/monitoring", tags=["monitoring"])


@limiter.limit(API_RATE_LIMIT)
@router.get("/metrics")
async def metrics(request: Request):
    """Prometheus metrics endpoint.

    Returns metrics in Prometheus text exposition format for scraping.
    This endpoint should be configured in your Prometheus scrape config.

    Returns:
        Response: Prometheus metrics in text format
    """
    # Update database pool metrics before exposing
    try:
        db_health = check_database_health()
        if db_health.get("status") == "healthy":
            update_db_pool_metrics(
                pool_size=db_health.get("pool_size", 0),
                checked_out=db_health.get("checked_out", 0),
                overflow=db_health.get("overflow", 0)
            )
    except Exception:
        pass  # Don't fail metrics endpoint if DB check fails

    # Set application info
    settings = get_settings()
    set_app_info(
        name=settings.app_name,
        version=settings.version,
        environment=settings.environment
    )

    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)


@limiter.limit(API_RATE_LIMIT)
@router.get("/health/database")
async def database_health(request: Request):
    """Database health check endpoint.

    Returns detailed information about database connection pool health.

    Returns:
        dict: Database health status and pool metrics
    """
    return check_database_health()


@router.get("/health")
async def monitoring_health(
    include_external: bool = Query(
        default=False,
        description="Include external provider checks (AI, telephony). Slower but more comprehensive."
    )
):
    """Comprehensive system health check.

    Returns detailed health status of all system components including:
    - Database connection pool
    - Redis cache
    - Disk space
    - Memory usage
    - AI providers (optional)
    - Telephony providers (optional)

    Args:
        include_external: If True, checks external AI and telephony provider APIs.
                         This makes the check slower but more comprehensive.

    Returns:
        dict: Comprehensive system health status
    """
    health = await get_system_health(include_external=include_external)
    return health.to_dict()


@limiter.limit(API_RATE_LIMIT)
@router.get("/health/ready")
async def readiness_check(request: Request):
    """Kubernetes-style readiness probe.

    Returns whether the application is ready to receive traffic.
    Checks only critical dependencies (database).

    Returns:
        dict: Readiness status with {"ready": bool, "checks": {...}}
    """
    return await get_readiness()


@limiter.limit(API_RATE_LIMIT)
@router.get("/health/live")
async def liveness_check(request: Request):
    """Kubernetes-style liveness probe.

    Returns whether the application process is alive.
    This is the lightest possible check.

    Returns:
        dict: Liveness status with {"alive": bool, "uptime_seconds": float}
    """
    return await get_liveness()


@limiter.limit(API_RATE_LIMIT)
@router.get("/health/summary")
async def health_summary(request: Request):
    """Quick health summary for dashboards.

    Returns a simplified health status suitable for status pages.

    Returns:
        dict: Simplified health summary
    """
    settings = get_settings()
    flags = get_feature_flags()
    db_health = check_database_health()

    return {
        "status": "healthy" if db_health.get("status") == "healthy" else "degraded",
        "service": settings.app_name,
        "version": settings.version,
        "environment": settings.environment,
        "metrics_enabled": flags.enable_metrics_collection,
        "database": db_health.get("status", "unknown"),
    }
