import json
import logging
import time
from typing import Optional, Tuple

from pydantic import Field

from src.service.services.microsoft.outlook_api import OutlookAPI
from src.service.Trigger.triggers import Trigger, TriggerConfig, TriggerResponse

LOGGER = logging.getLogger(__name__)


class OutlookTriggerConfig(TriggerConfig):
    """Configuration for Outlook trigger"""

    query: Optional[str] = Field(
        None, description="Outlook search query to filter emails"
    )


class OutlookTriggerReponse(TriggerResponse):
    """Response schema for the Track Played Trigger."""

    message_id: str
    sender: str
    subject: str
    snippet: str
    received_at: str


class OutlookTrigger(Trigger):
    """Trigger that activates when a new email is received in Outlook"""

    name = "outlook_receive"
    config = OutlookTriggerConfig

    def __init__(self, config: OutlookTriggerConfig):
        super().__init__(config)
        self.last_check_time = time.time()
        self.api = OutlookAPI(token=config.token)

    async def execute(self, *args, **kwargs) -> Optional[OutlookTriggerReponse]:
        """Check for new emails since last check"""
        try:
            timestamp = time.strftime(
                "%Y-%m-%dT%H:%M:%SZ", time.gmtime(self.last_check_time)
            )
            query = f"receivedDateTime gt {timestamp}"
            if self.config.query:
                query = f"({query}) and ({self.config.query})"

            messages = await self.api.list_messages(query=query)

            if not messages:
                return None

            message = messages[0]
            message_details = await self.api.get_message(message["id"])

            if not message_details:
                return None

            self.last_check_time = time.time()

            return OutlookTriggerReponse(
                triggered_at=time.time(),
                details={
                    "event": "mail_received",
                },
                message_id=message_details["id"],
                sender=message_details.get("from", {})
                .get("emailAddress", {})
                .get("address", "Unknown Sender"),
                subject=message_details.get("subject", "No Subject"),
                snippet=message_details.get("bodyPreview", ""),
                received_at=message_details.get("receivedDateTime", ""),
                content=json.dumps(message_details),
            )

        except Exception as e:
            LOGGER.error(f"Error checking for new emails: {str(e)}")
            return None
