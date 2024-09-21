__all__ = ["CreateUser", "ViewUser"]


from src.pydantic_base import BaseSchema


class CreateUser(BaseSchema):
    innohassle_id: str
    email: str
    name: str | None = None


class ViewUser(BaseSchema):
    id: int
    innohassle_id: str
    email: str
    name: str | None = None
