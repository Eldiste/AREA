import json
import logging
import time
from typing import Optional

from src.config import settings
from src.service.services.discord.dicord import DiscordAPI
from src.service.Trigger.discord.base_config import (
    BaseDiscordConfig,
    GuildDiscordConfig,
)
from src.service.Trigger.triggers import Trigger, TriggerResponse

LOGGER = logging.getLogger(__name__)


class ChannelUpdatedTriggerResponse(TriggerResponse):
    """
    Response schema for the created ChannelTrigger.
    """

    channel_id: str
    channel_name: str


class ChannelUpdatedTrigger(Trigger):
    name = "channel_updated"
    config = GuildDiscordConfig

    def __init__(self, config: GuildDiscordConfig):
        super().__init__(config)
        self.guild_id = config.guild_id

    async def execute(self, *args, **kwargs) -> Optional[ChannelUpdatedTriggerResponse]:
        if not self.guild_id:
            LOGGER.error("Missing guild_id in trigger config.")
            return None

        api = DiscordAPI(token=settings.oauth.providers.get("discord").token)
        await api.connect()

        async for channel_data in api.wait_for_event(
            "CHANNEL_UPDATE", lambda c: c.get("guild_id") == self.guild_id
        ):
            channel_id = channel_data.get("id")
            channel_name = channel_data.get("name")

            # Pass the channel_id and relevant data to the reaction
            return ChannelUpdatedTriggerResponse(
                triggered_at=time.time(),
                details={
                    "event": "channel_updated",
                    "guild_id": self.guild_id,
                },
                channel_id=channel_id,
                channel_name=channel_name,
                content=json.dumps(channel_data),
            )

        return None
