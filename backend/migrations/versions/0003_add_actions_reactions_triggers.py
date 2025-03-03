"""Add actions, reactions, and triggers

Revision ID: 5f23147a67a8
Revises: 34643999177f
Create Date: 2024-12-04 16:21:42.895090

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '5f23147a67a8'
down_revision: Union[str, None] = '34643999177f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    # Insert services
    op.execute(
        """
        INSERT INTO services (id, name, description, created_at, updated_at)
        VALUES
        (1, 'TimeService', 'Service for time-based triggers', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
        (2, 'PrintService', 'Service for printing messages', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
        """
    )

    # Insert actions
    op.execute(
        """
        INSERT INTO actions (id, service_id, name, description, created_at, updated_at)
        VALUES
        (1, 1, 'time_trigger', 'Trigger that activates at regular intervals', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
        (2, 2, 'print_message', 'Action that prints a message', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
        """
    )

    # Insert reactions
    op.execute(
        """
        INSERT INTO reactions (id, service_id, name, description, created_at, updated_at)
        VALUES
        (1, 2, 'print_reaction', 'Reaction that prints the result', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
        """
    )


def downgrade():
    # Remove the seed data if the migration is rolled back
    op.execute("DELETE FROM reactions WHERE id IN (1)")
    op.execute("DELETE FROM actions WHERE id IN (1, 2)")
    op.execute("DELETE FROM services WHERE id IN (1, 2)")