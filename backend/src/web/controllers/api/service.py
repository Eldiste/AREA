from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.config import get_db_async_session
from src.db.models import Service
from src.schemas.service import ServiceResponse

router = APIRouter(prefix="/api", tags=["API"])


# This endpoint doesn't need any Auth
@router.get("/services", response_model=List[ServiceResponse])
async def get_services(session: AsyncSession = Depends(get_db_async_session)):
    result = await session.execute(select(Service))
    services = result.scalars().all()
    return services
