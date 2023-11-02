__all__ = ["User"]

from sqlalchemy.orm import mapped_column, Mapped

from src.storages.sqlalchemy.models.__mixin__ import IdMixin
from src.storages.sqlalchemy.models.base import Base


class User(Base, IdMixin):
    __ownerships_tables__ = dict()
    __tablename__ = "users"

    name: Mapped[str] = mapped_column(nullable=True)
    email: Mapped[str] = mapped_column(unique=True)
