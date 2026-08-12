#!/usr/bin/env bash
# Open phpMyAdmin in the local browser through a private SSH tunnel.
# phpMyAdmin remains bound to 127.0.0.1 on the production VPS.
set -euo pipefail

readonly DEFAULT_HOST="185.227.134.221"
readonly DEFAULT_USER="ctrl4"
readonly DEFAULT_PORT="8080"
readonly REMOTE_PORT="8081"

TUNNEL_HOST="${CTRL4_TUNNEL_HOST:-$DEFAULT_HOST}"
TUNNEL_USER="${CTRL4_TUNNEL_USER:-$DEFAULT_USER}"
LOCAL_PORT="${CTRL4_PHPMYADMIN_TUNNEL_PORT:-$DEFAULT_PORT}"

if ! [[ "$LOCAL_PORT" =~ ^[0-9]+$ ]] || (( LOCAL_PORT < 1024 || LOCAL_PORT > 65535 )); then
  echo "CTRL4_PHPMYADMIN_TUNNEL_PORT must be a local port from 1024 to 65535." >&2
  exit 2
fi

cat <<EOF
Opening private phpMyAdmin access:
  Browser URL: http://127.0.0.1:${LOCAL_PORT}/
  VPS endpoint: 127.0.0.1:${REMOTE_PORT}

Open the browser URL after the tunnel is connected. Keep this terminal open
while using phpMyAdmin, then press Ctrl+C to close the tunnel.
EOF

exec ssh \
  -N \
  -L "${LOCAL_PORT}:127.0.0.1:${REMOTE_PORT}" \
  -o ExitOnForwardFailure=yes \
  -o ServerAliveInterval=30 \
  -o ServerAliveCountMax=3 \
  "${TUNNEL_USER}@${TUNNEL_HOST}"
