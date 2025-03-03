from typing import Optional

from pydantic import BaseModel


class ActionBase(BaseModel):
    name: str
    description: Optional[str] = None
    service_id: int


class ActionCreate(ActionBase):
    pass


class ActionUpdate(BaseModel):
    name: Optional[str]
    description: Optional[str]


class ActionResponse(ActionBase):
    id: int

    class Config:
        from_attributes = True
