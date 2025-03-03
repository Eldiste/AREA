import logging
from typing import Dict

from pydantic import Field

from src.config import settings
from src.service.Reaction.reactions import Reaction, ReactionConfig, ReactionResponse
from src.service.services.discord.dicord import DiscordAPI

LOGGER = logging.getLogger(__name__)


class DeleteMessageReactionConfig(ReactionConfig):
    """
    Configuration schema for the DeleteMessage reaction.
    """

    channel_id: str = Field(
        ..., description="The ID of the Discord channel containing the message"
    )
    message_id: str = Field(..., description="The ID of the message to delete")


class DeleteMessageReactionResponse(ReactionResponse):
    """
    Response schema for the DeleteMessage reaction.
    """

    details: Dict[str, str]


class DeleteMessage(Reaction):
    """
    Reaction that deletes a specified Discord message.
    """

    name: str = "delete_message"
    config = DeleteMessageReactionConfig

    def __init__(self, config: DeleteMessageReactionConfig):
        """
        Initialize the DeleteMessage reaction with its configuration.

        :param config: DeleteMessageReactionConfig object containing channel_id and message_id.
        """
        super().__init__(config)

    async def execute(
        self, action_result: dict = None
    ) -> DeleteMessageReactionResponse:
        """
        Execute the reaction to delete a Discord message.

        :param action_result: Optional result from a preceding action.
        :return: DeleteMessageReactionResponse indicating the success or failure of the operation.
        """
        channel_id = self.config.channel_id
        message_id = self.config.message_id

        LOGGER.info(
            f"Preparing to delete message {message_id} from channel {channel_id}"
        )

        discord_token = settings.oauth.providers.get("discord").token

        if not discord_token:
            raise ValueError("Discord token is missing in the configuration.")

        discord_api = DiscordAPI(token=discord_token)

        try:
            await discord_api.delete_message(
                channel_id=channel_id, message_id=message_id
            )
            LOGGER.info(
                f"Message {message_id} deleted successfully from channel {channel_id}"
            )
            return DeleteMessageReactionResponse(
                success=True,
                details={
                    "channel_id": channel_id,
                    "message_id": message_id,
                },
            )
        except Exception as e:
            LOGGER.error(f"Failed to delete message: {e}")
            return DeleteMessageReactionResponse(
                success=False,
                details={"error": str(e)},
            )
        finally:
            if discord_api.websocket:
                await discord_api.websocket.close()
