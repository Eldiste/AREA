import logging
from abc import ABC, abstractmethod

import aiohttp
from rich.console import Console

logger = logging.getLogger(__name__)


class AbstractClient(ABC):
    """Abstract base client for handling HTTP requests."""

    def __init__(self, base_url: str):
        self.base_url = base_url

    @abstractmethod
    def get_headers(self) -> dict:
        """Abstract method to get headers for the client."""
        pass

    async def request(self, method: str, endpoint: str, data=None, params=None):
        """
        Perform an asynchronous HTTP request using aiohttp.

        Args:
            method (str): HTTP method (GET, POST, etc.).
            endpoint (str): API endpoint (relative to base_url).
            data (dict, optional): JSON data to send in the request body.
            params (dict, optional): Query parameters for the request.

        Returns:
            Tuple[int, dict]: HTTP status code and response JSON data.
        """
        url = f"{self.base_url}/{endpoint}"
        headers = self.get_headers()
        logger.debug(f"[bold green]Requesting:[/bold green] {url} with method {method}")

        async with aiohttp.ClientSession() as session:
            try:
                async with session.request(
                    method=method,
                    url=url,
                    headers=headers,
                    json=data,
                    params=params,
                ) as response:
                    response_data = await response.json()
                    logger.debug(f"[bold cyan]Response:[/bold cyan] {response_data}")
                    return response.status, response_data
            except Exception as exc:
                logger.error(f"[bold red]Request failed: {exc}[/bold red]")
                raise
