#!/usr/bin/env bash
# Open a private MySQL tunnel from this computer to the CTRL4 production VPS.
#
# No database password is stored here. Enter it only in the database client
# after connecting to 127.0.0.1:3307.
set -euo pipefail

# Use the provisioned VPS address by default so it matches the verified local
# SSH host key. The public website domain remains independent of SSH access.
readonly DEFAULT_HOST="185.227.134.221"
readonly DEFAULT_USER="ctrl4"
readonly DEFAULT_PORT="3307"

TUNNEL_HOST="${CTRL4_TUNNEL_HOST:-$DEFAULT_HOST}"
TUNNEL_USER="${CTRL4_TUNNEL_USER:-$DEFAULT_USER}"
LOCAL_PORT="${CTRL4_TUNNEL_PORT:-$DEFAULT_PORT}"

if ! [[ "$LOCAL_PORT" =~ ^[0-9]+$ ]] || (( LOCAL_PORT < 1024 || LOCAL_PORT > 65535 )); then
  echo "CTRL4_TUNNEL_PORT must be a local port from 1024 to 65535." >&2
  exit 2
fi

cat <<EOF
Opening a private CTRL4 production database tunnel:
  Local database client: 127.0.0.1:${LOCAL_PORT}
  Remote MySQL endpoint: 127.0.0.1:3306 on ${TUNNEL_HOST}

Keep this terminal open while using the database client. Press Ctrl+C to close it.
EOF

exec ssh \
  -N \
  -L "${LOCAL_PORT}:127.0.0.1:3306" \
  -o ExitOnForwardFailure=yes \
  -o ServerAliveInterval=30 \
  -o ServerAliveCountMax=3 \
  "${TUNNEL_USER}@${TUNNEL_HOST}"
