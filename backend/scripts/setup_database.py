from __future__ import annotations

import logging

from bootstrap import setup_paths

setup_paths()

from server.db import (
    initialize_database,
    seed_database,
    list_accounts,
)

logger = logging.getLogger(__name__)


def main() -> int:
    initialize_database()
    
    seed_database()

    accounts = list_accounts()

    logger.info("Database initialized successfully.")
    logger.info("All required tables have been created or verified.")
    logger.info("Seeded accounts: %s", len(accounts))

    for account in accounts:
        logger.info("- %s (%s)", account["email"], account["role"])

    return 0


if __name__ == "__main__":
    raise SystemExit(main())