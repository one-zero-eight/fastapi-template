import re

from fastapi.routing import APIRoute

from src.config import settings


async def setup_repositories():
    from src.repositories.users import UserRepository
    from src.storages.sqlalchemy import SQLAlchemyStorage
    from src.app.dependencies import Dependencies

    # ------------------- Repositories Dependencies -------------------
    storage = SQLAlchemyStorage.from_url(settings.DB_URL.get_secret_value())
    user_repository = UserRepository(storage)

    Dependencies.set_storage(storage)
    Dependencies.set_user_repository(user_repository)

    await storage.create_all()


def generate_unique_operation_id(route: APIRoute) -> str:
    # Better names for operationId in OpenAPI schema.
    # It is needed because clients generate code based on these names.
    # Requires pair (tag name + function name) to be unique.
    # See fastapi.utils:generate_unique_id (default implementation).
    operation_id = f"{route.tags[0]}_{route.name}".lower()
    operation_id = re.sub(r"\W+", "_", operation_id)
    return operation_id
