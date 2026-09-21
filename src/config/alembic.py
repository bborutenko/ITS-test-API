from __future__ import annotations

import logging
from pathlib import Path

from alembic import command
from alembic.config import Config

from config.settings import settings

logger = logging.getLogger(__name__)

__all__ = ["upgrade_all_migrations"]


def upgrade_all_migrations() -> None:
    base_dir = Path(__file__).resolve().parents[2]

    alembic_ini = base_dir / "alembic.ini"
    cfg = Config(str(alembic_ini)) if alembic_ini.exists() else Config()

    try:
        db_url = settings.database_url
    except Exception:
        db_url = settings.DATABASE_URL
    cfg.set_main_option("sqlalchemy.url", db_url)

    script_location = base_dir / "migrations"
    cfg.set_main_option("script_location", str(script_location))

    logger.info("Running Alembic migrations: %s -> head", script_location)
    command.upgrade(cfg, "head")
