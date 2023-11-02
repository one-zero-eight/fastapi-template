__all__ = []

from typing import Annotated

from src.config import settings, Environment
from src.repositories.users import AbstractUserRepository

enabled = settings.ENVIRONMENT == Environment.DEVELOPMENT

if enabled:
    import warnings

    from src.app.auth import router
    from src.app.auth.common import redirect_with_token, ensure_allowed_return_to
    from src.repositories.tokens import TokenRepository
    from src.schemas.users import CreateUser
    from src.app.dependencies import DEPENDS_USER_REPOSITORY

    warnings.warn(
        "Dev auth provider is enabled! "
        "Use this only for development environment "
        "(otherwise, set ENVIRONMENT=production)."
    )

    @router.get("/dev/login", include_in_schema=False)
    async def dev_login(
        user_repository: Annotated[AbstractUserRepository, DEPENDS_USER_REPOSITORY],
        return_to: str = "/",
        email: str = "a.a@innopolis.university",
        name="Alex Alex",
    ):
        ensure_allowed_return_to(return_to)
        user = await user_repository.create_or_update(CreateUser(email=email, name=name))
        token = TokenRepository.create_access_token(user.id)
        return redirect_with_token(return_to, token)

    @router.get("/dev/token")
    async def get_dev_token(
        user_repository: Annotated[AbstractUserRepository, DEPENDS_USER_REPOSITORY],
        email: str = "a.a@innopolis.university",
        name="Alex Alex",
    ) -> str:
        user = await user_repository.create_or_update(CreateUser(email=email, name=name))
        return TokenRepository.create_access_token(user.id)
