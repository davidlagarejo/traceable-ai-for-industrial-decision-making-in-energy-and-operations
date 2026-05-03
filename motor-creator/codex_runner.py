#!/usr/bin/env python3
"""
codex_runner.py — Autonomous loop that drives Codex CLI to build all 33 motors.

Flow per iteration:
  1. Run orchestrator (--watch) → advances free motors, generates task files for blocked ones
  2. Find the next pending task file (dependency order)
  3. Invoke Codex CLI with a focused prompt
  4. After Codex exits (token limit, done, error) → run orchestrator to check progress
  5. If motor advanced → next task
  6. If still blocked → retry up to MAX_RETRIES, then skip
  7. Repeat until all eligible motors are closed or all remaining are hard-blocked

Usage:
  python codex_runner.py                        # full autonomous run
  python codex_runner.py --dry-run              # print tasks without running Codex
  python codex_runner.py --motor motor_001      # run only this motor
  python codex_runner.py --max-retries 5
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
from pathlib import Path

# ── path setup ────────────────────────────────────────────────────────────────
SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR / "src"))

from motor_creator.config import GOVERNANZA, MOTOR_DEPENDENCIES_FILE, RUNTIME_DIR
from motor_creator.dependency_checker import detect_cycles, get_eligible_motors
from motor_creator.loader import load_all_states, load_motor_dependencies
from motor_creator.models import MotorStatus, Stage
from motor_creator.orchestrator import Orchestrator
from motor_creator.task_generator import get_task_path

PYTHON = str(SCRIPT_DIR / ".venv" / "bin" / "python3")
CLI = str(SCRIPT_DIR / "cli.py")
TASKS_DIR = RUNTIME_DIR / "tasks"
LOG_FILE = RUNTIME_DIR / "codex_runner.log"
MAX_RETRIES_DEFAULT = 3


# ─── logging ──────────────────────────���───────────────────────────────��───────

def log(msg: str) -> None:
    from datetime import datetime, timezone
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    line = f"[{ts}] {msg}"
    print(line)
    RUNTIME_DIR.mkdir(parents=True, exist_ok=True)
    with LOG_FILE.open("a", encoding="utf-8") as f:
        f.write(line + "\n")


# ─── orchestrator helpers ──────────────────────────────────────────────────��──

def run_orchestrator() -> list[str]:
    """Run orchestrator --watch and return list of task files that were generated."""
    orc = Orchestrator(dry_run=False, auto_approve_gates=True)
    orc.startup_checks()
    results = orc.run_all()

    # Collect task files that now exist
    TASKS_DIR.mkdir(parents=True, exist_ok=True)
    return [str(p) for p in sorted(TASKS_DIR.glob("*.task.md"))]


def motor_is_closed(motor_id: str) -> bool:
    motors = load_motor_dependencies(MOTOR_DEPENDENCIES_FILE)
    all_states = load_all_states(motors, GOVERNANZA)
    s = all_states.get(motor_id)
    return s is not None and s.status == MotorStatus.CLOSED


def motor_advanced(motor_id: str, stage_before: str) -> bool:
    """Return True if the motor's stage changed or it closed."""
    motors = load_motor_dependencies(MOTOR_DEPENDENCIES_FILE)
    all_states = load_all_states(motors, GOVERNANZA)
    s = all_states.get(motor_id)
    if s is None:
        return False
    return s.status == MotorStatus.CLOSED or s.current_stage != stage_before


def get_motor_stage(motor_id: str) -> str:
    motors = load_motor_dependencies(MOTOR_DEPENDENCIES_FILE)
    all_states = load_all_states(motors, GOVERNANZA)
    s = all_states.get(motor_id)
    return s.current_stage if s else "not_started"


def all_done() -> bool:
    """Return True if all orchestrator-eligible motors are closed."""
    motors = load_motor_dependencies(MOTOR_DEPENDENCIES_FILE)
    all_states = load_all_states(motors, GOVERNANZA)
    for motor_id, entry in motors.items():
        if not entry.orchestrator_eligible:
            continue
        s = all_states.get(motor_id)
        if s is None or s.status != MotorStatus.CLOSED:
            return False
    return True


def count_status() -> dict:
    motors = load_motor_dependencies(MOTOR_DEPENDENCIES_FILE)
    all_states = load_all_states(motors, GOVERNANZA)
    counts = {"closed": 0, "in_progress": 0, "not_started": 0, "blocked": 0}
    for motor_id, entry in motors.items():
        if not entry.orchestrator_eligible:
            continue
        s = all_states.get(motor_id)
        if s is None:
            counts["not_started"] += 1
        elif s.status == MotorStatus.CLOSED:
            counts["closed"] += 1
        elif s.blocked:
            counts["blocked"] += 1
        else:
            counts["in_progress"] += 1
    return counts


# ─── task ordering ────────────────────────────────────────────────────────────

def next_pending_task(
    only_motor: str | None = None,
    skipped: set[str] | None = None,
) -> tuple[str, str, Path] | None:
    """
    Return (motor_id, stage, task_path) for the next task to run, in dependency order.
    Returns None if no pending tasks.
    """
    motors = load_motor_dependencies(MOTOR_DEPENDENCIES_FILE)
    all_states = load_all_states(motors, GOVERNANZA)
    eligible = get_eligible_motors(motors, all_states)
    skipped = skipped or set()

    for entry, _ in eligible:
        if only_motor and entry.motor_id != only_motor:
            continue
        if entry.motor_id in skipped:
            continue
        state = all_states.get(entry.motor_id)
        if state is None or state.status == MotorStatus.CLOSED:
            continue
        stage = state.current_stage
        task_file = get_task_path(entry.motor_id, Stage(stage))
        if task_file.exists():
            return (entry.motor_id, stage, task_file)

    return None


# ─── Codex invocation ─────────────────────────────────────────────────────────

_USAGE_LIMIT_PHRASES = (
    "usage limit",
    "rate limit",
    "quota exceeded",
    "upgrade to pro",
    "too many requests",
    "you have exceeded",
    "billing",
)
_USAGE_LIMIT_SLEEP_SECS = 35 * 60  # 35 min — slightly over the typical 30-min reset window


def _is_usage_limit(stdout: str, stderr: str, elapsed: float, returncode: int) -> bool:
    combined = (stdout + stderr).lower()
    if any(phrase in combined for phrase in _USAGE_LIMIT_PHRASES):
        return True
    # Heuristic: Codex exits with code 1 in < 15 s with very little output → not a task failure
    if returncode != 0 and elapsed < 15 and len(combined.strip()) < 300:
        return True
    return False


def build_codex_prompt(motor_id: str, stage: str, task_path: Path) -> str:
    """Build the focused prompt sent to Codex CLI."""
    from motor_creator.loader import load_motor_dependencies
    from motor_creator.config import MOTOR_DEPENDENCIES_FILE
    motors = load_motor_dependencies(MOTOR_DEPENDENCIES_FILE)
    entry = motors.get(motor_id)
    motor_slug = entry.slug if entry else motor_id
    return f"""Read and execute this task file completely:
{task_path}

Instructions:
1. Read every section of the task file carefully.
2. Edit each listed file, replacing ALL [PENDIENTE] markers with real, specific content.
3. For the implementation stage: write working Python code in the codebase/ directory.
4. When all files are filled, run this command to verify:
   cd {SCRIPT_DIR} && {PYTHON} {CLI} run --motor {motor_id} --auto-approve-gates
5. If the output shows action=advanced or action=closed — you are done. Stop.
6. If still blocked — read the new failure conditions, fix them, re-run the verify command.

Do NOT modify motor_state.json directly.
Do NOT leave any [PENDIENTE], TODO, TBD, or ??? in any file when you finish.
STRICT BOUNDARIES — do NOT touch these:
- motor-creator/ (codex_runner.py, cli.py, run_autonomous.sh, src/, tests/)
- governanza/automation-base/ (motor_registry.md, motor_dependencies.json, etc.)
- Any motor_state.json file

Your ONLY writable scope is:
  governanza/{motor_slug}/artifacts/{stage}/
"""


def run_codex(prompt: str, dry_run: bool = False) -> int:
    """Invoke Codex CLI with the given prompt.

    Detects usage-limit exits (fast exit, code≠0, minimal output) and sleeps
    until the quota resets before retrying the *same* task — without consuming
    a motor retry slot.  Returns 0 on success or non-zero on genuine failure.
    """
    cmd = [
        "codex",
        "exec",
        "--full-auto",
        "--cd",
        str(SCRIPT_DIR),
        "--add-dir",
        str(SCRIPT_DIR.parent),
        prompt,
    ]

    if dry_run:
        log(f"[DRY-RUN] Would run: {' '.join(cmd[:7])} <prompt>")
        log(f"[DRY-RUN] Prompt preview:\n{prompt[:400]}")
        return 0

    while True:
        log("Invoking Codex CLI for task...")
        t0 = time.time()
        result = subprocess.run(cmd, cwd=str(SCRIPT_DIR), capture_output=True, text=True)
        elapsed = time.time() - t0

        # Re-emit captured output so the shell tee still writes it to the log
        if result.stdout:
            print(result.stdout, end="", flush=True)
        if result.stderr:
            print(result.stderr, end="", file=sys.stderr, flush=True)

        if result.returncode == 0:
            return 0

        if _is_usage_limit(result.stdout, result.stderr, elapsed, result.returncode):
            wake_ts = time.strftime("%H:%M:%S", time.localtime(time.time() + _USAGE_LIMIT_SLEEP_SECS))
            log(
                f"⏸  Codex usage limit detected "
                f"(elapsed={elapsed:.1f}s, code={result.returncode}). "
                f"Sleeping {_USAGE_LIMIT_SLEEP_SECS // 60} min. "
                f"Will retry at ~{wake_ts} (local)."
            )
            time.sleep(_USAGE_LIMIT_SLEEP_SECS)
            log("⏵  Waking up after usage-limit sleep. Retrying same task...")
            continue  # retry without incrementing any retry counter

        # Genuine task failure (not a usage-limit issue)
        return result.returncode


# ─── main loop ───────────────────────���───────────────────────────────────���────

def run_loop(
    only_motor: str | None = None,
    max_retries: int = MAX_RETRIES_DEFAULT,
    dry_run: bool = False,
    interval: float = 2.0,
) -> int:
    log("=" * 60)
    log("Motor Creator — Codex autonomous runner starting")
    log(f"dry_run={dry_run}  max_retries={max_retries}  only_motor={only_motor or 'all'}")
    log("=" * 60)

    retry_counts: dict[str, int] = {}  # motor_id -> consecutive failures
    skipped: set[str] = set()
    global_rounds = 0
    MAX_GLOBAL_ROUNDS = 500

    while global_rounds < MAX_GLOBAL_ROUNDS:
        global_rounds += 1

        # Step 1: advance all free motors, generate task files for blocked ones
        log(f"\n── Round {global_rounds}: running orchestrator ──")
        run_orchestrator()
        status = count_status()
        log(f"Status: {status}")

        if all_done() and not only_motor:
            log("\n✓ All motors closed. Done.")
            return 0

        # Step 2: find next task
        task = next_pending_task(only_motor, skipped)
        if task is None:
            if only_motor:
                if motor_is_closed(only_motor):
                    log(f"✓ {only_motor} is closed.")
                    return 0
                log(f"No pending task for {only_motor}. Motor may be blocked by dependencies.")
                return 1
            # No tasks available — check if we're done or truly stuck
            remaining = {
                mid for mid, e in load_motor_dependencies(MOTOR_DEPENDENCIES_FILE).items()
                if e.orchestrator_eligible and not motor_is_closed(mid)
            }
            remaining -= skipped
            if not remaining:
                log("✓ All eligible motors closed.")
                return 0
            log(f"No tasks available. {len(remaining)} motors remain but none have pending tasks.")
            log(f"Remaining: {remaining}")
            log("Possible causes: all remaining motors are blocked by unmet dependencies.")
            return 1

        motor_id, stage, task_path = task

        if motor_id in skipped:
            log(f"Skipping {motor_id} (max retries exhausted previously).")
            continue

        log(f"\n── Task: {motor_id} / {stage} ──")
        log(f"Task file: {task_path}")

        stage_before = get_motor_stage(motor_id)

        # Step 3: invoke Codex
        prompt = build_codex_prompt(motor_id, stage, task_path)
        exit_code = run_codex(prompt, dry_run=dry_run)
        log(f"Codex exited with code {exit_code}")

        # Step 4: run orchestrator to check if motor advanced
        if not dry_run:
            time.sleep(interval)  # brief pause before re-checking
            run_orchestrator()

        advanced = motor_advanced(motor_id, stage_before)

        if advanced:
            log(f"✓ {motor_id} advanced (or closed). Retries reset.")
            retry_counts[motor_id] = 0
            # Delete the task file so we don't re-run it
            if task_path.exists():
                task_path.unlink()
        else:
            retry_counts[motor_id] = retry_counts.get(motor_id, 0) + 1
            attempts = retry_counts[motor_id]
            log(f"✗ {motor_id} did not advance. Attempt {attempts}/{max_retries}.")

            if attempts >= max_retries:
                log(f"  Max retries reached for {motor_id}. Skipping and continuing.")
                skipped.add(motor_id)

        if interval > 0 and not dry_run:
            time.sleep(interval)

    log(f"Reached max global rounds ({MAX_GLOBAL_ROUNDS}). Stopping.")
    return 1


# ─── CLI ──────────────────────────────────────────────────────────────────────

def main() -> int:
    p = argparse.ArgumentParser(description="Autonomous Codex runner for motor construction")
    p.add_argument("--motor", help="Run only this motor (e.g. motor_001)")
    p.add_argument("--dry-run", action="store_true", dest="dry_run",
                   help="Print tasks without invoking Codex")
    p.add_argument("--max-retries", type=int, default=MAX_RETRIES_DEFAULT, dest="max_retries",
                   help=f"Max Codex retries per task before skipping (default {MAX_RETRIES_DEFAULT})")
    p.add_argument("--interval", type=float, default=2.0,
                   help="Seconds between Codex invocations (default 2)")
    args = p.parse_args()

    return run_loop(
        only_motor=args.motor,
        max_retries=args.max_retries,
        dry_run=args.dry_run,
        interval=args.interval,
    )


if __name__ == "__main__":
    sys.exit(main())
