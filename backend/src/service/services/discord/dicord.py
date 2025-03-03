import asyncio
import json
import logging

import aiohttp
import websockets

# Logging setup
logging.basicConfig(level=logging.DEBUG)
LOGGER = logging.getLogger(__name__)


class DiscordAPI:
    """Discord WebSocket Connection."""

    def __init__(
        self, token: str, uri: str = "wss://gateway.discord.gg/?v=10&encoding=json"
    ):
        self.token = token
        self.uri = uri
        self.websocket = None
        self.sequence = None
        self.heartbeat_interval = None

        # Event queues for different types
        self.event_queues = {
            "MESSAGE_CREATE": asyncio.Queue(),
            "GUILD_ROLE_CREATE": asyncio.Queue(),
            "CHANNEL_CREATE": asyncio.Queue(),
            "GUILD_MEMBER_ADD": asyncio.Queue(),
            "GUILD_MEMBER_REMOVE": asyncio.Queue(),
            "MESSAGE_UPDATE": asyncio.Queue(),
            "MESSAGE_DELETE": asyncio.Queue(),
            "CHANNEL_UPDATE": asyncio.Queue(),
            "CHANNEL_DELETE": asyncio.Queue(),
            "GUILD_UPDATE": asyncio.Queue(),
            # Add other events as needed...
        }

        # Event handlers dynamically registered by event type
        self._event_handlers = {
            event: self.create_generic_handler(event) for event in self.event_queues
        }

    async def connect(self):
        """Connect to Discord WebSocket and handle IDENTIFY payload."""
        self.websocket = await websockets.connect(self.uri)
        await self.send_identify()
        asyncio.create_task(self.listen())  # Run listen as a separate task

    async def send_identify(self):
        """Send IDENTIFY payload to Discord."""
        payload = {
            "op": 2,
            "d": {
                "token": self.token,
                "intents": 32767 | (1 << 15),  # Listen to all intents
                "properties": {
                    "$os": "linux",
                    "$browser": "aiohttp",
                    "$device": "aiohttp",
                },
            },
        }
        await self.websocket.send(json.dumps(payload))

    async def listen(self):
        """Listen for events from Discord WebSocket."""
        while True:
            try:
                message = await self.websocket.recv()
                await self.handle_message(message)
            except websockets.ConnectionClosed as e:
                LOGGER.warning(f"WebSocket connection closed: {e}. Reconnecting...")
                await self.reconnect()
                break
            except Exception as e:
                LOGGER.error(f"Unexpected error while listening to WebSocket: {e}")
                break

    async def handle_message(self, message: str):
        """Handle incoming messages from Discord WebSocket."""
        try:
            event = json.loads(message)

            if event["op"] == 10:  # HELLO event
                self.heartbeat_interval = event["d"]["heartbeat_interval"] / 1000
                asyncio.create_task(self.send_heartbeat())
            elif event.get("t"):  # Check if the event type exists
                event_type = event["t"]
                event_data = event["d"]
                handler = self._event_handlers.get(event_type)
                if handler:
                    await handler(event_data)
        except json.JSONDecodeError as e:
            LOGGER.error(f"Failed to decode message: {e}")
        except KeyError as e:
            LOGGER.error(f"Missing expected key in event: {e}")

    def create_generic_handler(self, event_type: str):
        """Create a generic handler for events."""

        async def handler(data: dict):
            LOGGER.info(f"Event {event_type} received: {json.dumps(data, indent=2)}")
            queue = self.event_queues.get(event_type)
            if queue:
                await queue.put(data)

        return handler

    async def send_heartbeat(self):
        """Send heartbeat to keep the connection alive."""
        while True:
            await asyncio.sleep(self.heartbeat_interval)
            try:
                if self.websocket.state != websockets.protocol.State.OPEN:
                    LOGGER.warning("WebSocket is not open. Stopping heartbeat.")
                    break

                heartbeat_payload = {"op": 1, "d": self.sequence}
                await self.websocket.send(json.dumps(heartbeat_payload))
            except websockets.ConnectionClosed as e:
                LOGGER.warning(f"WebSocket connection closed: {e}. Stopping heartbeat.")
                break
            except Exception as e:
                LOGGER.error(f"Unexpected error while sending heartbeat: {e}")
                break

    async def wait_for_event(self, event_type: str, filter_fn=None):
        """
        Generator to wait for a specific event.
        :param event_type: The type of the event to wait for.
        :param filter_fn: Optional function to filter events.
        """
        if event_type not in self.event_queues:
            raise ValueError(f"Unsupported event type: {event_type}")

        while True:
            try:
                event_data = await self.event_queues[event_type].get()
                if not filter_fn or filter_fn(event_data):
                    yield event_data
            except asyncio.QueueEmpty:
                LOGGER.warning(f"Queue for event {event_type} is empty.")
            except Exception as e:
                LOGGER.error(f"Error while waiting for event {event_type}: {e}")

    async def reconnect(self):
        """Reconnect to the Discord WebSocket."""
        try:
            await self.connect()
        except Exception as e:
            LOGGER.error(f"Failed to reconnect: {e}")
            await asyncio.sleep(5)
            await self.reconnect()

    async def send_message(self, channel_id: str, content: str):
        """Send a message to a specific channel."""
        if not channel_id or not content:
            LOGGER.error("Channel ID and message content must be provided.")
            return

        try:
            url = f"https://discord.com/api/v10/channels/{channel_id}/messages"
            headers = {
                "Authorization": f"Bot {self.token}",
                "Content-Type": "application/json",
            }
            payload = {"content": content}

            async with aiohttp.ClientSession() as session:
                async with session.post(url, headers=headers, json=payload) as response:
                    if response.status == 200:
                        LOGGER.info(
                            f"Message sent successfully to channel {channel_id}: {content}"
                        )
                    else:
                        LOGGER.error(
                            f"Failed to send message. Status: {response.status}"
                        )
        except Exception as e:
            LOGGER.error(f"Error sending message: {e}")
