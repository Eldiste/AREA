"""Feat: new actions

Revision ID: 1384ce79e0bc
Revises: 86cbfd0e2cdb
Create Date: 2024-12-10 12:17:58.990094

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from datetime import datetime

# revision identifiers, used by Alembic.
revision: str = '1384ce79e0bc'
down_revision: Union[str, None] = '86cbfd0e2cdb'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


# List of actions to add
NEW_ACTIONS = [
    {"service_id": 4, "name": "channel_deleted", "description": "Detects when a channel is deleted"},
    {"service_id": 4, "name": "channel_updated", "description": "Detects when a channel is updated"},
    {"service_id": 4, "name": "member_removed", "description": "Detects when a member is removed"},
    {"service_id": 4, "name": "message_updated", "description": "Detects when a message is updated"},
]


def upgrade() -> None:
    # Insert new actions into the actions table
    for action in NEW_ACTIONS:
        op.execute(
            f"""
            INSERT INTO actions (service_id, name, description, created_at, updated_at)
            VALUES ({action['service_id']}, '{action['name']}', '{action['description']}', '{datetime.utcnow()}', '{datetime.utcnow()}')
            """
        )


def downgrade() -> None:
    # Remove the added actions from the actions table
    for action in NEW_ACTIONS:
        op.execute(
            f"DELETE FROM actions WHERE name = '{action['name']}'"
        )
