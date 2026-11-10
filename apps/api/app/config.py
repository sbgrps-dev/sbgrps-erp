from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = "postgresql+asyncpg://sbgrps:sbgrps@localhost:5432/sbgrps"
    # When set, every /api request must send "Authorization: Bearer <api_token>".
    api_token: str | None = None
    cors_origins: list[str] = ["http://localhost:3000"]
    company_short_name: str = "SBE"
    operator_name: str = "prem"


@lru_cache
def get_settings() -> Settings:
    return Settings()
