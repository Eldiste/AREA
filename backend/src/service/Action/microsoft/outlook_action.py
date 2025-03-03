import logging
from typing import Any, Dict, Optional

from pydantic import Field

from src.service.Action.actions import Action, ActionConfig, ActionResponse
from src.service.services.microsoft.outlook_api import OutlookAPI

LOGGER = logging.getLogger(__name__)


class OutlookReceiveConfig(ActionConfig):
    """Configuration for Outlook receive action"""

    query: str = Field("", description="Outlook search query to filter emails")


class OutlookReceiveAction(Action):
    """Action to detect new emails in Outlook based on criteria"""

    name = "outlook_receive"
    config = OutlookReceiveConfig

    def __init__(self, config: OutlookReceiveConfig):
        super().__init__(config)
        self.api = OutlookAPI()

    async def execute(
        self, data: Dict[str, Any], params: Optional[Dict[str, Any]] = None
    ) -> ActionResponse:
        """Check for emails matching the criteria"""
        try:
            if params and "token" in params:
                self.api.set_access_token(params["token"])

            messages = await self.api.list_messages(query=self.config.query)

            if not messages:
                return ActionResponse(
                    success=False, details={"error": "No matching messages found"}
                )

            message = messages[0]
            message_details = await self.api.get_message(message["id"])

            if not message_details:
                return ActionResponse(
                    success=False, details={"error": "Failed to get message details"}
                )

            return ActionResponse(
                success=True,
                details={
                    "message": "Email found successfully",
                    "message_id": message_details["id"],
                    "sender": message_details.get("from", {})
                    .get("emailAddress", {})
                    .get("address", "Unknown Sender"),
                    "subject": message_details.get("subject", "No Subject"),
                    "snippet": message_details.get("bodyPreview", ""),
                    "received_at": message_details.get("receivedDateTime", ""),
                },
            )

        except Exception as e:
            LOGGER.error(f"Error checking emails: {str(e)}")
            return ActionResponse(success=False, details={"error": str(e)})
