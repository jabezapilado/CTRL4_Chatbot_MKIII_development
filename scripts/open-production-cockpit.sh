#!/usr/bin/env bash
# Open the Cockpit VPS administration UI through a private SSH tunnel.
# Cockpit's port 9090 remains closed to the public internet.
set -euo pipefail

readonly DEFAULT_HOST="185.227.134.221"
readonly DEFAULT_USER="ctrl4"
readonly DEFAULT_PORT="9090"

TUNNEL_HOST="${CTRL4_TUNNEL_HOST:-$DEFAULT_HOST}"
TUNNEL_USER="${CTRL4_TUNNEL_USER:-$DEFAULT_USER}"
LOCAL_PORT="${CTRL4_COCKPIT_TUNNEL_PORT:-$DEFAULT_PORT}"

if ! [[ "$LOCAL_PORT" =~ ^[0-9]+$ ]] || (( LOCAL_PORT < 1024 || LOCAL_PORT > 65535 )); then
  echo "CTRL4_COCKPIT_TUNNEL_PORT must be a local port from 1024 to 65535." >&2
  exit 2
fi

cat <<EOF
Opening private Cockpit administration access:
  Browser URL: https://127.0.0.1:${LOCAL_PORT}/
  VPS endpoint: 127.0.0.1:9090

Cockpit uses its own local TLS certificate, so the browser may show a
certificate warning for 127.0.0.1. Verify the URL is exactly localhost before
continuing. Keep this terminal open while using Cockpit, then press Ctrl+C to
close the tunnel.
EOF

exec ssh \
  -N \
  -L "${LOCAL_PORT}:127.0.0.1:9090" \
  -o ExitOnForwardFailure=yes \
  -o ServerAliveInterval=30 \
  -o ServerAliveCountMax=3 \
  "${TUNNEL_USER}@${TUNNEL_HOST}"
