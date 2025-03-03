from asyncio import run as aiorun

import typer

from src.async_typer import AsyncTyper
from src.command import config, utils
from src.command.account import auth
from src.command.area import area, config
from src.command.oauth import oauth

app = AsyncTyper(no_args_is_help=True)

# Add subcommands
app.add_typer(auth.app, name="auth", help="Register & Test Login")
app.add_typer(utils.app, name="utils", help="Utils")
app.add_typer(oauth.app, name="oauth", help="Oauth")
app.add_typer(area.app, name="area", help="Workflow !")
app.add_typer(config.app, name="config", help="Workflow Config!")

if __name__ == "__main__":
    app()
