"""
Voice by Kraliki Communications Module for Ocelot Platform
Exports FastAPI app for platform mounting via API Gateway
"""

from fastapi import FastAPI, Request, HTTPException
from typing import Optional

from app.core.config import settings
from app.core.events import EventPublisher
from app.core.logger import get_logger

logger = get_logger(__name__)


class CommsModule:
    """
    Communications Module for Ocelot Platform

    Provides two modes:
    1. Standalone: Full authentication with Ed25519 JWT
    2. Platform: Trust headers from API Gateway (X-User-Id, X-Org-Id)

    Usage in Ocelot Platform:
        from cc_lite.backend.app.module import CommsModule

        comms = CommsModule(
            event_publisher=platform_event_publisher,
            platform_mode=True
        )

        app.mount("/api/communications", comms.get_app())
    """

    def __init__(
        self,
        event_publisher: Optional[EventPublisher] = None,
        platform_mode: bool = False,
    ):
        """
        Initialize Communications Module

        Args:
            event_publisher: Shared event publisher from platform (optional)
            platform_mode: If True, trust API Gateway headers instead of JWT
        """
        self.app = FastAPI(
            title="Communications Module",
            description="Multichannel communications and call center",
            version="2.0.0",
        )
        self.event_publisher = event_publisher
        self.platform_mode = platform_mode
        self._request_count = 0
        self._error_count = 0
        self._route_metrics = {}  # Track per-route metrics
        self._status_code_counts = {}  # Track status codes

        # Register middleware
        if platform_mode:
            self._register_platform_middleware()

        # Enhanced metrics middleware
        @self.app.middleware("http")
        async def _metrics_middleware(request, call_next):
            import time
            from fastapi.responses import Response

            start_time = time.time()
            self._request_count += 1

            # Track route
            route_path = request.url.path
            if route_path not in self._route_metrics:
                self._route_metrics[route_path] = {
                    "count": 0,
                    "errors": 0,
                    "avg_duration_ms": 0,
                    "total_duration_ms": 0
                }

            try:
                response = await call_next(request)

                # Track status codes
                status_code = response.status_code
                self._status_code_counts[status_code] = self._status_code_counts.get(status_code, 0) + 1

                # Update route metrics
                duration_ms = (time.time() - start_time) * 1000
                metrics = self._route_metrics[route_path]
                metrics["count"] += 1
                metrics["total_duration_ms"] += duration_ms
                metrics["avg_duration_ms"] = metrics["total_duration_ms"] / metrics["count"]

                if status_code >= 400:
                    metrics["errors"] += 1
                    self._error_count += 1

                return response
            except Exception as e:
                self._error_count += 1
                self._route_metrics[route_path]["errors"] += 1
                logger.error(f"Unhandled error on {route_path}: {e}")
                raise

        @self.app.get("/metrics")
        async def module_metrics():
            """Get comprehensive module metrics"""
            # Calculate error rate
            error_rate = (self._error_count / self._request_count * 100) if self._request_count > 0 else 0

            # Get top routes by request count
            top_routes = sorted(
                [
                    {
                        "path": path,
                        "count": metrics["count"],
                        "errors": metrics["errors"],
                        "avg_duration_ms": round(metrics["avg_duration_ms"], 2)
                    }
                    for path, metrics in self._route_metrics.items()
                ],
                key=lambda x: x["count"],
                reverse=True
            )[:10]  # Top 10 routes

            return {
                "module": "communications",
                "mode": "platform" if self.platform_mode else "standalone",
                "requests_total": self._request_count,
                "errors_total": self._error_count,
                "error_rate_percent": round(error_rate, 2),
                "status_codes": self._status_code_counts,
                "top_routes": top_routes,
                "routes_tracked": len(self._route_metrics)
            }

        # Register all routers
        self._register_routers()

        logger.info(
            f"Communications Module initialized (mode: {'platform' if platform_mode else 'standalone'})"
        )

    def _register_platform_middleware(self):
        """
        Platform mode middleware

        Trusts headers from API Gateway:
        - X-User-Id: Current user ID
        - X-Org-Id: Current organization ID
        - X-User-Role: User role (admin, manager, member, etc.)
        """

        @self.app.middleware("http")
        async def platform_auth_middleware(request: Request, call_next):
            """Extract user context from platform headers"""
            user_id = request.headers.get("X-User-Id")
            org_id = request.headers.get("X-Org-Id")
            user_role = request.headers.get("X-User-Role", "member")

            if not user_id or not org_id:
                raise HTTPException(
                    status_code=401,
                    detail="Missing platform authentication headers (X-User-Id, X-Org-Id)",
                )

            # Attach to request state for dependency injection
            request.state.user_id = user_id
            request.state.org_id = org_id
            request.state.user_role = user_role
            request.state.platform_mode = True

            return await call_next(request)

    def _register_routers(self):
        """Register all API routers"""
        from app.routers import (
            auth,
            calls,
            campaigns,
            agents,
            webhooks,
            teams,
            analytics,
            supervisor,
            contacts,
            sentiment,
            ivr,
            dashboard,
            telephony,
            ai,
            metrics,
            circuit_breaker,
            agent_assist,
            ai_health,
            payments,
            call_byok,
            agent_router,
        )

        # Register routers with /api prefix
        routers = [
            auth.router,
            calls.router,
            campaigns.router,
            agents.router,
            webhooks.router,
            teams.router,
            analytics.router,
            supervisor.router,
            contacts.router,
            sentiment.router,
            ivr.router,
            dashboard.router,
            telephony.router,
            ai.router,
            metrics.router,
            circuit_breaker.router,
            agent_assist.router,
            ai_health.router,
            payments.router,
            call_byok.router,
            agent_router.router,
        ]

        for router in routers:
            self.app.include_router(router)

    def get_app(self) -> FastAPI:
        """
        Return FastAPI app for mounting

        Returns:
            FastAPI application instance
        """
        return self.app

    async def handle_event(self, event: dict):
        """
        Handle events from other platform modules

        Args:
            event: Event payload from platform event bus

        Example events to handle:
        - task.completed: Trigger follow-up campaign
        - user.onboarded: Send welcome call
        - payment.failed: Send reminder call
        """
        event_type = event.get("type")

        logger.info(f"Received platform event: {event_type}")

        # TODO: Implement event handlers
        if event_type == "task.completed":
            # Maybe trigger a campaign based on task completion
            pass
        elif event_type == "user.onboarded":
            # Send welcome call
            pass

    def get_health(self) -> dict:
        """
        Health check for platform monitoring

        Returns:
            Health status dict
        """
        return {
            "module": "communications",
            "status": "healthy",
            "mode": "platform" if self.platform_mode else "standalone",
            "version": "2.0.0",
        }


# Standalone execution
if __name__ == "__main__":
    import uvicorn
    from app.core.events import event_publisher

    # Create module in standalone mode
    module = CommsModule(event_publisher=event_publisher, platform_mode=False)

    # Run with uvicorn
    uvicorn.run(
        module.get_app(),
        host=settings.HOST,
        port=settings.PORT,
        log_level="debug" if settings.DEBUG else "info",
    )
