from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from src.auth.config import get_current_user
from src.config import get_db_async_session
from src.db.models import User, UserService
from src.service.services.discord.dicord import DiscordAPI

"""
Those funcs on the idea as here to allow us to get more data, from the user.
This would likely meant to be helper func, implementations of func got removed but are stil quite easy to re 
implements.

If you are a front-end warrior ou can re implant them :)
"""


async def get_discord_access_token(session: AsyncSession, current_user: User) -> str:
    """
    Retrieve the Discord access token for the authenticated user.
    """
    query = (
        select(UserService)
        .where(UserService.user_id == current_user.id)
        .where(
            UserService.service_id == 1
        )  # Assuming '1' is the ID for Discord in the 'services' table
    )
    result = await session.execute(query)
    user_service = result.scalar_one_or_none()

    if not user_service or not user_service.access_token:
        raise HTTPException(
            status_code=401,
            detail="Discord access token not found for the current user.",
        )

    return user_service.access_token


router = APIRouter(prefix="/services/discord", tags=["Discord Helpers"])


async def get_discord_api(
    session: AsyncSession = Depends(get_db_async_session),
    current_user: User = Depends(get_current_user),
) -> DiscordAPI:
    """
    Initialize DiscordAPI with the current user's access token.
    """
    access_token = await get_discord_access_token(session, current_user)
    return DiscordAPI(token=access_token)


@router.get("/guilds")
async def get_user_guilds(
    discord_api: DiscordAPI = Depends(get_discord_api),
):
    """
    Fetch all guilds the authenticated user is a member of.
    """
    guilds = await discord_api.get_user_guilds()
    return {"guilds": guilds}


@router.get("/guilds/{guild_id}")
async def get_guild_details(
    guild_id: str, discord_api: DiscordAPI = Depends(get_discord_api)
):
    """
    Fetch details of a specific guild.
    """
    guild = await discord_api.get_guild(guild_id)
    return {"guild": guild}


@router.get("/guilds/{guild_id}/members")
async def get_guild_members(
    guild_id: str, discord_api: DiscordAPI = Depends(get_discord_api)
):
    """
    Fetch members of a specific guild.
    """
    members = await discord_api.get_guild_members(guild_id)
    return {"members": members}


@router.get("/guilds/{guild_id}/roles")
async def get_guild_roles(
    guild_id: str, discord_api: DiscordAPI = Depends(get_discord_api)
):
    """
    Fetch roles of a specific guild.
    """
    roles = await discord_api.get_guild_roles(guild_id)
    return {"roles": roles}


@router.get("/channels/{channel_id}")
async def get_channel_details(
    channel_id: str, discord_api: DiscordAPI = Depends(get_discord_api)
):
    """
    Fetch details of a specific channel.
    """
    channel = await discord_api.get_channel(channel_id)
    return {"channel": channel}


@router.get("/channels/{channel_id}/messages")
async def get_channel_messages(
    channel_id: str, discord_api: DiscordAPI = Depends(get_discord_api)
):
    """
    Fetch messages from a specific channel.
    """
    messages = await discord_api.get_channel_messages(channel_id)
    return {"messages": messages}


@router.get("/connections")
async def get_user_connections(
    discord_api: DiscordAPI = Depends(get_discord_api),
):
    """
    Fetch the authenticated user's connected accounts (e.g., Steam, Twitch).
    """
    connections = await discord_api.get_user_connections()
    return {"connections": connections}
