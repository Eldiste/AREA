import asyncio
from typing import Any, Dict, List, Optional

import typer
from rich.console import Console
from rich.prompt import Prompt

from src.async_typer import AsyncTyper
from src.client.auth_client import AuthenticatedAreaClient
from src.command.config import settings
from src.utils.auth import get_auth_area

console = Console()
app = AsyncTyper(no_args_is_help=True)


def fill_config(properties: dict) -> dict:
    """
    Interactive prompt to fill out a config based on a 'properties' dict
    from your JSON schema.
    """
    if not properties:
        console.print(
            "[yellow]No config properties found or schema is empty. Using empty config.[/yellow]"
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
                import json

                try:
                    filled[field_name] = json.loads(user_value)
                except json.JSONDecodeError:
                    console.print("[red]Invalid JSON input. Storing raw string.[/red]")
                    filled[field_name] = user_value
            else:
                filled[field_name] = default_val
        else:
            user_value = Prompt.ask(f"Value for '{field_name}'", default=default_val)
            filled[field_name] = user_value

    return filled


async def choose_from_list(
    items: List[Dict[str, Any]], label_key: str
) -> Dict[str, Any]:
    """
    Display a numbered list of items (each is a dict) and let the user pick one by index.
    """
    if not items:
        raise ValueError("No items to choose from!")

    console.print("\nChoose one of the following:")
    for idx, item in enumerate(items, start=1):
        console.print(f"[{idx}] {item[label_key]}")

    while True:
        choice = Prompt.ask("Enter the number of your choice")
        try:
            index = int(choice)
            if 1 <= index <= len(items):
                return items[index - 1]
            else:
                console.print("[red]Invalid choice, out of range.[/red]")
        except ValueError:
            console.print("[red]Please enter a valid number.[/red]")


@app.command("create_area")
async def create_area_command(
    username: str = typer.Option(settings.user_name, help="Username"),
    password: Optional[str] = typer.Option(settings.password, help="Password"),
):
    """
    Interactive wizard to create an Area:
      1) Login to get Auth client
      2) Pick an action (always use 'generic_action' for config)
      3) Pick a reaction (use *real* reaction name for config)
      4) Create the Area
      5) Optionally add triggers (use *real* trigger name for config)
    """

    client: AuthenticatedAreaClient = await get_auth_area(username, password)

    status, all_actions = await client.get_actions()
    if status != 200:
        console.print(f"[red]Could not retrieve actions (status={status}).[/red]")
        raise typer.Exit(code=1)

    if not all_actions:
        console.print("[red]No actions found on the server.[/red]")
        raise typer.Exit(code=1)

    chosen_action = await choose_from_list(all_actions, label_key="name")
    action_name = chosen_action["name"]
    action_id = chosen_action["id"]

    status, generic_action_template = await client.get_config_template(
        "action", "generic_action"
    )
    if status != 200 or not generic_action_template:
        console.print("[red]Could not retrieve 'generic_action' config template.[/red]")
        raise typer.Exit(code=1)

    action_props = {}
    if "config_schema" in generic_action_template:
        a_schema = generic_action_template["config_schema"]
        action_props = a_schema.get("properties", {})

    action_config = fill_config(action_props)

    status, all_reactions = await client.get_reactions()
    if status != 200:
        console.print(f"[red]Could not retrieve reactions (status={status}).[/red]")
        raise typer.Exit(code=1)

    if not all_reactions:
        console.print("[red]No reactions found on the server.[/red]")
        raise typer.Exit(code=1)

    chosen_reaction = await choose_from_list(all_reactions, label_key="name")
    reaction_name = chosen_reaction["name"]
    reaction_id = chosen_reaction["id"]

    status, real_reaction_template = await client.get_config_template(
        "reaction", reaction_name
    )
    if status != 200 or not real_reaction_template:
        console.print(
            f"[red]Could not retrieve config template for '{reaction_name}'.[/red]"
        )
        raise typer.Exit(code=1)

    reaction_props = {}
    if "config_schema" in real_reaction_template:
        r_schema = real_reaction_template["config_schema"]
        reaction_props = r_schema.get("properties", {})

    reaction_config = fill_config(reaction_props)

    status, area_data = await client.create_area(
        action_id=action_id,
        reaction_id=reaction_id,
        action_config=action_config,
        reaction_config=reaction_config,
    )

    if status != 200:
        console.print(f"[red]Failed to create Area (status={status}).[/red]")
        console.print(area_data)
        raise typer.Exit(code=1)

    area_id = area_data["id"]
    console.print(f"[green]Created Area with ID {area_id}[/green]")

    while True:
        create_more = Prompt.ask(
            "\nDo you want to add a Trigger to this Area?",
            choices=["y", "n"],
            default="n",
        )
        if create_more.lower() == "n":
            break

        status, all_triggers = await client.get_actions()
        if status != 200 or not all_triggers:
            console.print(f"[red]Could not retrieve triggers (status={status}).[/red]")
            break

        chosen_trigger = await choose_from_list(all_triggers, label_key="name")
        trigger_name = chosen_trigger["name"]

        status, trigger_template = await client.get_config_template(
            "trigger", trigger_name
        )
        if status != 200 or not trigger_template:
            console.print(
                f"[red]Could not retrieve trigger config for '{trigger_name}'.[/red]"
            )
            break

        trigger_props = {}
        if "config_schema" in trigger_template:
            t_schema = trigger_template["config_schema"]
            trigger_props = t_schema.get("properties", {})

        trigger_config = fill_config(trigger_props)

        t_name = action_name

        status, trigger_data = await client.create_trigger(
            name=t_name, area_id=area_id, config=trigger_config
        )
        if status != 200:
            console.print(f"[red]Failed to create Trigger (status={status}).[/red]")
            console.print(trigger_data)
        else:
            console.print(
                f"[green]Created trigger '{t_name}' with ID {trigger_data['id']}[/green]"
            )

    console.print("\n[bold green]Done![/bold green]")


@app.command("list_area")
async def list_area(
    username: str = typer.Option(settings.user_name, help="Username"),
    password: Optional[str] = typer.Option(settings.password, help="Password"),
):
    """
    List all Areas for the authenticated user, displayed in a Rich table.
    """
    client: AuthenticatedAreaClient = await get_auth_area(username, password)
    status, areas = await client.get_areas()

    if status != 200:
        console.print(f"[red]Failed to retrieve areas (status={status}).[/red]")
        raise typer.Exit(code=1)

    if not areas:
        console.print("[yellow]No areas found.[/yellow]")
        return

    from rich.table import Table

    table = Table(title="User Areas")
    table.add_column("ID", style="bold cyan")
    table.add_column("User ID", style="bold green")
    table.add_column("Action ID", style="dim")
    table.add_column("Reaction ID", style="dim")
    table.add_column("Trigger ID", style="dim")

    for area in areas:
        table.add_row(
            str(area["id"]),
            str(area["user_id"]),
            str(area["action_id"]),
            str(area["reaction_id"]),
            str(area["trigger_id"] or "None"),
        )

    console.print(table)
