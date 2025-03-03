from http.client import HTTPException

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.config import get_db_async_session
from src.db.models import Area, Service
from src.schemas.area import AreaCreate, AreaResponse

router = APIRouter(prefix="/api", tags=["API"])

from fastapi import Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.auth.config import get_current_user
from src.db.models import Area
from src.schemas.area import AreaCreate, AreaResponse


@router.get("/areas", response_model=list[AreaResponse])
async def get_areas(
    session: AsyncSession = Depends(get_db_async_session),
    current_user=Depends(get_current_user),
):
    result = await session.execute(
        select(Area)
        .where(Area.user_id == current_user.id)
        .options(selectinload(Area.trigger))
    )
    return result.scalars().all()


@router.post("/areas", response_model=AreaResponse)
async def create_area(
    area: AreaCreate,
    session: AsyncSession = Depends(get_db_async_session),
    current_user=Depends(get_current_user),
):
    new_area = Area(user_id=current_user.id, **area.dict())
    session.add(new_area)
    await session.commit()
    await session.refresh(new_area)
    return AreaResponse.from_orm(new_area)


@router.get("/areas/{area_id}", response_model=AreaResponse)
async def get_area(
    area_id: int,
    session: AsyncSession = Depends(get_db_async_session),
    current_user=Depends(get_current_user),
):
    result = await session.execute(
        select(Area)
        .where(Area.id == area_id, Area.user_id == current_user.id)
        .options(selectinload(Area.trigger))
    )
    area = result.scalar_one_or_none()
    if not area:
        raise HTTPException(status_code=404, detail="Area not found")
    return AreaResponse.from_orm(area)


@router.put("/areas/{area_id}", response_model=AreaResponse)
async def update_area(
    area_id: int,
    area: AreaCreate,
    session: AsyncSession = Depends(get_db_async_session),
    current_user=Depends(get_current_user),
):
    result = await session.execute(
        select(Area).where(Area.id == area_id, Area.user_id == current_user.id)
    )
    existing_area = result.scalar_one_or_none()
    if not existing_area:
        raise HTTPException(status_code=404, detail="Area not found")
    for key, value in area.dict().items():
        setattr(existing_area, key, value)
    await session.commit()
    await session.refresh(existing_area)
    return AreaResponse.from_orm(existing_area)


@router.delete("/areas/{area_id}")
async def delete_area(
    area_id: int,
    session: AsyncSession = Depends(get_db_async_session),
    current_user=Depends(get_current_user),
):
    result = await session.execute(
        select(Area).where(Area.id == area_id, Area.user_id == current_user.id)
    )
    area = result.scalar_one_or_none()
    if not area:
        raise HTTPException(status_code=404, detail="Area not found")
    await session.delete(area)
    await session.commit()
    return {"status": "success"}
