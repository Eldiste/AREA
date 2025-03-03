from typing import Optional

from rich.prompt import Prompt

from src.client.area_client import AreaClient
from src.client.auth_client import AuthenticatedAreaClient
from src.command.config import settings


def safe_getattr(obj, attr, default=None):
    for part in attr.split("."):
        obj = getattr(obj, part, default)
        if obj is default:
            break
    return obj


async def get_auth_area(
    username: str = settings.user_name, password: Optional[str] = settings.password
) -> AuthenticatedAreaClient:
    if not username:
        username = Prompt.ask("Enter your password")
    if not password:
        password = Prompt.ask("Enter your password", password=True)

    client = AreaClient(base_url=settings.api_url)

    login = await client.login(username, password)

    token = login[1].get("access_token")

    return AuthenticatedAreaClient(base_url=settings.api_url, token=token)
