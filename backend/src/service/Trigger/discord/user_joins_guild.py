import logging
import time
from typing import Optional

from src.config import settings
from src.service.services.discord.dicord import DiscordAPI
from src.service.Trigger.triggers import Trigger, TriggerResponse

from .base_config import GuildDiscordConfig

LOGGER = logging.getLogger(__name__)


class UserJoinsGuildTriggerResponse(TriggerResponse):
    """
    Response schema for the UserJoinsGuildTrigger.
    """

    user_id: str
    user_name: str
    joined_at: str
    guild_id: str


class UserJoinsGuildTrigger(Trigger):
    """
    Trigger that activates when a user joins a specific Discord guild.
    """

    name = "user_joins_guild"
    config = GuildDiscordConfig

    def __init__(self, config: GuildDiscordConfig):
        """
        Initialize the UserJoinsGuildTrigger with its configuration.

        :param config: UserJoinsGuildTriggerConfig object containing guild_id.
        """
        super().__init__(config)
        self.guild_id = config.guild_id

    async def execute(self, *args, **kwargs) -> Optional[UserJoinsGuildTriggerResponse]:
        """
        Listen for user join events in the specified guild.

        :return: UserJoinsGuildTriggerResponse if a new user joins, else None.
        """
        if not self.guild_id:
            LOGGER.error("Missing guild_id in trigger config.")
            return None

        api = DiscordAPI(token=settings.oauth.providers.get("discord").token)
        await api.connect()

        async for member_data in api.wait_for_event(
            "GUILD_MEMBER_ADD", lambda m: m.get("guild_id") == self.guild_id
        ):
            user_id = member_data.get("user", {}).get("id")
            user_name = member_data.get("user", {}).get("username")
            joined_at = member_data.get("joined_at")

            LOGGER.info(
                f"New user joined guild {self.guild_id}: {user_name} ({user_id}) at {joined_at}"
            )

            return UserJoinsGuildTriggerResponse(
                triggered_at=time.time(),
                details={
                    "event": "user_joins_guild",
                    "guild_id": self.guild_id,
                },
                user_id=user_id,
                user_name=user_name,
                joined_at=joined_at,
                guild_id=self.guild_id,
            )

        return None
