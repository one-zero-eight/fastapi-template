__all__ = ["get_current_user_id"]

from typing import Optional

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer, APIKeyCookie

from src.repositories.tokens import TokenRepository
from src.config import settings
from src.exceptions import (
    NoCredentialsException,
)

bearer_scheme = HTTPBearer(
    scheme_name="Bearer",
    description="Your JSON Web Token (JWT)",
    bearerFormat="JWT",
    auto_error=False,  # We'll handle error manually
)

cookie_scheme = APIKeyCookie(
    scheme_name="Cookie",
    description="Your JSON Web Token (JWT) stored as 'token' cookie",
    name=settings.AUTH_COOKIE_NAME,  # Cookie name
    auto_error=False,  # We'll handle error manually
)


async def get_access_token(
    bearer: Optional[HTTPAuthorizationCredentials] = Depends(bearer_scheme),
    cookie: str = Depends(cookie_scheme),
) -> Optional[str]:
    # Prefer header to cookie
    if bearer and bearer.credentials:
        return bearer.credentials
    elif cookie:
        return cookie


async def get_current_user_id(
    token: Optional[str] = Depends(get_access_token),
) -> int:
    """
    :raises NoCredentialsException: if token is not provided
    :param token: JWT token from header or cookie
    :return: user id
    """
    if not token:
        raise NoCredentialsException()

    token_data = await TokenRepository.verify_user_token(token)
    return token_data.user_id
