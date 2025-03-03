from typing import Optional

from pydantic import Field

from src.service.Trigger.triggers import TriggerConfig


class BaseDiscordConfig(TriggerConfig):
    channel_id: str = Field(..., description="Discord Channel ID")


class ChannelDiscordDiscord(TriggerConfig):
    channel_id: Optional[str] = Field(..., description="Discord Channel ID (Optional)")


class GuildDiscordConfig(TriggerConfig):
    guild_id: str = Field(..., description="Guild Id")
