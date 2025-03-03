import json
from typing import Optional

import typer
from rich.console import Console
from rich.prompt import Prompt
from rich.table import Table

from src.async_typer import AsyncTyper
from src.client.auth_client import AuthenticatedAreaClient
from src.command.config import settings
from src.utils.auth import get_auth_area

console = Console()
app = AsyncTyper(no_args_is_help=True)


def fill_config_interactively(properties: dict) -> dict:
    """
    Interactively fill out a config based on a 'properties' dict from JSON schema.
    """
    if not properties:
        console.print(
            "[yellow]No config properties found. Using empty config.[/yellow]"
        )
        return {}

    filled = {}
    for field_name, field_info in properties.items():
        default_val = field_info.get("default", "")
        description = field_info.get("description", "")
        field_type = field_info.get("type", "string")

        console.print(f"\n[bold]{field_name}[/bold] ({description})")
        if default_val:
            console.print(f"(Default: {default_val})")

        if field_type in ["object", "array"]:
            user_value = Prompt.ask(f"Enter JSON for '{field_name}'", default="")
            if user_value.strip():
                try:
                    filled[field_name] = json.loads(user_value)
                except json.JSONDecodeError:
                    console.print("[red]Invalid JSON. Storing raw string.[/red]")
                    filled[field_name] = user_value
            else:
                filled[field_name] = default_val
        else:
            user_value = Prompt.ask(f"Value for '{field_name}'", default=default_val)
            filled[field_name] = user_value

    return filled


def print_non_interactive_schema(properties: dict) -> None:
    """
    Print the config properties in a table without prompting the user.
    """
    if not properties:
        console.print("[yellow]No config properties found.[/yellow]")
        return

    table = Table(title="Config Schema")
    table.add_column("Field Name", style="bold cyan")
    table.add_column("Type")
    table.add_column("Default")
    table.add_column("Description")

    for field_name, field_info in properties.items():
        f_type = field_info.get("type", "")
        f_default = str(field_info.get("default", ""))
        f_desc = field_info.get("description", "")
        table.add_row(field_name, f_type, f_default, f_desc)

    console.print(table)


@app.command("get_config")
async def get_config(
    type_: Optional[str] = typer.Argument(
        None,
        help="The config type: 'action', 'trigger', or 'reaction'. If omitted, you will be prompted.",
    ),
    name: Optional[str] = typer.Argument(
        None,
        help="The name of the action/trigger/reaction. If omitted, you will be prompted.",
    ),
    username: str = typer.Option(settings.user_name, help="Username"),
    password: Optional[str] = typer.Option(settings.password, help="Password"),
):
    """
    Retrieve the config schema for an action, trigger, or reaction.

    Examples:
      1) area get_config action time_action
      2) area get_config trigger new_message_trigger
      3) area get_config  (then you'll be prompted for type, name, etc.)
    """

    client: AuthenticatedAreaClient = await get_auth_area(username, password)

    if not type_:
        console.print("[bold yellow]You did not specify the config type.[/bold yellow]")
        type_ = Prompt.ask(
            "Enter type (action/trigger/reaction)",
            choices=["action", "trigger", "reaction"],
        )

    if not name:
        console.print(
            f"[yellow]You did not specify the name for the {type_}. Fetching available options...[/yellow]"
        )

        if type_ == "action":
            status, items = await client.get_actions()
        elif type_ == "trigger":
            status, items = await client.get_triggers()
        elif type_ == "reaction":
            status, items = await client.get_reactions()
        else:
            console.print(f"[red]Invalid type '{type_}' specified.[/red]")
            raise typer.Exit(code=1)

        if status != 200 or not items:
            console.print(
                f"[red]Failed to retrieve {type_} options (status={status}).[/red]"
            )
            raise typer.Exit(code=1)

        console.print("\nChoose one of the following:")
        for idx, item in enumerate(items, start=1):
            console.print(f"[{idx}] {item['name']}")

        while True:
            choice = Prompt.ask("Enter the number of your choice")
            try:
                index = int(choice)
                if 1 <= index <= len(items):
                    name = items[index - 1]["name"]
                    break
                else:
                    console.print("[red]Invalid choice, out of range.[/red]")
            except ValueError:
                console.print("[red]Please enter a valid number.[/red]")

    status, config_template = await client.get_config_template(type_, name)
    if status != 200:
        console.print(
            f"[red]Failed to get config template for {type_} '{name}' (status={status}).[/red]"
        )
        raise typer.Exit(code=1)

    config_properties = {}
    if "config_schema" in config_template:
        config_schema = config_template["config_schema"]
        config_properties = config_schema.get("properties", {})

    console.print(f"[green]Entering interactive mode for {type_} '{name}'...[/green]")
    filled_config = fill_config_interactively(config_properties)

    console.print("\n[bold green]Your completed config:[/bold green]")
    console.print_json(json.dumps(filled_config, indent=2))
