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
from ..validator_severity_policy import effective_severity


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


# V3 G15: expand reuse detection to 5 dimensions.
# - RU1 jaccard token overlap (nugget vocabulary)
# - RU2 verbatim nugget reuse
# - RU3 TAD action set reuse
# - RU4 chart asset_id / title set reuse
# - RU5 evidence pack (minimum_evidence_to_activate strings) set reuse


def _set_overlap_ratio(current: set[str], prior: set[str]) -> float:
    if not prior:
        return 0.0
    return len(current & prior) / len(prior)


_HIGH_SET_OVERLAP_THRESHOLD = 0.90


def _collect_tad_action_ids(register: list[dict]) -> set[str]:
    out: set[str] = set()
    for row in register or []:
        if not isinstance(row, dict):
            continue
        action = _text(row.get("action")) or _text(row.get("tad_action"))
        if action:
            out.add(action.lower())
    return out


def _collect_chart_ids(chart_assets: list[dict]) -> set[str]:
    out: set[str] = set()
    for asset in chart_assets or []:
        if not isinstance(asset, dict):
            continue
        cid = _text(asset.get("chart_id")) or _text(asset.get("asset_id")) or _text(asset.get("title"))
        if cid:
            out.add(cid.lower())
    return out


def _collect_evidence_pack(register: list[dict]) -> set[str]:
    """Approximate evidence-pack fingerprint: union of pattern minimum_evidence
    plus combination minimum_evidence strings."""
    out: set[str] = set()
    for row in register or []:
        if not isinstance(row, dict):
            continue
        for key in ("minimum_evidence", "minimum_evidence_to_activate"):
            for item in row.get(key, []) or []:
                item_text = _text(item)
                if item_text:
                    out.add(item_text.lower())
    return out


def _scan_prior_runs(
    artifact_store_dir: Path,
    asset_family: str,
    current_nuggets: list[str],
    *,
    current_tad_ids: set[str] | None = None,
    current_chart_ids: set[str] | None = None,
    current_evidence_pack: set[str] | None = None,
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

    current_tad_ids = current_tad_ids or set()
    current_chart_ids = current_chart_ids or set()
    current_evidence_pack = current_evidence_pack or set()

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
        prior_tad_ids = _collect_tad_action_ids(
            output.get("expanded_structural_tad_action_register", [])
            or output.get("tad_action_register", [])
            or []
        )
        prior_chart_ids = _collect_chart_ids(output.get("chart_assets", []) or [])
        prior_evidence_pack = _collect_evidence_pack(prior_register)

        if not (prior_nuggets or prior_tad_ids or prior_chart_ids or prior_evidence_pack):
            continue

        prior_tokens: set[str] = set()
        for n in prior_nuggets:
            prior_tokens |= _tokenize(n)
        similarity = _jaccard(current_tokens, prior_tokens) if prior_nuggets else 0.0
        verbatim_overlap = sorted(set(prior_nuggets) & set(current_nuggets)) if prior_nuggets else []
        tad_overlap_ratio = _set_overlap_ratio(current_tad_ids, prior_tad_ids)
        chart_overlap_ratio = _set_overlap_ratio(current_chart_ids, prior_chart_ids)
        evidence_overlap_ratio = _set_overlap_ratio(current_evidence_pack, prior_evidence_pack)

        comparisons.append(
            {
                "envelope": envelope_path.name,
                "similarity": similarity,
                "verbatim_overlap_count": len(verbatim_overlap),
                "verbatim_overlap_sample": verbatim_overlap[:3],
                "tad_overlap_ratio": tad_overlap_ratio,
                "chart_overlap_ratio": chart_overlap_ratio,
                "evidence_overlap_ratio": evidence_overlap_ratio,
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
        # V3 G15: RU3 TAD action set reuse
        if comp.get("tad_overlap_ratio", 0.0) > _HIGH_SET_OVERLAP_THRESHOLD:
            out.append(
                {
                    "rule_id": "RU3_tad_action_set_reuse",
                    "severity": "warning",
                    "compared_to": comp["envelope"],
                    "tad_overlap_ratio": round(comp["tad_overlap_ratio"], 3),
                    "description": (
                        f"TAD action set overlaps with prior run by "
                        f"{comp['tad_overlap_ratio']:.0%} "
                        f"(>{_HIGH_SET_OVERLAP_THRESHOLD:.0%}). The strategic action "
                        "plan is essentially the same as a prior case — case-specific "
                        "TAD logic may have been lost."
                    ),
                }
            )
        # V3 G15: RU4 chart set reuse
        if comp.get("chart_overlap_ratio", 0.0) > _HIGH_SET_OVERLAP_THRESHOLD:
            out.append(
                {
                    "rule_id": "RU4_chart_set_reuse",
                    "severity": "warning",
                    "compared_to": comp["envelope"],
                    "chart_overlap_ratio": round(comp["chart_overlap_ratio"], 3),
                    "description": (
                        f"Chart set overlaps with prior run by "
                        f"{comp['chart_overlap_ratio']:.0%}. The report's visual "
                        "structure replays a prior case; case-specific charts may be "
                        "missing."
                    ),
                }
            )
        # V3 G15: RU5 evidence pack set reuse
        if comp.get("evidence_overlap_ratio", 0.0) > _HIGH_SET_OVERLAP_THRESHOLD:
            out.append(
                {
                    "rule_id": "RU5_evidence_pack_set_reuse",
                    "severity": "warning",
                    "compared_to": comp["envelope"],
                    "evidence_overlap_ratio": round(comp["evidence_overlap_ratio"], 3),
                    "description": (
                        f"Evidence pack overlaps with prior run by "
                        f"{comp['evidence_overlap_ratio']:.0%}. The minimum evidence "
                        "demanded looks identical — case-specific evidence requirements "
                        "have not been derived."
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
        # V3 G15: also read motor_018 (chart assets) and motor_033 (TAD actions)
        return ["motor_007", "motor_018", "motor_033", "motor_054"]

    def _run_impl(self, inputs: dict[str, Any]) -> dict[str, Any]:
        m007 = inputs.get("motor_007", {}) if isinstance(inputs.get("motor_007", {}), dict) else {}
        m018 = inputs.get("motor_018", {}) if isinstance(inputs.get("motor_018", {}), dict) else {}
        m033 = inputs.get("motor_033", {}) if isinstance(inputs.get("motor_033", {}), dict) else {}
        m054 = inputs.get("motor_054", {}) if isinstance(inputs.get("motor_054", {}), dict) else {}

        target_definition = m007.get("target_definition_contract", {}) if isinstance(m007.get("target_definition_contract", {}), dict) else {}
        asset_family = _text(target_definition.get("target_type") or target_definition.get("asset_family"))

        register = list(
            m054.get("strategic_gold_nugget_register")
            or m054.get("gold_nugget_register")
            or []
        )
        current_nuggets = _collect_nugget_text(register)
        # V3 G15: gather TAD ids, chart ids, evidence pack for set overlap
        current_tad_ids = _collect_tad_action_ids(
            m033.get("expanded_structural_tad_action_register", [])
            or m033.get("tad_action_register", [])
            or []
        )
        current_chart_ids = _collect_chart_ids(m018.get("chart_assets", []) or [])
        current_evidence_pack = _collect_evidence_pack(register)

        runtime_root = Path(__file__).resolve().parents[3]
        artifact_store = runtime_root / "artifact-store"
        comparisons = _scan_prior_runs(
            artifact_store,
            asset_family,
            current_nuggets,
            current_tad_ids=current_tad_ids,
            current_chart_ids=current_chart_ids,
            current_evidence_pack=current_evidence_pack,
        )
        warnings = _evaluate(comparisons)

        # V6 P4.7: apply validator_severity_policy gate (soft-mode no-op).
        pipeline_inputs = inputs.get("__pipeline__", {}) if isinstance(inputs.get("__pipeline__", {}), dict) else {}
        for w in warnings:
            rid = str(w.get("rule_id", ""))
            sev = str(w.get("severity", "warning"))
            w["severity"] = effective_severity(
                self.motor_id, rid, sev, pipeline_inputs=pipeline_inputs
            )
        blocking_count = sum(1 for w in warnings if w.get("severity") == "blocking")
        warning_count_pure = sum(1 for w in warnings if w.get("severity") == "warning")

        return {
            "report_uniqueness_warnings": warnings,
            "warning_count": len(warnings),
            "blocking_violations": blocking_count,
            "warning_violations": warning_count_pure,
            "asset_family_evaluated": asset_family,
            "prior_runs_compared": len(comparisons),
            "current_tad_action_count": len(current_tad_ids),
            "current_chart_count": len(current_chart_ids),
            "current_evidence_pack_size": len(current_evidence_pack),
            "rules_evaluated": [
                "RU1_high_jaccard_overlap",
                "RU2_verbatim_nugget_reuse",
                "RU3_tad_action_set_reuse",
                "RU4_chart_set_reuse",
                "RU5_evidence_pack_set_reuse",
            ],
        }
