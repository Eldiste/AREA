from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import Session

from src.db.models.user_service import UserService
from src.schemas.user_service import (
    UserServiceCreate,
    UserServiceResponse,
    UserServiceUpdate,
)


class SyncUserServiceAccessor:
    @staticmethod
    def create_user_service(
        session: Session, user_service_data: UserServiceCreate
    ) -> UserServiceResponse:
        new_user_service = UserService(**user_service_data.dict())
        session.add(new_user_service)
        session.commit()
        session.refresh(new_user_service)
        return UserServiceResponse.from_orm(new_user_service)

    @staticmethod
    def get_user_service_by_id(
        session: Session, user_service_id: int
    ) -> Optional[UserServiceResponse]:
        user_service = (
            session.query(UserService).filter(UserService.id == user_service_id).first()
        )
        if user_service:
            return UserServiceResponse.from_orm(user_service)
        return None

    @staticmethod
    def update_user_service(
        session: Session, user_service_id: int, user_service_data: UserServiceUpdate
    ) -> Optional[UserServiceResponse]:
        user_service = (
            session.query(UserService).filter(UserService.id == user_service_id).first()
        )
        if not user_service:
            return None

        update_data = user_service_data.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(user_service, key, value)

        session.commit()
        session.refresh(user_service)
        return UserServiceResponse.from_orm(user_service)

    @staticmethod
    def delete_user_service(session: Session, user_service_id: int) -> bool:
        user_service = (
            session.query(UserService).filter(UserService.id == user_service_id).first()
        )
        if not user_service:
            return False

        session.delete(user_service)
        session.commit()
        return True


class AsyncUserServiceAccessor:
    @staticmethod
    async def create_user_service(
        session: AsyncSession, user_service_data: UserServiceCreate
    ) -> UserServiceResponse:
        new_user_service = UserService(**user_service_data.dict())
        session.add(new_user_service)
        await session.commit()
        await session.refresh(new_user_service)
        return UserServiceResponse.from_orm(new_user_service)

    @staticmethod
    async def get_user_service_by_id(
        session: AsyncSession, user_service_id: int
    ) -> Optional[UserServiceResponse]:
        result = await session.execute(
            select(UserService).where(UserService.id == user_service_id)
        )
        user_service = result.scalar_one_or_none()
        if user_service:
            return UserServiceResponse.from_orm(user_service)
        return None

    @staticmethod
    async def update_user_service(
        session: AsyncSession,
        user_service_id: int,
        user_service_data: UserServiceUpdate,
    ) -> Optional[UserServiceResponse]:
        result = await session.execute(
            select(UserService).where(UserService.id == user_service_id)
        )
        user_service = result.scalar_one_or_none()
        if not user_service:
            return None

        update_data = user_service_data.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(user_service, key, value)

        await session.commit()
        await session.refresh(user_service)
        return UserServiceResponse.from_orm(user_service)

    @staticmethod
    async def delete_user_service(session: AsyncSession, user_service_id: int) -> bool:
        result = await session.execute(
            select(UserService).where(UserService.id == user_service_id)
        )
        user_service = result.scalar_one_or_none()
        if not user_service:
            return False

        await session.delete(user_service)
        await session.commit()
        return True
