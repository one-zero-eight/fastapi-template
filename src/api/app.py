__all__ = ["app"]

from fastapi import FastAPI
from fastapi_swagger import patch_fastapi
from starlette.middleware.cors import CORSMiddleware

import src.logging_  # noqa: F401
from src.api import docs
from src.api.lifespan import lifespan
from src.config import settings
from src.config_schema import Environment

# App definition
app = FastAPI(
    root_path=settings.app_root_path,
    root_path_in_servers=False,
    version=docs.VERSION,
    title=docs.TITLE,
    summary=docs.SUMMARY,
    description=docs.DESCRIPTION,
    contact=docs.CONTACT_INFO,
    license_info=docs.LICENSE_INFO,
    generate_unique_id_function=docs.generate_unique_operation_id,
    lifespan=lifespan,
    docs_url=None,
    redoc_url=None,
    swagger_ui_oauth2_redirect_url=None,
)
patch_fastapi(app)

# CORS settings
if settings.cors_allow_origins:
    # noinspection PyTypeChecker
    app.add_middleware(
        middleware_class=CORSMiddleware,
        allow_origins=settings.cors_allow_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
        allow_origin_regex=".*" if settings.environment == Environment.DEVELOPMENT else None,
    )

from src.modules.users.routes import router as router_users  # noqa: E402

app.include_router(router_users)
