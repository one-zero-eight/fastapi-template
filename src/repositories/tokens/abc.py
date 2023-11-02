__all__ = ["AbstractTokenRepository"]

from abc import ABCMeta, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.schemas.tokens import UserTokenData


class AbstractTokenRepository(metaclass=ABCMeta):
    @abstractmethod
    async def verify_user_token(self, token: str) -> "UserTokenData":
        """
        :raises IncorrectCredentialsException: if token is invalid.
        :raises UserNotFound: if user with given token does not exist.
        """

    @abstractmethod
    def create_access_token(self, user_id: int) -> str:
        ...
