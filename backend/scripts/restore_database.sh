#!/usr/bin/env bash
set -euo pipefail

# Restore only into an explicitly named, separately created database. This
# script never drops, recreates, or writes to the active configured database.

if [ "$#" -ne 1 ]; then
  echo "Usage: CTRL4_RESTORE_DB_NAME=<empty_database> $0 /path/to/backup.sql" >&2
  exit 64
fi

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
PYTHON_BIN="${CTRL4_PYTHON:-$(cd "$BACKEND_DIR/.." && pwd)/.venv/bin/python}"
DEFAULTS_FILE="${CTRL4_MYSQL_DEFAULTS_FILE:-}"
RESTORE_DATABASE="${CTRL4_RESTORE_DB_NAME:-}"
BACKUP_PATH="$1"

if [ ! -x "$PYTHON_BIN" ]; then
  echo "Configured CTRL4_PYTHON is not executable: $PYTHON_BIN" >&2
  exit 66
fi
if [ -z "$DEFAULTS_FILE" ] || [ ! -r "$DEFAULTS_FILE" ]; then
  echo "Set CTRL4_MYSQL_DEFAULTS_FILE to a readable, restricted MySQL defaults file." >&2
  exit 78
fi
if [ ! -r "$BACKUP_PATH" ]; then
  echo "Backup file is not readable: $BACKUP_PATH" >&2
  exit 66
fi
if [[ ! "$RESTORE_DATABASE" =~ ^[A-Za-z0-9_]+$ ]]; then
  echo "CTRL4_RESTORE_DB_NAME must be an alphanumeric/underscore database name." >&2
  exit 64
fi
if ! command -v mysql >/dev/null 2>&1; then
  echo "mysql is required but was not found in PATH." >&2
  exit 69
fi

ACTIVE_DATABASE="$(cd "$BACKEND_DIR" && "$PYTHON_BIN" -c 'from server.config import Config; print(Config().DB_NAME)')"
if [ "$RESTORE_DATABASE" = "$ACTIVE_DATABASE" ]; then
  echo "Refusing to restore into the active configured database." >&2
  exit 73
fi

mysql --defaults-extra-file="$DEFAULTS_FILE" "$RESTORE_DATABASE" < "$BACKUP_PATH"
echo "Backup restored into: $RESTORE_DATABASE"
