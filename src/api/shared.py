__all__ = ["Shared", "DEPENDS_VERIFIED_REQUEST", "DEPENDS_SESSION", "DEPENDS_ADMIN"]

from fastapi import Depends

from typing import TypeVar, ClassVar, Callable, Union, Hashable

from sqlalchemy.ext.asyncio import AsyncSession

from src.api.exceptions import ForbiddenException
from src.modules.auth.schemas import VerificationResult
from src.modules.auth.dependencies import verify_request

T = TypeVar("T")

CallableOrValue = Union[Callable[[], T], T]


class Shared:
    """
    Key-value storage with generic type support for accessing shared dependencies
    """

    __slots__ = ()

    providers: ClassVar[dict[type, CallableOrValue]] = {}

    @classmethod
    def register_provider(cls, key: type[T] | Hashable, provider: CallableOrValue):
        cls.providers[key] = provider

    @classmethod
    def f(cls, key: type[T] | Hashable) -> T:
        """
        Get shared dependency by key (f - fetch)
        :param key:
        :return:
        """
        if key not in cls.providers:
            if isinstance(key, type):
                # try by classname
                key = key.__name__

                if key not in cls.providers:
                    raise KeyError(f"Provider for {key} is not registered")

            elif isinstance(key, str):
                # try by classname
                for cls_key in cls.providers.keys():
                    if cls_key.__name__ == key:
                        key = cls_key
                        break
                else:
                    raise KeyError(f"Provider for {key} is not registered")

        provider = cls.providers[key]

        if callable(provider):
            return provider()
        else:
            return provider


DEPENDS_VERIFIED_REQUEST = Depends(verify_request)


async def get_session():
    async with Shared.f(AsyncSession) as session:
        yield session


DEPENDS_SESSION = Depends(get_session)


async def ensure_admin(verification: VerificationResult = DEPENDS_VERIFIED_REQUEST):
    if not verification.is_admin:
        raise ForbiddenException()
    return verification


DEPENDS_ADMIN = Depends(ensure_admin)
