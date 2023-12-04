__all__ = ["router"]

from typing import Annotated

from fastapi import APIRouter

from src.api.dependencies import DEPENDS_USER_REPOSITORY, DEPENDS_VERIFIED_REQUEST
from src.api.exceptions import (
    IncorrectCredentialsException,
    NoCredentialsException,
)
from src.modules.auth.schemas import VerificationResult
from src.modules.user.repository import UserRepository
from src.modules.user.schemas import ViewUser

router = APIRouter(prefix="/users", tags=["Users"])


@router.get(
    "/me",
    responses={
        200: {"description": "User info"},
        **IncorrectCredentialsException.responses,
        **NoCredentialsException.responses,
    },
)
async def get_me(
    user_repository: Annotated[UserRepository, DEPENDS_USER_REPOSITORY],
    verification: Annotated[VerificationResult, DEPENDS_VERIFIED_REQUEST],
) -> ViewUser:
    """
    Get user info
    """

    user = await user_repository.read(verification.user_id)
    user: ViewUser
    return user
