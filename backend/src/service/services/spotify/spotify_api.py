import logging
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

import aiohttp

LOGGER = logging.getLogger(__name__)


class SpotifyAPIClient:
    def __init__(self, token: Optional[str] = None):
        self.base_url = "https://api.spotify.com/v1"
        self.access_token = token
        self.token_expiry = None if not token else datetime.now() + timedelta(hours=1)

    def set_access_token(self, access_token: str, expires_in: int):
        """Set the access token and calculate its expiry time"""
        self.access_token = access_token
        self.token_expiry = datetime.now() + timedelta(seconds=expires_in)

    def is_token_valid(self) -> bool:
        """Check if the current access token is valid"""
        if not self.access_token or not self.token_expiry:
            return False
        return datetime.now() < self.token_expiry

    def get_headers(self) -> Dict[str, str]:
        """Get headers for API requests"""
        return {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json",
        }

    async def get_currently_playing(self) -> Optional[Dict[str, Any]]:
        """Get the user's currently playing track"""
        if not self.is_token_valid():
            return None

        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"{self.base_url}/me/player/currently-playing",
                headers=self.get_headers(),
            ) as response:
                if response.status == 204:  # No track playing
                    return None
                elif response.status == 200:
                    return await response.json()
                return None

    async def get_user_playlists(self) -> Optional[Dict[str, Any]]:
        """Get the user's playlists"""
        if not self.is_token_valid():
            return None

        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"{self.base_url}/me/playlists", headers=self.get_headers()
            ) as response:
                if response.status == 200:
                    return await response.json()
                return None

    async def create_playlist(
        self, user_id: str, name: str, description: str = "", public: bool = False
    ) -> Optional[Dict[str, Any]]:
        """Create a new playlist for the user"""
        if not self.is_token_valid():
            return None

        data = {"name": name, "description": description, "public": public}

        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.base_url}/users/{user_id}/playlists",
                headers=self.get_headers(),
                json=data,
            ) as response:
                if response.status == 201:
                    return await response.json()
                return None

    async def add_tracks_to_playlist(
        self, playlist_id: str, uris: List[str], position: Optional[int] = None
    ) -> bool:
        """Add tracks to a playlist"""
        LOGGER.info(f"Adding tracks to playlist {playlist_id}: {uris}")

        if not self.is_token_valid():
            LOGGER.error("Token is invalid or expired")
            return False

        data = {"uris": uris}
        if position is not None:
            data["position"] = position

        LOGGER.info(f"Making request to Spotify API with data: {data}")

        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.base_url}/playlists/{playlist_id}/tracks",
                headers=self.get_headers(),
                json=data,
            ) as response:
                LOGGER.info(f"Spotify API response status: {response.status}")
                if response.status != 201:
                    response_text = await response.text()
                    LOGGER.error(f"Failed to add tracks. Response: {response_text}")
                return response.status == 201
