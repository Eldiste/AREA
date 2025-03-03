import logging
from typing import Any, Dict, Optional

from pydantic import Field

LOGGER = logging.getLogger(__name__)

from src.service.Reaction.reactions import Reaction, ReactionConfig, ReactionResponse
from src.service.services.spotify.spotify_api import SpotifyAPIClient


class SpotifyReactionConfig(ReactionConfig):
    """Configuration for Spotify reactions"""

    playlist_id: Optional[str] = Field(
        None, description="Target playlist ID for playlist operations"
    )
    position: Optional[int] = Field(
        None, description="Position to insert tracks in playlist"
    )


class AddToPlaylistReaction(Reaction):
    """Reaction that adds tracks to a specified playlist"""

    name = "add_to_playlist"
    config = SpotifyReactionConfig

    def __init__(self, config: SpotifyReactionConfig):
        super().__init__(config)
        self.spotify_api = (
            SpotifyAPIClient()
        )  # Initialize without token, worker will inject it later

    async def execute(self, params: dict) -> ReactionResponse:
        """
        Add a track to the specified playlist

        Expected data:
        - track_id: The Spotify track ID to add
        """
        try:
            LOGGER.info(f"Starting AddToPlaylistReaction with params: {params}")
            LOGGER.info(
                f"Current config: token={self.config.token}, playlist_id={self.config.playlist_id}"
            )

            if self.config.token:
                LOGGER.info("Setting access token for Spotify API")
                self.spotify_api.set_access_token(
                    self.config.token, 3600
                )  # 1 hour expiry
            else:
                LOGGER.error("No token provided in config")
                return ReactionResponse(
                    success=False, details={"error": "No token provided"}
                )

            track_id = getattr(params, "track_id", None)
            if not track_id:
                LOGGER.error("No track ID provided in params")
                return ReactionResponse(
                    success=False, details={"error": "No track ID provided"}
                )

            if not self.config.playlist_id:
                LOGGER.error("No playlist ID provided in config")
                return ReactionResponse(
                    success=False, details={"error": "No playlist ID configured"}
                )

            # Create the track URI
            track_uri = f"spotify:track:{track_id}"
            LOGGER.info(
                f"Adding track URI {track_uri} to playlist {self.config.playlist_id}"
            )

            # Add the track to the playlist
            success = await self.spotify_api.add_tracks_to_playlist(
                playlist_id=self.config.playlist_id,
                uris=[track_uri],
                position=self.config.position,
            )

            if success:
                LOGGER.info(
                    f"Successfully added track {track_uri} to playlist {self.config.playlist_id}"
                )
                return ReactionResponse(
                    success=True,
                    details={
                        "message": "Track added to playlist successfully",
                        "track_id": track_id,
                        "playlist_id": self.config.playlist_id,
                    },
                )
            else:
                LOGGER.error(
                    f"Failed to add track {track_uri} to playlist {self.config.playlist_id}"
                )
                return ReactionResponse(
                    success=False, details={"error": "Failed to add track to playlist"}
                )

        except Exception as e:
            LOGGER.error(f"Exception in AddToPlaylistReaction: {str(e)}", exc_info=True)
            return ReactionResponse(success=False, details={"error": str(e)})


class SendPlaylistReaction(Reaction):
    """Reaction that creates a new playlist"""

    name = "send_playlist"
    config = SpotifyReactionConfig

    def __init__(self, config: SpotifyReactionConfig):
        super().__init__(config)
        self.spotify_api = (
            SpotifyAPI()
        )  # Initialize without token, worker will inject it later

    async def execute(
        self, data: Dict[str, Any], params: Optional[Dict[str, Any]] = None
    ) -> ReactionResponse:
        """
        Create a playlist and add tracks to it

        Expected params:
        - playlist_name: str
        - description: str (optional)
        - public: bool (optional)
        - track_uris: list[str] (optional)
        """
        try:
            if params and "token" in params:
                self.spotify_api.set_access_token(
                    params["token"], 3600
                )  # 1 hour expiry

            if not params or "playlist_name" not in params:
                return ReactionResponse(
                    success=False, details={"error": "Playlist name not provided"}
                )

            # Create the playlist
            user_id = data.get("user_id")
            if not user_id:
                return ReactionResponse(
                    success=False, details={"error": "User ID not provided"}
                )

            playlist = await self.spotify_api.create_playlist(
                user_id=user_id,
                name=params["playlist_name"],
                description=params.get("description", ""),
                public=params.get("public", False),
            )

            if not playlist:
                return ReactionResponse(
                    success=False, details={"error": "Failed to create playlist"}
                )

            # Add tracks if provided
            track_uris = params.get("track_uris", [])
            if track_uris:
                success = await self.spotify_api.add_tracks_to_playlist(
                    playlist["id"], track_uris
                )
                if not success:
                    return ReactionResponse(
                        success=False,
                        details={"error": "Failed to add tracks to playlist"},
                    )

            return ReactionResponse(
                success=True,
                details={
                    "message": "Playlist created successfully",
                    "playlist_id": playlist["id"],
                    "playlist_name": playlist["name"],
                },
            )

        except Exception as e:
            return ReactionResponse(success=False, details={"error": str(e)})
