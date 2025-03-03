import logging
from typing import Any, Dict, List, Optional

from pydantic import Field

from src.service.Reaction.reactions import Reaction, ReactionConfig, ReactionResponse

from ...services.github.github import GitHubAPI

LOGGER = logging.getLogger(__name__)


class GitHubReactionConfig(ReactionConfig):
    """Configuration for GitHub reactions"""

    repository: str = Field(..., description="Target repository (format: owner/repo)")
    title: str = Field(..., description="Issue title")
    body: str = Field(..., description="Issue body")


class CreateIssueReaction(Reaction):
    """Reaction that creates a new issue in a repository"""

    name = "create_issue"
    config = GitHubReactionConfig

    def __init__(self, config: GitHubReactionConfig):
        super().__init__(config)
        self.github_api = GitHubAPI(token=config.token)

    async def execute(
        self, data: Dict[str, Any], params: Optional[Dict[str, Any]] = None
    ) -> ReactionResponse:
        """
        Create a new issue in the specified repository

        The title and body can include placeholders that will be replaced with values from the data:
        {commit_message}, {author}, {branch}, {commit_url}, etc.
        """
        try:
            LOGGER.info(f"Creating issue in repository: {self.config.repository}")
            LOGGER.debug(f"Data received: {data}")

            # Convert data to dictionary if needed
            data_dict = data.dict() if hasattr(data, "dict") else data

            title = self.config.title.format(**data_dict)
            body = self.config.body.format(**data_dict)

            LOGGER.info(f"Attempting to create issue with title: {title}")
            LOGGER.debug(f"Issue body: {body}")

            issue = await self.github_api.create_issue(
                repo_id=self.config.repository,
                title=title,
                body=body,
            )

            if issue:
                LOGGER.info(
                    f"Issue created successfully with number: {issue['number']}"
                )
                return ReactionResponse(
                    success=True,
                    details={
                        "message": "Issue created successfully",
                        "issue_number": issue["number"],
                        "issue_url": issue["html_url"],
                    },
                )
            else:
                LOGGER.error("Failed to create issue - API returned empty response")
                return ReactionResponse(
                    success=False, details={"error": "Failed to create issue"}
                )

        except Exception as e:
            LOGGER.error(f"Error creating issue: {str(e)}", exc_info=True)
            return ReactionResponse(success=False, details={"error": str(e)})
