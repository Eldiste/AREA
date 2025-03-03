import asyncio
import json
import logging

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from src.config import async_redis_client, async_session_factory
from src.db.models import Area
from src.service.Action.http_get_action import HttpGetAction
from src.service.Reaction.print_reaction import PrintReaction
from src.service.Trigger.time_trigger import TimeTrigger
from src.service.Worker.worker import Worker

# Configure logging
logging.basicConfig(level=logging.INFO)
LOGGER = logging.getLogger(__name__)

# Redis queue name
QUEUE_NAME = "task_queue"

# Initialize the worker
worker = Worker(queue_name=QUEUE_NAME, redis_client=async_redis_client)


# Register triggers, actions, and reactions
worker.register_trigger(TimeTrigger)
worker.register_action(HttpGetAction)
worker.register_reaction(PrintReaction)


async def enqueue_tasks_from_db():
    async with async_session_factory() as session:
        # Query all areas with their triggers, actions, and reactions
        result = await session.execute(
            select(Area).options(
                selectinload(Area.trigger),
                selectinload(Area.action),
                selectinload(Area.reaction),
            )
        )
        areas = result.scalars().all()

        for area in areas:
            # Ensure configs are handled properly
            action_config = (
                area.action.config if area.action and area.action.config else {}
            )
            reaction_params = (
                area.reaction.config if area.reaction and area.reaction.config else {}
            )

            # Prepare the task for the Redis queue
            task = {
                "trigger": {"name": area.trigger.name, "config": area.trigger.config},
                "action": {"name": area.action.name, "params": action_config},
                "reaction": {"name": area.reaction.name, "params": reaction_params},
            }

            await async_redis_client.lpush(QUEUE_NAME, json.dumps(task))
            LOGGER.info(f"Task added to the queue for Area ID: {area.id}")


async def main():
    """
    Main entry point for running the worker and setting up the environment.
    """
    # Dynamically enqueue tasks from the database
    await enqueue_tasks_from_db()

    # Start the worker to listen for tasks
    await worker.listen()


if __name__ == "__main__":
    asyncio.run(main())
