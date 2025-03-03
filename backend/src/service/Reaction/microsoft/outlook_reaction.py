import logging
from typing import Any, Dict, List, Optional

from pydantic import Field

from src.service.Reaction.reactions import Reaction, ReactionConfig, ReactionResponse
from src.service.services.microsoft.outlook_api import OutlookAPI

LOGGER = logging.getLogger(__name__)


class OutlookSendReactionConfig(ReactionConfig):
    """Configuration for Outlook send email reaction"""

    to: str = Field(..., description="Recipient email address")
    subject: str = Field(..., description="Email subject")
    body: str = Field(..., description="Email body")


class OutlookSendReactionResponse(ReactionResponse):
    """Response schema for Outlook send email reaction"""

    pass


class OutlookSendReaction(Reaction):
    """Reaction to send an email through Outlook"""

    name = "send_mail"
    config = OutlookSendReactionConfig

    def __init__(self, config: OutlookSendReactionConfig):
        super().__init__(config)
        self.api = OutlookAPI()  # Initialize without token, worker will inject it later

    async def execute(
        self, data: Dict[str, Any], params: Optional[Dict[str, Any]] = None
    ) -> OutlookSendReactionResponse:
        """Send an email using Outlook API"""
        try:
            self.api.set_access_token(self.config.token)

            subject = self.config.subject
            body = self.config.body

            if data:
                data_dict = data.dict() if hasattr(data, "dict") else data
                subject = subject.format(**data_dict)
                body = body.format(**data_dict)

            result = await self.api.send_email(
                to=self.config.to,
                subject=subject,
                body=body,
            )

            if not result:
                raise Exception("Failed to send email")

            return OutlookSendReactionResponse(
                success=True, details={"message": "Email sent successfully"}
            )

        except Exception as e:
            LOGGER.error(f"Error sending email: {str(e)}")
            return OutlookSendReactionResponse(success=False, details={"error": str(e)})
