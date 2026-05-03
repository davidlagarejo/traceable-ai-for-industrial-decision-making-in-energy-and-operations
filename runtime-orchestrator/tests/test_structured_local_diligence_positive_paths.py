from __future__ import annotations

from runtime_orchestrator.adapters.motor_049 import Motor049Adapter


def _field(field: str, value, *, source_id: str | None = None) -> dict:
    return {
        "field": field,
        "value": value,
        "status": "OBSERVED",
        "source_id": source_id or f"test::{field}",
        "scope": "ASSET_LEVEL",
        "authority_score": "high",
        "recency": "current",
        "admissibility": "CONFIRMED_ASSET_LEVEL",
        "notes": "",
    }


def _logistics_structured_inputs() -> dict:
    return {
        "__pipeline__": {
            "facility_inputs": {
                "input_11_congruence_diligence": {
                    "packs": {
                        "utility_bill_pack": {
                            "source_families": ["utility_bill_record"],
                            "records": [{"source_id": "bill::1", "charge_type": "demand_charge", "charge_amount": "12000"}],
                        },
                        "throughput_schedule_pack": {
                            "source_families": ["schedule_record", "operator_input_record"],
                            "records": [{"dock_turns_per_day": "250", "operating_pattern": "24/6"}],
                        },
                        "equipment_inventory_pack": {
                            "source_families": ["equipment_inventory_record"],
                            "records": [{"critical_system": "forklift charging", "fleet_count": "80"}],
                        },
                        "metering_boundary_pack": {
                            "source_families": ["submetering_record", "operator_input_record"],
                            "records": [{"metering_scope": "charging submeter"}],
                        },
                        "maintenance_proof_pack": {
                            "source_families": ["maintenance_log_record", "maintenance_contract_record"],
                            "records": [{"pm_program": "quarterly"}],
                        },
                        "cmms_or_workorder_pack": {
                            "source_families": ["cmms_record"],
                            "records": [{"open_workorders": "8"}],
                        },
                    }
                }
            }
        },
        "motor_007": {
            "target_definition_contract": {
                "address_raw": "1450 Logistics Parkway, Joliet, IL 60436",
                "jurisdiction_scope": ["US-IL"],
                "target_type": "warehouse_distribution",
                "target_name": "Sunrise Logistics Hub",
                "target_identifier": "sunrise-logistics-hub",
            },
            "target_classification_object": {"target_type": "OPERATING_ASSET", "classification_confidence": "high"},
        },
        "motor_012": {
            "facility_prior": {"target_definition": {"target_type": "warehouse_distribution", "jurisdiction_scope": ["US-IL"]}},
            "asset_field_register": [_field("asset_class", "warehouse_distribution"), _field("use", "logistics warehouse")],
        },
        "motor_028": {"source_register": [], "enriched_data": {}},
    }


def _cold_chain_structured_inputs() -> dict:
    return {
        "__pipeline__": {
            "facility_inputs": {
                "input_11_congruence_diligence": {
                    "packs": {
                        "utility_bill_pack": {
                            "source_families": ["utility_bill_record"],
                            "records": [{"source_id": "bill::cold::1", "charge_type": "demand_charge", "demand_kw": "3900"}],
                        },
                        "throughput_schedule_pack": {
                            "source_families": ["schedule_record", "operator_input_record"],
                            "records": [{"service_level": "frozen outbound", "operating_pattern": "24/7"}],
                        },
                        "equipment_inventory_pack": {
                            "source_families": ["equipment_inventory_record"],
                            "records": [{"critical_system": "ammonia refrigeration plant", "compressor_count": "6"}],
                        },
                        "permit_detail_pack": {
                            "source_families": ["permit_record"],
                            "records": [{"permit_id": "permit::cold::1", "permit_type": "refrigeration safety permit"}],
                        },
                        "bms_or_controls_pack": {
                            "source_families": ["bms_trend_record", "operator_input_record"],
                            "records": [{"defrost_schedule": "staggered by zone"}],
                        },
                        "maintenance_proof_pack": {
                            "source_families": ["maintenance_log_record", "maintenance_contract_record"],
                            "records": [{"pm_program": "monthly oil analysis"}],
                        },
                        "cmms_or_workorder_pack": {
                            "source_families": ["cmms_record"],
                            "records": [{"open_workorders": "6"}],
                        },
                        "utility_tariff_pack": {
                            "source_families": ["utility_tariff_record"],
                            "records": [{"tariff_name": "Large Power Service", "service_class": "on-peak demand"}],
                        },
                    }
                }
            }
        },
        "motor_007": {
            "target_definition_contract": {
                "address_raw": "2500 South Damen Avenue, Chicago, IL 60608",
                "jurisdiction_scope": ["US-IL"],
                "target_type": "cold_chain_facility",
                "target_name": "Lakeshore Cold Storage Campus",
                "target_identifier": "lakeshore-cold-storage-campus",
            },
            "target_classification_object": {"target_type": "OPERATING_ASSET", "classification_confidence": "high"},
        },
        "motor_012": {
            "facility_prior": {"target_definition": {"target_type": "cold_chain_facility", "jurisdiction_scope": ["US-IL"]}},
            "asset_field_register": [_field("asset_class", "cold_chain_facility"), _field("use", "cold storage")],
        },
        "motor_028": {"source_register": [], "enriched_data": {}},
    }


def test_motor_049_promotes_logistics_case_from_structured_diligence():
    out = Motor049Adapter().run(_logistics_structured_inputs())

    assert out["selected_asset_family"] == "logistics_warehouse"
    assert out["structured_local_source_count"] >= 6
    assert out["research_mode"] == "operator_integrated_congruence"
    assert out["evidence_mode_state"] == "operator_integrated_congruence"
    assert out["promotion_blocker_count"] == 0
    assert out["utility_charge_breakdown_count"] >= 1


def test_motor_049_promotes_cold_chain_case_from_structured_diligence():
    out = Motor049Adapter().run(_cold_chain_structured_inputs())

    assert out["selected_asset_family"] == "cold_chain"
    assert out["structured_local_source_count"] >= 7
    assert out["research_mode"] == "operator_integrated_congruence"
    assert out["evidence_mode_state"] == "operator_integrated_congruence"
    assert out["promotion_blocker_count"] == 0
    assert out["tariff_exposure_count"] >= 1
    assert out["permit_to_system_count"] >= 1
