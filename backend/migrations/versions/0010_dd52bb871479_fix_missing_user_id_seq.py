"""Fix missing user_id_seq

Revision ID: dd52bb871479
Revises: 62a89bf08c56
Create Date: 2024-12-07 23:33:45.807155

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.

revision: str = 'dd52bb871479'
down_revision: Union[str, None] = '62a89bf08c56'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.execute("CREATE SEQUENCE user_id_seq START 1 INCREMENT 1")
    op.alter_column(
        "users",
        "id",
        server_default=sa.text("nextval('user_id_seq')")
    )

def downgrade():
    op.execute("DROP SEQUENCE user_id_seq")
