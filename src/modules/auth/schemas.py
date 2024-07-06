__all__ = ["VerificationResult", "AuthResult", "AuthCredentials", "UserCredentialsFromDB"]

from beanie import PydanticObjectId
from pydantic import BaseModel, Field

from src.storages.mongo.users import UserRole


class VerificationResult(BaseModel):
    success: bool
    user_id: PydanticObjectId | None = None
    role: UserRole | None = None


class AuthResult(BaseModel):
    success: bool
    token: str | None = None


class AuthCredentials(BaseModel):
    login: str = Field("admin", description="User login")
    password: str = Field("admin", description="User password")


class UserCredentialsFromDB(BaseModel):
    user_id: PydanticObjectId
    password_hash: str
