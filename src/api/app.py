__all__ = ["app"]

from fastapi import FastAPI
from fastapi_swagger import patch_fastapi
from starlette.middleware.cors import CORSMiddleware

import src.logging_  # noqa: F401
from src.api import docs
from src.api.lifespan import lifespan
from src.api.routers import routers
from src.config import settings

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
app.add_middleware(
    CORSMiddleware,
    allow_origin_regex=settings.cors_allow_origin_regex,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

for router in routers:
    app.include_router(router)
