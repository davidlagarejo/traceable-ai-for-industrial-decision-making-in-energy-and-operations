"""V6 P4 — validator_severity_policy tests."""
from __future__ import annotations

import os

import pytest

from runtime_orchestrator.validator_severity_policy import (
    _ENV_FLAG,
    effective_severity,
    hard_mode_active,
    is_v6_blocking_rule,
    list_v6_blocking_rules,
)


# ── V6 blocking rule set ────────────────────────────────────────────


def test_blocking_set_contains_expected_rules():
    """The canonical V6 set must include the named contamination signals."""
    expected = {
        ("motor_061", "asset_family_contamination_critical"),
        ("motor_062", "SJ1_scenario_missing_justification"),
        ("motor_063", "CV1_decorative_risk_chart"),
        ("motor_058", "RU2_verbatim_nugget_reuse"),
        ("motor_055", "HD1_fewer_than_2_active_claims"),
    }
    blocking = set(list_v6_blocking_rules())
    for entry in expected:
        assert entry in blocking, f"missing V6 blocking rule: {entry}"


def test_is_v6_blocking_rule_positive_case():
    assert is_v6_blocking_rule("motor_061", "asset_family_contamination_critical")
    assert is_v6_blocking_rule("motor_063", "CV3_decorative_ratio_contamination")


def test_is_v6_blocking_rule_negative_case():
    """Rules NOT in V6 set must return False."""
    assert not is_v6_blocking_rule("motor_055", "HD3_tad_convergence")  # informational
    assert not is_v6_blocking_rule("motor_062", "SJ_unknown_rule")
    assert not is_v6_blocking_rule("motor_999", "any_rule")


# ── hard_mode_active resolution ─────────────────────────────────────


def test_hard_mode_default_off(monkeypatch):
    monkeypatch.delenv(_ENV_FLAG, raising=False)
    assert hard_mode_active() is False


def test_hard_mode_env_flag_activates(monkeypatch):
    monkeypatch.setenv(_ENV_FLAG, "1")
    assert hard_mode_active() is True


def test_hard_mode_env_flag_accepts_true_yes_on(monkeypatch):
    for value in ("true", "yes", "on", "TRUE", "Yes"):
        monkeypatch.setenv(_ENV_FLAG, value)
        assert hard_mode_active() is True, value


def test_hard_mode_pipeline_inputs_override(monkeypatch):
    """pipeline_inputs.__validators_hard_block__ overrides env."""
    monkeypatch.delenv(_ENV_FLAG, raising=False)
    inputs = {"__validators_hard_block__": True}
    assert hard_mode_active(inputs) is True


def test_hard_mode_soft_mode_forces_off(monkeypatch):
    """pipeline_inputs.__validators_soft_mode__=True forces soft even when env is on."""
    monkeypatch.setenv(_ENV_FLAG, "1")
    inputs = {"__validators_soft_mode__": True}
    assert hard_mode_active(inputs) is False


def test_hard_mode_explicit_override_takes_precedence(monkeypatch):
    """explicit __validators_hard_block__ beats __validators_soft_mode__."""
    monkeypatch.delenv(_ENV_FLAG, raising=False)
    inputs = {
        "__validators_hard_block__": True,
        "__validators_soft_mode__": True,  # ignored when explicit set
    }
    assert hard_mode_active(inputs) is True


# ── effective_severity ──────────────────────────────────────────────


def test_effective_severity_soft_mode_returns_default(monkeypatch):
    monkeypatch.delenv(_ENV_FLAG, raising=False)
    assert effective_severity(
        "motor_061", "asset_family_contamination_critical", "warning"
    ) == "warning"
    assert effective_severity(
        "motor_063", "CV1_decorative_risk_chart", "critical"
    ) == "critical"


def test_effective_severity_hard_mode_promotes_v6_blocking(monkeypatch):
    monkeypatch.setenv(_ENV_FLAG, "1")
    # rule in V6 blocking set + hard mode → "blocking"
    assert effective_severity(
        "motor_061", "asset_family_contamination_critical", "warning"
    ) == "blocking"
    assert effective_severity(
        "motor_062", "SJ1_scenario_missing_justification", "warning"
    ) == "blocking"


def test_effective_severity_hard_mode_does_NOT_promote_non_v6_rule(monkeypatch):
    """Rules NOT in V6 blocking set keep their default severity even in hard mode."""
    monkeypatch.setenv(_ENV_FLAG, "1")
    assert effective_severity(
        "motor_055", "HD3_tad_convergence", "informational"
    ) == "informational"


def test_effective_severity_per_pipeline_override(monkeypatch):
    """Pipeline can locally enable hard mode without env."""
    monkeypatch.delenv(_ENV_FLAG, raising=False)
    inputs = {"__validators_hard_block__": True}
    assert effective_severity(
        "motor_061", "asset_family_contamination_critical", "warning",
        pipeline_inputs=inputs,
    ) == "blocking"


def test_effective_severity_pipeline_soft_mode_keeps_default(monkeypatch):
    monkeypatch.setenv(_ENV_FLAG, "1")
    inputs = {"__validators_soft_mode__": True}
    # Env says hard but pipeline says soft → soft wins
    assert effective_severity(
        "motor_061", "asset_family_contamination_critical", "warning",
        pipeline_inputs=inputs,
    ) == "warning"


# ── list_v6_blocking_rules ──────────────────────────────────────────


def test_list_blocking_rules_returns_sorted_pairs():
    rules = list_v6_blocking_rules()
    assert len(rules) > 0
    assert rules == sorted(rules)
    # Each entry is a (motor_id, rule_id) tuple
    for entry in rules:
        assert isinstance(entry, tuple)
        assert len(entry) == 2
        motor_id, rule_id = entry
        assert motor_id.startswith("motor_")
        assert rule_id


def test_list_blocking_rules_covers_target_motors():
    """The V6 set must cover the contamination-priority motors."""
    rules = list_v6_blocking_rules()
    motors = {r[0] for r in rules}
    expected_motors = {"motor_055", "motor_056", "motor_057", "motor_058",
                        "motor_059", "motor_061", "motor_062", "motor_063"}
    assert expected_motors.issubset(motors), (
        f"V6 blocking set missing motors: {expected_motors - motors}"
    )
