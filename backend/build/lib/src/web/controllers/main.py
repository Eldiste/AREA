from typing import Any

from fastapi import FastAPI
from fastapi.responses import PlainTextResponse

app = FastAPI()


@app.get("/", response_class=PlainTextResponse)  # type: ignore[misc]
def read_root() -> str:
    return "Hello World"
