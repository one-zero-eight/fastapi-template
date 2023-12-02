__all__ = ["init_app"]

import logging
from typing import Optional, Union, Sequence

from fastapi import FastAPI
from sqladmin import Admin

# noinspection PyProtectedMember
from sqladmin._types import ENGINE_TYPE
from sqladmin.authentication import AuthenticationBackend
from sqlalchemy import Engine
from sqlalchemy.ext.asyncio import AsyncEngine, async_sessionmaker
from sqlalchemy.orm import sessionmaker
from starlette.applications import Starlette
from starlette.middleware import Middleware
from starlette.routing import Mount, BaseRoute
from starlette.staticfiles import StaticFiles

from src.modules.admin.auth import authentication_backend
from src.modules.admin.views import models

from starlette.routing import Route


class CustomAdmin(Admin):
    def __init__(
        self,
        app: Starlette,
        engine: Optional[ENGINE_TYPE] = None,
        session_maker: Optional[Union[sessionmaker, "async_sessionmaker"]] = None,
        base_url: str = "/admin",
        title: str = "Admin",
        logo_url: Optional[str] = None,
        middlewares: Optional[Sequence[Middleware]] = None,
        debug: bool = False,
        templates_dir: str = "templates",
        authentication_backend: Optional[AuthenticationBackend] = None,
    ) -> None:
        super().__init__(
            app,
            engine,
            session_maker,
            base_url,
            title,
            logo_url,
            middlewares,
            debug,
            templates_dir,
            authentication_backend,
        )
        # Remount statics folder
        statics = StaticFiles(directory="src/modules/admin/statics", packages=["sqladmin"])
        routes: list[Route | BaseRoute] = self.admin.router.routes
        routes = [route for route in routes if route.name != "statics"]
        routes.append(Mount("/statics", app=statics, name="statics"))


def init_app(app: FastAPI, engine: Engine | AsyncEngine):
    admin = CustomAdmin(
        app,
        engine,
        authentication_backend=authentication_backend,
        templates_dir="src/modules/admin/templates",
    )

    for model in models:
        admin.add_view(model)

    logging.info(r"Admin panel is configured at /admin")
