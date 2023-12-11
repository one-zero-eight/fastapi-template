__all__ = ["lifespan"]

from contextlib import asynccontextmanager

from fastapi import FastAPI
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.shared import Shared
from src.config import settings
from src.config_schema import Environment
from src.modules.auth.repository import AuthRepository
from src.modules.user.repository import UserRepository
from src.storages.sqlalchemy.storage import SQLAlchemyStorage


async def setup_repositories():
    # ------------------- Repositories Dependencies -------------------
    storage = SQLAlchemyStorage(settings.database.get_async_engine())
    user_repository = UserRepository()
    auth_repository = AuthRepository()

    Shared.register_provider(AuthRepository, auth_repository)
    Shared.register_provider(SQLAlchemyStorage, storage)
    Shared.register_provider(UserRepository, user_repository)
    Shared.register_provider(AsyncSession, lambda: storage.create_session())

    if settings.environment == Environment.DEVELOPMENT:
        import logging

        logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
        logging.info("SQLAlchemy logging is enabled!")


def setup_admin_panel(app: FastAPI):
    from src.modules.admin.app import init_app

    init_app(app, settings.database.get_async_engine())


async def setup_predefined():
    user_repository = Shared.f(UserRepository)
    async with Shared.f(AsyncSession) as session:
        if not await user_repository.read_by_login(settings.predefined.first_superuser_login, session):
            await user_repository.create_superuser(
                login=settings.predefined.first_superuser_login,
                password=settings.predefined.first_superuser_password,
                session=session,
            )


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Application startup

    await setup_repositories()
    await setup_predefined()

    setup_admin_panel(app)

    yield

    # Application shutdown
    from src.api.shared import Shared

    storage = Shared.f(SQLAlchemyStorage)
    await storage.close_connection()
