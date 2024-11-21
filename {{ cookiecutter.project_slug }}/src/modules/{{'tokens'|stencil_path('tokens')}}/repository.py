__all__ = ["TokenRepository"]

import time

from authlib.jose import JoseError, JWTClaims, jwt

from src.modules.innohassle_accounts import innohassle_accounts
from src.modules.users.repository import user_repository
from src.modules.users.schemas import CreateUser, UserAuthData


class TokenRepository:
    @classmethod
    def decode_token(cls, token: str) -> JWTClaims:
        now = time.time()
        pub_key = innohassle_accounts.get_public_key()
        payload = jwt.decode(token, pub_key)
        payload.validate_exp(now, leeway=0)
        payload.validate_iat(now, leeway=0)
        return payload

    @classmethod
    async def _fetch_user_id_or_create(cls, innohassle_id: str):
        user_id = await user_repository.read_id_by_innohassle_id(innohassle_id)
        if user_id is not None:
            return user_id

        innohassle_user = await innohassle_accounts.get_user_by_id(innohassle_id)
        if innohassle_user is None:
            return None

        user = CreateUser(
            innohassle_id=innohassle_id,
            email=innohassle_user.innopolis_sso.email,
            name=innohassle_user.innopolis_sso.name,
        )
        user_id = (await user_repository.create(user)).id
        return user_id

    @classmethod
    async def verify_user_token(cls, token: str, credentials_exception) -> UserAuthData:
        try:
            payload = cls.decode_token(token)
            innohassle_id: str = payload.get("uid")
            if innohassle_id is None:
                raise credentials_exception
            user_id = await cls._fetch_user_id_or_create(innohassle_id)
            if user_id is None:
                raise credentials_exception
            return UserAuthData(user_id=user_id, innohassle_id=innohassle_id)
        except JoseError:
            raise credentials_exception
