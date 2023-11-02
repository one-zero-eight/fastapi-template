__all__ = ["TokenRepository"]

from datetime import timedelta, datetime

from authlib.jose import jwt, JoseError

from src.app.dependencies import Dependencies
from src.config import settings
from src.exceptions import IncorrectCredentialsException, UserNotFound
from src.repositories.tokens.abc import AbstractTokenRepository
from src.schemas.tokens import UserTokenData


class TokenRepository(AbstractTokenRepository):
    ALGORITHM = "RS256"

    @classmethod
    async def verify_user_token(cls, token: str) -> UserTokenData:
        try:
            user_repository = Dependencies.get_user_repository()
            payload = jwt.decode(token, settings.JWT_PUBLIC_KEY)
            user_id: str = payload.get("sub")

            if user_id is None or not user_id.isdigit():
                raise IncorrectCredentialsException()

            converted_user_id = int(user_id)

            if await user_repository.read(converted_user_id) is None:
                raise UserNotFound()

            token_data = UserTokenData(user_id=converted_user_id)
            return token_data
        except JoseError:
            raise IncorrectCredentialsException()

    @classmethod
    def _create_access_token(cls, data: dict, expires_delta: timedelta) -> str:
        payload = data.copy()
        issued_at = datetime.utcnow()
        expire = issued_at + expires_delta
        payload.update({"exp": expire, "iat": issued_at})
        encoded_jwt = jwt.encode({"alg": cls.ALGORITHM}, payload, settings.JWT_PRIVATE_KEY)
        return str(encoded_jwt, "utf-8")

    @classmethod
    def create_access_token(cls, user_id: int) -> str:
        data = {"sub": str(user_id)}
        access_token = TokenRepository._create_access_token(
            data=data,
            expires_delta=timedelta(days=90),
        )
        return access_token
