import logging
from pydantic import Field

from src.service.Action.actions import Action, ActionConfig, ActionResponse

LOGGER = logging.getLogger(__name__)


class DateActionConfig(ActionConfig):
    """
    Configuration schema for the DateAction.
    """

    # Spécifiez des champs pour la configuration si nécessaire
    date_message: str = Field(default="Default message for date action")


class DateActionResponse(ActionResponse):
    """
    Response schema for the DateAction.
    """

    # Spécifiez des champs pour la réponse
    success: bool
    details: dict


class DateAction(Action):
    """
    Action to perform an operation triggered by a specific date.
    """

    name: str = "date_action"
    config = DateActionConfig

    def __init__(self, config: DateActionConfig):
        """
        Initialize the DateAction with its configuration.

        :param config: DateActionConfig object containing action details.
        """
        super().__init__(config)

    async def execute(self, *args, **kwargs) -> DateActionResponse:
        """
        Execute the action and return a response.

        :return: DateActionResponse object containing the execution results.
        """
        LOGGER.info(f"Executing {self.name} with config: {self.config}")

        # Action exécutée pour le déclencheur sur une date spécifique
        LOGGER.info(f"Message associé à la date : {self.config.date_message}")

        return DateActionResponse(
            success=True,
            details={"message": f"Date action executed successfully with message: {self.config.date_message}"}
        )
