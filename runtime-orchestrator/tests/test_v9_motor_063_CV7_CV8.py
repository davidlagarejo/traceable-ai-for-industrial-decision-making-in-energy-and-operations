"""V9 P2 — motor_063 CV7 (section_id) + CV8 (hypothesis_supported) tests."""
from __future__ import annotations

import pytest

from runtime_orchestrator.adapters.motor_063 import (
    Motor063Adapter,
    _detect_CV7_chart_without_section_id,
    _detect_CV8_chart_without_hypothesis_supported,
)
from runtime_orchestrator.validator_severity_policy import is_v6_blocking_rule


@pytest.fixture(autouse=True)
def _force_soft_mode(monkeypatch):
    monkeypatch.setenv("ZLAB_VALIDATORS_HARD_BLOCK", "0")


def _run(charts: list[dict]):
    return Motor063Adapter().run({
        "motor_007": {"target_definition_contract": {
            "asset_family": "cold_chain_facility",
            "case_id": "CASE_X",
        }},
        "motor_018": {"chart_assets": charts, "chart_strategic_value_summary": {}},
        "motor_047": {"executive_thesis": {"thesis_state": "exploratory"}},
    })


# ── CV7 section_id ────────────────────────────────────────────────


def test_CV7_flags_chart_without_section_id():
    charts = [
        {"chart_id": "CHT-1",
         "intelligence_binding": {"claim_id": "c1"}},  # no section_id
    ]
    out = _detect_CV7_chart_without_section_id(charts)
    assert len(out) == 1
    assert out[0]["rule_id"] == "CV7_chart_without_section_id"
    assert out[0]["chart_id"] == "CHT-1"


def test_CV7_silent_when_section_id_present():
    charts = [
        {"chart_id": "CHT-1",
         "intelligence_binding": {"section_id": "executive_thesis", "claim_id": "c1"}},
    ]
    assert _detect_CV7_chart_without_section_id(charts) == []


def test_CV7_silent_when_truly_unbound():
    """CV2 covers fully-unbound charts; CV7 only fires when binding exists."""
    charts = [{"chart_id": "CHT-1", "intelligence_binding": {}}]
    assert _detect_CV7_chart_without_section_id(charts) == []


def test_CV7_accepts_alt_field_names():
    charts = [
        {"chart_id": "CHT-1",
         "intelligence_binding": {"section": "tad"}},
        {"chart_id": "CHT-2",
         "intelligence_binding": {"output_block_id": "tad"}},
    ]
    # Both should be considered "having section_id"
    assert _detect_CV7_chart_without_section_id(charts) == []


# ── CV8 hypothesis_supported ──────────────────────────────────────


def test_CV8_flags_chart_without_hypothesis_supported():
    charts = [
        {"chart_id": "CHT-1",
         "intelligence_binding": {"section_id": "tad"}},  # no hypothesis
    ]
    out = _detect_CV8_chart_without_hypothesis_supported(charts)
    assert len(out) == 1
    assert out[0]["rule_id"] == "CV8_chart_without_hypothesis_supported"


def test_CV8_silent_when_claim_id_present():
    charts = [
        {"chart_id": "CHT-1",
         "intelligence_binding": {"section_id": "tad", "claim_id": "c1"}},
    ]
    assert _detect_CV8_chart_without_hypothesis_supported(charts) == []


def test_CV8_silent_when_hypothesis_supported_present():
    charts = [
        {"chart_id": "CHT-1",
         "intelligence_binding": {"section_id": "tad",
                                   "hypothesis_supported": "refrigeration_duty"}},
    ]
    assert _detect_CV8_chart_without_hypothesis_supported(charts) == []


# ── Integration motor_063 ─────────────────────────────────────────


def test_motor_063_surfaces_CV7_and_CV8():
    out = _run(charts=[
        {"chart_id": "CHT-1",
         "intelligence_binding": {"claim_id": "c1"}},  # missing section_id
        {"chart_id": "CHT-2",
         "intelligence_binding": {"section_id": "tad"}},  # missing hypothesis
    ])
    rule_ids = [w["rule_id"] for w in out["chart_validity_warnings"]]
    assert "CV7_chart_without_section_id" in rule_ids
    assert "CV8_chart_without_hypothesis_supported" in rule_ids


def test_motor_063_lists_CV7_CV8_in_rules_evaluated():
    out = _run([])
    assert "CV7_chart_without_section_id" in out["rules_evaluated"]
    assert "CV8_chart_without_hypothesis_supported" in out["rules_evaluated"]


# ── V6 blocking set + hard mode promotion ─────────────────────────


def test_CV7_CV8_in_v6_blocking_set():
    assert is_v6_blocking_rule("motor_063", "CV7_chart_without_section_id")
    assert is_v6_blocking_rule("motor_063", "CV8_chart_without_hypothesis_supported")


def test_CV7_promotes_to_blocking_in_hard_mode(monkeypatch):
    monkeypatch.setenv("ZLAB_VALIDATORS_HARD_BLOCK", "1")
    out = _run([
        {"chart_id": "CHT-1", "intelligence_binding": {"claim_id": "c1"}},
    ])
    cv7 = [w for w in out["chart_validity_warnings"]
           if w["rule_id"] == "CV7_chart_without_section_id"]
    assert cv7 and cv7[0]["severity"] == "blocking"
