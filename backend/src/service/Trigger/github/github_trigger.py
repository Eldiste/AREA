import json
import logging
import time
from typing import Any, Dict, Optional, Tuple

from pydantic import Field

from ...services.github.github import GitHubAPI
from ..triggers import Trigger, TriggerConfig, TriggerResponse

LOGGER = logging.getLogger(__name__)


class GitHubTriggerConfig(TriggerConfig):
    """Configuration for GitHub triggers"""

    repo: str = Field(..., description="Repo URL")


class GitHubTriggerResponse(TriggerResponse):
    """Configuration for GitHub triggers"""

    commit_sha: str = Field(..., description="SHA of the commit")
    commit_message: str = Field(..., description="Message of the commit")
    author: str = Field(..., description="Author of the commit")
    branch: str = Field(..., description="Branch of the commit")
    commit_url: str = Field(..., description="Commit URL")


class NewPushTrigger(Trigger):
    """Trigger that activates when a new push is made to a repository"""

    name = "new_push"
    config = GitHubTriggerConfig

    def __init__(self, config: GitHubTriggerConfig):
        super().__init__(config)
        self.github_api = GitHubAPI(token=config.token)
        self.last_commit_sha = None

    async def execute(self, *args, **kwargs) -> Optional[GitHubTriggerResponse]:
        """Check for new pushes to the repository"""
        LOGGER.info(f"Executing NewPushTrigger with kwargs: {kwargs}")
        LOGGER.info(f"Attempting to fetch commits for repository: {self.config.repo}")

        try:
            commits = await self.github_api.get_repo_commits(self.config.repo)
            if not commits:
                LOGGER.info("No commits found in repository")
                return None

            latest_commit = commits[0]
            latest_sha = latest_commit["sha"]

            # Only trigger if it's a new commit
            if latest_sha == self.last_commit_sha:
                LOGGER.info(f"No new commits (last commit SHA: {self.last_commit_sha})")
                return None

            self.last_commit_sha = latest_sha
            LOGGER.info(f"New commit found: {latest_sha}")

            # Extract relevant commit information
            return GitHubTriggerResponse(
                commit_sha=latest_sha,
                commit_message=latest_commit["commit"]["message"],
                author=latest_commit["commit"]["author"]["name"],
                branch=latest_commit.get(
                    "branch", "main"
                ),  # Default to main if not specified
                commit_url=latest_commit["html_url"],
                content=json.dumps(latest_commit),  # Full commit data as content
                triggered_at=time.time(),
                details={"event": "new_push", "repository": self.config.repo},
            )

        except Exception as e:
            LOGGER.error(f"Error checking for new pushes: {str(e)}")
            return None
