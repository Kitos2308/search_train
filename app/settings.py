from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    ENVIRONMENT: str = Field(default=..., min_length=2, max_length=20)
    SERVICE_NAME: str = Field(default=..., min_length=2, max_length=20)
    # PostgreSQL
    DB_PORT: int = Field(default=..., ge=1)
    DB_HOST: str = Field(default=..., min_length=1)
    DB_USER: str = Field(default=..., min_length=1)
    DB_PASS: str = Field(default=..., min_length=1)
    DB_NAME: str = Field(default=..., min_length=1)
    DB_SCHEMA: str = Field(default=..., min_length=1)

    DB_TIMEOUT: int = Field(default=30, ge=0, le=300)
    DB_POOL_SIZE: int = Field(default=20, ge=1, le=100)
    DB_ECHO_QUERIES: bool = Field(default=False)
    DB_SESSION_EXPIRE_ON_COMMIT: bool = Field(default=False)
    DB_SESSION_AUTOCOMMIT: bool = Field(default=False)
    DB_SESSION_AUTOFLUSH: bool = Field(default=False)

    # Название базы данных для запуска локальных тестов (pytest). Если задано, то DB_SCHEMA будет заменено на это значение в conftest.py
    TEST_DB_SCHEMA: str = Field(default="")

    SENTRY_DSN: str = Field(default="")
    DEBUG: bool = Field(default=True)

    SEARCH_INDEX_NAME_ALPHA: str = Field(default="")
    SEARCH_INDEX_NAME_BETA: str = Field(default="")
    ACTIVE_SEARCH_INDEX_ALIAS: str = Field(default="")

    SENTRY_ENVIRONMENT: str = Field("SENTRY_ENVIRONMENT", min_length=1)

    ELASTICSEARCH_HOST: str = Field(default="", min_length=3)

    model_config = SettingsConfigDict(env_file=("../.env", ".env"), env_file_encoding="utf-8", extra="ignore")


settings = Settings()
