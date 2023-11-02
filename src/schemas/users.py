__all__ = ["ViewUser", "CreateUser"]

from pydantic import BaseModel, ConfigDict, EmailStr


class ViewUser(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: str
    name: str


class CreateUser(BaseModel):
    email: EmailStr
    name: str
