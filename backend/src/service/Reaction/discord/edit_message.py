import logging
from typing import Dict

from pydantic import Field

from src.config import settings
from src.service.Reaction.reactions import Reaction, ReactionConfig, ReactionResponse
from src.service.services.discord.dicord import DiscordAPI

LOGGER = logging.getLogger(__name__)


class EditMessageReactionConfig(ReactionConfig):
    """
    Configuration schema for the EditMessage reaction.
    """

    channel_id: str = Field(
        ..., description="The ID of the Discord channel containing the message"
    )
    message_id: str = Field(..., description="The ID of the message to edit")
    content: str = Field(..., description="The new content for the message")


class EditMessageReactionResponse(ReactionResponse):
    """
    Response schema for the EditMessage reaction.
    """

    details: Dict[str, str]


class EditMessage(Reaction):
    """
    Reaction that edits a specified Discord message.
    """

    name: str = "edit_message"
    config = EditMessageReactionConfig

    def __init__(self, config: EditMessageReactionConfig):
        """
        Initialize the EditMessage reaction with its configuration.

        :param config: EditMessageReactionConfig object containing channel_id, message_id, and new content.
        """
        super().__init__(config)

    async def execute(self, action_result: dict = None) -> EditMessageReactionResponse:
        """
        Execute the reaction to edit a Discord message.

        :param action_result: Optional result from a preceding action.
        :return: EditMessageReactionResponse indicating the success or failure of the operation.
        """
        channel_id = self.config.channel_id
        message_id = self.config.message_id
        new_content = self.config.content

        LOGGER.info(f"Preparing to edit message {message_id} in channel {channel_id}")

        discord_token = settings.oauth.providers.get("discord").token

        if not discord_token:
            raise ValueError("Discord token is missing in the configuration.")

        discord_api = DiscordAPI(token=discord_token)

        try:
            await discord_api.edit_message(
                channel_id=channel_id, message_id=message_id, content=new_content
            )
            LOGGER.info(
                f"Message {message_id} in channel {channel_id} edited successfully with new content: {new_content}"
            )
            return EditMessageReactionResponse(
                success=True,
                details={
                    "channel_id": channel_id,
                    "message_id": message_id,
                    "new_content": new_content,
                },
            )
        except Exception as e:
            LOGGER.error(f"Failed to edit message: {e}")
            return EditMessageReactionResponse(
                success=False,
                details={"error": str(e)},
            )
        finally:
            if discord_api.websocket:
                await discord_api.websocket.close()
