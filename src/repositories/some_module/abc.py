__all__ = ["AbstractSomeModuleRepository"]

from abc import ABCMeta, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    # safe import during type checking stage;
    # we can do it as abstraction layer doesn't use any scheme
    from src.schemas import CreateSomeScheme, ViewSomeScheme, UpdateSomeScheme


class AbstractSomeModuleRepository(metaclass=ABCMeta):
    # ----------------- CRUD ----------------- #
    @abstractmethod
    async def create(self, data: "CreateSomeScheme") -> "ViewSomeScheme":
        ...

    @abstractmethod
    async def batch_create(self, data: list["CreateSomeScheme"]) -> list["ViewSomeScheme"]:
        ...

    @abstractmethod
    async def read(self, id: int) -> "ViewSomeScheme":
        ...

    @abstractmethod
    async def read_all(self) -> list["ViewSomeScheme"]:
        ...

    @abstractmethod
    async def batch_read(self, ids: list[int]) -> list["ViewSomeScheme"]:
        ...

    @abstractmethod
    async def update(self, id_: int, data: "UpdateSomeScheme"):
        ...

    # ^^^^^^^^^^^^^^^^^ CRUD ^^^^^^^^^^^^^^^^^ #
