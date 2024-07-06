__all__ = ["lifespan"]

import asyncio
import json
from contextlib import asynccontextmanager

from beanie import init_beanie
from fastapi import FastAPI
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import timeout
from pymongo.errors import ConnectionFailure

from src.config import settings
from src.logging_ import logger
from src.modules.user.repository import user_repository
from src.storages.mongo import document_models


async def setup_database() -> AsyncIOMotorClient:
    motor_client: AsyncIOMotorClient = AsyncIOMotorClient(
        settings.database.uri.get_secret_value(),
        connectTimeoutMS=5000,
        serverSelectionTimeoutMS=5000,
        tz_aware=True,
    )
    motor_client.get_io_loop = asyncio.get_running_loop  # type: ignore[method-assign]

    # healthcheck mongo
    try:
        with timeout(2):
            server_info = await motor_client.server_info()
            server_info_pretty_text = json.dumps(server_info, indent=2, default=str)
            logger.info(f"Connected to MongoDB: {server_info_pretty_text}")
    except ConnectionFailure as e:
        logger.critical("Could not connect to MongoDB: %s" % e)
        raise e

    mongo_db = motor_client.get_database()
    await init_beanie(database=mongo_db, document_models=document_models, recreate_views=True)
    return motor_client


async def setup_predefined():
    if not await user_repository.read_by_login(settings.predefined.first_superuser_login):
        await user_repository.create_superuser(
            login=settings.predefined.first_superuser_login, password=settings.predefined.first_superuser_password
        )


@asynccontextmanager
async def lifespan(_app: FastAPI):
    # Application startup
    motor_client = await setup_database()
    await setup_predefined()
    yield

    # -- Application shutdown --
    motor_client.close()
