import logging
import time

from src.service.Trigger.triggers import Trigger

LOGGER = logging.getLogger(__name__)


class TimeTrigger(Trigger):
    name = "time_trigger"

    async def execute(self, subject: dict, *args, **kwargs) -> bool:
        """
        Check if the current time exceeds the last_run + interval.
        """
        current_time = subject.get("current_time", time.time())
        last_run = self.config.get("last_run", 0)
        interval = self.config.get("interval", 60)

        if current_time >= last_run + interval:
            # Trigger condition met
            return True

        # Skip execution if the interval has not yet passed
        return False
