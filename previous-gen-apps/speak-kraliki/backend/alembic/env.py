"""
Alembic Environment Configuration
"""

from logging.config import fileConfig

from sqlalchemy import pool, create_engine
from sqlalchemy.engine import Connection

from alembic import context

from app.core.config import settings
from app.core.database import Base
from app.models import *  # noqa: Import all models

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata

# Use sync driver for migrations (replace asyncpg with psycopg2)
sync_url = settings.database_url.replace("+asyncpg", "+psycopg2")


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    context.configure(
        url=sync_url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode with sync engine."""
    connectable = create_engine(
        sync_url,
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)

        with context.begin_transaction():
            context.run_migrations()

    connectable.dispose()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
