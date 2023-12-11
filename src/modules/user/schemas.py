__all__ = ["ViewUser", "CreateUser"]

from pydantic import BaseModel, ConfigDict, Field

from src.storages.sqlalchemy.models.users import UserRole


class ViewUser(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
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
