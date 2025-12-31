from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List, Optional
import logging
import sys

logger = logging.getLogger(__name__)


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True,
        extra="ignore",
    )

    # Database
    DATABASE_URL: str = "sqlite:///./focus_kraliki.db"

    # AI Services (Optional for initial setup)
    # Primary: Gemini (cost-effective), Secondary: Claude (quality), Tertiary: GLM/OpenRouter (user choice)
    ANTHROPIC_API_KEY: Optional[str] = None
    GEMINI_API_KEY: Optional[str] = None
    GLM_API_KEY: Optional[str] = None  # GLM-4/ChatGLM (cost-effective agent work)
    OPENROUTER_API_KEY: Optional[str] = None  # For user's model choice
    OPENAI_API_KEY: Optional[str] = None  # Legacy/optional

    # Brain AI Models - ALL VIA OPENROUTER (cheap defaults, user adds expensive)
    # Presets: Z.AI GLM-4.7 (primary), Gemini 3.0 Flash (fallback)
    # User can override with their preferred models
    BRAIN_MODEL: str = "zhipu/glm-4-plus"  # Z.AI GLM 4.7 - cost effective
    BRAIN_MODEL_PROVIDER: str = "openrouter"  # Always OpenRouter
    BRAIN_FALLBACK_MODEL: str = (
        "google/gemini-2.0-flash-001"  # Gemini Flash - cheap fallback
    )
    BRAIN_FALLBACK_PROVIDER: str = "openrouter"

    # Voice Models (via OpenRouter for consistency)
    VOICE_TRANSCRIPTION_MODEL: str = "google/gemini-2.0-flash-001"  # Cheap, fast
    VOICE_TRANSCRIPTION_PROVIDER: str = "openrouter"

    # Legacy direct API (only if user explicitly configures)
    GEMINI_AUDIO_MODEL: str = "gemini-2.5-flash-preview-native-audio-dialog"

    # Legacy (kept for compatibility, prefer settings above)
    OPENAI_REALTIME_API_KEY: Optional[str] = None
    OPENAI_REALTIME_MODEL: str = "gpt-4o-realtime-preview-2024-12-17"
    OPENAI_TTS_MODEL: str = "gpt-4o-mini-tts"
    DEEPGRAM_API_KEY: str = ""
    DEEPGRAM_MODEL: str = "nova-2-general"

    # Prompts file (external, not hardcoded)
    BRAIN_PROMPTS_FILE: str = "config/brain_prompts.json"

    # Auth (Stack 2026: Ed25519 JWT)
    JWT_SECRET: str = "replit-default-secret-change-in-production-min-32-chars"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15  # Ed25519 access token (short-lived)
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7  # Ed25519 refresh token (long-lived)
    AGENT_TOKEN_EXPIRE_MINUTES: int = 120  # Agent tokens (2 hours)

    # Redis (Token revocation, caching)
    REDIS_URL: str = "redis://localhost:6379/0"

    # RabbitMQ (Event publishing)
    RABBITMQ_URL: str = "amqp://localhost:5672"
    USE_INMEMORY_EVENTS: bool = False
    USE_SHARED_AUTH: bool = False

    # Platform Mode (when running behind API Gateway)
    PLATFORM_MODE: bool = False
    ENABLE_CALENDAR_INTEGRATION: bool = False

    # Telephony
    TWILIO_ACCOUNT_SID: Optional[str] = None
    TWILIO_AUTH_TOKEN: Optional[str] = None
    TELNYX_API_KEY: Optional[str] = None

    # Google OAuth
    GOOGLE_OAUTH_CLIENT_ID: Optional[str] = None
    GOOGLE_OAUTH_CLIENT_SECRET: Optional[str] = None
    GOOGLE_OAUTH_REDIRECT_URI: str = (
        "http://localhost:5173/auth/google/callback"  # Default dev URL
    )
    GOOGLE_CALENDAR_WEBHOOK_TOKEN: Optional[str] = (
        None  # Optional verification token for calendar webhooks
    )

    # II-Agent Webhook Security
    II_AGENT_WEBHOOK_SECRET: Optional[str] = None  # HMAC secret for II-Agent webhooks

    # Linear Webhook Security
    LINEAR_WEBHOOK_SECRET: Optional[str] = None  # HMAC secret for Linear webhooks

    # Stripe Billing
    STRIPE_SECRET_KEY: Optional[str] = None
    STRIPE_WEBHOOK_SECRET: Optional[str] = None
    STRIPE_PRICE_ID_PREMIUM: str = (
        "price_premium_monthly"  # Update with actual price ID
    )

    # n8n Orchestration
    N8N_URL: Optional[str] = None
    N8N_API_KEY: Optional[str] = None

    # Server
    HOST: str = "127.0.0.1"
    PORT: int = 3017
    ENVIRONMENT: str = "development"
    DEBUG: bool = False

    # CORS
    ALLOWED_ORIGINS: str = "http://127.0.0.1:5175,http://localhost:5175,http://0.0.0.0:5000,http://localhost:5000"

    @property
    def origins_list(self) -> List[str]:
        return [origin.strip() for origin in self.ALLOWED_ORIGINS.split(",")]


settings = Settings()

# Security validation for production
if settings.ENVIRONMENT.lower() == "production":
    # Validate DEBUG is not enabled
    if settings.DEBUG:
        logger.critical(
            "CRITICAL SECURITY ERROR: DEBUG mode is enabled in production! "
            "This exposes detailed error information and system internals. Set DEBUG=false in your .env file."
        )
        sys.exit(1)

    # Validate JWT_SECRET is not the default
    default_secret = "replit-default-secret-change-in-production-min-32-chars"
    if settings.JWT_SECRET == default_secret:
        logger.critical(
            "CRITICAL SECURITY ERROR: Using default JWT_SECRET in production! "
            "This is a severe security vulnerability. Set a strong, random JWT_SECRET in your .env file."
        )
        sys.exit(1)

    # Validate JWT_SECRET is strong enough
    if len(settings.JWT_SECRET) < 32:
        logger.critical(
            f"CRITICAL SECURITY ERROR: JWT_SECRET is too short ({len(settings.JWT_SECRET)} chars). "
            "Must be at least 32 characters for production use."
        )
        sys.exit(1)

    logger.info("Security validation passed for production environment")
