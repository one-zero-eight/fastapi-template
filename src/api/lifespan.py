__all__ = ["lifespan"]

from contextlib import asynccontextmanager

from fastapi import FastAPI

from src.api.dependencies import Dependencies
from src.config import settings
from src.config_schema import Environment
from src.modules.auth.repository import AuthRepository
from src.modules.user.repository import UserRepository
from src.storages.sqlalchemy.storage import SQLAlchemyStorage


async def setup_repositories():
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


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Application startup

    await setup_repositories()
    await setup_predefined()

    setup_admin_panel(app)

    yield

    # Application shutdown
    from src.api.dependencies import Dependencies

    storage = Dependencies.get_storage()
    await storage.close_connection()
