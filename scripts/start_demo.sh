#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
RUNTIME_DIR="${ROOT}/artifacts/runtime"
PID_FILE="${RUNTIME_DIR}/streamlit.pid"
LOG_FILE="${RUNTIME_DIR}/streamlit.log"
HEALTH_URL="http://127.0.0.1:8501/_stcore/health"

cd "${ROOT}"
python scripts/coder_preflight.py

health_check() {
  python - "${HEALTH_URL}" <<'PY'
import sys
import urllib.request

try:
    with urllib.request.urlopen(sys.argv[1], timeout=2) as response:
        raise SystemExit(0 if response.status == 200 else 1)
except Exception:
    raise SystemExit(1)
PY
}

if health_check; then
  echo "CardioTrust is already healthy on port 8501."
  exit 0
fi

mkdir -p "${RUNTIME_DIR}"
if [[ -f "${PID_FILE}" ]] && kill -0 "$(cat "${PID_FILE}")" 2>/dev/null; then
  echo "Streamlit process exists but is not healthy; see ${LOG_FILE}." >&2
  exit 1
fi

nohup python -m streamlit run app.py \
  --server.address=0.0.0.0 \
  --server.port=8501 \
  --server.headless=true \
  >"${LOG_FILE}" 2>&1 &
echo "$!" >"${PID_FILE}"

for _ in $(seq 1 30); do
  if health_check; then
    echo "CardioTrust is healthy on port 8501."
    exit 0
  fi
  sleep 1
done

echo "CardioTrust failed its startup health check; see ${LOG_FILE}." >&2
exit 1
