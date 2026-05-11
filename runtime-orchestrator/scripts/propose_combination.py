#!/usr/bin/env python3
"""Canonical entry point for proposing a new combination (V2-CRITICAL Item 2).

Any AI / automated flow that wants to register a new combination MUST go
through this script (or call combination_approval.propose() directly). It
routes the proposal to `combinations_pending/` for human review in the
dashboard. Writing directly to `combinations/` bypasses the rule that
combinations require human approval.

Usage:
  python3 scripts/propose_combination.py path/to/combination.json
  python3 scripts/propose_combination.py path/to/combination.json --proposed-by claude
  cat combo.json | python3 scripts/propose_combination.py --proposed-by ai

The JSON payload must include an `id` field (combination_id). Other
fields (name, version, pattern_ids, trigger_logic, anti_triggers,
combined_hypothesis, strategic_risk, minimum_evidence, financial_exposure,
tad_action, prohibited_claims, ...) are passed through unchanged.

Exit codes:
  0  proposal accepted (now in combinations_pending/)
  2  invalid input (bad JSON, missing id, etc.)
  3  conflict (combination_id already exists in pending/approved/rejected)
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

# Allow running as a standalone script.
_REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(_REPO_ROOT / "src"))

from runtime_orchestrator import combination_approval as ca  # noqa: E402


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Propose a combination → combinations_pending/ (human approval required)"
    )
    parser.add_argument(
        "input",
        nargs="?",
        type=Path,
        help="Path to combination JSON. Omit to read from stdin.",
    )
    parser.add_argument(
        "--proposed-by",
        default="ai",
        help="Identifier for who is proposing (default: 'ai')",
    )
    return parser.parse_args()


def _load_payload(input_path: Path | None) -> dict:
    if input_path is None:
        raw = sys.stdin.read()
    else:
        if not input_path.exists():
            print(f"error: input file not found: {input_path}", file=sys.stderr)
            sys.exit(2)
        raw = input_path.read_text(encoding="utf-8")
    try:
        payload = json.loads(raw)
    except json.JSONDecodeError as exc:
        print(f"error: invalid JSON: {exc}", file=sys.stderr)
        sys.exit(2)
    if not isinstance(payload, dict):
        print("error: payload must be a JSON object", file=sys.stderr)
        sys.exit(2)
    return payload


def main() -> int:
    args = _parse_args()
    payload = _load_payload(args.input)
    try:
        result = ca.propose(payload, proposed_by=args.proposed_by)
    except FileExistsError as exc:
        print(f"conflict: {exc}", file=sys.stderr)
        return 3
    except ValueError as exc:
        print(f"invalid: {exc}", file=sys.stderr)
        return 2
    print(
        f"proposed: {result['combination_id']} → combinations_pending/ "
        f"(by {result['proposed_by']}, at {result['proposed_at']})"
    )
    print("Review and approve at: http://localhost:7474/combinations")
    return 0


if __name__ == "__main__":
    sys.exit(main())
