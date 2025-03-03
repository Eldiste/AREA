from abc import ABC, abstractmethod

from pydantic import BaseModel


class BaseComponent(ABC):
    """
    Abstract base class for all components with integrated configuration.
    """

    name: str

    def __init__(self, config: BaseModel):
        """
        Initialize the component with a Pydantic configuration.

        :param config: A Pydantic model containing validated configuration.
        """
        self.config = config

    @abstractmethod
    def execute(self, *args, **kwargs):
        """
        Execute the component logic.
        """
        pass
