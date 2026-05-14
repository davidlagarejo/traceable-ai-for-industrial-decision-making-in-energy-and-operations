"""V9 P4 — Final Architectural Stability Suite.

4 contamination scenarios + 1 control, exercising every V9 hardening
together (Fair Comparison 10-dim + CV7/CV8 chart + Industry Onboarding).

  S0 Clean peer set + clean charts + ready industry → allows
  S1 Incomplete 10-dim peer set                     → refuses
  S2 Chart sin section_id (CV7)                     → refuses
  S3 Chart sin hypothesis_supported (CV8)           → refuses
  S4 Industry onboarding incomplete                 → validate rejects
"""
from __future__ import annotations

import pytest

from runtime_orchestrator.adapters.motor_063 import Motor063Adapter
from runtime_orchestrator.fair_comparison import (
    evaluate_peer_set,
    peer_set_admissible,
)
from runtime_orchestrator.industry_onboarding import (
    validate_industry_readiness,
)
from runtime_orchestrator.qa_score import build_qa_score_card
from runtime_orchestrator.render_gate import evaluate_render_gate


@pytest.fixture(autouse=True)
def _v9_hard_mode(monkeypatch):
    monkeypatch.setenv("ZLAB_RENDER_STRICT_DEFAULT", "1")
    monkeypatch.setenv("ZLAB_VALIDATORS_HARD_BLOCK", "1")


def _clean_qa_card():
    return build_qa_score_card(
        consistency_summary={"can_render_pdf": True, "critical_failures": 0},
        fallback_verdict={"prohibited_count": 0, "passed": True},
        motor_019_lint={"orphan_claim_findings": [], "unsupported_numeric_tokens": []},
        motor_061_summary={"contamination_count": 0, "cross_family_violations": 0,
                           "blocking_violations": 0},
        motor_063_summary={"blocking_violations": 0},
        motor_057_summary={"blocking_violations": 0},
        motor_058_summary={"blocking_violations": 0},
        motor_059_summary={"blocking_violations": 0},
        state_machine_state="client_safe",
        source_audit_passed=True,
    )


def _complete_profile(id_: str = "x", **overrides) -> dict:
    base = {
        "id": id_,
        "asset_family": "cold_chain_facility",
        "process_family": "refrigeration",
        "thermal_regime": "refrigerated",
        "throughput_band": "medium",
        "operating_hours": "24x7",
        "dock_density": "high",
        "charging_profile": "overnight",
        "tariff_profile": "demand_billed",
        "control_boundary": "owner_operator",
        "regulatory_context": "iiar",
    }
    base.update(overrides)
    return base


def _ready_industry_spec() -> dict:
    return {
        "industry_id": "thermal_process_demo",
        "process_taxonomy": ["cook", "pasteurize"],
        "machine_taxonomy": ["boiler", "steam_trap"],
        "dominant_variables": ["process_heat_duty"],
        "failure_modes": ["boiler_degradation"],
        "evidence_map": {"h1": ["boiler runtime log"]},
        "financial_translation": "process heat → CAPEX target",
        "regulatory_triggers": ["EPA NESHAP"],
        "combinations": ["process_heat_unbounded_duty_combo"],
        "tad_mapping": ["A1", "A2", "A3"],
        "qa_tests": ["t1"],
    }


# ── S0 — Clean control ────────────────────────────────────────────


def test_S0_clean_run_emits_client_safe():
    # Fair comparison: full 10-dim peer set
    candidate = _complete_profile("candidate")
    peers = [_complete_profile("peer_1"), _complete_profile("peer_2")]
    fc_verdict = evaluate_peer_set(candidate, peers)
    assert peer_set_admissible(fc_verdict) is True
    # Charts: properly bound
    out_063 = Motor063Adapter().run({
        "motor_007": {"target_definition_contract": {
            "asset_family": "cold_chain_facility", "case_id": "CASE_X",
        }},
        "motor_018": {"chart_assets": [
            {"chart_id": "CHT-1",
             "intelligence_binding": {
                 "section_id": "executive_thesis",
                 "hypothesis_supported": "refrigeration_duty",
                 "asset_family": "cold_chain_facility",
                 "source_case_id": "CASE_X",
             }},
        ], "chart_strategic_value_summary": {}},
        "motor_047": {"executive_thesis": {"thesis_state": "exploratory"}},
    })
    assert out_063["blocking_violations"] == 0
    # Industry: ready
    iv = validate_industry_readiness(_ready_industry_spec())
    assert iv.ready is True
    # Final gate: clean
    gate = evaluate_render_gate(state="client_safe", qa_card=_clean_qa_card())
    assert gate.allowed is True
    assert gate.publication_mode() == "client_safe"


# ── S1 — Incomplete 10-dim peer set → refuses ranking ────────────


def test_S1_incomplete_peer_set_refuses_ranking():
    candidate = _complete_profile("candidate")
    incomplete_peer = _complete_profile("peer_x")
    del incomplete_peer["regulatory_context"]  # 9/10
    del incomplete_peer["control_boundary"]    # 8/10
    del incomplete_peer["dock_density"]        # 7/10
    verdict = evaluate_peer_set(candidate, [incomplete_peer])
    assert verdict.peer_set_admissible is False
    assert len(verdict.rejected_peers) == 1


# ── S2 — Chart without section_id (CV7) → fails motor_063 ────────


def test_S2_chart_without_section_id_emits_CV7():
    out = Motor063Adapter().run({
        "motor_007": {"target_definition_contract": {
            "asset_family": "cold_chain_facility", "case_id": "CASE_X",
        }},
        "motor_018": {"chart_assets": [
            {"chart_id": "CHT-1",
             "intelligence_binding": {
                 "hypothesis_supported": "refrigeration_duty",
                 # section_id missing
             }},
        ], "chart_strategic_value_summary": {}},
        "motor_047": {"executive_thesis": {"thesis_state": "exploratory"}},
    })
    cv7 = [w for w in out["chart_validity_warnings"]
           if w["rule_id"] == "CV7_chart_without_section_id"]
    assert len(cv7) == 1
    assert out["blocking_violations"] >= 1


# ── S3 — Chart without hypothesis_supported (CV8) ────────────────


def test_S3_chart_without_hypothesis_supported_emits_CV8():
    out = Motor063Adapter().run({
        "motor_007": {"target_definition_contract": {
            "asset_family": "cold_chain_facility", "case_id": "CASE_X",
        }},
        "motor_018": {"chart_assets": [
            {"chart_id": "CHT-1",
             "intelligence_binding": {
                 "section_id": "tad",
                 # hypothesis_supported / claim_id missing
             }},
        ], "chart_strategic_value_summary": {}},
        "motor_047": {"executive_thesis": {"thesis_state": "exploratory"}},
    })
    cv8 = [w for w in out["chart_validity_warnings"]
           if w["rule_id"] == "CV8_chart_without_hypothesis_supported"]
    assert len(cv8) == 1


# ── S4 — Industry onboarding incomplete → rejects ────────────────


def test_S4_industry_incomplete_rejects():
    spec = _ready_industry_spec()
    spec["combinations"] = []
    spec["tad_mapping"] = ["A1"]  # below ≥3 threshold
    spec["qa_tests"] = []
    v = validate_industry_readiness(spec)
    assert v.ready is False
    assert "combinations" in v.missing_requirements
    assert "tad_mapping" in v.missing_requirements
    assert "qa_tests" in v.missing_requirements
    assert len(v.blocking_reasons) == 3
