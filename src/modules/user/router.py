__all__ = ["router"]

from fastapi import APIRouter

from src.api.exceptions import IncorrectCredentialsException
from src.api.shared import VerifiedDep
from src.modules.user.repository import user_repository
from src.modules.user.schemas import ViewUser

router = APIRouter(prefix="/users", tags=["Users"])


@router.get(
    "/me",
    responses={
        200: {"description": "User info"},
        **IncorrectCredentialsException.responses,
    },
)
async def get_me(
    verification: VerifiedDep,
) -> ViewUser:
    """
    Get user info
    """
    user: ViewUser = await user_repository.read(verification.user_id)
    return user
