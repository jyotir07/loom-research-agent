"""Application settings, loaded from environment / backend/.env."""
from __future__ import annotations

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # Default LLM routing (per-call overridable). Loom reads the actual
    # provider API keys (OPENAI_API_KEY, etc.) directly from the env.
    llm_provider: str = "openai"
    llm_model: str = "gpt-4o-mini"

    # Web search
    search_api_key: str | None = None
    search_provider: str = "tavily"

    # Optional persistence
    database_url: str | None = None
    redis_url: str | None = None

    # CORS (comma-separated origins)
    cors_origins: str = "http://localhost:3000"

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]


settings = Settings()
