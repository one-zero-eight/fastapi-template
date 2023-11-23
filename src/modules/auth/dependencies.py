__all__ = ["verify_request"]

from typing import Optional

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from src.api.exceptions import NoCredentialsException, IncorrectCredentialsException
from src.modules.auth.repository import TokenRepository
from src.modules.auth.schemas import VerificationResult

bearer_scheme = HTTPBearer(
    scheme_name="Bearer",
    description="Your JSON Web Token (JWT)",
    bearerFormat="JWT",
    auto_error=False,  # We'll handle error manually
)


async def get_access_token(
    bearer: Optional[HTTPAuthorizationCredentials] = Depends(bearer_scheme),
) -> Optional[str]:
    # Prefer header to cookie
    if bearer:
        return bearer.credentials


async def verify_request(
    bearer: Optional[HTTPAuthorizationCredentials] = Depends(bearer_scheme),
) -> VerificationResult:
    """
    Check one of the following:
    - Bearer token from header with BOT_TOKEN
    - Bearer token from header with webapp data
    :raises NoCredentialsException: if token is not provided
    :raises IncorrectCredentialsException: if token is invalid
    """
    if not bearer:
        raise NoCredentialsException()

    verification_result = await TokenRepository.verify_access_token(bearer.credentials)

    if verification_result.success:
        return verification_result

    raise IncorrectCredentialsException()
