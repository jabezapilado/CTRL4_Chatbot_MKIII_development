from __future__ import annotations

import argparse
import logging

from bootstrap import setup_paths

setup_paths()

from server.db import (
    initialize_database,
    seed_database,
    list_accounts,
)
from server.config import Config

logger = logging.getLogger(__name__)


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Initialize the configured CTRL4 database.",
    )
    parser.add_argument(
        "--seed",
        action="store_true",
        help="Seed optional development accounts after initialization.",
    )
    return parser.parse_args()


def main() -> int:
    args = _parse_args()
    config = Config()

    if config.IS_PRODUCTION and not config.DATABASE_BACKUP_CONFIRMED:
        logger.error(
            "Database initialization refused: confirm a verified backup before a production upgrade."
        )
        return 2

    initialize_database()

    # Preserve the established development setup behavior. Production only
    # seeds when explicitly requested by an operator.
    if not config.IS_PRODUCTION or args.seed:
        seed_database()

    accounts = list_accounts()

    logger.info("Database initialized successfully.")
    logger.info("All required tables have been created or verified.")
    logger.info("Account records present: %s", len(accounts))

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
