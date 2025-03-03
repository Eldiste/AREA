import time

from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from src.config import get_db_async_session
from src.db.models.service import Service

router = APIRouter()


@router.get("/about.json")
async def about_json(
    request: Request, session: AsyncSession = Depends(get_db_async_session)
):
    # Get the client host from the request
    client_host = request.client.host

    # Get the current Unix time
    current_time = int(time.time())

    # Query the database for services, actions, and reactions
    services_data = []
    services = await session.execute(
        select(Service).options(
            selectinload(Service.actions), selectinload(Service.reactions)
        )
    )
    services = services.scalars().all()

    for service in services:
        actions = [
            {"name": action.name, "description": action.description}
            for action in service.actions
        ]
        reactions = [
            {"name": reaction.name, "description": reaction.description}
            for reaction in service.reactions
        ]
        services_data.append(
            {
                "name": service.name,
                "actions": actions,
                "reactions": reactions,
            }
        )

    # Construct the response
    response = {
        "client": {"host": client_host},
        "server": {
            "current_time": current_time,
            "services": services_data,
        },
    }

    return response
