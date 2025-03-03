import logging
from typing import Dict

from pydantic import Extra, Field

from src.config import settings  # Assuming settings provide access to the Discord token
from src.service.Reaction.reactions import Reaction, ReactionConfig, ReactionResponse
from src.service.services.discord.dicord import DiscordAPI

LOGGER = logging.getLogger(__name__)


class SendMessageReactionConfig(ReactionConfig):
    """
    Configuration schema for the SendMessage reaction.
    """

    channel_id: str = Field(
        ..., description="The ID of the Discord channel to send the message to"
    )
    content: str = Field(..., description="The content of the message to send")

    class Config:
        extra = Extra.allow


class SendMessageReactionResponse(ReactionResponse):
    """
    Response schema for the SendMessage reaction.
    """

    details: Dict[str, str]


class SendMessage(Reaction):
    """
    Reaction that sends a message to a specific Discord channel.
    """

    name: str = "send_message"
    config = SendMessageReactionConfig

    def __init__(self, config: SendMessageReactionConfig):
        """
        Initialize the SendMessage reaction with its configuration.

        :param config: SendMessageReactionConfig object containing channel_id and content.
        """
        super().__init__(config)

    async def execute(self, action_result: dict = None) -> SendMessageReactionResponse:
        """
        Execute the reaction to send a message to a Discord channel.

        :param action_result: Optional result from a preceding action.
        :return: SendMessageReactionResponse indicating the success or failure of the operation.
        """
        channel_id = self.config.channel_id
        content = self.config.content

        LOGGER.info(f"Preparing to send message to channel {channel_id}")

        discord_token = settings.oauth.providers.get("discord").token

        if not discord_token:
            raise ValueError("Discord token is missing in the configuration.")

        discord_api = DiscordAPI(token=discord_token)

        try:
            await discord_api.send_message(channel_id, content)
            LOGGER.info(f"Message sent successfully to channel {channel_id}: {content}")
            return SendMessageReactionResponse(
                success=True,
                details={"channel_id": channel_id, "message": content},
            )
        except Exception as e:
            LOGGER.error(f"Failed to send message: {e}")
            return SendMessageReactionResponse(
                success=False,
                details={"error": str(e)},
            )
        finally:
            if discord_api.websocket:
                await discord_api.websocket.close()
