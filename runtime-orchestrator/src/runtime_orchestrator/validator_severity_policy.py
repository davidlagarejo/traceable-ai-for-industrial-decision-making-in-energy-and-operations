"""V6 P4 — centralized validator severity policy.

Today, motor_055-063 each hard-code their own severity ("warning" /
"critical"). Promoting individual rules to BLOCK requires editing every
motor file individually and rerunning regression. Risky.

V6 P4 centralizes the policy: each validator imports this module and
consults `effective_severity(motor_id, rule_id, default_severity)`.
The policy can then promote specific rules from warn→block based on:

  1. Global environment flag ZLAB_VALIDATORS_HARD_BLOCK=1
  2. Per-rule allowlist `_V6_BLOCKING_RULES` (the canonical V6 set)
  3. Pipeline-level opt-out `__pipeline__.__validators_soft_mode__ = true`
     (preserves regression backward compat — tests run in soft mode)

This gives a single switchboard. The default remains soft (warn) so
existing regression tests pass; opt-in HARD mode activates blocks.

Phase 0 anchor: "validators detect AND BLOCK". V6 ships the centralized
gate; later V6 sub-fases flip it on by default.
"""
from __future__ import annotations

import os
from typing import Mapping


# The CANONICAL V6 blocking rule set. Each entry is a (motor_id, rule_id)
# pair that V6 considers a hard-block contamination signal. When the
# policy is active, these promote from "warning" to "blocking" severity.
_V6_BLOCKING_RULES: frozenset[tuple[str, str]] = frozenset({
    # motor_055 Hypothesis Diversity — block on <2 active claims or
    # duplicate signatures. HD3 stays warn (TAD convergence is informational).
    ("motor_055", "HD1_low_claim_count"),
    ("motor_055", "HD2_duplicate_claim_signature"),

    # motor_056 Evidence Repetition — block on pack repetition (the
    # "service-level proxy in 5+ sections" symptom). ER2/ER3 stay warn.
    ("motor_056", "ER1_pack_repetition"),

    # motor_057 Gold Nugget Quality — block when nugget has zero
    # asset-family token (archetype-replay). GN2/GN3 stay warn.
    ("motor_057", "GN1_archetype_replay"),

    # motor_058 Report Uniqueness — block on verbatim nugget reuse.
    # RU1 (jaccard threshold) stays warn (probabilistic). RU3 stays warn.
    ("motor_058", "RU2_verbatim_nugget_reuse"),

    # motor_059 Strategic Intelligence — block on allowed-claim-without-
    # falsification AND TAD ACT-NOW on prohibited claim AND OBSERVED_FACT
    # without supporting evidence. R3 informational stays warn.
    ("motor_059", "R1_missing_falsification"),
    ("motor_059", "R2_act_now_with_prohibited_claim"),
    ("motor_059", "R4_observed_fact_without_evidence"),

    # motor_061 Asset Family Isolation — ALL critical contamination
    # findings block. Cross-family pattern activation is the V6 priority.
    ("motor_061", "AF1_pattern_contamination"),
    ("motor_061", "AF2_nugget_token_contamination"),

    # motor_062 Scenario Justification — ALL three SJ rules block when
    # the global gate is on (overrides motor_062's own mode="warn" default).
    ("motor_062", "SJ1_scenario_missing_justification"),
    ("motor_062", "SJ2_scenario_source_unknown"),
    ("motor_062", "SJ3_source_family_mismatch"),

    # motor_063 Chart Validity — block on decorative-risk charts (CV1)
    # and decorative-ratio critical tier (CV3).
    ("motor_063", "CV1_decorative_risk_chart"),
    ("motor_063", "CV3_decorative_ratio_critical"),
})


# Environment flag that flips the policy ON for the entire pipeline.
# Tests/regression run WITHOUT this flag → soft mode (warn-only).
# CI smoke tests can opt in with: export ZLAB_VALIDATORS_HARD_BLOCK=1
_ENV_FLAG = "ZLAB_VALIDATORS_HARD_BLOCK"


def hard_mode_active(pipeline_inputs: Mapping | None = None) -> bool:
    """True iff V6 hard-block mode is requested.

    Lookup order:
      1. pipeline_inputs.__validators_hard_block__ (explicit per-run override)
      2. pipeline_inputs.__validators_soft_mode__ → if True, forces False
      3. environment variable ZLAB_VALIDATORS_HARD_BLOCK ("1"/"true"/"yes")
      4. default: False (soft mode — preserves regression backward compat)
    """
    if pipeline_inputs:
        explicit = pipeline_inputs.get("__validators_hard_block__")
        if explicit is not None:
            return bool(explicit)
        if pipeline_inputs.get("__validators_soft_mode__"):
            return False
    env = (os.environ.get(_ENV_FLAG, "") or "").lower().strip()
    return env in ("1", "true", "yes", "on")


def is_v6_blocking_rule(motor_id: str, rule_id: str) -> bool:
    """True iff (motor_id, rule_id) is in the canonical V6 blocking set."""
    return (motor_id, rule_id) in _V6_BLOCKING_RULES


def effective_severity(
    motor_id: str,
    rule_id: str,
    default_severity: str,
    *,
    pipeline_inputs: Mapping | None = None,
) -> str:
    """Return the effective severity for a (motor_id, rule_id) finding.

    Args:
      motor_id: e.g. "motor_061"
      rule_id: the validator's rule identifier
      default_severity: what the motor would emit pre-V6 ("warning",
        "critical", "informational")
      pipeline_inputs: optional pipeline inputs to check overrides

    Returns:
      "blocking" if hard mode active AND rule in V6 blocking set
      Otherwise unchanged default_severity.

    This is the ONE function each validator calls. The decision lives
    in this module; the validators only ASK.
    """
    if not is_v6_blocking_rule(motor_id, rule_id):
        return default_severity
    if not hard_mode_active(pipeline_inputs):
        return default_severity
    return "blocking"


def list_v6_blocking_rules() -> list[tuple[str, str]]:
    """Return all (motor_id, rule_id) pairs in the V6 blocking set.

    Used by the dashboard and stability test suite to enumerate hard-
    block rules.
    """
    return sorted(_V6_BLOCKING_RULES)
