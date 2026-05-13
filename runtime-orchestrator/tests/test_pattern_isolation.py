"""V6 P5 — Pattern Asset-Family Isolation Engine tests."""
from __future__ import annotations

import pytest

from runtime_orchestrator.pattern_isolation import (
    IsolationContract,
    PatternIsolationViolation,
    audit_isolation_violations,
    is_activation_allowed,
    list_registered_patterns,
    pattern_isolation_contract,
    reset_registry_cache,
    validate_activation,
)
from runtime_orchestrator.industrial_research_engine.family_scope import (
    ALL_KNOWN_ASSET_FAMILIES,
)


@pytest.fixture(autouse=True)
def _reset_cache():
    reset_registry_cache()
    yield
    reset_registry_cache()


# ── Registry loads cleanly ─────────────────────────────────────────


def test_registry_loads_all_30_patterns():
    patterns = list_registered_patterns()
    assert len(patterns) >= 30
    assert "refrigeration_duty" in patterns
    assert "compressor_staging" in patterns
    assert "high_bay_lighting_waste" in patterns


# ── Contract derivation ────────────────────────────────────────────


def test_contract_for_refrigeration_duty_allows_cold_chain():
    c = pattern_isolation_contract("refrigeration_duty")
    assert isinstance(c, IsolationContract)
    assert "cold_chain_facility" in c.allowed_families
    assert "cold_chain_distribution" in c.allowed_families
    # forbidden = complement
    assert "datacenter" in c.forbidden_families
    assert "datacenter" not in c.allowed_families


def test_contract_allowed_plus_forbidden_partition_universe():
    c = pattern_isolation_contract("refrigeration_duty")
    union = c.allowed_families | c.forbidden_families
    assert union == ALL_KNOWN_ASSET_FAMILIES
    assert not (c.allowed_families & c.forbidden_families)


def test_contract_from_inline_spec_dict():
    spec = {
        "id": "synthetic_pattern",
        "asset_types": ["datacenter"],
    }
    c = pattern_isolation_contract(spec)
    assert c.pattern_id == "synthetic_pattern"
    assert c.allowed_families == frozenset({"datacenter"})
    assert "cold_chain_facility" in c.forbidden_families


# ── Activation gate ────────────────────────────────────────────────


def test_is_activation_allowed_positive():
    assert is_activation_allowed("refrigeration_duty", "cold_chain_facility")


def test_is_activation_allowed_negative_for_unrelated_family():
    assert not is_activation_allowed("refrigeration_duty", "datacenter")


def test_validate_activation_raises_on_forbidden_family():
    with pytest.raises(PatternIsolationViolation, match="not declared"):
        validate_activation("refrigeration_duty", "datacenter")


def test_validate_activation_silent_on_allowed_family():
    # Should not raise
    validate_activation("refrigeration_duty", "cold_chain_facility")


# ── Audit batch helper ─────────────────────────────────────────────


def test_audit_clean_activations_returns_empty():
    activations = [
        {"pattern_id": "refrigeration_duty", "asset_family": "cold_chain_facility"},
        {"pattern_id": "compressor_staging", "asset_family": "cold_chain_facility"},
    ]
    assert audit_isolation_violations(activations) == []


def test_audit_flags_cross_family_contamination():
    activations = [
        {"pattern_id": "refrigeration_duty", "asset_family": "datacenter"},
    ]
    violations = audit_isolation_violations(activations)
    assert len(violations) == 1
    v = violations[0]
    assert v["pattern_id"] == "refrigeration_duty"
    assert v["target_family"] == "datacenter"
    assert v["reason"] == "forbidden_family"
    assert "cold_chain_facility" in v["allowed_families"]


def test_audit_flags_unknown_pattern_id():
    activations = [{"pattern_id": "nonexistent_pattern", "asset_family": "datacenter"}]
    violations = audit_isolation_violations(activations)
    assert len(violations) == 1
    assert violations[0]["reason"] == "unknown_pattern_id"


def test_audit_accepts_alt_field_names():
    activations = [
        {"pattern": "refrigeration_duty", "family": "datacenter"},
    ]
    violations = audit_isolation_violations(activations)
    assert len(violations) == 1


def test_audit_skips_malformed_rows():
    activations = [
        None,
        "not a dict",
        {"pattern_id": "refrigeration_duty"},  # missing family
        {"asset_family": "datacenter"},  # missing pattern
    ]
    assert audit_isolation_violations(activations) == []


def test_audit_empty_input_returns_empty():
    assert audit_isolation_violations([]) == []
    assert audit_isolation_violations(None) == []  # type: ignore[arg-type]


# ── Universal sentinel handling ────────────────────────────────────


def test_universal_sentinel_allows_every_family():
    """digital_twin_prematurity declares all_operational_assets and must
    activate on every known family without violation."""
    c = pattern_isolation_contract("digital_twin_prematurity")
    assert c.allowed_families == ALL_KNOWN_ASSET_FAMILIES
    assert not c.forbidden_families
    assert is_activation_allowed("digital_twin_prematurity", "datacenter")
    assert is_activation_allowed("digital_twin_prematurity", "cold_chain_facility")


# ── Every registered pattern produces a valid contract ─────────────


def test_every_registered_pattern_has_at_least_one_allowed_family():
    """No pattern should accidentally declare zero known families."""
    for pid in list_registered_patterns():
        contract = pattern_isolation_contract(pid)
        assert contract.allowed_families, (
            f"pattern {pid} has empty allowed_families "
            f"(declared asset_types={contract.declared_asset_types})"
        )
