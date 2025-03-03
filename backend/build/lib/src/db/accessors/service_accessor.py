from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import Session

from src.db.models.service import Service
from src.schemas.service import ServiceCreate, ServiceResponse, ServiceUpdate


class SyncServiceAccessor:
    @staticmethod
    def create_service(
        session: Session, service_data: ServiceCreate
    ) -> ServiceResponse:
        new_service = Service(**service_data.dict())
        session.add(new_service)
        session.commit()
        session.refresh(new_service)
        return ServiceResponse.from_orm(new_service)

    @staticmethod
    def get_service_by_id(
        session: Session, service_id: int
    ) -> Optional[ServiceResponse]:
        service = session.query(Service).filter(Service.id == service_id).first()
        if service:
            return ServiceResponse.from_orm(service)
        return None

    @staticmethod
    def update_service(
        session: Session, service_id: int, service_data: ServiceUpdate
    ) -> Optional[ServiceResponse]:
        service = session.query(Service).filter(Service.id == service_id).first()
        if not service:
            return None

        update_data = service_data.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(service, key, value)

        session.commit()
        session.refresh(service)
        return ServiceResponse.from_orm(service)

    @staticmethod
    def delete_service(session: Session, service_id: int) -> bool:
        service = session.query(Service).filter(Service.id == service_id).first()
        if not service:
            return False

        session.delete(service)
        session.commit()
        return True


class AsyncServiceAccessor:
    @staticmethod
    async def create_service(
        session: AsyncSession, service_data: ServiceCreate
    ) -> ServiceResponse:
        new_service = Service(**service_data.dict())
        session.add(new_service)
        await session.commit()
        await session.refresh(new_service)
        return ServiceResponse.from_orm(new_service)

    @staticmethod
    async def get_service_by_id(
        session: AsyncSession, service_id: int
    ) -> Optional[ServiceResponse]:
        result = await session.execute(select(Service).where(Service.id == service_id))
        service = result.scalar_one_or_none()
        if service:
            return ServiceResponse.from_orm(service)
        return None

    @staticmethod
    async def update_service(
        session: AsyncSession, service_id: int, service_data: ServiceUpdate
    ) -> Optional[ServiceResponse]:
        result = await session.execute(select(Service).where(Service.id == service_id))
        service = result.scalar_one_or_none()
        if not service:
            return None

        update_data = service_data.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(service, key, value)

        await session.commit()
        await session.refresh(service)
        return ServiceResponse.from_orm(service)

    @staticmethod
    async def delete_service(session: AsyncSession, service_id: int) -> bool:
        result = await session.execute(select(Service).where(Service.id == service_id))
        service = result.scalar_one_or_none()
        if not service:
            return False

        await session.delete(service)
        await session.commit()
        return True
