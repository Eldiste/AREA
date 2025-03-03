from pydantic import BaseModel

from src.service.config.base import TriggersServiceConfig


class TriggerBase(BaseModel):
    area_id: int


class TriggerCreate(BaseModel):
    name: str
    area_id: int
    config: TriggersServiceConfig

    class Config:
        from_attributes = True


class TriggerUpdate(BaseModel):
    config: TriggersServiceConfig


class TriggerResponse(TriggerBase):
    id: int

    class Config:
        from_attributes = True
