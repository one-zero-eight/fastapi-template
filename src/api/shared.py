__all__ = ["VerifiedDep", "EnsureAdminDep"]

from typing import Annotated

from fastapi import Depends

from src.api.exceptions import ForbiddenException
from src.modules.auth.dependencies import verify_request
from src.modules.auth.schemas import VerificationResult
from src.storages.mongo.users import UserRole

VerifiedDep = Annotated[VerificationResult, Depends(verify_request)]


async def ensure_admin(verification: VerifiedDep):
    if not verification.role == UserRole.ADMIN:
        raise ForbiddenException()
    return verification


EnsureAdminDep = Annotated[VerificationResult, Depends(ensure_admin)]
