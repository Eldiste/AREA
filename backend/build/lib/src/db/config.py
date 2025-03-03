from typing import Optional

from pydantic import Field
from pydantic_settings import BaseSettings


class PostgresConfig(BaseSettings):
    host: str = Field("localhost", env="POSTGRES_HOST")
    port: int = Field(5432, env="POSTGRES_PORT")
    user: str = Field("postgres", env="POSTGRES_USER")
    password: Optional[str] = Field("password", env="POSTGRES_PASSWORD")
    database: str = Field("postgres_db", env="POSTGRES_DATABASE")
    pool_size: int = Field(5)

    def make_db_url(self, driver: str = "postgresql+asyncpg") -> str:
        """
        Constructs the database URL.
        """
        password_part = f":{self.password}" if self.password else ""
        return f"{driver}://{self.user}{password_part}@{self.host}:{self.port}/{self.database}"
