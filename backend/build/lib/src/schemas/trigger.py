from pydantic import BaseModel


class TriggerBase(BaseModel):
    area_id: int
    config: dict


class TriggerCreate(TriggerBase):
    pass


class TriggerUpdate(BaseModel):
    config: dict


class TriggerResponse(TriggerBase):
    id: int

    class Config:
        orm_mode = True
