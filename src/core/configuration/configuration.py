import os
import sys
import logging
import secrets
import warnings
from pathlib import Path
from typing import Any, Annotated, Literal
from typing_extensions import Self # 3.10 python moment

from pydantic import (
    EmailStr,
    AnyUrl,
    BeforeValidator,
    RedisDsn,
    PostgresDsn,
    computed_field,
    model_validator,
)
from pydantic_core import MultiHostUrl
from pydantic_settings import BaseSettings, SettingsConfigDict
from dotenv import load_dotenv


if os.getenv("ISLOCAL", "True").lower() == "true":
    env_p = "local.env"
else:
    project_root = Path(__file__).resolve().parents[3]
    env_p = os.path.join(project_root, ".env")

load_dotenv(dotenv_path=env_p, override=True)


def parse_cors(v: Any) -> list[str] | str:
    if isinstance(v, str) and not v.startswith("["):
        return [i.strip() for i in v.split(",")]
    elif isinstance(v, list | str):
        return v
    raise ValueError(v)


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=env_p, env_ignore_empty=True, extra="ignore"
    )
    SECRET_KEY: str = secrets.token_urlsafe(32)
    # 60 minutes * 24 hours * N days = N days
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 1
    REFRESH_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 14
    NGINX_ADDRESS: str
    DOMAIN: str = "localhost"
    ENVIRONMENT: Literal["local", "staging", "production"] = "local"

    @computed_field
    @property
    def server_host(self) -> str:
        if self.ENVIRONMENT == "local":
            return f"http://{self.DOMAIN}"
        return f"https://{self.DOMAIN}"

    BACKEND_CORS_ORIGINS: Annotated[
        list[AnyUrl] | str, BeforeValidator(parse_cors)
    ] = []

    ECHO_SQL: bool = False
    DROP_TABLES: bool = False
    
    PROJECT_NAME: str
    POSTGRES_SERVER: str
    POSTGRES_PORT: int = 5432
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str = ""

    @computed_field 
    @property
    def SQLALCHEMY_DATABASE_URI(self) -> PostgresDsn:
        return MultiHostUrl.build(
            scheme="postgresql+asyncpg",
            username=self.POSTGRES_USER,
            password=self.POSTGRES_PASSWORD,
            host=self.POSTGRES_SERVER,
            port=self.POSTGRES_PORT,
            path=self.POSTGRES_DB,
        )
    
    @computed_field 
    @property
    def DRIVER_DATABASE_URI(self) -> PostgresDsn:
        return MultiHostUrl.build(
            scheme="postgresql",
            username=self.POSTGRES_USER,
            password=self.POSTGRES_PASSWORD,
            host=self.POSTGRES_SERVER,
            port=self.POSTGRES_PORT,
            path=self.POSTGRES_DB,
        )
    
    REDIS_HOST: str
    REDIS_PORT: int
    
    def _redis_url(self) -> RedisDsn:
        return MultiHostUrl.build(
            scheme="redis",
            host=self.REDIS_HOST,
            port=self.REDIS_PORT,
        )
    
    @computed_field 
    @property
    def REDIS_URI(self) -> RedisDsn:
        return self._redis_url()
    
    @computed_field 
    @property
    def CELERY_BROKER_URL(self) -> RedisDsn:
        return self._redis_url()
    
    @computed_field 
    @property
    def CELERY_RESULT_BACKEND(self) -> RedisDsn:
        return self._redis_url()

    SMTP_PORT: int
    SMTP_HOST: str
    SMTP_USER: str
    SMTP_PASSWORD: str

    EMAIL_RESET_TOKEN_EXPIRE_HOURS: int = 48

    SUPERUSER_EMAIL: EmailStr
    SUPERUSER_PASSWORD: str
    
    @computed_field 
    @property # Не думаю что гуд, но пусть так
    def LOGGER(self) -> logging.Logger:
        return logging.getLogger("uvicorn")

    def _check_default_secret(self, var_name: str, value: str | None) -> None:
        if value == "changethis":
            message = (
                f'The value of {var_name} is "changethis", '
                "for security, please change it, at least for deployments."
            )
            if self.ENVIRONMENT == "local":
                warnings.warn(message, stacklevel=1)
            else:
                raise ValueError(message)

    @model_validator(mode="after")
    def _enforce_non_default_secrets(self) -> Self:
        self._check_default_secret("SECRET_KEY", self.SECRET_KEY)

        return self


settings = Settings()
