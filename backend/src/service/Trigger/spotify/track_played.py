import asyncio
import json
import logging
import time
from typing import Optional

from pydantic import Field
from typing_extensions import Optional

from src.service.services.spotify.spotify_api import SpotifyAPIClient
from src.service.Trigger.triggers import Trigger, TriggerConfig, TriggerResponse

LOGGER = logging.getLogger(__name__)


class SpotifyTriggerConfig(TriggerConfig):
    """Configuration for Spotify triggers"""

    pass


class TrackPlayedTriggerResponse(TriggerResponse):
    """Response schema for the Track Played Trigger."""

    track_id: str
    track_name: str
    artist_name: str
    album_name: str


class CurrentlyPlayingTrigger(Trigger):
    """Trigger that activates when a new track starts playing on Spotify"""

    name = "track_played"
    config = SpotifyTriggerConfig

    def __init__(self, config: SpotifyTriggerConfig):
        super().__init__(config)
        self.last_track_id = None
        self.spotify_api = SpotifyAPIClient(token=config.token)

    async def execute(self, *args, **kwargs) -> Optional[TrackPlayedTriggerResponse]:
        """Check for currently playing track and return when a new track is detected."""
        LOGGER.info("Running Track")
        while True:
            try:
                current_track = await self.spotify_api.get_currently_playing()
                LOGGER.info(current_track)
                if (
                    not current_track
                    or "item" not in current_track
                    or not current_track["item"]
                ):
                    LOGGER.info("No Track found skip")
                    await asyncio.sleep(self.config.interval)
                    continue

                track = current_track["item"]
                track_id = track["id"]

                if track_id != self.last_track_id:
                    self.last_track_id = track_id

                    track_info = TrackPlayedTriggerResponse(
                        triggered_at=time.time(),
                        details={
                            "event": "track_played",
                        },
                        track_id=track_id,
                        track_name=track["name"],
                        artist_name=(
                            track["artists"][0]["name"]
                            if track["artists"]
                            else "Unknown Artist"
                        ),
                        album_name=(
                            track["album"]["name"]
                            if "album" in track
                            else "Unknown Album"
                        ),
                        content=json.dumps(track),
                    )

                    LOGGER.info(f"New track detected: {track_info}")
                    return track_info

            except Exception as e:
                LOGGER.error(f"Error checking currently playing track: {str(e)}")

            # Sleep before the next check
            await asyncio.sleep(self.config.interval)
