from typing import Optional

from pydantic import BaseModel, EmailStr


class UserBase(BaseModel):
    username: str
    email: EmailStr


class UserCreate(BaseModel):
    username: str
    email: str
    password: str = None


class UserUpdate(BaseModel):
    username: Optional[str]
    email: Optional[EmailStr]
    password: Optional[str]
    is_active: Optional[bool]
    is_admin: Optional[bool]


class UserResponse(UserBase):
    id: int
    is_active: bool
    is_admin: bool

    class Config:
        from_attributes = True
