from typing import Optional

from pydantic import BaseModel


class AreaBase(BaseModel):
    user_id: int
    action_id: int
    reaction_id: int


class AreaCreate(AreaBase):
    pass


class AreaUpdate(BaseModel):
    action_id: Optional[int]
    reaction_id: Optional[int]


class AreaResponse(AreaBase):
    id: int

    class Config:
        orm_mode = True
