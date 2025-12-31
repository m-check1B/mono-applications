"""
Speak by Kraliki - Configuration
Stack 2026 Standard: Ed25519 JWT + PostgreSQL
"""

from functools import lru_cache
from pydantic import ConfigDict
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment."""

    model_config = ConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",  # Ignore Docker env vars (POSTGRES_USER, etc.) during tests
    )

    # App
    app_name: str = "Speak by Kraliki"
    app_version: str = "1.0.0"
    debug: bool = False

    # Server - MUST use 127.0.0.1 (internet-connected dev server!)
    host: str = "127.0.0.1"
    port: int = 8000

    # Database
    database_url: str = ""
    database_echo: bool = False

    # Auth (Ed25519 JWT - Stack 2026 standard)
    jwt_secret_key: str | None = None
    jwt_algorithm: str = "HS256"  # Use EdDSA for Ed25519 in production
    access_token_expire_minutes: int = 15
    refresh_token_expire_days: int = 7

    # Ed25519 keys (Stack 2026 - production)
    # Generate with: python -c "from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey; from cryptography.hazmat.primitives import serialization; key = Ed25519PrivateKey.generate(); print(key.private_bytes(serialization.Encoding.PEM, serialization.PrivateFormat.PKCS8, serialization.NoEncryption()).decode())"
    ed25519_private_key: str | None = None  # PEM format
    ed25519_public_key: str | None = (
        None  # PEM format (can be shared with microservices)
    )
    use_ed25519: bool = False  # Enable for production

    # AI - Gemini Live 2.5 Flash Native Audio (December 2025 GA)
    gemini_api_key: str = ""
    gemini_model: str = "models/gemini-2.5-flash-native-audio-preview-12-2025"

    # Telephony (Telnyx - voice-core)
    telnyx_api_key: str = ""
    telnyx_public_key: str = ""  # Ed25519 public key for webhook validation
    telnyx_connection_id: str = ""  # Telnyx TeXML app connection ID
    telnyx_phone_number: str = ""  # Outbound caller ID (E.164 format)

    # Reach Voice API (Voice by Kraliki)
    reach_voice_api_url: str = ""  # Base URL, e.g. https://voice.verduona.dev
    reach_voice_provider_type: str = "gemini"
    reach_voice_strategy: str = "realtime"

    # API base URL for webhooks
    api_base_url: str = "http://localhost:8000"

    # Frontend base URL for magic links
    frontend_base_url: str = "https://speak.verduona.dev"

    # Email
    resend_api_key: str = ""
    email_from: str = "noreply@kraliki.com"

    # Stripe
    stripe_secret_key: str = ""
    stripe_webhook_secret: str = ""

    # Stripe Price IDs (from HW-025)
    stripe_price_personal: str = "price_placeholder_personal"
    stripe_price_premium: str = "price_placeholder_premium"
    stripe_price_pro: str = "price_placeholder_pro"

    # CORS
    cors_origins: list[str] = [
        "http://localhost:5173",
        "http://localhost:3000",
        "https://speak.verduona.dev",
        "https://speak.kraliki.com",
    ]

    def validate_secrets(self) -> list[str]:
        """Validate that all required secrets are configured.

        This is called by validate_production_security() in auth.py.
        Separating validation logic from Settings class allows for better error handling.
        """
        errors = []

        # Check required secrets in production mode
        if not self.debug:
            if not self.database_url:
                errors.append("DATABASE_URL is required in production")
            elif (
                "postgres:postgres@" in self.database_url
                or "admin:admin@" in self.database_url
                or "root:root@" in self.database_url
                or "replace_me" in self.database_url
            ):
                errors.append(
                    "DATABASE_URL contains default credentials or placeholders - configure secure production database"
                )

            if not self.jwt_secret_key and not self.ed25519_private_key:
                errors.append(
                    "Either JWT_SECRET_KEY or ED25519_PRIVATE_KEY is required in production"
                )

            if self.use_ed25519:
                if not self.ed25519_private_key:
                    errors.append("ED25519_PRIVATE_KEY required when USE_ED25519=True")
                if not self.ed25519_public_key:
                    errors.append("ED25519_PUBLIC_KEY required when USE_ED25519=True")

        return errors


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()


settings = get_settings()
