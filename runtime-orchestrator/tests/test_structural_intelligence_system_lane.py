from __future__ import annotations

from runtime_orchestrator.adapters.motor_037 import Motor037Adapter
from runtime_orchestrator.adapters.motor_038 import Motor038Adapter
from runtime_orchestrator.adapters.motor_039 import Motor039Adapter


def _field(field: str, value: str, *, source_id: str = "test::field") -> dict:
    return {
        "field": field,
        "value": value,
        "status": "OBSERVED",
        "scope": "ASSET_LEVEL",
        "authority_score": "high",
        "admissibility": "CONFIRMED_ASSET_LEVEL",
        "source_id": source_id,
        "notes": "",
    }


def _nyc_building_inputs() -> dict:
    return {
        "motor_001": {},
        "motor_007": {
            "target_definition_contract": {
                "target_type": "commercial_building",
                "target_name": "One Vanderbilt",
                "jurisdiction_scope": ["US-NY-NYC"],
            },
            "target_classification_object": {"target_type": "OPERATING_ASSET", "classification_confidence": "high"},
        },
        "motor_012": {
            "canonical_asset_context_summary": {
                "screening_supported": True,
                "supported_field_register": [
                    {"field": "GFA"},
                    {"field": "floor_count"},
                    {"field": "current_EUI"},
                ],
            },
            "facility_prior": {
                "asset_name": "One Vanderbilt",
                "target_definition": {
                    "target_type": "commercial_building",
                    "target_name": "One Vanderbilt",
                    "jurisdiction_scope": ["US-NY-NYC"],
                },
            },
            "asset_field_register": [
                _field("GFA", "1700000", source_id="nyc_pluto::one-vanderbilt"),
                _field("floor_count", "73", source_id="nyc_pluto::one-vanderbilt"),
                _field("current_EUI", "72.1", source_id="nyc_ll84::one-vanderbilt"),
            ],
            "dataset_coverage_register": [
                {"dataset_key": "nyc_pluto_property", "status": "accepted"},
                {"dataset_key": "nyc_ll84_energy_benchmarking", "status": "accepted"},
                {"dataset_key": "nyc_ll97_covered_buildings_list", "status": "accepted"},
            ],
        },
        "motor_028": {
            "source_register": [
                {"source_type": "nyc_pluto_property", "accepted": True},
                {"source_type": "nyc_ll84_energy_benchmarking", "accepted": True},
            ]
        },
    }


def _wilsonart_inputs() -> dict:
    return {
        "motor_001": {},
        "motor_007": {
            "target_definition_contract": {
                "target_type": "manufacturing_facility",
                "target_name": "Wilsonart Temple North Laminate Facility",
                "jurisdiction_scope": ["US-TX"],
            },
            "target_classification_object": {"target_type": "OPERATING_ASSET", "classification_confidence": "high"},
        },
        "motor_012": {
            "canonical_asset_context_summary": {
                "screening_supported": False,
                "supported_field_register": [{"field": "address"}, {"field": "asset_class"}],
            },
            "facility_prior": {
                "asset_name": "Wilsonart Temple North Laminate Facility",
                "target_definition": {
                    "target_type": "manufacturing_facility",
                    "target_name": "Wilsonart Temple North Laminate Facility",
                    "jurisdiction_scope": ["US-TX"],
                },
            },
            "asset_field_register": [
                _field("process_flow", "Public process description for laminate production", source_id="company_facility_page::wilsonart"),
                _field("load_driver", "Laminate pressing and curing duty", source_id="company_facility_page::wilsonart"),
                _field("operating_schedule", "proxy: multi-shift manufacturing operations", source_id="company_facility_page::wilsonart"),
            ],
            "dataset_coverage_register": [
                {"dataset_key": "tceq_permits_and_emissions", "status": "accepted"},
            ],
        },
        "motor_028": {
            "source_register": [
                {"source_type": "tceq_air_permit", "accepted": True},
                {"source_type": "epa_echo", "accepted": True},
            ]
        },
    }


def test_motor_037_building_outputs_observed_regulatory_and_conditional_control_structure():
    inputs = _nyc_building_inputs()
    m39 = Motor039Adapter().run(inputs)
    out = Motor037Adapter().run({**inputs, "motor_039": m39})
    abstraction = out["system_abstraction"]

    assert abstraction["asset_type"]["evidence_state"] == "OBSERVED_FACT"
    assert abstraction["regulatory_exposure"]["evidence_state"] == "OBSERVED_FACT"
    assert abstraction["control_structure"]["evidence_state"] == "CONDITIONAL_HYPOTHESIS"
    assert "LL97" in abstraction["regulatory_exposure"]["statement"]


def test_motor_037_manufacturing_keeps_process_type_conditional_not_observed_truth():
    inputs = _wilsonart_inputs()
    m39 = Motor039Adapter().run(inputs)
    out = Motor037Adapter().run({**inputs, "motor_039": m39})
    abstraction = out["system_abstraction"]

    assert abstraction["dominant_process_type"]["evidence_state"] == "CONDITIONAL_HYPOTHESIS"
    assert abstraction["business_function"]["evidence_state"] == "ARCHETYPAL_PRIOR"
    assert abstraction["regulatory_exposure"]["evidence_state"] == "OBSERVED_FACT"


def test_motor_038_building_includes_expected_dominant_variables():
    inputs = _nyc_building_inputs()
    m39 = Motor039Adapter().run(inputs)
    m37 = Motor037Adapter().run({**inputs, "motor_039": m39})
    out = Motor038Adapter().run({**inputs, "motor_039": m39, "motor_037": m37})

    names = {row["variable"] for row in out["dominant_variable_register"]}
    evidence = {row["variable"]: row["evidence_state"] for row in out["dominant_variable_register"]}

    assert {"central_plant", "tenant_metering", "LL97_pathway", "owner_control_boundary"} <= names
    assert evidence["LL97_pathway"] == "OBSERVED_FACT"
    assert evidence["central_plant"] == "CONDITIONAL_HYPOTHESIS"


def test_motor_038_manufacturing_includes_expected_dominant_variables():
    inputs = _wilsonart_inputs()
    m39 = Motor039Adapter().run(inputs)
    m37 = Motor037Adapter().run({**inputs, "motor_039": m39})
    out = Motor038Adapter().run({**inputs, "motor_039": m39, "motor_037": m37})

    names = {row["variable"] for row in out["dominant_variable_register"]}
    evidence = {row["variable"]: row["evidence_state"] for row in out["dominant_variable_register"]}

    assert {"throughput", "thermal_duty", "compressed_air", "downtime"} <= names
    assert evidence["throughput"] == "CONDITIONAL_HYPOTHESIS"
    assert evidence["compressed_air"] == "CONDITIONAL_HYPOTHESIS"

