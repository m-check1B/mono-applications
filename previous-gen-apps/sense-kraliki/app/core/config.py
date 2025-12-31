"""Application configuration."""
from functools import lru_cache
from typing import List

from pydantic import ConfigDict, Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings."""

    model_config = ConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
    )

    # Telegram
    telegram_bot_token: str = Field(..., min_length=1)
    telegram_stars_provider_token: str = ""

    # AI
    gemini_api_key: str = Field(..., min_length=1)
    gemini_model: str = "gemini-2.0-flash"
    gemini_vision_model: str = "gemini-2.0-flash"

    # Database
    database_url: str = "postgresql+asyncpg://localhost/sense_kraliki"
    redis_url: str = "redis://localhost:6379/0"

    # Admin user IDs (comma-separated in env)
    admin_user_ids: List[int] = Field(default_factory=list)

    # Data sources
    noaa_base_url: str = "https://services.swpc.noaa.gov"
    usgs_base_url: str = "https://earthquake.usgs.gov"
    weather_base_url: str = "https://api.open-meteo.com/v1"
    schumann_image_url: str = "https://geocenter.info/en/monitoring/schumann"

    # Subscription pricing (Telegram Stars)
    free_dreams_per_month: int = 3
    sensitive_price_stars: int = 150  # ~$3/mo
    empath_price_stars: int = 350  # ~$7/mo

    # Audit
    audit_price_eur: int = 500
    audit_payment_link: str = "https://buy.stripe.com/placeholder_sense_kraliki_audit"

    # Cache TTL (seconds)
    cosmic_data_ttl: int = 3600  # 1 hour
    weather_data_ttl: int = 1800  # 30 min
    schumann_ttl: int = 3600  # 1 hour


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
