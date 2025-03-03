import logging

from src.service.Reaction.reactions import Reaction

LOGGER = logging.getLogger(__name__)


class PrintReaction(Reaction):
    name = "print_reaction"

    async def execute(self, action_result, **kwargs):
        """
        Print the result of the action to the log.

        :param action_result: The result from the action.
        """
        LOGGER.info(
            f"Executing PrintReaction with result: {action_result} and params: {kwargs}"
        )
