import logging
from typing import Optional

from pydantic import Field

from src.service.Action.actions import Action, ActionConfig, ActionResponse
from src.service.services.discord.dicord import DiscordAPI

LOGGER = logging.getLogger(__name__)


class ChannelDeletedActionConfig(ActionConfig):
    """
    Configuration schema for the ChannelDeletedAction.
    """

    channel_name: Optional[str] = Field(
        None, description="The name of the deleted channel."
    )
    content: Optional[str] = Field(
        None, description="Additional content about the channel deletion."
    )


class ChannelDeletedResponse(ActionResponse):
    """
    Response schema for the ChannelDeletedAction.
    """

    channel_id: str
    channel_name: Optional[str]
    guild_id: str
    content: Optional[str]


class ChannelDeletedAction(Action):
    name = "channel_deleted"
    config = ChannelDeletedActionConfig

    def __init__(self, config: ChannelDeletedActionConfig):
        """
        Initialize the action with channel deletion details.

        :param config: ChannelDeletedActionConfig containing the channel and guild details.
        """
        super().__init__(config)

    async def execute(self, *args, **kwargs) -> Optional[ChannelDeletedResponse]:
        """
        Process the channel deletion and return relevant details.

        :return: A ChannelDeletedResponse with the details of the deleted channel.
        """
        try:
            # Log the channel deletion
            LOGGER.info(
                f"Channel {self.config.channel_name} (ID: {self.config.channel_id}) deleted in guild {self.config.guild_id}."
            )

            # Return a successful response
            return ChannelDeletedResponse(
                success=True,
                channel_id=self.config.channel_id,
                channel_name=self.config.channel_name,
                guild_id=self.config.guild_id,
                content=self.config.content,
            )

        except Exception as e:
            LOGGER.error(f"Error processing channel deletion: {str(e)}")
            return None
