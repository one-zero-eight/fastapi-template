__all__ = ["VerificationResult", "AuthResult", "AuthCredentials", "UserCredentialsFromDB"]

from typing import Optional

from pydantic import BaseModel, Field


class VerificationResult(BaseModel):
    success: bool
    user_id: Optional[int] = None


class AuthResult(BaseModel):
    success: bool
    token: Optional[str] = None


class AuthCredentials(BaseModel):
    login: str = Field("admin", description="User login")
    password: str = Field("admin", description="User password")


class UserCredentialsFromDB(BaseModel):
    user_id: int
    password_hash: str
