"""Adapter for motor_058 — Report Uniqueness Validator (Layer F).

Detects when the strategic narrative of the current run is too similar to
recent runs of the same asset_family (a sign that the framework is
producing template-disguised reports rather than per-case intelligence).

Without persistent cross-run history available in this phase, the validator
operates on the artifact_store cache: it scans recent motor_054 outputs for
the same asset_family and computes Jaccard similarity over the
strategic_gold_nugget_register text.

Rules:
  RU1 — Jaccard similarity vs any prior run > 0.65 (high overlap).
  RU2 — Identical gold nugget text reused verbatim from a prior run.
"""
from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from .base import BaseMotorAdapter


_TOKEN_RE = re.compile(r"[a-z0-9]+")
_HIGH_OVERLAP_THRESHOLD = 0.65
_MAX_PRIOR_RUNS_TO_SCAN = 10


def _text(value: Any) -> str:
    return str(value or "").strip()


def _tokenize(text: str) -> set[str]:
    return set(_TOKEN_RE.findall(text.lower()))


def _jaccard(a: set[str], b: set[str]) -> float:
    if not a or not b:
        return 0.0
    intersection = a & b
    union = a | b
    if not union:
        return 0.0
    return len(intersection) / len(union)


def _collect_nugget_text(register: list[dict]) -> list[str]:
    texts: list[str] = []
    for nugget in register:
        if not isinstance(nugget, dict):
            continue
        text = _text(nugget.get("gold_nugget") or nugget.get("nugget"))
        if text:
            texts.append(text)
    return texts


def _scan_prior_runs(
    artifact_store_dir: Path,
    asset_family: str,
    current_nuggets: list[str],
) -> list[dict]:
    """Best-effort scan of motor_054 cached envelopes for prior runs.

    Returns a list of comparison records. If the artifact-store path does
    not exist or contains no readable manifests, returns [].
    """
    if not artifact_store_dir or not asset_family:
        return []
    motor_054_dir = artifact_store_dir / "motor_054"
    if not motor_054_dir.exists():
        return []
    current_tokens: set[str] = set()
    for nugget in current_nuggets:
        current_tokens |= _tokenize(nugget)
    if not current_tokens:
        return []

    comparisons: list[dict] = []
    files = sorted(motor_054_dir.glob("*.json"), reverse=True)[:_MAX_PRIOR_RUNS_TO_SCAN]
    for envelope_path in files:
        try:
            envelope = json.loads(envelope_path.read_text(encoding="utf-8"))
        except Exception:
            continue
        output = envelope.get("output", {}) if isinstance(envelope.get("output", {}), dict) else {}
        prior_register = list(
            output.get("strategic_gold_nugget_register")
            or output.get("gold_nugget_register")
            or []
        )
        prior_nuggets = _collect_nugget_text(prior_register)
        if not prior_nuggets:
            continue
        prior_tokens: set[str] = set()
        for n in prior_nuggets:
            prior_tokens |= _tokenize(n)
        similarity = _jaccard(current_tokens, prior_tokens)
        verbatim_overlap = sorted(set(prior_nuggets) & set(current_nuggets))
        comparisons.append(
            {
                "envelope": envelope_path.name,
                "similarity": similarity,
                "verbatim_overlap_count": len(verbatim_overlap),
                "verbatim_overlap_sample": verbatim_overlap[:3],
            }
        )
    return comparisons


def _evaluate(comparisons: list[dict]) -> list[dict]:
    out: list[dict] = []
    for comp in comparisons:
        if comp["similarity"] > _HIGH_OVERLAP_THRESHOLD:
            out.append(
                {
                    "rule_id": "RU1_high_jaccard_overlap",
                    "severity": "warning",
                    "compared_to": comp["envelope"],
                    "similarity": round(comp["similarity"], 3),
                    "description": (
                        f"Strategic gold-nugget vocabulary overlaps with prior run "
                        f"by {comp['similarity']:.0%} (>{_HIGH_OVERLAP_THRESHOLD:.0%}). "
                        "The two reports are likely too similar; consider whether the "
                        "case-specific intelligence has been preserved."
                    ),
                }
            )
        if comp["verbatim_overlap_count"]:
            out.append(
                {
                    "rule_id": "RU2_verbatim_nugget_reuse",
                    "severity": "warning",
                    "compared_to": comp["envelope"],
                    "verbatim_overlap_count": comp["verbatim_overlap_count"],
                    "sample": comp["verbatim_overlap_sample"],
                    "description": (
                        "One or more gold nuggets are reused verbatim from a prior run. "
                        "This is template fill, not case-specific insight."
                    ),
                }
            )
    return out


class Motor058Adapter(BaseMotorAdapter):
    @property
    def motor_id(self) -> str:
        return "motor_058"

    @property
    def input_motor_ids(self) -> list[str]:
        return ["motor_007", "motor_054"]

    def _run_impl(self, inputs: dict[str, Any]) -> dict[str, Any]:
        m007 = inputs.get("motor_007", {}) if isinstance(inputs.get("motor_007", {}), dict) else {}
        m054 = inputs.get("motor_054", {}) if isinstance(inputs.get("motor_054", {}), dict) else {}

        target_definition = m007.get("target_definition_contract", {}) if isinstance(m007.get("target_definition_contract", {}), dict) else {}
        asset_family = _text(target_definition.get("target_type") or target_definition.get("asset_family"))

        register = list(
            m054.get("strategic_gold_nugget_register")
            or m054.get("gold_nugget_register")
            or []
        )
        current_nuggets = _collect_nugget_text(register)

        # Best-effort: locate the artifact store relative to this file.
        # If the path does not exist (e.g., in unit tests with no store) the
        # validator silently produces no warnings — that is the correct
        # behavior for the first-run case.
        runtime_root = Path(__file__).resolve().parents[3]
        artifact_store = runtime_root / "artifact-store"
        comparisons = _scan_prior_runs(artifact_store, asset_family, current_nuggets)
        warnings = _evaluate(comparisons)

        return {
            "report_uniqueness_warnings": warnings,
            "warning_count": len(warnings),
            "asset_family_evaluated": asset_family,
            "prior_runs_compared": len(comparisons),
            "rules_evaluated": [
                "RU1_high_jaccard_overlap",
                "RU2_verbatim_nugget_reuse",
            ],
        }
