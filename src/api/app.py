__all__ = ["app"]

from fastapi import FastAPI, Request
from fastapi.openapi.docs import get_swagger_ui_html
from starlette.middleware.cors import CORSMiddleware
from starlette.responses import RedirectResponse, FileResponse

import src.api.logging_  # noqa: F401
from src.api.docs import generate_unique_operation_id, custom_openapi
from src.api.lifespan import lifespan
from src.api.routers import routers
from src.config import settings
from src.config_schema import Environment

# App definition
app = FastAPI(
    root_path=settings.app_root_path,
    root_path_in_servers=False,
    generate_unique_id_function=generate_unique_operation_id,
    lifespan=lifespan,
    docs_url=None,
    redoc_url=None,
    swagger_ui_oauth2_redirect_url=None,
)

app.openapi = custom_openapi(app)  # type: ignore

# Static files
if settings.static_files is not None:
    from starlette.staticfiles import StaticFiles

    app.mount(
        settings.static_files.mount_path,
        StaticFiles(directory=settings.static_files.directory),
        name=settings.static_files.mount_name,
    )

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


# Redirect root to docs
@app.get("/", tags=["Root"], include_in_schema=False)
async def redirect_to_docs(request: Request):
    return RedirectResponse(url=request.url_for("swagger_ui_html"))


# noinspection PyUnresolvedReferences
@app.get("/docs", tags=["System"], include_in_schema=False)
async def swagger_ui_html(request: Request):
    root_path = request.scope.get("root_path", "").rstrip("/")

    openapi_url = root_path + app.openapi_url
    swagger_js_url = request.url_for("swagger_ui_bundle")
    swagger_css_url = request.url_for("swagger_ui_css")
    swagger_favicon_url = request.url_for("swagger_favicon")

    return get_swagger_ui_html(
        openapi_url=openapi_url,
        title=app.title + " - Swagger UI",
        swagger_js_url=str(swagger_js_url),
        swagger_css_url=str(swagger_css_url),
        swagger_favicon_url=str(swagger_favicon_url),
        swagger_ui_parameters={"tryItOutEnabled": True, "persistAuthorization": True, "filter": True},
    )


@app.get("/swagger/favicon.png", tags=["System"], include_in_schema=False, response_class=FileResponse)
async def swagger_favicon() -> FileResponse:
    return FileResponse("src/swagger/favicon.png")


@app.get("/swagger/swagger-ui-bundle.js", tags=["System"], include_in_schema=False, response_class=FileResponse)
async def swagger_ui_bundle() -> FileResponse:
    return FileResponse("src/swagger/swagger-ui-bundle.js")


@app.get("/swagger/swagger-ui.css", tags=["System"], include_in_schema=False, response_class=FileResponse)
async def swagger_ui_css() -> FileResponse:
    return FileResponse("src/swagger/swagger-ui.css")


for router in routers:
    app.include_router(router)
