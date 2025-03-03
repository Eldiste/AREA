"""Feat: new api

Revision ID: b2a6997dc43e
Revises: bc7a6ec6b1e2
Create Date: 2025-01-19 21:32:25.344078

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy import text

# revision identifiers, used by Alembic.
revision: str = 'b2a6997dc43e'
down_revision: Union[str, None] = 'bc7a6ec6b1e2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    conn = op.get_bind()

    existing_services = conn.execute(text("SELECT name FROM services")).fetchall()
    existing_service_names = {row[0] for row in existing_services}

    if "github" not in existing_service_names:
        conn.execute(
            text(
                "INSERT INTO services (name, description, created_at, updated_at) "
                "VALUES ('github', 'Github integration', now(), now())"
            )
        )

    existing_actions = conn.execute(text("SELECT name FROM actions")).fetchall()
    existing_action_names = {row[0] for row in existing_actions}

    spotify_actions = [
        {"name": "new_push", "description": "Detects a github commit"},
    ]

    for action in spotify_actions:
        if action["name"] not in existing_action_names:
            conn.execute(
                text(
                    "INSERT INTO actions (service_id, name, description, created_at, updated_at) "
                    "VALUES ((SELECT id FROM services WHERE name = 'github'), :name, :description, now(), now())"
                ),
                {"name": action["name"], "description": action["description"]},
            )

    existing_reactions = conn.execute(text("SELECT name FROM reactions")).fetchall()
    existing_reaction_names = {row[0] for row in existing_reactions}

    spotify_reactions = [
        {"name": "create_issue", "description": "Create Github Issue"},
    ]

    for reaction in spotify_reactions:
        if reaction["name"] not in existing_reaction_names:
            conn.execute(
                text(
                    "INSERT INTO reactions (service_id, name, description, created_at, updated_at) "
                    "VALUES ((SELECT id FROM services WHERE name = 'github'), :name, :description, now(), now())"
                ),
                {"name": reaction["name"], "description": reaction["description"]},
            )


def downgrade() -> None:
    conn = op.get_bind()

    conn.execute(
        text("DELETE FROM reactions WHERE service_id = (SELECT id FROM services WHERE name = 'github')")
    )

    conn.execute(
        text("DELETE FROM actions WHERE service_id = (SELECT id FROM services WHERE name = 'github')")
    )

    conn.execute(
        text("DELETE FROM services WHERE name = 'github'")
    )