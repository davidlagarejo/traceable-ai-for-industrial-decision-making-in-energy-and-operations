#!/usr/bin/env python3
"""
Motor Creator CLI
Usage:
  python cli.py run [--motor motor_001] [--all] [--dry-run]
  python cli.py run --watch [--auto-approve-gates] [--max-rounds 200] [--interval 0]
  python cli.py status
  python cli.py approve --motor motor_001 --gate gate_1
  python cli.py correct --motor motor_001 --to-stage documentation_base --reason "..."
  python cli.py init --motor motor_001 [--dry-run]
"""
from __future__ import annotations

import argparse
import json
import signal
import sys
from pathlib import Path

# Ensure src/ is in path when running from repo root
sys.path.insert(0, str(Path(__file__).parent / "src"))

from motor_creator.models import Stage
from motor_creator.orchestrator import Orchestrator


# ─── signal handler for clean Ctrl+C ─────────────────────────────────────────

_interrupted = False


def _handle_sigint(signum, frame):
    global _interrupted
    _interrupted = True
    print("\n[INTERRUPT] Signal received. Finishing current motor and stopping cleanly...")


signal.signal(signal.SIGINT, _handle_sigint)


# ─── commands ─────────────────────────────────────────────────────────────────

def cmd_run(args: argparse.Namespace) -> int:
    orc = Orchestrator(
        dry_run=args.dry_run,
        auto_approve_gates=args.auto_approve_gates,
    )

    # ── watch mode: loop until done ──────────────────────────────────────────
    if args.watch:
        print(
            f"[WATCH] Starting autonomous loop "
            f"(max_rounds={args.max_rounds}, interval={args.interval}s, "
            f"auto_approve_gates={args.auto_approve_gates})"
        )
        try:
            summary = _run_watch(orc, args)
        except KeyboardInterrupt:
            print("\n[WATCH] Interrupted by user.")
            return 130

        print("\n[WATCH] Run complete.")
        print(f"  rounds:        {summary['rounds']}")
        print(f"  closed:        {summary['closed']}")
        print(f"  in_progress:   {summary['in_progress']}")
        print(f"  blocked:       {summary['blocked']}")
        print(f"  paused:        {summary['paused']}")
        print(f"  not_started:   {summary['not_started']}")
        print(f"  total actions: {summary['total_actions']}")
        return 0

    # ── single motor ─────────────────────────────────────────────────────────
    if args.motor:
        result = orc.run_one(args.motor)
        _print_result(result, args.dry_run)
        return 0 if result.action not in ("error",) else 1

    # ── all eligible in one pass ──────────────────────────────────────────────
    if args.all:
        results = orc.run_all()
        for r in results:
            _print_result(r, args.dry_run)
        return 0

    # ── default: process next eligible motor ─────────────────────────────────
    result = orc.run_next()
    if result is None:
        print("[INFO] No eligible motors found.")
        return 0
    _print_result(result, args.dry_run)
    return 0 if result.action not in ("error",) else 1


def _run_watch(orc: Orchestrator, args: argparse.Namespace) -> dict:
    """
    Autonomous loop. Calls run_until_done() which already handles progress
    detection internally. Re-enters on context interruption (token limit pause)
    because state is always persisted to disk.
    """
    import time
    from motor_creator.loader import load_all_states
    from motor_creator.models import MotorStatus

    total_rounds = 0
    total_actions = 0

    while total_rounds < args.max_rounds and not _interrupted:
        # Run one pass over all currently eligible motors
        all_states = load_all_states(orc.motors, orc.governanza)
        from motor_creator.dependency_checker import get_eligible_motors
        eligible = get_eligible_motors(orc.motors, all_states)

        if not eligible:
            break

        progress_this_pass = False

        for entry, _ in eligible:
            if _interrupted:
                break
            all_states = load_all_states(orc.motors, orc.governanza)
            result = orc._process_motor(entry, all_states)
            total_rounds += 1
            total_actions += 1
            _print_result(result, orc.dry_run)

            if result.action in ("advanced", "closed"):
                progress_this_pass = True
            if result.action == "error":
                print(f"[ERROR] Fatal error on {entry.motor_id}. Stopping.")
                progress_this_pass = False
                break

        if not progress_this_pass:
            break  # All remaining motors are blocked/paused — no point continuing

        if args.interval > 0 and not _interrupted:
            time.sleep(args.interval)

    # Final tallies
    final_states = load_all_states(orc.motors, orc.governanza)
    counts: dict[str, int] = {
        "closed": 0, "in_progress": 0, "not_started": 0, "blocked": 0, "paused": 0,
    }
    for motor_id, entry in orc.motors.items():
        if not entry.orchestrator_eligible:
            continue
        s = final_states.get(motor_id)
        if s is None:
            counts["not_started"] += 1
            continue
        if s.status == MotorStatus.CLOSED:
            counts["closed"] += 1
        elif s.blocked:
            counts["blocked"] += 1
        elif s.paused:
            counts["paused"] += 1
        elif s.status == MotorStatus.IN_PROGRESS:
            counts["in_progress"] += 1
        else:
            counts["not_started"] += 1

    return {"rounds": total_rounds, "total_actions": total_actions, **counts}


def cmd_status(args: argparse.Namespace) -> int:
    orc = Orchestrator()
    summary = orc.status()

    # Count totals
    from collections import Counter
    status_counts: Counter = Counter()
    for m in summary:
        status_counts[m["status"]] += 1

    print(f"\n{'ID':<12} {'Name':<45} {'G':<3} {'Status':<18} {'Stage':<22} {'Blk':<5} {'Psd'}")
    print("-" * 115)
    for m in summary:
        eligible_mark = "" if m["orchestrator_eligible"] else " [C]"
        blk = "Y" if m["blocked"] else "-"
        psd = "Y" if m["paused"] else "-"
        print(
            f"{m['motor_id']:<12} "
            f"{m['name'][:44]:<45} "
            f"{m['group']:<3} "
            f"{m['status']:<18} "
            f"{m['current_stage']:<22} "
            f"{blk:<5} "
            f"{psd}"
            f"{eligible_mark}"
        )

    print(f"\nSummary: {dict(status_counts)}")
    print()
    return 0


def cmd_approve(args: argparse.Namespace) -> int:
    orc = Orchestrator()
    result = orc.approve_manual_gate(args.motor, args.gate)
    _print_result(result)
    return 0 if result.action != "error" else 1


def cmd_correct(args: argparse.Namespace) -> int:
    try:
        target = Stage(args.to_stage)
    except ValueError:
        print(f"[ERROR] Invalid stage: {args.to_stage}")
        print(f"Valid stages: {[s.value for s in Stage if s != Stage.CLOSED]}")
        return 1

    orc = Orchestrator()
    result = orc.open_correction_for_motor(args.motor, target, args.reason)
    _print_result(result)
    return 0 if result.action != "error" else 1


def cmd_init(args: argparse.Namespace) -> int:
    """Initialize motor state from scratch (not_started). Useful for bootstrapping."""
    from motor_creator.config import GOVERNANZA
    from motor_creator.loader import initialize_motor_state, load_motor_dependencies
    from motor_creator.state_writer import write_motor_state

    motors = load_motor_dependencies()
    entry = motors.get(args.motor)
    if entry is None:
        print(f"[ERROR] Motor {args.motor} not found in motor_dependencies.json")
        return 1

    state = initialize_motor_state(entry)
    path = write_motor_state(entry, state, GOVERNANZA, dry_run=args.dry_run)
    print(f"[OK] Initialized motor_state.json for {entry.name} at {path}")
    return 0


# ─── helpers ──────────────────────────────────────────────────────────────────

def _print_result(result, dry_run: bool = False) -> None:
    prefix = "[DRY] " if dry_run else ""
    icon = {
        "advanced": "→",
        "closed":   "✓",
        "blocked":  "✗",
        "paused":   "⏸",
        "skipped":  "–",
        "correction": "↩",
        "approved": "✓",
        "error":    "!",
    }.get(result.action, "?")

    print(
        f"{prefix}[{icon}] {result.motor_id} | {result.action} | "
        f"{result.from_stage} → {result.to_stage}"
    )
    print(f"       {result.reason}")
    if result.artifacts_created:
        print(f"       artifacts: {result.artifacts_created}")


# ─── argument parser ──────────────────────────────────────────────────────────

def main() -> int:
    parser = argparse.ArgumentParser(
        description="Motor Creator — ZLab framework orchestrator",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    sub = parser.add_subparsers(dest="command", required=True)

    # ── run ──────────────────────────────────────────────────────────────────
    p_run = sub.add_parser("run", help="Process one or all motors")
    p_run.add_argument("--motor", help="Specific motor ID (e.g. motor_001)")
    p_run.add_argument("--all", action="store_true", help="One pass over all eligible motors")
    p_run.add_argument("--dry-run", action="store_true", help="Show decisions without writing")
    p_run.add_argument(
        "--watch", action="store_true",
        help="Loop continuously until all motors are done or blocked",
    )
    p_run.add_argument(
        "--auto-approve-gates", action="store_true", dest="auto_approve_gates",
        help="Automatically approve manual gate checks (fully autonomous mode)",
    )
    p_run.add_argument(
        "--max-rounds", type=int, default=500, dest="max_rounds",
        help="Safety limit on total processing iterations in --watch mode (default 500)",
    )
    p_run.add_argument(
        "--interval", type=float, default=0.0,
        help="Seconds to sleep between rounds in --watch mode (default 0)",
    )

    # ── status ────────────────────────────────────────────────────────────────
    sub.add_parser("status", help="Show current status of all motors")

    # ── approve ───────────────────────────────────────────────────────────────
    p_approve = sub.add_parser("approve", help="Approve a pending manual gate check")
    p_approve.add_argument("--motor", required=True)
    p_approve.add_argument("--gate", required=True, help="e.g. gate_1 or gate_6")

    # ── correct ───────────────────────────────────────────────────────────────
    p_correct = sub.add_parser("correct", help="Open a correction loop for a motor")
    p_correct.add_argument("--motor", required=True)
    p_correct.add_argument("--to-stage", required=True, dest="to_stage")
    p_correct.add_argument("--reason", required=True)

    # ── init ──────────────────────────────────────────────────────────────────
    p_init = sub.add_parser("init", help="Initialize motor_state.json for a motor")
    p_init.add_argument("--motor", required=True)
    p_init.add_argument("--dry-run", action="store_true")

    args = parser.parse_args()

    dispatch = {
        "run":     cmd_run,
        "status":  cmd_status,
        "approve": cmd_approve,
        "correct": cmd_correct,
        "init":    cmd_init,
    }
    return dispatch[args.command](args)


if __name__ == "__main__":
    sys.exit(main())
