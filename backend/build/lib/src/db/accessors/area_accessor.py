from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import Session

from src.db.models.area import Area
from src.schemas.area import AreaCreate, AreaResponse, AreaUpdate


class SyncAreaAccessor:
    @staticmethod
    def create_area(session: Session, area_data: AreaCreate) -> AreaResponse:
        new_area = Area(**area_data.dict())
        session.add(new_area)
        session.commit()
        session.refresh(new_area)
        return AreaResponse.from_orm(new_area)

    @staticmethod
    def get_area_by_id(session: Session, area_id: int) -> Optional[AreaResponse]:
        area = session.query(Area).filter(Area.id == area_id).first()
        if area:
            return AreaResponse.from_orm(area)
        return None

    @staticmethod
    def update_area(
        session: Session, area_id: int, area_data: AreaUpdate
    ) -> Optional[AreaResponse]:
        area = session.query(Area).filter(Area.id == area_id).first()
        if not area:
            return None

        update_data = area_data.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(area, key, value)

        session.commit()
        session.refresh(area)
        return AreaResponse.from_orm(area)

    @staticmethod
    def delete_area(session: Session, area_id: int) -> bool:
        area = session.query(Area).filter(Area.id == area_id).first()
        if not area:
            return False

        session.delete(area)
        session.commit()
        return True


class AsyncAreaAccessor:
    @staticmethod
    async def create_area(session: AsyncSession, area_data: AreaCreate) -> AreaResponse:
        new_area = Area(**area_data.dict())
        session.add(new_area)
        await session.commit()
        await session.refresh(new_area)
        return AreaResponse.from_orm(new_area)

    @staticmethod
    async def get_area_by_id(
        session: AsyncSession, area_id: int
    ) -> Optional[AreaResponse]:
        result = await session.execute(select(Area).where(Area.id == area_id))
        area = result.scalar_one_or_none()
        if area:
            return AreaResponse.from_orm(area)
        return None

    @staticmethod
    async def update_area(
        session: AsyncSession, area_id: int, area_data: AreaUpdate
    ) -> Optional[AreaResponse]:
        result = await session.execute(select(Area).where(Area.id == area_id))
        area = result.scalar_one_or_none()
        if not area:
            return None

        update_data = area_data.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(area, key, value)

        await session.commit()
        await session.refresh(area)
        return AreaResponse.from_orm(area)

    @staticmethod
    async def delete_area(session: AsyncSession, area_id: int) -> bool:
        result = await session.execute(select(Area).where(Area.id == area_id))
        area = result.scalar_one_or_none()
        if not area:
            return False

        await session.delete(area)
        await session.commit()
        return True
