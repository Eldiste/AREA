# Actions, Reactions, and Triggers Documentation

This document explains how to define and implement new Actions, Reactions, and Triggers in the backend system.

---

## Overview

### **Actions**
Actions define operations that are performed as a result of a trigger. For example, sending an HTTP request or creating a database record.

### **Reactions**
Reactions are tasks executed after an action is completed. For example, logging the result or notifying a user.

### **Triggers**
Triggers define the conditions under which an action is initiated. For example, a time-based trigger or an event-based trigger.

---

## Base Classes

The following base classes are used to create new Actions, Reactions, and Triggers:

### **Base Action**
```python
from src.service.base import BaseComponent

class Action(BaseComponent):
    """
    Base Action class with configurable parameters and a defined response type.
    All specific actions should inherit from this class.
    """
    name = "base_action"
    config: dict = {}  # Optional configuration for the Action

    async def execute(self, *args, **kwargs) -> dict:
        """
        Perform the action with optional configuration.

        :return: Dictionary containing the result of the action execution.
        """
        raise NotImplementedError("Action subclasses must implement the `execute` method.")

```
### **Base Re Action**

```python
from src.service.base import BaseComponent

class Trigger(BaseComponent):
    """
    Base Trigger class with dynamic configurations and filters.
    All specific triggers should inherit from this class.
    """
    name = "base_trigger"
    config: dict = {}  # Configuration dict to define conditions

    def __init__(self, config: dict = None):
        self.config = config or {}

    async def execute(self, *args, **kwargs) -> dict:
        """
        Evaluate the trigger condition.

        :return: Dictionary containing the evaluation status and any additional filter data.
        """
        raise NotImplementedError("Trigger subclasses must implement the `execute` method.")
```

### **Base Trigger**
```py
from src.service.base import BaseComponent

class Trigger(BaseComponent):
    """
    Base Trigger class. All specific triggers should inherit from this class.
    """
    name = "base_trigger"

    def __init__(self, config: dict):
        self.config = config

    async def execute(self, *args, **kwargs) -> bool:
        """
        Check if the trigger condition is met.

        :return: True if the trigger condition is met, False otherwise.
        """
        raise NotImplementedError("Trigger subclasses must implement the `execute` method.")

```



# Examples
## **Creating a New Action**
```py
from src.service.Action.actions import Action
import aiohttp

class HttpGetAction(Action):
    """
    An Action that performs an HTTP GET request.
    """
    name = "http_get_action"

    async def execute(self, url: str, *args, **kwargs):
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                result = await response.text()
                return result
```
# **Creating a New Reaction**

```py
from src.service.Reaction.reactions import Reaction

class PrintReaction(Reaction):
    """
    A Reaction that prints the action result alongside metadata.
    """
    name = "print_reaction"
    config: dict = {"include_metadata": True}  # Example configuration for metadata handling

    async def execute(self, action_result: dict, *args, **kwargs) -> None:
        metadata = kwargs.get("metadata", {})
        if self.config.get("include_metadata", False):
            print(f"Reaction executed with result: {action_result} | Metadata: {metadata}")
        else:
            print(f"Reaction executed with result: {action_result}")
```
##  **Creating a New Trigger**
```python
from src.service.Trigger.triggers import Trigger
import time

class TimeTrigger(Trigger):
    """
    A Trigger that activates based on a time interval.
    """
    name = "time_trigger"

    async def execute(self, *args, **kwargs) -> dict:
        last_run = self.config.get("last_run", 0)
        interval = self.config.get("interval", 60)  # Default interval is 60 seconds
        current_time = time.time()
        
        if current_time - last_run >= interval:
            self.config["last_run"] = current_time
            return {"status": True, "timestamp": current_time}
        return {"status": False, "time_remaining": interval - (current_time - last_run)}
```

# Adding a New Component to the Worker
To add a new Action, Reaction, or Trigger to the system, register it with the Worker:

## **Example Registration**
```python
from src.service.Worker.worker import Worker
from src.service.Action.http_get_action import HttpGetAction
from src.service.Reaction.print_reaction import PrintReaction
from src.service.Trigger.time_trigger import TimeTrigger

worker = Worker(queue_name="task_queue", redis_client=redis_client)

# Register components
worker.register_action(HttpGetAction)
worker.register_reaction(PrintReaction)
worker.register_trigger(TimeTrigger)s
```