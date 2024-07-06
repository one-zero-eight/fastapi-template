__all__ = ["verify_request"]

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from src.api.exceptions import IncorrectCredentialsException
from src.modules.auth.repository import TokenRepository
from src.modules.auth.schemas import VerificationResult

bearer_scheme = HTTPBearer(
    scheme_name="Bearer",
    description="Your JSON Web Token (JWT)",
    bearerFormat="JWT",
    auto_error=False,  # We'll handle error manually
)


async def get_access_token(
    bearer: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
) -> str | None:
    # Prefer header to cookie
    if bearer:
        return bearer.credentials


async def verify_request(
    bearer: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
) -> VerificationResult:
    """
    Check one of the following:
    - Bearer token from header with BOT_TOKEN
    - Bearer token from header with webapp data
    :raises IncorrectCredentialsException: if token is invalid
    """

    if not bearer:
        raise IncorrectCredentialsException(no_credentials=True)

    verification_result = await TokenRepository.verify_access_token(bearer.credentials)

    if verification_result.success:
        return verification_result

    raise IncorrectCredentialsException()
