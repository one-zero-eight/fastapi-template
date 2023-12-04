"""

Live Template for dependencies:
    enum(
        "storage: Annotated[SQLAlchemyStorage, DEPENDS_STORAGE]",
        "user_repository: Annotated[UserRepository, DEPENDS_USER_REPOSITORY]",
        "auth_repository: Annotated[AuthRepository, DEPENDS_AUTH_REPOSITORY]",
        "verification: Annotated[VerificationResult, DEPENDS_VERIFIED_REQUEST]",
    )
"""

__all__ = [
    "DEPENDS",
    "DEPENDS_STORAGE",
    "DEPENDS_USER_REPOSITORY",
    "DEPENDS_VERIFIED_REQUEST",
    "DEPENDS_AUTH_REPOSITORY",
    "Dependencies",
]

from fastapi import Depends

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.modules.user.repository import UserRepository
    from src.modules.auth.repository import AuthRepository
    from src.storages.sqlalchemy.storage import SQLAlchemyStorage


class Dependencies:
    _storage: "SQLAlchemyStorage"
    _user_repository: "UserRepository"
    _auth_repository: "AuthRepository"

    @classmethod
    def get_storage(cls) -> "SQLAlchemyStorage":
        return cls._storage

    @classmethod
    def set_storage(cls, storage: "SQLAlchemyStorage"):
        cls._storage = storage

    @classmethod
    def get_user_repository(cls) -> "UserRepository":
        return cls._user_repository

    @classmethod
    def set_user_repository(cls, user_repository: "UserRepository"):
        cls._user_repository = user_repository

    @classmethod
    def get_auth_repository(cls) -> "AuthRepository":
        return cls._auth_repository

    @classmethod
    def set_auth_repository(cls, auth_repository: "AuthRepository"):
        cls._auth_repository = auth_repository


DEPENDS = Depends(lambda: Dependencies)
"""It's a dependency injection container for FastAPI.
See `FastAPI docs <(https://fastapi.tiangolo.com/tutorial/dependencies/)>`_ for more info"""
DEPENDS_STORAGE = Depends(Dependencies.get_storage)
DEPENDS_USER_REPOSITORY = Depends(Dependencies.get_user_repository)
DEPENDS_AUTH_REPOSITORY = Depends(Dependencies.get_auth_repository)

from src.modules.auth.dependencies import verify_request  # noqa: E402

DEPENDS_VERIFIED_REQUEST = Depends(verify_request)
