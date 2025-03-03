import logging
from typing import Dict

from src.service.Reaction.reactions import Reaction, ReactionConfig, ReactionResponse

LOGGER = logging.getLogger(__name__)


class PrintReactionConfig(ReactionConfig):
    """
    Configuration schema for the PrintReaction.
    """

    pass


class PrintReactionResponse(ReactionResponse):
    """
    Response schema for the PrintReaction.
    """

    details: Dict[str, str]


class PrintReaction(Reaction):
    """
    Reaction that logs the result of an action to the log.
    """

    name: str = "print_reaction"
    config = PrintReactionConfig

    def __init__(self, config: PrintReactionConfig):
        """
        Initialize the PrintReaction with its configuration.

        :param config: PrintReactionConfig object.
        """
        super().__init__(config)

    async def execute(self, action_result, **kwargs) -> PrintReactionResponse:
        """
        Log the result of the action.

        :param action_result: The result from the action.
        :param kwargs: Additional parameters.
        :return: PrintReactionResponse indicating the result of the execution.
        """
        LOGGER.info(
            f"Executing PrintReaction with result: {action_result} and params: {kwargs}"
        )

        return PrintReactionResponse(
            success=True, details={"printed": "true", "params": str(kwargs)}
        )
