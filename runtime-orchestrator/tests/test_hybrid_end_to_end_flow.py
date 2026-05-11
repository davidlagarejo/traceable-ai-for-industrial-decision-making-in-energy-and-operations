"""End-to-end test: hybrid asset-family path activates with real evidence (V2-LIVE Item 6).

The hybrid path threads through:
  motor_007 (derive_evidence_tokens from facility_inputs)
    → target_definition_contract.facility_evidence_tokens
    → motor_061 (find_admissible_hybrid)
    → hybrid_admissible=True + shared_patterns exempted from contamination

This test exercises the full chain end-to-end with a dairy + cold-chain
hybrid case. Pre-V2-LIVE, this path was inert because no motor emitted
the trigger tokens. After Items 1+2+3+4+5, the path is live.
"""
from __future__ import annotations

from runtime_orchestrator.adapters.motor_007 import derive_evidence_tokens
from runtime_orchestrator.adapters.motor_061 import Motor061Adapter
from runtime_orchestrator.hybrid_families import find_admissible_hybrid


def _build_hybrid_dairy_case() -> dict:
    """Construct a cold_chain + food_processing hybrid case."""
    return {
        "target_definition_contract": {
            "target_type": "cold_chain_facility",
            "target_name": "Heartland Creamery Cold Chain",
            "asset_family": "cold_chain_facility",
        },
        "observable_cluster_register": {
            "thermal_systems_cluster": ["ammonia refrigeration plant", "process steam loop"],
        },
        "facility_inputs": {
            "input_02_facility_type": {
                "asset_category": "Dairy processing plant with cook chill line and blast freezer",
                "primary_classification": "Cold Chain + Food Processing",
            },
            "input_09_known_systems": {
                "known_systems": [
                    "ammonia refrigeration plant",
                    "process heat boiler",
                    "sanitation steam header",
                    "blast freezer",
                ],
            },
        },
    }


# ── Step 1: motor_007 derives the right tokens ─────────────────────────


def test_step1_motor007_derives_hybrid_trigger_tokens():
    case = _build_hybrid_dairy_case()
    facility, process = derive_evidence_tokens(
        target_definition=case["target_definition_contract"],
        observable_clusters=case["observable_cluster_register"],
        facility_inputs=case["facility_inputs"],
    )
    # facility tokens must trigger cold_chain + food_processing hybrid
    assert "cook_chill_present" in facility
    assert "dairy_processing_evidence" in facility
    assert "blast_freezer_with_cook_line" in facility
    # process tokens must include process_heat or sanitation_steam
    assert any(t in process for t in ("process_heat_signature", "sanitation_steam_present"))


# ── Step 2: hybrid_families.find_admissible_hybrid matches ────────────


def test_step2_find_admissible_hybrid_resolves_cold_chain_food_processing():
    case = _build_hybrid_dairy_case()
    facility, process = derive_evidence_tokens(
        target_definition=case["target_definition_contract"],
        observable_clusters=case["observable_cluster_register"],
        facility_inputs=case["facility_inputs"],
    )
    hybrid = find_admissible_hybrid("cold_chain_facility", set(facility) | set(process))
    assert hybrid is not None
    assert hybrid["hybrid_id"] == "cold_chain_food_processing"
    assert hybrid["secondary"] == "manufacturing_facility"


# ── Step 3: motor_061 admits the hybrid and exempts shared patterns ──


def test_step3_motor061_admits_hybrid_and_exempts_shared_patterns():
    """Construct the full motor_061 input that mirrors a real pipeline:
       motor_007 has populated facility_evidence_tokens; motor_054 has
       activated combinations that include normally-cross-family patterns.
       The hybrid admission must clear contamination."""
    case = _build_hybrid_dairy_case()
    facility, process = derive_evidence_tokens(
        target_definition=case["target_definition_contract"],
        observable_clusters=case["observable_cluster_register"],
        facility_inputs=case["facility_inputs"],
    )
    # Build the contract motor_007 would emit downstream
    target_def = {
        **case["target_definition_contract"],
        "facility_evidence_tokens": facility,
        "process_evidence_tokens": process,
    }
    adapter = Motor061Adapter()
    out = adapter.run({
        "motor_007": {"target_definition_contract": target_def},
        "motor_054": {
            "skill_combination_activation_register": [
                {
                    "combination_id": "dairy_cold_chain_process_combo",
                    "pattern_ids": [
                        "refrigeration_duty",            # cold-chain native
                        "process_load_vs_waste",         # normally manufacturing-only
                        "steam_trap_failure_plausibility",  # normally manufacturing-only
                        "boiler_degradation_plausibility",  # normally manufacturing-only
                    ],
                }
            ]
        },
    })
    assert out["hybrid_admissible"] is True
    assert out["hybrid_id"] == "cold_chain_food_processing"
    assert "process_load_vs_waste" in out["hybrid_shared_patterns"]
    assert "steam_trap_failure_plausibility" in out["hybrid_shared_patterns"]
    assert out["contamination_detected"] is False


# ── Negative path: same case WITHOUT hybrid markers stays blocked ──


def test_negative_pure_cold_chain_with_manufacturing_patterns_stays_blocked():
    """When the facility is pure cold-chain (no dairy/cook-chill markers),
    the same manufacturing-only patterns must remain contamination."""
    target_def = {
        "target_type": "cold_chain_facility",
        "target_name": "Pure Cold Storage",
        "asset_family": "cold_chain_facility",
        # NO evidence tokens — pure cold-chain, no hybrid trigger
    }
    adapter = Motor061Adapter()
    out = adapter.run({
        "motor_007": {"target_definition_contract": target_def},
        "motor_054": {
            "skill_combination_activation_register": [
                {
                    "combination_id": "unjustified_cross",
                    "pattern_ids": [
                        "refrigeration_duty",
                        "process_load_vs_waste",
                        "boiler_degradation_plausibility",
                    ],
                }
            ]
        },
    })
    assert out["hybrid_admissible"] is False
    assert out["contamination_detected"] is True


# ── Coverage: all 5 hybrid combinations have testable trigger paths ──


def test_coverage_all_5_hybrid_combinations_have_at_least_one_textual_trigger():
    """Sanity check: each declared hybrid in asset_family_hybrids.json must
    have at least one trigger that motor_007 can detect via substring
    match. Otherwise the hybrid is permanently unreachable in production."""
    from runtime_orchestrator.adapters.motor_007 import (
        _FACILITY_EVIDENCE_TOKEN_PATTERNS,
        _PROCESS_EVIDENCE_TOKEN_PATTERNS,
    )
    from runtime_orchestrator.hybrid_families import all_hybrids

    detectable = set(_FACILITY_EVIDENCE_TOKEN_PATTERNS.keys()) | set(_PROCESS_EVIDENCE_TOKEN_PATTERNS.keys())
    for hybrid in all_hybrids():
        triggers = set(hybrid.get("justification_triggers", []) or [])
        # NOTE: not every trigger needs to be detectable, but at least one
        # must overlap with motor_007's vocabulary for the hybrid to be
        # reachable without explicit author declaration.
        reachable = triggers.intersection(detectable)
        assert reachable, (
            f"Hybrid '{hybrid['hybrid_id']}' has NO motor_007-detectable "
            f"trigger. Triggers: {triggers}. Detectable vocabulary: "
            f"{sorted(detectable)}"
        )
