__all__ = [
    "setup_repositories",
    "setup_admin_panel",
    "setup_predefined",
]

from fastapi import FastAPI

from src.api.dependencies import Dependencies
from src.config import settings
from src.config_schema import Environment
from src.modules.auth.repository import AuthRepository


async def setup_repositories():
    from src.modules.users.repository import UserRepository
    from src.storages.sqlalchemy.storage import SQLAlchemyStorage

    # ------------------- Repositories Dependencies -------------------
    storage = SQLAlchemyStorage(settings.database.get_async_engine())
    user_repository = UserRepository(storage)
    auth_repository = AuthRepository(storage)

    Dependencies.set_auth_repository(auth_repository)
    Dependencies.set_storage(storage)
    Dependencies.set_user_repository(user_repository)

    if settings.environment == Environment.DEVELOPMENT:
        import logging

        logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
        logging.info("SQLAlchemy logging is enabled!")


def setup_admin_panel(app: FastAPI):
    from src.modules.admin.app import init_app

    init_app(app, settings.database.get_async_engine())


async def setup_predefined():
    user_repository = Dependencies.get_user_repository()
    if not await user_repository.read_by_login(settings.predefined.first_superuser_login):
        await user_repository.create_superuser(
            login=settings.predefined.first_superuser_login,
            password=settings.predefined.first_superuser_password,
        )
