from typing import Optional

from src.config import Settings


def make_db_url(
    driver: str, config: Settings, application_name: Optional[str] = None
) -> str:
    """
    Returns the database connection string from configuration values.

    :param driver: Driver name. Ex: psycopg2, asyncpg.
    :param config: Configuration. If not specified, the global configuration object is used.
    :param application_name: Application name.
    :returns: The database connection string.
    """
    host = config.postgres.host
    port = config.postgres.port
    user = config.postgres.user
    password = config.postgres.password
    database = config.postgres.database

    connection_string = f"postgresql+{driver}://{user}:"

    if password:
        connection_string += f"{password}"

    connection_string += "@"

    if host:
        connection_string += f"{host}:{port}"

    connection_string += f"/{database}"

    if application_name:
        connection_string += f"?application_name={application_name}"

    return connection_string
