"""V5 P9 — autodraft rule derivation tests.

Verifies the deterministic algorithm that derives `_AUTO_PATTERN_RULES`-
shaped rules from a pattern_spec's `trigger_conditions` +
`applicable_contexts`.
"""
from __future__ import annotations

import json
from pathlib import Path

from runtime_orchestrator.zlab_skill.autodraft_rule_derivation import (
    derive_autodraft_rule_from_pattern_spec,
    derive_rules_for_patterns_missing_autodraft,
)


_REPO_ROOT = Path(__file__).resolve().parents[2]
_REGISTRY = (
    _REPO_ROOT / "runtime-orchestrator" / "zlab_skill" / "registry" / "patterns"
)


# ── Single pattern derivation ───────────────────────────────────────


def test_derive_handles_simple_trigger():
    spec = {
        "trigger_conditions": ["refrigerated or frozen zone present"],
        "applicable_contexts": [],
    }
    rule = derive_autodraft_rule_from_pattern_spec(spec)
    assert rule is not None
    # 'present' stripped, 'or' splits → both alternatives kept
    group = rule["required_groups"][0]
    assert any("refrigerated" in g for g in group)
    assert any("frozen" in g for g in group)


def test_derive_expands_parenthesized_alternatives():
    spec = {
        "trigger_conditions": [
            "defrost initiation method (time/demand/ambient) unknown",
        ],
        "applicable_contexts": [],
    }
    rule = derive_autodraft_rule_from_pattern_spec(spec)
    assert rule is not None
    group = rule["required_groups"][0]
    # Should produce 'time', 'demand', 'ambient' as standalone alternatives
    # (the bare paren tokens) plus the composed forms
    assert "time" in group or any("time" in g for g in group)
    assert "demand" in group or any("demand" in g for g in group)
    assert "ambient" in group or any("ambient" in g for g in group)


def test_derive_strips_stopword_tails():
    spec = {
        "trigger_conditions": [
            "compressor inventory unresolved",
            "boiler condition unknown",
            "vapor barrier condition unknown",
        ],
        "applicable_contexts": [],
    }
    rule = derive_autodraft_rule_from_pattern_spec(spec)
    assert rule is not None
    # Should NOT contain trailing "unresolved", "unknown"
    flat = [t for group in rule["required_groups"] for t in group]
    assert not any("unresolved" in t for t in flat), flat
    assert not any(t.endswith(" unknown") for t in flat), flat


def test_derive_combines_multiple_triggers_into_separate_groups():
    spec = {
        "trigger_conditions": [
            "refrigerated zone present",
            "compressor inventory unresolved",
            "operating temperature setpoints unknown",
        ],
        "applicable_contexts": [],
    }
    rule = derive_autodraft_rule_from_pattern_spec(spec)
    assert rule is not None
    # First 2 triggers → required_groups (AND); rest → optional_terms.
    # Hand-authored rules use ≤3 groups so the 2-cap matches granularity.
    assert len(rule["required_groups"]) == 2
    # 3rd trigger surplus → optional_terms should include 'operating' or
    # 'temperature' or 'setpoints' (or 'setpoint')
    flat_opt = " ".join(rule["optional_terms"])
    assert any(t in flat_opt for t in ("operating", "temperature", "setpoint"))


def test_derive_uses_applicable_contexts_as_optional_terms():
    spec = {
        "trigger_conditions": ["refrigerated zone present"],
        "applicable_contexts": [
            "cold-chain or refrigerated facility confirmed",
            "refrigeration system inventory unresolved",
        ],
    }
    rule = derive_autodraft_rule_from_pattern_spec(spec)
    assert rule is not None
    # Some terms from applicable_contexts should appear in optional_terms
    opts = rule["optional_terms"]
    assert any("cold-chain" in t or "refrigeration system" in t for t in opts), opts


def test_derive_empty_input_returns_none():
    assert derive_autodraft_rule_from_pattern_spec({}) is None
    assert derive_autodraft_rule_from_pattern_spec({"trigger_conditions": []}) is None


def test_derive_only_applicable_contexts_falls_back():
    """If trigger_conditions empty, applicable_contexts are used as fallback."""
    spec = {
        "trigger_conditions": [],
        "applicable_contexts": ["evaporator coils in freezer zones"],
    }
    rule = derive_autodraft_rule_from_pattern_spec(spec)
    assert rule is not None
    assert rule["required_groups"]


# ── Real registry patterns derive cleanly ───────────────────────────


def _load_pattern(pid: str) -> dict:
    f = _REGISTRY / f"{pid}.v1.json"
    return json.loads(f.read_text(encoding="utf-8"))


def test_derive_refrigeration_duty_real_spec():
    rule = derive_autodraft_rule_from_pattern_spec(
        _load_pattern("refrigeration_duty")
    )
    assert rule is not None
    flat = [t for group in rule["required_groups"] for t in group]
    # Sanity: should include refrigeration-domain tokens
    assert any("refrigerated" in t or "frozen" in t for t in flat), flat
    assert any("compressor" in t or "condenser" in t for t in flat), flat


def test_derive_defrost_profile_real_spec():
    rule = derive_autodraft_rule_from_pattern_spec(
        _load_pattern("defrost_profile")
    )
    assert rule is not None
    flat = [t for group in rule["required_groups"] for t in group]
    assert any("defrost" in t for t in flat), flat


def test_derive_refrigerant_integrity_real_spec():
    rule = derive_autodraft_rule_from_pattern_spec(
        _load_pattern("refrigerant_integrity")
    )
    assert rule is not None
    flat = [t for group in rule["required_groups"] for t in group]
    assert any("refrigerant" in t for t in flat), flat


def test_derive_compressor_staging_real_spec():
    rule = derive_autodraft_rule_from_pattern_spec(
        _load_pattern("compressor_staging")
    )
    assert rule is not None
    flat = [t for group in rule["required_groups"] for t in group]
    assert any("compressor" in t for t in flat), flat


def test_derive_thermal_boundary_real_spec():
    rule = derive_autodraft_rule_from_pattern_spec(
        _load_pattern("thermal_boundary")
    )
    assert rule is not None
    flat = [t for group in rule["required_groups"] for t in group]
    # Should have insulation/envelope keywords
    assert any("insulation" in t or "envelope" in t or "vapor" in t for t in flat), flat


# ── Bulk derivation ─────────────────────────────────────────────────


def test_bulk_derive_only_for_missing_ids():
    pattern_specs = {
        "alpha": {"trigger_conditions": ["alpha foo present"]},
        "beta": {"trigger_conditions": ["beta bar unknown"]},
        "gamma": {"trigger_conditions": ["gamma baz unresolved"]},
    }
    existing = {"beta"}
    out = derive_rules_for_patterns_missing_autodraft(pattern_specs, existing)
    assert "beta" not in out
    assert "alpha" in out
    assert "gamma" in out


def test_bulk_derive_skips_unusable_patterns():
    pattern_specs = {
        "empty": {"trigger_conditions": [], "applicable_contexts": []},
        "good": {"trigger_conditions": ["compressor inventory unresolved"]},
    }
    out = derive_rules_for_patterns_missing_autodraft(pattern_specs, set())
    assert "empty" not in out  # no usable content
    assert "good" in out


def test_bulk_derive_covers_all_10_missing_registry_patterns():
    """The 10 patterns that lacked hand-authored autodraft rules in V5 P3
    must ALL derive cleanly here."""
    missing_ids = [
        "refrigeration_duty", "defrost_profile", "refrigerant_integrity",
        "compressor_staging", "door_cycle_losses", "infiltration_load",
        "thermal_boundary", "maintenance_hidden_value_driver",
        "process_load_vs_waste", "procurement_vs_lifecycle_cost",
    ]
    specs = {pid: _load_pattern(pid) for pid in missing_ids}
    out = derive_rules_for_patterns_missing_autodraft(specs, set())
    for pid in missing_ids:
        assert pid in out, f"failed to derive rule for {pid}"
        rule = out[pid]
        assert rule["required_groups"], f"{pid} produced empty required_groups"
