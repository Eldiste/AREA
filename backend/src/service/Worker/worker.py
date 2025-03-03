import asyncio
import json
import logging
from typing import Dict, Type

from pydantic import ValidationError

from src.service.Action.actions import Action
from src.service.Reaction.reactions import Reaction

LOGGER = logging.getLogger(__name__)


class Worker:
    def __init__(self, queue_name, redis_client, session_factory):
        """
        Worker initialization with queue, Redis client, and DB session factory.
        """
        self.queue_name = queue_name
        self.redis_client = redis_client
        self.session_factory = session_factory

        self.triggers: Dict[str, Dict] = {}
        self.actions: Dict[str, Dict] = {}
        self.reactions: Dict[str, Dict] = {}

    def register_trigger(self, name: str, trigger_data: Dict[str, Type]):
        """
        Register a trigger with its name and configuration model.
        """
        self.triggers[name] = trigger_data
        LOGGER.info(f"Registered trigger: {name}")

    def register_action(self, name: str, action_data: Dict[str, Type]):
        """
        Register an action with its name and configuration model.
        """
        self.actions[name] = action_data
        LOGGER.info(f"Registered action: {name}")

    def register_reaction(self, name: str, reaction_data: Dict[str, Type]):
        """
        Register a reaction with its name and configuration model.
        """
        self.reactions[name] = reaction_data
        LOGGER.info(f"Registered reaction: {name}")

    async def process_task(self, task: dict):
        """
        Process a single task from the queue.
        """
        try:
            action_name = task["action"]["name"]
            reaction_name = task["reaction"]["name"]

            action_data = self.actions.get(action_name)
            reaction_data = self.reactions.get(reaction_name)
            LOGGER.debug(f"Liste des actions enregistrées: {list(self.actions.keys())}")
            LOGGER.debug(
                f"Liste des réactions enregistrées: {list(self.reactions.keys())}"
            )
            LOGGER.debug(
                f"Tâche en cours : action '{task['action']['name']}' et réaction '{task['reaction']['name']}'"
            )
            if not action_data or not reaction_data:
                raise ValueError(f"Task references unknown action/reaction: {task}")

            # Initialize the action with validated configuration
            action_class: Type[Action] = action_data["class"]

            action_config_model = action_class.config
            try:
                print(task["action"]["params"])
                action_config = action_config_model(**task["action"]["params"])
            except ValidationError as e:
                raise ValueError(
                    f"Invalid action configuration for '{action_name}': {e}"
                )

            action_instance = action_class(action_config)
            action_result = await action_instance.execute(task["action"]["params"])

            reaction_class: Type[Reaction] = reaction_data["class"]
            reaction_config_model = reaction_class.config
            reaction_params = {
                **task["reaction"]["params"],
                "token": (
                    task["reaction"]["config"]["token"]
                    if "config" in task["reaction"]
                    and "token" in task["reaction"]["config"]
                    else None
                ),
            }
            try:
                reaction_config = reaction_config_model(**reaction_params)
            except ValidationError as e:
                raise ValueError(
                    f"Invalid reaction configuration for '{reaction_name}': {e}"
                )
            reaction_instance = reaction_class(config=reaction_config)
            await reaction_instance.execute(action_result)

        except Exception as e:
            LOGGER.error(f"Error processing task: {e}", exc_info=True)

    async def listen(self):
        """
        Continuously listen for tasks from the queue.
        """
        LOGGER.info(f"Worker listening for tasks on queue: {self.queue_name}")
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
