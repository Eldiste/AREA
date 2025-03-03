from typing import Optional

from pydantic import BaseModel, EmailStr


class UserBase(BaseModel):
    id: int
    username: str
    email: EmailStr
    is_active: bool
    is_admin: bool

    class Config:
        orm_mode = True


class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str


class UserUpdate(BaseModel):
    username: Optional[str]
    email: Optional[EmailStr]
    password: Optional[str]
    is_active: Optional[bool]
    is_admin: Optional[bool]


class UserResponse(UserBase):
    pass
