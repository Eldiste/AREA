import base64
import logging
from email.mime.text import MIMEText
from typing import Any, Dict, List, Optional, Union

import aiohttp

LOGGER = logging.getLogger(__name__)


class GoogleAPI:
    """Google API client for various Google services"""

    def __init__(self, token: str):
        self.token = token
        self.base_url = "https://www.googleapis.com"

    async def _make_request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        json_data: Optional[Dict[str, Any]] = None,
    ) -> Union[Dict[str, Any], List[Dict[str, Any]], None]:
        """Utility function to make API requests."""
        url = f"{self.base_url}/{endpoint}"
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json",
        }

        async with aiohttp.ClientSession() as session:
            async with session.request(
                method, url, headers=headers, params=params, json=json_data
            ) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    LOGGER.error(f"Failed to {method} {endpoint}: {response.status}")
                    return [] if method == "GET" else None

    async def list_messages(self, query: str = "") -> List[Dict[str, Any]]:
        """List Gmail messages matching the query"""
        params = {"q": query} if query else {}
        data = await self._make_request(
            "GET", "gmail/v1/users/me/messages", params=params
        )
        return data.get("messages", [])

    async def get_message(self, message_id: str) -> Optional[Dict[str, Any]]:
        """Get Gmail message details by ID"""
        return await self._make_request(
            "GET", f"gmail/v1/users/me/messages/{message_id}"
        )

    async def send_email(
        self,
        to: str,
        subject: str,
        body: str,
        cc: Optional[List[str]] = None,
        bcc: Optional[List[str]] = None,
    ) -> Optional[Dict[str, Any]]:
        """Send an email using Gmail API"""
        try:
            # Create message
            message = MIMEText(body)
            message["to"] = to
            message["subject"] = subject

            if cc:
                message["cc"] = ", ".join(cc)
            if bcc:
                message["bcc"] = ", ".join(bcc)

            # Encode the message
            encoded_message = base64.urlsafe_b64encode(message.as_bytes()).decode()

            # Prepare the request
            data = {"raw": encoded_message}
            return await self._make_request(
                "POST", "gmail/v1/users/me/messages/send", json_data=data
            )

        except Exception as e:
            LOGGER.error(f"Error sending email: {str(e)}")
            return None

    async def create_calendar_event(self, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new calendar event."""
        return await self._make_request(
            "POST", "calendar/v3/calendars/primary/events", json_data=event_data
        )
