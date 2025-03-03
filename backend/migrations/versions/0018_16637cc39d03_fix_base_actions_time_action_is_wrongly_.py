"""Fix: base actions time_action is wrongly named

Revision ID: 16637cc39d03
Revises: 1384ce79e0bc
Create Date: 2025-01-15 17:50:18.424416

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '16637cc39d03'
down_revision: Union[str, None] = '1384ce79e0bc'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None



def upgrade():
    # Rename time_trigger to time_action
    op.execute(
        """
        UPDATE actions
        SET name = 'time_action'
        WHERE name = 'time_trigger'
        """
    )

def downgrade():
    # Revert time_action back to time_trigger
    op.execute(
        """
        UPDATE actions
        SET name = 'time_trigger'
        WHERE name = 'time_action'
        """
    )

