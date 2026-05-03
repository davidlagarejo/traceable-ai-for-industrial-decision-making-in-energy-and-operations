#!/usr/bin/env bash
# ─────────────────────────────────────────────────────────────────────────────
# run_autonomous.sh
#
# Arranca y mantiene el loop autónomo de Codex CLI hasta que los 33 motores
# estén cerrados. Si Codex sale por límite de tokens o cualquier otra razón,
# el loop lo reinicia automáticamente en el siguiente task pendiente.
#
# Usage:
#   ./run_autonomous.sh                     # corre todo
#   ./run_autonomous.sh --motor motor_001   # solo un motor
#   ./run_autonomous.sh --dry-run           # muestra tasks sin ejecutar Codex
#   ./run_autonomous.sh --max-retries 5
# ─────────────────────────────────────────────────────────────────────────────

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PYTHON="${SCRIPT_DIR}/.venv/bin/python3"
RUNNER="${SCRIPT_DIR}/codex_runner.py"
LOG="${SCRIPT_DIR}/runtime/codex_runner.log"

# ── args ──────────────────────────────────────────────────────────────────────
EXTRA_ARGS=("$@")

# ── checks ────────────────────────────────────────────────────────────────────
if [[ ! -f "$PYTHON" ]]; then
  echo "[ERROR] .venv not found."
  echo "  Run: python3.12 -m venv .venv && .venv/bin/pip install -e '.[dev]'"
  exit 1
fi

if ! command -v codex &>/dev/null; then
  echo "[ERROR] 'codex' CLI not found in PATH."
  echo "  Install: npm install -g @openai/codex"
  echo "  Then set: export OPENAI_API_KEY=..."
  exit 1
fi

mkdir -p "${SCRIPT_DIR}/runtime"

echo ""
echo "══════════════════════════════════════════════��═════════════"
echo "  Motor Creator — Autonomous Codex Runner"
echo "  log → ${LOG}"
echo "════════════════════════════════════════════════════════════"
echo ""

# ── run ───────────────────────────────────────────────────────────────────────
# The Python runner handles all retry logic internally.
# This shell script just ensures it restarts if it crashes unexpectedly.

# Shell-level restarts are a last-resort safety net.
# Usage-limit detection and sleeping is handled inside codex_runner.py itself,
# so the Python process should rarely need to be restarted for that reason.
# This counter guards against genuine crashes or unexpected exits.
MAX_SHELL_RESTARTS=200
RESTART_COUNT=0

while [[ $RESTART_COUNT -lt $MAX_SHELL_RESTARTS ]]; do
  EXIT_CODE=0
  if [[ ${#EXTRA_ARGS[@]} -gt 0 ]]; then
    "$PYTHON" "$RUNNER" "${EXTRA_ARGS[@]}" 2>&1 | tee -a "$LOG" || EXIT_CODE=$?
  else
    "$PYTHON" "$RUNNER" 2>&1 | tee -a "$LOG" || EXIT_CODE=$?
  fi

  if [[ $EXIT_CODE -eq 0 ]]; then
    echo ""
    echo "✓ All motors complete."
    break
  fi

  if [[ $EXIT_CODE -eq 130 ]]; then
    echo ""
    echo "[INFO] Interrupted by user. State is saved."
    echo "[INFO] Re-run this script to continue."
    exit 130
  fi

  RESTART_COUNT=$((RESTART_COUNT + 1))
  echo ""
  echo "[WARN] Runner exited with code $EXIT_CODE. Restart $RESTART_COUNT/$MAX_SHELL_RESTARTS..."
  echo "[INFO] All state is persisted. Continuing from last checkpoint."
  # Brief pause before restart to avoid hammering on a hard block
  sleep 30
done

if [[ $RESTART_COUNT -ge $MAX_SHELL_RESTARTS ]]; then
  echo "[ERROR] Max shell restarts reached. Check ${LOG} for details."
  exit 1
fi

# ── final status ──────────────────────────────────────────────────────────────
echo ""
echo "────────────────────────────────────────────────────────────"
"$PYTHON" "${SCRIPT_DIR}/cli.py" status 2>&1 | tee -a "$LOG"
echo "────────────────────────────────────────────────────────────"
