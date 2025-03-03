import logging
import time
from typing import Optional

from pydantic import Field

from src.service.services.google.google import GoogleAPI
from src.service.Trigger.triggers import Trigger, TriggerConfig, TriggerResponse

LOGGER = logging.getLogger(__name__)


class GmailTriggerConfig(TriggerConfig):
    """Configuration for Gmail trigger"""

    pass


class GmailTriggerResponse(TriggerResponse):
    """Response schema for Gmail trigger"""

    # Gmail specific fields
    message_id: str
    sender: str
    subject: str
    snippet: str
    received_at: str


class GmailTrigger(Trigger):
    """Trigger that activates when a new email is received in Gmail"""

    name = "gmail_receive"
    config = GmailTriggerConfig

    def __init__(self, config: GmailTriggerConfig):
        super().__init__(config)
        self.last_check_time = time.time()
        self.api = GoogleAPI(token=config.token)

    async def execute(self, *args, **kwargs) -> Optional[GmailTriggerResponse]:
        """Check for new emails since last check"""
        try:
            # Get new messages since last check
            query = f"after:{int(self.last_check_time)}"
            messages = await self.api.list_messages(query=query)

            if not messages:
                return None

            # Get the most recent message details
            message = messages[0]  # Most recent message
            message_details = await self.api.get_message(message["id"])

            if not message_details:
                return None

            # Update last check time
            self.last_check_time = time.time()

            # Extract relevant information
            headers = message_details.get("payload", {}).get("headers", [])
            subject = next(
                (h["value"] for h in headers if h["name"].lower() == "subject"),
                "No Subject",
            )
            sender = next(
                (h["value"] for h in headers if h["name"].lower() == "from"),
                "Unknown Sender",
            )

            return GmailTriggerResponse(
                content=str(message_details),  # Full message as content
                triggered_at=time.time(),
                details={"event": "mail_received"},
                message_id=message_details["id"],
                sender=sender,
                subject=subject,
                snippet=message_details.get("snippet", ""),
                received_at=message_details.get("internalDate", ""),
            )

        except Exception as e:
            LOGGER.error(f"Error checking for new emails: {str(e)}")
            return None
