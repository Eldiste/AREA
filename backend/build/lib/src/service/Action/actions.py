from src.service.base import BaseComponent


class Action(BaseComponent):
    """
    Base Action class to define a common interface for all actions.
    """

    name = "generic_action"

    def execute(self, *args, **kwargs):
        """
        Perform the action. Subclasses must implement their specific logic here.
        """
        raise NotImplementedError("Subclasses must implement the `execute` method.")
