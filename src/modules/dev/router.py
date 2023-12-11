__all__ = ["router"]

from typing import Annotated

from fastapi import APIRouter
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.exceptions import ForbiddenException
from src.api.shared import Shared, DEPENDS_VERIFIED_REQUEST, DEPENDS_SESSION
from src.config import settings
from src.config_schema import Environment
from src.modules.auth.schemas import VerificationResult
from src.modules.user.repository import UserRepository

router = APIRouter(prefix="/dev", tags=["Development"])

if settings.environment == Environment.PRODUCTION:
    raise RuntimeError("You can't use this router in production environment!")


@router.get("/drop-all-tables")
async def drop_all_tables(
    verification: Annotated[VerificationResult, DEPENDS_VERIFIED_REQUEST], session: AsyncSession = DEPENDS_SESSION
):
    """
    DROP SCHEMA public CASCADE; CREATE SCHEMA public;
    """
    user = await Shared.f(UserRepository).read(verification.user_id, session)
    if not user.is_admin:
        raise ForbiddenException()
    await session.execute(text("DROP SCHEMA public CASCADE;"))
    await session.execute(text("CREATE SCHEMA public;"))
    await session.commit()

    return {"success": True}
