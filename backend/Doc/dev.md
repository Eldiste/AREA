# Contributions Documentation

Welcome to the contribution guide for the AREA project! This document will help you set up your development environment, run the project, and contribute effectively. Below are instructions for common development tasks, tools, and libraries used in the project.

---

## Table of Contents

- [Contributions Documentation](#contributions-documentation)
  - [Table of Contents](#table-of-contents)
  - [Setup and Running the Project](#setup-and-running-the-project)
    - [Clone the Repository](#clone-the-repository)
    - [Set Up Virtual Environment](#set-up-virtual-environment)
    - [Install Dependencies](#install-dependencies)
    - [Run the Application](#run-the-application)
  - [Code Quality and Linting](#code-quality-and-linting)
    - [Code Formatting](#code-formatting)
    - [Static Typing](#static-typing)
    - [Linting and Formatting Commands](#linting-and-formatting-commands)
  - [Database Setup](#database-setup)
    - [Initialize Database](#initialize-database)
    - [Migrations with Alembic](#migrations-with-alembic)
  - [Testing](#testing)
    - [Run Unit Tests](#run-unit-tests)
    - [Run Tests with Coverage](#run-tests-with-coverage)
  - [Additional Tools and Libraries](#additional-tools-and-libraries)
  - [Contributing Guidelines](#contributing-guidelines)
  - [Creating Triggers, Actions, and Reactions](#creating-triggers-actions-and-reactions)

---

## Setup and Running the Project

### Clone the Repository

```bash
git clone <repository-url>
cd area
```

### Set Up Virtual Environment

We recommend using `venv` for creating a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate  # On Linux/Mac
.venv\Scripts\activate     # On Windows
```

### Install Dependencies

With your virtual environment activated, install the dependencies:

```bash
pip install -e .
```

Alternatively, for Hatch-based workflows, use:

(this is automaticly made if u just do hatch run cmd)
```bash
hatch env create
```

### Run the Application

Run the FastAPI application locally using `hatch` or `uvicorn`:

```bash
hatch run run
```

Or directly with `uvicorn`:

```bash
uvicorn src.web.controllers.main:app --reload
```

---

## Code Quality and Linting

The project uses `black`, `isort`, and `mypy` for code quality. These tools are configured in the `pyproject.toml` file.

### Code Formatting

Ensure all Python files follow `black` formatting standards:

```bash
hatch run linting:fmt
```

### Static Typing

Use `mypy` for static type checking:

```bash
hatch run linting:typing
```

### Linting and Formatting Commands

Run all linting checks:

```bash
hatch run linting:all
```

To fix formatting issues automatically, use:

```bash
hatch run linting:fmt
```

---

## Database Setup

The project uses `alembic` for database migrations.

### Initialize Database

To set up the database, create an `.env` file with your database configuration (see `.env.example` for a template). Then, initialize the database:

```bash
alembic upgrade head
```

### Migrations with Alembic

To create a new migration:

```bash
alembic revision --autogenerate -m "Add migration description"
```

With autogenerate all edit in `src.db.models` with automaticly give you the good migrations script code

Apply the migration:

```bash
alembic upgrade head
```

---

## Testing

The project uses `pytest` for running tests.

### Run Unit Tests

To run all unit tests:

```bash
hatch run test
```

### Run Tests with Coverage

To run tests and generate a coverage report:

```bash
hatch run test_cov
```

---

## Additional Tools and Libraries

- **FastAPI**: The main web framework.
- **SQLAlchemy**: For ORM and database interactions.
- **Alembic**: For database migrations.
- **Redis**: For task queue and caching.
- **hatch**: For environment and script management.
- **black**, **mypy**, **isort**: For code quality and style.

---
## Creating Triggers, Actions, and Reactions

This section provides a step-by-step guide to creating a new `Trigger`, `Action`, and `Reaction` by extending the abstract classes provided in `triggers.py`, `actions.py`, and `reactions.py`.

### Creating a Trigger

1. Open the `triggers.py` file.
2. Create a new class that inherits from the `Trigger` abstract class.
3. Implement all the required abstract methods defined in the base class.
4. Add any additional logic or properties needed for your specific trigger functionality.

Example:

```python
from triggers import Trigger

class DateTrigger(Trigger):
    def __init__(self, date):
        self.date = date

    def check(self):
        # Logic to check if the trigger condition is met
        return datetime.now() >= self.date
```

### Creating an Action

1. Open the `actions.py` file.
2. Create a new class that inherits from the `Action` abstract class.
3. Implement all the required abstract methods defined in the base class.
4. Define any additional parameters or configuration needed for the action.

Example:

```python
from actions import Action

class SendEmailAction(Action):
    def __init__(self, recipient, subject, body):
        self.recipient = recipient
        self.subject = subject
        self.body = body

    def execute(self):
        # Logic to send an email
        print(f"Sending email to {self.recipient} with subject '{self.subject}'")
```

### Creating a Reaction

1. Open the `reactions.py` file.
2. Create a new class that inherits from the `Reaction` abstract class.
3. Implement all the required abstract methods defined in the base class.
4. Provide specific logic for how the reaction should respond to triggers/actions.

Example:

```python
from reactions import Reaction

class LogReaction(Reaction):
    def __init__(self, message):
        self.message = message

    def react(self):
        # Logic to log the message
        print(f"Log: {self.message}")
```

By following these steps, you can extend the functionality of the system by adding new triggers, actions, and reactions that conform to the abstract structure provided.
## Contributing Guidelines

1. **Branching**: Always create a new branch for your feature or bugfix.
2. **Pull Requests**: Ensure your PR includes tests and passes all checks before submission.
3. **Documentation**: Update documentation if you introduce new features or changes.

Thank you for contributing!
