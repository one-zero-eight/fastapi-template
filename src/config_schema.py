from enum import StrEnum
from pathlib import Path
from typing import Union, Optional

import yaml
from pydantic import BaseModel, Field, field_validator, SecretStr, ConfigDict
from pydantic_core.core_schema import ValidationInfo
from pydantic_settings import SettingsConfigDict
from sqlalchemy import URL as DatabaseURI, make_url


class Environment(StrEnum):
    DEVELOPMENT = "development"
    PRODUCTION = "production"
    TESTING = "testing"


class Cookies(BaseModel):
    # Authentication
    name: str = "token"
    domain: str = "innohassle.ru"
    allowed_domains: list[str] = ["innohassle.ru", "api.innohassle.ru", "localhost"]


class AdminPanel(BaseModel):
    ...


class StaticFiles(BaseModel):
    mount_path: str = "/static"
    mount_name: str = "static"
    directory: Path = Path("static")


class Database(BaseModel):
    """PostgreSQL database settings."""

    model_config = ConfigDict(arbitrary_types_allowed=True)

    uri: Union[Optional[DatabaseURI], Optional[str]] = Field(
        None, description="Database URI. If not set, will be generated from other settings"
    )

    username: Optional[str] = Field(None, description="Database username")
    password: Optional[str] = Field(None, description="Database password")
    host: Optional[str] = Field(None, description="Database host")
    port: Optional[int] = Field(None, description="Database port")
    database_name: Optional[str] = Field(None, description="Database name")

    @field_validator("uri", mode="before")
    @classmethod
    def resolve(cls, v: Optional[str], values: ValidationInfo) -> Optional[DatabaseURI]:
        if isinstance(v, str):
            return make_url(v)
        elif isinstance(v, DatabaseURI):
            return v
        return DatabaseURI.create(
            "postgresql",
            username=values.data.get("USERNAME", "postgres"),
            password=values.data.get("PASSWORD", "postgres"),
            host=values.data.get("HOST", "localhost"),
            port=values.data.get("PORT", 5432),
            database=f"{values.data.get('DATABASE_NAME', 'postgres') or ''}",
        )

    def get_async_engine(self):
        from sqlalchemy.ext.asyncio import create_async_engine

        return create_async_engine(self.uri)

    def get_sync_engine(self):
        from sqlalchemy import create_engine

        return create_engine(self.uri)


class Predefined(BaseModel):
    """Predefined settings. Will be used in setup stage."""

    first_superuser_login: str = Field(default="admin", description="Login for the first superuser")
    first_superuser_password: str = Field(default="admin", description="Password for the first superuser")


class Settings(BaseModel):
    """
    Settings for the application.
    """

    model_config = SettingsConfigDict()

    environment: Environment = Field(Environment.DEVELOPMENT, description="App environment flag")

    app_root_path: str = Field("", description='Prefix for the API path (e.g. "/api/v0")')

    database: Database = Field(default_factory=Database, description="PostgreSQL database settings")

    predefined: Predefined = Field(default_factory=Predefined, description="Predefined settings")

    session_secret_key: SecretStr = Field(
        ..., description="Secret key for sessions middleware. Use 'openssl " "rand -hex 32' to generate keys"
    )

    jwt_private_key: SecretStr = Field(
        ...,
        description="Private key for JWT. Use 'openssl genrsa -out private.pem 2048' to generate keys",
    )

    jwt_public_key: str = Field(
        ...,
        description="Public key for JWT. Use 'openssl rsa -in private.pem -pubout -out public.pem' to generate keys",
    )

    # Static files
    static_files: StaticFiles = Field(default_factory=StaticFiles, description="Static files settings")

    # Security
    cors_allow_origins: list[str] = Field(
        default_factory=lambda: [
            "https://innohassle.ru",
            "http://localhost:3000",
        ],
        description="CORS origins, used by FastAPI CORSMiddleware",
    )

    # Admin panel
    admin_panel: Optional[AdminPanel] = Field(None, description="Admin panel settings. If not set, will be disabled")

    # Authentication
    cookie: Optional[Cookies] = Field(default_factory=Cookies, description="Cookies settings")

    @classmethod
    def from_yaml(cls, path: Path) -> "Settings":
        with open(path, "r", encoding="utf-8") as f:
            yaml_config = yaml.safe_load(f)

        return cls.model_validate(yaml_config)

    @classmethod
    def save_schema(cls, path: Path) -> None:
        with open(path, "w", encoding="utf-8") as f:
            schema = {"$schema": "http://json-schema.org/draft-07/schema#", **cls.model_json_schema()}
            yaml.dump(schema, f, sort_keys=False)


if __name__ == "__main__":
    Settings.save_schema(Path(__file__).parents[1] / "settings.schema.yaml")
