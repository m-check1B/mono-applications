"""
Focus by Kraliki Planning Module for Ocelot Platform
Dual-mode operation: Standalone or Platform-mounted
"""

import logging

from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
from typing import Dict, Any, Optional


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Add security headers to all responses.

    OWASP recommended security headers to prevent common attacks:
    - XSS, clickjacking, MIME sniffing, etc.
    """

    async def dispatch(self, request: Request, call_next) -> Response:
        response = await call_next(request)

        # Prevent MIME type sniffing
        response.headers["X-Content-Type-Options"] = "nosniff"

        # Prevent clickjacking (allow same-origin frames for SvelteKit embedding)
        response.headers["X-Frame-Options"] = "SAMEORIGIN"

        # Enable XSS filter in browsers (legacy but still useful)
        response.headers["X-XSS-Protection"] = "1; mode=block"

        # Control referrer information leakage
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"

        # Disable potentially dangerous browser features
        response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"

        # Content Security Policy (API-focused, allow self)
        # Note: Frontend handles its own CSP via SvelteKit
        response.headers["Content-Security-Policy"] = "default-src 'self'; frame-ancestors 'self'"

        # HSTS - Enforce HTTPS for 1 year, include subdomains
        # This is critical for production HTTPS security
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"

        return response

logger = logging.getLogger(__name__)

from app.core.config import settings
from app.core.database import Base, engine
from app.core.events import event_publisher
from app.core.token_revocation import token_blacklist
from app.routers import (
    auth,
    auth_v2,
    tasks,
    ai,
    google_oauth,
    users,
    shadow,
    assistant,
    pricing,
    swarm_tools,
    projects,
    time_entries,
    events,
    ai_scheduler,
    ai_stream,
    websocket,
    flow_memory,
    knowledge,
    knowledge_ai,
    ai_file_search,
    voice,
    workflow,
    # agent,  # Legacy agent router
    agent_sessions,  # New agent sessions router
    agent_tools,
    billing,
    workspaces,
    analytics,
    onboarding,
    exports,
    calendar_integration,
)
from app.routers import settings as settings_router


class PlanningModule:
    """
    Planning module for Ocelot Platform integration.

    Modes:
    - Standalone: Independent FastAPI app with full auth
    - Platform: Mounted behind API Gateway, trusts platform headers
    """

    def __init__(
        self,
        platform_mode: Optional[bool] = None,
        event_publisher_instance: Optional[Any] = None
    ):
        """
        Initialize Planning Module.

        Args:
            platform_mode: If True, trusts API Gateway headers for auth. If None, uses settings.
            event_publisher_instance: Optional shared event publisher
        """
        if platform_mode is not None:
            self.platform_mode = platform_mode
        else:
            self.platform_mode = settings.PLATFORM_MODE
        
        self.app = self._create_app()
        self.event_publisher = event_publisher_instance or event_publisher
        self._request_count = 0
        self._error_count = 0
        self._event_bus_ready = False

    def _create_app(self) -> FastAPI:
        """Create and configure FastAPI application."""
        app = FastAPI(
            title="Focus by Kraliki Planning Module",
            description="AI-first task and project planning system",
            version="2.1.0",
            docs_url="/docs" if settings.DEBUG else None,
            redoc_url="/redoc" if settings.DEBUG else None
        )

        # Create database tables (skip in test mode)
        import os
        if os.getenv("SKIP_DB_INIT") != "1":
            Base.metadata.create_all(bind=engine)

        # Add security headers middleware (OWASP recommended)
        app.add_middleware(SecurityHeadersMiddleware)

        # Add CORS middleware (only in standalone mode)
        if not self.platform_mode:
            app.add_middleware(
                CORSMiddleware,
                allow_origins=settings.origins_list,
                allow_credentials=True,
                allow_methods=["*"],
                allow_headers=["*"],
            )

            @app.middleware("http")
            async def _cors_options_fallback(request: Request, call_next):
                response = await call_next(request)
                if request.method == "OPTIONS" and "access-control-allow-origin" not in response.headers:
                    response.headers["Access-Control-Allow-Origin"] = "*"
                return response

        # Add platform mode middleware
        if self.platform_mode:
            app.middleware("http")(self._platform_auth_middleware)

        # Register routers
        self._register_routers(app)

        # Startup/shutdown events
        app.add_event_handler("startup", self._on_startup)
        app.add_event_handler("shutdown", self._on_shutdown)

        # Error logging + metrics middleware (non-intrusive)
        @app.middleware("http")
        async def _error_logging_middleware(request, call_next):
            self._request_count += 1
            try:
                return await call_next(request)
            except Exception as e:
                self._error_count += 1
                logger.error(f"[Focus by Kraliki] Unhandled error: {e}")
                raise

        return app

    def _register_routers(self, app: FastAPI):
        """Register API routers."""
        # Use Ed25519 auth (stack 2026) and keep legacy v2 routes for compatibility
        app.include_router(auth.router)
        app.include_router(auth_v2.router)

        # Legacy OAuth (keep for now)
        app.include_router(google_oauth.router)

        # Core features
        app.include_router(users.router)
        app.include_router(tasks.router)
        app.include_router(projects.router)
        app.include_router(events.router)
        app.include_router(time_entries.router)
        app.include_router(knowledge.router)
        app.include_router(knowledge_ai.router)
        app.include_router(ai_file_search.router)
        app.include_router(onboarding.router)
        app.include_router(ai.flow_memory_router)
        app.include_router(ai.router)
        app.include_router(ai_scheduler.router)
        app.include_router(shadow.router)
        app.include_router(flow_memory.router)
        app.include_router(assistant.router)
        app.include_router(pricing.router)
        app.include_router(swarm_tools.router)
        app.include_router(voice.router)
        app.include_router(workflow.router)
        app.include_router(ai_stream.router)
        app.include_router(websocket.router)
        # app.include_router(agent.router)  # Legacy
        app.include_router(agent_sessions.router)
        app.include_router(agent_tools.router)
        app.include_router(settings_router.router)
        app.include_router(billing.router)
        app.include_router(workspaces.router)
        app.include_router(analytics.router)
        app.include_router(exports.router)
        app.include_router(calendar_integration.router)

        # Integration status endpoints
        from app.routers import (
            calendar_sync, 
            webhooks, 
            linear_sync, 
            notifications,
            brain,
            comments,
            activity,
            captures,
            sales,
            academy
        )
        app.include_router(calendar_sync.router)
        app.include_router(webhooks.router)
        app.include_router(linear_sync.router)
        app.include_router(notifications.router)
        app.include_router(brain.router)
        app.include_router(comments.router)
        app.include_router(activity.router)
        app.include_router(captures.router)
        app.include_router(sales.router)
        app.include_router(academy.router)

        # Health check
        @app.get("/")
        async def root():
            return {
                "name": "Focus by Kraliki Planning Module",
                "version": "2.1.0",
                "mode": "platform" if self.platform_mode else "standalone",
                "status": "running"
            }

        @app.get("/health")
        async def health_check():
            return {
                "status": "healthy",
                "mode": "platform" if self.platform_mode else "standalone"
            }

        @app.get("/metrics")
        async def module_metrics():
            return {
                "module": "planning",
                "mode": "platform" if self.platform_mode else "standalone",
                "requests": self._request_count,
                "errors": self._error_count,
            }

    async def _platform_auth_middleware(self, request: Request, call_next):
        """
        Platform mode middleware: Trust API Gateway headers.

        The API Gateway verifies JWT and sets headers:
        - X-User-Id: Authenticated user ID
        - X-Org-Id: Organization ID
        - X-Roles: User roles (comma-separated)

        These headers are trusted in platform mode.
        """
        if self.platform_mode and not request.url.path.startswith(("/health", "/integration/calendar/status")):
            # Extract platform headers
            user_id = request.headers.get("X-User-Id")
            org_id = request.headers.get("X-Org-Id")

            if not user_id or not org_id:
                return JSONResponse(
                    status_code=401,
                    content={"detail": "Missing platform authentication headers"},
                )

            # Attach to request state (available in dependencies)
            request.state.user_id = user_id
            request.state.org_id = org_id
            request.state.roles = request.headers.get("X-Roles", "").split(",")

        return await call_next(request)

    async def _on_startup(self):
        """Initialize connections on startup."""
        # Connect to Redis (token revocation)
        await token_blacklist.connect()

        # Connect to RabbitMQ (event publishing) – tolerate local dev without broker
        try:
            await self.event_publisher.connect()
            self._event_bus_ready = True
        except Exception as exc:  # pragma: no cover - developer convenience
            self._event_bus_ready = False
            logger.warning(f"Event publisher unavailable ({exc}). Proceeding without RabbitMQ.")

        mode = "Platform" if self.platform_mode else "Standalone"
        event_status = self.event_publisher.amqp_url if self._event_bus_ready else "DISABLED (RabbitMQ not reachable)"
        logger.info(f"Focus by Kraliki Planning Module started - Mode: {mode}, Event Publishing: {event_status}, Token Revocation: {token_blacklist.redis_url}")

    async def _on_shutdown(self):
        """Close connections on shutdown."""
        await token_blacklist.disconnect()
        await self.event_publisher.disconnect()
        logger.info("Focus by Kraliki Planning Module stopped")

    def get_app(self) -> FastAPI:
        """
        Get FastAPI application for mounting or running.

        Returns:
            FastAPI app instance
        """
        return self.app

    async def handle_event(self, event: Dict[str, Any]):
        """
        Handle events from other platform modules.

        Example events to handle:
        - call.ended → Create follow-up task
        - campaign.completed → Mark milestone
        - agent.workflow_suggested → Auto-create tasks

        Args:
            event: Event dictionary with type, data, etc.
        """
        event_type = event.get("type")

        if event_type == "call.ended":
            # Create follow-up task if callback requested
            if event.get("data", {}).get("outcome") == "callback_requested":
                await self._create_followup_task(event["data"])

        elif event_type == "agent.workflow_suggested":
            # Auto-create tasks from workflow suggestion
            await self._create_tasks_from_workflow(event["data"])

    async def _create_followup_task(self, call_data: Dict[str, Any]):
        """Create follow-up task from call event."""
        # Implementation will integrate with tasks service
        pass

    async def _create_tasks_from_workflow(self, workflow_data: Dict[str, Any]):
        """Create tasks from agent workflow suggestion."""
        # Implementation will integrate with tasks service
        pass


# Standalone mode entry point
def create_standalone_app() -> FastAPI:
    """
    Create standalone Focus by Kraliki app (not platform-mounted).

    Returns:
        FastAPI application
    """
    module = PlanningModule(platform_mode=False)
    return module.get_app()


# Platform mode entry point
def create_platform_module() -> PlanningModule:
    """
    Create platform-mounted Focus by Kraliki module.

    Returns:
        PlanningModule instance for platform integration
    """
    return PlanningModule(platform_mode=True)


# Default export for standalone uvicorn
app = create_standalone_app()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.module:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG
    )
