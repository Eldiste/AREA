from abc import ABC, abstractmethod


class BaseComponent(ABC):
    name: str

    def __init__(self, **kwargs):
        """Initialize the component with arbitrary arguments"""
        self.config = kwargs

    @abstractmethod
    def execute(self, *args, **kwargs):
        """Execute the component logic"""
        pass
