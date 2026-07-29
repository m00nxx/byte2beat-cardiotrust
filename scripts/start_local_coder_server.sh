#!/usr/bin/env bash
set -euo pipefail

PORT="${CODER_LOCAL_PORT:-30000}"
HTTP_ADDRESS="${CODER_LOCAL_HTTP_ADDRESS:-0.0.0.0:${PORT}}"
WSL_ADDRESS="$(hostname -I | awk '{print $1}')"
ACCESS_URL="${CODER_LOCAL_ACCESS_URL:-http://${WSL_ADDRESS}:${PORT}}"
WILDCARD_ACCESS_URL="${CODER_LOCAL_WILDCARD_ACCESS_URL:-*.localhost:${PORT}}"

echo "Starting Coder at ${ACCESS_URL}."
echo "Keep this terminal open while the Byte2Beat workspace is in use."

exec coder server \
  --http-address "${HTTP_ADDRESS}" \
  --access-url "${ACCESS_URL}" \
  --wildcard-access-url "${WILDCARD_ACCESS_URL}" \
  --telemetry=false
