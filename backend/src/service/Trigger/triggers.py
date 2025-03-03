import asyncio
import logging
import time
from abc import ABC, abstractmethod
from typing import Any, Callable, Dict, Optional

from pydantic import BaseModel, Field

LOGGER = logging.getLogger(__name__)


class TriggerConfig(BaseModel):
    """
    Base configuration schema for all triggers.
    """

    token: Optional[str] = None  ## This will be Inject into the TriggerConfig
    interval: Optional[int] = Field(
        1, description="Interval in seconds between trigger evaluations"
    )
    last_run: Optional[float] = Field(
        time.time(), description="Timestamp of the last run"
    )


class TriggerResponse(BaseModel):
    """
    Abstract response schema for all triggers.
    """

    content: str
    triggered_at: float
    details: Dict[str, Any]


class Trigger(ABC):
    """
    Abstract base class for all triggers, using Pydantic for configuration.
    """

    name: str = "generic_trigger"  # Unique identifier for the trigger type
    config = TriggerConfig

    def __init__(self, config: TriggerConfig):
        """
        Initialize the Trigger with a validated configuration.

        :param config: A TriggerConfig object containing validated configuration.
        """
        self.config = config
        self.is_running = False
        self.last_run_time = config.last_run

    @abstractmethod
    async def execute(self, *args, **kwargs) -> Optional[TriggerResponse]:
        """
        Evaluate the trigger condition and return a typed response.

        :return: A TriggerResponse object if the condition is met, otherwise None.
        """
        pass

    async def run(self, report_callback: Callable[[str, TriggerResponse], None]):
        """
        Continuous trigger loop that evaluates the trigger and reports back when conditions are met.

        :param report_callback: A callback function to handle trigger events.
        """
        if self.is_running:
            LOGGER.warning(f"Trigger '{self.name}' is already running.")
            return

        self.is_running = True
        LOGGER.info(f"Starting trigger '{self.name}' loop.")

        while self.is_running:
            try:
                response = await self.execute()

                if response:
                    LOGGER.info(
                        f"Trigger '{self.name}' fired with event: {response.json()}"
                    )
                    await report_callback(self.name, response)

                await asyncio.sleep(self.config.interval)
            except asyncio.CancelledError:
                LOGGER.info(f"Trigger '{self.name}' loop cancelled.")
                break
            except Exception as e:
                LOGGER.error(
                    f"Error in trigger '{self.name}' loop: {str(e)}", exc_info=True
                )

        LOGGER.info(f"Trigger '{self.name}' loop stopped.")

    def stop(self):
        """
        Stop the trigger's loop.
        """
        if not self.is_running:
            LOGGER.warning(f"Trigger '{self.name}' is not running.")
            return

        self.is_running = False
        LOGGER.info(f"Stopping trigger '{self.name}'.")
