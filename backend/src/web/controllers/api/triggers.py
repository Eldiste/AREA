import logging

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.auth.config import get_current_user
from src.config import get_db_async_session
from src.db.models import Area, Trigger, User
from src.schemas.trigger import TriggerCreate, TriggerResponse

router = APIRouter(prefix="/api", tags=["API"])
LOGGER = logging.getLogger(__name__)


@router.get("/triggers", response_model=list[TriggerResponse])
async def get_triggers(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_async_session),
):
    result = await session.execute(
        select(Trigger)
        .join(Trigger.area)  # Join with Area table
        .where(Area.user_id == current_user.id)  # Restrict to user's areas
        .options(selectinload(Trigger.area))
    )
    return result.scalars().all()


import json


@router.post("/triggers", response_model=TriggerResponse)
async def create_trigger(
    trigger: TriggerCreate,
    session: AsyncSession = Depends(get_db_async_session),
    current_user=Depends(get_current_user),
):
    LOGGER.info(f"Received trigger data: {json.dumps(trigger.dict(), indent=2)}")

    # Ensure the area belongs to the current user
    result = await session.execute(
        select(Area).where(Area.id == trigger.area_id, Area.user_id == current_user.id)
    )
    area = result.scalar_one_or_none()
    if not area:
        raise HTTPException(
            status_code=404, detail="Area not found or not owned by the user"
        )

    new_trigger = Trigger(**trigger.dict())
    session.add(new_trigger)
    await session.commit()
    await session.refresh(new_trigger)
    return new_trigger
