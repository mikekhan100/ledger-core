from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", 
        env_file_encoding="utf-8", 
        extra="ignore"
    )

    PROJECT_NAME: str = "ledger-core"
    ENVIRONMENT: str = "development"
    LOG_LEVEL: str = "INFO"
    
    # Defaults to async SQLite for local dev/testing; overridden by Postgres in production
    DATABASE_URL: str = "sqlite+aiosqlite:///./ledger.db"

settings = Settings()