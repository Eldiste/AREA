from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.table import Table

from src.async_typer import AsyncTyper
from src.client.area_client import AreaClient
from src.command.config import settings
from src.types.auth.register import RegisterConfig
from src.utils.auth import get_auth_area

app = AsyncTyper(no_args_is_help=True)
console = Console()
client = AreaClient(settings.api_url)


@app.command()
async def register(
    username: str = typer.Option(None, help="Username"),
    email: str = typer.Option(None, help="email"),
    password: str = typer.Option(None, help="password"),
):
    """
    Register a new user.

    This command sends the user registration details to the API.
    """
    try:
        register_data = RegisterConfig(
            username=username, email=email, password=password
        )

        status, response_data = await client.register(register_data)

        if status == 200:
            console.print("[bold green]Registration successful![/bold green]")

            # Create a Rich Table to display user details
            table = Table(title="User Details")
            table.add_column("Field", style="cyan")
            table.add_column("Value", style="magenta")

            table.add_row("Username", response_data["username"])
            table.add_row("Email", response_data["email"])
            table.add_row("ID", str(response_data["id"]))
            table.add_row("Is Active", str(response_data["is_active"]))
            table.add_row("Is Admin", str(response_data["is_admin"]))

            console.print(table)
        elif status == 403:
            console.print("[bold red]Registration failed: Forbidden[/bold red]")
        else:
            console.print(f"[bold yellow]Unexpected error: {status}[/bold yellow]")
            console.print(response_data)
    except Exception as exc:
        console.print(f"[bold red]Error:[/bold red] {exc}")


@app.command()
async def login(username_or_email: str, password: str):
    """
    Login a user and retrieve the access token.

    This command authenticates the user, displays the access token, and stores it in a file.
    """
    try:
        status, response_data = await client.login(username_or_email, password)

        if status == 200:
            console.print("[bold green]Login successful![/bold green]")

            table = Table(title="Access Token Details")
            table.add_column("Field", style="cyan", justify="right")
            table.add_column("Value", style="magenta")

            table.add_row("Access Token", response_data["access_token"])
            table.add_row("Token Type", response_data["token_type"])

            console.print(table)

            token_path = Path(settings.token_file)
            token_path.write_text(response_data["access_token"])
            console.print(
                f"[bold green]Access token saved to:[/bold green] {token_path.resolve()}"
            )

        elif status == 422:
            console.print("[bold yellow]Validation error:[/bold yellow]")
            for error in response_data.get("detail", []):
                console.print(f"[bold red]- {error['msg']}[/bold red]")
        else:
            console.print(f"[bold yellow]Unexpected error: {status}[/bold yellow]")
            console.print(response_data)
    except Exception as exc:
        console.print(f"[bold red]Error:[/bold red] {exc}")


@app.command()
async def mail(
    username: str = typer.Option(settings.user_name, help="Username"),
    password: Optional[str] = typer.Option(settings.password, help="Password"),
):
    test = await get_auth_area(username=username, password=password)

    response, email = await test.get_user_email()

    console.print(f"Email : [bold green] {email.get('email')}[/bold green]")


@app.command()
async def connected(
    username: str = typer.Option(settings.user_name, help="Username"),
    password: Optional[str] = typer.Option(settings.password, help="Password"),
):
    """
    Display the user's connected services in a tabular format.
    """
    client = await get_auth_area(username=username, password=password)
    status, service_list = await client.get_connected_services()

    if status != 200:
        console.print(f"[red]Failed to retrieve services (status={status}).[/red]")
        raise typer.Exit(code=1)

    if not service_list:
        console.print("[yellow]No connected services found.[/yellow]")
        raise typer.Exit()

    from rich.table import Table

    table = Table(title="Connected Services")
    table.add_column("Service Name", style="bold cyan")

    for service in service_list:
        table.add_row(service)

    console.print(table)
