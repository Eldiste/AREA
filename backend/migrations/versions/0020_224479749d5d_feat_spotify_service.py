"""Feat: spotify service

Revision ID: 224479749d5d
Revises: a6894550f53d
Create Date: 2025-01-19 18:10:42.563903

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy import text

# revision identifiers, used by Alembic.
revision: str = '224479749d5d'
down_revision: Union[str, None] = 'a6894550f53d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    conn = op.get_bind()

    existing_services = conn.execute(text("SELECT name FROM services")).fetchall()
    existing_service_names = {row[0] for row in existing_services}

    if "spotify" not in existing_service_names:
        conn.execute(
            text(
                "INSERT INTO services (name, description, created_at, updated_at) "
                "VALUES ('spotify', 'Spotify integration', now(), now())"
            )
        )

    existing_actions = conn.execute(text("SELECT name FROM actions")).fetchall()
    existing_action_names = {row[0] for row in existing_actions}

    spotify_actions = [
        {"name": "track_played", "description": "Detects when a track is played"},
    ]

    for action in spotify_actions:
        if action["name"] not in existing_action_names:
            conn.execute(
                text(
                    "INSERT INTO actions (service_id, name, description, created_at, updated_at) "
                    "VALUES ((SELECT id FROM services WHERE name = 'spotify'), :name, :description, now(), now())"
                ),
                {"name": action["name"], "description": action["description"]},
            )

    existing_reactions = conn.execute(text("SELECT name FROM reactions")).fetchall()
    existing_reaction_names = {row[0] for row in existing_reactions}

    spotify_reactions = [
        {"name": "add_to_playlist", "description": "Adds a track to a playlist"},
    ]

    for reaction in spotify_reactions:
        if reaction["name"] not in existing_reaction_names:
            conn.execute(
                text(
                    "INSERT INTO reactions (service_id, name, description, created_at, updated_at) "
                    "VALUES ((SELECT id FROM services WHERE name = 'spotify'), :name, :description, now(), now())"
                ),
                {"name": reaction["name"], "description": reaction["description"]},
            )


def downgrade() -> None:
    conn = op.get_bind()

    conn.execute(
        text("DELETE FROM reactions WHERE service_id = (SELECT id FROM services WHERE name = 'spotify')")
    )

    conn.execute(
        text("DELETE FROM actions WHERE service_id = (SELECT id FROM services WHERE name = 'spotify')")
    )

    conn.execute(
        text("DELETE FROM services WHERE name = 'spotify'")
    )