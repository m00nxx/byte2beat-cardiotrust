#!/usr/bin/env bash
set -euo pipefail

STATE_DIR="${CODER_LOCAL_STATE_DIR:-${HOME}/.local/state/byte2beat-coder}"
PID_FILE="${STATE_DIR}/server.pid"
LOG_FILE="${STATE_DIR}/server.log"
HTTP_ADDRESS="${CODER_LOCAL_HTTP_ADDRESS:-0.0.0.0:3000}"
HEALTH_URL="${CODER_LOCAL_HEALTH_URL:-http://127.0.0.1:3000}"
WSL_ADDRESS="$(hostname -I | awk '{print $1}')"
ACCESS_URL="${CODER_LOCAL_ACCESS_URL:-http://${WSL_ADDRESS}:3000}"

mkdir -p "${STATE_DIR}"
chmod 700 "${STATE_DIR}"

if [[ -f "${PID_FILE}" ]] && kill -0 "$(cat "${PID_FILE}")" 2>/dev/null; then
  echo "Coder server is already running at ${ACCESS_URL}."
  exit 0
fi

nohup coder server \
  --http-address "${HTTP_ADDRESS}" \
  --access-url "${ACCESS_URL}" \
  --telemetry=false \
  >"${LOG_FILE}" 2>&1 &
echo "$!" >"${PID_FILE}"

for _ in $(seq 1 60); do
  if curl -fsS "${HEALTH_URL}/api/v2/buildinfo" >/dev/null 2>&1; then
    echo "Coder server is healthy at ${ACCESS_URL}."
    exit 0
  fi
  if ! kill -0 "$(cat "${PID_FILE}")" 2>/dev/null; then
    echo "Coder server exited; inspect ${LOG_FILE}." >&2
    exit 1
  fi
  sleep 1
done

echo "Coder server did not become healthy; inspect ${LOG_FILE}." >&2
exit 1
