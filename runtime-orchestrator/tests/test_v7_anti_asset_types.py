"""V7 P3 — explicit anti_asset_types per pattern.

When a pattern spec declares `anti_asset_types` explicitly, the isolation
contract uses that list as the forbidden set (NOT the complement of
asset_types). Families neither in asset_types nor in anti_asset_types
are "neutral" — pattern doesn't apply but it's not flagged as
contamination either.
"""
from __future__ import annotations

import pytest

from runtime_orchestrator.pattern_isolation import (
    IsolationContract,
    audit_isolation_violations,
    pattern_isolation_contract,
    reset_registry_cache,
)


@pytest.fixture(autouse=True)
def _reset_cache():
    reset_registry_cache()
    yield
    reset_registry_cache()


# ── Spec-driven anti list ─────────────────────────────────────────


def test_inline_spec_with_anti_uses_explicit_forbidden():
    spec = {
        "id": "synthetic_anti_test",
        "asset_types": ["warehouse_distribution"],
        "anti_asset_types": ["commercial_building", "cold_chain_facility"],
    }
    c = pattern_isolation_contract(spec)
    assert c.explicit_anti_declared is True
    assert c.forbidden_families == frozenset({"commercial_building", "cold_chain_facility"})
    # datacenter is neither allowed nor in anti → neutral
    assert "datacenter" not in c.allowed_families
    assert "datacenter" not in c.forbidden_families


def test_inline_spec_without_anti_keeps_complement():
    """Backward compat: patterns without anti_asset_types still derive
    forbidden = complement of allowed."""
    spec = {
        "id": "synthetic_no_anti",
        "asset_types": ["datacenter"],
    }
    c = pattern_isolation_contract(spec)
    assert c.explicit_anti_declared is False
    assert "cold_chain_facility" in c.forbidden_families
    assert "warehouse_distribution" in c.forbidden_families


# ── Audit semantics ────────────────────────────────────────────────


def test_audit_flags_explicit_anti_target():
    activations = [
        {"pattern_id": "synthetic_anti_target",
         "asset_family": "commercial_building",
         "spec": True},
    ]
    # We use the registry path through refrigeration_duty which now has
    # anti_asset_types declared.
    activations = [
        {"pattern_id": "refrigeration_duty", "asset_family": "commercial_building"},
    ]
    violations = audit_isolation_violations(activations)
    assert len(violations) == 1
    assert violations[0]["reason"] == "explicit_anti_family"


def test_audit_does_not_flag_neutral_family_when_anti_explicit():
    """If a pattern has explicit anti list and target is NEITHER allowed
    NOR in anti → no violation (it's neutral)."""
    # refrigeration_duty: asset_types=[cold_chain_facility, cold_chain_distribution,
    # food_processing, supermarket]; anti=[datacenter, commercial_building,
    # infrastructure_node, manufacturing_facility]
    # → "warehouse_distribution" is neutral.
    activations = [
        {"pattern_id": "refrigeration_duty", "asset_family": "warehouse_distribution"},
    ]
    violations = audit_isolation_violations(activations)
    assert violations == []


def test_audit_still_flags_complement_when_anti_absent():
    """For patterns WITHOUT anti_asset_types, every non-allowed family is
    still flagged as forbidden_family (legacy V6 behavior)."""
    # high_bay_lighting_waste did not get anti_asset_types in V7 P3.
    activations = [
        {"pattern_id": "high_bay_lighting_waste", "asset_family": "cold_chain_facility"},
    ]
    violations = audit_isolation_violations(activations)
    assert len(violations) == 1
    assert violations[0]["reason"] == "forbidden_family"


# ── Registry-level: 6 patterns now declare anti explicitly ─────────


_EXPECTED_ANTI_PATTERNS = {
    "refrigeration_duty",
    "defrost_profile",
    "compressor_staging",
    "door_cycle_losses",
    "boiler_degradation_plausibility",
    "hvac_schedule_drift",
}


def test_six_canonical_patterns_declare_explicit_anti():
    for pid in _EXPECTED_ANTI_PATTERNS:
        c = pattern_isolation_contract(pid)
        assert c.explicit_anti_declared, (
            f"{pid} should declare anti_asset_types explicitly in V7 P3"
        )
        assert c.declared_anti_asset_types, f"{pid} anti list is empty"


def test_refrigeration_anti_does_not_overlap_with_allowed():
    c = pattern_isolation_contract("refrigeration_duty")
    overlap = c.allowed_families & c.forbidden_families
    assert overlap == frozenset(), f"overlap: {overlap}"


def test_boiler_anti_blocks_cold_chain():
    """boiler_degradation_plausibility activating on cold_chain_facility → block."""
    activations = [
        {"pattern_id": "boiler_degradation_plausibility",
         "asset_family": "cold_chain_facility"},
    ]
    violations = audit_isolation_violations(activations)
    assert len(violations) == 1
    assert violations[0]["reason"] == "explicit_anti_family"


def test_hvac_drift_anti_blocks_manufacturing():
    activations = [
        {"pattern_id": "hvac_schedule_drift", "asset_family": "manufacturing_facility"},
    ]
    violations = audit_isolation_violations(activations)
    assert len(violations) == 1
    assert violations[0]["reason"] == "explicit_anti_family"
