from fastapi import APIRouter

from src.api.dependencies import USER_AUTH
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
async def get_me(auth: USER_AUTH) -> ViewUser:
    """
    Get current user info if authenticated
    """

    user = await user_repository.read(auth.user_id)
    return user
