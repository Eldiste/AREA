from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import Session

from src.db.models.reaction import Reaction
from src.schemas.reaction import ReactionCreate, ReactionResponse, ReactionUpdate


class SyncReactionAccessor:
    @staticmethod
    def create_reaction(
        session: Session, reaction_data: ReactionCreate
    ) -> ReactionResponse:
        new_reaction = Reaction(**reaction_data.dict())
        session.add(new_reaction)
        session.commit()
        session.refresh(new_reaction)
        return ReactionResponse.from_orm(new_reaction)

    @staticmethod
    def get_reaction_by_id(
        session: Session, reaction_id: int
    ) -> Optional[ReactionResponse]:
        reaction = session.query(Reaction).filter(Reaction.id == reaction_id).first()
        if reaction:
            return ReactionResponse.from_orm(reaction)
        return None

    @staticmethod
    def update_reaction(
        session: Session, reaction_id: int, reaction_data: ReactionUpdate
    ) -> Optional[ReactionResponse]:
        reaction = session.query(Reaction).filter(Reaction.id == reaction_id).first()
        if not reaction:
            return None

        update_data = reaction_data.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(reaction, key, value)

        session.commit()
        session.refresh(reaction)
        return ReactionResponse.from_orm(reaction)

    @staticmethod
    def delete_reaction(session: Session, reaction_id: int) -> bool:
        reaction = session.query(Reaction).filter(Reaction.id == reaction_id).first()
        if not reaction:
            return False

        session.delete(reaction)
        session.commit()
        return True


class AsyncReactionAccessor:
    @staticmethod
    async def create_reaction(
        session: AsyncSession, reaction_data: ReactionCreate
    ) -> ReactionResponse:
        new_reaction = Reaction(**reaction_data.dict())
        session.add(new_reaction)
        await session.commit()
        await session.refresh(new_reaction)
        return ReactionResponse.from_orm(new_reaction)

    @staticmethod
    async def get_reaction_by_id(
        session: AsyncSession, reaction_id: int
    ) -> Optional[ReactionResponse]:
        result = await session.execute(
            select(Reaction).where(Reaction.id == reaction_id)
        )
        reaction = result.scalar_one_or_none()
        if reaction:
            return ReactionResponse.from_orm(reaction)
        return None

    @staticmethod
    async def update_reaction(
        session: AsyncSession, reaction_id: int, reaction_data: ReactionUpdate
    ) -> Optional[ReactionResponse]:
        result = await session.execute(
            select(Reaction).where(Reaction.id == reaction_id)
        )
        reaction = result.scalar_one_or_none()
        if not reaction:
            return None

        update_data = reaction_data.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(reaction, key, value)

        await session.commit()
        await session.refresh(reaction)
        return ReactionResponse.from_orm(reaction)

    @staticmethod
    async def delete_reaction(session: AsyncSession, reaction_id: int) -> bool:
        result = await session.execute(
            select(Reaction).where(Reaction.id == reaction_id)
        )
        reaction = result.scalar_one_or_none()
        if not reaction:
            return False

        await session.delete(reaction)
        await session.commit()
        return True
