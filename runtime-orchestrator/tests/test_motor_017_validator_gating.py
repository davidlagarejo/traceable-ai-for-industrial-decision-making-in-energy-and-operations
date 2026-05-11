"""Tests for V3 G1: motor_017 gates render on motor_055-059 validator outputs.

Until V3, motors 055-059 detected issues but emitted warnings only; motor_017
ignored them. V3 wires their key rules into block_reasons so the render is
actually blocked when those validators fire.

Thresholds are configurable via __pipeline__.validator_thresholds to keep
regression/CI behavior stable.
"""
from __future__ import annotations

import pytest

from runtime_orchestrator.adapters.motor_017 import Motor017Adapter


def _base_inputs(**overrides):
    """Build the minimum motor_017 input set; tests override per-validator outputs."""
    base = {
        "motor_014": {"scenario_space": []},
        "motor_016": {
            "report_package": {
                "package_id": "test_pkg",
                "case_metadata": {"case_id": "test_case_v3_g1"},
                "approved_views": {},
                "render_section_contract": {},
                "context_integrity_scan": {"render_eligible": True},
                "framework_constraint": "",
                "governance_summary": {},
            }
        },
        "motor_036": {"can_render_pdf": True},
        "motor_055": {},
        "motor_056": {},
        "motor_057": {},
        "motor_058": {},
        "motor_059": {},
        "motor_061": {},
        "motor_062": {},
        "motor_063": {},
        "__pipeline__": {},
    }
    base.update(overrides)
    return base


def _run(**overrides) -> dict:
    adapter = Motor017Adapter()
    return adapter.run(_base_inputs(**overrides))


# ── motor_055 — Hypothesis Diversity ────────────────────────────────────


def test_m055_duplicate_claim_signature_blocks_render():
    out = _run(
        motor_055={
            "hypothesis_diversity_warnings": [
                {"rule_id": "HD2_duplicate_claim_signature", "severity": "warning",
                 "description": "duplicate signature detected"}
            ],
            "warning_count": 1,
            "rules_evaluated": ["HD2_duplicate_claim_signature"],
        }
    )
    assert out["compilation_status"] == "blocked"
    assert "motor_055.HD2" in (out.get("blocking_reason") or "")


def test_m055_low_claim_count_does_not_block_render():
    """HD1 (low claim count) is informational; only HD2 blocks."""
    out = _run(
        motor_055={
            "hypothesis_diversity_warnings": [
                {"rule_id": "HD1_low_claim_count", "severity": "warning"}
            ],
            "warning_count": 1,
        }
    )
    # No HD2, no block from m055
    blocking = out.get("blocking_reason", "") or ""
    assert "motor_055" not in blocking


# ── motor_056 — Evidence Repetition ─────────────────────────────────────


def test_m056_pack_repetition_under_threshold_does_not_block():
    out = _run(
        motor_056={
            "evidence_repetition_warnings": [
                {"rule_id": "ER1_pack_repetition", "severity": "warning"}
            ],
            "warning_count": 1,
        }
    )
    blocking = out.get("blocking_reason", "") or ""
    assert "motor_056" not in blocking  # default threshold 2


def test_m056_pack_repetition_above_threshold_blocks():
    out = _run(
        motor_056={
            "evidence_repetition_warnings": [
                {"rule_id": "ER1_pack_repetition", "severity": "warning"},
                {"rule_id": "ER1_pack_repetition", "severity": "warning"},
            ],
            "warning_count": 2,
        }
    )
    assert "motor_056.ER1" in (out.get("blocking_reason") or "")


# ── motor_057 — Gold Nugget Quality ─────────────────────────────────────


def test_m057_archetype_replay_blocks():
    out = _run(
        motor_057={
            "gold_nugget_quality_warnings": [
                {"rule_id": "GN1_archetype_replay", "severity": "warning"}
            ],
            "warning_count": 1,
        }
    )
    assert "motor_057.GN1" in (out.get("blocking_reason") or "")


# ── motor_058 — Report Uniqueness ───────────────────────────────────────


def test_m058_verbatim_nugget_reuse_blocks():
    out = _run(
        motor_058={
            "report_uniqueness_warnings": [
                {"rule_id": "RU2_verbatim_nugget_reuse", "severity": "warning"}
            ],
            "warning_count": 1,
        }
    )
    assert "motor_058.RU2" in (out.get("blocking_reason") or "")


def test_m058_high_jaccard_only_does_not_block():
    """RU1 (jaccard overlap) is signal, not closure. Only RU2 (verbatim) blocks."""
    out = _run(
        motor_058={
            "report_uniqueness_warnings": [
                {"rule_id": "RU1_high_jaccard_overlap", "severity": "warning"}
            ],
            "warning_count": 1,
        }
    )
    blocking = out.get("blocking_reason", "") or ""
    assert "motor_058" not in blocking


# ── motor_059 — Strategic Intelligence ──────────────────────────────────


def test_m059_error_severity_blocks():
    out = _run(
        motor_059={
            "strategic_intelligence_warnings": [
                {"rule_id": "R2_act_now_with_prohibited_claim",
                 "severity": "error",
                 "description": "ACT NOW on prohibited claim"}
            ],
            "warning_count": 1,
            "warning_count_by_severity": {"error": 1, "warning": 0, "info": 0},
        }
    )
    assert "motor_059" in (out.get("blocking_reason") or "")


def test_m059_warning_severity_does_not_block():
    out = _run(
        motor_059={
            "strategic_intelligence_warnings": [
                {"rule_id": "R1_missing_falsification", "severity": "warning"}
            ],
            "warning_count": 1,
            "warning_count_by_severity": {"error": 0, "warning": 1, "info": 0},
        }
    )
    blocking = out.get("blocking_reason", "") or ""
    assert "motor_059" not in blocking


# ── Thresholds are pipeline-configurable ────────────────────────────────


def test_thresholds_can_relax_m056_for_specific_pipelines():
    """A CI/regression pipeline can raise ER1 threshold to 99 to ignore it."""
    out = _run(
        motor_056={
            "evidence_repetition_warnings": [
                {"rule_id": "ER1_pack_repetition"},
                {"rule_id": "ER1_pack_repetition"},
                {"rule_id": "ER1_pack_repetition"},
            ],
        },
        **{"__pipeline__": {"validator_thresholds": {"m056_ER1": 99}}},
    )
    blocking = out.get("blocking_reason", "") or ""
    assert "motor_056" not in blocking


# ── Blocked payload exposes new summaries ───────────────────────────────


def test_blocked_payload_includes_all_new_validator_summaries():
    out = _run(
        motor_059={
            "strategic_intelligence_warnings": [
                {"rule_id": "R2_act_now_with_prohibited_claim", "severity": "error"}
            ],
            "warning_count": 1,
            "warning_count_by_severity": {"error": 1, "warning": 0, "info": 0},
            "rules_evaluated": ["R1", "R2", "R3", "R4"],
        }
    )
    assert out["compilation_status"] == "blocked"
    for key in (
        "hypothesis_diversity_summary",
        "evidence_repetition_summary",
        "gold_nugget_quality_summary",
        "report_uniqueness_summary",
        "strategic_intelligence_summary",
    ):
        assert key in out, f"missing {key} in blocked payload"
    assert out["strategic_intelligence_summary"]["warning_count_by_severity"]["error"] == 1
