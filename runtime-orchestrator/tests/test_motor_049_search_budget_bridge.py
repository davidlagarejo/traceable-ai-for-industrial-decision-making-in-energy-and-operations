from __future__ import annotations

from runtime_orchestrator.adapters.motor_049 import Motor049Adapter


def test_motor_049_passes_through_search_budget_and_attempt_registers():
    out = Motor049Adapter().run(
        {
            "motor_007": {
                "target_definition_contract": {
                    "target_type": "warehouse_distribution",
                    "target_name": "Sunrise Logistics Hub",
                    "target_identifier": "sunrise-logistics-hub-2026",
                    "jurisdiction_scope": ["US-TX"],
                },
                "target_classification_object": {
                    "target_type": "OPERATING_ASSET",
                    "classification_confidence": "high",
                },
            },
            "motor_012": {
                "facility_prior": {
                    "target_definition": {
                        "target_type": "warehouse_distribution",
                        "target_name": "Sunrise Logistics Hub",
                        "target_identifier": "sunrise-logistics-hub-2026",
                        "jurisdiction_scope": ["US-TX"],
                    }
                },
                "asset_field_register": [],
            },
            "motor_028": {
                "source_register": [],
                "enriched_data": {},
                "search_budget_register": [
                    {"budget_scope": "total_public_discovery", "budget_state": "bounded"}
                ],
                "search_attempt_ledger": [
                    {"attempt_sequence": 1, "purpose": "Bound the asset address."}
                ],
                "search_attempt_outcome_register": [
                    {"attempt_kind": "primary", "outcome_class": "evidence_found", "attempt_count": 1}
                ],
                "search_exhaustion_register": [],
            },
        }
    )

    assert out["search_budget_count"] == 1
    assert out["search_attempt_count"] == 1
    assert out["search_exhaustion_count"] == 0
    assert out["operational_intake_pack"]["search_budget_register"][0]["budget_scope"] == "total_public_discovery"
    assert out["operational_intake_pack"]["search_attempt_ledger"][0]["attempt_sequence"] == 1
