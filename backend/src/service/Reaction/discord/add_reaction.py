import logging
from typing import Dict

from pydantic import Field

from src.config import settings
from src.service.Reaction.reactions import Reaction, ReactionConfig, ReactionResponse
from src.service.services.discord.dicord import DiscordAPI

LOGGER = logging.getLogger(__name__)


class AddReactionConfig(ReactionConfig):
    """
    Configuration schema for the AddReaction reaction.
    """

    channel_id: str = Field(
        ..., description="The ID of the Discord channel containing the message"
    )
    message_id: str = Field(..., description="The ID of the message to react to")
    emoji: str = Field(..., description="The emoji to add as a reaction")


class AddReactionResponse(ReactionResponse):
    """
    Response schema for the AddReaction reaction.
    """

    details: Dict[str, str]


class AddReaction(Reaction):
    """
    Reaction that adds a reaction (emoji) to a specific Discord message.
    """

    name: str = "add_reaction"
    config = AddReactionConfig

    def __init__(self, config: AddReactionConfig):
        """
        Initialize the AddReaction reaction with its configuration.

        :param config: AddReactionConfig object containing channel_id, message_id, and emoji.
        """
        super().__init__(config)

    async def execute(self, action_result: dict = None) -> AddReactionResponse:
        """
        Execute the reaction to add a reaction to a Discord message.

        :param action_result: Optional result from a preceding action.
        :return: AddReactionResponse indicating the success or failure of the operation.
        """
        channel_id = self.config.channel_id
        message_id = self.config.message_id
        emoji = self.config.emoji

        LOGGER.info(
            f"Preparing to add reaction '{emoji}' to message {message_id} in channel {channel_id}"
        )

        discord_token = settings.oauth.providers.get("discord").token

        if not discord_token:
            raise ValueError("Discord token is missing in the configuration.")

        discord_api = DiscordAPI(token=discord_token)

        try:
            await discord_api.add_reaction(channel_id, message_id, emoji)
            LOGGER.info(
                f"Reaction '{emoji}' added successfully to message {message_id} in channel {channel_id}"
            )
            return AddReactionResponse(
                success=True,
                details={
                    "channel_id": channel_id,
                    "message_id": message_id,
                    "emoji": emoji,
                },
            )
        except Exception as e:
            LOGGER.error(f"Failed to add reaction: {e}")
            return AddReactionResponse(
                success=False,
                details={"error": str(e)},
            )
        finally:
            if discord_api.websocket:
                await discord_api.websocket.close()
