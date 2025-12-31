#!/usr/bin/env python3
"""
Voice by Kraliki FastAPI Backend
Call center application with AI-powered telephony
Stack 2026 - Python 3.11+ + FastAPI + SQLAlchemy
"""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import os
import sys
from pathlib import Path

from app.core.config import settings
from app.core.database import init_db, get_db
from app.core.logger import setup_logging, get_logger
from app.core.events import event_publisher

# Setup logging first
setup_logging(level=10 if settings.DEBUG else 20)
logger = get_logger(__name__)

# Security check for production
if not settings.DEBUG and settings.SECRET_KEY == "change-me-in-production":
    logger.error("=" * 80)
    logger.error("SECURITY ERROR: Default SECRET_KEY detected in production!")
    logger.error("Set environment variable: export CC_LITE_SECRET_KEY='your-secret-key'")
    logger.error("Generate with: python3 -c 'import secrets; print(secrets.token_hex(32))'")
    logger.error("=" * 80)
    sys.exit(1)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    # Startup
    logger.info("🚀 Initializing Voice by Kraliki backend...")

    # Initialize database
    await init_db()
    logger.info("✅ Database initialized")

    # Initialize event publisher (RabbitMQ)
    if settings.ENABLE_EVENTS:
        try:
            await event_publisher.connect()
            logger.info("✅ Event publisher initialized")
        except Exception as e:
            logger.warning(f"Event publisher failed to initialize: {e}")

    # TODO: Initialize telephony services
    # TODO: Initialize AI services
    # TODO: Initialize Redis/Cache

    logger.info("=" * 60)
    logger.info("📞 Voice by Kraliki Call Center - Ready")
    logger.info("=" * 60)
    logger.info(f"🌐 API Docs: http://{settings.HOST}:{settings.PORT}/docs")
    logger.info(f"📚 ReDoc: http://{settings.HOST}:{settings.PORT}/redoc")
    logger.info(f"🔒 Environment: {'DEBUG' if settings.DEBUG else 'PRODUCTION'}")
    logger.info("=" * 60)

    yield

    # Shutdown
    logger.info("👋 Voice by Kraliki shutting down...")

    # Disconnect event publisher
    if settings.ENABLE_EVENTS:
        await event_publisher.disconnect()

# Create FastAPI app
app = FastAPI(
    title="Voice by Kraliki API",
    description="AI-powered call center backend with telephony integration",
    version="2.0.0",
    lifespan=lifespan,
    docs_url="/docs" if settings.DEBUG or settings.ENABLE_DOCS else None,
    redoc_url="/redoc" if settings.DEBUG or settings.ENABLE_DOCS else None
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health check endpoints
@app.get("/")
async def root():
    return {
        "name": "Voice by Kraliki API",
        "version": "2.0.0",
        "status": "running",
        "stack": "Python 3.11 + FastAPI + SQLAlchemy"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring"""
    # TODO: Add database health check
    # TODO: Add Redis health check
    # TODO: Add telephony provider health check
    return {
        "status": "healthy",
        "database": "connected",  # TODO: Real check
        "services": {
            "telephony": "ready",  # TODO: Real check
            "ai": "ready"  # TODO: Real check
        }
    }

# Register routers - ALL 21+ ROUTERS
from app.routers import (
    auth, calls, campaigns, agents, webhooks, teams, analytics, supervisor,
    contacts, sentiment, ivr, dashboard, telephony, ai, metrics,
    circuit_breaker, agent_assist, ai_health, payments, call_byok, agent_router, sms
)

app.include_router(auth.router)
app.include_router(calls.router)
app.include_router(campaigns.router)
app.include_router(agents.router)
app.include_router(webhooks.router)
app.include_router(teams.router)
app.include_router(analytics.router)
app.include_router(supervisor.router)
app.include_router(contacts.router)
app.include_router(sentiment.router)
app.include_router(ivr.router)
app.include_router(dashboard.router)
app.include_router(telephony.router)
app.include_router(ai.router)
app.include_router(metrics.router)
app.include_router(circuit_breaker.router)
app.include_router(agent_assist.router)
app.include_router(ai_health.router)
app.include_router(payments.router)
app.include_router(call_byok.router)
app.include_router(agent_router.router)
app.include_router(sms.router)

# Error handlers
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error" if not settings.DEBUG else str(exc)}
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level="debug" if settings.DEBUG else "info"
    )
