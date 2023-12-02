__all__ = ["models"]

from sqladmin import ModelView
from starlette.requests import Request

from src.api.dependencies import Dependencies
from src.storages.sqlalchemy.models import User


class CustomUserModelView(ModelView):
    async def on_model_change(self, data: dict, model: User, is_created: bool, request: Request) -> None:
        # get password from form
        password = data.get("password_hash")

        if password is None:
            return

        # hash password
        hashed_password = Dependencies.get_auth_repository().get_password_hash(password)

        data["password_hash"] = hashed_password


class UserView(CustomUserModelView, model=User):
    form_columns = [
        "login",
        "password_hash",
    ]
    form_args = {"password_hash": {"label": "Пароль"}}

    column_details_exclude_list = ["password_hash"]
    column_exclude_list = ["password_hash"]

    icon = "fa-solid fa-user"


models = [UserView]
