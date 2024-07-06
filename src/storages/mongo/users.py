__all__ = ["User", "UserRole"]

from enum import StrEnum

from pydantic import BaseModel
from pymongo import IndexModel

from src.storages.mongo.__base__ import CustomDocument


class UserRole(StrEnum):
    DEFAULT = "default"
    ADMIN = "admin"


class UserSchema(BaseModel):
    name: str | None = None
    login: str
    password_hash: str
    role: UserRole = UserRole.DEFAULT


class User(UserSchema, CustomDocument):
    class Settings:
        indexes = [IndexModel("login", unique=True)]
