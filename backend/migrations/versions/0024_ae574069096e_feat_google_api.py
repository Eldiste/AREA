"""Feat: google API

Revision ID: ae574069096e
Revises: eeba97687abf
Create Date: 2025-01-19 22:03:55.838068

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy import text

# revision identifiers, used by Alembic.
revision: str = 'ae574069096e'
down_revision: Union[str, None] = 'eeba97687abf'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    conn = op.get_bind()

    # Check if Google service already exists
    existing_services = conn.execute(text("SELECT name FROM services")).fetchall()
    existing_service_names = {row[0] for row in existing_services}

    if "google" not in existing_service_names:
        conn.execute(
            text(
                "INSERT INTO services (name, description, created_at, updated_at) "
                "VALUES ('google', 'Google integration', now(), now())"
            )
        )

    # Add Google-specific actions
    existing_actions = conn.execute(text("SELECT name FROM actions")).fetchall()
    existing_action_names = {row[0] for row in existing_actions}
    google_actions = [
        {"name": "gmail_receive", "description": "Detects when a new email is received"}
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

    # Add Google-specific reactions
    existing_reactions = conn.execute(text("SELECT name FROM reactions")).fetchall()
    existing_reaction_names = {row[0] for row in existing_reactions}
    google_reactions = [
        {"name": "send_email", "description": "Sends an email through Gmail"}
    ]

    for reaction in google_reactions:
        if reaction["name"] not in existing_reaction_names:
            conn.execute(
                text(
                    "INSERT INTO reactions (service_id, name, description, created_at, updated_at) "
                    "VALUES ((SELECT id FROM services WHERE name = 'google'), :name, :description, now(), now())"
                ),
                {"name": reaction["name"], "description": reaction["description"]},
            )

    # Update existing Gmail action name if it exists
    conn.execute(
        text(
            "UPDATE actions SET name = 'gmail_receive', description = 'Detects when a new email is received' "
            "WHERE name = 'new_gmail' AND service_id = (SELECT id FROM services WHERE name = 'google')"
        )
    )


def downgrade():
    conn = op.get_bind()
    # Delete Google-related reactions and actions
    conn.execute(
        text("DELETE FROM reactions WHERE service_id = (SELECT id FROM services WHERE name = 'google')")
    )
    conn.execute(
        text("DELETE FROM actions WHERE service_id = (SELECT id FROM services WHERE name = 'google')")
    )
    conn.execute(
        text("DELETE FROM services WHERE name = 'google'")
    )