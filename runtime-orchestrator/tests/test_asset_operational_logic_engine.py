from __future__ import annotations

from runtime_orchestrator.adapters.motor_049 import Motor049Adapter
from runtime_orchestrator.adapters.motor_050 import Motor050Adapter


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


def _building_inputs() -> dict:
    return {
        "motor_007": {
            "target_definition_contract": {
                "address_raw": "ONE VANDERBILT AVE, NEW YORK, NY 10017",
                "jurisdiction_scope": ["US-NY-NYC"],
                "target_type": "commercial_building",
                "target_name": "One Vanderbilt",
                "decision_intent": "Assess LL97 and retrofit pathway",
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
                },
            },
            "asset_field_register": [
                _field("asset_class", "commercial_building"),
                _field("GFA", "1678135"),
                _field("current_EUI", "72.1"),
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


def _manufacturing_inputs() -> dict:
    return {
        "motor_007": {
            "target_definition_contract": {
                "address_raw": "TEMPLE, TX",
                "jurisdiction_scope": ["US-TX"],
                "target_type": "manufacturing_facility",
                "target_name": "Wilsonart Temple North Laminate Facility",
                "decision_intent": "Assess process load and redesign",
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
                },
            },
            "asset_field_register": [
                _field("asset_class", "manufacturing_facility"),
                _field("industry_context", "laminate manufacturing"),
                _field("process_signal", "thermal-mechanical batch process"),
            ],
        },
        "motor_028": {
            "source_register": [
                {
                    "source_id": "tceq::site",
                    "title": "TCEQ permit coverage",
                    "url": "https://example.test/tceq",
                    "source_family": "regulatory_coverage_record",
                },
                {
                    "source_id": "doe::sourcebook",
                    "title": "DOE sourcebook",
                    "url": "https://example.test/doe",
                    "source_family": "technical_sourcebook_record",
                },
            ]
        },
    }


def _bounded_warehouse_inputs() -> dict:
    return {
        "motor_007": {
            "target_definition_contract": {
                "address_raw": "500 DISTRIBUTION LOOP, DALLAS, TX 75001",
                "jurisdiction_scope": ["US-TX"],
                "target_type": "warehouse_distribution_asset",
                "target_name": "Regional distribution warehouse",
                "decision_intent": "Assess warehouse operating cost drivers",
            },
            "target_classification_object": {
                "target_type": "OPERATING_ASSET",
                "classification_confidence": "high",
            },
        },
        "motor_012": {
            "facility_prior": {
                "target_definition": {
                    "target_type": "warehouse_distribution_asset",
                    "target_name": "Regional distribution warehouse",
                    "jurisdiction_scope": ["US-TX"],
                },
            },
            "asset_field_register": [
                _field("asset_class", "warehouse_distribution_asset"),
                _field("dock_count", "24"),
                _field("schedule", "two-shift warehouse operation"),
            ],
        },
        "motor_028": {
            "source_register": [
                {
                    "source_id": "county_property::warehouse",
                    "title": "County property record",
                    "url": "https://example.test/property",
                    "source_family": "property_record",
                }
            ]
        },
    }


def _run(inputs: dict) -> dict:
    m49 = Motor049Adapter().run(inputs)
    return Motor050Adapter().run({**inputs, "motor_049": m49})


def test_motor_050_building_outputs_control_boundary_and_service_logic():
    out = _run(_building_inputs())

    assert out["operational_logic_state"] == "research_seeded_operational_logic"
    assert out["process_map"]["asset_family"] == "commercial_building"
    assert out["process_map"]["transformations"][0]["stage"] == "building_services_delivery"
    subsystem_names = {row["subsystem_name"] for row in out["subsystem_register"]}
    assert "HVAC / central plant" in subsystem_names
    boundary_names = {row["boundary_name"] for row in out["control_boundary_map"]}
    assert "owner_vs_tenant_load_boundary" in boundary_names


def test_motor_050_manufacturing_outputs_process_vs_support_boundary():
    out = _run(_manufacturing_inputs())

    assert out["process_map"]["asset_family"] == "industrial_manufacturing"
    assert out["process_map"]["loss_points"][0]["stage"] == "process_vs_waste_ambiguity"
    subsystem_names = {row["subsystem_name"] for row in out["subsystem_register"]}
    assert "compressed air" in subsystem_names
    boundary_names = {row["boundary_name"] for row in out["control_boundary_map"]}
    assert "process_load_vs_support_system_load" in boundary_names


def test_motor_050_logistics_outputs_movement_and_service_level_logic():
    out = _run(_bounded_warehouse_inputs())

    assert out["process_map"]["asset_family"] == "logistics_warehouse"
    assert out["process_map"]["market_value_link"][0]["stage"] == "service_level_cost_tradeoff"
    subsystem_names = {row["subsystem_name"] for row in out["subsystem_register"]}
    assert "dock and door systems" in subsystem_names
    assert out["equipment_dominance_count"] > 0


def test_motor_050_degrades_unbounded_target_to_inadmissible_operational_logic():
    inputs = {
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
            "facility_prior": {
                "target_definition": {
                    "target_type": "warehouse_distribution_asset",
                    "target_name": "Warehouse candidate",
                    "jurisdiction_scope": ["US-TX"],
                },
            },
            "asset_field_register": [_field("address", "123 TEST ASSET WAY, AUSTIN, TX 78701")],
        },
        "motor_028": {"source_register": []},
    }
    out = _run(inputs)

    assert out["operational_logic_state"] == "inadmissible_until_asset_identity_bounded"
    assert out["subsystem_register"] == []
    assert out["control_boundary_map"] == []
