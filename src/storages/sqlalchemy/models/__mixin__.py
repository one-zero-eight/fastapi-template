__all__ = [
    "IdMixin",
]

from sqlalchemy.orm import Mapped, mapped_column


class IdMixin:
    id: Mapped[int] = mapped_column(primary_key=True)
