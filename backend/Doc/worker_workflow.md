# Worker Workflow Documentation

This document explains the workflow of the worker, including task processing and interaction between triggers, actions, and reactions.

---

## Workflow Overview

The worker listens for tasks in a queue, processes them, and executes the associated trigger, action, reaction, and post-action cleanup.

---

## Workflow Steps

### 1. **Listen for Tasks**
   - The worker continuously monitors a Redis queue for new tasks.
   - If no tasks are found, it waits for a short interval before checking again.

### 2. **Fetch and Parse Task**
   - The worker retrieves a task from the queue.
   - The task contains information about the trigger, action, reaction, and post-action cleanup steps.

### 3. **Execute the Trigger**
   - The worker evaluates the trigger to determine if the condition is met.
   - If the trigger condition is not met, the task is rescheduled.

### 4. **Execute the Action**
   - If the trigger condition is met, the associated action is executed.
   - The result of the action is passed to the reaction.

### 5. **Execute the Reaction**
   - The worker processes the reaction using the action's result.
   - This could involve logging, notifications, or other operations.

### 6. **Perform Post-Action Cleanup**
   - Ensures the worker clears any temporary states or resources used during the action and reaction.
   - Logs the cleanup status for monitoring.

### 7. **Reschedule or Finish**
   - If the task is periodic (e.g., a time-based trigger), it is rescheduled.
   - Otherwise, the task is marked as complete.

---

## Workflow Diagram

```plaintext
+---------------------------+
|                           |
|     Start Worker Loop     |
|                           |
+---------------------------+
             |
             v
+---------------------------+
|                           |
|   Fetch Task from Queue   |
|                           |
+---------------------------+
             |
             v
+---------------------------+
|                           |
|  Parse Task (Trigger,     |
|  Action, Reaction,        |
|  Post-Cleanup Steps Info) |
|                           |
+---------------------------+
             |
             v
+---------------------------+
|                           |
|  Execute Trigger Logic    |
|                           |
+---------------------------+
      |            |
      | No         | Yes
      |            v
      |   +---------------------------+
      |   |                           |
      |   |    Execute Associated     |
      +-->|          Action           |
          |                           |
          +---------------------------+
                     |
                     v
          +---------------------------+
          |                           |
          |    Execute Associated     |
          |         Reaction          |
          |                           |
          +---------------------------+
          |                           |
          |    Perform Post-Action    |
          |         Cleanup           |
          |                           |
          +---------------------------+
                     |
                     v
          +---------------------------+
          |                           |
          |   Reschedule Task if      |
          |    Periodic Trigger       |
          |                           |
          +---------------------------+
                     |
                     v
          +---------------------------+
          |                           |
          |       End of Cycle        |
          |      Wait for Next Task   |
          |                           |
          +---------------------------+
