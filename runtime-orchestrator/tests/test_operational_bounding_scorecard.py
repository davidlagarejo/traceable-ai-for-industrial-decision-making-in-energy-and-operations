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


def _building_public_inputs() -> dict:
    return {
        "motor_007": {
            "target_definition_contract": {
                "address_raw": "ONE VANDERBILT AVE, NEW YORK, NY 10017",
                "jurisdiction_scope": ["US-NY-NYC"],
                "target_type": "commercial_building",
                "target_name": "One Vanderbilt",
            },
            "target_classification_object": {"target_type": "OPERATING_ASSET", "classification_confidence": "high"},
        },
        "motor_012": {
            "facility_prior": {"target_definition": {"target_type": "commercial_building", "jurisdiction_scope": ["US-NY-NYC"]}},
            "asset_field_register": [_field("asset_class", "commercial_building")],
        },
        "motor_028": {
            "source_register": [
                {"source_id": "ll84::site", "source_family": "benchmarking_disclosure_record", "title": "LL84"},
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
                "target_name": "Wilsonart",
            },
            "target_classification_object": {"target_type": "OPERATING_ASSET", "classification_confidence": "high"},
        },
        "motor_012": {
            "facility_prior": {"target_definition": {"target_type": "manufacturing_facility", "jurisdiction_scope": ["US-TX"]}},
            "asset_field_register": [_field("asset_class", "manufacturing_facility")],
        },
        "motor_028": {
            "source_register": [
                {"source_id": "bill::site", "source_family": "utility_bill_record", "title": "Utility bill"},
                {"source_id": "tariff::site", "source_family": "utility_tariff_record", "title": "Tariff"},
                {"source_id": "equipment::site", "source_family": "equipment_inventory_record", "title": "Equipment"},
                {"source_id": "schedule::site", "source_family": "schedule_record", "title": "Schedule"},
                {"source_id": "permit::site", "source_family": "permit_record", "title": "Permit"},
                {"source_id": "maintenance::site", "source_family": "maintenance_contract_record", "title": "Maintenance contract"},
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
            "target_classification_object": {"target_type": "OPERATING_ASSET", "classification_confidence": "high"},
        },
        "motor_012": {
            "facility_prior": {"target_definition": {"target_type": "commercial_building", "jurisdiction_scope": ["US-NY-NYC"]}},
            "asset_field_register": [_field("asset_class", "commercial_building")],
        },
        "motor_028": {
            "source_register": [
                {"source_id": "bill::site", "source_family": "utility_bill_record", "title": "Utility bill"},
                {"source_id": "lease::site", "source_family": "lease_matrix_record", "title": "Lease matrix"},
                {"source_id": "bms::site", "source_family": "bms_trend_record", "title": "BMS trend"},
                {"source_id": "cmms::site", "source_family": "cmms_record", "title": "CMMS"},
                {"source_id": "operator::site", "source_family": "operator_input_record", "title": "Operator input"},
                {"source_id": "maintenance::site", "source_family": "maintenance_log_record", "title": "Maintenance log"},
            ]
        },
    }


def _weak_candidate_inputs() -> dict:
    return {
        "motor_007": {
            "target_definition_contract": {
                "address_raw": "123 TEST ASSET WAY, AUSTIN, TX 78701",
                "jurisdiction_scope": ["US-TX"],
                "target_type": "warehouse_distribution_asset",
                "target_name": "Warehouse candidate",
            },
            "target_classification_object": {
                "target_type": "REGISTERED_AGENT_OR_MAILING_ADDRESS",
                "classification_confidence": "medium",
            },
        },
        "motor_012": {
            "facility_prior": {"target_definition": {"target_type": "warehouse_distribution_asset", "jurisdiction_scope": ["US-TX"]}},
            "asset_field_register": [_field("address", "123 TEST ASSET WAY, AUSTIN, TX 78701")],
        },
        "motor_028": {"source_register": []},
    }


def test_motor_049_public_screening_scorecard_stays_public_with_hybrid_blockers():
    out = Motor049Adapter().run(_building_public_inputs())
    scorecard = out["operational_bounding_scorecard"]

    assert scorecard["evidence_mode_state"] == "public_only_screening"
    assert scorecard["bounded_asset_gate_passed"] is True
    assert scorecard["next_promotable_mode"] == "hybrid_diligence"
    assert out["promotion_blocker_count"] >= 1


def test_motor_049_hybrid_scorecard_promotes_manufacturing_case_to_hybrid_diligence():
    out = Motor049Adapter().run(_manufacturing_hybrid_inputs())
    scorecard = out["operational_bounding_scorecard"]

    assert out["research_mode"] == "hybrid_diligence"
    assert out["evidence_mode_state"] == "hybrid_diligence"
    assert scorecard["hybrid_score"] >= scorecard["required_hybrid_count"]
    assert scorecard["operator_score"] < scorecard["required_operator_count"]
    assert scorecard["next_promotable_mode"] == "operator_integrated_congruence"


def test_motor_049_operator_scorecard_promotes_building_case_to_operator_integrated():
    out = Motor049Adapter().run(_building_operator_inputs())
    scorecard = out["operational_bounding_scorecard"]

    assert out["research_mode"] == "operator_integrated_congruence"
    assert out["evidence_mode_state"] == "operator_integrated_congruence"
    assert scorecard["hybrid_score"] >= scorecard["required_hybrid_count"]
    assert scorecard["operator_score"] >= scorecard["required_operator_count"]
    assert scorecard["next_promotable_mode"] == ""


def test_motor_049_unbounded_candidate_keeps_route_blocker():
    out = Motor049Adapter().run(_weak_candidate_inputs())
    scorecard = out["operational_bounding_scorecard"]

    assert scorecard["bounded_asset_gate_passed"] is False
    assert out["evidence_mode_state"] == "public_only_screening"
    blocker_codes = {row["blocker_code"] for row in out["promotion_blocker_register"]}
    assert "asset_not_operationally_bounded" in blocker_codes
