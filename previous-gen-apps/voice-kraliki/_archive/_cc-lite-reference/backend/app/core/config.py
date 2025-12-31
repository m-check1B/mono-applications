"""
Centralized configuration for Voice by Kraliki
Based on Stack 2026 standards with Pydantic Settings
"""

import os
from pathlib import Path
from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, validator


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra='allow'  # Allow extra fields from .env
    )
    """Application settings with environment variable support"""

    # Application
    APP_NAME: str = "Voice by Kraliki"
    VERSION: str = "2.0.0"
    DEBUG: bool = Field(default=False, env="CC_LITE_DEBUG")
    SECRET_KEY: str = Field(default="change-me-in-production", env="CC_LITE_SECRET_KEY")

    # Server
    HOST: str = Field(default="127.0.0.1", env="CC_LITE_HOST")
    PORT: int = Field(default=3018, env="CC_LITE_PORT")  # Stack 2026 - Communications Module port
    ENABLE_DOCS: bool = Field(default=True, env="CC_LITE_ENABLE_DOCS")

    # Database
    DATABASE_URL: str = Field(
        default="postgresql+asyncpg://cc_lite:cc_lite_dev@localhost:5432/cc_lite",
        env="DATABASE_URL"
    )

    # CORS
    FRONTEND_URL: str = Field(default="http://127.0.0.1:5173", env="FRONTEND_URL")
    CORS_ORIGINS: List[str] = [
        "http://127.0.0.1:5173",
        "http://localhost:5173",
        "http://127.0.0.1:5174",
        "http://localhost:5174"
    ]

    # Redis (optional)
    REDIS_URL: str | None = Field(default=None, env="REDIS_URL")
    REDIS_HOST: str = Field(default="127.0.0.1", env="REDIS_HOST")
    REDIS_PORT: int = Field(default=6379, env="REDIS_PORT")

    # RabbitMQ Event Bus
    RABBITMQ_URL: str = Field(
        default="amqp://guest:guest@localhost:5672/",
        env="RABBITMQ_URL"
    )
    ENABLE_EVENTS: bool = Field(default=True, env="ENABLE_EVENTS")
    USE_SHARED_AUTH: bool = Field(default=False, env="USE_SHARED_AUTH")
    USE_INMEMORY_EVENTS: bool = Field(default=True, env="USE_INMEMORY_EVENTS")

    # Authentication
    JWT_SECRET: str | None = Field(default=None, env="JWT_SECRET")
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # Use JWT_SECRET if available, else fall back to SECRET_KEY
    @property
    def jwt_secret(self) -> str:
        return self.JWT_SECRET or self.SECRET_KEY

    # Telephony - Twilio
    TWILIO_ACCOUNT_SID: str | None = Field(default=None, env="TWILIO_ACCOUNT_SID")
    TWILIO_AUTH_TOKEN: str | None = Field(default=None, env="TWILIO_AUTH_TOKEN")
    TWILIO_PHONE_NUMBER: str | None = Field(default=None, env="TWILIO_PHONE_NUMBER")
    TELEPHONY_ENABLED: bool = Field(default=False, env="TELEPHONY_ENABLED")

    # AI Services
    OPENAI_API_KEY: str | None = Field(default=None, env="OPENAI_API_KEY")
    ANTHROPIC_API_KEY: str | None = Field(default=None, env="ANTHROPIC_API_KEY")
    GEMINI_API_KEY: str | None = Field(default=None, env="GEMINI_API_KEY")
    ELEVENLABS_API_KEY: str | None = Field(default=None, env="ELEVENLABS_API_KEY")
    DEEPGRAM_API_KEY: str | None = Field(default=None, env="DEEPGRAM_API_KEY")

    # Monitoring
    SENTRY_DSN: str | None = Field(default=None, env="SENTRY_DSN")
    LOG_LEVEL: str = Field(default="INFO", env="LOG_LEVEL")

    # Payments
    POLAR_ACCESS_TOKEN: str | None = Field(default=None, env="POLAR_ACCESS_TOKEN")
    POLAR_WEBHOOK_SECRET: str | None = Field(default=None, env="POLAR_WEBHOOK_SECRET")

    # BYOK (Bring Your Own Keys)
    BYOK_ENABLED: bool = Field(default=False, env="BYOK_ENABLED")
    BYOK_ENCRYPTION_KEY: str | None = Field(default=None, env="BYOK_ENCRYPTION_KEY")

    def is_production(self) -> bool:
        """Check if running in production"""
        return not self.DEBUG

    def has_telephony(self) -> bool:
        """Check if telephony is properly configured"""
        return (
            self.TELEPHONY_ENABLED
            and self.TWILIO_ACCOUNT_SID is not None
            and self.TWILIO_AUTH_TOKEN is not None
            and self.TWILIO_PHONE_NUMBER is not None
        )

    def has_ai_providers(self) -> dict:
        """Check which AI providers are configured"""
        return {
            "openai": self.OPENAI_API_KEY is not None,
            "anthropic": self.ANTHROPIC_API_KEY is not None,
            "gemini": self.GEMINI_API_KEY is not None,
            "elevenlabs": self.ELEVENLABS_API_KEY is not None,
            "deepgram": self.DEEPGRAM_API_KEY is not None,
        }


# Global settings instance
settings = Settings()

# Print config on import if debug
if settings.DEBUG:
    print(f"Voice by Kraliki Config loaded:")
    print(f"  - Database: {settings.DATABASE_URL.split('@')[-1]}")  # Hide credentials
    print(f"  - Host: {settings.HOST}:{settings.PORT}")
    print(f"  - Telephony: {settings.has_telephony()}")
    print(f"  - AI Providers: {list(k for k, v in settings.has_ai_providers().items() if v)}")
