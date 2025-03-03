import logging

from src.service.Action.actions import Action

LOGGER = logging.getLogger(__name__)


class PrintAction(Action):
    name = "print_action"

    async def execute(self, message: str, **kwargs):
        """
        Print a message.

        :param message: The message to print.
        """
        LOGGER.info(f"Executing PrintAction with message: {message}")
