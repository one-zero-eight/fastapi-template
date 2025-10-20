__all__ = ["LoginPasswordRepository", "login_password_repository"]

from src.modules.user.schemas import UserAuthData
from src.modules.user.repository import user_repository

import bcrypt


class LoginPasswordRepository:
    @classmethod
    def get_password_hash(cls, password: str) -> str:
        # Bcrypt has a maximum password length of 72 bytes
        password_bytes = password.encode('utf-8')[:72]
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password_bytes, salt)
        return hashed.decode('utf-8')

    async def verify_credentials(self, login: str, password: str) -> UserAuthData | None:
        user = await user_repository.read_id_and_password_hash(login)

        if user is None:
            return None
        user_id, password_hash = user

        # Apply same truncation for verification
        password_bytes = password.encode('utf-8')[:72]
        password_verified = bcrypt.checkpw(password_bytes, password_hash.encode('utf-8'))
        if not password_verified:
            return None

        return UserAuthData(user_id=user_id)


login_password_repository: LoginPasswordRepository = LoginPasswordRepository()
