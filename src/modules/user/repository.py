__all__ = ["UserRepository"]

import random
from typing import Optional

from sqlalchemy import select, insert
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.shared import Shared
from src.modules.auth.repository import AuthRepository
from src.modules.user.schemas import ViewUser, CreateUser
from src.storages.sqlalchemy.models.users import User

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


class UserRepository:
    async def get_all(self, session: AsyncSession) -> list["ViewUser"]:
        q = select(User)
        users = await session.scalars(q)
        if users:
            return [ViewUser.model_validate(user, from_attributes=True) for user in users]

    # ------------------ CRUD ------------------ #

    async def create(self, user: CreateUser, session: AsyncSession) -> ViewUser:
        user_dict = user.model_dump(exclude={"password"})
        user_dict["id"] = await _get_available_user_ids(session)
        user_dict["password_hash"] = Shared.f(AuthRepository).get_password_hash(user.password)
        q = insert(User).values(user_dict).returning(User)
        new_user = await session.scalar(q)
        await session.commit()
        return ViewUser.model_validate(new_user)

    async def create_superuser(self, login: str, password: str, session: AsyncSession) -> ViewUser:
        user_dict = {
            "id": await _get_available_user_ids(session),
            "login": login,
            "name": "Superuser",
            "password_hash": Shared.f(AuthRepository).get_password_hash(password),
            "role": "admin",
        }

        q = insert(User).values(user_dict).returning(User)
        new_user = await session.scalar(q)
        await session.commit()
        return ViewUser.model_validate(new_user)

    async def read(self, id_: int, session: AsyncSession) -> Optional["ViewUser"]:
        q = select(User).where(User.id == id_)
        user = await session.scalar(q)
        if user:
            return ViewUser.model_validate(user, from_attributes=True)

    async def read_by_login(self, login: str, session: AsyncSession) -> Optional["ViewUser"]:
        q = select(User).where(User.login == login)
        user = await session.scalar(q)
        if user:
            return ViewUser.model_validate(user, from_attributes=True)

    # ^^^^^^^^^^^^^^^^^^^ CRUD ^^^^^^^^^^^^^^^^^^^ #
