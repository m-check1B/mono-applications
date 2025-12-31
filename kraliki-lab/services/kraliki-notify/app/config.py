from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    bot_token: str
    admin_chat_id: str | int | None = None
    debug: bool = False
    github_root: str = "/home/adminmatej/github"

    # Webhook settings (required for production)
    webhook_url: str | None = None  # e.g., https://kraliki.com (prod) or https://kraliki.verduona.dev (dev)
    webhook_secret: str | None = None  # Random string for security
    webhook_port: int = 8097  # Internal port for FastAPI

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

settings = Settings()
