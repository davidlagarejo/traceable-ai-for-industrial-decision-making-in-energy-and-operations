from __future__ import annotations

from runtime_orchestrator.adapters.motor_037 import Motor037Adapter
from runtime_orchestrator.adapters.motor_038 import Motor038Adapter
from runtime_orchestrator.adapters.motor_039 import Motor039Adapter
from runtime_orchestrator.adapters.motor_040 import Motor040Adapter
from runtime_orchestrator.adapters.motor_041 import Motor041Adapter
from runtime_orchestrator.adapters.motor_042 import Motor042Adapter
from runtime_orchestrator.adapters.motor_043 import Motor043Adapter
from runtime_orchestrator.adapters.motor_044 import Motor044Adapter
from runtime_orchestrator.adapters.motor_045 import Motor045Adapter
from runtime_orchestrator.adapters.motor_046 import Motor046Adapter


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
                "decision_intent": "Evaluate retrofit and LL97 strategy",
            },
            "target_classification_object": {"target_type": "OPERATING_ASSET", "classification_confidence": "high"},
        },
        "motor_012": {
            "facility_prior": {
                "target_definition": {
                    "target_type": "commercial_building",
                    "target_name": "One Vanderbilt",
                    "jurisdiction_scope": ["US-NY-NYC"],
                    "decision_intent": "Evaluate retrofit and LL97 strategy",
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
                "decision_intent": "Evaluate efficiency CAPEX",
            },
            "target_classification_object": {"target_type": "OPERATING_ASSET", "classification_confidence": "high"},
        },
        "motor_012": {
            "facility_prior": {
                "target_definition": {
                    "target_type": "manufacturing_facility",
                    "target_name": "Wilsonart Temple North Laminate Facility",
                    "jurisdiction_scope": ["US-TX"],
                    "decision_intent": "Evaluate efficiency CAPEX",
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
    m40 = Motor040Adapter().run({**inputs, "motor_039": m39, "motor_037": m37, "motor_038": m38})
    m41 = Motor041Adapter().run({**inputs, "motor_039": m39, "motor_037": m37, "motor_038": m38, "motor_040": m40})
    m42 = Motor042Adapter().run({**inputs, "motor_039": m39, "motor_037": m37, "motor_038": m38})
    m43 = Motor043Adapter().run({**inputs, "motor_039": m39, "motor_042": m42, "motor_012": inputs["motor_012"], "motor_007": inputs["motor_007"]})
    m44 = Motor044Adapter().run({**inputs, "motor_038": m38, "motor_040": m40, "motor_041": m41, "motor_043": m43})
    m45 = Motor045Adapter().run({**inputs, "motor_037": m37, "motor_038": m38, "motor_040": m40, "motor_041": m41, "motor_043": m43, "motor_044": m44})
    m46 = Motor046Adapter().run({**inputs, "motor_038": m38, "motor_040": m40, "motor_041": m41, "motor_044": m44})
    return {"motor_044": m44, "motor_045": m45, "motor_046": m46}


def test_motor_044_building_outputs_owner_tenant_redesign_hypothesis():
    out = _run_lane(_building_inputs())
    rows = out["motor_044"]["conditional_redesign_register"]
    assert any("Tenant-driven loads" in row["hypothesis"] for row in rows)
    assert any("green leases" in row["redesign_direction"] or "Submetering" in row["redesign_direction"] for row in rows)
    assert all(row["trigger_hypothesis"] for row in rows)
    assert all(row["conflict_resolved"] for row in rows)
    assert all(row["economic_logic"] for row in rows)
    assert all(row["kill_condition"] for row in rows)
    assert all(row["evidence_state"] in {"CONDITIONAL_HYPOTHESIS", "OBSERVED_FACT", "ARCHETYPAL_PRIOR"} for row in rows)


def test_motor_044_manufacturing_outputs_structural_load_vs_support_waste_hypothesis():
    out = _run_lane(_manufacturing_inputs())
    rows = out["motor_044"]["conditional_redesign_register"]
    assert any("structurally tied to throughput" in row["hypothesis"] for row in rows)
    assert any("compressed air" in row["if_falsified"].lower() for row in rows)


def test_motor_043_building_peer_comparison_is_bounded_and_non_superiority_claim():
    inputs = _building_inputs()
    m39 = Motor039Adapter().run(inputs)
    m37 = Motor037Adapter().run({**inputs, "motor_039": m39})
    m38 = Motor038Adapter().run({**inputs, "motor_039": m39, "motor_037": m37})
    m42 = Motor042Adapter().run({**inputs, "motor_039": m39, "motor_037": m37, "motor_038": m38})
    rows = Motor043Adapter().run({**inputs, "motor_039": m39, "motor_042": m42, "motor_012": inputs["motor_012"], "motor_007": inputs["motor_007"]})["competitive_comparison_register"]

    assert rows
    assert all(row["peer_type"] for row in rows)
    assert all(row["what_it_proves"] for row in rows)
    assert all(row["what_it_does_not_prove"] for row in rows)


def test_motor_045_building_blocks_roi_and_payback_outputs():
    out = _run_lane(_building_inputs())
    rows = out["motor_045"]["structural_financial_exposure_register"]
    assert any("owner-controllable savings" in row["structural_assumption"] for row in rows)
    assert any("ROI" in row["prohibited_financial_output"] for row in rows)
    assert all("savings claim" in row["prohibited_financial_output"] for row in rows)


def test_motor_045_manufacturing_translates_structural_load_to_capex_risk():
    out = _run_lane(_manufacturing_inputs())
    rows = out["motor_045"]["structural_financial_exposure_register"]
    assert any("Process energy is correctable waste" in row["structural_assumption"] for row in rows)
    assert any("structural process load" in row["financial_exposure_if_wrong"] for row in rows)


def test_motor_045_building_emits_complete_evidence_state_by_layer_register():
    out = _run_lane(_building_inputs())
    rows = out["motor_045"]["evidence_state_by_layer_register"]
    row_map = {row["layer"]: row for row in rows}

    assert out["motor_045"]["evidence_state_by_layer_count"] == 12
    assert {
        "physics",
        "operation",
        "energy",
        "finance",
        "regulation",
        "maintenance",
        "logistics",
        "procurement",
        "commercial",
        "culture",
        "control/responsibility",
        "market/competitiveness",
    } == set(row_map)
    assert row_map["regulation"]["evidence_state"] == "OBSERVED_FACT"
    assert row_map["finance"]["evidence_state"] == "CONDITIONAL_HYPOTHESIS"
    assert row_map["control/responsibility"]["dominant_open_questions"]
    assert row_map["market/competitiveness"]["structural_risk_if_wrong"]


def test_motor_045_manufacturing_emits_complete_evidence_state_by_layer_register():
    out = _run_lane(_manufacturing_inputs())
    rows = out["motor_045"]["evidence_state_by_layer_register"]
    row_map = {row["layer"]: row for row in rows}

    assert out["motor_045"]["evidence_state_by_layer_count"] == 12
    assert row_map["physics"]["evidence_state"] == "CONDITIONAL_HYPOTHESIS"
    assert row_map["maintenance"]["evidence_state"] == "CONDITIONAL_HYPOTHESIS"
    assert row_map["regulation"]["evidence_state"] == "OBSERVED_FACT"
    assert row_map["procurement"]["dominant_open_questions"]
    assert row_map["commercial"]["structural_risk_if_wrong"]


def test_motor_046_building_requests_discriminating_evidence_not_generic_checklist():
    out = _run_lane(_building_inputs())
    rows = out["motor_046"]["minimum_evidence_for_discrimination_register"]
    assert any("tenant metering map" in row["minimum_evidence"] for row in rows)
    assert any("Owner-controllable base-building upside dominates." in row["rival_hypotheses"] for row in rows)


def test_motor_046_manufacturing_requests_throughput_utility_equipment_and_downtime():
    out = _run_lane(_manufacturing_inputs())
    rows = out["motor_046"]["minimum_evidence_for_discrimination_register"]
    assert any("Throughput by shift + utility bills + equipment inventory + downtime logs" == row["minimum_evidence"] for row in rows)
    assert any("capital sequencing" in row["unlocks"] for row in rows)
