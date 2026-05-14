"""TAD action registry (V3 G11 machinery closure).

The framework uses ~18 TAD action strings emitted in pattern specs'
`tad_actions` field. Until V3 they were free text — any pattern could
emit any string. This module introduces a REGISTERED set of valid
action_ids plus a validator that ensures pattern.tad_actions reference
only registered actions.

Per the V4 P0 rule: this is machinery (a registry + validator), not
content. The set of valid actions is OPEN at extension time — new
actions enter via TAD_ACTIONS table here OR via a future YAML registry
loaded at runtime. Pattern files don't get edited by Claude; they get
validated against the registry.

V3 G11 deliberately closes the MACHINERY half (this module + validator)
without adding content (Claude does not author 5 new TAD actions
inside pattern files). When real V4 P1 extraction proposes new TAD
actions, they enter via knowledge_pending/ approval and may extend
this registry through a future yaml-driven loader.

Validator usage:
  from runtime_orchestrator.tad_action_registry import (
      is_registered_action, unknown_actions_in,
  )
"""
from __future__ import annotations

from typing import Iterable


# Canonical TAD actions discovered from V1-V2 patterns. Frozen here so a
# typo in a pattern's tad_actions field is caught at validation time.
# New actions extend the set by adding to this tuple — never by editing
# the pattern files (that would be content).
TAD_ACTIONS: frozenset[str] = frozenset({
    # validate / falsify
    "VALIDATE_LOSS_PATTERN",
    "VALIDATE_MAINTENANCE_REALITY",
    "VALIDATE_REGULATORY_EXPOSURE",
    "VALIDATE_TARIFF_EXPOSURE",
    "VALIDATE_PF_TARIFF_EXPOSURE",
    "VALIDATE_CONTROL_BOUNDARY",
    "VALIDATE_DOCK_ACTIVITY",
    "VALIDATE_CHARGING_PROFILE",
    "VALIDATE_TEMPERATURE_DUTY",
    "VALIDATE_DRY_VS_COLD_CHAIN",
    "VALIDATE_FIRST",
    # do not / hold
    "DO_NOT_INVEST_YET",
    "DO_NOT_MODEL_YET",
    "DO_NOT_SENSOR_YET",
    "DO_NOT_UNDERWRITE_ENERGY_RETROFIT_YET",
    "DO_NOT_RETROFIT_YET",  # V8 P4
    "DO_NOT_RECOMMEND_HVAC_CAPEX_UNTIL_DOCK_INTERFACE_IS_BOUNDED",
    "DO_NOT_RECOMMEND_CAPACITOR_BANK_YET",
    "REQUEST_EVIDENCE_FIRST",  # V8 P4
    "COMPARE_ONLY_AFTER_NORMALIZATION",  # V8 P4
    # peer set / fair comparison
    "BUILD_FAIR_PEER_SET",
    "PROHIBIT_GENERIC_WAREHOUSE_COMPARISON",
    # inspection / request (used by V2 cold-chain patterns)
    "INSPECT_DOORS_AND_SEALS",
    "INSPECT_DOOR_DISCIPLINE",
    "INSPECT_DEFROST_CONTROLS",
    "INSPECT_COMPRESSOR_STAGING",
    "DECOMPOSE_REFRIGERATION_DUTY",
    "REQUEST_LEAK_AUDIT",
    "REQUEST_ENVELOPE_AUDIT",
    # pre-existing user-authored actions (commit 810844d — not Claude content)
    "REQUEST_MINIMUM_EVIDENCE",
    "REQUEST_UTILITY_BILLS",
    "REQUEST_CONTROL_BOUNDARY",
    "PROHIBIT_CLAIM",
    "PROHIBIT_ROI",
    "PROHIBIT_PEER_SUPERIORITY",
    "COMPARE_FAIRLY",
    "DEFINE_MODEL_PURPOSE",
    "REDESIGN_HYPOTHESIS",
    "DEFER_RETROFIT_UNDERWRITING",
})


def is_registered_action(action: str) -> bool:
    """Whether the action string is in the canonical registry."""
    return (action or "").strip() in TAD_ACTIONS


def unknown_actions_in(actions: Iterable[str]) -> list[str]:
    """Return the subset of `actions` that are NOT registered."""
    return sorted(a for a in actions if (a or "").strip() and not is_registered_action(a))


def all_registered_actions() -> list[str]:
    """Stable sorted list of registered actions — for dashboard / API surfaces."""
    return sorted(TAD_ACTIONS)


def action_count() -> int:
    return len(TAD_ACTIONS)


def validate_pattern_tad_actions(pattern_id: str, tad_actions: list) -> None:
    """Raise ValueError if any tad_action in a pattern is not registered."""
    unknown = unknown_actions_in(tad_actions or [])
    if unknown:
        raise ValueError(
            f"pattern '{pattern_id}' references unregistered TAD action(s): "
            f"{unknown}. Registered actions: {sorted(TAD_ACTIONS)}"
        )
