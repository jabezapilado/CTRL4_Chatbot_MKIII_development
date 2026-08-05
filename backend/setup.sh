#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$SCRIPT_DIR"

VENV_DIR="${CTRL4_VENV_DIR:-$PROJECT_ROOT/.venv}"

if [ ! -d "$VENV_DIR" ]; then
  python3 -m venv "$VENV_DIR"
fi

"$VENV_DIR/bin/python" -m pip install --upgrade pip
"$VENV_DIR/bin/python" -m pip install -r requirements.txt

if [ ! -f ".env" ] && [ -f ".env.example" ]; then
  cp .env.example .env
  echo "Created backend/.env from backend/.env.example"
fi

"$VENV_DIR/bin/python" scripts/setup_database.py

echo "Backend setup complete."
echo "Run: $VENV_DIR/bin/python app.py"
