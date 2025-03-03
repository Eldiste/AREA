import asyncio
import logging
from typing import Dict, List

from ...Trigger.discord.new_message_in_channel import NewMessageInChannelTrigger
from .dicord import DiscordAPI

LOGGER = logging.getLogger(__name__)


class DiscordGateway:
    def __init__(self, token: str):
        self.token = token
        self.ws = None
        self.subscriptions: Dict[str, List["NewMessageInChannelTrigger"]] = {}

    async def start_connection(self):
        """Start the WebSocket connection to Discord and manage events."""
        self.ws = await self._connect_to_discord_gateway()
        await self._listen_for_events()

    async def _connect_to_discord_gateway(self):
        """Simulated connection to Discord gateway."""
        # Logic for initiating the WebSocket connection to Discord
        # You would need to use a library like discord.py here to establish the connection
        pass

    async def _listen_for_events(self):
        """Listen for incoming events from Discord."""
        while True:
            event = await self.ws.receive()
            await self._handle_event(event)

    async def _handle_event(self, event: dict):
        """Filter events and route them to the relevant trigger."""
        channel_id = event.get("channel_id")
        user_id = event.get("user_id")

        # Route the event to the appropriate triggers
        if channel_id and channel_id in self.subscriptions:
            for trigger in self.subscriptions[channel_id]:
                await trigger.process_event(event)

        if user_id and user_id in self.subscriptions:
            for trigger in self.subscriptions[user_id]:
                await trigger.process_event(event)

    def subscribe_to_channel(
        self, channel_id: str, trigger: "NewMessageInChannelTrigger"
    ):
        """Subscribe a trigger to a specific channel."""
        if channel_id not in self.subscriptions:
            self.subscriptions[channel_id] = []
        self.subscriptions[channel_id].append(trigger)
        # Tell Discord to listen to this channel's messages (via WebSocket)
        self._add_subscription_to_discord(channel_id)

    def subscribe_to_user(self, user_id: str, trigger: "NewMessageInChannelTrigger"):
        """Subscribe a trigger to a specific user."""
        if user_id not in self.subscriptions:
            self.subscriptions[user_id] = []
        self.subscriptions[user_id].append(trigger)
        # Tell Discord to listen to this user's messages (via WebSocket)
        self._add_subscription_to_discord(user_id)

    def _add_subscription_to_discord(self, identifier: str):
        """Inform Discord that we want to listen to this identifier (channel or user)."""
        pass  # This would be an API call to subscribe to a channel's or user's messages
