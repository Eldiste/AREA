import logging
import time
from typing import Callable, Optional

from src.service.base import BaseComponent

LOGGER = logging.getLogger(__name__)


class Trigger(BaseComponent):
    """
    Base Trigger class. All specific triggers should inherit from this class.
    """

    name = "generic_trigger"

    def __init__(self, config: dict):
        """
        Initialize the Trigger with its configuration.

        :param config: Configuration dictionary for the trigger.
        """
        self.config = config

    async def execute(self, subject: dict, *args, **kwargs) -> bool:
        """
        Evaluate the trigger condition based on the provided subject and additional arguments.

        :param subject: dict containing the data to evaluate the trigger condition.
        :return: True if the condition is met, False otherwise.
        """
        raise NotImplementedError(
            "Trigger subclasses must implement the `execute` method."
        )

    async def update_last_run(
        self, update_callback: Optional[Callable[[str, float], None]] = None
    ):
        """
        Update the trigger's last_run timestamp.

        :param update_callback: Optional callback to handle database or external updates.
                                The callback should accept two arguments: `name` and `last_run`.
        """
        last_run_time = time.time()
        self.config["last_run"] = last_run_time
        LOGGER.info(
            f"Trigger '{self.name}' last_run updated to {last_run_time} in memory."
        )

        if update_callback:
            try:
                await update_callback(
                    self.name, last_run_time
                )  # Pass both arguments correctly.
                LOGGER.info(f"Trigger '{self.name}' last_run updated in database.")
            except Exception as e:
                LOGGER.error(
                    f"Failed to update last_run for trigger '{self.name}' in database: {str(e)}",
                    exc_info=True,
                )
        else:
            LOGGER.warning(f"No update callback provided for trigger '{self.name}'.")
