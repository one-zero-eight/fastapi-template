__all__ = ["SomeModelInSingle", "SomeModelInSingleXTag"]

from typing import TYPE_CHECKING

from sqlalchemy import String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.storages.sqlalchemy.models import Base
from src.storages.sqlalchemy.models.__mixin__ import (
    IdMixin,
)

if TYPE_CHECKING:
    # Should be: from src.storages.sqlalchemy.models.users import User
    class User:
        pass

    # Should be: from src.storages.sqlalchemy.models.tags import Tag
    class Tag:
        pass


class SomeModelInSingle(
    Base,
    IdMixin,
):
    # - Meta
    __tablename__ = "some_model_in_plural"
    # - Fields
    alias: Mapped[str] = mapped_column(String(255), unique=True)
    # - - Relationships
    # one-to-many
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), primary_key=True
    )
    user: Mapped["User"] = relationship("User", back_populates="some_model_in_single")
    # many-to-many
    tags: Mapped[list["Tag"]] = relationship(
        "Tag", secondary="some_model_in_single_x_tag"
    )


class SomeModelInSingleXTag(Base):
    # - Meta
    __tablename__ = "some_model_in_single_x_tag"
    # - Fields
    some_model_in_single_id: Mapped[int] = mapped_column(
        ForeignKey("some_model_in_plural.id", ondelete="CASCADE"), primary_key=True
    )
    tag_id: Mapped[int] = mapped_column(
        ForeignKey("tags.id", ondelete="CASCADE"), primary_key=True
    )
    # - - Relationships
    some_model_in_single: Mapped[SomeModelInSingle] = relationship(
        "SomeModelInSingle", back_populates="some_model_in_single_x_tags"
    )
    tag: Mapped[Tag] = relationship("Tag", back_populates="some_model_in_single_x_tags")
