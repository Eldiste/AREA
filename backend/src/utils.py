from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

import redis.asyncio as redis
from redis.asyncio import Redis
from src.db.config import PostgresConfig
from src.redis.config import RedisConfig


def make_async_engine(config, echo: bool = False) -> AsyncEngine:
    return create_async_engine(
        config.postgres.make_db_url(driver="postgresql+asyncpg"), echo=echo
    )


def make_engine(config, echo: bool = False) -> Engine:
    return create_engine(config.postgres.make_db_url(driver="postgresql"), echo=echo)


def make_async_session_factory(engine: Engine) -> sessionmaker:
    return sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)


def make_session_factory(engine: Engine) -> sessionmaker:
    return sessionmaker(bind=engine)


def make_async_redis_client(config: RedisConfig) -> Redis:
    return redis.Redis(
        host=config.host,
        port=config.port,
        db=config.db,
        password=config.password,
        decode_responses=config.decode_responses,
    )
