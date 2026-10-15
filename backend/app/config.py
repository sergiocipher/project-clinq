"""
WHY THIS FILE EXISTS:
Centralises all configuration loaded from environment variables.
Using pydantic-settings means missing required vars fail fast at startup
with a clear error, rather than crashing silently mid-request.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database_url: str  # required — no default; app refuses to start without it
    app_version: str = "dev"
    cors_origins: str = "http://localhost:5173"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    @property
    def cors_origins_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",")]


settings = Settings()
