"""Feat: time service

Revision ID: b2007d8b116b
Revises: 7a714bf8a184
Create Date: 2025-01-21 14:03:10.661661

"""
from typing import Sequence, Union

from alembic import op
from sqlalchemy import text

# revision identifiers, used by Alembic.
revision: str = 'b2007d8b116b'
down_revision: Union[str, None] = '7a714bf8a184'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None



def upgrade():
    conn = op.get_bind()

    # Check if Google service already exists
    existing_services = conn.execute(text("SELECT name FROM services")).fetchall()
    existing_service_names = {row[0] for row in existing_services}

    if "TimeService" not in existing_service_names:
        conn.execute(
            text(
                "INSERT INTO services (name, description, created_at, updated_at) "
                "VALUES ('TimeService', 'TimeService integration', now(), now())"
            )
        )

    # Add Google-specific actions
    existing_actions = conn.execute(text("SELECT name FROM actions")).fetchall()
    existing_action_names = {row[0] for row in existing_actions}
    google_actions = [
        {"name": "date_action", "description": "Detects When we pass a date"},
        {"name": "time_of_day_action", "description": "Repeat everyday"}
    ]

    for action in google_actions:
        if action["name"] not in existing_action_names:
            conn.execute(
                text(
                    "INSERT INTO actions (service_id, name, description, created_at, updated_at) "
                    "VALUES ((SELECT id FROM services WHERE name = 'google'), :name, :description, now(), now())"
                ),
                {"name": action["name"], "description": action["description"]},
            )



def downgrade():
    conn = op.get_bind()
    # Delete Google-related reactions and actions
    conn.execute(
        text("DELETE FROM reactions WHERE service_id = (SELECT id FROM services WHERE name = 'TimeService')")
    )
    conn.execute(
        text("DELETE FROM actions WHERE service_id = (SELECT id FROM services WHERE name = 'TimeService')")
    )
    conn.execute(
        text("DELETE FROM services WHERE name = 'TimeService'")
    )