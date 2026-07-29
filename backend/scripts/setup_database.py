from __future__ import annotations

from bootstrap import setup_paths

setup_paths()

from server.db import (
    initialize_database,
    seed_database,
    list_accounts,
)


def main() -> int:
    initialize_database()
    
    seed_database()

    accounts = list_accounts()

    print("Database initialized successfully.")
    print("All required tables have been created or verified.")
    print(f"Seeded accounts: {len(accounts)}")

    for account in accounts:
        print(f"- {account['email']} ({account['role']})")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())