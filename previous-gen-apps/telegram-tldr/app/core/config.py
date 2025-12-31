from functools import lru_cache

from pydantic import ConfigDict, model_validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    model_config = ConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
    )
    # Telegram
    telegram_bot_token: str = ""
    telegram_webhook_url: str = ""  # e.g., https://yourdomain.com/webhook
    telegram_webhook_secret: str = ""  # Secret token for webhook validation

    @model_validator(mode="after")
    def validate_webhook_config(self) -> "Settings":
        """Ensure webhook secret is set when webhook URL is configured.

        Security: Fail fast at startup rather than at runtime to prevent
        misconfigured deployments from accepting webhook requests without
        proper authentication.
        """
        if self.telegram_webhook_url and not self.telegram_webhook_secret.strip():
            raise ValueError(
                "TELEGRAM_WEBHOOK_SECRET is required when TELEGRAM_WEBHOOK_URL is set. "
                "Generate a secure random string (e.g., openssl rand -hex 32) and set it in .env"
            )
        return self

    # Gemini (Google AI)
    gemini_api_key: str = ""
    gemini_model: str = "gemini-2.0-flash"  # Latest stable Flash model

    # Redis
    redis_url: str = "redis://localhost:6379/0"

    # App
    app_name: str = "TL;DR Bot"
    debug: bool = False

    # Monetization
    free_summaries: int = 3  # Free tier limit
    subscription_price_stars: int = 250  # ~$4.99
    newsletter_price_stars: int = 250  # Newsletter subscription price
    telegram_stars_provider_token: str = (
        ""  # Payment provider token (empty for Telegram Stars, or token for Stripe/etc.)
    )

    # Stripe
    stripe_api_key: str = ""  # Stripe API key
    stripe_webhook_secret: str = ""  # Stripe webhook secret for signature validation
    stripe_price_pro_monthly: str = ""  # Pro plan monthly price ID
    stripe_price_pro_yearly: str = ""  # Pro plan yearly price ID
    stripe_price_content_monthly: str = ""  # Content Pro monthly price ID
    stripe_price_content_yearly: str = ""  # Content Pro yearly price ID
    stripe_webhook_url: str = ""  # Stripe webhook endpoint URL

    # Newsletter settings
    newsletter_hours_to_fetch: int = 24  # Hours of news to include
    newsletter_max_articles: int = 50  # Max articles per digest

    # Buffer settings
    message_buffer_hours: int = 24
    max_messages_per_summary: int = 500

    # Summary length settings
    default_summary_length: str = "medium"  # short, medium, long

    # Admin settings (comma-separated user IDs)
    admin_user_ids: str = ""


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
