__all__ = ["User", "UserRole"]

from enum import StrEnum

from pymongo import IndexModel

from src.pydantic_base import BaseSchema
from src.storages.mongo.__base__ import CustomDocument


class UserRole(StrEnum):
    DEFAULT = "default"
    ADMIN = "admin"


class UserSchema(BaseSchema):
    innohassle_id: str
    email: str
    name: str | None = None
    role: UserRole = UserRole.DEFAULT


class User(UserSchema, CustomDocument):
    class Settings:
        indexes = [IndexModel("innohassle_id", unique=True), IndexModel("email", unique=True)]
