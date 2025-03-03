import logging

import aiohttp

from src.service.Action.actions import Action

LOGGER = logging.getLogger(__name__)


class HttpGetAction(Action):
    name = "http_get_action"

    def __init__(self, **params):
        """
        Initialize the action with parameters.
        :param params: Dictionary of parameters, including 'url'.
        """
        self.params = params  # Store all parameters for later use
        if not self.params.get("url"):
            raise ValueError("URL parameter is required for HttpGetAction.")

    async def execute(self, **kwargs):
        """
        Perform an HTTP GET request using the stored parameters.
        """
        url = self.params["url"]
        LOGGER.info(f"Executing HttpGetAction with URL: {url}")
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                data = await response.text()
                LOGGER.info(f"HTTP GET to {url} returned status {response.status}")
                return data
