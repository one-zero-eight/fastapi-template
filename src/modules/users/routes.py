from fastapi import APIRouter

from src.api.dependencies import CURRENT_USER_ID_DEPENDENCY
from src.api.exceptions import IncorrectCredentialsException
from src.modules.users.repository import user_repository
from src.modules.users.schemas import ViewUser

router = APIRouter(
    prefix="/users",
    tags=["Users"],
    responses={
        **IncorrectCredentialsException.responses,
    },
)


@router.get("/me", responses={200: {"description": "Current user info"}})
async def get_me(user_id: CURRENT_USER_ID_DEPENDENCY) -> ViewUser:
    """
    Get current user info if authenticated
    """

    user = await user_repository.read(user_id)
    return user
