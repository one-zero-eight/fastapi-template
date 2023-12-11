__all__ = [
    "Shared",
    "DEPENDS_VERIFIED_REQUEST",
]

from fastapi import Depends

from typing import TypeVar, ClassVar, Callable, Union, Hashable

T = TypeVar("T")

CallableOrValue = Union[Callable[[], T], T]


class Shared:
    """
    Key-value storage with generic type support for accessing shared dependencies
    """

    providers: ClassVar[dict[type, CallableOrValue]] = {}

    @classmethod
    def register_provider(cls, key: type[T] | Hashable, provider: CallableOrValue):
        cls.providers[key] = provider

    @classmethod
    def fetch(cls, key: type[T] | Hashable) -> T:
        if isinstance(key, type) and key not in cls.providers:
            # try by classname
            key = key.__name__

            if key not in cls.providers:
                raise KeyError(f"Provider for {key} is not registered")
        elif isinstance(key, str) and key not in cls.providers:
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


from src.modules.auth.dependencies import verify_request  # noqa: E402

DEPENDS_VERIFIED_REQUEST = Depends(verify_request)
"""It's a dependency injection container for FastAPI.
See `FastAPI docs <(https://fastapi.tiangolo.com/tutorial/dependencies/)>`_ for more info"""
