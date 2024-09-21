__all__ = ["User", "UserRole"]

from enum import StrEnum

from sqlalchemy import Enum

from src.storages.sql.models.base import Base
from src.storages.sql.utils import *


class UserRole(StrEnum):
    DEFAULT = "default"
    ADMIN = "admin"


class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    "Unique identifier for the object"
    innohassle_id: Mapped[str]
    "InnoHassle identifier"
    email: Mapped[str]
    "User's email"
    name: Mapped[str | None]
    "User's name"
    role: Mapped[UserRole] = mapped_column(Enum(UserRole), default=UserRole.DEFAULT)
    "User's role"
