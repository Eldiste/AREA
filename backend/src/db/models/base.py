from typing import Any, Dict, Iterable, Optional, Set

from sqlalchemy import Column, Table, exists, func, select, text
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session


# Augmented base class
class AugmentedBase:
    __tablename__: str
    __table__: Table

    def to_dict(self, exclude: Optional[Set[str]] = None) -> Dict[str, Any]:
        exclude_set = exclude if exclude is not None else set()
        return {
            column.name: getattr(self, column.name)
            for column in self.__table__.columns
            if column.name not in exclude_set
        }

    @classmethod
    def count(cls, session: Session) -> int:
        return session.execute(
            text(f"SELECT COUNT(*) FROM {cls.__tablename__}")
        ).scalar_one()

    @classmethod
    async def async_count(cls, session: AsyncSession) -> int:
        result = await session.execute(
            text(f"SELECT COUNT(*) FROM {cls.__tablename__}")
        )
        return result.scalar_one()

    @classmethod
    def estimate_count(cls, session: Session) -> int:
        return session.execute(
            text(
                f"SELECT reltuples::bigint FROM pg_class WHERE relname = '{cls.__tablename__}'"
            )
        ).scalar_one()

    @classmethod
    async def async_estimate_count(cls, session: AsyncSession) -> int:
        result = await session.execute(
            text(
                f"SELECT reltuples::bigint FROM pg_class WHERE relname = '{cls.__tablename__}'"
            )
        )
        return result.scalar_one()

    @classmethod
    def fast_count(cls, session: Session) -> int:
        estimate_count = cls.estimate_count(session)
        if estimate_count == -1:
            return cls.count(session)
        return estimate_count

    @classmethod
    async def async_fast_count(cls, session: AsyncSession) -> int:
        estimate_count = await cls.async_estimate_count(session)
        if estimate_count == -1:
            return await cls.async_count(session)
        return estimate_count

    @classmethod
    def exists(cls, session: Session, where) -> bool:
        exists_stmt = exists(select([text("1")])).where(where)
        result = session.execute(exists_stmt).scalar()
        return result is not None

    @classmethod
    async def async_exists(cls, session: AsyncSession, where) -> bool:
        exists_stmt = exists(select([text("1")])).where(where)
        result = await session.execute(exists_stmt)
        return result.scalar() is not None

    @classmethod
    def jsonb_keys(cls, session: Session, column: Column, where) -> Iterable[str]:
        select_stmt = select(func.jsonb_object_keys(column)).where(where)
        return session.execute(select_stmt).scalars()

    @classmethod
    async def async_jsonb_keys(
        cls, session: AsyncSession, column: Column, where
    ) -> Iterable[str]:
        select_stmt = select(func.jsonb_object_keys(column)).where(where)
        result = await session.execute(select_stmt)
        return result.scalars()


Base = declarative_base(cls=AugmentedBase)
