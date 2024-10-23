from enum import StrEnum
from pathlib import Path

import yaml
from pydantic import ConfigDict, Field, SecretStr

from src.pydantic_base import BaseSchema


class Environment(StrEnum):
    DEVELOPMENT = "development"
    PRODUCTION = "production"


class SettingBase(BaseSchema):
    model_config = ConfigDict(use_attribute_docstrings=True, extra="forbid")


class Accounts(SettingBase):
    """InNoHassle-Accounts integration settings"""

    api_url: str = "https://api.innohassle.ru/accounts/v0"
    "URL of the Accounts API"
    well_known_url: str = "https://api.innohassle.ru/accounts/v0/.well-known"
    "URL of the well-known endpoint for the Accounts API"
    api_jwt_token: SecretStr
    "JWT token for accessing the Accounts API as a service"


class Settings(SettingBase):
    """
    Settings for the application.
    """

    schema_: str = Field(None, alias="$schema")
    environment: Environment = Environment.DEVELOPMENT
    "App environment flag"
    app_root_path: str = ""
    'Prefix for the API path (e.g. "/api/v0")'
    database_uri: SecretStr = Field(..., examples=["mongodb://mongoadmin:secret@localhost:27017/db?authSource=admin"])
    "MongoDB database settings"
    cors_allow_origins: list[str] = ["https://innohassle.ru", "https://pre.innohassle.ru", "http://localhost:3000"]
    "Allowed origins for CORS: from which domains requests to the API are allowed"
    accounts: Accounts
    "InNoHassle-Accounts integration settings"

    @classmethod
    def from_yaml(cls, path: Path) -> "Settings":
        with open(path, encoding="utf-8") as f:
            yaml_config = yaml.safe_load(f)

        return cls.model_validate(yaml_config)

    @classmethod
    def save_schema(cls, path: Path) -> None:
        with open(path, "w", encoding="utf-8") as f:
            schema = {"$schema": "http://json-schema.org/draft-07/schema#", **cls.model_json_schema()}
            yaml.dump(schema, f, sort_keys=False)
