from __future__ import annotations

from runtime_orchestrator.adapters.motor_049 import Motor049Adapter
from runtime_orchestrator.adapters.motor_050 import Motor050Adapter
from runtime_orchestrator.adapters.motor_051 import Motor051Adapter


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


def _infrastructure_structured_inputs() -> dict:
    return {
        "__pipeline__": {
            "facility_inputs": {
                "input_11_congruence_diligence": {
                    "packs": {
                        "utility_bill_pack": {
                            "source_families": ["utility_bill_record"],
                            "records": [{"source_id": "bill::infra::1", "charge_type": "demand_charge", "charge_amount": "42000", "demand_kw": "6100"}],
                        },
                        "utility_tariff_pack": {
                            "source_families": ["utility_tariff_record"],
                            "records": [{"source_id": "tariff::infra::1", "tariff_name": "Large Power Service", "pf_charge": "present"}],
                        },
                        "throughput_schedule_pack": {
                            "source_families": ["schedule_record", "operator_input_record"],
                            "records": [{"service_continuity_target": "99.98%", "dispatch_burden": "peak switching and feeder balancing"}],
                        },
                        "equipment_inventory_pack": {
                            "source_families": ["equipment_inventory_record"],
                            "records": [{"critical_system": "power transformer bank", "transformer_count": "3", "capacitor_bank": "installed"}],
                        },
                        "maintenance_proof_pack": {
                            "source_families": ["maintenance_log_record", "maintenance_contract_record"],
                            "records": [{"pm_program": "quarterly breaker and infrared inspection"}],
                        },
                        "cmms_or_workorder_pack": {
                            "source_families": ["cmms_record"],
                            "records": [{"open_workorders": "5", "recent_outage_postmortem": "completed"}],
                        },
                        "permit_detail_pack": {
                            "source_families": ["permit_record", "regulatory_coverage_record"],
                            "records": [{"permit_type": "electrical operating and safety inspection context"}],
                        },
                    }
                }
            }
        },
        "motor_007": {
            "target_definition_contract": {
                "address_raw": "4100 Power Corridor Road, Joliet, IL 60431",
                "jurisdiction_scope": ["US-IL"],
                "target_type": "infrastructure_node",
                "target_name": "Riverside Grid Substation",
                "target_identifier": "riverside-grid-substation",
            },
            "target_classification_object": {"target_type": "OPERATING_ASSET", "classification_confidence": "high"},
        },
        "motor_012": {
            "facility_prior": {"target_definition": {"target_type": "infrastructure_node", "jurisdiction_scope": ["US-IL"]}},
            "asset_field_register": [
                _field("asset_class", "infrastructure_node"),
                _field("use", "grid substation"),
                _field("major_equipment", "power transformer bank"),
                _field("service_continuity_target", "99.98%"),
            ],
        },
        "motor_028": {"source_register": [], "enriched_data": {}},
    }


def test_motor_049_promotes_infrastructure_case_from_structured_diligence():
    out = Motor049Adapter().run(_infrastructure_structured_inputs())

    assert out["selected_asset_family"] == "infrastructure_node"
    assert out["research_mode"] == "operator_integrated_congruence"
    assert out["evidence_mode_state"] == "operator_integrated_congruence"
    assert out["promotion_blocker_count"] == 0
    assert out["tariff_exposure_count"] >= 1
    assert out["permit_to_system_count"] >= 1


def test_infrastructure_case_emits_specific_congruence_contradiction():
    base = _infrastructure_structured_inputs()
    out49 = Motor049Adapter().run(base)
    out50 = Motor050Adapter().run({**base, "motor_049": out49})
    out51 = Motor051Adapter().run({**base, "motor_049": out49, "motor_050": out50})

    contradictions = {row["contradiction"] for row in out51["cross_layer_congruence_register"]}
    invalid_frames = {row["apparent_problem"] for row in out51["invalid_problem_frame_register"]}

    assert "Energy average vs service continuity burden" in contradictions
    assert "high_node_energy_automatically_means_waste" in invalid_frames


def test_motor_049_keeps_infrastructure_family_when_distribution_language_is_physical_not_logistics():
    inputs = _infrastructure_structured_inputs()
    inputs["motor_012"]["asset_field_register"].append(
        _field("primary_use", "Power conversion and distribution")
    )

    out = Motor049Adapter().run(inputs)

    assert out["selected_asset_family"] == "infrastructure_node"
