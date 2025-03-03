from abc import ABC, abstractmethod
from typing import Any, Dict

from pydantic import BaseModel
from typing_extensions import Optional


class ReactionConfig(BaseModel):
    """
    Base configuration schema for all reactions.
    """

    token: Optional[str]
    description: str = "Base reaction configuration"


class ReactionResponse(BaseModel):
    """
    Base response schema for all reactions.
    """

    success: bool  # Indicates if the reaction was successfully executed
    details: Dict[str, Any]  # Additional details specific to the reaction


class Reaction(ABC):
    """
    Abstract base class for all reactions, using ReactionConfig for configuration
    and ReactionResponse for typed responses.
    """

    name: str = "generic_reaction"
    config = ReactionConfig

    def __init__(self, config: ReactionConfig):
        """
        Initialize the Reaction with a validated configuration.

        :param config: A validated ReactionConfig object.
        """
        self.config = config

    @abstractmethod
    async def execute(self, *args, **kwargs) -> ReactionResponse:
        """
        Perform the reaction logic.

        :return: A ReactionResponse object containing the execution results.
        """
        pass
