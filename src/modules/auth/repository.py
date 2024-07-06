__all__ = ["TokenRepository", "AuthRepository", "auth_repository"]

import time
from datetime import timedelta, datetime, UTC

from authlib.jose import jwt, JoseError, JWTClaims
from beanie import PydanticObjectId
from passlib.context import CryptContext

from src.api.exceptions import IncorrectCredentialsException
from src.config import settings
from src.modules.auth.schemas import VerificationResult, UserCredentialsFromDB
from src.storages.mongo.users import User


class TokenRepository:
    ALGORITHM = "RS256"

    @classmethod
    def decode_token(cls, token: str) -> JWTClaims:
        now = time.time()
        payload = jwt.decode(token, settings.jwt_public_key)
        payload.validate_exp(now, leeway=0)
        payload.validate_iat(now, leeway=0)
        return payload

    @classmethod
    async def verify_access_token(cls, auth_token: str) -> VerificationResult:
        from src.modules.user.repository import user_repository

        try:
            payload = cls.decode_token(auth_token)
        except JoseError:
            return VerificationResult(success=False)

        user_id: str | None = payload.get("sub")

        if user_id is None or not PydanticObjectId.is_valid(user_id):
            return VerificationResult(success=False)

        converted_user_id = PydanticObjectId(user_id)

        user = await user_repository.read(converted_user_id)

        if user is None:
            return VerificationResult(success=False)

        return VerificationResult(success=True, user_id=converted_user_id, role=user.role)

    @classmethod
    def create_access_token(cls, user_id: PydanticObjectId) -> str:
        access_token = TokenRepository._create_access_token(
            data={"sub": str(user_id)},
            expires_delta=timedelta(days=1),
        )
        return access_token

    @classmethod
    def _create_access_token(cls, data: dict, expires_delta: timedelta) -> str:
        payload = data.copy()
        issued_at = datetime.now(UTC)
        expire = issued_at + expires_delta
        payload.update({"exp": expire, "iat": issued_at})
        encoded_jwt = jwt.encode({"alg": cls.ALGORITHM}, payload, settings.jwt_private_key.get_secret_value())
        return str(encoded_jwt, "utf-8")


class AuthRepository:
    PWD_CONTEXT = CryptContext(schemes=["bcrypt"])

    @classmethod
    def get_password_hash(cls, password: str) -> str:
        return cls.PWD_CONTEXT.hash(password)

    async def authenticate_user(self, login: str, password: str) -> PydanticObjectId:
        user_credentials = await self._get_user(login)
        if user_credentials is None:
            raise IncorrectCredentialsException()
        password_verified = await self.verify_password(password, user_credentials.password_hash)
        if not password_verified:
            raise IncorrectCredentialsException()
        return user_credentials.user_id

    async def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        return self.PWD_CONTEXT.verify(plain_password, hashed_password)

    async def _get_user(self, login: str) -> UserCredentialsFromDB | None:
        user = await User.find_one({"login": login})
        if user:
            return UserCredentialsFromDB(user_id=user.id, password_hash=user.password_hash)


auth_repository: AuthRepository = AuthRepository()
