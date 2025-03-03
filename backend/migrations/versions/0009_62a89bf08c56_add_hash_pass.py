"""add hash pass

Revision ID: 62a89bf08c56
Revises: 2ec5f406dc32
Create Date: 2024-12-07 23:28:47.458836

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.engine.reflection import Inspector


# revision identifiers, used by Alembic.
revision: str = '62a89bf08c56'
down_revision: Union[str, None] = '2ec5f406dc32'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    conn = op.get_bind()
    inspector = Inspector.from_engine(conn)

    # Check existing columns in user_services
    user_services_columns = [col["name"] for col in inspector.get_columns("user_services")]
    if "access_token" not in user_services_columns:
        op.add_column("user_services", sa.Column("access_token", sa.String(), nullable=True))
    if "refresh_token" not in user_services_columns:
        op.add_column("user_services", sa.Column("refresh_token", sa.String(), nullable=True))
    if "created_at" not in user_services_columns:
        op.add_column("user_services", sa.Column("created_at", sa.DateTime(), nullable=False))
    if "updated_at" not in user_services_columns:
        op.add_column("user_services", sa.Column("updated_at", sa.DateTime(), nullable=False))

    # Alter existing columns
    op.alter_column('user_services', 'id',
                    existing_type=sa.INTEGER(),
                    type_=sa.BigInteger(),
                    existing_nullable=False,
                    autoincrement=True)
    op.alter_column('user_services', 'user_id',
                    existing_type=sa.INTEGER(),
                    type_=sa.BigInteger(),
                    existing_nullable=False)
    op.alter_column('user_services', 'service_id',
                    existing_type=sa.INTEGER(),
                    type_=sa.BigInteger(),
                    existing_nullable=False)

    # Check existing columns in users
    users_columns = [col["name"] for col in inspector.get_columns("users")]
    if "hashed_password" not in users_columns:
        op.add_column("users", sa.Column("hashed_password", sa.String(length=255), nullable=True))
    if "is_active" not in users_columns:
        op.add_column("users", sa.Column("is_active", sa.Boolean(), nullable=True))
    if "is_admin" not in users_columns:
        op.add_column("users", sa.Column("is_admin", sa.Boolean(), nullable=True))
    if "is_oauth" not in users_columns:
        op.add_column("users", sa.Column("is_oauth", sa.Boolean(), nullable=True))

    # Alter existing columns
    op.alter_column('users', 'id',
                    existing_type=sa.INTEGER(),
                    type_=sa.BigInteger(),
                    existing_nullable=False,
                    autoincrement=True,
                    existing_server_default=sa.text("nextval('users_id_seq'::regclass)"))


def downgrade() -> None:
    op.alter_column('users', 'id',
                    existing_type=sa.BigInteger(),
                    type_=sa.INTEGER(),
                    existing_nullable=False,
                    autoincrement=True,
                    existing_server_default=sa.text("nextval('users_id_seq'::regclass)"))
    op.drop_column('users', 'is_oauth')
    op.drop_column('users', 'is_admin')
    op.drop_column('users', 'is_active')
    op.drop_column('users', 'hashed_password')
    op.alter_column('user_services', 'service_id',
                    existing_type=sa.BigInteger(),
                    type_=sa.INTEGER(),
                    existing_nullable=False)
    op.alter_column('user_services', 'user_id',
                    existing_type=sa.BigInteger(),
                    type_=sa.INTEGER(),
                    existing_nullable=False)
    op.alter_column('user_services', 'id',
                    existing_type=sa.BigInteger(),
                    type_=sa.INTEGER(),
                    existing_nullable=False,
                    autoincrement=True)
    op.drop_column('user_services', 'updated_at')
    op.drop_column('user_services', 'created_at')
    op.drop_column('user_services', 'refresh_token')
    op.drop_column('user_services', 'access_token')
