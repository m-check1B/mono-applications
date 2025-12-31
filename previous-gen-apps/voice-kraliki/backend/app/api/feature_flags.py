"""API endpoints for feature flags management."""


from fastapi import APIRouter, HTTPException, Request, status
from pydantic import BaseModel

from app.config.feature_flags import (
    DEMO_CONFIGS,
    get_demo_config,
    get_feature_flags,
    is_feature_enabled,
)
from app.middleware.rate_limit import API_RATE_LIMIT, WRITE_OPERATION_RATE_LIMIT, limiter

router = APIRouter(prefix="/api/feature-flags", tags=["feature-flags"])


class FeatureFlagStatus(BaseModel):
    """Feature flag status response."""

    name: str
    enabled: bool
    description: str


class FeatureFlagsResponse(BaseModel):
    """Feature flags list response."""

    flags: list[FeatureFlagStatus]
    total: int
    enabled: int
    disabled: int


class DemoConfigResponse(BaseModel):
    """Demo configuration response."""

    name: str
    description: str
    features: dict[str, bool]
    providers: list[str]
    scenarios: list[str]


@router.get("/", response_model=FeatureFlagsResponse)
@limiter.limit(API_RATE_LIMIT)
async def get_all_feature_flags(request: Request):
    """Get all feature flags and their status."""
    flags = get_feature_flags()

    flag_statuses = []
    enabled_count = 0

    # Get all field names and descriptions
    field_descriptions = {
        "enable_openai_realtime": "Enable OpenAI Realtime API integration",
        "enable_gemini_native_audio": "Enable Gemini 2.5 Native Audio",
        "enable_deepgram_nova3": "Enable Deepgram Nova 3 agentic SDK",
        "enable_twilio_media_stream": "Enable Twilio MediaStream support",
        "enable_telnyx_call_control": "Enable Telnyx Call Control",
        "enable_webhook_validation": "Enable webhook signature validation",
        "enable_persistent_sessions": "Enable Redis/Postgres session persistence",
        "enable_session_recovery": "Enable graceful session recovery",
        "enable_session_analytics": "Enable session analytics and metrics",
        "enable_function_calling": "Enable AI function calling and workflows",
        "enable_auto_execution": "Enable automatic workflow execution",
        "enable_sentiment_analysis": "Enable real-time sentiment analysis",
        "enable_intent_detection": "Enable real-time intent detection",
        "enable_provider_switching": "Enable mid-call provider switching",
        "enable_realtime_transcripts": "Enable real-time transcription display",
        "enable_suggestion_panels": "Enable AI suggestion panels",
        "enable_browser_chat": "Enable browser-based chat channel",
        "enable_cobrowse": "Enable co-browsing functionality",
        "enable_consent_capture": "Enable consent capture for recordings",
        "enable_retention_controls": "Enable data retention controls",
        "enable_audit_logging": "Enable comprehensive audit logging",
        "enable_metrics_collection": "Enable Prometheus metrics collection",
        "enable_distributed_tracing": "Enable distributed tracing",
        "enable_health_probes": "Enable provider health probes",
        "demo_mode": "Enable demo-specific configurations",
        "mock_providers": "Use mock providers for testing",
        "stress_test_mode": "Enable stress testing configurations",
    }

    for field_name, value in flags.model_dump().items():
        if isinstance(value, bool):
            is_enabled = value
            if is_enabled:
                enabled_count += 1

            flag_statuses.append(
                FeatureFlagStatus(
                    name=field_name,
                    enabled=is_enabled,
                    description=field_descriptions.get(field_name, "No description available"),
                )
            )

    return FeatureFlagsResponse(
        flags=flag_statuses,
        total=len(flag_statuses),
        enabled=enabled_count,
        disabled=len(flag_statuses) - enabled_count,
    )


# Demo config routes must be defined BEFORE /{flag_name} to avoid route conflicts
@router.get("/demo-configs/", response_model=list[DemoConfigResponse])
@limiter.limit(API_RATE_LIMIT)
async def list_demo_configs(request: Request):
    """Get all available demo configurations."""
    demo_configs = []

    for demo_name, config in DEMO_CONFIGS.items():
        demo_configs.append(
            DemoConfigResponse(
                name=demo_name,
                description=config["description"],
                features=config["features"],
                providers=config["providers"],
                scenarios=config["scenarios"],
            )
        )

    return demo_configs


@router.get("/demo-configs/{demo_type}", response_model=DemoConfigResponse)
@limiter.limit(API_RATE_LIMIT)
async def get_specific_demo_config(request: Request, demo_type: str):
    """Get specific demo configuration."""
    try:
        config = get_demo_config(demo_type)
        return DemoConfigResponse(
            name=demo_type,
            description=config["description"],
            features=config["features"],
            providers=config["providers"],
            scenarios=config["scenarios"],
        )
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Demo configuration '{demo_type}' not found",
        )


@router.post("/demo-configs/{demo_type}/activate")
@limiter.limit(WRITE_OPERATION_RATE_LIMIT)
async def activate_specific_demo_config(request: Request, demo_type: str):
    """Activate a specific demo configuration.

    Note: This is a placeholder implementation. In a real system,
    this would update the feature flags in a persistent store.
    """
    try:
        config = get_demo_config(demo_type)

        # In a real implementation, this would:
        # 1. Update the feature flags in a database
        # 2. Notify other services of the change
        # 3. Possibly restart services or trigger reconfiguration

        return {
            "message": f"Demo configuration '{demo_type}' activated successfully",
            "demo_type": demo_type,
            "features_activated": len(config["features"]),
            "providers_enabled": config["providers"],
        }
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Demo configuration '{demo_type}' not found",
        )


# Dynamic route must come AFTER all specific routes
@router.get("/{flag_name}")
@limiter.limit(API_RATE_LIMIT)
async def get_feature_flag_status(request: Request, flag_name: str):
    """Get status of a specific feature flag."""
    try:
        enabled = is_feature_enabled(flag_name)
        return {
            "name": flag_name,
            "enabled": enabled,
            "message": f"Feature flag '{flag_name}' is {'enabled' if enabled else 'disabled'}",
        }
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Feature flag '{flag_name}' not found"
        )
