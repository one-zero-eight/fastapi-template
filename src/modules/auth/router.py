__all__ = ["router"]

from fastapi import APIRouter

from src.modules.auth.repository import TokenRepository, auth_repository
from src.modules.auth.schemas import AuthResult, AuthCredentials

router = APIRouter(prefix="/auth", tags=["Auth"])


# by-tag
@router.post("/by-credentials", response_model=AuthResult)
async def by_credentials(credentials: AuthCredentials):
    user_id = await auth_repository.authenticate_user(password=credentials.password, login=credentials.login)
    token = TokenRepository.create_access_token(user_id)
    return AuthResult(token=token, success=True)
