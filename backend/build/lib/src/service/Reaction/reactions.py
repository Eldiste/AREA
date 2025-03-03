from src.service.base import BaseComponent


class Reaction(BaseComponent):
    """
    Base Reaction class to define a common interface for all reactions.
    """

    name = "generic_reaction"

    def execute(self, *args, **kwargs):
        """
        Perform the reaction. Subclasses must implement their specific logic here.
        """
        raise NotImplementedError("Subclasses must implement the `execute` method.")
