"""
Speak by Kraliki - Main Application
AI Voice Employee Intelligence Platform

Stack 2026: FastAPI + PostgreSQL + Ed25519 JWT
"""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi.errors import RateLimitExceeded

from app.core.config import settings
from app.core.database import create_tables
from app.core.auth import validate_production_security
from app.middleware.rate_limit import limiter, rate_limit_handler
from app.routers import (
    auth_router,
    surveys_router,
    conversations_router,
    voice_router,
    actions_router,
    alerts_router,
    insights_router,
    employees_router,
    telephony_router,
    usage_router,
    billing_router,
)

logger = logging.getLogger(__name__)


class SpeakAliasMiddleware:
    """Map legacy /api/vop requests to canonical /api/speak routes."""

    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope.get("type") in ("http", "websocket"):
            path = scope.get("path", "")
            alias_prefix = "/api/vop"
            if path == alias_prefix or path.startswith(f"{alias_prefix}/"):
                new_path = "/api/speak" + path[len(alias_prefix):]
                scope = dict(scope)
                scope["path"] = new_path
                if scope.get("raw_path") is not None:
                    scope["raw_path"] = new_path.encode()

        await self.app(scope, receive, send)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events."""
    # Startup
    if settings.debug:
        logger.warning(
            "⚠️  DEBUG MODE ENABLED - This must be disabled in production! "
            "Set DEBUG=false in .env or environment variables."
        )
        await create_tables()
    else:
        logger.info("Starting in production mode (DEBUG=false)")
        validate_production_security()

    yield
    # Shutdown
    pass


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="AI Voice Employee Intelligence Platform",
    lifespan=lifespan,
)

# Legacy aliasing to keep /api/vop working while /api/speak remains canonical.
app.add_middleware(SpeakAliasMiddleware)

# Rate limiting
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, rate_limit_handler)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth_router, prefix="/api")
app.include_router(surveys_router, prefix="/api")
app.include_router(conversations_router, prefix="/api")
app.include_router(voice_router, prefix="/api")
app.include_router(actions_router, prefix="/api")
app.include_router(alerts_router, prefix="/api")
app.include_router(insights_router, prefix="/api")
app.include_router(employees_router, prefix="/api")
app.include_router(telephony_router, prefix="/api")
app.include_router(usage_router, prefix="/api")
app.include_router(billing_router, prefix="/api")


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "name": settings.app_name,
        "version": settings.app_version,
        "status": "running"
    }


@app.get("/health")
@app.get("/api/health")
async def health():
    """Health check endpoint."""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
    )
