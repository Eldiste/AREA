from src.client.client import AbstractClient
from src.types.auth.register import RegisterConfig


class AreaClient(AbstractClient):
    """Non-authenticated client for interacting with the AREA API."""

    def get_headers(self) -> dict:
        """Return basic headers for non-authenticated requests."""
        return {"Content-Type": "application/json"}

    async def register(self, user_data: RegisterConfig):
        """
        Call the register API to create a new user.

        Args:
            user_data (RegisterConfig): The registration details.

        Returns:
            Tuple[int, dict]: HTTP status code and response JSON data.
        """
        return await self.request("POST", "auth/register", data=user_data.dict())

    def login(self, username_or_email: str, password: str):
        """
        Call the login API to authenticate a user.

        Args:
            username_or_email (str): Username or email of the user.
            password (str): Password of the user.

        Returns:
            Coroutine[Tuple[int, dict]]: A coroutine yielding (HTTP status code, JSON).
        """
        data = {"username_or_email": username_or_email, "password": password}
        return self.request("POST", "auth/login", data=data)

    def get_about(self):
        """
        Call the /about.json endpoint to retrieve information.

        Returns:
            Coroutine[Tuple[int, dict]]: A coroutine yielding (HTTP status code, JSON).
        """
        return self.request("GET", "about.json")

    def get_config_template(self, type_: str, name: str):
        """
        GET /api/config/{type}/{name}
        Fetch the configuration template for a specific trigger, action, or reaction.

        Example usage:
            get_config_template("trigger", "track_played")
            get_config_template("action", "print_message")
            get_config_template("reaction", "send_message")

        Args:
            type_ (str): "trigger", "action", or "reaction"
            name (str): The specific name (e.g., "track_played").

        Returns:
            Coroutine[Tuple[int, dict]]: (HTTP status code, JSON).
        """
        endpoint = f"api/config/{type_}/{name}"
        return self.request("GET", endpoint)

    def get_actions(self):
        """
        GET /api/actions
        Retrieve a list of all actions.

        Returns:
            Coroutine[Tuple[int, list]]: (HTTP status code, JSON array of actions).
        """
        return self.request("GET", "api/actions")

    def get_triggers(self):
        """
        GET /api/triggers
        Retrieve a list of all triggers.

        Returns:
            Coroutine[Tuple[int, list]]: (HTTP status code, JSON array of triggers).
        """
        return self.request("GET", "api/triggers")

    def get_reactions(self):
        """
        GET /api/reactions
        Retrieve a list of all reactions.

        Returns:
            Coroutine[Tuple[int, list]]: (HTTP status code, JSON array of reactions).
        """
        return self.request("GET", "api/reactions")

    def get_services(self):
        """
        GET /api/services
        Retrieve a list of services.

        Returns:
            Coroutine[Tuple[int, list]]: (HTTP status code, JSON array of services).
        """
        return self.request("GET", "api/services")
