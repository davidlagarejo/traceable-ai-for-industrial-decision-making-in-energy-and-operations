from __future__ import annotations

from runtime_orchestrator.adapters.motor_049 import Motor049Adapter
from runtime_orchestrator.adapters.motor_050 import Motor050Adapter
from runtime_orchestrator.adapters.motor_051 import Motor051Adapter
from runtime_orchestrator.adapters.motor_052 import Motor052Adapter
from runtime_orchestrator.adapters.motor_053 import Motor053Adapter


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


def _warehouse_inputs() -> dict:
    return {
        "motor_007": {
            "target_definition_contract": {
                "address_raw": "1450 Logistics Parkway, Dallas, TX 75201",
                "jurisdiction_scope": ["US-TX"],
                "target_type": "warehouse_distribution",
                "target_name": "Sunrise Logistics Hub",
            },
            "target_classification_object": {"target_type": "OPERATING_ASSET", "classification_confidence": "high"},
        },
        "motor_012": {
            "facility_prior": {"target_definition": {"target_type": "warehouse_distribution", "jurisdiction_scope": ["US-TX"]}},
            "asset_field_register": [_field("asset_class", "warehouse_distribution")],
        },
        "motor_028": {
            "source_register": [],
            "search_budget_register": [
                {
                    "budget_scope": "total_public_discovery",
                    "budget_state": "bounded",
                    "budget_class": "bounded_public_discovery",
                }
            ],
            "search_attempt_ledger": [],
            "search_attempt_outcome_register": [],
            "search_exhaustion_register": [],
            "discovery_need_register": [
                {"need_id": "dock_and_service_intensity", "discovery_need": "Bound dock density and service-level intensity."},
                {"need_id": "operator_boundary_and_control", "discovery_need": "Confirm tenant / operator boundary and who controls docks, charging, and schedules."},
                {"need_id": "mhe_charging_and_mechanical_clues", "discovery_need": "Look for motive-power charging and roof/HVAC/mechanical clues."},
                {"need_id": "utility_territory_and_tariff_context", "discovery_need": "Confirm utility territory and tariff context."},
            ],
            "search_family_execution_plan": [],
            "accepted_evidence_type_register": [],
            "discovery_stop_condition_register": [],
            "next_best_search_register": [],
            "search_target_priority_register": [],
            "search_success_effect_register": [],
            "search_failure_effect_register": [],
        },
    }


def _building_inputs() -> dict:
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
        "motor_028": {"source_register": []},
    }


def _manufacturing_inputs() -> dict:
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
        "motor_028": {"source_register": []},
    }


def _run(inputs: dict) -> dict:
    m49 = Motor049Adapter().run(inputs)
    m50 = Motor050Adapter().run({**inputs, "motor_049": m49})
    m51 = Motor051Adapter().run({**inputs, "motor_049": m49, "motor_050": m50})
    m52 = Motor052Adapter().run({**inputs, "motor_049": m49, "motor_050": m50, "motor_051": m51})
    return Motor053Adapter().run({**inputs, "motor_049": m49, "motor_050": m50, "motor_051": m51, "motor_052": m52})


def test_warehouse_financial_exposure_type_engine_emits_tariff_peer_and_value_leakage_types():
    out = _run(_warehouse_inputs())

    exposure_types = {row["financial_exposure_type"] for row in out["financial_exposure_type_register"]}
    assert "wrong_peer_valuation" in exposure_types
    assert "tariff_exposure_hidden" in exposure_types
    assert "demand_charge_exposure" in exposure_types
    assert "operational_savings_not_capturable" in exposure_types
    assert "tenant_operator_value_leakage" in exposure_types

    by_type = {row["financial_exposure_type"]: row for row in out["financial_exposure_type_register"]}
    assert by_type["wrong_peer_valuation"]["evidence_needed"]
    assert "BUILD_FAIR_PEER_SET" in by_type["wrong_peer_valuation"]["tad_consequence"]
    assert "VALIDATE_TARIFF_EXPOSURE" in by_type["tariff_exposure_hidden"]["tad_consequence"]

    leakage_types = {row["financial_exposure_type"] for row in out["value_leakage_register"]}
    assert "operational_savings_not_capturable" in leakage_types
    assert "tenant_operator_value_leakage" in leakage_types
    skill_categories = {row["governed_exposure_category"] for row in out["skill_financial_exposure_register"]}
    assert "wrong peer valuation" in skill_categories
    assert "tariff exposure" in skill_categories
    assert "hidden demand charge exposure" in skill_categories
    assert "boundary leakage" in skill_categories


def test_building_and_manufacturing_financial_exposure_types_cover_capex_compliance_and_downtime():
    building = _run(_building_inputs())
    manufacturing = _run(_manufacturing_inputs())

    building_types = {row["financial_exposure_type"] for row in building["financial_exposure_type_register"]}
    assert "CAPEX_misallocated" in building_types
    assert "compliance_exposure_misunderstood" in building_types

    manufacturing_types = {row["financial_exposure_type"] for row in manufacturing["financial_exposure_type_register"]}
    assert "CAPEX_misallocated" in manufacturing_types
    assert "maintenance_downtime_exposure" in manufacturing_types
    assert "wrong_retrofit_sequencing" in manufacturing_types

    underwriting_types = {row["financial_exposure_type"] for row in manufacturing["underwriting_misread_register"]}
    assert "CAPEX_misallocated" in underwriting_types
    manufacturing_skill_categories = {
        row["governed_exposure_category"] for row in manufacturing["skill_financial_exposure_register"]
    }
    assert "CAPEX misallocation risk" in manufacturing_skill_categories
    assert "maintenance downtime exposure" in manufacturing_skill_categories
