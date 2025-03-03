"""Add Trigger

Revision ID: 81d92b4d56e6
Revises: 5f23147a67a8
Create Date: 2024-12-04 16:44:10.563241

"""
from datetime import datetime
import json
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '81d92b4d56e6'
down_revision: Union[str, None] = '5f23147a67a8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None



def upgrade():
    # Insert a user
    op.execute(
        """
        INSERT INTO users (id, username, email, hashed_password, is_active, is_admin, created_at, updated_at)
        VALUES (
            1,
            'test_user',
            'test@example.com',
            'hashedpassword',  -- Replace with an actual hashed password
            TRUE,
            FALSE,
            NOW(),
            NOW()
        )
        """
    )

    # Insert an area
    op.execute(
        """
        INSERT INTO areas (id, user_id, action_id, reaction_id, created_at, updated_at)
        VALUES (
            1,  -- ID of the area
            1,  -- user_id
            1,  -- action_id (time_trigger)
            1,  -- reaction_id (print_reaction)
            NOW(),
            NOW()
        )
        """
    )

    # Insert a trigger for the area
    op.execute(
        """
        INSERT INTO triggers (area_id, config, created_at, updated_at)
        VALUES (
            1,  -- area_id
            '{"interval": 60, "last_run": 0}',  -- Trigger configuration
            NOW(),
            NOW()
        )
        """
    )


def downgrade():
    # Remove the trigger
    op.execute(
        """
        DELETE FROM triggers
        WHERE area_id = 1
        """
    )

    # Remove the area
    op.execute(
        """
        DELETE FROM areas
        WHERE id = 1
        """
    )

    # Remove the user
    op.execute(
        """
        DELETE FROM users
        WHERE id = 1
        """
    )