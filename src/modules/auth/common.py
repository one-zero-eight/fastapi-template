from datetime import datetime, timedelta, timezone

from starlette.datastructures import URL
from starlette.responses import RedirectResponse

from src.api.exceptions import InvalidRedirectUri
from src.config import settings


def redirect_with_token(return_to: str, token: str):
    response = RedirectResponse(return_to, status_code=302)

    if settings.COOKIE:
        response.set_cookie(
            key=settings.COOKIE.NAME,
            value=token,
            httponly=True,
            secure=True,
            domain=settings.COOKIE.DOMAIN,
            expires=datetime.now().astimezone(tz=timezone.utc) + timedelta(days=90),
        )
    return response


def redirect_deleting_token(return_to: str):
    response = RedirectResponse(return_to, status_code=302)
    if settings.COOKIE:
        response.delete_cookie(
            key=settings.COOKIE.NAME,
            httponly=True,
            secure=True,
            domain=settings.COOKIE.DOMAIN,
        )
    return response


def ensure_allowed_return_to(return_to: str):
    try:
        url = URL(return_to)
        if url.hostname is None:
            return  # Ok. Allow returning to current domain
        if settings.COOKIE and url.hostname in settings.COOKIE.ALLOWED_DOMAINS:
            return  # Ok. Hostname is allowed (does not check port)
    except (AssertionError, ValueError):
        pass  # Bad. URL is malformed
    raise InvalidRedirectUri()
