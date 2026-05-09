"""Tests for the R-W03 wiring: motor_016 merges legacy + governed
claim contract registers before rendering claim-permission sections.
"""
from __future__ import annotations

from runtime_orchestrator.adapters.motor_016 import _merge_claim_contract_registers


def test_merge_governed_only():
    legacy = []
    governed = [
        {
            "claim_id": "claim_a",
            "permission": "allowed",
            "evidence_state": "ARCHETYPAL_PRIOR",
            "falsification_condition": "Asset evidence proves frame is wrong.",
            "allowed_use": ["bounded screening"],
            "prohibited_use": ["ROI"],
        }
    ]
    out = _merge_claim_contract_registers(legacy, governed)
    assert len(out) == 1
    assert out[0]["claim_id"] == "claim_a"
    assert out[0]["evidence_state"] == "ARCHETYPAL_PRIOR"


def test_merge_legacy_only():
    legacy = [
        {
            "claim_id": "claim_a",
            "permission": "allowed",
            "evidence_state": "OBSERVED_FACT",
        }
    ]
    governed = []
    out = _merge_claim_contract_registers(legacy, governed)
    assert len(out) == 1
    assert out[0]["evidence_state"] == "OBSERVED_FACT"


def test_governed_overrides_legacy_on_id_collision():
    legacy = [
        {
            "claim_id": "claim_a",
            "permission": "prohibited",
            "evidence_state": "CONDITIONAL_HYPOTHESIS",
            "falsification_condition": "",  # legacy has no falsification
        }
    ]
    governed = [
        {
            "claim_id": "claim_a",
            "permission": "allowed",
            "evidence_state": "ARCHETYPAL_PRIOR",
            "falsification_condition": "Tariff bills prove charging is not the driver.",
        }
    ]
    out = _merge_claim_contract_registers(legacy, governed)
    assert len(out) == 1
    # Governed wins
    assert out[0]["evidence_state"] == "ARCHETYPAL_PRIOR"
    assert out[0]["permission"] == "allowed"
    assert out[0]["falsification_condition"].startswith("Tariff bills")


def test_legacy_entries_preserved_when_only_in_legacy():
    legacy = [
        {"claim_id": "legacy_only", "permission": "prohibited", "evidence_state": "OBSERVED_FACT"},
        {"claim_id": "shared", "permission": "prohibited", "evidence_state": "CONDITIONAL_HYPOTHESIS"},
    ]
    governed = [
        {"claim_id": "shared", "permission": "allowed", "evidence_state": "ARCHETYPAL_PRIOR"},
        {"claim_id": "governed_only", "permission": "allowed", "evidence_state": "WEAK_SIGNAL"},
    ]
    out = _merge_claim_contract_registers(legacy, governed)
    ids = [row["claim_id"] for row in out]
    assert ids == ["legacy_only", "shared", "governed_only"]
    # The shared one took the governed payload
    shared = next(row for row in out if row["claim_id"] == "shared")
    assert shared["evidence_state"] == "ARCHETYPAL_PRIOR"


def test_merge_does_not_mutate_inputs():
    legacy = [{"claim_id": "x", "permission": "prohibited"}]
    governed = [{"claim_id": "x", "permission": "allowed"}]
    legacy_snapshot = [dict(row) for row in legacy]
    governed_snapshot = [dict(row) for row in governed]
    _merge_claim_contract_registers(legacy, governed)
    assert legacy == legacy_snapshot
    assert governed == governed_snapshot


def test_merge_handles_rows_without_claim_id_in_legacy():
    """Rows in legacy without a claim_id are preserved as-is, not dropped."""
    legacy = [{"statement": "untyped legacy entry", "permission": "prohibited"}]
    governed = []
    out = _merge_claim_contract_registers(legacy, governed)
    assert len(out) == 1
    assert out[0]["statement"] == "untyped legacy entry"


def test_merge_skips_governed_rows_without_claim_id():
    """Governed rows without a claim_id are not appended (cannot merge by id)."""
    legacy = []
    governed = [{"statement": "governed without id", "permission": "allowed"}]
    out = _merge_claim_contract_registers(legacy, governed)
    assert out == []
