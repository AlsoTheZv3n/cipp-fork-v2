import os
from logging.config import fileConfig

from alembic import context
from sqlalchemy import create_engine

from app.core.database import Base

# Import all models so Alembic sees them
from app.models.audit import AuditLog  # noqa: F401
from app.models.tenant import Tenant  # noqa: F401
from app.models.token_cache import TenantToken  # noqa: F401
from app.models.user import CippUser  # noqa: F401
from app.models.standard import BPATemplate, StandardResult, StandardTemplate  # noqa: F401
from app.models.template import CippLog, CippScheduledItem, CippTemplate  # noqa: F401

config = context.config

# Convert async URL to sync for Alembic migrations
async_url = os.getenv("DATABASE_URL", "postgresql+asyncpg://cipp:cipp_dev@localhost:5433/cipp")
sync_url = async_url.replace("postgresql+asyncpg", "postgresql+psycopg")
config.set_main_option("sqlalchemy.url", sync_url)

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")
    context.configure(url=url, target_metadata=target_metadata, literal_binds=True)
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    connectable = create_engine(config.get_main_option("sqlalchemy.url"))
    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()
    connectable.dispose()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
