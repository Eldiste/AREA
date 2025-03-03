import logging
from typing import Optional

from pydantic import Field

from src.service.Action.actions import Action, ActionConfig, ActionResponse

LOGGER = logging.getLogger(__name__)


class ChannelCreatedActionConfig(ActionConfig):
    """
    Configuration schema for the ChannelUpdatedAction.
    """

    channel_id: str = Field(
        ..., description="The ID of the guild where the channel is updated."
    )
    channel_name: str = Field(
        ..., description="The ID of the guild where the channel is updated."
    )
    content: str = Field(
        None, description="Additional content about the channel deletion."
    )


class ChannelUpdatedActionResponse(ActionResponse):
    """
    Response schema for the ChannelUpdatedAction.
    """

    channel_id: str
    content: str


class ChannelCreatedAction(Action):
    name = "channel_created"
    config = ChannelCreatedActionConfig

    def __init__(self, config: ChannelCreatedActionConfig):
        """
        Initialize the action with channel details.
        :param channel_id: The ID of the created channel.
        :param channel_name: The name of the created channel.
        :param created_at: The creation time of the channel.
        """
        super().__init__(config)

    async def execute(self, *args, **kwargs) -> Optional[ChannelUpdatedActionResponse]:
        """
        Process the channel update details and log the event.

        :return: A ChannelUpdatedActionResponse with the updated channel details.
        """
        try:
            # Log the channel update
            LOGGER.info(
                f"Channel {self.config.channel_id} in guild {self.config.guild_id} Created"
            )

            # Return a successful response
            return ChannelUpdatedActionResponse(
                success=True,
                details={
                    "event": "channel_created",
                    "guild_id": self.config.guild_id,
                },
                channel_id=self.config.channel_id,
                content=self.config.content,
            )

        except Exception as e:
            LOGGER.error(f"Error processing channel update: {str(e)}")
            return None
