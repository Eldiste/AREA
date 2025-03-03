import logging
from typing import Optional

from pydantic import Field

from src.service.Action.actions import Action, ActionConfig, ActionResponse

LOGGER = logging.getLogger(__name__)


class MessageUpdatedActionConfig(ActionConfig):
    """
    Configuration schema for the MessageUpdatedAction.
    """

    content: str = Field(..., description="The new content of the message.")
    author: dict = Field(..., description="The author of the message.")
    channel_id: str = Field(
        ..., description="The ID of the channel where the message was updated."
    )


class MessageUpdatedResponse(ActionResponse):
    """
    Response schema for MessageUpdatedAction.
    """

    message_id: str
    updated_content: str
    author: dict
    channel_id: str


class MessageUpdatedAction(Action):
    name = "message_updated"
    config = MessageUpdatedActionConfig

    def __init__(self, config: MessageUpdatedActionConfig):
        """
        Initialize the action with message update details.
        :param config: MessageUpdatedActionConfig containing the message data.
        """
        super().__init__(config)

    async def execute(self, *args, **kwargs) -> Optional[MessageUpdatedResponse]:
        """
        Process the message update details.
        :return: A dictionary with the updated message details or None if the filter does not match.
        """
        try:
            # Step 1: Log the message update
            LOGGER.info(
                f"Message {self.config.message_id} in channel {self.config.channel_id} by {self.config.author.get('username')} was updated to: {self.config.updated_content}"
            )

            # Step 2: Return a successful response
            return MessageUpdatedResponse(
                message_id=self.config.message_id,
                updated_content=self.config.updated_content,
                author=self.config.author,
                channel_id=self.config.channel_id,
            )

        except Exception as e:
            LOGGER.error(f"Error processing message update: {str(e)}")
            return None
