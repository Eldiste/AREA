"""Add Discord service, actions, and reactions

Revision ID: 7b049b642570
Revises: 00b5f8b31ced
Create Date: 2024-12-08 14:37:55.659614

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy import text

# revision identifiers, used by Alembic.
revision: str = '7b049b642570'
down_revision: Union[str, None] = '00b5f8b31ced'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():

    # Create the sequence if it does not exist
    op.execute(text("CREATE SEQUENCE IF NOT EXISTS services_id_seq START 1"))
    op.execute(text("CREATE SEQUENCE IF NOT EXISTS actions_id_seq START 1"))
    op.execute(text("CREATE SEQUENCE IF NOT EXISTS reactions_id_seq START 1"))

    # Sync the sequence values with the current max id
    op.execute(text("SELECT setval('services_id_seq', (SELECT MAX(id) FROM services) + 1)"))
    op.execute(text("SELECT setval('actions_id_seq', (SELECT MAX(id) FROM actions) + 1)"))
    op.execute(text("SELECT setval('reactions_id_seq', (SELECT MAX(id) FROM reactions) + 1)"))

    # Set default for sequences in case it isn't already set
    op.execute(text("ALTER TABLE services ALTER COLUMN id SET DEFAULT nextval('services_id_seq')"))
    op.execute(text("ALTER TABLE actions ALTER COLUMN id SET DEFAULT nextval('actions_id_seq')"))
    op.execute(text("ALTER TABLE reactions ALTER COLUMN id SET DEFAULT nextval('reactions_id_seq')"))

    # Insert the Discord service
    conn = op.get_bind()
    existing_services = conn.execute(text("SELECT name FROM services")).fetchall()
    existing_service_names = {row[0] for row in existing_services}

    if "discord" not in existing_service_names:
        conn.execute(
            text(
                "INSERT INTO services (name, description, created_at, updated_at) "
                "VALUES ('discord', 'Discord integration', now(), now())"
            )
        )

    # Fetch the Discord service ID
    discord_service_id = conn.execute(
        text("SELECT id FROM services WHERE name = 'discord'")
    ).scalar()

    # Insert Discord actions
    existing_actions = conn.execute(text("SELECT name FROM actions")).fetchall()
    existing_action_names = {row[0] for row in existing_actions}

    actions = [
        {"name": "new_message_in_channel", "description": "Detects a new message in a channel"},
        {"name": "user_joins_guild", "description": "Detects when a user joins a guild"},
        {"name": "guild_role_added", "description": "Detects when a new role is added to a guild"},
        {"name": "channel_created", "description": "Detects when a new channel is created"},
    ]

    for action in actions:
        if action["name"] not in existing_action_names:
            conn.execute(
                text(
                    "INSERT INTO actions (service_id, name, description, created_at, updated_at) "
                    "VALUES (:service_id, :name, :description, now(), now())"
                ),
                {"service_id": discord_service_id, "name": action["name"], "description": action["description"]},
            )

    # Insert Discord reactions
    existing_reactions = conn.execute(text("SELECT name FROM reactions")).fetchall()
    existing_reaction_names = {row[0] for row in existing_reactions}

    reactions = [
        {"name": "send_message", "description": "Sends a message to a channel"},
        {"name": "add_reaction", "description": "Adds a reaction to a message"},
        {"name": "delete_message", "description": "Deletes a message from a channel"},
        {"name": "edit_message", "description": "Edits the content of a message"},
    ]

    for reaction in reactions:
        if reaction["name"] not in existing_reaction_names:
            conn.execute(
                text(
                    "INSERT INTO reactions (service_id, name, description, created_at, updated_at) "
                    "VALUES (:service_id, :name, :description, now(), now())"
                ),
                {"service_id": discord_service_id, "name": reaction["name"], "description": reaction["description"]},
            )


def downgrade() -> None:
    conn = op.get_bind()

    # Fetch the Discord service ID
    discord_service_id = conn.execute(
        text("SELECT id FROM services WHERE name = 'discord'")
    ).scalar()

    # Delete reactions linked to Discord
    conn.execute(text("DELETE FROM reactions WHERE service_id = :service_id"), {"service_id": discord_service_id})

    # Delete actions linked to Discord
    conn.execute(text("DELETE FROM actions WHERE service_id = :service_id"), {"service_id": discord_service_id})

    # Delete the Discord service
    conn.execute(text("DELETE FROM services WHERE id = :service_id"), {"service_id": discord_service_id})
