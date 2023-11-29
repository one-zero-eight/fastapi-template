__all__ = ["authentication_backend"]

from sqladmin.authentication import AuthenticationBackend
from starlette.requests import Request

from src.api.dependencies import Dependencies
from src.api.exceptions import IncorrectCredentialsException
from src.config import settings
from src.modules.auth.repository import TokenRepository


class AdminAuth(AuthenticationBackend):
    async def login(self, request: Request) -> bool:
        form = await request.form()
        login = form.get("username")
        password = form.get("password")

        if not login or not password:
            return False

        auth_repository = Dependencies.get_auth_repository()
        try:
            user_id = await auth_repository.authenticate_user(login=login, password=password)
        except IncorrectCredentialsException:
            return False

        token = TokenRepository.create_access_token(user_id)
        request.session["access_token"] = token
        return True

    async def logout(self, request: Request) -> bool:
        # Usually you'd want to just clear the session
        request.session.clear()
        return True

    async def authenticate(self, request: Request) -> bool:
        # check token from Header
        bearer = request.headers.get("Authorization")

        # Bearer
        if not bearer:
            token = request.session.get("access_token")
            if not token:
                return False
        else:
            token = bearer.replace("Bearer ", "")

        verification_result = await TokenRepository.verify_access_token(token)

        if not verification_result:
            return False

        user = await Dependencies.get_user_repository().read(verification_result.user_id)

        if not user or not user.is_admin:
            return False

        return True


authentication_backend = AdminAuth(secret_key=settings.session_secret_key.get_secret_value())
