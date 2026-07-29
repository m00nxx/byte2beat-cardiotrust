#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
REPO_ROOT="${BYTE2BEAT_GIT_ROOT:-${ROOT}/artifacts/runtime}"
PORT="${BYTE2BEAT_GIT_PORT:-9418}"

exec git daemon \
  --reuseaddr \
  --base-path="${REPO_ROOT}" \
  --export-all \
  --verbose \
  --informative-errors \
  --listen=0.0.0.0 \
  --port="${PORT}" \
  "${REPO_ROOT}"
