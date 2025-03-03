from typing import Optional

from pydantic import BaseModel


class UserServiceBase(BaseModel):
    user_id: int
    service_id: int


class UserServiceCreate(UserServiceBase):
    access_token: Optional[str] = None
    refresh_token: Optional[str] = None


class UserServiceUpdate(BaseModel):
    access_token: Optional[str]
    refresh_token: Optional[str]


class UserServiceResponse(UserServiceBase):
    id: int
    access_token: Optional[str]
    refresh_token: Optional[str]

    class Config:
        orm_mode = True
