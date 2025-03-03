import logging
import time
from typing import Optional

from src.config import settings
from src.service.services.discord.dicord import DiscordAPI
from src.service.Trigger.triggers import Trigger, TriggerResponse

from .base_config import BaseDiscordConfig

LOGGER = logging.getLogger(__name__)


class NewMessageInChannelResponse(TriggerResponse):
    """
    Response schema for the NewMessageInChannelTrigger.
    """

    content: str
    author: dict
    channel_id: str


class NewMessageInChannelTrigger(Trigger):
    """
    Trigger that activates when a new message is posted in a specific Discord channel.
    """

    name = "new_message_in_channel"
    config = BaseDiscordConfig

    def __init__(self, config: BaseDiscordConfig):
        """
        Initialize the NewMessageInChannelTrigger with its configuration.

        :param config: NewMessageInChannelTriggerConfig object containing channel_id and other configurations.
        """
        super().__init__(config)
        self.channel_id = config.channel_id

    async def execute(self, *args, **kwargs) -> Optional[NewMessageInChannelResponse]:
        """
        Listen for new messages in the specified channel.

        :return: Tuple (True, NewMessageInChannelResponse) if a message is received, else (False, None).
        """
        if not self.channel_id:
            LOGGER.error("Missing channel_id in trigger config.")
            return None

        api = DiscordAPI(token=settings.oauth.providers.get("discord").token)
        await api.connect()

        async for message in api.wait_for_event(
            "MESSAGE_CREATE", lambda m: m.get("channel_id") == self.channel_id
        ):
            LOGGER.info(
                f"New message received in channel {self.channel_id}: {message.get('content')}"
            )
            return NewMessageInChannelResponse(
                triggered_at=time.time(),
                details={
                    "event": "new_message",
                    "channel_id": self.channel_id,
                },
                content=message.get("content"),
                author=message.get("author"),
                channel_id=self.channel_id,
            )

        return None
