"""
Application settings management using Pydantic BaseSettings.

This module provides centralized configuration management for application,
loading settings from environment variables with sensible defaults.
"""

import logging
from functools import lru_cache
from typing import Literal

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

logger = logging.getLogger(__name__)


class Settings(BaseSettings):
    """Application settings.

    All settings can be overridden via environment variables.
    For example, APP_NAME can be set via APP_NAME environment variable.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Application metadata
    app_name: str = Field(
        default="Operator Demo Backend",
        description="Application name",
    )
    version: str = Field(
        default="0.1.0",
        description="Application version",
    )
    environment: Literal["development", "staging", "production"] = Field(
        default="development",
        description="Current environment",
    )

    # Server configuration
    host: str = Field(
        default="0.0.0.0",
        description="Server host",
    )
    port: int = Field(
        default=8000,
        description="Server port",
        ge=1,
        le=65535,
    )
    debug: bool = Field(
        default=True,
        description="Debug mode (auto-reload, verbose errors)",
    )

    public_url: str | None = Field(
        default=None,
        description="Public base URL used for webhook/stream callbacks",
    )

    # CORS configuration - accepts comma-separated string or JSON array
    cors_origins: str | list[str] = Field(
        default="http://localhost:3000,http://localhost:5173",
        description="Allowed CORS origins (comma-separated string or JSON array)",
    )

    @field_validator("cors_origins", mode="after")
    @classmethod
    def parse_cors_origins(cls, v) -> list[str]:
        """Parse cors_origins from comma-separated string or JSON array."""
        if isinstance(v, str):
            # Try JSON first
            if v.startswith("["):
                import json
                return json.loads(v)
            # Otherwise split by comma
            return [origin.strip() for origin in v.split(",") if origin.strip()]
        return v

    # Security
    # NOTE: SECRET_KEY must be set via environment variable. There is no default.
    # Generate with: python -c "import secrets; print(secrets.token_urlsafe(32))"
    secret_key: str = Field(
        default="",
        description="Secret key for JWT and other cryptographic operations. REQUIRED - must be set via environment variable.",
    )

    @field_validator("secret_key")
    @classmethod
    def validate_secret_key(cls, v: str, info) -> str:
        """Validate that secret_key is set and secure.

        In production, rejects empty, weak, or placeholder secret keys.
        In development, allows placeholder but logs a warning.
        """
        weak_patterns = [
            "insecure",
            "dev-secret",
            "changeme",
            "change-in-production",
            "placeholder",
            "example",
            "your_secret",
            "xxx",
        ]

        # Check if the key is weak or placeholder
        is_weak = not v or len(v) < 16 or any(
            pattern in v.lower() for pattern in weak_patterns
        )

        # Get environment from values - note: can't access other fields directly in validators
        # We'll check env var directly for environment
        import os
        environment = os.getenv("ENVIRONMENT", "development").lower()

        if environment == "production":
            if is_weak:
                raise ValueError(
                    "SECRET_KEY is required in production and must be a strong random value. "
                    "Generate with: python -c \"import secrets; print(secrets.token_urlsafe(32))\""
                )
        elif is_weak:
            # Development/staging - warn but allow
            logger.warning(
                "SECRET_KEY is empty or weak. This is acceptable for development but "
                "MUST be set to a strong random value in production."
            )
            # Provide a dev-only fallback so the app can start
            if not v:
                v = "dev-only-insecure-key-DO-NOT-USE-IN-PRODUCTION"
                logger.warning("Using fallback dev secret key. NOT FOR PRODUCTION USE.")

        return v

    jwt_algorithm: str = Field(
        default="EdDSA",
        description="JWT signing algorithm",
    )
    jwt_expiration_minutes: int = Field(
        default=1440,
        description="JWT access token expiration in minutes",
        ge=1,
    )
    jwt_keys_dir: str = Field(
        default="keys",
        description="Directory containing Ed25519 keypair",
    )
    auth_cookie_name: str = Field(
        default="auth_token",
        description="HTTP-only cookie name for access token",
    )
    refresh_cookie_name: str = Field(
        default="refresh_token",
        description="HTTP-only cookie name for refresh token",
    )
    auth_cookie_domain: str | None = Field(
        default=None,
        description="Cookie domain (e.g. .verduona.dev)",
    )
    auth_cookie_secure: bool = Field(
        default=False,
        description="Whether auth cookies require HTTPS",
    )
    auth_cookie_samesite: Literal["lax", "strict", "none"] = Field(
        default="lax",
        description="SameSite attribute for auth cookies",
    )

    # Database (placeholder for future use)
    database_url: str | None = Field(
        default=None,
        description="Database connection URL",
    )

    # Redis Configuration (for token revocation, caching, rate limiting)
    redis_host: str = Field(
        default="localhost",
        description="Redis server host",
    )
    redis_port: int = Field(
        default=6379,
        description="Redis server port",
        ge=1,
        le=65535,
    )
    redis_db: int = Field(
        default=0,
        description="Redis database number",
        ge=0,
        le=15,
    )
    redis_password: str | None = Field(
        default=None,
        description="Redis password (optional)",
    )

    # AI Provider API Keys
    # ===================================================
    # CRITICAL CONFIGURATION: API keys for AI providers
    #
    # Without these keys, AI features will not function.
    # See .env.example for detailed instructions on obtaining keys.
    #
    # Required for core functionality:
    #   - OPENAI_API_KEY: Required for OpenAI Realtime API and GPT models
    #   - GEMINI_API_KEY: Required for Gemini 2.5 Native Audio
    #   - DEEPGRAM_API_KEY: Required for Speech-to-Text and Text-to-Speech
    #
    # Security Notes:
    #   - NEVER commit actual API keys to version control
    #   - Use environment variables or secret management systems
    #   - Rotate keys regularly in production environments
    openai_api_key: str | None = Field(
        default=None,
        description="OpenAI API key for Realtime API (get from: https://platform.openai.com/api-keys)",
    )
    gemini_api_key: str | None = Field(
        default=None,
        description="Google Gemini API key (get from: https://aistudio.google.com/app/apikey)",
    )
    deepgram_api_key: str | None = Field(
        default=None,
        description="Deepgram API key for STT/TTS (get from: https://console.deepgram.com/project/*/keys)",
    )

    # Telephony Provider Credentials
    twilio_account_sid: str | None = Field(
        default=None,
        description="Twilio account SID",
    )
    twilio_auth_token: str | None = Field(
        default=None,
        description="Twilio authentication token",
    )
    twilio_phone_number_us: str | None = Field(
        default=None,
        description="Primary Twilio phone number (US)",
    )
    twilio_phone_number_cz: str | None = Field(
        default=None,
        description="Secondary Twilio phone number (CZ)",
    )
    telnyx_api_key: str | None = Field(
        default=None,
        description="Telnyx API key",
    )
    telnyx_public_key: str | None = Field(
        default=None,
        description="Telnyx Ed25519 public key for webhook validation",
    )
    telnyx_phone_number: str | None = Field(
        default=None,
        description="Telnyx phone number for outbound calls",
    )

    # Webhook Security Settings
    enable_webhook_ip_whitelist: bool = Field(
        default=True,
        description="Enable IP whitelisting for webhooks (set to False for development)",
    )

    # AWS S3 Configuration
    aws_access_key_id: str | None = Field(
        default=None,
        description="AWS access key ID for S3",
    )
    aws_secret_access_key: str | None = Field(
        default=None,
        description="AWS secret access key for S3",
    )
    aws_region: str = Field(
        default="us-east-1",
        description="AWS region for S3",
    )
    s3_bucket_name: str | None = Field(
        default=None,
        description="S3 bucket name for recordings",
    )

    # Azure Storage Configuration
    azure_storage_account_name: str | None = Field(
        default=None,
        description="Azure Storage account name",
    )
    azure_storage_account_key: str | None = Field(
        default=None,
        description="Azure Storage account key",
    )
    azure_storage_connection_string: str | None = Field(
        default=None,
        description="Azure Storage connection string (alternative to account name/key)",
    )
    azure_blob_container_name: str | None = Field(
        default=None,
        description="Azure Blob container name for recordings",
    )
    twilio_webhook_ips: list[str] = Field(
        default_factory=lambda: [
            # Twilio IP CIDR blocks from https://www.twilio.com/docs/usage/webhooks/ip-addresses
            "54.172.60.0/23",  # US East (Virginia)
            "54.244.51.0/24",  # US West (Oregon)
            "54.171.127.192/26",  # US West (N. California)
            "35.156.191.128/26",  # EU (Frankfurt)
            "54.65.63.192/26",  # Asia Pacific (Tokyo)
            "54.169.127.128/26",  # Asia Pacific (Singapore)
            "54.252.254.64/26",  # Asia Pacific (Sydney)
            "177.71.206.192/26",  # South America (São Paulo)
        ],
        description="Allowed IP addresses/CIDR blocks for Twilio webhooks",
    )
    telnyx_webhook_ips: list[str] = Field(
        default_factory=lambda: [
            # Telnyx IP addresses (using CIDR notation)
            "185.125.138.0/24",
            "185.125.139.0/24",
        ],
        description="Allowed IP addresses/CIDR blocks for Telnyx webhooks",
    )

    # Logging
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = Field(
        default="INFO",
        description="Logging level",
    )

    # API Key Validation Methods
    # ===================================================

    def validate_api_keys(self) -> dict[str, bool]:
        """Validate that required API keys are configured.

        Returns:
            dict: Dictionary mapping provider names to their configuration status

        Example:
            >>> settings = get_settings()
            >>> status = settings.validate_api_keys()
            >>> if not status['openai']:
            ...     logger.warning("OpenAI API key is not configured")
        """
        return {
            "openai": self._is_key_valid(self.openai_api_key),
            "gemini": self._is_key_valid(self.gemini_api_key),
            "deepgram": self._is_key_valid(self.deepgram_api_key),
        }

    def _is_key_valid(self, key: str | None) -> bool:
        """Check if an API key is valid (not None, not empty, not placeholder).

        Args:
            key: The API key to validate

        Returns:
            bool: True if key appears to be valid
        """
        if not key:
            return False

        # Check for placeholder values
        placeholder_patterns = [
            "your_",
            "xxx",
            "example",
            "placeholder",
            "changeme",
            "replace",
        ]

        key_lower = key.lower()
        return not any(pattern in key_lower for pattern in placeholder_patterns)

    def get_missing_api_keys(self) -> list[str]:
        """Get list of missing or invalid API keys.

        Returns:
            list: List of provider names with missing API keys

        Example:
            >>> settings = get_settings()
            >>> missing = settings.get_missing_api_keys()
            >>> if missing:
            ...     logger.warning(f"Missing API keys: {', '.join(missing)}")
        """
        validation = self.validate_api_keys()
        return [provider for provider, is_valid in validation.items() if not is_valid]

    def get_api_key_status_message(self) -> str:
        """Get a formatted status message about API key configuration.

        Returns:
            str: Human-readable status message

        Example:
            >>> settings = get_settings()
            >>> logger.info(settings.get_api_key_status_message())
        """
        validation = self.validate_api_keys()
        missing = self.get_missing_api_keys()

        if not missing:
            return "All AI provider API keys are configured."

        lines = [
            "WARNING: Some AI provider API keys are not configured:",
            "",
        ]

        for provider, is_valid in validation.items():
            status = "OK" if is_valid else "MISSING"
            emoji = "✓" if is_valid else "✗"
            lines.append(f"  {emoji} {provider.upper()}: {status}")

        if missing:
            lines.extend(
                [
                    "",
                    "To configure missing API keys:",
                    "1. Copy backend/.env.example to backend/.env",
                    "2. Add your API keys to .env file",
                    "3. See .env.example for links to obtain API keys",
                    "",
                    f"Missing providers: {', '.join(missing)}",
                ]
            )

        return "\n".join(lines)


@lru_cache
def get_settings() -> Settings:
    """Get cached application settings.

    Uses LRU cache to ensure settings are loaded only once.

    Returns:
        Settings: Application settings instance
    """
    return Settings()
