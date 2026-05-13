"""Adapter for motor_057 — Gold Nugget Quality Validator (Layer F).

Detects archetype-replay nuggets — gold nuggets that read identical to the
generic archetype prior because they contain none of the asset-specific
tokens that would tie them to the case under analysis.

Rules:
  GN1 — Nugget contains NO asset-family-specific token.
        (e.g. a warehouse case nugget that mentions neither dock, charging,
        refrigeration, throughput, etc.)
  GN2 — Nugget shorter than 40 characters (too thin to carry an insight).
  GN3 — Multiple nuggets share the same first 30 characters (template-fill).
"""
from __future__ import annotations

from collections import defaultdict
from typing import Any

from ..pattern_library import asset_family_concept_markers
from .base import BaseMotorAdapter
from ..validator_severity_policy import effective_severity


# Conservative fallback used only if the Pattern Library JSON file for an
# asset_family is missing. The authoritative source is
# governanza/asset-operational-logic-engine_050/patterns/<asset_family>.json
# (loaded via runtime_orchestrator.pattern_library).
_ASSET_FAMILY_TOKENS_FALLBACK: dict[str, set[str]] = {
    "warehouse_distribution": {"dock", "charging", "refrigeration", "throughput"},
    "manufacturing_facility": {"process heat", "compressed air", "downtime", "throughput"},
    "commercial_building": {"tenant", "bms", "after-hours", "hvac"},
    "datacenter": {"pue", "it load", "redundancy", "cooling"},
    "logistics_terminal": {"continuity", "dispatch", "reefer"},
}


def _resolve_family_tokens(asset_family: str) -> set[str]:
    """Prefer the JSON Pattern Library; fall back to the hardcoded seed."""
    library_tokens = asset_family_concept_markers(asset_family)
    if library_tokens:
        return library_tokens
    return _ASSET_FAMILY_TOKENS_FALLBACK.get(asset_family, set())

_GENERIC_FALLBACK_TOKENS = {"asset", "site", "facility"}

_MIN_NUGGET_LENGTH = 40
_TEMPLATE_PREFIX_LENGTH = 30


def _text(value: Any) -> str:
    return str(value or "").strip()


def _normalize(text: str) -> str:
    return " ".join(text.lower().split())


def _detect_archetype_replay(
    nuggets: list[dict],
    asset_family: str,
) -> list[dict]:
    family_tokens = _resolve_family_tokens(asset_family)
    if not family_tokens:
        return []
    out: list[dict] = []
    for nugget in nuggets:
        if not isinstance(nugget, dict):
            continue
        text = _normalize(_text(nugget.get("gold_nugget") or nugget.get("nugget")))
        if not text:
            continue
        if any(token in text for token in family_tokens):
            continue
        # No family token AND no generic asset reference => almost certainly
        # archetype-replay
        if any(token in text for token in _GENERIC_FALLBACK_TOKENS):
            continue
        out.append(
            {
                "rule_id": "GN1_archetype_replay",
                "severity": "warning",
                "nugget_id": _text(nugget.get("nugget_id")),
                "asset_family": asset_family,
                "description": (
                    "Gold nugget contains no asset-family-specific token. The reader "
                    "cannot tell whether this insight belongs to the case under analysis "
                    "or to a generic archetype prior."
                ),
            }
        )
    return out


def _detect_thin_nuggets(nuggets: list[dict]) -> list[dict]:
    out: list[dict] = []
    for nugget in nuggets:
        if not isinstance(nugget, dict):
            continue
        text = _text(nugget.get("gold_nugget") or nugget.get("nugget"))
        if not text:
            continue
        if len(text) >= _MIN_NUGGET_LENGTH:
            continue
        out.append(
            {
                "rule_id": "GN2_thin_nugget",
                "severity": "warning",
                "nugget_id": _text(nugget.get("nugget_id")),
                "length": len(text),
                "description": (
                    f"Gold nugget is shorter than {_MIN_NUGGET_LENGTH} characters; "
                    "likely too thin to carry a structural insight."
                ),
            }
        )
    return out


def _detect_template_fill(nuggets: list[dict]) -> list[dict]:
    by_prefix: dict[str, list[str]] = defaultdict(list)
    for nugget in nuggets:
        if not isinstance(nugget, dict):
            continue
        text = _normalize(_text(nugget.get("gold_nugget") or nugget.get("nugget")))
        if len(text) < _TEMPLATE_PREFIX_LENGTH:
            continue
        prefix = text[:_TEMPLATE_PREFIX_LENGTH]
        by_prefix[prefix].append(_text(nugget.get("nugget_id")))
    out: list[dict] = []
    for prefix, ids in by_prefix.items():
        if len(ids) > 1:
            out.append(
                {
                    "rule_id": "GN3_template_fill",
                    "severity": "warning",
                    "shared_prefix": prefix,
                    "nugget_ids": ids,
                    "description": (
                        "Multiple nuggets share the same opening phrase. The composer "
                        "is likely template-filling rather than producing distinct insights."
                    ),
                }
            )
    return out


# V3 G16: nugget count enforcement (5-12 per RECOVERY_V3_BACKLOG).
# Configurable via __pipeline__.nugget_count_thresholds.
_DEFAULT_NUGGET_COUNT_MIN = 5
_DEFAULT_NUGGET_COUNT_MAX = 12


def _detect_nugget_count_out_of_range(
    nuggets: list[dict],
    min_count: int,
    max_count: int,
) -> list[dict]:
    """GN4: emit critical when the rendered report has too few or too many
    gold nuggets. Per V3 prompt §6.B: 5-10 unique nuggets is the target;
    we use 5-12 to allow 2-nugget headroom for diverse cases."""
    n = len(nuggets)
    if min_count <= n <= max_count:
        return []
    if n < min_count:
        description = (
            f"Report has {n} gold nuggets — below the minimum of {min_count}. "
            "Reports with fewer nuggets read as thin and miss decision-grade signal. "
            "Either generate more nuggets or surface why this case cannot reach the minimum."
        )
    else:
        description = (
            f"Report has {n} gold nuggets — above the maximum of {max_count}. "
            "Reports with too many nuggets read as noisy and dilute decision-grade signal. "
            "Curate the strongest nuggets and drop the rest."
        )
    return [
        {
            "rule_id": "GN4_nugget_count_out_of_range",
            "severity": "critical",
            "nugget_count": n,
            "min_required": min_count,
            "max_allowed": max_count,
            "description": description,
        }
    ]


class Motor057Adapter(BaseMotorAdapter):
    @property
    def motor_id(self) -> str:
        return "motor_057"

    @property
    def input_motor_ids(self) -> list[str]:
        return ["motor_007", "motor_054"]

    def _run_impl(self, inputs: dict[str, Any]) -> dict[str, Any]:
        m007 = inputs.get("motor_007", {}) if isinstance(inputs.get("motor_007", {}), dict) else {}
        m054 = inputs.get("motor_054", {}) if isinstance(inputs.get("motor_054", {}), dict) else {}

        target_definition = m007.get("target_definition_contract", {}) if isinstance(m007.get("target_definition_contract", {}), dict) else {}
        asset_family = _text(target_definition.get("target_type") or target_definition.get("asset_family"))

        nuggets = list(
            m054.get("strategic_gold_nugget_register")
            or m054.get("gold_nugget_register")
            or []
        )

        # V3 G16: configurable thresholds
        pipeline_inputs = inputs.get("__pipeline__", {}) if isinstance(inputs.get("__pipeline__", {}), dict) else {}
        thresholds = pipeline_inputs.get("nugget_count_thresholds", {}) if isinstance(pipeline_inputs.get("nugget_count_thresholds", {}), dict) else {}
        min_count = int(thresholds.get("min", _DEFAULT_NUGGET_COUNT_MIN) or _DEFAULT_NUGGET_COUNT_MIN)
        max_count = int(thresholds.get("max", _DEFAULT_NUGGET_COUNT_MAX) or _DEFAULT_NUGGET_COUNT_MAX)

        warnings: list[dict] = []
        warnings.extend(_detect_archetype_replay(nuggets, asset_family))
        warnings.extend(_detect_thin_nuggets(nuggets))
        warnings.extend(_detect_template_fill(nuggets))
        warnings.extend(_detect_nugget_count_out_of_range(nuggets, min_count, max_count))

        # V6 P4.6: apply validator_severity_policy gate (soft-mode no-op).
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
            "gold_nugget_quality_warnings": warnings,
            "warning_count": len(warnings),
            "blocking_violations": blocking_count,
            "warning_violations": warning_count_pure,
            "asset_family_evaluated": asset_family,
            "nugget_count_evaluated": len(nuggets),
            "nugget_count_min": min_count,
            "nugget_count_max": max_count,
            "rules_evaluated": [
                "GN1_archetype_replay",
                "GN2_thin_nugget",
                "GN3_template_fill",
                "GN4_nugget_count_out_of_range",
            ],
        }
