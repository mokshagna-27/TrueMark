from logging.config import fileConfig

from sqlalchemy import pool
from alembic import context

from database.connection import DatabaseConfigError, get_database_url, get_engine
from database.models import Base

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name, disable_existing_loggers=False)

# Add our models' MetaData object for autogenerate support
target_metadata = Base.metadata


def get_url() -> str:
    """Retrieve database URL safely from project configuration utilities."""
    return get_database_url()


# Dynamically set the database URL in Alembic config if available in environment
try:
    url = get_url()
    config.set_main_option("sqlalchemy.url", url.replace("%", "%%"))
except DatabaseConfigError:
    # If DATABASE_URL is not configured at module load, get_url will raise
    # DatabaseConfigError when migrations are actually executed.
    pass


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = get_url()
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    # Check if a connection was provided externally (e.g., test harness)
    connection = config.attributes.get("connection", None)

    if connection is not None:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
        )

        with context.begin_transaction():
            context.run_migrations()
    else:
        connectable = get_engine()

        with connectable.connect() as connection:
            context.configure(
                connection=connection,
                target_metadata=target_metadata,
            )

            with context.begin_transaction():
                context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
