"""V7 P6 — motor_058 RU6 intra-run evidence pack repetition tests."""
from __future__ import annotations

import pytest

from runtime_orchestrator.adapters.motor_058 import (
    Motor058Adapter,
    _detect_RU6_intra_run_evidence_pack_repetition,
)
from runtime_orchestrator.validator_severity_policy import is_v6_blocking_rule


@pytest.fixture(autouse=True)
def _force_soft_mode(monkeypatch):
    """RU6 defaults to 'warning'. Hard mode promotes it to 'blocking'.
    Most tests verify the warning level."""
    monkeypatch.setenv("ZLAB_VALIDATORS_HARD_BLOCK", "0")


# ── Unit: _detect_RU6 helper ───────────────────────────────────────


def test_RU6_flags_two_cases_with_identical_evidence():
    register = [
        {"case_id": "CASE_A",
         "minimum_evidence": ["compressor inventory", "setpoint log", "operating schedule"]},
        {"case_id": "CASE_B",
         "minimum_evidence": ["compressor inventory", "setpoint log", "operating schedule"]},
    ]
    out = _detect_RU6_intra_run_evidence_pack_repetition(register)
    assert len(out) == 1
    assert out[0]["rule_id"] == "RU6_intra_run_evidence_pack_repetition"
    assert out[0]["jaccard"] == 1.0
    assert {out[0]["case_a"], out[0]["case_b"]} == {"CASE_A", "CASE_B"}


def test_RU6_silent_when_evidence_disjoint():
    register = [
        {"case_id": "CASE_A", "minimum_evidence": ["compressor inventory"]},
        {"case_id": "CASE_B", "minimum_evidence": ["dock cycle log"]},
    ]
    assert _detect_RU6_intra_run_evidence_pack_repetition(register) == []


def test_RU6_silent_when_low_overlap():
    """50% overlap (below 80% threshold) is fine."""
    register = [
        {"case_id": "CASE_A", "minimum_evidence": ["a", "b"]},
        {"case_id": "CASE_B", "minimum_evidence": ["a", "c", "d", "e"]},
    ]
    out = _detect_RU6_intra_run_evidence_pack_repetition(register)
    assert out == []


def test_RU6_silent_when_only_one_case():
    register = [
        {"case_id": "CASE_A", "minimum_evidence": ["a", "b", "c"]},
    ]
    assert _detect_RU6_intra_run_evidence_pack_repetition(register) == []


def test_RU6_silent_when_empty_evidence():
    register = [
        {"case_id": "CASE_A", "minimum_evidence": []},
        {"case_id": "CASE_B", "minimum_evidence": []},
    ]
    assert _detect_RU6_intra_run_evidence_pack_repetition(register) == []


def test_RU6_reads_evidence_required_field_too():
    """Validators / motor_054 may surface evidence under different keys."""
    register = [
        {"case_id": "CASE_A", "evidence_required": ["x", "y", "z"]},
        {"case_id": "CASE_B", "evidence_required": ["x", "y", "z"]},
    ]
    out = _detect_RU6_intra_run_evidence_pack_repetition(register)
    assert len(out) == 1


def test_RU6_unique_pair_per_violation():
    """Three cases with same pack → 3 pairs (C(3,2))."""
    register = [
        {"case_id": "A", "minimum_evidence": ["x", "y"]},
        {"case_id": "B", "minimum_evidence": ["x", "y"]},
        {"case_id": "C", "minimum_evidence": ["x", "y"]},
    ]
    out = _detect_RU6_intra_run_evidence_pack_repetition(register)
    assert len(out) == 3


# ── Integration: motor_058 emits RU6 in output ─────────────────────


def test_motor_058_surface_RU6_warning():
    register = [
        {"case_id": "RC-1", "nugget_text": "n1",
         "minimum_evidence": ["a", "b", "c", "d"]},
        {"case_id": "RC-2", "nugget_text": "n2",
         "minimum_evidence": ["a", "b", "c", "d"]},
    ]
    out = Motor058Adapter().run({
        "motor_007": {"target_definition_contract": {"asset_family": "warehouse_distribution"}},
        "motor_018": {}, "motor_033": {},
        "motor_054": {"strategic_gold_nugget_register": register},
    })
    ru6 = [w for w in out["report_uniqueness_warnings"]
           if w["rule_id"] == "RU6_intra_run_evidence_pack_repetition"]
    assert len(ru6) == 1


# ── V6 blocking set + hard mode promotion ──────────────────────────


def test_RU6_in_v6_blocking_set():
    assert is_v6_blocking_rule("motor_058", "RU6_intra_run_evidence_pack_repetition")


def test_RU6_promotes_to_blocking_in_hard_mode(monkeypatch):
    monkeypatch.setenv("ZLAB_VALIDATORS_HARD_BLOCK", "1")
    register = [
        {"case_id": "A", "minimum_evidence": ["x", "y", "z"]},
        {"case_id": "B", "minimum_evidence": ["x", "y", "z"]},
    ]
    out = Motor058Adapter().run({
        "motor_007": {"target_definition_contract": {"asset_family": "warehouse_distribution"}},
        "motor_018": {}, "motor_033": {},
        "motor_054": {"strategic_gold_nugget_register": register},
    })
    ru6 = [w for w in out["report_uniqueness_warnings"]
           if w["rule_id"] == "RU6_intra_run_evidence_pack_repetition"]
    assert ru6 and ru6[0]["severity"] == "blocking"
