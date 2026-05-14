"""V8 P2 — motor_063 CV6 chart wrong source_case_id provenance.

Chief QA Architect § Error 2 + § B: a chart whose intelligence_binding
declares `source_case_id` belonging to ANOTHER case must be blocked,
unless explicitly marked `reusable_generic=True`.

V7 P7 (CV5) covers cross-asset-family chart leaks.
V8 P2 (CV6) covers same-family-different-case leaks (e.g., warehouse
Austin's dock chart appearing in warehouse Memphis's report).
"""
from __future__ import annotations

import pytest

from runtime_orchestrator.adapters.motor_063 import (
    Motor063Adapter,
    _detect_CV6_chart_wrong_source_case_id,
)
from runtime_orchestrator.validator_severity_policy import is_v6_blocking_rule


@pytest.fixture(autouse=True)
def _force_soft_mode(monkeypatch):
    monkeypatch.setenv("ZLAB_VALIDATORS_HARD_BLOCK", "0")


def _run(target_case_id: str, charts: list[dict]):
    return Motor063Adapter().run({
        "motor_007": {
            "target_definition_contract": {
                "asset_family": "cold_chain_facility",
                "case_id": target_case_id,
            },
        },
        "motor_018": {"chart_assets": charts, "chart_strategic_value_summary": {}},
        "motor_047": {"executive_thesis": {"thesis_state": "exploratory"}},
    })


# ── Unit ─────────────────────────────────────────────────────────


def test_CV6_flags_chart_from_other_case():
    charts = [
        {"chart_id": "CHT-1",
         "intelligence_binding": {"source_case_id": "WAREHOUSE_AUSTIN_2024"}},
    ]
    out = _detect_CV6_chart_wrong_source_case_id(charts, "WAREHOUSE_MEMPHIS_2026")
    assert len(out) == 1
    assert out[0]["chart_id"] == "CHT-1"
    assert out[0]["source_case_id"] == "warehouse_austin_2024"
    assert out[0]["target_case_id"] == "WAREHOUSE_MEMPHIS_2026"


def test_CV6_silent_when_case_matches():
    charts = [
        {"chart_id": "CHT-1",
         "intelligence_binding": {"source_case_id": "WAREHOUSE_MEMPHIS_2026"}},
    ]
    out = _detect_CV6_chart_wrong_source_case_id(charts, "WAREHOUSE_MEMPHIS_2026")
    assert out == []


def test_CV6_silent_when_reusable_generic_flag_true():
    """Charts explicitly marked reusable_generic are exempt."""
    charts = [
        {"chart_id": "CHT-1",
         "intelligence_binding": {
             "source_case_id": "WAREHOUSE_AUSTIN_2024",
             "reusable_generic": True,
         }},
    ]
    out = _detect_CV6_chart_wrong_source_case_id(charts, "WAREHOUSE_MEMPHIS_2026")
    assert out == []


def test_CV6_silent_when_no_source_case_declared():
    """A chart without source_case_id is unbound; CV2 covers that."""
    charts = [{"chart_id": "CHT-1", "intelligence_binding": {}}]
    out = _detect_CV6_chart_wrong_source_case_id(charts, "WAREHOUSE_MEMPHIS_2026")
    assert out == []


def test_CV6_silent_when_no_target_case_context():
    """If we don't know the target case, we cannot judge."""
    charts = [
        {"chart_id": "CHT-1",
         "intelligence_binding": {"source_case_id": "ANY_CASE"}},
    ]
    out = _detect_CV6_chart_wrong_source_case_id(charts, "")
    assert out == []


def test_CV6_case_insensitive_match():
    charts = [
        {"chart_id": "CHT-1",
         "intelligence_binding": {"source_case_id": "CASE_X_2026"}},
    ]
    out = _detect_CV6_chart_wrong_source_case_id(charts, "case_x_2026")
    assert out == []


# ── Integration ──────────────────────────────────────────────────


def test_motor_063_surfaces_CV6_warning():
    out = _run(
        target_case_id="CURRENT_CASE_2026",
        charts=[
            {"chart_id": "CHT-1",
             "intelligence_binding": {"source_case_id": "OTHER_CASE_2025",
                                       "claim_id": "c1"}},
        ],
    )
    cv6 = [w for w in out["chart_validity_warnings"]
           if w["rule_id"] == "CV6_chart_wrong_source_case_id"]
    assert len(cv6) == 1


def test_motor_063_lists_CV6_in_rules_evaluated():
    out = _run("CASE_X", [])
    assert "CV6_chart_wrong_source_case_id" in out["rules_evaluated"]


# ── V6 blocking set + hard mode promotion ─────────────────────────


def test_CV6_in_v6_blocking_set():
    assert is_v6_blocking_rule("motor_063", "CV6_chart_wrong_source_case_id")


def test_CV6_promotes_to_blocking_in_hard_mode(monkeypatch):
    monkeypatch.setenv("ZLAB_VALIDATORS_HARD_BLOCK", "1")
    out = _run(
        target_case_id="CASE_A",
        charts=[
            {"chart_id": "CHT-1",
             "intelligence_binding": {"source_case_id": "CASE_B"}},
        ],
    )
    cv6 = [w for w in out["chart_validity_warnings"]
           if w["rule_id"] == "CV6_chart_wrong_source_case_id"]
    assert cv6 and cv6[0]["severity"] == "blocking"
