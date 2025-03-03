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


class GuildRoleAddedTriggerResponse(TriggerResponse):
    """
    Response schema for the created ChannelTrigger.
    """

    role_id: str
    role_name: str


class GuildRoleAddedTrigger(Trigger):
    name = "guild_role_added"
    config = GuildDiscordConfig

    def __init__(self, config: GuildDiscordConfig):
        super().__init__(config)
        self.guild_id = config.guild_id

    async def execute(self, *args, **kwargs) -> Optional[GuildRoleAddedTriggerResponse]:
        if not self.guild_id:
            LOGGER.error("Missing guild_id in trigger config.")
            return None

        api = DiscordAPI(token=settings.oauth.providers.get("discord").token)
        await api.connect()

        async for role_data in api.wait_for_event(
            "GUILD_ROLE_CREATE", lambda r: r.get("guild_id") == self.guild_id
        ):
            try:
                role = role_data.get("role", {})
                role_id = role.get("id")
                role_name = role.get("name")

                if not role_id or not role_name:
                    raise ValueError(
                        "Role data is incomplete or missing required fields."
                    )

                return GuildRoleAddedTriggerResponse(
                    triggered_at=time.time(),
                    details={
                        "event": "guild_role_added",
                        "guild_id": self.guild_id,
                    },
                    role_id=role_id,
                    role_name=role_name,
                    content=json.dumps(role),
                )
            except Exception as e:
                LOGGER.error(f"Error processing role data: {e}")
                continue

        return None
