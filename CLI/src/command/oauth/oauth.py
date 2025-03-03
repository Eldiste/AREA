from typing import List, Optional

import typer
from rich.console import Console
from rich.table import Table

from src.async_typer import AsyncTyper
from src.client.area_client import AreaClient
from src.command.config import settings
from src.utils.auth import get_auth_area

app = AsyncTyper(no_args_is_help=True)
console = Console()
client = AreaClient(settings.api_url)


async def fetch_oauth_providers() -> List[str]:
    """
    Dynamically fetch services from /about.json and filter only
    those service 'name's that you consider as OAuth providers.
    """
    status, response_data = await client.request("GET", "about.json")
    if status != 200:
        raise RuntimeError(
            f"Error fetching /about.json (HTTP {status}): {response_data}"
        )

    services = response_data["server"].get("services", [])

    known_oauth_services = {"github", "google", "discord", "spotify", "outlook"}

    oauth_providers = []
    for svc in services:
        service_name = svc.get("name", "").lower()
        oauth_providers.append(service_name)

    if not oauth_providers:
        raise RuntimeError("No OAuth providers found in the API response.")
    return oauth_providers


@app.command("login")
async def oauth_login(
    provider: Optional[str] = typer.Argument(
        None,
        help="Name of the OAuth provider. If omitted, you will be prompted to choose.",
    ),
    username: str = typer.Option(settings.user_name, help="Username"),
    password: Optional[str] = typer.Option(settings.password, help="Password"),
    access_token: Optional[str] = None,
):
    """
    Open the OAuth login endpoint in the default browser.

    Usage:
      my_cli_tool login                # Interactively select provider
      my_cli_tool login github         # Direct provider
      my_cli_tool login outlook --access-token="someToken"
    """
    try:
        providers = await fetch_oauth_providers()
    except Exception as exc:
        typer.secho(f"Error fetching OAuth providers: {exc}", fg=typer.colors.RED)
        raise typer.Exit(code=1)

    if not provider:
        console.print("[bold]Available OAuth Providers:[/bold]")
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("#", style="dim")
        table.add_column("Provider", style="cyan")

        for i, p in enumerate(providers, start=1):
            table.add_row(str(i), p)

        console.print(table)

        console.print(
            "[bold magenta]Enter the number of the provider you want to use:[/bold magenta]",
            end=" ",
        )
        choice_str = input()
        choice = int(choice_str)
        if choice < 1 or choice > len(providers):
            typer.secho("Invalid choice, exiting.", fg=typer.colors.RED)
            raise typer.Exit(code=1)

        provider = providers[choice - 1]
    else:
        provider_lower = provider.lower()
        if provider_lower not in providers:
            valid_list_str = ", ".join(providers)
            typer.secho(
                f"Provider '{provider}' not found. Valid options: {valid_list_str}",
                fg=typer.colors.RED,
            )
            raise typer.Exit(code=1)
        provider = provider_lower

    typer.secho(f"Using provider: {provider}", fg=typer.colors.BLUE)

    try:
        test = await get_auth_area(username=username, password=password)
    except Exception as auth_exc:
        typer.secho(f"Authentication error: {auth_exc}", fg=typer.colors.RED)
        raise typer.Exit(code=1)

    access_token = test.token
    if access_token:
        url = f"{settings.api_url}/oauth/{provider}/login?access_token={access_token}"
    else:
        url = f"{settings.api_url}/oauth/{provider}/login"

    typer.secho(
        f"Launching OAuth login for provider '{provider}':", fg=typer.colors.GREEN
    )
    typer.echo(url)
