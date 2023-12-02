__all__ = ["router"]

from typing import Annotated

from fastapi import APIRouter
from sqlalchemy import text

from src.api.dependencies import DEPENDS_STORAGE
from src.config import settings
from src.config_schema import Environment
from src.storages.sqlalchemy import SQLAlchemyStorage

router = APIRouter(prefix="/dev", tags=["Development"])

if settings.environment == Environment.PRODUCTION:
    raise RuntimeError("You can't use this router in production environment!")


@router.get("/drop-all-tables")
async def drop_all_tables(storage: Annotated[SQLAlchemyStorage, DEPENDS_STORAGE]):
    """
    DROP SCHEMA public CASCADE; CREATE SCHEMA public;
    """

    async with storage.create_session() as session:
        await session.execute(text("DROP SCHEMA public CASCADE;"))
        await session.execute(text("CREATE SCHEMA public;"))
        await session.commit()

    return {"success": True}
