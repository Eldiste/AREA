import os
import sys
from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from sqlalchemy.engine import create_engine
from alembic import context

# Add the project root directory to PYTHONPATH dynamically
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../")))

# Import your Base and settings
from src.db.models.base import Base  # Ensure your Base imports all models
from src.db.models.user import User
from src.db.models.action import Action
from src.db.models.service import Service
from src.db.models.user_service import UserService
from src.db.models.area import Area
from src.db.models.reaction import Reaction
from src.db.models.triggers import Trigger
from src.config import settings  # Ensure this points to your settings/config file

# Alembic Config object, provides access to the .ini file
config = context.config

print(config)
# Use a synchronous driver for Alembic migrations
sync_url = settings.postgres.make_db_url(driver="postgresql+psycopg2")
print(sync_url)
config.set_main_option("sqlalchemy.url", sync_url)

# Debug: Verify settings import
print("Database URL (sync for Alembic):", sync_url)

# Configure logging from the config file
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Add your model's metadata here for Alembic migrations
target_metadata = Base.metadata


def run_migrations_offline():
    """Run migrations in 'offline' mode."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    """Run migrations in 'online' mode."""
    connectable = create_engine(sync_url, poolclass=pool.NullPool)

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
        )

        with context.begin_transaction():
            context.run_migrations()
    print("hello world")


if context.is_offline_mode():
    print("hello world")
    run_migrations_offline()
else:
    print("hello world")

    run_migrations_online()
