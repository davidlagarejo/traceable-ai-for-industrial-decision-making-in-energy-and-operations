#!/usr/bin/env python3
"""Manual knowledge extraction CLI (V4 Phase 1).

When you have an authoritative source (IIAR Bulletin, ASHRAE handbook,
DOE Better Plants case study, etc.) and you've manually authored a
KnowledgeObject draft from it, this CLI:

  1. Validates the draft against the V4 P0 schema
  2. Stamps it with provenance (source_id, extraction_path=manual)
  3. Lands it in knowledge_pending/<kind>/
  4. Surfaces it in the dashboard /knowledge page for human approval

This is the V4 P1 path for landing real knowledge while the LLM
extractor stays a stub. When V4 P2 wires real PDF + LLM extraction,
the same proposal endpoint receives the output — no architecture
change downstream.

Usage:
  python3 scripts/extract_knowledge.py \\
    --source-id iiar_bulletin_109 \\
    --topic refrigeration \\
    --kind pattern \\
    path/to/knowledge_draft.json

  cat draft.json | python3 scripts/extract_knowledge.py \\
    --source-id ashrae_handbook_refrigeration --topic refrigeration --kind pattern

Exit codes:
  0  proposal accepted (now in knowledge_pending/<kind>/)
  2  invalid input (bad JSON, validation failure, etc.)
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
    propose_knowledge_from_manual_text,
)


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Manual knowledge extraction. Validates a hand-authored "
            "knowledge draft against the V4 P0 schema, stamps provenance, "
            "and lands the proposal in knowledge_pending/. Approve in the "
            "dashboard at http://localhost:7474/knowledge."
        )
    )
    parser.add_argument(
        "input",
        nargs="?",
        type=Path,
        help="Path to knowledge draft JSON. Omit to read from stdin.",
    )
    parser.add_argument(
        "--source-id",
        required=True,
        help="Catalog source_id (e.g., iiar_bulletin_109). Must be in industrial_source_catalog.json.",
    )
    parser.add_argument(
        "--topic",
        required=True,
        help="Industrial topic (e.g., refrigeration, thermal_process, compressed_air).",
    )
    parser.add_argument(
        "--kind",
        required=True,
        choices=KNOWLEDGE_KINDS,
        help=f"knowledge_kind. Valid: {', '.join(KNOWLEDGE_KINDS)}",
    )
    parser.add_argument(
        "--proposed-by",
        default="manual_extraction",
        help="Identifier for who proposed (default: 'manual_extraction').",
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

    # Ensure the payload's knowledge_kind matches the CLI flag (or set it).
    payload["knowledge_kind"] = args.kind

    try:
        proposed = propose_knowledge_from_manual_text(
            source_id=args.source_id,
            topic=args.topic,
            target_kind=args.kind,
            knowledge_payload=payload,
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
        f"extracted (manual): id={proposed.get('id','?')} "
        f"kind={args.kind} source={args.source_id} topic={args.topic} "
        f"by={proposed.get('__proposed_by__','?')} at={proposed.get('__proposed_at__','?')}"
    )
    print("Review and approve at: http://localhost:7474/revisar")
    return 0


if __name__ == "__main__":
    sys.exit(main())
