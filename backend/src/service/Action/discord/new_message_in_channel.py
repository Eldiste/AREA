import logging

from src.service.Action.actions import Action, ActionConfig, ActionResponse

LOGGER = logging.getLogger(__name__)

from pydantic import Field


class NewMessageInChannelActionConfig(ActionConfig):
    """
    Configuration schema for the NewMessageInChannelAction.
    """

    content: str = Field(..., description="The content of the message")
    author: dict = Field(..., description="The author of the message")
    channel_id: str = Field(
        ..., description="The ID of the channel where the message was posted"
    )


class NewMessageInChannelActionResponse(ActionResponse):
    """
    Response schema for the NewMessageInChannelAction.
    """

    content: str
    author: dict
    channel_id: str


class NewMessageInChannelAction(Action):
    """
    Action to process and log details of a new message in a specific channel.
    """

    name: str = "new_message_in_channel"
    config = NewMessageInChannelActionConfig

    def __init__(self, config: NewMessageInChannelActionConfig):
        """
        Initialize the NewMessageInChannelAction with its configuration.

        :param config: NewMessageInChannelActionConfig object containing message details.
        """
        super().__init__(config)

    async def execute(self, *args, **kwargs) -> NewMessageInChannelActionResponse:
        """
        Process the message details.

        :return: NewMessageInChannelActionResponse with the processed message details.
        """
        content = self.config.content
        author = self.config.author
        channel_id = self.config.channel_id

        LOGGER.info(
            f"Processing message in channel {channel_id} by {author['username']}: {content}"
        )

        return NewMessageInChannelActionResponse(
            success=True,
            details={"processed": True},
            content=content,
            author=author,
            channel_id=channel_id,
        )
