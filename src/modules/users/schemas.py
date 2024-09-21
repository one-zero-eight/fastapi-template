__all__ = ["CreateUser"]

from src.pydantic_base import BaseSchema


class CreateUser(BaseSchema):
    innohassle_id: str
    email: str
    name: str | None = None
