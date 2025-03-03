import logging
from typing import List, Optional

from pydantic import Field

from src.service.Action.actions import Action, ActionConfig, ActionResponse

LOGGER = logging.getLogger(__name__)


class GmailReceiveConfig(ActionConfig):
    """Configuration for Gmail receive action"""

    message_id: str = Field(..., description="Gmail message id")
    sender: str = Field(..., description="Sender mails")
    subject: str = Field(..., description="Mail Subjects")
    snippet: str = Field(..., description="Mail Snippet")
    received_at: str = Field(..., description="When did you receive the mail")
    filter_sender: Optional[str] = Field(None, description="Filter by sender email")
    filter_subject: Optional[str] = Field(
        None, description="Filter by subject contains"
    )
    filter_content: Optional[str] = Field(
        None, description="Filter by content contains"
    )


class GmailReceiveResponse(ActionResponse):
    """Response schema for Gmail receive action"""

    message_id: str
    sender: str
    subject: str
    snippet: str
    received_at: str


class GmailReceiveAction(Action):
    """
    Action to process Gmail data provided in the configuration and evaluate it against filters.
    """

    name = "gmail_receive"
    config = GmailReceiveConfig

    def __init__(self, config: GmailReceiveConfig):
        """
        Initialize with already extracted Gmail data.
        :param config: GmailReceiveConfig containing the data and optional filters.
        """
        super().__init__(config)

    async def execute(self, *args, **kwargs) -> Optional[GmailReceiveResponse]:
        """
        Process the provided Gmail data and evaluate it against the filters.
        """
        try:
            # Apply filters if they exist
            if (
                self.config.filter_sender
                and self.config.filter_sender.lower() not in self.config.sender.lower()
            ):
                return None

            if (
                self.config.filter_subject
                and self.config.filter_subject.lower()
                not in self.config.subject.lower()
            ):
                return None

            if (
                self.config.filter_content
                and self.config.filter_content.lower()
                not in self.config.snippet.lower()
            ):
                return None

            # Return a successful response if all filters pass
            return GmailReceiveResponse(
                success=True,
                message_id=self.config.message_id,
                sender=self.config.sender,
                subject=self.config.subject,
                snippet=self.config.snippet,
                received_at=self.config.received_at,
            )

        except Exception as e:
            LOGGER.error(f"Error processing Gmail data: {str(e)}")
            return None
