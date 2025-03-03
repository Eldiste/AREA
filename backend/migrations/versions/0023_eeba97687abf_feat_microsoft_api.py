"""
Feat: microsoft API

Revision ID: eeba97687abf
Revises: b2a6997dc43e
Create Date: 2025-01-19 21:41:09.753322

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import text  # Corrected import

# revision identifiers, used by Alembic.
revision: str = 'eeba97687abf'
down_revision: Union[str, None] = 'b2a6997dc43e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    conn = op.get_bind()
    # Insert Outlook service if missing
    conn.execute(
        text(
            "INSERT INTO services (name, description, created_at, updated_at) "
            "SELECT 'outlook', 'Outlook integration', now(), now() "
            "WHERE NOT EXISTS (SELECT 1 FROM services WHERE name = 'outlook')"
        )
    )

    # Update existing mail_received action to outlook_receive
    conn.execute(
        text(
            "UPDATE actions SET name = 'outlook_receive', description = 'Detects when an Outlook mail is received' "
            "WHERE name = 'mail_received' AND service_id = (SELECT id FROM services WHERE name = 'outlook')"
        )
    )

    # Insert Outlook actions
    outlook_actions = [
        {"name": "outlook_receive", "description": "Detects when an Outlook mail is received"}
    ]
    for action in outlook_actions:
        conn.execute(
            text(
                "INSERT INTO actions (service_id, name, description, created_at, updated_at) "
                "SELECT (SELECT id FROM services WHERE name = 'outlook'), :name, :description, now(), now() "
                "WHERE NOT EXISTS (SELECT 1 FROM actions WHERE name = :name)"
            ),
            {"name": action["name"], "description": action["description"]},
        )

    # Insert Outlook reactions
    outlook_reactions = [
        {"name": "send_mail", "description": "Sends an Outlook mail"}
    ]
    for reaction in outlook_reactions:
        conn.execute(
            text(
                "INSERT INTO reactions (service_id, name, description, created_at, updated_at) "
                "SELECT (SELECT id FROM services WHERE name = 'outlook'), :name, :description, now(), now() "
                "WHERE NOT EXISTS (SELECT 1 FROM reactions WHERE name = :name)"
            ),
            {"name": reaction["name"], "description": reaction["description"]},
        )


def downgrade() -> None:
    conn = op.get_bind()
    conn.execute(text("DELETE FROM reactions WHERE service_id = (SELECT id FROM services WHERE name = 'outlook')"))
    conn.execute(text("DELETE FROM actions WHERE service_id = (SELECT id FROM services WHERE name = 'outlook')"))
    conn.execute(text("DELETE FROM services WHERE name = 'outlook'"))
