#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="${HOME}/gcp-ai-governor"
VENV_PATH="${PROJECT_ROOT}/.venv"
MAIN_APP="${PROJECT_ROOT}/daemon/main.py"
SIMULATOR="${PROJECT_ROOT}/daemon/simulator/simulate_event.py"

if [ ! -d "${PROJECT_ROOT}" ]; then
  echo "Project directory not found: ${PROJECT_ROOT}"
  exit 1
fi

if [ ! -d "${VENV_PATH}" ]; then
  echo "Virtual environment not found: ${VENV_PATH}"
  exit 1
fi

source "${VENV_PATH}/bin/activate"

python3 "${MAIN_APP}" > "${PROJECT_ROOT}/smoke_test_server.log" 2>&1 &
SERVER_PID=$!

cleanup() {
  kill "${SERVER_PID}" >/dev/null 2>&1 || true
}
trap cleanup EXIT

sleep 2

echo "=== Health Check ==="
curl -s http://127.0.0.1:8080/health
echo
echo

echo "=== Simulation Run ==="
python3 "${SIMULATOR}"
echo
echo "Smoke test complete."
