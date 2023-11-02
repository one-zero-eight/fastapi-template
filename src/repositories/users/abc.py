__all__ = ["AbstractUserRepository"]

from abc import ABCMeta, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.schemas.users import ViewUser, CreateUser


class AbstractUserRepository(metaclass=ABCMeta):
    # ----------------- CRUD ----------------- #
    @abstractmethod
    async def create_or_update(self, user: "CreateUser") -> "ViewUser":
        ...

    @abstractmethod
    async def read(self, id_: int) -> "ViewUser":
        ...

    @abstractmethod
    async def read_by_email(self, innopolis_email: str) -> "ViewUser":
        ...
