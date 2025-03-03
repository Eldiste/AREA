from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class UserServiceBase(BaseModel):
    user_id: int
    service_id: int


class UserServiceCreate(UserServiceBase):
    access_token: Optional[str] = None
    refresh_token: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class UserServiceUpdate(BaseModel):
    access_token: Optional[str]
    refresh_token: Optional[str]


class UserServiceResponse(UserServiceBase):
    id: int
    access_token: Optional[str]
    refresh_token: Optional[str]

    class Config:
        from_attributes = True
