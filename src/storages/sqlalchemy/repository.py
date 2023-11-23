__all__ = ["SQLAlchemyRepository"]

from sqlalchemy.ext.asyncio import AsyncSession

from src.storages.sqlalchemy import SQLAlchemyStorage


class SQLAlchemyRepository:
    storage: SQLAlchemyStorage

    def __init__(self, storage: SQLAlchemyStorage):
        self.storage = storage

    def _create_session(self) -> AsyncSession:
        return self.storage.create_session()
