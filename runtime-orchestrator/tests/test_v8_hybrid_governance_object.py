"""V8 P3 — Hybrid Governance Object (structured 10-field) tests.

V7 P4 emitía solo la WHY string. V8 P3 emite el objeto estructurado
completo (10 campos) que el prompt Chief QA Architect § 3 + § C exige.
"""
from __future__ import annotations

import pytest

from runtime_orchestrator.hybrid_families import all_hybrids
from runtime_orchestrator.hybrid_justification import (
    build_hybrid_governance_object,
)


_REQUIRED_FIELDS = {
    "primary_asset_family",
    "secondary_asset_family",
    "trigger_evidence",
    "why_secondary_logic_is_allowed",
    "scope_allowed",
    "scope_prohibited",
    "evidence_to_confirm",
    "evidence_to_falsify",
    "report_sections_allowed",
    "report_sections_blocked",
    "tad_impact",
}


# ── Unit: build_hybrid_governance_object ──────────────────────────


def test_governance_object_has_all_required_fields():
    hybrid = {
        "primary": "cold_chain_facility",
        "secondary": "manufacturing_facility",
        "rationale": "Dairy + thermal processing.",
        "justification_triggers": ["cook_chill_present"],
        "scope_allowed": ["thermal duty hypothesis"],
        "scope_prohibited": ["resin/press dominance"],
        "evidence_to_confirm": ["process heat meter"],
        "evidence_to_falsify": ["storage-only confirmed"],
        "report_sections_allowed": ["executive_structural_thesis"],
        "report_sections_blocked": ["owner_capturable_roi"],
        "tad_impact": ["VALIDATE_PROCESS_HEAT_DUTY"],
    }
    obj = build_hybrid_governance_object(
        hybrid=hybrid, matched_evidence_tokens=["cook_chill_present"]
    )
    assert set(obj.keys()) >= _REQUIRED_FIELDS
    assert obj["primary_asset_family"] == "cold_chain_facility"
    assert obj["secondary_asset_family"] == "manufacturing_facility"
    assert obj["trigger_evidence"] == ["cook_chill_present"]
    assert "manufacturing_facility logic" in obj["why_secondary_logic_is_allowed"]
    assert obj["scope_allowed"] == ["thermal duty hypothesis"]
    assert obj["scope_prohibited"] == ["resin/press dominance"]


def test_governance_object_empty_when_hybrid_missing():
    assert build_hybrid_governance_object(hybrid=None) == {}
    assert build_hybrid_governance_object(hybrid={"primary": ""}) == {}


def test_governance_object_fills_empty_lists_when_fields_absent():
    """Hybrid without V8 fields still produces a valid object with empty lists."""
    hybrid = {
        "primary": "warehouse_distribution",
        "secondary": "cold_chain_facility",
        "rationale": "Mixed-temp DC.",
    }
    obj = build_hybrid_governance_object(hybrid=hybrid)
    assert obj["scope_allowed"] == []
    assert obj["scope_prohibited"] == []
    assert obj["evidence_to_confirm"] == []
    assert obj["evidence_to_falsify"] == []
    assert obj["report_sections_allowed"] == []
    assert obj["report_sections_blocked"] == []
    assert obj["tad_impact"] == []


# ── Registry: 5 hybrids backfilled with V8 fields ─────────────────


def test_every_hybrid_has_full_governance_object():
    """All 5 hybrids in asset_family_hybrids.json must carry the V8 fields."""
    for hybrid in all_hybrids():
        obj = build_hybrid_governance_object(
            hybrid=hybrid,
            matched_evidence_tokens=hybrid.get("justification_triggers", [])[:2],
        )
        hid = hybrid.get("hybrid_id", "?")
        for field in _REQUIRED_FIELDS:
            assert field in obj, f"{hid} governance object missing {field!r}"
        # V8 P3 backfill: each hybrid should have non-empty governance arrays.
        assert obj["scope_allowed"], f"{hid} scope_allowed is empty"
        assert obj["scope_prohibited"], f"{hid} scope_prohibited is empty"
        assert obj["evidence_to_confirm"], f"{hid} evidence_to_confirm is empty"
        assert obj["evidence_to_falsify"], f"{hid} evidence_to_falsify is empty"
        assert obj["report_sections_allowed"], f"{hid} report_sections_allowed empty"
        assert obj["report_sections_blocked"], f"{hid} report_sections_blocked empty"
        assert obj["tad_impact"], f"{hid} tad_impact is empty"


def test_cold_chain_food_processing_governance_is_correct():
    hybrid = next(h for h in all_hybrids() if h["hybrid_id"] == "cold_chain_food_processing")
    obj = build_hybrid_governance_object(
        hybrid=hybrid,
        matched_evidence_tokens=["cook_chill_present"],
    )
    assert obj["primary_asset_family"] == "cold_chain_facility"
    assert obj["secondary_asset_family"] == "manufacturing_facility"
    # Must explicitly block resin/press scenarios.
    assert any("resin" in s.lower() or "press" in s.lower() or "curing" in s.lower()
               for s in obj["scope_prohibited"])
    # Must explicitly allow process-heat hypothesis.
    assert any("process" in s.lower() or "thermal" in s.lower()
               for s in obj["scope_allowed"])


# ── motor_061 integration ──────────────────────────────────────────


def test_motor_061_emits_governance_object_when_hybrid_admitted():
    from runtime_orchestrator.adapters.motor_061 import Motor061Adapter
    inputs = {
        "motor_007": {
            "target_definition_contract": {
                "asset_family": "cold_chain_facility",
                "facility_evidence_tokens": ["cook_chill_present"],
            },
        },
        "motor_054": {"skill_combination_activation_register": [],
                       "strategic_gold_nugget_register": []},
    }
    out = Motor061Adapter().run(inputs)
    assert out["hybrid_admissible"] is True
    obj = out["hybrid_governance_object"]
    assert obj["primary_asset_family"] == "cold_chain_facility"
    assert obj["secondary_asset_family"] == "manufacturing_facility"
    assert obj["trigger_evidence"] == ["cook_chill_present"]
    assert obj["scope_allowed"]
    assert obj["scope_prohibited"]


def test_motor_061_empty_governance_object_when_no_hybrid():
    from runtime_orchestrator.adapters.motor_061 import Motor061Adapter
    inputs = {
        "motor_007": {
            "target_definition_contract": {
                "asset_family": "datacenter",
                "facility_evidence_tokens": ["pue_only"],
            },
        },
        "motor_054": {"skill_combination_activation_register": [],
                       "strategic_gold_nugget_register": []},
    }
    out = Motor061Adapter().run(inputs)
    assert out["hybrid_admissible"] is False
    assert out["hybrid_governance_object"] == {}
