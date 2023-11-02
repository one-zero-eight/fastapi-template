__all__ = ["UserRepository"]

import random
from typing import Optional

from sqlalchemy import select, update, insert
from sqlalchemy.ext.asyncio import AsyncSession

from src.repositories.users.abc import AbstractUserRepository
from src.schemas.users import ViewUser, CreateUser
from src.storages.sqlalchemy.models import User
from src.storages.sqlalchemy.storage import AbstractSQLAlchemyStorage

MIN_USER_ID = 100_000
MAX_USER_ID = 999_999


async def _get_available_user_ids(session: AsyncSession, count: int = 1) -> list[int] | int:
    q = select(User.id)
    excluded_ids = set(await session.scalars(q))
    excluded_ids: set[int]
    available_ids = set()
    while len(available_ids) < count:
        chosen_id = random.randint(MIN_USER_ID, MAX_USER_ID)
        if chosen_id not in excluded_ids:
            available_ids.add(chosen_id)
    return list(available_ids) if count > 1 else available_ids.pop()


class UserRepository(AbstractUserRepository):
    storage: AbstractSQLAlchemyStorage

    def __init__(self, storage: AbstractSQLAlchemyStorage):
        self.storage = storage

    def _create_session(self) -> AsyncSession:
        return self.storage.create_session()

    # ------------------ CRUD ------------------ #

    async def create_or_update(self, user: CreateUser) -> ViewUser:
        async with self._create_session() as session:
            q = select(User).where(User.email == user.email)
            existing_user = await session.scalar(q)
            if existing_user:
                q = (
                    update(User)
                    .where(User.id == existing_user.id)
                    .values(**user.model_dump(exclude_unset=True))
                    .returning(User)
                )
                existing_user = await session.scalar(q)
                await session.commit()
                return ViewUser.model_validate(existing_user)
            else:
                user_id = await _get_available_user_ids(session)
                q = insert(User).values(id=user_id, **user.model_dump()).returning(User)
                new_user = await session.scalar(q)
                await session.commit()
                return ViewUser.model_validate(new_user)

    async def read(self, id_: int) -> Optional["ViewUser"]:
        async with self._create_session() as session:
            q = select(User).where(User.id == id_)
            user = await session.scalar(q)
            if user:
                return ViewUser.model_validate(user, from_attributes=True)

    async def read_by_email(self, email: str) -> Optional["ViewUser"]:
        async with self._create_session() as session:
            q = select(User).where(User.email == email)
            user = await session.scalar(q)
            if user:
                return ViewUser.model_validate(user, from_attributes=True)

    # ^^^^^^^^^^^^^^^^^^^ CRUD ^^^^^^^^^^^^^^^^^^^ #
