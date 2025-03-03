from typing import Optional

from pydantic import BaseModel, Field


class UserConnect(BaseModel):
    username_or_email: str = Field(..., description="Username or Email")
    password: str = Field(..., description="User's password")


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: Optional[str] = None
