from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.config import get_db_async_session
from src.db.models import Reaction
from src.schemas.reaction import ReactionResponse

router = APIRouter(prefix="/api", tags=["API"])


@router.get("/reactions", response_model=list[ReactionResponse])
async def get_reactions(session: AsyncSession = Depends(get_db_async_session)):
    result = await session.execute(select(Reaction))
    return result.scalars().all()
