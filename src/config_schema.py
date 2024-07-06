from enum import StrEnum
from pathlib import Path

import yaml
from pydantic import BaseModel, Field, SecretStr, ConfigDict


class Environment(StrEnum):
    DEVELOPMENT = "development"
    PRODUCTION = "production"


class SettingBaseModel(BaseModel):
    model_config = ConfigDict(use_attribute_docstrings=True, extra="forbid")


class Cookies(SettingBaseModel):
    # Authentication
    name: str = "token"
    domain: str = "innohassle.ru"
    allowed_domains: list[str] = ["innohassle.ru", "api.innohassle.ru", "localhost"]


class StaticFiles(SettingBaseModel):
    mount_path: str = "/static"
    mount_name: str = "static"
    directory: Path = Path("static")


class Database(SettingBaseModel):
    """MongoDB database settings."""

    uri: SecretStr = Field(..., examples=["mongodb://username:password@localhost:27017/db?authSource=admin"])


class Predefined(SettingBaseModel):
    """Predefined settings. Will be used in setup stage."""

    first_superuser_login: str = "admin"
    "Login for the first superuser"
    first_superuser_password: str = "admin"
    "Password for the first superuser"


class Settings(SettingBaseModel):
    """
    Settings for the application.
    """

    schema_: str = Field(None, alias="$schema")
    environment: Environment = Environment.DEVELOPMENT
    "App environment flag"
    app_root_path: str = ""
    'Prefix for the API path (e.g. "/api/v0")'
    database: Database
    "MongoDB database settings"
    predefined: Predefined = Predefined()
    "Predefined settings"
    session_secret_key: SecretStr
    "Secret key for sessions middleware. Use 'openssl " "rand -hex 32' to generate keys"
    jwt_private_key: SecretStr
    "Private key for JWT. Use 'openssl genrsa -out private.pem 2048' to generate keys"
    jwt_public_key: str
    "Public key for JWT. Use 'openssl rsa -in private.pem -pubout -out public.pem' to generate keys"
    # Static files
    static_files: StaticFiles | None = None
    "Static files settings"
    cors_allow_origins: list[str] = ["https://innohassle.ru", "http://localhost:3000"]
    "CORS origins, used by FastAPI CORSMiddleware"
    # Authentication
    cookie: Cookies | None = Cookies()
    "Cookies settings"

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
