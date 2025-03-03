import asyncio
import json
import logging
import time
from datetime import datetime
from typing import Type

from sqlalchemy import func, select, update

from redis.asyncio import Redis
from src.config import async_session_factory
from src.db.models import Trigger as TriggerModel

LOGGER = logging.getLogger(__name__)


class Worker:
    def __init__(self, queue_name: str, redis_client: Redis):
        self.queue_name = queue_name
        self.redis_client = redis_client
        self.triggers = {}
        self.actions = {}
        self.reactions = {}

    def register_trigger(self, trigger_class: Type):
        self.triggers[trigger_class.name] = trigger_class
        LOGGER.info(f"Registered trigger: {trigger_class.name}")

    def register_action(self, action_class: Type):
        self.actions[action_class.name] = action_class
        LOGGER.info(f"Registered action: {action_class.name}")

    def register_reaction(self, reaction_class: Type):
        self.reactions[reaction_class.name] = reaction_class
        LOGGER.info(f"Registered reaction: {reaction_class.name}")

    async def process_task(self, task: dict):
        """
        Process a task from the queue.
        """
        try:
            trigger_name = task["trigger"]["name"]
            trigger_config = task["trigger"]["config"]
            trigger_class = self.triggers.get(trigger_name)

            if not trigger_class:
                LOGGER.error(f"Unknown trigger: {trigger_name}")
                return

            # Instantiate the trigger
            trigger_instance = trigger_class(trigger_config)
            current_time = time.time()

            # Execute the trigger logic
            if await trigger_instance.execute({"current_time": current_time}):
                # Perform the action and reaction
                await self.execute_action_and_reaction(task)

                # Update `last_run` for the trigger
                await trigger_instance.update_last_run(self.update_trigger_last_run)
            else:
                # Calculate delay until next execution
                interval = trigger_config.get("interval", 60)
                delay = (
                    trigger_instance.config.get("last_run", 0) + interval
                ) - current_time
                delay = max(delay, 0)  # Ensure delay is not negative

                LOGGER.info(
                    f"Task for trigger '{trigger_name}' will be rescheduled after {delay:.2f} seconds."
                )
                await asyncio.sleep(delay)

            # Reschedule the task by requeuing it
            await self.reschedule_task(task)

        except Exception as e:
            LOGGER.error(f"Error processing task: {e}", exc_info=True)

    async def reschedule_task(self, task: dict):
        """
        Reschedule the task in the Redis queue.
        """
        try:
            # Add the task back to the queue
            await self.redis_client.lpush(self.queue_name, json.dumps(task))
            LOGGER.info(f"Task rescheduled for trigger '{task['trigger']['name']}'.")
        except Exception as e:
            LOGGER.error(f"Error rescheduling task: {e}", exc_info=True)

    async def update_trigger_last_run(self, trigger_name: str, last_run: float):
        """
        Update the `last_run` column of a trigger by its name.
        """
        try:
            last_run_datetime = datetime.fromtimestamp(last_run)
            stmt = (
                update(TriggerModel)
                .where(TriggerModel.name == trigger_name)
                .values(last_run=last_run_datetime, updated_at=func.now())
            )
            LOGGER.debug(
                f"Updating trigger '{trigger_name}' last_run to {last_run_datetime}."
            )
            async with async_session_factory() as session:
                await session.execute(stmt)
                await session.commit()
                LOGGER.info(
                    f"Trigger '{trigger_name}' last_run successfully committed."
                )
        except Exception as e:
            LOGGER.error(
                f"Error updating last_run for trigger '{trigger_name}': {str(e)}",
                exc_info=True,
            )
            raise

    async def execute_action_and_reaction(self, task: dict):
        """
        Execute the associated action and reaction for the task.
        """
        action_name = task["action"]["name"]
        action_params = task["action"]["params"]
        reaction_name = task["reaction"]["name"]
        reaction_params = task["reaction"]["params"]

        action_class = self.actions.get(action_name)
        reaction_class = self.reactions.get(reaction_name)

        if not action_class:
            LOGGER.error(f"Unknown action: {action_name}")
            return

        if not reaction_class:
            LOGGER.error(f"Unknown reaction: {reaction_name}")
            return

        action_instance = action_class(**action_params)
        action_result = await action_instance.execute()

        reaction_instance = reaction_class(**reaction_params)
        await reaction_instance.execute(action_result)

    async def listen(self):
        """
        Continuously listen for tasks on the Redis queue.
        """
        LOGGER.info(f"Listening for tasks on queue: {self.queue_name}")
        while True:
            try:
                task_data = await self.redis_client.rpop(self.queue_name)

                if not task_data:
                    await asyncio.sleep(1)
                    continue

                task = json.loads(task_data)
                await self.process_task(task)
            except Exception as e:
                LOGGER.error(f"Error during task listening: {e}", exc_info=True)
                await asyncio.sleep(1)
