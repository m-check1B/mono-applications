"""
Learn by Kraliki - Configuration
"""

from pydantic import ConfigDict
from pydantic_settings import BaseSettings
from typing import List
import os


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = ConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
    )

    # App
    app_name: str = "Learn by Kraliki"
    app_version: str = "1.0.0"
    debug: bool = True

    # Server - SECURITY: Always bind to 127.0.0.1, never 0.0.0.0
    host: str = "127.0.0.1"
    port: int = 8030

    # Database
    database_url: str = "sqlite+aiosqlite:///./learn.db"

    # CORS
    cors_origins: List[str] = [
        "http://localhost:5176",
        "http://127.0.0.1:5176",
        "https://learn.verduona.dev",
        "https://learn.kraliki.com",
        "https://kraliki.verduona.dev",
        "https://kraliki.com",
    ]

    # Content directory
    content_dir: str = os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))),
        "content"
    )


settings = Settings()
