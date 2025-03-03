from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class Operator(str, Enum):
    CONTAINS = "contains"
    EQUALS = "equals"
    STARTS_WITH = "starts_with"
    ENDS_WITH = "ends_with"
    GREATER_THAN = "greater_than"
    LESS_THAN = "less_than"
    NOT_EQUALS = "not_equals"


class MatchLogic(str, Enum):
    ALL = "all"
    ANY = "any"


class FilterCondition(BaseModel):
    """
    Represents a single filtering condition.
    """

    field: str = Field(
        ..., description="Field to filter on (e.g., message content, channel_id)"
    )
    operator: str = Field(
        ..., description="Operator for filtering (e.g., 'contains', 'equals')"
    )
    value: Any = Field(
        ..., description="Value to compare against (e.g., 'urgent', '12345')"
    )


def evaluate_condition(condition: FilterCondition, data: Dict[str, Any]) -> bool:
    """
    Evaluates a single filter condition against the given dataset.

    :param condition: The condition to evaluate.
    :param data: The dataset to evaluate the condition against.
    :return: True if the condition is satisfied, False otherwise.
    """
    field_value = data.get(condition.field)

    if field_value is None:
        return False

    # Evaluate based on the operator
    if condition.operator == Operator.CONTAINS:
        return isinstance(field_value, str) and condition.value in field_value
    elif condition.operator == Operator.EQUALS:
        return field_value == condition.value
    elif condition.operator == Operator.NOT_EQUALS:
        return field_value != condition.value
    elif condition.operator == Operator.STARTS_WITH:
        return isinstance(field_value, str) and field_value.startswith(
            str(condition.value)
        )
    elif condition.operator == Operator.ENDS_WITH:
        return isinstance(field_value, str) and field_value.endswith(
            str(condition.value)
        )
    elif condition.operator == Operator.GREATER_THAN:
        return field_value > condition.value
    elif condition.operator == Operator.LESS_THAN:
        return field_value < condition.value
    else:
        raise ValueError(f"Unsupported operator: {condition.operator}")


class FilterConfig(BaseModel):
    """
    Represents a collection of filtering conditions.
    """

    conditions: List[FilterCondition]
    match: MatchLogic = MatchLogic.ALL  # Default to "all"

    def evaluate(self, data: Dict[str, Any]) -> bool:
        """
        Evaluates the filter configuration against a given dataset.

        :param data: The dataset to evaluate against.
        :return: True if the filter matches, False otherwise.
        """
        results = [evaluate_condition(condition, data) for condition in self.conditions]

        if self.match == MatchLogic.ALL:
            return all(results)
        elif self.match == MatchLogic.ANY:
            return any(results)
        else:
            raise ValueError(f"Unsupported match logic: {self.match}")
