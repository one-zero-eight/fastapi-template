from datetime import datetime, timedelta, timezone

from starlette.datastructures import URL
from starlette.responses import RedirectResponse

from src.api.exceptions import InvalidRedirectUri
from src.config import settings


def redirect_with_token(return_to: str, token: str):
    response = RedirectResponse(return_to, status_code=302)

    if settings.cookie:
        response.set_cookie(
            key=settings.cookie.name,
            value=token,
            httponly=True,
            secure=True,
            domain=settings.cookie.domain,
            expires=datetime.now().astimezone(tz=timezone.utc) + timedelta(days=90),
        )
    return response


def redirect_deleting_token(return_to: str):
    response = RedirectResponse(return_to, status_code=302)
    if settings.cookie:
        response.delete_cookie(
            key=settings.cookie.name,
            httponly=True,
            secure=True,
            domain=settings.cookie.domain,
        )
    return response


def ensure_allowed_return_to(return_to: str):
    try:
        url = URL(return_to)
        if url.hostname is None:
            return  # Ok. Allow returning to current domain
        if settings.cookie and url.hostname in settings.cookie.allowed_domains:
            return  # Ok. Hostname is allowed (does not check port)
    except (AssertionError, ValueError):
        pass  # Bad. URL is malformed
    raise InvalidRedirectUri()
