import logging
from typing import Any, Dict, Optional

from pydantic import Field

from src.service.Action.actions import Action, ActionConfig, ActionResponse
from src.service.services.github.github import GitHubAPI

LOGGER = logging.getLogger(__name__)


class GitHubActionConfig(ActionConfig):
    """Configuration for GitHub actions"""

    content: str = Field(..., description="The content of the message")
    commit_sha: str = Field(..., description="SHA of the commit")
    commit_message: str = Field(..., description="Message of the commit")
    author: str = Field(..., description="Author of the commit")
    branch: str = Field(..., description="Branch of the commit")
    commit_url: str = Field(..., description="Commit URL")


class GitHubActionResponse(ActionResponse):
    """Configuration for GitHub actions"""

    commit_sha: str = Field(..., description="SHA of the commit")
    commit_message: str = Field(..., description="Message of the commit")
    author: str = Field(..., description="Author of the commit")
    branch: str = Field(..., description="Branch of the commit")
    commit_url: str = Field(..., description="Commit URL")
    content: str


class NewPushAction(Action):
    """Action that processes new push events"""

    name = "new_push"
    config = GitHubActionConfig

    def __init__(self, config: GitHubActionConfig):
        super().__init__(config)

    async def execute(self, *args, **kwargs) -> Optional[GitHubActionResponse]:
        """
        Process a new push event.
        The data parameter contains information about the push event from the trigger.
        """
        try:
            # The data already contains the push information from the trigger
            # We can process it or enrich it here if needed
            return GitHubActionResponse(
                success=True,
                details={
                    "event": self.name,
                },
                content=self.config.content,
                commit_sha=self.config.commit_sha,
                commit_message=self.config.commit_message,
                author=self.config.author,
                branch=self.config.branch,
                commit_url=self.config.commit_url,
            )

        except Exception as e:
            LOGGER.error(f"Error processing push event: {str(e)}")
            return None
