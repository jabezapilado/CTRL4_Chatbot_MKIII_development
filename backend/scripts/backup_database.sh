#!/usr/bin/env bash
set -euo pipefail

# Create one non-overwriting logical backup using a restricted MySQL defaults
# file. The defaults file keeps credentials out of process arguments and logs.

if [ "$#" -ne 1 ]; then
  echo "Usage: $0 /absolute/path/to/backup.sql" >&2
  exit 64
fi

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
PYTHON_BIN="${CTRL4_PYTHON:-$(cd "$BACKEND_DIR/.." && pwd)/.venv/bin/python}"
DEFAULTS_FILE="${CTRL4_MYSQL_DEFAULTS_FILE:-}"
OUTPUT_PATH="$1"

if [ ! -x "$PYTHON_BIN" ]; then
  echo "Configured CTRL4_PYTHON is not executable: $PYTHON_BIN" >&2
  exit 66
fi
if [ -z "$DEFAULTS_FILE" ] || [ ! -r "$DEFAULTS_FILE" ]; then
  echo "Set CTRL4_MYSQL_DEFAULTS_FILE to a readable, restricted MySQL defaults file." >&2
  exit 78
fi
if [ -e "$OUTPUT_PATH" ]; then
  echo "Refusing to overwrite an existing backup: $OUTPUT_PATH" >&2
  exit 73
fi
if ! command -v mysqldump >/dev/null 2>&1; then
  echo "mysqldump is required but was not found in PATH." >&2
  exit 69
fi

DATABASE_NAME="$(cd "$BACKEND_DIR" && "$PYTHON_BIN" -c 'from server.config import Config; print(Config().DB_NAME)')"
OUTPUT_DIRECTORY="$(dirname "$OUTPUT_PATH")"
mkdir -p "$OUTPUT_DIRECTORY"
umask 077
TEMPORARY_PATH="$(mktemp "$OUTPUT_DIRECTORY/.ctrl4-backup.XXXXXX")"
trap 'rm -f "$TEMPORARY_PATH"' EXIT

mysqldump \
  --defaults-extra-file="$DEFAULTS_FILE" \
  --single-transaction \
  --routines \
  --events \
  "$DATABASE_NAME" > "$TEMPORARY_PATH"

mv "$TEMPORARY_PATH" "$OUTPUT_PATH"
trap - EXIT
echo "Backup created: $OUTPUT_PATH"
