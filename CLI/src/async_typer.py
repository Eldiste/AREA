import asyncio
import inspect
from functools import partial, wraps

import typer
from aiohttp import ClientSession


class AsyncTyper(typer.Typer):
    @staticmethod
    def maybe_run_async(decorator, f):
        if inspect.iscoroutinefunction(f):

            @wraps(f)
            def runner(*args, **kwargs):
                return asyncio.run(f(*args, **kwargs))

            decorator(runner)
        else:
            decorator(f)
        return f

    def callback(self, *args, **kwargs):
        decorator = super().callback(*args, **kwargs)
        return partial(self.maybe_run_async, decorator)

    def command(self, *args, **kwargs):
        decorator = super().command(*args, **kwargs)
        return partial(self.maybe_run_async, decorator)

    async def fetch_json(session: ClientSession, url: str) -> dict:
        async with session.get(url) as resp:
            resp.raise_for_status()
            return await resp.json()
