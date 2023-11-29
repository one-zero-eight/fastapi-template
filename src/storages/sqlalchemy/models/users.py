__all__ = ["User"]

from enum import StrEnum

from sqlalchemy import Enum

from src.storages.sqlalchemy.models.__mixin__ import IdMixin
from src.storages.sqlalchemy.models.base import Base
from src.storages.sqlalchemy.utils import *


class UserRole(StrEnum):
    DEFAULT = "default"
    ADMIN = "admin"


class User(Base, IdMixin):
    __tablename__ = "users"

    name: Mapped[str] = mapped_column(nullable=True)
    login: Mapped[str] = mapped_column(unique=True)

    password_hash: Mapped[str] = mapped_column(nullable=False)

    role: Mapped[UserRole] = mapped_column(Enum(UserRole), nullable=False, default=UserRole.DEFAULT)
