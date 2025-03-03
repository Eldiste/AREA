import logging
from typing import Optional

from pydantic import Field

from src.service.Action.actions import Action, ActionConfig, ActionResponse

LOGGER = logging.getLogger(__name__)


class SpotifyActionConfig(ActionConfig):
    """Configuration for Spotify actions"""

    track_id: str = Field(None, description="Track ID")
    track_name: str = Field(None, description="Track Name")
    artist_name: str = Field(None, description="Artist Name")
    album_name: str = Field(None, description="Album Name")

    content: str = Field(
        None, description="Additional content about the channel deletion."
    )


class SpotifyActionResponse(ActionResponse):
    """Response schema for Spotify actions"""

    track_id: str = Field(None, description="Track ID")
    track_name: str = Field(None, description="Track Name")
    artist_name: str = Field(None, description="Artist Name")
    album_name: str = Field(None, description="Album Name")

    content: str = Field(
        None, description="Additional content about the channel deletion."
    )


class TrackPlayedAction(Action):
    """Action that triggers when a track is played on Spotify"""

    name = "track_played"
    config = SpotifyActionConfig

    def __init__(self, config: SpotifyActionConfig):
        super().__init__(config)

    async def execute(self, *args, **kwargs) -> Optional[SpotifyActionResponse]:
        LOGGER.info(
            f"Track {self.config.track_name}  launch from {self.config.artist_name}"
        )
        # TODO: Add Filter

        return SpotifyActionResponse(
            success=True,
            track_id=self.config.track_id,
            track_name=self.config.track_name,
            artist_name=self.config.artist_name,
            album_name=self.config.album_name,
            content=self.config.content,
        )
