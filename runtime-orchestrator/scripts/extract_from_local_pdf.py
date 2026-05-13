#!/usr/bin/env python3
"""V5 P3 — deterministic local-PDF extraction CLI.

Replaces the V4 P2/P3 LLM-extractor CLI (removed in V5 P0). This CLI is
100% deterministic:

  pdfplumber → keyword rules (zlab_skill._AUTO_PATTERN_RULES)
  matched patterns → bridge → propose_knowledge → knowledge_pending/

NO LLM is involved. Phase 0 anchor: "el LLM no es soberano".

Approval still happens via the dashboard `/revisar` page; this CLI only
LANDS candidates as pending.

Usage:
  python3 scripts/extract_from_local_pdf.py \\
    --pdf-path "/path/to/IIAR-Bulletin-109.pdf" \\
    --source-id iiar_bulletin_109 \\
    [--id-suffix v5p3_iiar109]   # appended to each matched pattern id
                                  # to avoid collision with existing
                                  # registry entries

  python3 scripts/extract_from_local_pdf.py --batch-dir <dir> \\
    [--manifest <file.json>]      # mapping pdf_filename → source_id

Exit codes:
  0 — at least one candidate landed (or zero matches, no error)
  2 — invalid input
  3 — all candidates conflicted with pre-existing pending
  4 — pdfplumber missing
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(_REPO_ROOT / "src"))

from runtime_orchestrator.industrial_research_engine import (  # noqa: E402
    KnowledgeValidationError,
    load_pattern_spec,
    propose_extracted_pattern,
)
from runtime_orchestrator.zlab_skill.autodraft_rule_derivation import (  # noqa: E402
    derive_autodraft_rule_from_pattern_spec,
)
from runtime_orchestrator.zlab_skill.local_pdf_autodraft import (  # noqa: E402
    _AUTO_PATTERN_RULES,
    _evaluate_pattern_rule,
    _extract_excerpt,
    extract_bounded_pdf_text,
    pdfplumber,
)


_REGISTRY_PATTERNS_DIR = (
    _REPO_ROOT / "zlab_skill" / "registry" / "patterns"
)


def _all_registry_pattern_ids() -> list[str]:
    """Return every pattern_id present in the registry (filesystem)."""
    if not _REGISTRY_PATTERNS_DIR.exists():
        return []
    ids = set()
    for f in _REGISTRY_PATTERNS_DIR.glob("*.json"):
        # Filename format: <id>.v<N>.json
        # Use the spec's own id to be robust
        try:
            import json as _json
            d = _json.loads(f.read_text(encoding="utf-8"))
            if d.get("id"):
                ids.add(d["id"])
        except Exception:
            pass
    return sorted(ids)


def _resolve_rule_for_pattern(pattern_id: str) -> tuple[dict | None, dict | None, str]:
    """Return (rule, pattern_spec, source) for a pattern_id.

    Source is one of:
      'hand_authored' — rule from _AUTO_PATTERN_RULES (V5 P3 vocabulary)
      'derived'       — rule auto-derived from pattern_spec (V5 P9)
      'none'          — no rule and derivation failed
    """
    spec = load_pattern_spec(pattern_id)
    rule = _AUTO_PATTERN_RULES.get(pattern_id)
    if rule is not None:
        return rule, spec, "hand_authored"
    if spec is None:
        return None, None, "none"
    derived = derive_autodraft_rule_from_pattern_spec(spec)
    if derived is None:
        return None, spec, "none"
    return derived, spec, "derived"


def _process_pdf(
    *, pdf_path: Path, source_id: str, id_suffix: str = "", verbose: bool = True
) -> dict:
    """Process one PDF and return a manifest of matched/landed/skipped patterns."""
    result: dict = {
        "pdf": str(pdf_path),
        "source_id": source_id,
        "matched": [],
        "landed": [],
        "conflicts": [],
        "errors": [],
        "pdf_text_status": "",
    }
    if not pdf_path.exists():
        result["errors"].append(f"PDF not found: {pdf_path}")
        return result

    if verbose:
        print(f"[+] {pdf_path.name}  (source_id={source_id})")

    text_result = extract_bounded_pdf_text(
        artifact_path=str(pdf_path), max_pages=20, max_chars=60000
    )
    result["pdf_text_status"] = text_result["status"]
    if text_result["status"] != "success":
        result["errors"].append(f"pdfplumber: {text_result['status']}")
        if verbose:
            print(f"    ! pdfplumber failed: {text_result['status']}")
        return result
    search_text = text_result["visible_text"].lower()

    # V5 P9: iterate ALL registry pattern_ids (not just _AUTO_PATTERN_RULES).
    # For each, use the hand-authored rule if present, else derive one
    # from the pattern_spec's own trigger_conditions.
    all_ids = _all_registry_pattern_ids()
    for pattern_id in all_ids:
        rule, spec, rule_source = _resolve_rule_for_pattern(pattern_id)
        if rule is None or spec is None:
            continue
        evaluation = _evaluate_pattern_rule(search_text, rule)
        if not evaluation:
            continue
        matched_terms = evaluation["matched_terms"]
        excerpt = _extract_excerpt(search_text, matched_terms)
        result["matched"].append({
            "pattern_id": pattern_id,
            "matched_terms": matched_terms,
            "score": evaluation["score"],
            "rule_source": rule_source,
        })

        bridged_id = (
            f"{pattern_id}__{id_suffix}" if id_suffix else f"{pattern_id}__from_{source_id}"
        )

        try:
            proposed = propose_extracted_pattern(
                pattern_spec=spec,
                source_id=source_id,
                supporting_excerpt=excerpt,
                source_locator=f"local_pdf::{pdf_path.name}::{pattern_id}",
                matched_terms=matched_terms,
                pdf_path=str(pdf_path),
                override_id=bridged_id,
            )
            result["landed"].append(proposed["id"])
            if verbose:
                print(f"    ✓ landed: {proposed['id']}  (score={evaluation['score']})")
        except FileExistsError as exc:
            result["conflicts"].append(bridged_id)
            if verbose:
                print(f"    ~ conflict: {bridged_id}  ({exc})")
        except KnowledgeValidationError as exc:
            result["errors"].append(f"{bridged_id}: validation: {exc}")
            if verbose:
                print(f"    ! validation failed: {bridged_id}: {exc}")
        except Exception as exc:  # noqa: BLE001
            result["errors"].append(f"{bridged_id}: {type(exc).__name__}: {exc}")
            if verbose:
                print(f"    ! error: {bridged_id}: {type(exc).__name__}")

    return result


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Deterministic local-PDF extraction (V5 P3, no LLM)."
    )
    g = parser.add_mutually_exclusive_group(required=True)
    g.add_argument("--pdf-path", type=Path, help="single PDF to process")
    g.add_argument("--batch-dir", type=Path, help="directory of PDFs to batch-process")
    parser.add_argument("--source-id", help="catalog source_id (single-PDF mode)")
    parser.add_argument(
        "--manifest",
        type=Path,
        help="batch-mode JSON mapping pdf_basename → source_id",
    )
    parser.add_argument("--id-suffix", default="", help="suffix appended to bridged ids")
    parser.add_argument("--out", type=Path, help="manifest output file")
    args = parser.parse_args()

    if pdfplumber is None:
        print(
            "FATAL: pdfplumber not installed. Run: pip install pdfplumber",
            file=sys.stderr,
        )
        return 4

    manifests: list[dict] = []

    if args.pdf_path:
        if not args.source_id:
            print("error: --source-id required with --pdf-path", file=sys.stderr)
            return 2
        manifests.append(
            _process_pdf(
                pdf_path=args.pdf_path,
                source_id=args.source_id,
                id_suffix=args.id_suffix,
            )
        )
    else:
        if not args.batch_dir.exists() or not args.batch_dir.is_dir():
            print(f"error: not a directory: {args.batch_dir}", file=sys.stderr)
            return 2
        mapping: dict[str, str] = {}
        if args.manifest:
            mapping = json.loads(args.manifest.read_text(encoding="utf-8"))
        for pdf_path in sorted(args.batch_dir.rglob("*.pdf")):
            source_id = mapping.get(pdf_path.name) or args.source_id
            if not source_id:
                print(f"[!] skip {pdf_path.name}: no source_id mapping")
                continue
            manifests.append(
                _process_pdf(
                    pdf_path=pdf_path,
                    source_id=source_id,
                    id_suffix=args.id_suffix,
                )
            )

    total_matched = sum(len(m["matched"]) for m in manifests)
    total_landed = sum(len(m["landed"]) for m in manifests)
    total_conflicts = sum(len(m["conflicts"]) for m in manifests)
    total_errors = sum(len(m["errors"]) for m in manifests)
    print(
        f"\nSUMMARY: pdfs={len(manifests)}  matched={total_matched}  "
        f"landed={total_landed}  conflicts={total_conflicts}  errors={total_errors}"
    )
    print("Review at: http://localhost:7474/revisar")

    if args.out:
        args.out.write_text(
            json.dumps(manifests, indent=2, ensure_ascii=False), encoding="utf-8"
        )
        print(f"manifest → {args.out}")

    if total_landed == 0 and total_conflicts > 0 and total_matched > 0:
        return 3
    return 0


if __name__ == "__main__":
    sys.exit(main())
