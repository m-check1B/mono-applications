"""Monitoring and observability module for Prometheus metrics and health checks."""

from app.monitoring.health_service import (
    ComponentHealth,
    HealthStatus,
    SystemHealth,
    get_liveness,
    get_readiness,
    get_system_health,
)
from app.monitoring.prometheus_metrics import (
    set_app_info,
    track_ai_provider_error,
    track_ai_provider_request,
    track_db_query,
    track_request,
    track_telephony_call,
    track_websocket_message,
    update_active_calls,
    update_active_sessions,
    update_db_pool_metrics,
)

__all__ = [
    # Health service
    "HealthStatus",
    "ComponentHealth",
    "SystemHealth",
    "get_system_health",
    "get_readiness",
    "get_liveness",
    # Metrics
    "track_request",
    "track_db_query",
    "track_websocket_message",
    "track_ai_provider_request",
    "track_ai_provider_error",
    "track_telephony_call",
    "update_db_pool_metrics",
    "update_active_sessions",
    "update_active_calls",
    "set_app_info",
]
