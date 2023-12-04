import re

from fastapi.routing import APIRoute

# API version
VERSION = "0.1.0"

# Info for OpenAPI specification
TITLE = "FastAPI template"
SUMMARY = "FastAPI template for InNoHassle ecosystem."

DESCRIPTION = """
### About this project
"""

CONTACT_INFO = {
    "name": "one-zero-eight (Telegram)",
    "url": "https://t.me/one_zero_eight",
}

LICENSE_INFO = {
    "name": "MIT License",
    "identifier": "MIT",
}

TAGS_INFO = [
    {
        "name": "Users",
        "description": "User data and linking users with event groups.",
    },
]


def generate_unique_operation_id(route: APIRoute) -> str:
    # Better names for operationId in OpenAPI schema.
    # It is needed because clients generate code based on these names.
    # Requires pair (tag name + function name) to be unique.
    # See fastapi.utils:generate_unique_id (default implementation).
    if route.tags:
        operation_id = f"{route.tags[0]}_{route.name}".lower()
    else:
        operation_id = route.name.lower()
    operation_id = re.sub(r"\W+", "_", operation_id)
    return operation_id
