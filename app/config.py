from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str
    redis_url: str = "redis://localhost:6379"
    hashids_salt: str = "change-me-in-production"
    database_url_test: str | None = None
    jwt_secret_key: str = "change-me-in-production"



settings = Settings()