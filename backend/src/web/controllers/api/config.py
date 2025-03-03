from enum import Enum
from typing import Any, Dict

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from src.service.Action.actions import Action
from src.service.main import ALL_COMPONENTS
from src.service.Reaction.reactions import Reaction
from src.service.Trigger.triggers import Trigger

router = APIRouter(prefix="/api", tags=["API"])


class ConfigType(str, Enum):
    TRIGGER = "trigger"
    ACTION = "action"
    REACTION = "reaction"


@router.get("/config/{type}/{name}", response_model=Dict[str, Any])
async def get_config_template(type: ConfigType, name: str):
    """
    Endpoint to fetch the configuration template for a specific trigger, action, or reaction.
    """
    component_class = next(
        (
            component
            for component in ALL_COMPONENTS
            if component.name == name
            and issubclass(
                component,
                {
                    ConfigType.TRIGGER: Trigger,
                    ConfigType.ACTION: Action,
                    ConfigType.REACTION: Reaction,
                }[type],
            )
        ),
        None,
    )

    if not component_class:
        raise HTTPException(
            status_code=404, detail=f"{type.capitalize()} '{name}' not found."
        )

    config_model = component_class.config

    if not config_model or not issubclass(config_model, BaseModel):
        raise HTTPException(status_code=500, detail="Invalid configuration model.")

    return {
        "type": type,
        "name": name,
        "config_schema": config_model.schema(),
    }
