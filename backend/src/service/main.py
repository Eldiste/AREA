import asyncio
import json
import logging
from typing import Dict, Optional

from pydantic import BaseModel, ValidationError
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from src.config import async_redis_client, async_session_factory
from src.db.models import Area as db_area
from src.db.models import UserService
from src.service.Action.actions import Action
from src.service.Action.discord import NewMessageInChannelAction
from src.service.Action.discord.channel_created import ChannelCreatedAction
from src.service.Action.discord.channel_deleted import ChannelDeletedAction
from src.service.Action.discord.channel_upadte import ChannelUpdatedAction
from src.service.Action.discord.guild_role_added import GuildRoleAddedAction
from src.service.Action.discord.member_removed import (
    MemberRemovedAction,
    MemberRemovedActionConfig,
)
from src.service.Action.discord.message_updated import MessageUpdatedAction
from src.service.Action.github.github_action import NewPushAction
from src.service.Action.google.gmail_action import GmailReceiveAction
from src.service.Action.microsoft.outlook_action import OutlookReceiveAction
from src.service.Action.spotify.track_played import (
    SpotifyActionConfig,
    TrackPlayedAction,
)
from src.service.Action.time_action import TimeAction
from src.service.Reaction.discord.add_reaction import AddReaction
from src.service.Reaction.discord.delete_message import DeleteMessage
from src.service.Reaction.discord.edit_message import EditMessage
from src.service.Reaction.discord.send_message import SendMessage
from src.service.Reaction.github.github_reaction import CreateIssueReaction
from src.service.Reaction.google.gmail_reaction import GmailSendReaction
from src.service.Reaction.microsoft.outlook_reaction import OutlookSendReaction
from src.service.Reaction.print_reaction import PrintReaction
from src.service.Reaction.reactions import Reaction
from src.service.Reaction.spotify.add_playlist import AddToPlaylistReaction
from src.service.Trigger.discord.channel_created import ChannelCreatedTrigger
from src.service.Trigger.discord.channel_deleted import ChannelDeletedTrigger
from src.service.Trigger.discord.channel_upadte import ChannelUpdatedTrigger
from src.service.Trigger.discord.guild_role_added import GuildRoleAddedTrigger
from src.service.Trigger.discord.member_removed import MemberRemovedTrigger
from src.service.Trigger.discord.message_updated import MessageUpdatedTrigger
from src.service.Trigger.date_trigger import DateTrigger
from src.service.Trigger.hourly_trigger import HourlyTrigger
from src.service.Trigger.discord.new_message_in_channel import (
    NewMessageInChannelTrigger,
)
from src.service.Trigger.github.github_trigger import NewPushTrigger
from src.service.Trigger.google.gmail_trigger import GmailTrigger
from src.service.Trigger.microsoft.outlook_trigger import OutlookTrigger
from src.service.Trigger.spotify.track_played import CurrentlyPlayingTrigger

# Import Triggers, Actions, Reactions
from src.service.Trigger.time_trigger import TimeTrigger
from src.service.Trigger.triggers import Trigger
from src.service.Worker.worker import Worker

# Configure logging
logging.basicConfig(level=logging.INFO)
LOGGER = logging.getLogger(__name__)

# Constants
QUEUE_NAME = "task_queue"

# Global registry for active triggers
ACTIVE_TRIGGERS: Dict[int, asyncio.Task] = {}

# Dynamically Register All Components
ALL_COMPONENTS = [
    MessageUpdatedTrigger,
    MessageUpdatedAction,
    MemberRemovedTrigger,
    MemberRemovedAction,
    ChannelDeletedAction,
    ChannelDeletedTrigger,
    ChannelUpdatedAction,
    ChannelUpdatedTrigger,
    ChannelCreatedTrigger,
    ChannelCreatedAction,
    GuildRoleAddedTrigger,
    GuildRoleAddedAction,
    TrackPlayedAction,
    OutlookTrigger,
    GmailTrigger,
    NewPushTrigger,
    AddToPlaylistReaction,
    CurrentlyPlayingTrigger,
    TimeTrigger,
    NewMessageInChannelTrigger,
    NewMessageInChannelAction,
    TimeAction,
    PrintReaction,
    SendMessage,
    AddReaction,
    DeleteMessage,
    EditMessage,
    AddToPlaylistReaction,
    OutlookSendReaction,
    GmailSendReaction,
    CreateIssueReaction,
    OutlookReceiveAction,
    GmailReceiveAction,
    NewPushAction,
    HourlyTrigger,
    DateTrigger,
    Action,  # Temp Fix
]


async def refresh_triggers():
    """
    Periodically refresh triggers by checking for added or removed areas.
    """
    global ACTIVE_TRIGGERS

    while True:
        try:
            async with async_session_factory() as session:
                # Fetch all areas from the database
                result = await session.execute(
                    select(db_area).options(
                        selectinload(db_area.trigger),
                        selectinload(db_area.action),
                        selectinload(db_area.reaction),
                    )
                )
                current_areas = result.scalars().all()

            # Map current areas by their IDs for easy comparison
            current_area_ids = {area.id for area in current_areas}
            active_area_ids = set(ACTIVE_TRIGGERS.keys())

            # Identify areas to start and stop
            areas_to_start = [
                area for area in current_areas if area.id not in active_area_ids
            ]
            areas_to_stop = active_area_ids - current_area_ids

            # Stop triggers for removed areas
            for area_id in areas_to_stop:
                LOGGER.info(f"Stopping trigger for removed Area ID {area_id}.")
                task = ACTIVE_TRIGGERS.pop(area_id, None)
                if task:
                    task.cancel()
                    try:
                        await task
                    except asyncio.CancelledError:
                        LOGGER.info(
                            f"Trigger for Area ID {area_id} stopped successfully."
                        )

            # Start triggers for new areas
            for area in areas_to_start:
                LOGGER.info(f"Starting trigger for new Area ID {area.id}.")
                await start_trigger(area)

        except Exception as e:
            LOGGER.error(f"Error while refreshing triggers: {e}", exc_info=True)

        # Wait for 1 minute before checking again
        await asyncio.sleep(10)


async def start_trigger(area):
    """
    Start a trigger for the given area.
    """
    if area.id in ACTIVE_TRIGGERS:
        LOGGER.warning(f"Trigger loop already running for Area ID {area.id}. Skipping.")
        return

    trigger_class = next(
        (
            cls
            for cls in ALL_COMPONENTS
            if issubclass(cls, Trigger) and cls.name == area.trigger.name
        ),
        None,
    )
    if not trigger_class:
        LOGGER.error(
            f"No trigger class found for trigger '{area.trigger.name}' in Area ID {area.id}."
        )
        return

    try:
        if not area.trigger.config:
            LOGGER.error(
                f"Missing config for trigger '{area.trigger.name}' in Area ID {area.id}."
            )
            return

        async with async_session_factory() as session:
            user_service = await session.scalar(
                select(UserService).where(
                    UserService.user_id == area.user_id,
                    UserService.service_id == area.action.service_id,
                )
            )
        token : Optional[str] = None
        if user_service and user_service.access_token:
            token = user_service.access_token

        trigger_config_with_token = {
            **area.trigger.config,
            "token": token,
        }
        validated_config = trigger_class.config(**trigger_config_with_token)
        trigger_instance = trigger_class(validated_config)

        task = asyncio.create_task(trigger_runner(trigger_instance, area))
        ACTIVE_TRIGGERS[area.id] = task
        LOGGER.info(f"Trigger loop started for Area ID {area.id}.")

    except ValidationError as e:
        LOGGER.error(f"Invalid trigger configuration for Area ID {area.id}: {e}")
    except Exception as e:
        LOGGER.error(
            f"Error starting trigger for Area ID {area.id}: {e}", exc_info=True
        )


def register_components(worker: Worker):
    for component in ALL_COMPONENTS:
        try:
            if not hasattr(component, "config"):
                raise ValueError(
                    f"{component.__name__} is missing a `config` attribute."
                )
            if issubclass(component, Trigger):
                print(component.__name__)

                worker.register_trigger(
                    component.name, {"class": component, "config": component.config}
                )
                LOGGER.info(f"Registered trigger: {component.name}")
            elif issubclass(component, Action):
                worker.register_action(
                    component.name, {"class": component, "config": component.config}
                )
                LOGGER.info(f"Registered action: {component.name}")
            elif issubclass(component, Reaction):
                worker.register_reaction(
                    component.name, {"class": component, "config": component.config}
                )
                LOGGER.info(f"Registered reaction: {component.name}")
        except Exception as e:
            LOGGER.error(f"Failed to register component {component.__name__}: {e}")


async def test_redis_connection():
    try:
        pong = await async_redis_client.ping()
        if pong:
            LOGGER.info("Redis connection successful.")
    except Exception as e:
        LOGGER.error(f"Redis connection failed: {e}")


def to_serializable(obj):
    """
    Convert an object to a serializable dictionary.
    Handles nested objects and dicts dynamically.
    """
    if isinstance(obj, dict):
        return {key: to_serializable(value) for key, value in obj.items()}
    elif hasattr(obj, "__dict__"):
        return {key: to_serializable(value) for key, value in vars(obj).items()}
    elif isinstance(obj, list):
        return [to_serializable(item) for item in obj]
    elif isinstance(obj, tuple):
        return tuple(to_serializable(item) for item in obj)
    else:
        return obj  # Base case: return the object as-is if it's already primitive


async def trigger_runner(trigger_instance: Trigger, area):
    """
    Run a trigger instance in a loop and send events to Redis when triggered.

    This version fetches two tokens:
      - Action token (for area.action.service_id) --> injected into action config
      - Reaction token (for area.reaction.service_id) --> injected into reaction config
    """
    LOGGER.info(f"Starting trigger {trigger_instance.name} for Area ID {area.id}")

    while True:
        try:
            # Execute the trigger and fetch event data
            event_data = await trigger_instance.execute()
            LOGGER.debug(f"Raw Event Data: {event_data}")

            if event_data:
                # Serialize event_data to ensure compatibility
                if hasattr(event_data, "model_dump"):
                    serialized_event_data = event_data.model_dump()
                else:
                    serialized_event_data = to_serializable(event_data)

                # Merge event data and the existing reaction_config (if needed later)
                reaction_params = {
                    **serialized_event_data,
                    **(area.reaction_config or {}),
                }

                # Fetch the user tokens for both the Action and Reaction services
                async with async_session_factory() as session:
                    # Action token
                    action_user_service = await session.scalar(
                        select(UserService).where(
                            UserService.user_id == area.user_id,
                            UserService.service_id == area.action.service_id,
                        )
                    )

                    # Reaction token
                    reaction_user_service = await session.scalar(
                        select(UserService).where(
                            UserService.user_id == area.user_id,
                            UserService.service_id == area.reaction.service_id,
                        )
                    )

                # Build the job/task payload
                task = {
                    # Trigger info
                    "trigger": {"name": trigger_instance.name},
                    # Action details
                    "action": {
                        "name": area.action.name,
                        # Extract the needed params from event data + area.action_config
                        "params": _extract_action_params(
                            serialized_event_data, area.action_config
                        ),
                        # Inject the action token into the action's config
                        "config": {
                            **(area.action_config or {}),
                            "token": (
                                action_user_service.access_token
                                if action_user_service
                                else None
                            ),
                        },
                    },
                    # Reaction details
                    "reaction": {
                        "name": area.reaction.name,
                        # You could include reaction params if needed,
                        # or keep them separate from 'config':
                        "params": reaction_params,
                        # Inject the reaction token into the reaction's config
                        "config": {
                            **(area.reaction_config or {}),
                            "token": (
                                reaction_user_service.access_token
                                if reaction_user_service
                                else None
                            ),
                        },
                    },
                    # The original (serialized) event data
                    "event_data": serialized_event_data,
                }

                LOGGER.info(f"Task to enqueue: {task}")

                # Enqueue the task to the Redis queue
                await async_redis_client.lpush(QUEUE_NAME, json.dumps(task))
                LOGGER.info(f"Task enqueued successfully for Area ID {area.id}")

            # Wait for the next interval
            await asyncio.sleep(getattr(trigger_instance.config, "interval", 60))

        except Exception as e:
            LOGGER.error(
                f"Error in trigger_runner for {trigger_instance.name}: {e}",
                exc_info=True,
            )
            # Sleep briefly to avoid rapid retries on repeated failures
            await asyncio.sleep(60)


def _extract_action_params(event_data: dict, config_model: BaseModel):
    """
    Dynamically map event_data into the action's params structure based on the config model.
    """
    try:
        if hasattr(config_model, "__annotations__"):
            expected_fields = config_model.__annotations__.keys()
            return {
                key: event_data.get(key) for key in expected_fields if key in event_data
            }
        return event_data
    except Exception as e:
        LOGGER.error(f"Failed to extract action params: {e}", exc_info=True)
        return {}


async def stop_all_triggers():
    """
    Stop all active trigger loops.
    """
    LOGGER.info("Stopping all active triggers...")
    for area_id, task in ACTIVE_TRIGGERS.items():
        task.cancel()
        try:
            await task
        except asyncio.CancelledError:
            LOGGER.info(f"Trigger loop for Area ID {area_id} stopped successfully.")
    ACTIVE_TRIGGERS.clear()


async def main():
    """
    Main function to initialize and start the worker and trigger management.
    """
    try:
        worker = Worker(
            queue_name=QUEUE_NAME,
            redis_client=async_redis_client,
            session_factory=async_session_factory,
        )

        register_components(worker)

        LOGGER.info("Starting the worker...")
        worker_task = asyncio.create_task(worker.listen())

        LOGGER.info("Starting trigger manager...")
        trigger_manager_task = asyncio.create_task(refresh_triggers())

        # Wait for both tasks to complete
        await asyncio.gather(worker_task, trigger_manager_task)

    except KeyboardInterrupt:
        LOGGER.info("KeyboardInterrupt received. Stopping all triggers...")
        await stop_all_triggers()
    except Exception as e:
        LOGGER.error(f"Unexpected error in main: {e}", exc_info=True)
        await stop_all_triggers()


if __name__ == "__main__":
    asyncio.run(main())
