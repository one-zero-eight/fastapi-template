__all__ = ["VerificationResult", "AuthResult", "AuthCredentials", "UserCredentialsFromDB"]

from typing import Optional

from pydantic import BaseModel


class VerificationResult(BaseModel):
    success: bool
    user_id: Optional[int] = None


class AuthResult(BaseModel):
    success: bool
    token: Optional[str] = None


class AuthCredentials(BaseModel):
    login: str
    password: str


class UserCredentialsFromDB(BaseModel):
    user_id: int
    password_hash: str
