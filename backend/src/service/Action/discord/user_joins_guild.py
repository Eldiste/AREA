import logging

from pydantic import Field

from src.service.Action.actions import Action, ActionConfig
from src.service.services.discord.dicord import DiscordAPI

LOGGER = logging.getLogger(__name__)


class UserJoinsGuildActionConfig(ActionConfig):
    content: str = Field(..., description="The content of the message")
    user_id: str = Field(..., description="The id of the user")
    user_name: str = Field(..., description="The name of the user")
    joined_at: str = Field(..., description="wHEN ")


class UserJoinsGuildAction(Action):
    name = "user_joins_guild"

    def __init__(self, config: dict):
        self.config = config

    async def execute(self) -> dict:
        """
        Fetch the most recently joined member in the specified guild.
        :return: A dictionary containing the member's details.
        """

        token = self.config.get("token")
        guild_id = self.config.get("guild_id")

        if not token or not guild_id:
            LOGGER.error("Missing token or guild_id in action config")
            return {}

        api = DiscordAPI(token)
        members = await api.get_guild_members(guild_id=guild_id)

        if not members:
            LOGGER.info("No members found in guild")
            return {}

        latest_member = max(members, key=lambda m: m["joined_at"])
        return latest_member  # Return the latest member details
