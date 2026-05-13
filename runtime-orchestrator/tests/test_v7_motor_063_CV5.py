"""V7 P7 — motor_063 CV5 chart cross-asset-family contamination."""
from __future__ import annotations

import pytest

from runtime_orchestrator.adapters.motor_063 import (
    Motor063Adapter,
    _detect_CV5_chart_cross_asset_family,
)
from runtime_orchestrator.validator_severity_policy import is_v6_blocking_rule


@pytest.fixture(autouse=True)
def _force_soft_mode(monkeypatch):
    monkeypatch.setenv("ZLAB_VALIDATORS_HARD_BLOCK", "0")


def _run(target_family: str, charts: list[dict]):
    return Motor063Adapter().run({
        "motor_007": {"target_definition_contract": {"asset_family": target_family}},
        "motor_018": {"chart_assets": charts,
                      "chart_strategic_value_summary": {}},
        "motor_047": {"executive_thesis": {"thesis_state": "exploratory"}},
    })


# ── Unit: _detect_CV5 helper ───────────────────────────────────────


def test_CV5_flags_chart_bound_to_different_family():
    charts = [
        {"chart_id": "CHT-1",
         "intelligence_binding": {"asset_family": "commercial_building"}},
    ]
    out = _detect_CV5_chart_cross_asset_family(charts, "cold_chain_facility")
    assert len(out) == 1
    assert out[0]["chart_id"] == "CHT-1"
    assert out[0]["bound_asset_family"] == "commercial_building"
    assert out[0]["target_asset_family"] == "cold_chain_facility"


def test_CV5_silent_when_chart_family_matches():
    charts = [
        {"chart_id": "CHT-1",
         "intelligence_binding": {"asset_family": "cold_chain_facility"}},
    ]
    out = _detect_CV5_chart_cross_asset_family(charts, "cold_chain_facility")
    assert out == []


def test_CV5_silent_when_chart_has_no_binding():
    """CV2 covers unbound charts; CV5 only fires on bound+mismatch."""
    charts = [{"chart_id": "CHT-1", "intelligence_binding": {}}]
    out = _detect_CV5_chart_cross_asset_family(charts, "cold_chain_facility")
    assert out == []


def test_CV5_silent_when_target_family_unknown():
    """Cannot judge contamination without a target context."""
    charts = [
        {"chart_id": "CHT-1",
         "intelligence_binding": {"asset_family": "office"}},
    ]
    out = _detect_CV5_chart_cross_asset_family(charts, "")
    assert out == []


def test_CV5_reads_alternate_binding_keys():
    charts = [
        {"chart_id": "CHT-1",
         "chart_intelligence_binding": {"asset_family": "manufacturing_facility"}},
        {"chart_id": "CHT-2",
         "intelligence_binding": {"asset_type": "manufacturing_facility"}},
        {"chart_id": "CHT-3",
         "intelligence_binding": {"target_family": "manufacturing_facility"}},
    ]
    out = _detect_CV5_chart_cross_asset_family(charts, "warehouse_distribution")
    assert len(out) == 3


def test_CV5_case_insensitive_match():
    charts = [
        {"chart_id": "CHT-1",
         "intelligence_binding": {"asset_family": "COLD_CHAIN_FACILITY"}},
    ]
    out = _detect_CV5_chart_cross_asset_family(charts, "cold_chain_facility")
    assert out == []


# ── Integration: motor_063 emits CV5 ───────────────────────────────


def test_motor_063_surfaces_CV5_warning():
    out = _run(
        target_family="warehouse_distribution",
        charts=[
            {"chart_id": "CHT-1",
             "intelligence_binding": {"asset_family": "cold_chain_facility",
                                       "claim_id": "c1"}},
        ],
    )
    cv5 = [w for w in out["chart_validity_warnings"]
           if w["rule_id"] == "CV5_chart_cross_asset_family"]
    assert len(cv5) == 1


def test_motor_063_lists_CV5_in_rules_evaluated():
    out = _run(target_family="warehouse_distribution", charts=[])
    assert "CV5_chart_cross_asset_family" in out["rules_evaluated"]


# ── V6 blocking set + hard mode promotion ──────────────────────────


def test_CV5_in_v6_blocking_set():
    assert is_v6_blocking_rule("motor_063", "CV5_chart_cross_asset_family")


def test_CV5_promotes_to_blocking_in_hard_mode(monkeypatch):
    monkeypatch.setenv("ZLAB_VALIDATORS_HARD_BLOCK", "1")
    out = _run(
        target_family="cold_chain_facility",
        charts=[{"chart_id": "CHT-1",
                 "intelligence_binding": {"asset_family": "datacenter",
                                          "claim_id": "c1"}}],
    )
    cv5 = [w for w in out["chart_validity_warnings"]
           if w["rule_id"] == "CV5_chart_cross_asset_family"]
    assert cv5 and cv5[0]["severity"] == "blocking"
