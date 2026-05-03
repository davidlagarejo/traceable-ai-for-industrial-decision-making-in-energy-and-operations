#!/usr/bin/env bash
# ─────────────────────────────────────────────────────────────────────────────
# run_all_motors.sh
#
# Fully autonomous orchestrator runner.
# Loops cli.py run --watch until all motors are closed or nothing moves.
# Resumes automatically after any interruption (token limit, crash, Ctrl+C)
# because all state is persisted in motor_state.json files on disk.
#
# Usage:
#   ./run_all_motors.sh                      # advance all motors + generate Codex tasks for blocked ones
#   ./run_all_motors.sh --no-auto-approve    # pause on manual gates
#   ./run_all_motors.sh --dry-run            # show what would happen, no writes
#   ./run_all_motors.sh --interval 2         # sleep 2s between rounds
#
# When a motor is blocked, the orchestrator writes a Codex task to:
#   runtime/tasks/{motor_id}_{stage}.task.md
# Codex reads that file, executes the task, then re-runs this script.
# ─────────────────────────────────────────────────────────────────────────────

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PYTHON="${SCRIPT_DIR}/.venv/bin/python3"
CLI="${SCRIPT_DIR}/cli.py"
LOG="${SCRIPT_DIR}/runtime/run_all.log"

# ── defaults ──────────────────────────────────────────────────────────────────
AUTO_APPROVE="--auto-approve-gates"
DRY_RUN=""
INTERVAL="0"
MAX_ROUNDS="500"

# ── parse args ────────────────────────────────────────────────────────────────
while [[ $# -gt 0 ]]; do
  case "$1" in
    --no-auto-approve) AUTO_APPROVE="" ;;
    --dry-run)         DRY_RUN="--dry-run" ;;
    --interval)        INTERVAL="$2"; shift ;;
    --max-rounds)      MAX_ROUNDS="$2"; shift ;;
    *) echo "[WARN] Unknown arg: $1" ;;
  esac
  shift
done

# ── check python ──────────────────────────────────────────────────────────────
if [[ ! -f "$PYTHON" ]]; then
  echo "[ERROR] .venv not found. Run: python3.12 -m venv .venv && .venv/bin/pip install -e '.[dev]'"
  exit 1
fi

mkdir -p "${SCRIPT_DIR}/runtime"

echo "════════════════════════════════════════════════════════════"
echo "  Motor Creator — autonomous run"
echo "  auto_approve=${AUTO_APPROVE:+yes}"
echo "  dry_run=${DRY_RUN:+yes}"
echo "  interval=${INTERVAL}s  max_rounds=${MAX_ROUNDS}"
echo "  log → ${LOG}"
echo "════════════════════════════════════════════════════════════"
echo ""

# ── run ───────────────────────────────────────────────────────────────────────
# The Python orchestrator already handles its own loop via --watch.
# This shell wrapper adds: logging, exit code checking, and a resume message.

run_pass() {
  "$PYTHON" "$CLI" run \
    --watch \
    ${AUTO_APPROVE} \
    ${DRY_RUN} \
    --interval "$INTERVAL" \
    --max-rounds "$MAX_ROUNDS" \
    2>&1 | tee -a "$LOG"
  return "${PIPESTATUS[0]}"
}

EXIT_CODE=0
run_pass || EXIT_CODE=$?

echo ""
echo "────────────────────────────────────────────────────────────"
"$PYTHON" "$CLI" status 2>&1 | tee -a "$LOG"
echo "────────────────────────────────────────────────────────────"

if [[ $EXIT_CODE -eq 130 ]]; then
  echo ""
  echo "[INFO] Run was interrupted. All state is saved to disk."
  echo "[INFO] Resume by running this script again — it will continue from where it stopped."
  exit 130
fi

echo "[DONE] Exit code: $EXIT_CODE"
exit $EXIT_CODE
