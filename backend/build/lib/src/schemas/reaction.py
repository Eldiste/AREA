from typing import Optional

from pydantic import BaseModel


class ReactionBase(BaseModel):
    name: str
    description: Optional[str] = None
    service_id: int


class ReactionCreate(ReactionBase):
    pass


class ReactionUpdate(BaseModel):
    name: Optional[str]
    description: Optional[str]


class ReactionResponse(ReactionBase):
    id: int

    class Config:
        orm_mode = True
