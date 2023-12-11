__all__ = ["router"]

from fastapi import APIRouter
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.shared import DEPENDS_SESSION, DEPENDS_ADMIN
from src.config import settings
from src.config_schema import Environment

router = APIRouter(prefix="/dev", tags=["Development"])

if settings.environment == Environment.PRODUCTION:
    raise RuntimeError("You can't use this router in production environment!")


@router.get("/drop-all-tables")
async def drop_all_tables(
    session: AsyncSession = DEPENDS_SESSION,
    _ensure_admin=DEPENDS_ADMIN,
):
    """
    DROP SCHEMA public CASCADE; CREATE SCHEMA public;
    """
    await session.execute(text("DROP SCHEMA public CASCADE;"))
    await session.execute(text("CREATE SCHEMA public;"))
    await session.commit()

    return {"success": True}
