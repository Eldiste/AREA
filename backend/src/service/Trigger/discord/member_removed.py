import logging
import time
from typing import Optional

from src.config import settings
from src.service.services.discord.dicord import DiscordAPI
from src.service.Trigger.triggers import Trigger, TriggerResponse

from .base_config import GuildDiscordConfig

LOGGER = logging.getLogger(__name__)


class MemberRemovedTriggerResponse(TriggerResponse):
    """
    Response schema for the MemberRemovedTrigger.
    """

    user_id: str
    user_name: str
    guild_id: str


class MemberRemovedTrigger(Trigger):
    """
    Trigger that activates when a member is removed from a specific Discord guild.
    """

    name = "member_removed"
    config = GuildDiscordConfig

    def __init__(self, config: GuildDiscordConfig):
        """
        Initialize the MemberRemovedTrigger with its configuration.

        :param config: MemberRemovedTriggerConfig object containing guild_id.
        """
        super().__init__(config)
        self.guild_id = config.guild_id

    async def execute(self, *args, **kwargs) -> Optional[MemberRemovedTriggerResponse]:
        """
        Listen for member removal events in the specified guild.

        :return: MemberRemovedTriggerResponse if a member is removed, else None.
        """
        if not self.guild_id:
            LOGGER.error("Missing guild_id in trigger config.")
            return None

        api = DiscordAPI(token=settings.oauth.providers.get("discord").token)
        await api.connect()

        async for member_data in api.wait_for_event(
            "GUILD_MEMBER_REMOVE", lambda m: m.get("guild_id") == self.guild_id
        ):
            user_id = member_data.get("user", {}).get("id")
            user_name = member_data.get("user", {}).get("username")

            LOGGER.info(
                f"Member removed from guild {self.guild_id}: {user_name} ({user_id})"
            )

            return MemberRemovedTriggerResponse(
                triggered_at=time.time(),
                details={
                    "event": "member_removed",
                    "guild_id": self.guild_id,
                },
                user_id=user_id,
                user_name=user_name,
                guild_id=self.guild_id,
            )

        return None
