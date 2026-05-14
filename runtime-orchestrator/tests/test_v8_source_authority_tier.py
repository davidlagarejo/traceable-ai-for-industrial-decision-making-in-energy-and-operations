"""V8 P6 — Source Authority Tier classification tests."""
from __future__ import annotations

import pytest

from runtime_orchestrator.source_execution_auditor import (
    SourceAuthorityTier,
    SourceGap,
    SourceExecutionAuditReport,
    audit_source_execution,
    classify_source_authority,
    client_safe_compatible,
)


# ── classify_source_authority ──────────────────────────────────────


def test_identity_tier_classification():
    assert classify_source_authority("sec_edgar_2024") == SourceAuthorityTier.IDENTITY
    assert classify_source_authority("county_assessor_tx") == SourceAuthorityTier.IDENTITY
    assert classify_source_authority("property_record_dallas") == SourceAuthorityTier.IDENTITY


def test_permit_emissions_tier_classification():
    assert classify_source_authority("epa_air_permits_2024") == SourceAuthorityTier.PERMIT_EMISSIONS
    assert classify_source_authority("npdes_wastewater_us") == SourceAuthorityTier.PERMIT_EMISSIONS
    assert classify_source_authority("state_environmental_tx") == SourceAuthorityTier.PERMIT_EMISSIONS
    assert classify_source_authority("tceq_compliance") == SourceAuthorityTier.PERMIT_EMISSIONS


def test_benchmark_tier_classification():
    assert classify_source_authority("energystar_pm_2024") == SourceAuthorityTier.BENCHMARK
    assert classify_source_authority("cbecs_2018") == SourceAuthorityTier.BENCHMARK
    assert classify_source_authority("mecs_2018") == SourceAuthorityTier.BENCHMARK


def test_reference_tier_classification():
    assert classify_source_authority("iiar_bulletin_109") == SourceAuthorityTier.REFERENCE
    assert classify_source_authority("ashrae_handbook_refrig") == SourceAuthorityTier.REFERENCE
    assert classify_source_authority("eia_923_2024") == SourceAuthorityTier.REFERENCE


def test_unknown_prefix_is_OTHER():
    assert classify_source_authority("random_unknown_source") == SourceAuthorityTier.OTHER


def test_empty_source_key_is_OTHER():
    assert classify_source_authority("") == SourceAuthorityTier.OTHER
    assert classify_source_authority(None) == SourceAuthorityTier.OTHER  # type: ignore


# ── SourceGap tier + blocks_client_safe ───────────────────────────


def test_audit_marks_identity_gap_as_blocking():
    report = audit_source_execution(
        routing_plan_compliance={
            "total_routed_sources": 2,
            "mandatory_sources_missing_from_executor": [
                "sec_edgar_2024", "energystar_pm_2024",
            ],
            "rows": [
                {"source_key": "sec_edgar_2024", "priority": "mandatory",
                 "status": "not_executed_by_executor"},
                {"source_key": "energystar_pm_2024", "priority": "mandatory",
                 "status": "not_executed_by_executor"},
            ],
        },
    )
    identity_gaps = [g for g in report.unjustified_gaps
                     if g.authority_tier == "identity"]
    benchmark_gaps = [g for g in report.unjustified_gaps
                      if g.authority_tier == "benchmark"]
    assert len(identity_gaps) == 1
    assert identity_gaps[0].blocks_client_safe is True
    assert len(benchmark_gaps) == 1
    assert benchmark_gaps[0].blocks_client_safe is False


# ── client_safe_compatible helper ─────────────────────────────────


def test_client_safe_compatible_returns_true_when_only_benchmark_gaps():
    report = audit_source_execution(
        routing_plan_compliance={
            "total_routed_sources": 1,
            "mandatory_sources_missing_from_executor": ["energystar_pm_2024"],
            "rows": [{"source_key": "energystar_pm_2024", "priority": "mandatory",
                      "status": "not_executed_by_executor"}],
        },
    )
    compatible, reasons = client_safe_compatible(report)
    assert compatible is True
    assert reasons == []


def test_client_safe_compatible_returns_false_for_identity_gap():
    report = audit_source_execution(
        routing_plan_compliance={
            "total_routed_sources": 1,
            "mandatory_sources_missing_from_executor": ["sec_edgar_2024"],
            "rows": [{"source_key": "sec_edgar_2024", "priority": "mandatory",
                      "status": "not_executed_by_executor"}],
        },
    )
    compatible, reasons = client_safe_compatible(report)
    assert compatible is False
    assert any("identity-tier" in r for r in reasons)


def test_client_safe_compatible_returns_false_for_permit_gap():
    report = audit_source_execution(
        routing_plan_compliance={
            "total_routed_sources": 1,
            "mandatory_sources_missing_from_executor": ["epa_air_permits"],
            "rows": [{"source_key": "epa_air_permits", "priority": "mandatory",
                      "status": "not_executed_by_executor"}],
        },
    )
    compatible, reasons = client_safe_compatible(report)
    assert compatible is False
    assert any("permit_emissions-tier" in r for r in reasons)


def test_client_safe_compatible_when_no_gaps():
    report = audit_source_execution(routing_plan_compliance={})
    compatible, reasons = client_safe_compatible(report)
    assert compatible is True


# ── render_gate integration ───────────────────────────────────────


def test_render_gate_refuses_identity_gap_in_strict_mode(monkeypatch):
    from runtime_orchestrator.render_gate import evaluate_render_gate
    from runtime_orchestrator.qa_score import build_qa_score_card
    monkeypatch.setenv("ZLAB_RENDER_STRICT_DEFAULT", "1")
    src = audit_source_execution(
        routing_plan_compliance={
            "total_routed_sources": 1,
            "mandatory_sources_missing_from_executor": ["sec_edgar_2024"],
            "rows": [{"source_key": "sec_edgar_2024", "priority": "mandatory",
                      "status": "not_executed_by_executor"}],
        },
    )
    card = build_qa_score_card(
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
    verdict = evaluate_render_gate(
        state="client_safe", qa_card=card, source_audit=src,
    )
    assert verdict.allowed is False
    assert verdict.no_unjustified_sources is False
    assert any("identity-tier" in r for r in verdict.reasons)
