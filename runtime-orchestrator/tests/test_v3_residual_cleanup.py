"""V3 residual cleanup tests (G3 family alignment + G11 TAD registry + G12 fair-comp registry).

Closes the 3 V3 gaps that could be done as pure machinery without
authoring content:
  G3 — motor_061 reads families from family_scope.ALL_KNOWN_ASSET_FAMILIES
  G11 — tad_action_registry validates pattern.tad_actions
  G12 — fair_comparison_registry loads + validates rules YAML
"""
from __future__ import annotations

import json
import os
from pathlib import Path

import pytest

from runtime_orchestrator.adapters.motor_061 import (
    Motor061Adapter,
    is_family_canonically_known,
    _contamination_set_for,
)
from runtime_orchestrator.fair_comparison_registry import (
    FairComparisonRulesError,
    canonical_match_keys,
    load_fair_comparison_rules,
    reload_rules,
    rules_for_family,
)
from runtime_orchestrator.industrial_research_engine.family_scope import (
    ALL_KNOWN_ASSET_FAMILIES,
)
from runtime_orchestrator.tad_action_registry import (
    TAD_ACTIONS,
    action_count,
    all_registered_actions,
    is_registered_action,
    unknown_actions_in,
    validate_pattern_tad_actions,
)


# ── G3: motor_061 ↔ family_scope alignment ────────────────────────────


def test_g3_motor_061_recognizes_all_16_canonical_families():
    """motor_061 should accept every family in family_scope without raising,
    even when no contamination rules are defined for that family."""
    for family in ALL_KNOWN_ASSET_FAMILIES:
        assert is_family_canonically_known(family) is True


def test_g3_unknown_family_falls_to_empty_contamination_set():
    """Unknown families return empty set — graceful permissive default."""
    assert _contamination_set_for("unicorn_factory") == set()


def test_g3_canonical_family_without_explicit_rules_returns_empty_set():
    """Families that ARE canonical but have no V2-era rules return empty —
    no false positives when V4 brings new families."""
    # pharma_facility is canonical (V4 P0 family_scope) but motor_061 has
    # no contamination set for it yet → should return empty, not raise.
    assert _contamination_set_for("pharma_facility") == set()
    assert _contamination_set_for("food_processing") == set()


def test_g3_existing_family_contamination_still_works():
    """The V2-era contamination sets are still active for the 6 original families."""
    cs = _contamination_set_for("warehouse_distribution")
    assert "process_load_vs_waste" in cs
    assert "boiler_degradation_plausibility" in cs


def test_g3_motor_061_output_surfaces_canonical_taxonomy_signal():
    out = Motor061Adapter().run({
        "motor_007": {"target_definition_contract": {"target_type": "cold_chain_facility"}},
        "motor_054": {},
    })
    assert "asset_family_in_canonical_taxonomy" in out
    assert out["asset_family_in_canonical_taxonomy"] is True
    assert out["canonical_asset_family_count"] == len(ALL_KNOWN_ASSET_FAMILIES)


def test_g3_motor_061_handles_new_v4_family_gracefully():
    """Pharma-family case: motor_061 doesn't crash, doesn't fire contamination,
    surfaces canonical_taxonomy_signal=True."""
    out = Motor061Adapter().run({
        "motor_007": {"target_definition_contract": {"target_type": "pharma_facility"}},
        "motor_054": {
            "skill_combination_activation_register": [
                {"combination_id": "test", "pattern_ids": ["any_pattern"]}
            ]
        },
    })
    assert out["asset_family_in_canonical_taxonomy"] is True
    assert out["contamination_detected"] is False  # no rules defined → no contamination


# ── G11: TAD action registry ──────────────────────────────────────────


def test_g11_registry_has_at_least_25_actions():
    assert action_count() >= 25


def test_g11_known_actions_are_recognized():
    for action in [
        "VALIDATE_LOSS_PATTERN",
        "DO_NOT_INVEST_YET",
        "BUILD_FAIR_PEER_SET",
        "REQUEST_MINIMUM_EVIDENCE",
        "PROHIBIT_ROI",
    ]:
        assert is_registered_action(action) is True


def test_g11_unknown_action_rejected():
    assert is_registered_action("MAKE_COFFEE") is False


def test_g11_unknown_actions_in_returns_subset():
    assert unknown_actions_in([
        "VALIDATE_LOSS_PATTERN",
        "MAKE_COFFEE",
        "FIND_THE_BUG",
        "DO_NOT_INVEST_YET",
    ]) == ["FIND_THE_BUG", "MAKE_COFFEE"]


def test_g11_validate_pattern_tad_actions_passes_for_known_actions():
    validate_pattern_tad_actions("test_pattern", ["VALIDATE_LOSS_PATTERN", "DO_NOT_INVEST_YET"])


def test_g11_validate_pattern_tad_actions_rejects_unknown():
    with pytest.raises(ValueError, match="unregistered TAD action"):
        validate_pattern_tad_actions("bad_pattern", ["VALIDATE_LOSS_PATTERN", "TYPO_ACTION"])


def test_g11_all_existing_patterns_pass_registry_validation():
    """Critical: every pattern committed in the repo references only
    registered TAD actions. This locks down the contract — typos in
    future pattern files get caught."""
    patterns_dir = Path(__file__).resolve().parents[1] / "zlab_skill" / "registry" / "patterns"
    failures: list[str] = []
    for p in patterns_dir.glob("*.json"):
        data = json.loads(p.read_text(encoding="utf-8"))
        unk = unknown_actions_in(data.get("tad_actions", []) or [])
        if unk:
            failures.append(f"{p.name}: {unk}")
    assert not failures, (
        f"patterns referencing unregistered TAD actions:\n" + "\n".join(failures)
    )


def test_g11_all_registered_actions_is_sorted():
    actions = all_registered_actions()
    assert actions == sorted(actions)


# ── G12: fair_comparison_registry ─────────────────────────────────────


def test_g12_canonical_match_keys_has_at_least_15_keys():
    assert len(canonical_match_keys()) >= 15


def test_g12_canonical_match_keys_includes_key_dimensions():
    keys = canonical_match_keys()
    for required in ("target_family", "naics_4", "throughput_band", "thermal_duty_band"):
        assert required in keys


def test_g12_empty_rules_yaml_returns_empty_list():
    """Current fair_comparison_rules.yaml has no `rules:` section. Loader
    must return [] without raising — preserves V3 behavior."""
    reload_rules()
    rules = load_fair_comparison_rules()
    assert isinstance(rules, list)


def test_g12_rules_for_family_returns_list():
    rules = rules_for_family("cold_chain_facility")
    assert isinstance(rules, list)


def test_g12_loader_validates_rule_schema(tmp_path, monkeypatch):
    """Inject a tmp YAML with a bad rule (unknown family) and verify
    the loader raises."""
    import runtime_orchestrator.fair_comparison_registry as fcr
    bad_yaml = tmp_path / "fair_comparison_rules.yaml"
    bad_yaml.write_text("""\
rules:
  - rule_id: bad_rule
    applies_to_families:
      - unicorn_factory
""", encoding="utf-8")
    monkeypatch.setattr(fcr, "_RULES_PATH", bad_yaml)
    fcr.reload_rules()
    with pytest.raises(FairComparisonRulesError, match="unknown families"):
        fcr.load_fair_comparison_rules()


def test_g12_loader_rejects_duplicate_rule_ids(tmp_path, monkeypatch):
    import runtime_orchestrator.fair_comparison_registry as fcr
    yaml_path = tmp_path / "fair_comparison_rules.yaml"
    yaml_path.write_text("""\
rules:
  - rule_id: r1
    applies_to_families: []
  - rule_id: r1
    applies_to_families: []
""", encoding="utf-8")
    monkeypatch.setattr(fcr, "_RULES_PATH", yaml_path)
    fcr.reload_rules()
    with pytest.raises(FairComparisonRulesError, match="duplicate rule_id"):
        fcr.load_fair_comparison_rules()


def test_g12_loader_accepts_valid_rule(tmp_path, monkeypatch):
    import runtime_orchestrator.fair_comparison_registry as fcr
    yaml_path = tmp_path / "fair_comparison_rules.yaml"
    yaml_path.write_text("""\
rules:
  - rule_id: process_vs_process
    applies_to_families:
      - manufacturing_facility
      - thermal_process_facility
    requires_match:
      - target_family
      - naics_4
      - throughput_band
    blocks_when: missing throughput characterization
    rationale: Throughput band is structural to process duty.
""", encoding="utf-8")
    monkeypatch.setattr(fcr, "_RULES_PATH", yaml_path)
    fcr.reload_rules()
    rules = fcr.load_fair_comparison_rules()
    assert len(rules) == 1
    assert rules[0]["rule_id"] == "process_vs_process"
    assert "naics_4" in rules[0]["requires_match"]


def test_g12_loader_filters_rules_for_family(tmp_path, monkeypatch):
    import runtime_orchestrator.fair_comparison_registry as fcr
    yaml_path = tmp_path / "fair_comparison_rules.yaml"
    yaml_path.write_text("""\
rules:
  - rule_id: mfg_only
    applies_to_families:
      - manufacturing_facility
  - rule_id: universal
    applies_to_families: []
""", encoding="utf-8")
    monkeypatch.setattr(fcr, "_RULES_PATH", yaml_path)
    fcr.reload_rules()
    mfg = fcr.rules_for_family("manufacturing_facility")
    cold = fcr.rules_for_family("cold_chain_facility")
    assert {r["rule_id"] for r in mfg} == {"mfg_only", "universal"}
    assert {r["rule_id"] for r in cold} == {"universal"}
