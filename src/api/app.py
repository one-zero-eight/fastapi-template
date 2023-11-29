__all__ = ["app"]

from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from starlette.responses import RedirectResponse

from src.api import docs
from src.api.docs import generate_unique_operation_id
from src.api.routers import routers
from src.api.startup import setup_repositories
from src.config import settings
from src.config_schema import Environment

# App definition
app = FastAPI(
    title=docs.TITLE,
    summary=docs.SUMMARY,
    description=docs.DESCRIPTION,
    version=docs.VERSION,
    contact=docs.CONTACT_INFO,
    license_info=docs.LICENSE_INFO,
    openapi_tags=docs.TAGS_INFO,
    servers=[
        {"url": settings.APP_ROOT_PATH, "description": "Current"},
    ],
    root_path=settings.APP_ROOT_PATH,
    root_path_in_servers=False,
    swagger_ui_oauth2_redirect_url=None,
    generate_unique_id_function=generate_unique_operation_id,
)

# Static files
if settings.STATIC_FILES is not None:
    from starlette.staticfiles import StaticFiles

    app.mount(
        settings.STATIC_FILES.MOUNT_PATH,
        StaticFiles(directory=settings.STATIC_FILES.DIRECTORY),
        name=settings.STATIC_FILES.MOUNT_NAME,
    )

# CORS settings
if settings.CORS_ALLOW_ORIGINS:
    app.add_middleware(
        middleware_class=CORSMiddleware,
        allow_origins=settings.CORS_ALLOW_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

# Mock utilities
if settings.ENVIRONMENT == Environment.DEVELOPMENT:
    from fastapi_mock import MockUtilities

    MockUtilities(app, return_example_instead_of_500=True)


@app.on_event("startup")
async def startup_event():
    await setup_repositories()

    # Admin panel
    if settings.ADMIN_PANEL is not None:
        from src.api.startup import setup_admin_panel

        setup_admin_panel(app)


@app.on_event("shutdown")
async def close_connection():
    from src.api.dependencies import Dependencies

    storage = Dependencies.get_storage()
    await storage.close_connection()


# Redirect root to docs
@app.get("/", tags=["Root"], include_in_schema=False)
async def redirect_to_docs():
    return RedirectResponse(url="/docs")


for router in routers:
    app.include_router(router)
