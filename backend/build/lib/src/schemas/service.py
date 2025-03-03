from typing import Optional

from pydantic import BaseModel


class ServiceBase(BaseModel):
    name: str
    description: Optional[str] = None


class ServiceCreate(ServiceBase):
    pass


class ServiceUpdate(BaseModel):
    name: Optional[str]
    description: Optional[str]


class ServiceResponse(ServiceBase):
    id: int

    class Config:
        orm_mode = True
