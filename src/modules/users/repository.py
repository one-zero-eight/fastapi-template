__all__ = ["UserRepository", "user_repository"]

from src.modules.users.schemas import CreateUser
from src.storages.mongo.users import User


# noinspection PyMethodMayBeStatic
class UserRepository:
    async def create(self, user: CreateUser) -> User:
        created = User(**user.model_dump())
        return await created.insert()

    async def read(self, user_id: int) -> User | None:
        return await User.get(user_id)

    async def read_id_by_innohassle_id(self, innohassle_id: str) -> int | None:
        user = await User.find_one(User.innohassle_id == innohassle_id)
        return user.id if user else None


user_repository: UserRepository = UserRepository()
