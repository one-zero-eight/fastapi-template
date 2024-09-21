__all__ = ["SqlUserRepository", "user_repository"]

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.modules.users.schemas import CreateUser, ViewUser
from src.storages.sql.models import User


class SqlUserRepository:
    def _create_session(self) -> AsyncSession:
        from src.storages.sql.storage import storage

        return storage.create_session()

    async def create(self, user: CreateUser) -> ViewUser:
        async with self._create_session() as session:
            created = User(**user.model_dump())
            session.add(created)
            await session.commit()
            return ViewUser.model_validate(created, from_attributes=True)

    async def read(self, user_id: int) -> ViewUser:
        async with self._create_session() as session:
            user = await session.get(User, user_id)
            return ViewUser.model_validate(user, from_attributes=True)

    async def read_id_by_innohassle_id(self, innohassle_id: str) -> int | None:
        async with self._create_session() as session:
            user_id = await session.scalar(select(User.id).where(User.innohassle_id == innohassle_id))
            return user_id


user_repository: SqlUserRepository = SqlUserRepository()
