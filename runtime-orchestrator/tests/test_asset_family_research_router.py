from __future__ import annotations

from runtime_orchestrator.adapters.motor_049 import Motor049Adapter
from runtime_orchestrator.congruence_intelligence import source_policy


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
                "dataset_coverage_register": [
                    {"dataset_key": "nyc_pluto", "status": "accepted"},
                    {"dataset_key": "nyc_ll84_benchmarking", "status": "accepted"},
                ],
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
                {
                    "source_id": "nyc_dof::one-vanderbilt",
                    "title": "NYC DOF",
                    "url": "https://example.test/dof",
                    "source_family": "property_record",
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
                }
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


def _weak_warehouse_inputs() -> dict:
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
            "facility_prior": {
                "target_definition": {
                    "target_type": "warehouse_distribution_asset",
                    "target_name": "Warehouse candidate",
                    "jurisdiction_scope": ["US-TX"],
                }
            },
            "asset_field_register": [
                _field("address", "123 TEST ASSET WAY, AUSTIN, TX 78701"),
            ],
        },
        "motor_028": {"source_register": []},
    }


def test_motor_049_routes_one_vanderbilt_to_commercial_building_public_screening():
    out = Motor049Adapter().run(_building_inputs())

    assert out["selected_asset_family"] == "commercial_building"
    assert out["research_mode"] == "public_only_screening"
    assert out["route_state"] == "operational_asset_candidate"
    assert "benchmarking_disclosure_record" in out["asset_family_research_profile"]["authoritative_source_families"]
    assert out["operational_intake_pack"]["asset_identity_pack"]["classification_state"] == "OPERATING_ASSET"
    assert out["local_evidence_binding_register"][0]["current_local_binding_state"] == "public_context_only_unbound"


def test_motor_049_routes_wilsonart_to_industrial_manufacturing_and_requests_process_binding():
    out = Motor049Adapter().run(_manufacturing_inputs())

    assert out["selected_asset_family"] == "industrial_manufacturing"
    assert "throughput by shift" in out["local_evidence_binding_register"][0]["local_binding_needed"]
    assert "technical_sourcebook_record" in out["asset_family_research_profile"]["authoritative_source_families"]
    assert out["operational_intake_pack"]["process_overview_pack"]["current_state"] == "research_seed_only"


def test_motor_049_degrades_unbounded_warehouse_candidate_without_fabricating_local_truth():
    out = Motor049Adapter().run(_weak_warehouse_inputs())

    assert out["selected_asset_family"] == "logistics_warehouse"
    assert out["route_state"] == "target_not_yet_operationally_bounded"
    assert out["local_evidence_binding_register"][0]["current_local_binding_state"] == "inadmissible_until_asset_identity_bounded"
    assert out["operational_intake_pack"]["asset_identity_pack"]["classification_state"] == "REGISTERED_AGENT_OR_MAILING_ADDRESS"


def test_source_policy_marks_vendor_material_as_non_diagnostic():
    policy = source_policy("vendor_implementation_record")

    assert policy["source_tier"] == "tier_3_vendor_or_secondary"
    assert "local_dominant_loss_diagnosis" in policy["prohibited_inference_class"]
