"""Adapter for motor_061 — Asset Family Isolation Validator (Layer F).

Detects asset-family contamination: patterns activated for the case that do
NOT belong to the asset family being analyzed. Blocks the report at validator
level when contamination is critical.

This implements Validator A of the new prompt (RECOVERY_2026-05-09):

  > A. ASSET FAMILY CONTAMINATION VALIDATOR
  > Bloquea:
  >   - office charts en warehouse;
  >   - resin logic en cold-chain;
  >   - refrigeration logic en office;
  >   - fulfillment logic en manufacturing.

The validator reads:
  - motor_007.target_definition_contract → asset_family
  - motor_054.skill_combination_activation_register → activated combinations
  - motor_054.strategic_gold_nugget_register → emitted nuggets

For each activated combination it checks anti_triggers against the asset
family. If a combination tagged with manufacturing-only patterns activates
in a warehouse case, that is contamination.

Today the validator emits warnings (severity=critical) and a
`contamination_detected` flag. A future commit will gate the LaTeX render
on this flag, similar to motor_036's existing can_render_pdf gate.
"""
from __future__ import annotations

from typing import Any

from .base import BaseMotorAdapter


# Per asset_family, the set of pattern_ids that signal CONTAMINATION when
# they activate in a case of THIS family. Conservative seed; can be moved
# to JSON in a follow-up commit.
_CROSS_FAMILY_CONTAMINATION: dict[str, set[str]] = {
    "warehouse_distribution": {
        "process_load_vs_waste",
        "boiler_degradation_plausibility",
        "chiller_degradation_plausibility",
        "compressed_air_leak_plausibility",
        "steam_trap_failure_plausibility",
        "tenant_operator_boundary_unresolved",
    },
    "cold_chain_facility": {
        "process_load_vs_waste",
        "boiler_degradation_plausibility",
        "compressed_air_leak_plausibility",
        "steam_trap_failure_plausibility",
        "tenant_operator_boundary_unresolved",
    },
    "manufacturing_facility": {
        "warehouse_mhe_charging_demand_peak",
        "warehouse_dock_infiltration_loss",
        "cold_chain_status_unknown",
        "tenant_operator_boundary_unresolved",
        "high_bay_lighting_waste",
        "hvac_schedule_drift",
    },
    "commercial_building": {
        "warehouse_mhe_charging_demand_peak",
        "warehouse_dock_infiltration_loss",
        "cold_chain_status_unknown",
        "process_load_vs_waste",
        "boiler_degradation_plausibility",
        "compressed_air_leak_plausibility",
        "steam_trap_failure_plausibility",
    },
    "datacenter": {
        "warehouse_mhe_charging_demand_peak",
        "warehouse_dock_infiltration_loss",
        "cold_chain_status_unknown",
        "process_load_vs_waste",
        "tenant_operator_boundary_unresolved",
        "boiler_degradation_plausibility",
        "compressed_air_leak_plausibility",
        "steam_trap_failure_plausibility",
        "hvac_schedule_drift",
    },
    "logistics_terminal": {
        "process_load_vs_waste",
        "boiler_degradation_plausibility",
        "compressed_air_leak_plausibility",
        "tenant_operator_boundary_unresolved",
    },
}


# Token markers that, when present in a gold nugget for a given asset family,
# signal cross-family language contamination. Lower-case, substring match.
_CROSS_FAMILY_NUGGET_TOKENS: dict[str, set[str]] = {
    "warehouse_distribution": {"tenant", "process heat", "boiler", "steam trap"},
    "cold_chain_facility": {"tenant", "process heat", "boiler", "steam trap", "compressed air"},
    "manufacturing_facility": {"tenant", "dock cycles", "charging window", "high-bay lighting"},
    "commercial_building": {"dock cycles", "charging window", "process heat", "boiler", "compressed air"},
    "datacenter": {"tenant", "dock cycles", "charging window", "process heat", "boiler"},
    "logistics_terminal": {"tenant", "process heat", "boiler", "compressed air"},
}


def _text(value: Any) -> str:
    return str(value or "").strip()


def _resolve_asset_family(inputs: dict[str, Any]) -> str:
    m007 = inputs.get("motor_007", {}) if isinstance(inputs.get("motor_007", {}), dict) else {}
    target_definition = (
        m007.get("target_definition_contract", {})
        if isinstance(m007.get("target_definition_contract", {}), dict)
        else {}
    )
    return _text(
        target_definition.get("target_type")
        or target_definition.get("asset_family")
    )


def _detect_pattern_contamination(
    asset_family: str,
    activated_combinations: list[dict],
) -> list[dict]:
    contamination_set = _CROSS_FAMILY_CONTAMINATION.get(asset_family, set())
    if not contamination_set:
        return []
    out: list[dict] = []
    for combo in activated_combinations:
        if not isinstance(combo, dict):
            continue
        combo_id = _text(combo.get("combination_id"))
        pattern_ids = list(combo.get("pattern_ids", []) or [])
        contaminating = sorted(set(pattern_ids).intersection(contamination_set))
        if contaminating:
            out.append(
                {
                    "rule_id": "AF1_pattern_contamination",
                    "severity": "critical",
                    "combination_id": combo_id,
                    "asset_family": asset_family,
                    "contaminating_patterns": contaminating,
                    "description": (
                        f"Combination '{combo_id}' activates patterns that do not "
                        f"belong to asset_family '{asset_family}': {contaminating}. "
                        "This is asset-family contamination — block the report."
                    ),
                }
            )
    return out


def _detect_nugget_token_contamination(
    asset_family: str,
    nuggets: list[dict],
) -> list[dict]:
    forbidden_tokens = _CROSS_FAMILY_NUGGET_TOKENS.get(asset_family, set())
    if not forbidden_tokens:
        return []
    out: list[dict] = []
    for nugget in nuggets:
        if not isinstance(nugget, dict):
            continue
        text = _text(nugget.get("gold_nugget") or nugget.get("nugget")).lower()
        if not text:
            continue
        offending = sorted(t for t in forbidden_tokens if t in text)
        if offending:
            out.append(
                {
                    "rule_id": "AF2_nugget_token_contamination",
                    "severity": "critical",
                    "nugget_id": _text(nugget.get("nugget_id")),
                    "asset_family": asset_family,
                    "offending_tokens": offending,
                    "description": (
                        f"Gold nugget for asset_family '{asset_family}' contains "
                        f"tokens that do not belong: {offending}. "
                        "Cross-family language leaked into the report."
                    ),
                }
            )
    return out


class Motor061Adapter(BaseMotorAdapter):
    @property
    def motor_id(self) -> str:
        return "motor_061"

    @property
    def input_motor_ids(self) -> list[str]:
        return ["motor_007", "motor_054"]

    def _run_impl(self, inputs: dict[str, Any]) -> dict[str, Any]:
        asset_family = _resolve_asset_family(inputs)
        m054 = inputs.get("motor_054", {}) if isinstance(inputs.get("motor_054", {}), dict) else {}
        activated_combinations = list(
            m054.get("skill_combination_activation_register", []) or []
        )
        nuggets = list(
            m054.get("strategic_gold_nugget_register")
            or m054.get("gold_nugget_register")
            or []
        )

        warnings: list[dict] = []
        warnings.extend(_detect_pattern_contamination(asset_family, activated_combinations))
        warnings.extend(_detect_nugget_token_contamination(asset_family, nuggets))

        critical_count = sum(1 for w in warnings if w.get("severity") == "critical")

        return {
            "asset_family_isolation_warnings": warnings,
            "warning_count": len(warnings),
            "critical_count": critical_count,
            "contamination_detected": critical_count > 0,
            "asset_family_evaluated": asset_family,
            "activated_combinations_count": len(activated_combinations),
            "rules_evaluated": [
                "AF1_pattern_contamination",
                "AF2_nugget_token_contamination",
            ],
        }
