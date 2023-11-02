__all__ = [
    "NoCredentialsException",
    "IncorrectCredentialsException",
    "NotEnoughPermissionsException",
    "InvalidRedirectUri",
    "UserNotFound",
    "ClientNotFound",
    "DBUserAlreadyExists",
]

from typing import Optional

from fastapi import HTTPException
from starlette import status


class NoCredentialsException(HTTPException):
    """
    HTTP_401_UNAUTHORIZED
    """

    def __init__(self):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=self.responses[401]["description"],
            headers={"WWW-Authenticate": "Bearer"},
        )

    responses = {
        401: {
            "description": "No credentials provided",
            "headers": {"WWW-Authenticate": {"schema": {"type": "string"}}},
        }
    }


class IncorrectCredentialsException(HTTPException):
    """
    HTTP_401_UNAUTHORIZED
    """

    def __init__(self):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=self.responses[401]["description"],
        )

    responses = {401: {"description": "Could not validate credentials"}}


class NotEnoughPermissionsException(HTTPException):
    """
    HTTP_403_FORBIDDEN
    """

    def __init__(self, authenticate_header: Optional[str] = None):
        if authenticate_header is None:
            super().__init__(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=self.responses[403]["description"],
            )
        else:
            super().__init__(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=self.responses[403]["description"],
                headers={"WWW-Authenticate": authenticate_header},
            )

    responses = {403: {"description": "Not enough permissions"}}


class InvalidRedirectUri(HTTPException):
    """
    HTTP_400_BAD_REQUEST
    """

    def __init__(self):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=self.responses[400]["description"],
        )

    responses = {400: {"description": "Invalid redirect_uri URL"}}


class UserNotFound(HTTPException):
    """
    HTTP_404_NOT_FOUND
    """

    def __init__(self):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=self.responses[404]["description"],
        )

    responses = {404: {"description": "User with this id not found"}}


class ClientNotFound(HTTPException):
    """
    HTTP_404_NOT_FOUND
    """

    def __init__(self):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=self.responses[404]["description"],
        )

    responses = {404: {"description": "Client with this id not found"}}


class DBUserAlreadyExists(ValueError):
    """
    Integration error with database: unique constraint failed
    """

    def __init__(self, **kwargs):
        if not kwargs:
            super().__init__("User already exists")
        else:
            super().__init__(f"User with {kwargs} already exists")
