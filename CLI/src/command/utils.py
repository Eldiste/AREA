import logging

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from src.async_typer import AsyncTyper
from src.client.area_client import AreaClient
from src.command.config import settings
from src.utils.typer import display_json

app = AsyncTyper(no_args_is_help=True)
logger = logging.getLogger(__name__)

services_app = AsyncTyper()

# Initialize client
client = AreaClient(settings.api_url)
console = Console()


async def fetch_about_data() -> dict:
    """
    Helper to fetch data from /about.json using the AreaClient.
    Returns a Python dict.
    Raises an exception if status != 200.
    """
    status, response_data = await client.get_about()
    if status != 200:
        raise RuntimeError(f"Unexpected error ({status}): {response_data}")
    return response_data


@app.command()
async def about():
    """
    Retrieve and display information from the /about.json endpoint.
    """
    try:
        data = await fetch_about_data()
        typer.echo("Information retrieved successfully!")
        display_json(data)
    except Exception as exc:
        typer.echo(f"Error: {exc}")


@services_app.command("list")
async def list_services():
    """
    List all services retrieved from the /about.json endpoint.
    """
    try:
        data = await fetch_about_data()
        services = data["server"]["services"]

        table = Table(title="Available Services")
        table.add_column("Service Name", style="cyan", justify="left")
        table.add_column("Actions (#)", style="magenta", justify="right")
        table.add_column("Reactions (#)", style="green", justify="right")

        for svc in services:
            name = svc["name"]
            actions_count = len(svc.get("actions", []))
            reactions_count = len(svc.get("reactions", []))
            table.add_row(name, str(actions_count), str(reactions_count))

        console.print(table)
    except Exception as exc:
        typer.echo(f"Error listing services: {exc}")


@services_app.command("info")
async def service_info(service_name: str):
    """
    Show detailed information (actions and reactions) for a given service.
    """
    try:
        data = await fetch_about_data()
        services = data["server"]["services"]

        for svc in services:
            if svc["name"].lower() == service_name.lower():
                panel_content = f"[bold]Name:[/bold] {svc['name']}\n"

                actions = svc.get("actions", [])
                panel_content += "[bold]Actions:[/bold]\n"
                if actions:
                    for action in actions:
                        panel_content += f"  - [cyan]{action['name']}[/cyan]: {action['description']}\n"
                else:
                    panel_content += "  [dim]No actions found[/dim]\n"

                reactions = svc.get("reactions", [])
                panel_content += "[bold]Reactions:[/bold]\n"
                if reactions:
                    for reaction in reactions:
                        panel_content += f"  - [green]{reaction['name']}[/green]: {reaction['description']}\n"
                else:
                    panel_content += "  [dim]No reactions found[/dim]\n"

                console.print(
                    Panel(panel_content, title="Service Details", expand=False)
                )
                return

        console.print(f"[red]Service '{service_name}' not found.[/red]")
    except Exception as exc:
        typer.echo(f"Error showing service info: {exc}")


@services_app.command("actions")
async def list_actions(service_name: str):
    """
    List all actions for a given service.
    """
    try:
        data = await fetch_about_data()
        services = data["server"]["services"]

        for svc in services:
            if svc["name"].lower() == service_name.lower():
                actions = svc.get("actions", [])
                if not actions:
                    console.print(
                        f"[yellow]No actions found for '{service_name}'[/yellow]"
                    )
                    return

                table = Table(title=f"Actions for {service_name}")
                table.add_column("Name", style="cyan")
                table.add_column("Description", style="white")

                for action in actions:
                    table.add_row(action["name"], action["description"])

                console.print(table)
                return

        console.print(f"[red]Service '{service_name}' not found.[/red]")
    except Exception as exc:
        typer.echo(f"Error listing actions: {exc}")


@services_app.command("reactions")
async def list_reactions(service_name: str):
    """
    List all reactions for a given service.
    """
    try:
        data = await fetch_about_data()
        services = data["server"]["services"]

        for svc in services:
            if svc["name"].lower() == service_name.lower():
                reactions = svc.get("reactions", [])
                if not reactions:
                    console.print(
                        f"[yellow]No reactions found for '{service_name}'[/yellow]"
                    )
                    return

                table = Table(title=f"Reactions for {service_name}")
                table.add_column("Name", style="green")
                table.add_column("Description", style="white")

                for reaction in reactions:
                    table.add_row(reaction["name"], reaction["description"])

                console.print(table)
                return

        console.print(f"[red]Service '{service_name}' not found.[/red]")
    except Exception as exc:
        typer.echo(f"Error listing reactions: {exc}")


# Attach the subcommands
app.add_typer(services_app, name="services", help="Manage and explore services")


if __name__ == "__main__":
    app()
