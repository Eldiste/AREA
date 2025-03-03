import logging
from pydantic import Field

from src.service.Action.actions import Action, ActionConfig, ActionResponse

LOGGER = logging.getLogger(__name__)


class HourlyActionConfig(ActionConfig):
    """
    Configuration schema for the HourlyAction.
    """

    # Spécifiez des champs pour la configuration de l'action horaire
    time_message: str = Field(default="Default message for time of day action")


class HourlyActionResponse(ActionResponse):
    """
    Response schema for the HourlyAction.
    """

    # Spécifiez des champs pour la réponse
    success: bool
    details: dict


class HourlyAction(Action):
    """
    Action to perform an operation triggered at a specific time of day.
    """

    name: str = "time_of_day_action"
    config = HourlyActionConfig

    def __init__(self, config: HourlyActionConfig):
        """
        Initialize the HourlyAction with its configuration.

        :param config: HourlyActionConfig object containing action details.
        """
        super().__init__(config)

    async def execute(self, *args, **kwargs) -> HourlyActionResponse:
        """
        Execute the action and return a response.

        :return: HourlyActionResponse object containing the execution results.
        """
        LOGGER.info(f"Executing {self.name} with config: {self.config}")

        # Action exécutée à un horaire spécifique
        LOGGER.info(f"Message associé à l'horaire : {self.config.time_message}")

        return HourlyActionResponse(
            success=True,
            details={"message": f"Time of day action executed successfully with message: {self.config.time_message}"}
        )
