from src.client.area_client import AreaClient


class AuthenticatedAreaClient(AreaClient):
    """
    Authenticated client for interacting with the AREA API.
    Includes additional methods for /api/areas and /api/triggers.
    """

    def __init__(self, base_url: str, token: str):
        super().__init__(base_url)
        self.token = token

    def get_headers(self) -> dict:
        """Return headers with authentication."""
        return {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.token}",
        }

    async def get_user_email(self):
        """
        Call the GET /auth/user/email endpoint to retrieve the current user's email.

        Returns:
            Tuple[int, dict]: HTTP status code and response JSON data.
        """
        return await self.request("GET", "auth/user/email")

    async def get_areas(self):
        """
        GET /api/areas
        Retrieve a list of all Areas for the authenticated user.

        Returns:
            Tuple[int, list]: HTTP status code and a list of Areas (as JSON).
        """
        return await self.request("GET", "api/areas")

    async def create_area(
        self,
        action_id: int,
        reaction_id: int,
        action_config: dict,
        reaction_config: dict,
    ):
        """
        POST /api/areas
        Create a new Area.

        Args:
            action_id (int): ID of the action.
            reaction_id (int): ID of the reaction.
            action_config (dict): Configuration for the action.
            reaction_config (dict): Configuration for the reaction.

        Returns:
            Tuple[int, dict]: HTTP status code and the created Area (as JSON).
        """
        data = {
            "action_id": action_id,
            "reaction_id": reaction_id,
            "action_config": action_config,
            "reaction_config": reaction_config,
        }
        return await self.request("POST", "api/areas", data=data)

    async def get_area(self, area_id: int):
        """
        GET /api/areas/{area_id}
        Retrieve a single Area by its ID.

        Args:
            area_id (int): The ID of the Area to retrieve.

        Returns:
            Tuple[int, dict]: HTTP status code and the Area details (as JSON).
        """
        return await self.request("GET", f"api/areas/{area_id}")

    async def update_area(
        self,
        area_id: int,
        action_id: int,
        reaction_id: int,
        action_config: dict,
        reaction_config: dict,
    ):
        """
        PUT /api/areas/{area_id}
        Update an existing Area.

        Args:
            area_id (int): The ID of the Area to update.
            action_id (int): New action ID.
            reaction_id (int): New reaction ID.
            action_config (dict): Updated action config.
            reaction_config (dict): Updated reaction config.

        Returns:
            Tuple[int, dict]: HTTP status code and updated Area (as JSON).
        """
        data = {
            "action_id": action_id,
            "reaction_id": reaction_id,
            "action_config": action_config,
            "reaction_config": reaction_config,
        }
        return await self.request("PUT", f"api/areas/{area_id}", data=data)

    async def delete_area(self, area_id: int):
        """
        DELETE /api/areas/{area_id}
        Delete an existing Area.

        Args:
            area_id (int): The ID of the Area to delete.

        Returns:
            Tuple[int, dict|str]: HTTP status code and response data (often just a message).
        """
        return await self.request("DELETE", f"api/areas/{area_id}")

    async def create_trigger(
        self,
        name: str,
        area_id: int,
        config: dict,
    ):
        """
        POST /api/triggers
        Create a new trigger for an existing area.

        Args:
            name (str): Name of the trigger.
            area_id (int): The ID of the Area to which this trigger belongs.
            config (dict): Configuration details for the trigger
                           (e.g., interval or other custom keys).

        Returns:
            Tuple[int, dict]: HTTP status code and the created trigger (as JSON).
        """
        data = {
            "name": name,
            "area_id": area_id,
            "config": config,
        }
        return await self.request("POST", "api/triggers", data=data)

    async def get_connected_services(self):
        """
        GET /api/user_services/connected
        Retrieve a list of service names that the current user is connected to.

        Returns:
            Tuple[int, list]: HTTP status code and a list of service names (as JSON).
        """
        return await self.request("GET", "api/user_services/connected")
