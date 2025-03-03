from pydantic_settings import BaseSettings


class RedisConfig(BaseSettings):
    host: str = "localhost"
    port: int = 6379
    db: int = 0
    password: str | None = None
    decode_responses: bool = True

    class Config:
        env_prefix = "REDIS_"
        env_nested_delimiter = "__"
