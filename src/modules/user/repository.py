__all__ = ["UserRepository", "user_repository"]

from beanie import PydanticObjectId

from src.modules.auth.repository import AuthRepository
from src.modules.user.schemas import ViewUser, CreateUser
from src.storages.mongo.users import User


# noinspection PyMethodMayBeStatic
class UserRepository:
    async def get_all(self) -> list[ViewUser]:
        users = await User.find_all().to_list()
        return [ViewUser.model_validate(user, from_attributes=True) for user in users]

    # ------------------ CRUD ------------------ #

    async def create(self, user: CreateUser) -> ViewUser:
        user_dict = user.model_dump(exclude={"password"})
        user_dict["password_hash"] = AuthRepository.get_password_hash(user.password)

        if await User.find({"login": user.login}).exists():
            raise ValueError("User with this login already exists")

        new_user = await User.model_validate(user_dict).insert()
        return ViewUser.model_validate(new_user, from_attributes=True)

    async def create_superuser(self, login: str, password: str) -> ViewUser:
        user_dict = {
            "login": login,
            "name": "Superuser",
            "password_hash": AuthRepository.get_password_hash(password),
            "role": "admin",
        }

        if await User.find({"login": login}).exists():
            raise ValueError("User with this login already exists")

        new_user = await User.model_validate(user_dict).insert()
        return ViewUser.model_validate(new_user, from_attributes=True)

    async def read(self, id_: PydanticObjectId) -> ViewUser | None:
        user = await User.get(id_)
        if user:
            return ViewUser.model_validate(user, from_attributes=True)

    async def read_by_login(self, login: str) -> ViewUser | None:
        user = await User.find_one({"login": login})
        if user:
            return ViewUser.model_validate(user, from_attributes=True)

    # ^^^^^^^^^^^^^^^^^^^ CRUD ^^^^^^^^^^^^^^^^^^^ #


user_repository: UserRepository = UserRepository()
