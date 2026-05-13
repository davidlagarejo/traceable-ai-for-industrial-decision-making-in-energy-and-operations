"""V7 P4 — Hybrid Justification Narrative Emitter tests."""
from __future__ import annotations

import pytest

from runtime_orchestrator.hybrid_families import (
    all_hybrids,
    find_admissible_hybrid,
)
from runtime_orchestrator.hybrid_justification import (
    build_hybrid_narrative,
    match_evidence_against_hybrid,
)


# ── build_hybrid_narrative ─────────────────────────────────────────


def test_canonical_form_for_cold_chain_food_processing():
    hybrid = {
        "hybrid_id": "cold_chain_food_processing",
        "primary": "cold_chain_facility",
        "secondary": "manufacturing_facility",
        "rationale": "Dairy facilities combine cold-chain with thermal processing.",
        "justification_triggers": ["cook_chill_present", "process_heat_signature"],
    }
    narrative = build_hybrid_narrative(
        hybrid=hybrid,
        matched_evidence_tokens=["cook_chill_present", "process_heat_signature"],
    )
    assert "activates manufacturing_facility logic" in narrative
    assert "cook chill present" in narrative
    assert "process heat signature" in narrative
    assert "cold_chain_facility-only deployment" in narrative
    assert "Dairy facilities" in narrative


def test_empty_when_hybrid_missing_primary_or_secondary():
    assert build_hybrid_narrative(hybrid={"primary": ""}, matched_evidence_tokens=[]) == ""
    assert build_hybrid_narrative(hybrid={"secondary": "x"}, matched_evidence_tokens=[]) == ""
    assert build_hybrid_narrative(hybrid=None, matched_evidence_tokens=[]) == ""


def test_fallback_when_no_matched_tokens():
    hybrid = {
        "primary": "warehouse_distribution",
        "secondary": "cold_chain_facility",
        "rationale": "Some warehouses host refrigerated zones.",
    }
    narrative = build_hybrid_narrative(hybrid=hybrid, matched_evidence_tokens=[])
    # Fallback evidence chain when no triggers matched
    assert "process-routing evidence" in narrative
    assert "warehouse_distribution-only deployment" in narrative


def test_caps_token_list_at_five():
    """Long token chains are truncated for readability."""
    hybrid = {"primary": "p", "secondary": "s", "rationale": ""}
    tokens = [f"token_{i}" for i in range(10)]
    n = build_hybrid_narrative(hybrid=hybrid, matched_evidence_tokens=tokens)
    # 5 tokens shown
    assert "token 4" in n  # 5th
    assert "token 5" not in n  # 6th truncated


# ── match_evidence_against_hybrid ──────────────────────────────────


def test_match_returns_intersection():
    hybrid = {
        "justification_triggers": ["cook_chill_present", "sanitation_steam_present",
                                    "dairy_processing_evidence"],
    }
    evidence = {"cook_chill_present", "noise", "DAIRY_PROCESSING_EVIDENCE"}
    matched = match_evidence_against_hybrid(hybrid, evidence)
    assert "cook_chill_present" in matched
    assert "dairy_processing_evidence" in matched
    assert "sanitation_steam_present" not in matched


def test_match_empty_when_no_overlap():
    hybrid = {"justification_triggers": ["a", "b"]}
    assert match_evidence_against_hybrid(hybrid, ["c", "d"]) == []


def test_match_empty_when_hybrid_has_no_triggers():
    assert match_evidence_against_hybrid({}, ["any"]) == []


# ── Every registered hybrid produces a valid narrative ─────────────


def test_every_registered_hybrid_produces_non_empty_narrative():
    for hybrid in all_hybrids():
        triggers = hybrid.get("justification_triggers", []) or []
        narrative = build_hybrid_narrative(
            hybrid=hybrid,
            matched_evidence_tokens=triggers[:2],  # simulate 2 matched
        )
        assert narrative, f"empty narrative for {hybrid.get('hybrid_id')}"
        assert hybrid["primary"] in narrative
        assert hybrid["secondary"] in narrative


# ── motor_061 integration ──────────────────────────────────────────


def test_motor_061_emits_narrative_when_hybrid_admitted():
    from runtime_orchestrator.adapters.motor_061 import Motor061Adapter
    inputs = {
        "motor_007": {
            "target_definition_contract": {
                "asset_family": "cold_chain_facility",
                "facility_evidence_tokens": [
                    "cook_chill_present", "dairy_processing_evidence",
                ],
                "process_evidence_tokens": [],
            },
        },
        "motor_054": {
            "skill_combination_activation_register": [],
            "strategic_gold_nugget_register": [],
        },
    }
    out = Motor061Adapter().run(inputs)
    assert out["hybrid_admissible"] is True
    assert out["hybrid_id"] == "cold_chain_food_processing"
    assert out["hybrid_justification_narrative"]
    assert "manufacturing_facility logic" in out["hybrid_justification_narrative"]
    assert "cold_chain_facility-only deployment" in out["hybrid_justification_narrative"]


def test_motor_061_emits_empty_narrative_when_no_hybrid():
    from runtime_orchestrator.adapters.motor_061 import Motor061Adapter
    inputs = {
        "motor_007": {
            "target_definition_contract": {
                "asset_family": "datacenter",
                "facility_evidence_tokens": ["pue_evidence"],
                "process_evidence_tokens": [],
            },
        },
        "motor_054": {
            "skill_combination_activation_register": [],
            "strategic_gold_nugget_register": [],
        },
    }
    out = Motor061Adapter().run(inputs)
    assert out["hybrid_admissible"] is False
    assert out["hybrid_justification_narrative"] == ""
    assert out["hybrid_matched_evidence_triggers"] == []
