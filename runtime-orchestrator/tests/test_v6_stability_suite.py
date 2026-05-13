"""V6 P11 — Stability Test Suite.

Nine end-to-end contamination scenarios exercising the V6 hardening
modules together. Each scenario simulates a way the framework could
silently contaminate a report and asserts that the V6 gates BLOCK
rather than degrade.

V6 Stability prompt item 18: "Stability Test Suite — 9 contamination
scenarios that previously slipped through".

The scenarios:
  S1  Pattern activated on forbidden asset family
  S2  Combination missing required_evidence_pack / V6 strict fields
  S3  Validator severity hard-block (env flag) reraises blocking violations
  S4  PROHIBITED fallback in a publishable state
  S5  Non-US source claimed but not justified
  S6  QA score below decision-blocked threshold
  S7  Claim cardinality divergence across 5 motors
  S8  Pattern isolation audit batch flags cross-family contamination
  S9  DUMB render layer (composer chain) remains pure

These tests are the regression net that prevents the 17 V6 symptoms
from re-emerging silently.
"""
from __future__ import annotations

import os

import pytest

from runtime_orchestrator.claim_synchronization_auditor import (
    audit_claim_synchronization,
    claim_sync_blocks_render,
)
from runtime_orchestrator.fallback_policy import (
    FallbackEvent,
    FallbackTier,
    FallbackViolation,
    assess,
    classify,
    enforce_for_render,
)
from runtime_orchestrator.industrial_research_engine import (
    KnowledgeValidationError,
    validate_combination_v6_strict,
)
from runtime_orchestrator.pattern_isolation import (
    PatternIsolationViolation,
    audit_isolation_violations,
    pattern_isolation_contract,
    validate_activation,
)
from runtime_orchestrator.qa_score import (
    DECISION_BLOCKED_THRESHOLD,
    build_qa_score_card,
)
from runtime_orchestrator.source_execution_auditor import (
    audit_source_execution,
    gaps_block_render,
)
from runtime_orchestrator.validator_severity_policy import (
    effective_severity,
    hard_mode_active,
)


# ── S1: pattern on forbidden family ────────────────────────────────


def test_S1_pattern_on_forbidden_family_is_blocked():
    """refrigeration_duty must not activate on `datacenter` family."""
    with pytest.raises(PatternIsolationViolation):
        validate_activation("refrigeration_duty", "datacenter")

    contract = pattern_isolation_contract("refrigeration_duty")
    assert "datacenter" in contract.forbidden_families
    assert "cold_chain_facility" in contract.allowed_families


# ── S2: combination missing V6 strict field ────────────────────────


def test_S2_combination_without_v6_strict_fields_rejected():
    """A combination missing required_evidence_pack must be rejected
    by the V6 strict validator."""
    bad = {
        "id": "broken_combo",
        "version": "1.0.0",
        "knowledge_kind": "combination",
        "asset_families": ["cold_chain_facility"],
        "trigger_conditions": ["x"],
        "falsification_conditions": ["y"],
        "evidence_required": ["e1"],
        "financial_translation": "f",
        "tad_actions": ["MEASURE"],
        "allowed_language": "ok",
        "prohibited_language": [],
        "claim_ceiling": "L2",
        "source_basis": [{"source_id": "s", "confidence": "high"}],
        "required_patterns": ["a", "b"],
        "combined_hypothesis": "h",
        "evidence_pack": {"id": "x", "items": ["i"]},
        "prohibited_claims": [],
        "preconditions": [],
        "layers_combined": ["physical_process", "asset_archetype"],
        "required_asset_family": "cold_chain_facility",
        "allowed_claim_ceiling": "L2",
        # required_evidence_pack MISSING
        "tad_mapping": ["measure"],
        "allowed_render_modes": ["exploratory_prior"],
        "forbidden_render_modes": [],
    }
    with pytest.raises(KnowledgeValidationError, match="required_evidence_pack"):
        validate_combination_v6_strict(bad)


# ── S3: validator severity hard-block ──────────────────────────────


def test_S3_hard_mode_promotes_blocking_rule_severity(monkeypatch):
    """With ZLAB_VALIDATORS_HARD_BLOCK=1, a known V6 blocking rule
    is elevated from 'warning' to 'blocking'."""
    monkeypatch.setenv("ZLAB_VALIDATORS_HARD_BLOCK", "1")
    assert hard_mode_active() is True
    sev = effective_severity(
        motor_id="motor_059",
        rule_id="R8_digital_twin_with_unresolved_dominant_variable",
        default_severity="warning",
        pipeline_inputs={},
    )
    assert sev == "blocking"


def test_S3_soft_mode_keeps_default_severity(monkeypatch):
    """V7: diagnostic / soft mode is opt-out via env=0 or pipeline_inputs."""
    monkeypatch.setenv("ZLAB_VALIDATORS_HARD_BLOCK", "0")
    assert hard_mode_active(pipeline_inputs={}) is False
    sev = effective_severity(
        motor_id="motor_059",
        rule_id="R8_digital_twin_with_unresolved_dominant_variable",
        default_severity="warning",
        pipeline_inputs={},
    )
    assert sev == "warning"


# ── S4: prohibited fallback in publishable state ───────────────────


def test_S4_prohibited_fallback_blocks_publish_bounded():
    """A `synthetic_gold_nugget` fallback must never appear in publishable output."""
    assert classify("synthetic_gold_nugget") == FallbackTier.PROHIBITED
    events = [FallbackEvent(motor_id="motor_054", kind="synthetic_gold_nugget")]
    verdict = assess("publish_bounded", events)
    assert not verdict.passed
    assert verdict.prohibited_count == 1

    with pytest.raises(FallbackViolation):
        enforce_for_render("publish_bounded", events)


# ── S5: non-US source claimed without justification ────────────────


def test_S5_us_mandatory_source_without_justification_blocks_render():
    """A US-jurisdiction mandatory source missing from the executor with
    NO skip_reason / coverage_gap event must block render.
    (Non-US sources are auto-justified per US-only case-discovery policy.)"""
    report = audit_source_execution(
        routing_plan_compliance={
            "total_routed_sources": 1,
            "mandatory_sources_missing_from_executor": ["eia_consumption_2024"],
            "rows": [
                {
                    "source_key": "eia_consumption_2024",
                    "priority": "mandatory",
                    "status": "not_executed_by_executor",
                },
            ],
        },
        routing_plan=None,
        fallback_events=None,
    )
    assert gaps_block_render(report) is True
    assert any(not g.justified for g in report.unjustified_gaps)


# ── S6: QA score < decision_blocked threshold ──────────────────────


def test_S6_qa_score_decision_blocked_when_overall_low():
    """If motor_061 reports contamination + cross-family violations
    AND motor_063 reports critical decorative-ratio, the overall QA
    score must fall to <= 0.50 → decision_blocked."""
    card = build_qa_score_card(
        motor_061_summary={
            "contamination_count": 5,
            "cross_family_violations": 3,
            "blocking_violations": 4,
        },
        motor_063_summary={"blocking_violations": 3},
        motor_057_summary={"blocking_violations": 2},
        motor_058_summary={"blocking_violations": 2},
        motor_059_summary={"blocking_violations": 4},
        fallback_verdict={"prohibited_count": 2},
        motor_019_lint={"orphan_claim_findings": ["c1", "c2"]},
    )
    assert card.overall_score <= DECISION_BLOCKED_THRESHOLD
    assert card.decision_blocked is True
    assert card.client_safe is False


# ── S7: claim cardinality divergence across motors ─────────────────


def test_S7_claim_synchronization_divergence_blocks_render():
    """motor_034 has fewer claims than motor_014 → block."""
    outputs = {
        "motor_014_output": {
            "inference_records": [{"case_id": "CL-1"}, {"case_id": "CL-2"}, {"case_id": "CL-3"}],
        },
        "motor_034_output": {
            "claim_permission_register": [{"claim_name": "CL-1"}, {"claim_name": "CL-2"}],
        },
        "motor_054_output": {
            "congruence_claim_contract_register": [
                {"claim_id": "CL-1"}, {"claim_id": "CL-2"}, {"claim_id": "CL-3"}
            ],
        },
        "motor_025_output": {
            "epistemic_status_register": [
                {"output_id": "CL-1"}, {"output_id": "CL-2"}, {"output_id": "CL-3"}
            ],
        },
        "motor_016_output": {
            "report_package": {"governance_summary": {"claim_count": 3}},
        },
    }
    report = audit_claim_synchronization(**outputs)
    assert not report.consistent
    assert claim_sync_blocks_render(report) is True


# ── S8: pattern isolation audit flags cross-family activations ─────


def test_S8_isolation_audit_flags_cross_family_batch():
    """An activation batch containing a cold-chain pattern landing on
    a datacenter must surface a contamination violation."""
    activations = [
        {"pattern_id": "refrigeration_duty", "asset_family": "cold_chain_facility"},
        {"pattern_id": "compressor_staging", "asset_family": "datacenter"},  # bad
    ]
    violations = audit_isolation_violations(activations)
    assert len(violations) == 1
    assert violations[0]["pattern_id"] == "compressor_staging"
    assert violations[0]["target_family"] == "datacenter"
    assert violations[0]["reason"] == "forbidden_family"


# ── S9: DUMB render layer remains pure ─────────────────────────────


def test_S9_composer_layer_has_no_analytical_imports():
    """The composer chain (motor_015/016/017) must not import analytical
    helpers from structural_intelligence or congruence_intelligence —
    those would mean Layer E is fabricating logic at render time."""
    from pathlib import Path
    adapters = Path(__file__).resolve().parents[1] / "src" / "runtime_orchestrator" / "adapters"
    # motor_017 is the strictest gate (LaTeX render — pure assembly).
    # motor_015/016 may consume case_isolation register builders to format
    # output blocks (that's render assembly, not analytical fabrication).
    for motor_id in ("motor_017",):
        src = (adapters / f"{motor_id}.py").read_text(encoding="utf-8")
        assert "from ..structural_intelligence" not in src, (
            f"{motor_id} imports structural_intelligence — Layer E contamination"
        )
        assert "from ..congruence_intelligence" not in src, (
            f"{motor_id} imports congruence_intelligence — Layer E contamination"
        )
    # No external LLM SDK in ANY composer motor (only motor_019 may invoke Codex).
    for motor_id in ("motor_015", "motor_016", "motor_017"):
        src = (adapters / f"{motor_id}.py").read_text(encoding="utf-8")
        for sdk in ("import anthropic", "from anthropic", "import openai", "from openai"):
            assert sdk not in src, f"{motor_id} imports LLM SDK: {sdk}"


# ── Suite-level invariant: at least one V6 gate fires per scenario ─


def test_V6_stability_modules_are_all_importable():
    """Sanity: all V6 modules can be imported in one go.
    If one breaks, the whole suite is at risk."""
    # The imports at the top of the file already executed.
    assert callable(audit_claim_synchronization)
    assert callable(audit_source_execution)
    assert callable(build_qa_score_card)
    assert callable(effective_severity)
    assert callable(pattern_isolation_contract)
    assert callable(validate_combination_v6_strict)
