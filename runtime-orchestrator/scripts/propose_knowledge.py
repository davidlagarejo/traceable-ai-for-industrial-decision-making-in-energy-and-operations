#!/usr/bin/env python3
"""Canonical entry point for proposing knowledge to the framework (V4 P0 item 2).

ANY automated flow (motor_028 discovery, future LLM extractor, manual
knowledge import) that wants to land a pattern / combination / archetype
/ process_logic block in the framework MUST go through this CLI (or
call industrial_research_engine.propose_knowledge() directly).

Writing directly to knowledge_memory/approved/ bypasses human approval
and is forbidden — the dashboard is the only entry point to approved
memory.

Usage:
  python3 scripts/propose_knowledge.py path/to/knowledge.json
  python3 scripts/propose_knowledge.py path/to/knowledge.json --kind pattern --proposed-by claude
  cat knowledge.json | python3 scripts/propose_knowledge.py --kind combination

Exit codes:
  0  proposal accepted (now in knowledge_pending/<kind>/)
  2  invalid input (bad JSON, schema failure, etc.)
  3  conflict (knowledge_id already pending)
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(_REPO_ROOT / "src"))

from runtime_orchestrator.industrial_research_engine import (  # noqa: E402
    KNOWLEDGE_KINDS,
    KnowledgeValidationError,
    propose_knowledge,
)


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Propose a knowledge entry → knowledge_pending/<kind>/. "
            "Human approval required via dashboard before it reaches "
            "approved memory."
        )
    )
    parser.add_argument(
        "input",
        nargs="?",
        type=Path,
        help="Path to knowledge JSON. Omit to read from stdin.",
    )
    parser.add_argument(
        "--kind",
        choices=KNOWLEDGE_KINDS,
        help=(
            "Override destination kind. Defaults to payload.knowledge_kind. "
            f"Valid kinds: {', '.join(KNOWLEDGE_KINDS)}"
        ),
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
        result = propose_knowledge(
            payload,
            kind=args.kind,
            proposed_by=args.proposed_by,
        )
    except KnowledgeValidationError as exc:
        print(f"validation failed: {exc}", file=sys.stderr)
        return 2
    except FileExistsError as exc:
        print(f"conflict: {exc}", file=sys.stderr)
        return 3
    except ValueError as exc:
        print(f"invalid: {exc}", file=sys.stderr)
        return 2
    print(
        f"proposed: id={result['id']} kind={result['__pending_kind__']} "
        f"by={result['__proposed_by__']} at={result['__proposed_at__']}"
    )
    print("Review and approve at: http://localhost:7474/knowledge")
    return 0


if __name__ == "__main__":
    sys.exit(main())
