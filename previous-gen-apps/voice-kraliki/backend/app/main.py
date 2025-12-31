"""Main application factory and FastAPI app configuration.

This module provides the application factory pattern for creating
and configuring the FastAPI application instance.
"""

import logging
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from typing import Any
from uuid import UUID

from fastapi import FastAPI, HTTPException, Request, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from prometheus_fastapi_instrumentator import Instrumentator
from slowapi.errors import RateLimitExceeded

from app.api.alert_webhooks import router as alert_webhooks_router

# from app.api.compliance import router as compliance_router
from app.api.alerting import router as alerting_router
from app.api.billing import router as billing_router
from app.api.call_dispositions import router as call_dispositions_router
from app.api.campaign_management import router as campaign_management_router

# Import missing API routers
from app.api.campaign_scripts import router as campaign_scripts_router
from app.api.companies import router as companies_router

from app.api.analytics import router as analytics_router
from app.api.feature_flags import router as feature_flags_router
from app.api.monitoring import router as monitoring_router
from app.api.queue_management import router as queue_management_router
from app.api.scenarios import router as scenarios_router
from app.api.scorecards import router as scorecards_router
from app.api.sessions import router as sessions_router
from app.api.supervisor import router as supervisor_router
from app.api.team_management import router as team_management_router
from app.api.telephony import router as telephony_api_router
from app.api.v1.endpoints.analytics import router as analytics_v1_router
from app.api.v1.endpoints.ivr import router as ivr_router
from app.api.v1.endpoints.recording import router as recording_router
from app.api.v1.endpoints.reports import router as reports_router
from app.api.v1.endpoints.routing import router as routing_router
from app.api.v1.endpoints.usage import router as usage_router
from app.api.v1.endpoints.voicemail import router as voicemail_router

# Import arena routes
from app.arena_routes import router as arena_router
from app.auth.routes import router as auth_router
from app.campaigns.routes import router as campaigns_router

# Import APM and monitoring
from app.config.sentry import init_sentry
from app.config.settings import get_settings

# Import structured logging
from app.logging import configure_root_logger, get_logger
from app.middleware.correlation_id import CorrelationIdMiddleware
from app.middleware.rate_limit import SESSION_RATE_LIMIT, limiter, rate_limit_handler
from app.providers.registry import get_provider_registry
from app.sessions.manager import get_session_manager
from app.sessions.models import SessionCreateRequest, SessionResponse, SessionStatus
from app.settings.provider import router as provider_settings_router
from app.streaming.websocket import create_websocket_handler
from app.telephony.routes import router as telephony_router


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None]:
    """Application lifespan manager.

    Handles startup and shutdown events for the application.
    """
    settings = get_settings()

    # Configure structured logging
    log_level = logging.DEBUG if settings.debug else logging.INFO
    configure_root_logger(service_name=settings.app_name, level=log_level)
    logger = get_logger(__name__)

    # Initialize Sentry for error tracking
    init_sentry()

    # Startup
    logger.info(
        "Application starting",
        app_name=settings.app_name,
        version=settings.version,
        environment=settings.environment,
        debug=settings.debug,
    )

    # Initialize database
    from app.database_init import initialize_database

    logger.info("Initializing database")
    if initialize_database():
        logger.info("Database initialized successfully")
    else:
        logger.warning("Database initialization failed (continuing anyway)")

    # Recover active call states
    from app.telephony.call_state_manager import get_call_state_manager

    try:
        manager = get_call_state_manager()
        active_calls = manager.recover_active_calls()
        if active_calls:
            logger.info(
                "Recovered active calls from database", active_calls_count=len(active_calls)
            )
    except Exception as exc:
        logger.log_exception("Failed to recover active calls", exc=exc)

    yield

    # Shutdown
    logger.info("Application shutting down")


def create_app() -> FastAPI:
    """Create and configure the FastAPI application.

    Returns:
        FastAPI: Configured FastAPI application instance
    """
    settings = get_settings()

    app = FastAPI(
        title=settings.app_name,
        version=settings.version,
        description="Stack 2026 compliant backend for operator demo multiprovider",
        debug=settings.debug,
        lifespan=lifespan,
    )

    # Rate limiting - wire the limiter into the app
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, rate_limit_handler)

    # Add correlation ID middleware (before CORS so it's available in all requests)
    app.add_middleware(CorrelationIdMiddleware)

    # Configure CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Initialize Prometheus FastAPI Instrumentator for automatic request metrics
    instrumentator = Instrumentator(
        should_group_status_codes=False,
        should_ignore_untemplated=True,
        should_respect_env_var=True,
        should_instrument_requests_inprogress=True,
        excluded_handlers=["/metrics", "/health", "/ready", "/live"],
        env_var_name="ENABLE_METRICS",
        inprogress_name="http_requests_inprogress",
        inprogress_labels=True,
    )
    instrumentator.instrument(app).expose(app, endpoint="/metrics", include_in_schema=False)

    # Initialize logger for route handlers
    logger = get_logger(__name__)

    # Health check endpoint
    @app.get("/health")
    async def health_check() -> dict[str, str]:
        """Health check endpoint.

        Returns:
            dict: Health status information
        """
        logger.debug("Health check requested")
        return {
            "status": "healthy",
            "service": settings.app_name,
            "version": settings.version,
            "environment": settings.environment,
        }

    # Readiness probe for Kubernetes/load balancers
    @app.get("/ready")
    async def readiness_check() -> dict[str, Any]:
        """Kubernetes-style readiness probe.

        Returns whether the application is ready to receive traffic.
        Checks database connectivity.

        Returns:
            dict: Readiness status
        """
        from app.monitoring.health_service import get_readiness

        return await get_readiness()

    # Liveness probe for Kubernetes
    @app.get("/live")
    async def liveness_check() -> dict[str, Any]:
        """Kubernetes-style liveness probe.

        Returns whether the application process is alive.

        Returns:
            dict: Liveness status
        """
        from app.monitoring.health_service import get_liveness

        return await get_liveness()

    # Root endpoint
    @app.get("/")
    async def root() -> dict[str, str]:
        """Root endpoint.

        Returns:
            dict: Basic API information
        """
        return {
            "message": f"Welcome to {settings.app_name}",
            "version": settings.version,
            "docs": "/docs",
            "health": "/health",
            "ready": "/ready",
            "metrics": "/metrics",
        }

    # Include authentication routes
    app.include_router(auth_router)
    app.include_router(provider_settings_router)
    app.include_router(telephony_router)
    app.include_router(campaigns_router)

    # Include API routers (previously unregistered)
    app.include_router(campaign_scripts_router)
    app.include_router(campaign_management_router)
    app.include_router(team_management_router)
    app.include_router(supervisor_router)
    app.include_router(companies_router)
    app.include_router(call_dispositions_router)
    app.include_router(telephony_api_router)
    # app.include_router(compliance_router)
    app.include_router(alerting_router)
    app.include_router(analytics_router)
    app.include_router(monitoring_router)
    app.include_router(alert_webhooks_router)
    app.include_router(sessions_router)
    app.include_router(queue_management_router)
    app.include_router(ivr_router)
    app.include_router(routing_router)
    app.include_router(recording_router)
    app.include_router(voicemail_router)
    app.include_router(analytics_v1_router)
    app.include_router(reports_router)
    app.include_router(scenarios_router)
    app.include_router(scorecards_router)
    app.include_router(arena_router)
    app.include_router(billing_router)
    app.include_router(usage_router)
    app.include_router(feature_flags_router)

    # ===== Provider API Endpoints =====

    provider_registry = get_provider_registry()

    @app.get("/api/v1/providers")
    async def list_providers() -> dict[str, list[dict[str, Any]]]:
        """List available AI and telephony providers with metadata."""
        logger.info("Listing available providers", endpoint="/api/v1/providers")

        providers = [info.model_dump() for info in provider_registry.list_providers()]
        telephony = [info.model_dump() for info in provider_registry.list_telephony_adapters()]

        logger.debug(
            "Providers listed", providers_count=len(providers), telephony_count=len(telephony)
        )

        return {"providers": providers, "telephony": telephony}

    # ===== Session Management Endpoints =====

    @limiter.limit(SESSION_RATE_LIMIT)
    @app.post("/api/v1/sessions/bootstrap")
    async def bootstrap_session(request: Request, session_request: SessionCreateRequest) -> dict:
        """Bootstrap a session and return websocket URL + session ID.

        This endpoint provides complete information needed to establish
        a WebSocket connection for a session, including websocket URL
        and session identifier. Rate limited to prevent abuse.

        Args:
            request: FastAPI request (for rate limiting)
            session_request: Session creation parameters

        Returns:
            dict: Session bootstrap information with websocket URL
        """
        try:
            logger.info(
                "Bootstrapping new session",
                provider_type=session_request.provider_type,
                strategy=session_request.strategy,
            )

            session_manager = get_session_manager()
            session = await session_manager.create_session(session_request)

            # Build websocket URL
            settings = get_settings()
            ws_scheme = "wss" if settings.environment == "production" else "ws"
            host = settings.host if settings.host not in ["0.0.0.0", "::"] else "localhost"
            ws_url = f"{ws_scheme}://{host}:{settings.port}/ws/sessions/{session.id}"

            logger.info(
                "Session bootstrapped successfully",
                session_id=str(session.id),
                provider_type=session.provider_type,
                websocket_url=ws_url,
            )

            return {
                "session_id": str(session.id),
                "websocket_url": ws_url,
                "provider_type": session.provider_type,
                "status": session.status.value,
                "metadata": session.metadata,
            }
        except ValueError as e:
            logger.error("Invalid session bootstrap request", error=str(e), error_type="ValueError")
            raise HTTPException(status_code=400, detail=str(e))
        except Exception as e:
            logger.log_exception("Failed to bootstrap session", exc=e)
            raise HTTPException(status_code=500, detail=f"Failed to bootstrap session: {e}")

    @limiter.limit(SESSION_RATE_LIMIT)
    @app.post("/api/v1/sessions")
    async def create_session(
        request: Request, session_request: SessionCreateRequest
    ) -> SessionResponse:
        """Create a new AI conversation session. Rate limited to prevent abuse.

        Args:
            request: FastAPI request (for rate limiting)
            session_request: Session creation parameters

        Returns:
            SessionResponse: Created session information

        Raises:
            HTTPException: If provider type is invalid or creation fails
        """
        try:
            session_manager = get_session_manager()
            session = await session_manager.create_session(session_request)

            return SessionResponse(
                id=session.id,
                provider_type=session.provider_type,
                provider_model=session.provider_model,
                strategy=session.strategy,
                telephony_provider=session.telephony_provider,
                status=session.status,
                created_at=session.created_at,
                updated_at=session.updated_at,
                ended_at=session.ended_at,
                metadata=session.metadata,
            )
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to create session: {e}")

    @app.get("/api/v1/sessions/{session_id}", response_model=SessionResponse)
    async def get_session(session_id: UUID) -> SessionResponse:
        """Get session details by ID.

        Args:
            session_id: Session identifier

        Returns:
            SessionResponse: Session information

        Raises:
            HTTPException: If session not found
        """
        session_manager = get_session_manager()
        session = await session_manager.get_session(session_id)

        if not session:
            raise HTTPException(status_code=404, detail="Session not found")

        return SessionResponse(
            id=session.id,
            provider_type=session.provider_type,
            provider_model=session.provider_model,
            strategy=session.strategy,
            telephony_provider=session.telephony_provider,
            status=session.status,
            created_at=session.created_at,
            updated_at=session.updated_at,
            ended_at=session.ended_at,
            metadata=session.metadata,
        )

    @app.get("/api/v1/sessions")
    async def list_sessions(
        status: SessionStatus | None = None,
    ) -> dict[str, list[SessionResponse]]:
        """List all sessions, optionally filtered by status.

        Args:
            status: Optional status filter

        Returns:
            dict: List of sessions
        """
        session_manager = get_session_manager()
        sessions = await session_manager.list_sessions(status)

        return {
            "sessions": [
                SessionResponse(
                    id=s.id,
                    provider_type=s.provider_type,
                    provider_model=s.provider_model,
                    strategy=s.strategy,
                    telephony_provider=s.telephony_provider,
                    status=s.status,
                    created_at=s.created_at,
                    updated_at=s.updated_at,
                    ended_at=s.ended_at,
                    metadata=s.metadata,
                )
                for s in sessions
            ]
        }

    @app.post("/api/v1/sessions/{session_id}/start")
    async def start_session(session_id: UUID) -> dict[str, str]:
        """Start a session by connecting to the AI provider.

        Args:
            session_id: Session identifier

        Returns:
            dict: Success message

        Raises:
            HTTPException: If session not found or start fails
        """
        try:
            session_manager = get_session_manager()
            await session_manager.start_session(session_id)
            return {"message": "Session started successfully"}
        except ValueError as e:
            raise HTTPException(status_code=404, detail=str(e))
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to start session: {e}")

    @app.post("/api/v1/sessions/{session_id}/end")
    async def end_session(session_id: UUID) -> dict[str, str]:
        """End a session and cleanup resources.

        Args:
            session_id: Session identifier

        Returns:
            dict: Success message
        """
        session_manager = get_session_manager()
        await session_manager.end_session(session_id)
        return {"message": "Session ended successfully"}

    # ===== WebSocket Streaming Endpoint =====

    async def _handle_websocket_session(websocket: WebSocket, session_id: UUID) -> None:
        """Shared WebSocket session handler."""
        handler = await create_websocket_handler(websocket, session_id)
        await handler.handle()

    @app.websocket("/ws/sessions/{session_id}")
    async def websocket_stream(websocket: WebSocket, session_id: UUID) -> None:
        """Primary WebSocket endpoint for real-time audio/text streaming.

        Establishes bidirectional streaming connection between client
        and AI provider for the specified session.

        Args:
            websocket: WebSocket connection
            session_id: Session identifier
        """
        await _handle_websocket_session(websocket, session_id)

    @app.websocket("/api/v1/sessions/{session_id}/stream")
    async def websocket_stream_legacy(websocket: WebSocket, session_id: UUID) -> None:
        """Legacy WebSocket endpoint retained for backwards compatibility."""
        await _handle_websocket_session(websocket, session_id)

    return app


# Create application instance
app = create_app()


if __name__ == "__main__":
    import uvicorn

    settings = get_settings()
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
    )
