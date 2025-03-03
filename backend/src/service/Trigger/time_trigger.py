import logging
import time
from typing import Optional

from src.service.Trigger.triggers import Trigger, TriggerConfig, TriggerResponse

LOGGER = logging.getLogger(__name__)


class TimeTriggerConfig(TriggerConfig):
    """
    Base configuration schema for all triggers.
    """

    time: int

class TimeTriggerResponse(TriggerResponse):
    """
    Response schema for the TimeTrigger.
    """

    event_time: float


class TimeTrigger(Trigger):
    """
    Trigger that activates at a regular interval.
    """

    name = "time_trigger"
    config = TriggerConfig

    def __init__(self, config: TriggerConfig):
        """
        Initialize the TimeTrigger with the base configuration.

        :param config: TriggerConfig object containing interval and last_run time.
        """
        super().__init__(config)

    async def execute(self, *args, **kwargs) -> Optional[TimeTriggerResponse]:
        """
        Evaluate if the interval has passed since the last run.

        :return: TimeTriggerResponse
        """
        current_time = time.time()
        LOGGER.error(f"{current_time}")
        if current_time - self.config.last_run >= self.config.interval:
            self.config.last_run = current_time
            LOGGER.info(f"TimeTrigger fired at {current_time}.")
            return TimeTriggerResponse(
                details={
                    "event_data" : "time_trigger"
                },
                event_time=current_time,
                triggered_at=current_time,
                content=f"{current_time}",
            )
        return None
