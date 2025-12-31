"""Comprehensive health check service for CC-Lite.

This module provides deep health checks for all application dependencies
including database, Redis, AI providers, and telephony providers.
"""

import asyncio
import logging
import os
import time
from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import Enum
from typing import Any

import httpx

logger = logging.getLogger(__name__)


class HealthStatus(str, Enum):
    """Health check status levels."""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"


@dataclass
class ComponentHealth:
    """Health status for a single component."""
    name: str
    status: HealthStatus
    latency_ms: float = 0.0
    message: str = ""
    details: dict[str, Any] = field(default_factory=dict)
    checked_at: datetime = field(default_factory=lambda: datetime.now(UTC))

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "status": self.status.value,
            "latency_ms": round(self.latency_ms, 2),
            "message": self.message,
            "details": self.details,
            "checked_at": self.checked_at.isoformat(),
        }


@dataclass
class SystemHealth:
    """Aggregate health status for the entire system."""
    status: HealthStatus
    version: str
    environment: str
    uptime_seconds: float
    components: list[ComponentHealth]
    checked_at: datetime = field(default_factory=lambda: datetime.now(UTC))

    def to_dict(self) -> dict[str, Any]:
        return {
            "status": self.status.value,
            "version": self.version,
            "environment": self.environment,
            "uptime_seconds": round(self.uptime_seconds, 2),
            "components": [c.to_dict() for c in self.components],
            "checked_at": self.checked_at.isoformat(),
        }


# Track application start time for uptime calculation
_start_time = time.time()


async def check_database_health() -> ComponentHealth:
    """Check database connectivity and pool status."""
    start = time.time()
    try:
        from app.database import check_database_health as db_check
        from app.database import engine

        # Execute a simple query to verify connectivity
        with engine.connect() as conn:
            conn.execute("SELECT 1")

        pool_status = db_check()
        latency = (time.time() - start) * 1000

        if pool_status.get("status") == "healthy":
            return ComponentHealth(
                name="database",
                status=HealthStatus.HEALTHY,
                latency_ms=latency,
                message="Database connection successful",
                details=pool_status,
            )
        else:
            return ComponentHealth(
                name="database",
                status=HealthStatus.DEGRADED,
                latency_ms=latency,
                message="Database pool issues detected",
                details=pool_status,
            )
    except Exception as e:
        return ComponentHealth(
            name="database",
            status=HealthStatus.UNHEALTHY,
            latency_ms=(time.time() - start) * 1000,
            message=f"Database check failed: {str(e)}",
        )


async def check_redis_health() -> ComponentHealth:
    """Check Redis connectivity."""
    start = time.time()
    redis_url = os.getenv("REDIS_URL", "redis://localhost:6379")

    try:
        import redis.asyncio as aioredis

        client = aioredis.from_url(redis_url, decode_responses=True)
        await client.ping()
        info = await client.info("memory")
        await client.close()

        latency = (time.time() - start) * 1000

        return ComponentHealth(
            name="redis",
            status=HealthStatus.HEALTHY,
            latency_ms=latency,
            message="Redis connection successful",
            details={
                "used_memory_human": info.get("used_memory_human", "unknown"),
                "connected_clients": info.get("connected_clients", 0),
            },
        )
    except ImportError:
        return ComponentHealth(
            name="redis",
            status=HealthStatus.DEGRADED,
            latency_ms=0,
            message="Redis client not installed (optional)",
        )
    except Exception as e:
        return ComponentHealth(
            name="redis",
            status=HealthStatus.DEGRADED,
            latency_ms=(time.time() - start) * 1000,
            message=f"Redis check failed: {str(e)}",
        )


async def check_ai_provider_health(provider: str, endpoint: str) -> ComponentHealth:
    """Check AI provider API accessibility."""
    start = time.time()

    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            # Just check if the API is reachable (not a full auth check)
            response = await client.head(endpoint)
            latency = (time.time() - start) * 1000

            # Most APIs return 401/403 without auth, but they're reachable
            if response.status_code < 500:
                return ComponentHealth(
                    name=f"ai_provider_{provider}",
                    status=HealthStatus.HEALTHY,
                    latency_ms=latency,
                    message=f"{provider} API reachable",
                    details={"status_code": response.status_code},
                )
            else:
                return ComponentHealth(
                    name=f"ai_provider_{provider}",
                    status=HealthStatus.UNHEALTHY,
                    latency_ms=latency,
                    message=f"{provider} API returned error",
                    details={"status_code": response.status_code},
                )
    except Exception as e:
        return ComponentHealth(
            name=f"ai_provider_{provider}",
            status=HealthStatus.UNHEALTHY,
            latency_ms=(time.time() - start) * 1000,
            message=f"{provider} API unreachable: {str(e)}",
        )


async def check_telephony_provider_health(provider: str, endpoint: str) -> ComponentHealth:
    """Check telephony provider API accessibility."""
    start = time.time()

    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.head(endpoint)
            latency = (time.time() - start) * 1000

            if response.status_code < 500:
                return ComponentHealth(
                    name=f"telephony_{provider}",
                    status=HealthStatus.HEALTHY,
                    latency_ms=latency,
                    message=f"{provider} API reachable",
                    details={"status_code": response.status_code},
                )
            else:
                return ComponentHealth(
                    name=f"telephony_{provider}",
                    status=HealthStatus.DEGRADED,
                    latency_ms=latency,
                    message=f"{provider} API returned error",
                    details={"status_code": response.status_code},
                )
    except Exception as e:
        return ComponentHealth(
            name=f"telephony_{provider}",
            status=HealthStatus.DEGRADED,
            latency_ms=(time.time() - start) * 1000,
            message=f"{provider} API unreachable: {str(e)}",
        )


async def check_disk_space() -> ComponentHealth:
    """Check available disk space."""
    start = time.time()

    try:
        import shutil

        total, used, free = shutil.disk_usage("/")
        free_percent = (free / total) * 100
        latency = (time.time() - start) * 1000

        if free_percent > 20:
            status = HealthStatus.HEALTHY
            message = f"{free_percent:.1f}% disk space available"
        elif free_percent > 10:
            status = HealthStatus.DEGRADED
            message = f"Low disk space: {free_percent:.1f}% available"
        else:
            status = HealthStatus.UNHEALTHY
            message = f"Critical disk space: {free_percent:.1f}% available"

        return ComponentHealth(
            name="disk",
            status=status,
            latency_ms=latency,
            message=message,
            details={
                "total_gb": round(total / (1024**3), 2),
                "used_gb": round(used / (1024**3), 2),
                "free_gb": round(free / (1024**3), 2),
                "free_percent": round(free_percent, 2),
            },
        )
    except Exception as e:
        return ComponentHealth(
            name="disk",
            status=HealthStatus.DEGRADED,
            latency_ms=(time.time() - start) * 1000,
            message=f"Disk check failed: {str(e)}",
        )


async def check_memory() -> ComponentHealth:
    """Check system memory usage."""
    start = time.time()

    try:
        import psutil

        mem = psutil.virtual_memory()
        latency = (time.time() - start) * 1000

        if mem.percent < 80:
            status = HealthStatus.HEALTHY
            message = f"{100 - mem.percent:.1f}% memory available"
        elif mem.percent < 90:
            status = HealthStatus.DEGRADED
            message = f"High memory usage: {mem.percent:.1f}% used"
        else:
            status = HealthStatus.UNHEALTHY
            message = f"Critical memory usage: {mem.percent:.1f}% used"

        return ComponentHealth(
            name="memory",
            status=status,
            latency_ms=latency,
            message=message,
            details={
                "total_gb": round(mem.total / (1024**3), 2),
                "available_gb": round(mem.available / (1024**3), 2),
                "percent_used": round(mem.percent, 2),
            },
        )
    except ImportError:
        return ComponentHealth(
            name="memory",
            status=HealthStatus.DEGRADED,
            latency_ms=0,
            message="psutil not installed (memory check skipped)",
        )
    except Exception as e:
        return ComponentHealth(
            name="memory",
            status=HealthStatus.DEGRADED,
            latency_ms=(time.time() - start) * 1000,
            message=f"Memory check failed: {str(e)}",
        )


async def get_system_health(include_external: bool = True) -> SystemHealth:
    """Get comprehensive system health status.

    Args:
        include_external: Whether to check external providers (AI, telephony)

    Returns:
        SystemHealth: Aggregate health status
    """
    from app.config.settings import get_settings

    settings = get_settings()

    # Core health checks (always run)
    checks = [
        check_database_health(),
        check_redis_health(),
        check_disk_space(),
        check_memory(),
    ]

    # External provider checks (optional, slower)
    if include_external:
        # AI providers
        ai_providers = [
            ("openai", "https://api.openai.com/v1/models"),
            ("anthropic", "https://api.anthropic.com/v1/messages"),
            ("google", "https://generativelanguage.googleapis.com/v1/models"),
        ]
        for name, endpoint in ai_providers:
            checks.append(check_ai_provider_health(name, endpoint))

        # Telephony providers
        telephony_providers = [
            ("twilio", "https://api.twilio.com/2010-04-01"),
            ("telnyx", "https://api.telnyx.com/v2"),
        ]
        for name, endpoint in telephony_providers:
            checks.append(check_telephony_provider_health(name, endpoint))

    # Run all checks concurrently
    components = await asyncio.gather(*checks, return_exceptions=True)

    # Handle any exceptions from checks
    processed_components = []
    for result in components:
        if isinstance(result, Exception):
            processed_components.append(ComponentHealth(
                name="unknown",
                status=HealthStatus.UNHEALTHY,
                message=f"Check failed: {str(result)}",
            ))
        else:
            processed_components.append(result)

    # Determine overall status
    statuses = [c.status for c in processed_components]
    if HealthStatus.UNHEALTHY in statuses:
        overall_status = HealthStatus.UNHEALTHY
    elif HealthStatus.DEGRADED in statuses:
        overall_status = HealthStatus.DEGRADED
    else:
        overall_status = HealthStatus.HEALTHY

    return SystemHealth(
        status=overall_status,
        version=settings.version,
        environment=settings.environment,
        uptime_seconds=time.time() - _start_time,
        components=processed_components,
    )


async def get_readiness() -> dict[str, Any]:
    """Check if the application is ready to serve requests.

    This is a lighter check than full health, suitable for Kubernetes readiness probes.
    Only checks critical dependencies (database).
    """
    db_health = await check_database_health()

    is_ready = db_health.status != HealthStatus.UNHEALTHY

    return {
        "ready": is_ready,
        "checks": {
            "database": db_health.status.value,
        },
    }


async def get_liveness() -> dict[str, Any]:
    """Check if the application is alive.

    This is the lightest check, suitable for Kubernetes liveness probes.
    Just verifies the application process is responding.
    """
    return {
        "alive": True,
        "uptime_seconds": round(time.time() - _start_time, 2),
    }
