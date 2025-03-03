from typing import Optional

from pydantic import BaseModel


class DiscordOAuthResponse(BaseModel):
    access_token: str
    token_type: str
    expires_in: int
    refresh_token: str
    scope: str


class DiscordUserResponse(BaseModel):
    id: str
    username: str
    discriminator: str
    avatar: Optional[str]
    email: Optional[str]
