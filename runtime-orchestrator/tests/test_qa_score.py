"""V6 P3 — qa_score aggregator tests."""
from __future__ import annotations

from runtime_orchestrator.qa_score import (
    CLIENT_SAFE_THRESHOLD,
    DECISION_BLOCKED_THRESHOLD,
    QAScoreCard,
    build_qa_score_card,
)


# ── all-clean case → client_safe ────────────────────────────────────


def test_all_clean_inputs_yield_client_safe():
    card = build_qa_score_card(
        consistency_summary={"can_render_pdf": True, "critical_failure_count": 0, "warning_failure_count": 0},
        fallback_verdict={"prohibited_count": 0, "degraded_count": 0},
        motor_019_lint={"violations": [], "orphan_claim_findings": []},
        motor_025_summary={"ladder_violations": 0},
        motor_054_summary={"skill_combination_activation_count": 3},
        motor_057_summary={"blocking_violations": 0, "warning_violations": 0},
        motor_058_summary={"blocking_violations": 0, "warning_violations": 0},
        motor_059_summary={"blocking_violations": 0, "warning_violations": 0},
        motor_061_summary={"blocking_violations": 0, "warning_violations": 0,
                            "cross_family_violations": 0, "contamination_count": 0},
        motor_063_summary={"blocking_violations": 0, "warning_violations": 0},
        state_machine_state="client_safe",
        source_audit_passed=True,
    )
    assert card.client_safe
    assert not card.decision_blocked
    assert card.overall_score >= CLIENT_SAFE_THRESHOLD


# ── prohibited fallback blocks client_safe ──────────────────────────


def test_prohibited_fallback_blocks_client_safe():
    card = build_qa_score_card(
        consistency_summary={"can_render_pdf": True, "critical_failure_count": 0, "warning_failure_count": 0},
        fallback_verdict={"prohibited_count": 1},  # ← blocker
        motor_019_lint={"violations": [], "orphan_claim_findings": []},
        state_machine_state="client_safe",
    )
    assert not card.client_safe
    # decision_blocked should also flag
    assert card.decision_blocked


# ── consistency cannot_render blocks client_safe ───────────────────


def test_cannot_render_blocks_client_safe():
    card = build_qa_score_card(
        consistency_summary={"can_render_pdf": False, "critical_failure_count": 2},
        fallback_verdict={"prohibited_count": 0},
        state_machine_state="client_safe",
    )
    assert not card.client_safe


# ── source audit failed blocks client_safe ─────────────────────────


def test_source_audit_failed_blocks_client_safe():
    card = build_qa_score_card(
        consistency_summary={"can_render_pdf": True, "critical_failure_count": 0},
        fallback_verdict={"prohibited_count": 0},
        motor_019_lint={"violations": []},
        motor_054_summary={"skill_combination_activation_count": 3},
        state_machine_state="client_safe",
        source_audit_passed=False,  # ← blocker
    )
    assert not card.client_safe


# ── contamination score ─────────────────────────────────────────────


def test_contamination_score_drops_with_asset_family_violations():
    card = build_qa_score_card(
        motor_061_summary={"blocking_violations": 2, "warning_violations": 1},
        motor_063_summary={"blocking_violations": 0, "warning_violations": 0},
    )
    # 2 critical = -0.40, 1 warning = -0.05, score = 0.55
    assert card.contamination_score < 0.70
    assert card.contamination_score > 0.40


def test_contamination_score_zero_violations_is_one():
    card = build_qa_score_card(
        motor_061_summary={"blocking_violations": 0, "warning_violations": 0},
        motor_063_summary={"blocking_violations": 0, "warning_violations": 0},
    )
    assert card.contamination_score == 1.0


# ── rendering integrity score ───────────────────────────────────────


def test_rendering_integrity_drops_with_orphan_claims():
    card = build_qa_score_card(
        motor_019_lint={
            "violations": [],
            "orphan_claim_findings": [
                {"sentence_index": 0, "sentence_excerpt": "x"},
                {"sentence_index": 1, "sentence_excerpt": "y"},
                {"sentence_index": 2, "sentence_excerpt": "z"},
                {"sentence_index": 3, "sentence_excerpt": "w"},  # >3 → critical
            ],
        },
    )
    assert card.rendering_integrity_score < 0.85


def test_rendering_integrity_detects_forbidden_phrases():
    card = build_qa_score_card(
        motor_019_lint={
            "violations": [
                "forbidden_phrase:due diligence",
                "closure_phrase:verified",
            ],
            "orphan_claim_findings": [],
        },
    )
    # 2 critical → 1.0 - 0.40 = 0.60
    assert card.rendering_integrity_score < 0.75


# ── epistemic integrity ─────────────────────────────────────────────


def test_epistemic_integrity_drops_with_ladder_violations():
    card = build_qa_score_card(
        motor_059_summary={"blocking_violations": 1, "warning_violations": 0},
        motor_025_summary={"ladder_violations": 2},
    )
    assert card.epistemic_integrity_score < 0.70


# ── overall score weighted aggregation ──────────────────────────────


def test_overall_score_is_weighted_mean():
    card = build_qa_score_card(
        consistency_summary={"can_render_pdf": True, "critical_failure_count": 0, "warning_failure_count": 0},
        fallback_verdict={"prohibited_count": 0},
        motor_019_lint={"violations": [], "orphan_claim_findings": []},
        motor_025_summary={"ladder_violations": 0},
        motor_054_summary={"skill_combination_activation_count": 0},
        motor_057_summary={"blocking_violations": 0, "warning_violations": 0},
        motor_058_summary={"blocking_violations": 0, "warning_violations": 0},
        motor_059_summary={"blocking_violations": 0, "warning_violations": 0},
        motor_061_summary={"blocking_violations": 0, "warning_violations": 0},
        motor_063_summary={"blocking_violations": 0, "warning_violations": 0},
        state_machine_state="client_safe",
    )
    # All inputs perfect → overall ≈ 1.0
    assert card.overall_score >= 0.95


def test_overall_score_low_when_dimensions_degrade():
    card = build_qa_score_card(
        consistency_summary={"can_render_pdf": False, "critical_failure_count": 5},
        fallback_verdict={"prohibited_count": 0},
        motor_061_summary={"blocking_violations": 3, "warning_violations": 5},
        motor_063_summary={"blocking_violations": 2},
        motor_058_summary={"blocking_violations": 2},
    )
    assert card.overall_score < DECISION_BLOCKED_THRESHOLD


# ── decision_blocked ────────────────────────────────────────────────


def test_decision_blocked_when_overall_below_threshold():
    card = build_qa_score_card(
        consistency_summary={"can_render_pdf": True, "critical_failure_count": 10},
        motor_061_summary={"blocking_violations": 10},
    )
    assert card.decision_blocked


def test_decision_not_blocked_when_clean():
    card = build_qa_score_card(
        consistency_summary={"can_render_pdf": True, "critical_failure_count": 0},
        fallback_verdict={"prohibited_count": 0},
        motor_019_lint={"violations": [], "orphan_claim_findings": []},
        motor_054_summary={"skill_combination_activation_count": 2},
        state_machine_state="client_safe",
    )
    assert not card.decision_blocked


# ── rationale strings ──────────────────────────────────────────────


def test_rationale_includes_all_dimensions():
    card = build_qa_score_card()
    assert set(card.rationale.keys()) == {
        "stability", "contamination", "epistemic_integrity",
        "rendering_integrity", "combination_quality",
        "report_uniqueness", "asset_family_integrity",
    }
    for key, value in card.rationale.items():
        assert isinstance(value, str), key


# ── to_dict serialization ──────────────────────────────────────────


def test_to_dict_produces_serializable_output():
    import json
    card = build_qa_score_card(
        consistency_summary={"can_render_pdf": True, "critical_failure_count": 0},
    )
    d = card.to_dict()
    # Must be JSON-serializable
    js = json.dumps(d)
    assert "overall_score" in js
    assert "client_safe" in js


# ── conservative defaults when inputs missing ──────────────────────


def test_missing_all_inputs_returns_baseline():
    card = build_qa_score_card()
    # With no input, defaults to optimistic scores (no violations seen)
    # but client_safe should still depend on hard requirements
    assert isinstance(card, QAScoreCard)
    assert 0.0 <= card.overall_score <= 1.0
