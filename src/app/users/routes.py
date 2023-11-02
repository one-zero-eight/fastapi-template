from typing import Annotated

from src.app.dependencies import DEPENDS_CURRENT_USER_ID, DEPENDS_USER_REPOSITORY
from src.app.users import router
from src.exceptions import (
    IncorrectCredentialsException,
    NoCredentialsException,
)
from src.repositories.users import AbstractUserRepository
from src.schemas.users import ViewUser


@router.get(
    "/me",
    responses={
        200: {"description": "Current user info"},
        **IncorrectCredentialsException.responses,
        **NoCredentialsException.responses,
    },
)
async def get_me(
    user_id: Annotated[int, DEPENDS_CURRENT_USER_ID],
    user_repository: Annotated[AbstractUserRepository, DEPENDS_USER_REPOSITORY],
) -> ViewUser:
    """
    Get current user info if authenticated
    """
    user = await user_repository.read(user_id)
    user: ViewUser
    return user
