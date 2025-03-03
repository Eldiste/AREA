"""add hash pass

Revision ID: 2d92830436ae
Revises: d69a4b6d9043
Create Date: 2024-12-08 22:30:30.836455

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '2d92830436ae'
down_revision: Union[str, None] = 'd69a4b6d9043'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('areas', sa.Column('action_config', sa.JSON(), nullable=True))
    op.add_column('areas', sa.Column('reaction_config', sa.JSON(), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('areas', 'reaction_config')
    op.drop_column('areas', 'action_config')
    # ### end Alembic commands ###
