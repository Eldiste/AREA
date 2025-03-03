from typing import List, Optional

from pydantic import BaseModel, Extra, Field

from src.service.config.filter import FilterConfig


class TriggersServiceConfig(BaseModel):
    interval: Optional[int] = Field(..., description="Interval Between Run")

    class Config:
        extra = Extra.allow


class ActionServiceConfig(BaseModel):
    filters: Optional[FilterConfig] = Field(
        None, description="Filters applied to the action data"
    )


class ReactionServiceConfig(BaseModel):
    custom_action_output: Optional[str] = Field(
        None, description="Use any data instead of the output"
    )


class ServiceConfig(BaseModel):
    """
    Represents a configuration for a service, with support for multiple triggers, actions, and reactions.
    """

    service_name: str = Field(
        ..., description="Name of the service (e.g., Discord, Email, Slack)"
    )
    trigger_configs: List[TriggersServiceConfig] = Field(
        ..., description="List of trigger configurations"
    )
    action_configs: List[ActionServiceConfig] = Field(
        ..., description="List of action configurations"
    )
    reaction_configs: List[ReactionServiceConfig] = Field(
        ..., description="List of reaction configurations"
    )
