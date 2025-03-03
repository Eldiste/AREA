from dotenv import load_dotenv
from pydantic_settings import BaseSettings
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session

from src.db.config import PostgresConfig
from src.redis.config import RedisConfig
from src.utils import (
    make_async_engine,
    make_async_redis_client,
    make_async_session_factory,
    make_engine,
    make_session_factory,
)

# Load .env file
load_dotenv()


class Settings(BaseSettings):
    postgres: PostgresConfig = PostgresConfig()
    redis: RedisConfig = RedisConfig()

    class Config:
        env_nested_delimiter = "__"


settings = Settings()

# Create Sync and Async Engine
async_engine = make_async_engine(config=settings, echo=True)
sync_engine = make_engine(config=settings, echo=True)

# Create the session factory
async_session_factory = make_async_session_factory(async_engine)
sync_session_factory = make_session_factory(sync_engine)

# Make Async Redis Client
async_redis_client = make_async_redis_client(config=settings.redis)


# Dependency function for a database session
async def get_db_async_session() -> AsyncSession:
    async with async_session_factory() as session:
        yield session


async def get_db_sync_session() -> Session:
    async with sync_session_factory() as session:
        yield session
