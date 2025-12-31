from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response, JSONResponse
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from app.core.config import settings


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
        response.headers["Permissions-Policy"] = (
            "geolocation=(), microphone=(), camera=()"
        )

        # Content Security Policy (API-focused, allow self)
        # Note: Frontend handles its own CSP via SvelteKit
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; frame-ancestors 'self'"
        )

        # HSTS - Enforce HTTPS for 1 year, include subdomains
        # This is critical for production HTTPS security
        response.headers["Strict-Transport-Security"] = (
            "max-age=31536000; includeSubDomains"
        )

        return response


from app.core.database import Base, engine
from app.middleware.rate_limit import limiter
from app.routers import (
    auth,
    tasks,
    ai,
    google_oauth,
    users,
    shadow,
    assistant,
    pricing,
    swarm_tools,
    projects,
    events,
    time_entries,
    ai_scheduler,
    voice,
    workflow,
    ai_stream,
    websocket,
    flow_memory,
    knowledge,
    knowledge_ai,
    ai_file_search,
    agent,
    agent_tools,
    agent_sessions,
    billing,
    workspaces,
    analytics,
    onboarding,
    exports,
    calendar_sync,
    calendar_integration,
    webhooks,
    orchestration,
    academy,
    linear_sync,
    notifications,
    brain,
    comments,
    activity,
    captures,
    sales,
    search,
)
from app.routers import settings as settings_router
from app.routers import infra
from app.routers.flow_memory import close_redis_client as close_flow_memory_redis

# Create database tables (skip in test mode)
import os

if os.getenv("SKIP_DB_INIT") != "1":
    Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Focus by Kraliki API",
    description="AI-first productivity system backend",
    version="2.1.0",
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
)


@app.on_event("shutdown")
async def shutdown_resources() -> None:
    await close_flow_memory_redis()

# Rate limiting middleware (protects against abuse)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Security headers middleware (OWASP recommended)
app.add_middleware(SecurityHeadersMiddleware)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Global exception handler for sanitized error responses
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    if settings.DEBUG:
        return JSONResponse(
            status_code=500, content={"detail": str(exc), "type": type(exc).__name__}
        )
    else:
        return JSONResponse(
            status_code=500, content={"detail": "Internal server error"}
        )


# Include routers
app.include_router(auth.router)
app.include_router(google_oauth.router)
app.include_router(users.router)
app.include_router(tasks.router)
app.include_router(projects.router)
app.include_router(events.router)
app.include_router(time_entries.router)
app.include_router(knowledge.router)  # Knowledge layer
app.include_router(knowledge_ai.router)  # AI-powered knowledge management
app.include_router(ai_file_search.router)  # AI File Search with Gemini
app.include_router(ai.router)
app.include_router(ai_scheduler.router)  # AI task scheduler
app.include_router(shadow.router)
app.include_router(flow_memory.router)  # Flow Memory System
app.include_router(assistant.router)
app.include_router(pricing.router)
app.include_router(swarm_tools.router)
app.include_router(voice.router)
app.include_router(workflow.router)
app.include_router(ai_stream.router)
app.include_router(websocket.router)
# app.include_router(agent.router)  # II-Agent session management (Legacy/Conflicting)
app.include_router(agent_sessions.router)  # II-Agent execution sessions
app.include_router(agent_tools.router)  # II-Agent tools API
app.include_router(settings_router.router)  # Settings and BYOK
app.include_router(billing.router)  # Stripe billing and subscriptions
app.include_router(workspaces.router)
app.include_router(analytics.router)
app.include_router(onboarding.router)  # Persona onboarding and trust (Track 5)
app.include_router(exports.router)  # Invoice and billable exports (Track 6)
app.include_router(calendar_sync.router)  # Google Calendar two-way sync (Track 6)
app.include_router(
    calendar_integration.router
)  # Lightweight calendar integration endpoints
app.include_router(infra.router)  # Infrastructure status and logs
app.include_router(orchestration.router)  # n8n orchestration triggers
app.include_router(academy.router)  # AI Academy leads and waitlist
app.include_router(webhooks.router)  # n8n/external webhook integration (VD-239)
app.include_router(linear_sync.router)  # Focus → Linear sync for swarm execution
app.include_router(notifications.router)  # Push notifications (VD-384)
app.include_router(brain.router)  # Focus Brain - central AI intelligence
app.include_router(comments.router)  # Team collaboration - comments
app.include_router(activity.router)
app.include_router(captures.router)
app.include_router(sales.router)
app.include_router(search.router)  # Semantic search (VD-340)


@app.get("/")
async def root():
    return {"name": "Focus by Kraliki API", "version": "2.1.0", "status": "running"}


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup resources on shutdown"""
    # Close Redis connections if any
    from app.routers.flow_memory import _redis_client

    if _redis_client is not None:
        await _redis_client.close()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app", host=settings.HOST, port=settings.PORT, reload=settings.DEBUG
    )
