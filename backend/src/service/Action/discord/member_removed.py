import logging
from typing import Optional

from pydantic import Field

from src.service.Action.actions import Action, ActionConfig, ActionResponse

LOGGER = logging.getLogger(__name__)


class MemberRemovedActionConfig(ActionConfig):
    """
    Configuration schema for the MemberRemovedAction.
    """

    user_id: str = Field(..., description="The ID of the member removed.")
    user_name: str = Field(..., description="The name of the member removed.")


class MemberRemovedResponse(ActionResponse):
    """
    Response schema for MemberRemovedAction.
    """

    user_id: str
    user_name: str


class MemberRemovedAction(Action):
    name = "member_removed"
    config = MemberRemovedActionConfig

    def __init__(self, config: MemberRemovedActionConfig):
        """
        Initialize the action with member removal details.
        :param config: MemberRemovedActionConfig containing the member data.
        """
        super().__init__(config)

    async def execute(self, *args, **kwargs) -> Optional[MemberRemovedResponse]:
        """
        Process the member removal details.
        :return: A dictionary with the removed member details.
        """
        try:
            # Log the member removal
            LOGGER.info(
                f"User {self.config.user_name} (ID: {self.config.user_id}) was removed from the guild."
            )

            # Return a successful response
            return MemberRemovedResponse(
                user_id=self.config.user_id,
                user_name=self.config.user_name,
            )

        except Exception as e:
            LOGGER.error(f"Error processing member removal: {str(e)}")
            return None
