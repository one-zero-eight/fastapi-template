__all__ = ["User"]

from src.storages.sqlalchemy.models.__mixin__ import IdMixin
from src.storages.sqlalchemy.models.base import Base
from src.storages.sqlalchemy.utils import *


class User(Base, IdMixin):
    __tablename__ = "users"

    name: Mapped[str] = mapped_column(nullable=True)
    email: Mapped[str] = mapped_column(unique=True)

    password_hash: Mapped[str] = mapped_column(nullable=False)
