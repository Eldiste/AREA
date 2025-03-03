import json

from rich.console import Console
from rich.json import JSON

console = Console()


def display_json(data):
    """
    Display a JSON string with Rich styling.
    If data is a dict, convert it to a JSON string before printing.
    """
    try:
        if not isinstance(data, str):
            data = json.dumps(data)

        console.print(JSON(data))
    except Exception as exc:
        console.print(f"[bold red]Error displaying JSON:[/bold red] {exc}")
