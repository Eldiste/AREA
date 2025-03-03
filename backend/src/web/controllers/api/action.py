from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.config import get_db_async_session
from src.db.models import Action
from src.schemas.action import ActionResponse

router = APIRouter(prefix="/api", tags=["API"])


@router.get("/actions", response_model=list[ActionResponse])
async def get_actions(session: AsyncSession = Depends(get_db_async_session)):
    result = await session.execute(select(Action))
    return result.scalars().all()
