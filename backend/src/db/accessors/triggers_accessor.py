from sqlalchemy import update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from src.db.models.triggers import Trigger
from src.schemas.trigger import TriggerCreate, TriggerResponse


class AsyncTriggerAccessor:
    @staticmethod
    async def create_trigger(
        session: AsyncSession, trigger_data: TriggerCreate
    ) -> TriggerResponse:
        """
        Create a new trigger in the database.
        """
        new_trigger = Trigger(**trigger_data.dict())
        session.add(new_trigger)
        await session.commit()
        await session.refresh(new_trigger)
        return TriggerResponse.from_orm(new_trigger)

    @staticmethod
    async def get_trigger_by_id(
        session: AsyncSession, trigger_id: int
    ) -> TriggerResponse:
        """
        Retrieve a trigger by its ID.
        """
        result = await session.execute(select(Trigger).where(Trigger.id == trigger_id))
        trigger = result.scalar_one_or_none()
        if trigger:
            return TriggerResponse.from_orm(trigger)
        return None

    @staticmethod
    async def get_trigger_by_name(
        session: AsyncSession, trigger_name: str
    ) -> TriggerResponse:
        """
        Retrieve a trigger by its name.
        """
        result = await session.execute(
            select(Trigger).where(Trigger.name == trigger_name)
        )
        trigger = result.scalar_one_or_none()
        if trigger:
            return TriggerResponse.from_orm(trigger)
        return None

    @staticmethod
    async def update_trigger_config(
        session: AsyncSession, trigger_name: str, new_config: dict
    ) -> bool:
        """
        Update the configuration of a trigger by its name.
        """
        result = await session.execute(
            select(Trigger).where(Trigger.name == trigger_name)
        )
        trigger = result.scalar_one_or_none()
        if not trigger:
            return False  # Trigger not found

        stmt = (
            update(Trigger)
            .where(Trigger.name == trigger_name)
            .values(config=new_config)
        )
        await session.execute(stmt)
        await session.commit()
        return True

    @staticmethod
    async def delete_trigger(session: AsyncSession, trigger_id: int) -> bool:
        """
        Delete a trigger by its ID.
        """
        result = await session.execute(select(Trigger).where(Trigger.id == trigger_id))
        trigger = result.scalar_one_or_none()
        if not trigger:
            return False

        await session.delete(trigger)
        await session.commit()
        return True
