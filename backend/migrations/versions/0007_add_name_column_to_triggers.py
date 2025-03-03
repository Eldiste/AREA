from alembic import op
import sqlalchemy as sa


# Revision identifiers, used by Alembic.
revision = '734c86237fc1'
down_revision = '30e42c914bac'
branch_labels = None
depends_on = None


def upgrade():
    # Step 1: Add the 'name' column as nullable
    op.add_column('triggers', sa.Column('name', sa.String(length=100), nullable=True))

    # Step 2: Populate the 'name' column with the default value
    op.execute("UPDATE triggers SET name = 'time_trigger'")

    # Step 3: Alter the 'name' column to make it NOT NULL
    op.alter_column('triggers', 'name', nullable=False)


def downgrade():
    # Remove the 'name' column
    op.drop_column('triggers', 'name')
