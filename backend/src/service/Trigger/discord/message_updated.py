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


class MessageUpdatedTriggerResponse(TriggerResponse):
    """
    Response schema for the MessageUpdatedInChannelTrigger.
    """

    content: str
    author: dict
    channel_id: str


class MessageUpdatedTrigger(Trigger):
    name = "message_updated"
    config = BaseDiscordConfig

    def __init__(self, config: BaseDiscordConfig):
        super().__init__(config)
        self.channel_id = config.channel_id

    async def execute(self, *args, **kwargs) -> Optional[MessageUpdatedTriggerResponse]:
        if not self.channel_id:
            LOGGER.error("channel_id in trigger config.")
            return None

        api = DiscordAPI(token=settings.oauth.providers.get("discord").token)
        await api.connect()

        async for message in api.wait_for_event(
            "MESSAGE_UPDATE", lambda m: m.get("channel_id") == self.channel_id
        ):
            LOGGER.info(
                f"Updated message in channel {self.channel_id}: {message.get('content')}"
            )
            return MessageUpdatedTriggerResponse(
                triggered_at=time.time(),
                details={
                    "event": "message_updated",
                    "channel_id": self.channel_id,
                },
                content=message.get("content"),
                author=message.get("author"),
                channel_id=self.channel_id,
            )

        return None
