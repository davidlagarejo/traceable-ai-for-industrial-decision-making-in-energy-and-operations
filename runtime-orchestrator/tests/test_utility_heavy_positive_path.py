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


def _utility_heavy_structured_inputs() -> dict:
    return {
        "__pipeline__": {
            "facility_inputs": {
                "input_11_congruence_diligence": {
                    "packs": {
                        "utility_bill_pack": {
                            "source_families": ["utility_bill_record"],
                            "records": [
                                {"source_id": "bill::utility::1", "charge_type": "demand_charge", "charge_amount": "55000", "demand_kw": "7420"},
                                {"source_id": "bill::utility::2", "charge_type": "pf_charge", "charge_amount": "9300"},
                            ],
                        },
                        "utility_tariff_pack": {
                            "source_families": ["utility_tariff_record"],
                            "records": [{"source_id": "tariff::utility::1", "tariff_name": "Large Power Service", "pf_charge": "present"}],
                        },
                        "throughput_schedule_pack": {
                            "source_families": ["schedule_record", "operator_input_record"],
                            "records": [{"support_duty_profile": "three downstream process blocks", "dispatch_note": "compressor and pump sequencing tracks process demand ramps"}],
                        },
                        "equipment_inventory_pack": {
                            "source_families": ["equipment_inventory_record"],
                            "records": [{"critical_system": "compressor trains and cooling water pumps", "major_motor_count": "42", "compressor_trains": "5"}],
                        },
                        "metering_boundary_pack": {
                            "source_families": ["submetering_record", "operator_input_record"],
                            "records": [{"metering_scope": "dedicated fiscal meter plus feeder-level process meters"}],
                        },
                        "maintenance_proof_pack": {
                            "source_families": ["maintenance_log_record", "maintenance_contract_record"],
                            "records": [{"pm_program": "monthly vibration and quarterly compressor valve inspection"}],
                        },
                        "cmms_or_workorder_pack": {
                            "source_families": ["cmms_record"],
                            "records": [{"open_workorders": "11", "repeat_failure_theme": "compressor unloader drift"}],
                        },
                        "permit_detail_pack": {
                            "source_families": ["permit_record", "regulatory_coverage_record"],
                            "records": [{"permit_type": "support utility service context"}],
                        },
                    }
                }
            }
        },
        "motor_007": {
            "target_definition_contract": {
                "address_raw": "8200 Utility Corridor Drive, Corpus Christi, TX 78409",
                "jurisdiction_scope": ["US-TX"],
                "target_type": "industrial_plant",
                "target_name": "Prairie Central Utility Island",
                "target_identifier": "prairie-central-utility-island",
            },
            "target_classification_object": {"target_type": "OPERATING_ASSET", "classification_confidence": "high"},
        },
        "motor_012": {
            "facility_prior": {"target_definition": {"target_type": "industrial_plant", "jurisdiction_scope": ["US-TX"]}},
            "asset_field_register": [
                _field("asset_class", "industrial_plant"),
                _field("primary_classification", "utility heavy site"),
                _field("asset_category", "central utility island"),
                _field("major_equipment", "large motors and drives, compressor trains, cooling water pumps"),
                _field("tariff_signal", "power factor and reactive-charge exposure"),
            ],
        },
        "motor_028": {"source_register": [], "enriched_data": {}},
    }


def test_motor_049_promotes_utility_heavy_case_from_structured_diligence():
    out = Motor049Adapter().run(_utility_heavy_structured_inputs())

    assert out["selected_asset_family"] == "utility_heavy_site"
    assert out["research_mode"] == "operator_integrated_congruence"
    assert out["evidence_mode_state"] == "operator_integrated_congruence"
    assert out["promotion_blocker_count"] == 0
    assert out["tariff_exposure_count"] >= 1
    assert out["utility_charge_breakdown_count"] >= 1


def test_utility_heavy_case_emits_specific_congruence_contradiction():
    base = _utility_heavy_structured_inputs()
    out49 = Motor049Adapter().run(base)
    out50 = Motor050Adapter().run({**base, "motor_049": out49})
    out51 = Motor051Adapter().run({**base, "motor_049": out49, "motor_050": out50})

    contradictions = {row["contradiction"] for row in out51["cross_layer_congruence_register"]}
    invalid_frames = {row["apparent_problem"] for row in out51["invalid_problem_frame_register"]}

    assert "Consumption framing vs demand-structure reality" in contradictions
    assert "high_site_consumption_automatically_means_main_utility_opportunity" in invalid_frames
