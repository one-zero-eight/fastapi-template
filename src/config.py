import os
from enum import StrEnum
from pathlib import Path
from typing import Optional

import yaml
from pydantic import SecretStr, BaseModel, Field
from pydantic_settings import SettingsConfigDict


class Environment(StrEnum):
    DEVELOPMENT = "development"
    PRODUCTION = "production"
    TESTING = "testing"


class Cookies(BaseModel):
    # Authentication
    NAME: str = "token"
    DOMAIN: str = "innohassle.ru"
    ALLOWED_DOMAINS: list[str] = ["innohassle.ru", "api.innohassle.ru", "localhost"]


class AdminPanel(BaseModel):
    ...


class StaticFiles(BaseModel):
    MOUNT_PATH: str = "/static"
    MOUNT_NAME: str = "static"
    DIRECTORY: Path = Path("static")


class Settings(BaseModel):
    """
    Settings for the application.
    """

    model_config = SettingsConfigDict(extra="ignore")

    # App environment
    ENVIRONMENT: Environment = Environment.DEVELOPMENT

    # Prefix for the API path (e.g. "/api/v0")
    APP_ROOT_PATH: str = ""

    # PostgreSQL database connection URL
    DB_URL: SecretStr

    # You can run 'openssl rand -hex 32' to generate keys
    SESSION_SECRET_KEY: SecretStr

    # Run 'openssl genrsa -out private.pem 2048' to generate keys
    JWT_PRIVATE_KEY: SecretStr
    # For existing key run 'openssl rsa -in private.pem -pubout -out public.pem'
    JWT_PUBLIC_KEY: str

    # Static files
    STATIC_FILES: StaticFiles = Field(default_factory=StaticFiles)

    # Security
    CORS_ALLOW_ORIGINS: list[str] = [
        "https://innohassle.ru",
        "http://localhost:3000",
    ]

    # Admin panel
    ADMIN_PANEL: Optional[AdminPanel] = None

    # Authentication
    COOKIE: Optional[Cookies] = Field(default_factory=Cookies)

    @classmethod
    def from_yaml(cls, path: Path) -> "Settings":
        with open(path, "r", encoding="utf-8") as f:
            yaml_config = yaml.safe_load(f)

        return cls.model_validate(yaml_config)


settings_path = os.getenv("SETTINGS_PATH")
if settings_path is None:
    settings_path = "settings.yaml"
settings: Settings = Settings.from_yaml(Path(settings_path))
