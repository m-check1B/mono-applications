"""Feature flags configuration for the Operator Demo application.

This module provides centralized feature flag management to allow
gradual rollout of risky features and demo-specific configurations.
"""

import os
from functools import lru_cache
from typing import Any

from pydantic import BaseModel, Field


class FeatureFlags(BaseModel):
    """Feature flags configuration."""

    # AI Provider Features
    enable_openai_realtime: bool = Field(default=True, description="Enable OpenAI Realtime API integration")
    enable_gemini_native_audio: bool = Field(default=True, description="Enable Gemini 2.5 Native Audio")
    enable_deepgram_nova3: bool = Field(default=False, description="Enable Deepgram Nova 3 agentic SDK")

    # Telephony Features
    enable_twilio_media_stream: bool = Field(default=True, description="Enable Twilio MediaStream support")
    enable_telnyx_call_control: bool = Field(default=True, description="Enable Telnyx Call Control")
    enable_webhook_validation: bool = Field(default=True, description="Enable webhook signature validation")

    # Session Management
    enable_persistent_sessions: bool = Field(default=True, description="Enable Redis/Postgres session persistence")
    enable_session_recovery: bool = Field(default=True, description="Enable graceful session recovery")
    enable_session_analytics: bool = Field(default=True, description="Enable session analytics and metrics")

    # AI Automation Features
    # CRITICAL FEATURES: These enable advanced AI capabilities for automation and analysis
    enable_function_calling: bool = Field(default=True, description="Enable AI function calling and workflows - allows AI to execute predefined functions")
    enable_auto_execution: bool = Field(default=False, description="Enable automatic workflow execution")
    enable_sentiment_analysis: bool = Field(default=True, description="Enable real-time sentiment analysis - analyzes customer emotion during calls")
    enable_intent_detection: bool = Field(default=True, description="Enable real-time intent detection - identifies customer intent from conversation")

    # UI Features
    enable_provider_switching: bool = Field(default=True, description="Enable mid-call provider switching")
    enable_realtime_transcripts: bool = Field(default=True, description="Enable real-time transcription display")
    enable_suggestion_panels: bool = Field(default=True, description="Enable AI suggestion panels - displays real-time AI suggestions to agents")

    # Browser Channel
    enable_browser_chat: bool = Field(default=False, description="Enable browser-based chat channel")
    enable_cobrowse: bool = Field(default=False, description="Enable co-browsing functionality")

    # Compliance and Security
    enable_consent_capture: bool = Field(default=False, description="Enable consent capture for recordings")
    enable_retention_controls: bool = Field(default=False, description="Enable data retention controls")
    enable_audit_logging: bool = Field(default=True, description="Enable comprehensive audit logging")

    # Monitoring and Observability
    enable_metrics_collection: bool = Field(default=True, description="Enable Prometheus metrics collection")  # Prometheus metrics for production monitoring
    enable_distributed_tracing: bool = Field(default=False, description="Enable distributed tracing")
    enable_health_probes: bool = Field(default=False, description="Enable provider health probes")

    # Demo Specific
    demo_mode: bool = Field(default=False, description="Enable demo-specific configurations")
    mock_providers: bool = Field(default=False, description="Use mock providers for testing")
    stress_test_mode: bool = Field(default=False, description="Enable stress testing configurations")


@lru_cache
def get_feature_flags() -> FeatureFlags:
    """Get feature flags configuration from environment variables.
    
    Returns:
        FeatureFlags: Configured feature flags
    """
    # Map environment variables to feature flags
    env_mapping: dict[str, str] = {
        # AI Providers
        'ENABLE_OPENAI_REALTIME': 'enable_openai_realtime',
        'ENABLE_GEMINI_NATIVE_AUDIO': 'enable_gemini_native_audio',
        'ENABLE_DEEPGRAM_NOVA3': 'enable_deepgram_nova3',

        # Telephony
        'ENABLE_TWILIO_MEDIA_STREAM': 'enable_twilio_media_stream',
        'ENABLE_TELNYX_CALL_CONTROL': 'enable_telnyx_call_control',
        'ENABLE_WEBHOOK_VALIDATION': 'enable_webhook_validation',

        # Session Management
        'ENABLE_PERSISTENT_SESSIONS': 'enable_persistent_sessions',
        'ENABLE_SESSION_RECOVERY': 'enable_session_recovery',
        'ENABLE_SESSION_ANALYTICS': 'enable_session_analytics',

        # AI Automation
        'ENABLE_FUNCTION_CALLING': 'enable_function_calling',
        'ENABLE_AUTO_EXECUTION': 'enable_auto_execution',
        'ENABLE_SENTIMENT_ANALYSIS': 'enable_sentiment_analysis',
        'ENABLE_INTENT_DETECTION': 'enable_intent_detection',

        # UI Features
        'ENABLE_PROVIDER_SWITCHING': 'enable_provider_switching',
        'ENABLE_REALTIME_TRANSCRIPTS': 'enable_realtime_transcripts',
        'ENABLE_SUGGESTION_PANELS': 'enable_suggestion_panels',

        # Browser Channel
        'ENABLE_BROWSER_CHAT': 'enable_browser_chat',
        'ENABLE_COBROWSE': 'enable_cobrowse',

        # Compliance
        'ENABLE_CONSENT_CAPTURE': 'enable_consent_capture',
        'ENABLE_RETENTION_CONTROLS': 'enable_retention_controls',
        'ENABLE_AUDIT_LOGGING': 'enable_audit_logging',

        # Monitoring
        'ENABLE_METRICS_COLLECTION': 'enable_metrics_collection',
        'ENABLE_DISTRIBUTED_TRACING': 'enable_distributed_tracing',
        'ENABLE_HEALTH_PROBES': 'enable_health_probes',

        # Demo
        'DEMO_MODE': 'demo_mode',
        'MOCK_PROVIDERS': 'mock_providers',
        'STRESS_TEST_MODE': 'stress_test_mode',
    }

    # Build config from environment
    config: dict[str, Any] = {}
    for env_var, flag_name in env_mapping.items():
        env_value = os.getenv(env_var, '').lower()
        if env_value in ('true', '1', 'yes', 'on'):
            config[flag_name] = True
        elif env_value in ('false', '0', 'no', 'off'):
            config[flag_name] = False

    return FeatureFlags(**config)


def is_feature_enabled(flag_name: str) -> bool:
    """Check if a specific feature flag is enabled.

    Args:
        flag_name: Name of the feature flag

    Returns:
        bool: True if feature is enabled

    Raises:
        AttributeError: If the flag name is not a valid feature flag
    """
    flags = get_feature_flags()
    if not hasattr(flags, flag_name):
        raise AttributeError(f"Feature flag '{flag_name}' not found")
    return getattr(flags, flag_name)


# Demo-specific configurations
DEMO_CONFIGS = {
    'basic_demo': {
        'description': 'Basic AI operator demo with single provider',
        'features': {
            'enable_openai_realtime': True,
            'enable_realtime_transcripts': True,
            'demo_mode': True,
        },
        'providers': ['openai'],
        'scenarios': ['inbound_call', 'outbound_call'],
    },
    'multi_provider_demo': {
        'description': 'Advanced demo with provider switching',
        'features': {
            'enable_openai_realtime': True,
            'enable_gemini_native_audio': True,
            'enable_provider_switching': True,
            'enable_realtime_transcripts': True,
            'demo_mode': True,
        },
        'providers': ['openai', 'gemini'],
        'scenarios': ['provider_switch', 'failover'],
    },
    'ai_first_demo': {
        'description': 'Full AI-first experience with automation',
        'features': {
            'enable_openai_realtime': True,
            'enable_gemini_native_audio': True,
            'enable_deepgram_nova3': True,
            'enable_function_calling': True,
            'enable_auto_execution': True,
            'enable_sentiment_analysis': True,
            'enable_intent_detection': True,
            'enable_suggestion_panels': True,
            'enable_realtime_transcripts': True,
            'demo_mode': True,
        },
        'providers': ['openai', 'gemini', 'deepgram'],
        'scenarios': ['ai_automation', 'sentiment_analysis', 'intent_detection'],
    },
    'compliance_demo': {
        'description': 'Demo with compliance and consent features',
        'features': {
            'enable_consent_capture': True,
            'enable_retention_controls': True,
            'enable_audit_logging': True,
            'demo_mode': True,
        },
        'providers': ['openai'],
        'scenarios': ['consent_capture', 'data_retention'],
    },
}


def get_demo_config(demo_type: str) -> dict[str, Any]:
    """Get demo-specific configuration.

    Args:
        demo_type: Type of demo configuration

    Returns:
        Dict: Demo configuration

    Raises:
        KeyError: If the demo type is not found
    """
    if demo_type not in DEMO_CONFIGS:
        raise KeyError(f"Demo configuration '{demo_type}' not found")
    return DEMO_CONFIGS[demo_type]
