import logging
from typing import Any, Dict, List, Union

import aiohttp

LOGGER = logging.getLogger(__name__)


class GitHubAPI:
    """GitHub API Client."""

    def __init__(self, token: str, api_base_url: str = "https://api.github.com"):
        self.token = token
        self.api_base_url = api_base_url

    async def _make_request(
        self, endpoint: str, method: str = "GET", data: Dict[str, Any] = None
    ) -> Union[Dict[str, Any], List[Dict[str, Any]]]:
        """Utility function to make API requests."""
        url = f"{self.api_base_url}/{endpoint}"
        headers = {
            "Authorization": f"token {self.token}",
            "Accept": "application/vnd.github.v3+json",
        }
        async with aiohttp.ClientSession() as session:
            if method == "GET":
                async with session.get(url, headers=headers) as response:
                    if response.status == 200:
                        data = await response.json()
                        # Check if the response is a list and return it as such
                        if isinstance(data, list):
                            return data
                        return data
                    else:
                        LOGGER.error(
                            f"Failed to fetch data from {endpoint}: {response.status}"
                        )
                        return (
                            []
                            if endpoint in ["user/repos", "repos/{repo_id}/issues"]
                            else {}
                        )
            elif method == "POST":
                async with session.post(url, headers=headers, json=data) as response:
                    if response.status in [200, 201]:
                        return await response.json()
                    else:
                        error_data = await response.text()
                        LOGGER.error(
                            f"Failed to post data to {endpoint}: {response.status}, {error_data}"
                        )
                        return {}

    async def get_user_repos(self) -> List[Dict[str, Any]]:
        """Fetch all repositories of the authenticated user."""
        return await self._make_request("user/repos")

    async def get_repo(self, repo_id: str) -> Dict[str, Any]:
        """Fetch details of a specific repository."""
        return await self._make_request(f"repos/{repo_id}")

    async def get_repo_issues(self, repo_id: str) -> List[Dict[str, Any]]:
        """Fetch issues from a specific repository."""
        return await self._make_request(f"repos/{repo_id}/issues")

    async def get_user(self) -> Dict[str, Any]:
        """Fetch the authenticated user's GitHub profile details."""
        return await self._make_request("user")

    async def get_repo_commits(self, repo_id: str) -> List[Dict[str, Any]]:
        """Fetch commits from a specific repository."""
        return await self._make_request(f"repos/{repo_id}/commits")

    async def create_issue(self, repo_id: str, title: str, body: str) -> Dict[str, Any]:
        """Create a new issue in a repository."""
        return await self._make_request(
            f"repos/{repo_id}/issues",
            method="POST",
            data={"title": title, "body": body},
        )
