__all__ = ["router"]

from fastapi import APIRouter
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.shared import Shared, VerifiedDep
from src.api.exceptions import (
    IncorrectCredentialsException,
    NoCredentialsException,
)
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
    verification: VerifiedDep,
) -> ViewUser:
    """
    Get user info
    """
    user_repository = Shared.f(UserRepository)
    async with Shared.f(AsyncSession) as session:
        user = await user_repository.read(verification.user_id, session)
    user: ViewUser
    return user
