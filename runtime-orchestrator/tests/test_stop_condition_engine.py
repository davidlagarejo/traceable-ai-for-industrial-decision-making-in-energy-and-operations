from __future__ import annotations

from runtime_orchestrator.congruence_intelligence.stop_conditions import (
    build_downgrade_condition_register,
    build_escalation_condition_register,
    build_minimum_sufficient_evidence_register,
    build_stop_condition_register,
)


def test_stop_condition_engine_encodes_search_and_intake_paths():
    stop_register = build_stop_condition_register(
        discovery_need_register=[
            {
                "need_id": "warehouse_subtype_classification",
                "discovery_need": "Confirm warehouse subtype.",
                "minimum_sufficient_evidence": "Subtype clue from brochure or operator.",
                "stop_condition": "asset subtype classified with evidence_state >= L2",
                "downgrade_condition": "no subtype clue after listing and assessor families exhausted",
                "escalation_condition": "ask operator whether facility is dry, cold-chain, fulfillment, cross-dock, or mixed",
                "matched_gap_types": ["asset_energy_behavior_reference"],
            }
        ],
        next_best_search_register=[
            {
                "need_id": "warehouse_subtype_classification",
                "search_family": "leasing_brochure",
                "expected_evidence": "asset_brochure",
            }
        ],
        search_budget_register=[
            {
                "budget_scope": "total_public_discovery",
                "budget_state": "exhausted",
            }
        ],
        operational_intake_pack={
            "diligence_pack_register": [
                {
                    "pack_name": "utility_bill_pack",
                    "current_state": "requested_but_absent",
                    "decision_relevance": "Actual utility cost and load structure before capital framing.",
                    "expected_local_sources": ["utility_bill_record", "meter_interval_record"],
                    "present_source_families": [],
                    "binding_needed": ["12-24 months of utility bills"],
                }
            ]
        },
    )

    by_id = {(row["path_type"], row["path_id"]): row for row in stop_register}
    search_row = by_id[("public_search", "warehouse_subtype_classification")]
    intake_row = by_id[("intake_escalation", "utility_bill_pack")]

    assert search_row["current_state"] == "stop_and_escalate"
    assert search_row["continuation_allowed"] is False
    assert "ask operator" in search_row["escalation_condition"].lower()
    assert intake_row["current_state"] == "escalate_to_operator"
    assert intake_row["required_from"] == "owner / accounting / operator"

    downgrade = build_downgrade_condition_register(stop_condition_register=stop_register)
    escalation = build_escalation_condition_register(stop_condition_register=stop_register)
    minimum = build_minimum_sufficient_evidence_register(stop_condition_register=stop_register)

    assert any(row["path_id"] == "warehouse_subtype_classification" for row in downgrade)
    assert any(row["path_id"] == "utility_bill_pack" for row in escalation)
    assert any(row["path_id"] == "utility_bill_pack" for row in minimum)
