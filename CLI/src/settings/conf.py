from typing import Optional

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    api_url: str = "http://137.74.94.58:8080/"
    token_file: str = "./access_token.txt"
    user_name: Optional[str]
    password: Optional[str]
    debug: bool = False

    class Config:
        env_file = ".env"
