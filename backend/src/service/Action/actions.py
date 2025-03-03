from abc import ABC, abstractmethod
from typing import Any, Dict, Optional

from pydantic import BaseModel, Extra, Field

from src.service.config.filter import FilterConfig


class ActionConfig(BaseModel):
    """
    Base configuration schema for all actions.
    """

    description: str = "Base action configuration"
    filter: Optional[FilterConfig] = Field(
        None,
        description="Optional filter configuration to apply additional criteria",
    )


class ActionResponse(BaseModel):
    """
    Base response schema for all actions.
    """

    success: bool  # Indicates if the action was successfully executed
    details: Optional[Dict[str, Any]] = None

    class Config:
        extra = Extra.allow


class Action(ABC):
    """
    Abstract base class for all actions, using ActionConfig for configuration and
    ActionResponse for typed responses.
    """

    name: str = "generic_action"
    config = ActionConfig

    def __init__(self, config: ActionConfig):
        """
        Initialize the Action with a validated configuration.

        :param config: A validated ActionConfig object.
        """
        self.config = config

    @abstractmethod
    async def execute(self, *args, **kwargs) -> ActionResponse:
        """
        Perform the action logic.

        :return: An ActionResponse object containing the execution results.
        """
        pass
