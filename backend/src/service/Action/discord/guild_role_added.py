import logging
from typing import Optional

from pydantic import Field

from src.service.Action.actions import Action, ActionConfig, ActionResponse
from src.service.services.discord.dicord import DiscordAPI

LOGGER = logging.getLogger(__name__)


class GuildRoleAddedActionConfig(ActionConfig):
    """
    Configuration schema for the GuildRoleAddedAction.
    """

    content: str = Field(..., description="The content of the message")
    role_id: str = Field(..., description="The ID of the role added.")
    role_name: str = Field(..., description="The name of the role added.")


from pydantic import validator


class GuildRoleAddedResponse(ActionResponse):
    content: str
    role_id: str
    role_name: str


class GuildRoleAddedAction(Action):
    name = "guild_role_added"
    config = GuildRoleAddedActionConfig

    def __init__(self, config: GuildRoleAddedActionConfig):
        """
        Initialize the action with role addition details.
        :param config: GuildRoleAddedActionConfig containing the role and guild details.
        """
        super().__init__(config)

    async def execute(self, *args, **kwargs) -> Optional[GuildRoleAddedResponse]:
        """
        Process the newly added role details.
        :return: A dictionary with the role details.
        """
        try:
            # Log the role addition
            LOGGER.info(
                f"Role {self.config.role_name} (ID: {self.config.role_id}) was added to guild {self.config.guild_id}."
            )

            # Return a successful response
            return GuildRoleAddedResponse(succes=True, content=self.config.content)

        except Exception as e:
            LOGGER.error(f"Error processing role addition: {str(e)}")
            return None
