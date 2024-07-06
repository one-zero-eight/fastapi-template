__all__ = ["ViewUser", "CreateUser"]

from beanie import PydanticObjectId
from pydantic import BaseModel, Field

from src.storages.mongo.users import UserRole


class ViewUser(BaseModel):
    id: PydanticObjectId
    login: str
    name: str
    password_hash: str = Field(exclude=True)
    role: UserRole = UserRole.DEFAULT

    @property
    def is_admin(self) -> bool:
        return self.role == UserRole.ADMIN


class CreateUser(BaseModel):
    login: str
    password: str
    name: str
