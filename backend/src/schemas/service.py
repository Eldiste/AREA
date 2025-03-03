from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class ServiceBase(BaseModel):
    name: str
    description: Optional[str] = None


class ServiceCreate(ServiceBase):
    pass


class ServiceResponse(BaseModel):
    id: int
    name: str
    description: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda dt: dt.isoformat(),
        }
