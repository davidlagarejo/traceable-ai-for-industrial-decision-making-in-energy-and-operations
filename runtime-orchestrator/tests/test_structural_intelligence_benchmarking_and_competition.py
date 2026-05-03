from __future__ import annotations

from runtime_orchestrator.adapters.motor_037 import Motor037Adapter
from runtime_orchestrator.adapters.motor_038 import Motor038Adapter
from runtime_orchestrator.adapters.motor_039 import Motor039Adapter
from runtime_orchestrator.adapters.motor_042 import Motor042Adapter
from runtime_orchestrator.adapters.motor_043 import Motor043Adapter


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


def _building_inputs() -> dict:
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
            "facility_prior": {
                "target_definition": {
                    "target_type": "commercial_building",
                    "target_name": "One Vanderbilt",
                    "jurisdiction_scope": ["US-NY-NYC"],
                }
            },
            "canonical_asset_context_summary": {
                "screening_supported": True,
                "supported_field_register": [{"field": "GFA"}, {"field": "current_EUI"}],
            },
            "asset_field_register": [
                _field("GFA", "1700000", source_id="nyc_pluto::one-vanderbilt"),
                _field("current_EUI", "72.1", source_id="nyc_ll84::one-vanderbilt"),
            ],
            "dataset_coverage_register": [
                {"dataset_key": "nyc_ll84_energy_benchmarking", "status": "accepted"},
                {"dataset_key": "nyc_ll97_covered_buildings_list", "status": "accepted"},
                {"dataset_key": "nyc_pluto_property", "status": "accepted"},
            ],
        },
        "motor_028": {"source_register": [{"source_type": "nyc_ll84_energy_benchmarking", "accepted": True}]},
    }


def _manufacturing_inputs() -> dict:
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
            "facility_prior": {
                "target_definition": {
                    "target_type": "manufacturing_facility",
                    "target_name": "Wilsonart Temple North Laminate Facility",
                    "jurisdiction_scope": ["US-TX"],
                }
            },
            "canonical_asset_context_summary": {
                "screening_supported": False,
                "supported_field_register": [{"field": "address"}, {"field": "asset_class"}],
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
        "motor_028": {"source_register": [{"source_type": "tceq_air_permit", "accepted": True}]},
    }


def _run_lane(inputs: dict) -> dict:
    m39 = Motor039Adapter().run(inputs)
    m37 = Motor037Adapter().run({**inputs, "motor_039": m39})
    m38 = Motor038Adapter().run({**inputs, "motor_039": m39, "motor_037": m37})
    m42 = Motor042Adapter().run({**inputs, "motor_039": m39, "motor_037": m37, "motor_038": m38})
    m43 = Motor043Adapter().run({**inputs, "motor_039": m39, "motor_042": m42, "motor_012": inputs["motor_012"], "motor_007": inputs["motor_007"]})
    return {"motor_039": m39, "motor_037": m37, "motor_038": m38, "motor_042": m42, "motor_043": m43}


def test_motor_042_building_produces_bounded_structural_benchmark_rows():
    out = _run_lane(_building_inputs())
    rows = out["motor_042"]["structural_benchmark_register"]
    dimensions = {row["dimension"] for row in rows}
    assert "compliance and public screening context" in dimensions
    assert any("Class A NYC" in row["peer_or_benchmark"] for row in rows)
    assert all(row["evidence_state"] in {"OBSERVED_FACT", "CONDITIONAL_HYPOTHESIS", "ARCHETYPAL_PRIOR"} for row in rows)


def test_motor_042_manufacturing_keeps_process_benchmark_bounded():
    out = _run_lane(_manufacturing_inputs())
    rows = out["motor_042"]["structural_benchmark_register"]
    assert any("thermal-process laminate" in row["peer_or_benchmark"] for row in rows)
    assert any("Do not map benchmark intensity directly to waste" in row["interpretation"] for row in rows)


def test_motor_043_building_outputs_conditional_competitive_comparison():
    out = _run_lane(_building_inputs())
    rows = out["motor_043"]["competitive_comparison_register"]
    assert any(row["comparison_mode"] in {"conditional_comparison", "archetypal_best_practice"} for row in rows)
    assert any("green-lease" in row["what_they_do_better"] or "submetering" in row["what_they_do_better"] for row in rows)
    assert all(row["evidence_state"] in {"CONDITIONAL_HYPOTHESIS", "ARCHETYPAL_PRIOR", "OBSERVED_FACT"} for row in rows)


def test_motor_043_manufacturing_outputs_process_and_uptime_framing():
    out = _run_lane(_manufacturing_inputs())
    rows = out["motor_043"]["competitive_comparison_register"]
    assert any("thermal integration" in row["what_they_do_better"] or "uptime" in row["structural_advantage"].lower() for row in rows)
    assert any("process map" in row["evidence_needed"] for row in rows)

