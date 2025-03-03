import logging
from typing import Any, Dict, List, Optional

import aiohttp

LOGGER = logging.getLogger(__name__)


class OutlookAPI:
    """Microsoft Graph API client for Outlook services"""

    def __init__(self, token: Optional[str] = None):
        self.token = token
        self.base_url = "https://graph.microsoft.com/v1.0"

    def set_access_token(self, access_token: str) -> None:
        """Set the access token for API requests"""
        self.token = access_token

    def get_headers(self) -> Dict[str, str]:
        """Get headers for API requests"""
        if not self.token:
            raise ValueError("No access token available")
        return {
            "Authorization": f"Bearer {self.token}",
        }

    async def list_messages(self, query: str = "") -> List[Dict[str, Any]]:
        """List Outlook messages matching the query"""
        url = f"{self.base_url}/me/messages"
        params = (
            {"$filter": query, "$orderby": "receivedDateTime desc"}
            if query
            else {"$orderby": "receivedDateTime desc"}
        )

        async with aiohttp.ClientSession() as session:
            async with session.get(
                url, headers=self.get_headers(), params=params
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    return data.get("value", [])
                else:
                    LOGGER.error(f"Failed to list messages: {response.status}")
                    return []

    async def get_message(self, message_id: str) -> Optional[Dict[str, Any]]:
        """Get Outlook message details by ID"""
        url = f"{self.base_url}/me/messages/{message_id}"

        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=self.get_headers()) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    LOGGER.error(
                        f"Failed to get message {message_id}: {response.status}"
                    )
                    return None

    async def send_email(
        self,
        to: str,
        subject: str,
        body: str,
        cc: Optional[List[str]] = None,
        bcc: Optional[List[str]] = None,
    ) -> bool:
        """Send an email using Outlook API"""
        url = f"{self.base_url}/me/sendMail"
        data = {
            "message": {
                "subject": subject,
                "body": {"contentType": "Text", "content": body},
                "toRecipients": [{"emailAddress": {"address": to}}],
                "ccRecipients": [
                    {"emailAddress": {"address": email}} for email in (cc or [])
                ],
                "bccRecipients": [
                    {"emailAddress": {"address": email}} for email in (bcc or [])
                ],
            }
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(
                url, headers=self.get_headers(), json=data
            ) as response:
                success = response.status == 202
                if not success:
                    LOGGER.error(f"Failed to send email: {response.status}")
                return success
