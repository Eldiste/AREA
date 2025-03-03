from typing import Dict, Optional

from pydantic import BaseModel, Extra, ValidationError

from src.schemas.trigger import TriggerResponse
from src.service.Action.actions import Action
from src.service.main import ALL_COMPONENTS
from src.service.Reaction.reactions import Reaction
from src.service.Trigger.triggers import Trigger


class AreaBase(BaseModel):
    user_id: int
    action_id: int
    reaction_id: int
    trigger_id: Optional[int] = None  # Make trigger_id optional with default None


class AreaCreate(BaseModel):
    action_id: int
    reaction_id: int
    action_config: Optional[Dict]
    reaction_config: Optional[Dict]

    class Config:
        extra = Extra.allow


class AreaUpdate(BaseModel):
    action_id: Optional[int]
    reaction_id: Optional[int]
    trigger_id: Optional[int]  # Add trigger_id
    action_config: Optional[Dict]
    reaction_config: Optional[Dict]
    trigger_config: Optional[Dict]  # Add trigger_config


class AreaResponse(AreaBase):
    id: int
    action_config: Optional[Dict]
    reaction_config: Optional[Dict]

    class Config:
        from_attributes = True

    @staticmethod
    def validate_and_transform_config(config: Dict, config_model: type) -> Dict:
        """
        Validate and transform a configuration dictionary using the provided Pydantic model.
        """
        try:
            validated = config_model(**config)  # Validate against the config model
            return validated.dict()  # Transform to a valid dictionary
        except ValidationError as e:
            return {"error": str(e)}

    def dict(self, **kwargs):
        """
        Override dict method to ensure action_config, reaction_config, and trigger_config are validated dynamically.
        """
        base = super().dict(**kwargs)

        if "action_id" in base and "action_config" in base:
            action_class = next(
                (
                    component
                    for component in ALL_COMPONENTS
                    if issubclass(component, Action)
                    and component.name == base["action_id"]
                ),
                None,
            )
            if action_class:
                base["action_config"] = self.validate_and_transform_config(
                    base["action_config"] or {}, action_class.config
                )

        if "reaction_id" in base and "reaction_config" in base:
            reaction_class = next(
                (
                    component
                    for component in ALL_COMPONENTS
                    if issubclass(component, Reaction)
                    and component.name == base["reaction_id"]
                ),
                None,
            )
            if reaction_class:
                base["reaction_config"] = self.validate_and_transform_config(
                    base["reaction_config"] or {}, reaction_class.config
                )

        if "trigger_id" in base and "trigger_config" in base:
            trigger_class = next(
                (
                    component
                    for component in ALL_COMPONENTS
                    if issubclass(component, Trigger)
                    and component.name == base["trigger_id"]
                ),
                None,
            )
            if trigger_class:
                base["trigger_config"] = self.validate_and_transform_config(
                    base["trigger_config"] or {}, trigger_class.config
                )

        return base
