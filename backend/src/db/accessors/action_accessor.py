from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import Session

from src.db.models.action import Action
from src.schemas.action import ActionCreate, ActionResponse, ActionUpdate


class SyncActionAccessor:
    @staticmethod
    def create_action(session: Session, action_data: ActionCreate) -> ActionResponse:
        new_action = Action(**action_data.dict())
        session.add(new_action)
        session.commit()
        session.refresh(new_action)
        return ActionResponse.from_orm(new_action)

    @staticmethod
    def get_action_by_id(session: Session, action_id: int) -> Optional[ActionResponse]:
        action = session.query(Action).filter(Action.id == action_id).first()
        if action:
            return ActionResponse.from_orm(action)
        return None

    @staticmethod
    def update_action(
        session: Session, action_id: int, action_data: ActionUpdate
    ) -> Optional[ActionResponse]:
        action = session.query(Action).filter(Action.id == action_id).first()
        if not action:
            return None

        update_data = action_data.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(action, key, value)

        session.commit()
        session.refresh(action)
        return ActionResponse.from_orm(action)

    @staticmethod
    def delete_action(session: Session, action_id: int) -> bool:
        action = session.query(Action).filter(Action.id == action_id).first()
        if not action:
            return False

        session.delete(action)
        session.commit()
        return True


class AsyncActionAccessor:
    @staticmethod
    async def create_action(
        session: AsyncSession, action_data: ActionCreate
    ) -> ActionResponse:
        new_action = Action(**action_data.dict())
        session.add(new_action)
        await session.commit()
        await session.refresh(new_action)
        return ActionResponse.from_orm(new_action)

    @staticmethod
    async def get_action_by_id(
        session: AsyncSession, action_id: int
    ) -> Optional[ActionResponse]:
        result = await session.execute(select(Action).where(Action.id == action_id))
        action = result.scalar_one_or_none()
        if action:
            return ActionResponse.from_orm(action)
        return None

    @staticmethod
    async def get_action_by_name(
        session: AsyncSession, action_name: str
    ) -> Optional[Action]:
        """
        Fetch an Action by its name from the database.
        :param session: AsyncSession instance
        :param action_name: Name of the Action
        :return: Action instance or None
        """
        result = await session.execute(select(Action).where(Action.name == action_name))
        return result.scalar_one_or_none()

    @staticmethod
    async def update_action(
        session: AsyncSession, action_id: int, action_data: ActionUpdate
    ) -> Optional[ActionResponse]:
        result = await session.execute(select(Action).where(Action.id == action_id))
        action = result.scalar_one_or_none()
        if not action:
            return None

        update_data = action_data.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(action, key, value)

        await session.commit()
        await session.refresh(action)
        return ActionResponse.from_orm(action)

    @staticmethod
    async def delete_action(session: AsyncSession, action_id: int) -> bool:
        result = await session.execute(select(Action).where(Action.id == action_id))
        action = result.scalar_one_or_none()
        if not action:
            return False

        await session.delete(action)
        await session.commit()
        return True
