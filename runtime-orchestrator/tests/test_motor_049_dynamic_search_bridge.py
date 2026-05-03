from __future__ import annotations

from runtime_orchestrator.adapters.motor_049 import Motor049Adapter


def test_motor_049_propagates_dynamic_search_registers():
    out = Motor049Adapter().run(
        {
            "motor_007": {
                "target_definition_contract": {
                    "target_name": "Sunrise Logistics Hub",
                    "target_identifier": "sunrise-logistics-hub-2026",
                    "address_raw": "1450 Logistics Parkway, Dallas, TX 75201",
                    "target_type": "warehouse_distribution",
                    "jurisdiction_scope": ["US-TX"],
                },
                "target_classification_object": {
                    "target_type": "OPERATING_ASSET",
                    "classification_confidence": "high",
                },
            },
            "motor_012": {
                "facility_prior": {},
                "asset_field_register": [],
            },
            "motor_028": {
                "source_register": [],
                "enriched_data": {},
                "search_budget_register": [],
                "search_attempt_ledger": [],
                "search_attempt_outcome_register": [],
                "search_exhaustion_register": [],
                "discovery_need_register": [
                    {
                        "need_id": "warehouse_subtype_classification",
                        "discovery_need": "Confirm warehouse subtype.",
                    }
                ],
                "search_family_execution_plan": [
                    {
                        "need_id": "warehouse_subtype_classification",
                        "search_family": "leasing_brochure",
                    }
                ],
                "accepted_evidence_type_register": [
                    {
                        "need_id": "warehouse_subtype_classification",
                        "accepted_evidence_type": "asset_brochure",
                    }
                ],
                "discovery_stop_condition_register": [
                    {
                        "need_id": "warehouse_subtype_classification",
                        "stop_condition": "asset subtype classified with evidence_state >= L2",
                    }
                ],
                "next_best_search_register": [
                    {
                        "need_id": "warehouse_subtype_classification",
                        "next_search_target": "Confirm warehouse subtype.",
                    }
                ],
                "search_target_priority_register": [
                    {
                        "need_id": "warehouse_subtype_classification",
                        "priority_score": 100,
                    }
                ],
                "search_success_effect_register": [
                    {
                        "need_id": "warehouse_subtype_classification",
                        "if_found": "Subtype bounded.",
                    }
                ],
                "search_failure_effect_register": [
                    {
                        "need_id": "warehouse_subtype_classification",
                        "if_not_found": "Ask operator.",
                    }
                ],
            },
        }
    )

    assert out["discovery_need_count"] == 1
    assert out["next_best_search_count"] == 1
    assert out["stop_condition_count"] >= 1
    assert len(out["operational_intake_pack"]["discovery_need_register"]) == 1
    assert len(out["operational_intake_pack"]["next_best_search_register"]) == 1
    assert len(out["operational_intake_pack"]["stop_condition_register"]) >= 1
