from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str
    redis_url: str = "redis://localhost:6379"
    hashids_salt: str = "change-me-in-production"
    database_url_test: str | None = None
    jwt_secret_key: str = "change-me-in-production"
    base_url: str = "http://127.0.0.1:8000"
    max_custom_aliases_per_user: int = 5
    custom_alias_limit_window_days: int | None = 30
    qr_cache_ttl_seconds: int = 86400


settings = Settings()