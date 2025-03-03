from typing import Dict, List, Optional

from pydantic import field_validator
from pydantic_settings import BaseSettings


class OAuthProviderConfig(BaseSettings):
    client_id: str
    client_secret: str
    redirect_uri: str
    authorize_url: str
    token_url: str
    api_base_url: str
    scopes: List[str]  # List to accommodate multiple scopes
    token: Optional[str]

    @field_validator("scopes", mode="before")
    def split_scopes(cls, v):
        if isinstance(v, str):
            return v.split(",")
        return v


class OAuthConfig(BaseSettings):
    providers: Dict[str, OAuthProviderConfig] = {}

    class Config:
        env_nested_delimiter = "__"
