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

from .base import BaseMotorAdapter


# Asset-family-specific tokens. Conservative seed set; the proper Pattern
# Library (RECOVERY_BACKLOG.md R-30..R-37) will replace this with versioned
# JSON files per asset family.
_ASSET_FAMILY_TOKENS: dict[str, set[str]] = {
    "warehouse_distribution": {
        "dock", "charging", "refrigeration", "throughput", "logistics",
        "service-level", "movement", "fleet", "cold-chain", "shipment",
    },
    "manufacturing_facility": {
        "process heat", "process_heat", "compressed air", "compressed_air",
        "downtime", "throughput", "uptime", "power factor", "power_factor",
        "harmonics", "reactive", "shift", "production",
    },
    "commercial_building": {
        "tenant", "bms", "occupancy", "after-hours", "after_hours",
        "ll97", "hvac", "reheat", "lease", "common area",
    },
    "datacenter": {
        "pue", "it load", "redundancy", "cooling", "n+1", "tier",
    },
    "logistics_terminal": {
        "continuity", "dispatch", "fleet", "charging", "refrigeration",
    },
}

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
    family_tokens = _ASSET_FAMILY_TOKENS.get(asset_family, set())
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

        warnings: list[dict] = []
        warnings.extend(_detect_archetype_replay(nuggets, asset_family))
        warnings.extend(_detect_thin_nuggets(nuggets))
        warnings.extend(_detect_template_fill(nuggets))

        return {
            "gold_nugget_quality_warnings": warnings,
            "warning_count": len(warnings),
            "asset_family_evaluated": asset_family,
            "nugget_count_evaluated": len(nuggets),
            "rules_evaluated": [
                "GN1_archetype_replay",
                "GN2_thin_nugget",
                "GN3_template_fill",
            ],
        }
