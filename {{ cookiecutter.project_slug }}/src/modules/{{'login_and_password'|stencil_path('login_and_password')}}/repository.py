__all__ = ["LoginPasswordRepository", "login_password_repository"]

from src.modules.users.schemas import UserAuthData
from src.modules.users.repository import user_repository

from passlib.context import CryptContext


class LoginPasswordRepository:
    PWD_CONTEXT = CryptContext(schemes=["bcrypt"])

    @classmethod
    def get_password_hash(cls, password: str) -> str:
        return cls.PWD_CONTEXT.hash(password)

    async def verify_credentials(self, login: str, password: str) -> UserAuthData | None:
        user = await user_repository.read_id_and_password_hash(login)

        if user is None:
            return None
        user_id, password_hash = user

        password_verified = self.PWD_CONTEXT.verify(password, password_hash)
        if not password_verified:
            return None

        return UserAuthData(user_id=user_id)


login_password_repository: LoginPasswordRepository = LoginPasswordRepository()
