import logging
from typing import List, Optional

from pydantic import Field

from src.service.Reaction.reactions import Reaction, ReactionConfig, ReactionResponse
from src.service.services.google.google import GoogleAPI

LOGGER = logging.getLogger(__name__)


class GmailSendReactionConfig(ReactionConfig):
    """
    Configuration for Gmail send reaction.
    """

    token: str = Field(..., description="Google access token for authentication.")
    to: str = Field(..., description="Email address of the recipient.")
    subject: str = Field(..., description="Subject of the email.")
    body: str = Field(..., description="Body of the email.")
    cc: Optional[List[str]] = Field(default=None, description="CC recipients.")
    bcc: Optional[List[str]] = Field(default=None, description="BCC recipients.")


class GmailSendReaction(Reaction):
    """
    Reaction that sends an email using Gmail.
    """

    name = "send_email"
    config = GmailSendReactionConfig

    def __init__(self, config: GmailSendReactionConfig):
        super().__init__(config)
        self.google_api = GoogleAPI(self.config.token)

    async def execute(
        self, data: dict, params: Optional[dict] = None
    ) -> ReactionResponse:
        """
        Send an email using the Gmail API.
        :param data: Action data containing dynamic content for the email.
        :param params: Optional additional parameters, including 'token'.
        :return: ReactionResponse indicating success or failure.
        """
        try:
            LOGGER.info(
                f"Executing GmailSendReaction with data: {data} and params: {params}"
            )

            # Validate and set the token
            if params and "token" in params:
                self.google_api.set_access_token(params["token"])
            elif not self.config.token:
                raise ValueError("No access token provided.")

            # Format the email content dynamically
            data_dict = data.dict() if hasattr(data, "dict") else data
            formatted_body = (
                self.config.body.format(**data_dict) if data_dict else self.config.body
            )
            formatted_subject = (
                self.config.subject.format(**data_dict)
                if data_dict
                else self.config.subject
            )

            LOGGER.info(
                f"Sending email to {self.config.to} with subject: {formatted_subject}"
            )

            # Send the email via Google API
            result = await self.google_api.send_email(
                to=self.config.to,
                subject=formatted_subject,
                body=formatted_body,
                cc=self.config.cc,
                bcc=self.config.bcc,
            )

            if result:
                LOGGER.info(f"Email sent successfully: {result}")
                return ReactionResponse(
                    success=True,
                    details={
                        "message_id": result.get("id"),
                        "thread_id": result.get("threadId"),
                        "to": self.config.to,
                        "subject": formatted_subject,
                    },
                )
            else:
                raise ValueError("Failed to send email.")

        except Exception as e:
            LOGGER.error(f"Error in GmailSendReaction: {e}", exc_info=True)
            return ReactionResponse(success=False, details={"error": str(e)})
