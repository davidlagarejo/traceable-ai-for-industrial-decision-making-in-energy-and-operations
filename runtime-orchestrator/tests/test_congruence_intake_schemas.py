from __future__ import annotations

from runtime_orchestrator.adapters.motor_049 import Motor049Adapter
from runtime_orchestrator.congruence_intelligence import DILIGENCE_PACK_NAMES


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


def _building_public_inputs() -> dict:
    return {
        "motor_007": {
            "target_definition_contract": {
                "address_raw": "ONE VANDERBILT AVE, NEW YORK, NY 10017",
                "jurisdiction_scope": ["US-NY-NYC"],
                "target_type": "commercial_building",
                "target_name": "One Vanderbilt",
            },
            "target_classification_object": {
                "target_type": "OPERATING_ASSET",
                "classification_confidence": "high",
            },
        },
        "motor_012": {
            "facility_prior": {
                "target_definition": {
                    "target_type": "commercial_building",
                    "target_name": "One Vanderbilt",
                    "jurisdiction_scope": ["US-NY-NYC"],
                }
            },
            "asset_field_register": [
                _field("asset_class", "commercial_building"),
                _field("GFA", "1678135"),
            ],
        },
        "motor_028": {
            "source_register": [
                {
                    "source_id": "nyc_pluto::one-vanderbilt",
                    "title": "NYC PLUTO",
                    "url": "https://example.test/pluto",
                    "source_family": "geospatial_public_record",
                },
                {
                    "source_id": "nyc_ll84::one-vanderbilt",
                    "title": "NYC LL84",
                    "url": "https://example.test/ll84",
                    "source_family": "benchmarking_disclosure_record",
                },
            ]
        },
    }


def _manufacturing_hybrid_inputs() -> dict:
    return {
        "motor_007": {
            "target_definition_contract": {
                "address_raw": "TEMPLE, TX",
                "jurisdiction_scope": ["US-TX"],
                "target_type": "manufacturing_facility",
                "target_name": "Wilsonart Temple North Laminate Facility",
            },
            "target_classification_object": {
                "target_type": "OPERATING_ASSET",
                "classification_confidence": "high",
            },
        },
        "motor_012": {
            "facility_prior": {
                "target_definition": {
                    "target_type": "manufacturing_facility",
                    "target_name": "Wilsonart Temple North Laminate Facility",
                    "jurisdiction_scope": ["US-TX"],
                }
            },
            "asset_field_register": [
                _field("industry_context", "laminate manufacturing"),
                _field("process_signal", "thermal-mechanical batch process"),
            ],
        },
        "motor_028": {
            "source_register": [
                {
                    "source_id": "utility-bills::site",
                    "title": "Utility bills",
                    "url": "https://example.test/bills",
                    "source_family": "utility_bill_record",
                },
                {
                    "source_id": "utility-tariff::site",
                    "title": "Utility tariff",
                    "url": "https://example.test/tariff",
                    "source_family": "utility_tariff_record",
                },
                {
                    "source_id": "equipment::site",
                    "title": "Equipment inventory",
                    "url": "https://example.test/equipment",
                    "source_family": "equipment_inventory_record",
                },
                {
                    "source_id": "schedule::site",
                    "title": "Shift schedule",
                    "url": "https://example.test/schedule",
                    "source_family": "schedule_record",
                },
                {
                    "source_id": "maintenance-contract::site",
                    "title": "Maintenance contract",
                    "url": "https://example.test/maintenance-contract",
                    "source_family": "maintenance_contract_record",
                },
                {
                    "source_id": "permit::site",
                    "title": "Permit detail",
                    "url": "https://example.test/permit",
                    "source_family": "permit_record",
                },
            ]
        },
    }


def _building_operator_inputs() -> dict:
    return {
        "motor_007": {
            "target_definition_contract": {
                "address_raw": "ONE VANDERBILT AVE, NEW YORK, NY 10017",
                "jurisdiction_scope": ["US-NY-NYC"],
                "target_type": "commercial_building",
                "target_name": "One Vanderbilt",
            },
            "target_classification_object": {
                "target_type": "OPERATING_ASSET",
                "classification_confidence": "high",
            },
        },
        "motor_012": {
            "facility_prior": {
                "target_definition": {
                    "target_type": "commercial_building",
                    "target_name": "One Vanderbilt",
                    "jurisdiction_scope": ["US-NY-NYC"],
                }
            },
            "asset_field_register": [
                _field("asset_class", "commercial_building"),
            ],
        },
        "motor_028": {
            "source_register": [
                {
                    "source_id": "bills::site",
                    "title": "Utility bills",
                    "url": "https://example.test/bills",
                    "source_family": "utility_bill_record",
                },
                {
                    "source_id": "lease::site",
                    "title": "Lease matrix",
                    "url": "https://example.test/lease",
                    "source_family": "lease_matrix_record",
                },
                {
                    "source_id": "bms::site",
                    "title": "BMS trends",
                    "url": "https://example.test/bms",
                    "source_family": "bms_trend_record",
                },
                {
                    "source_id": "cmms::site",
                    "title": "CMMS export",
                    "url": "https://example.test/cmms",
                    "source_family": "cmms_record",
                },
                {
                    "source_id": "operator::site",
                    "title": "Operator notes",
                    "url": "https://example.test/operator",
                    "source_family": "operator_input_record",
                },
                {
                    "source_id": "tariff::site",
                    "title": "Tariff",
                    "url": "https://example.test/tariff",
                    "source_family": "utility_tariff_record",
                },
            ]
        },
    }


def _pack_map(out: dict) -> dict[str, dict]:
    return {
        str(row.get("pack_name", "")).strip(): row
        for row in list(out["operational_intake_pack"].get("diligence_pack_register", []) or [])
    }


def test_motor_049_emits_all_canonical_diligence_packs_for_public_screening():
    out = Motor049Adapter().run(_building_public_inputs())
    pack_map = _pack_map(out)

    assert set(pack_map) == set(DILIGENCE_PACK_NAMES)
    assert out["diligence_pack_count"] == len(DILIGENCE_PACK_NAMES)
    assert pack_map["utility_bill_pack"]["current_state"] == "requested_but_absent"
    assert pack_map["lease_responsibility_pack"]["current_state"] == "requested_but_absent"
    assert pack_map["permit_detail_pack"]["current_state"] == "requested_but_absent"


def test_motor_049_marks_hybrid_diligence_packs_as_partially_evidenced():
    out = Motor049Adapter().run(_manufacturing_hybrid_inputs())
    pack_map = _pack_map(out)

    assert out["research_mode"] == "hybrid_diligence"
    assert out["partially_evidenced_pack_count"] >= 4
    assert pack_map["utility_bill_pack"]["current_state"] == "partially_evidenced"
    assert pack_map["equipment_inventory_pack"]["current_state"] == "partially_evidenced"
    assert pack_map["throughput_schedule_pack"]["current_state"] == "partially_evidenced"
    assert pack_map["permit_detail_pack"]["current_state"] in {"partially_evidenced", "public_context_only"}
    assert pack_map["lease_responsibility_pack"]["current_state"] == "not_primary"


def test_motor_049_marks_operator_integrated_boundary_and_controls_packs():
    out = Motor049Adapter().run(_building_operator_inputs())
    pack_map = _pack_map(out)

    assert out["research_mode"] == "operator_integrated_congruence"
    assert out["partially_evidenced_pack_count"] >= 5
    assert pack_map["metering_boundary_pack"]["current_state"] == "partially_evidenced"
    assert pack_map["lease_responsibility_pack"]["current_state"] == "partially_evidenced"
    assert pack_map["bms_or_controls_pack"]["current_state"] == "partially_evidenced"
    assert pack_map["cmms_or_workorder_pack"]["current_state"] == "partially_evidenced"
    assert pack_map["utility_tariff_pack"]["current_state"] in {"partially_evidenced", "public_context_only"}
