from __future__ import annotations

from runtime_orchestrator.adapters.motor_037 import Motor037Adapter
from runtime_orchestrator.adapters.motor_038 import Motor038Adapter
from runtime_orchestrator.adapters.motor_039 import Motor039Adapter
from runtime_orchestrator.adapters.motor_040 import Motor040Adapter
from runtime_orchestrator.adapters.motor_041 import Motor041Adapter


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
                "decision_intent": "Assess LL97 and retrofit pathway",
            },
            "target_classification_object": {"target_type": "OPERATING_ASSET", "classification_confidence": "high"},
        },
        "motor_012": {
            "canonical_asset_context_summary": {
                "screening_supported": True,
                "supported_field_register": [{"field": "GFA"}, {"field": "current_EUI"}],
            },
            "facility_prior": {
                "target_definition": {
                    "target_type": "commercial_building",
                    "target_name": "One Vanderbilt",
                    "jurisdiction_scope": ["US-NY-NYC"],
                    "decision_intent": "Assess LL97 and retrofit pathway",
                }
            },
            "asset_field_register": [
                _field("GFA", "1700000", source_id="nyc_pluto::one-vanderbilt"),
                _field("current_EUI", "72.1", source_id="nyc_ll84::one-vanderbilt"),
            ],
            "dataset_coverage_register": [
                {"dataset_key": "nyc_pluto_property", "status": "accepted"},
                {"dataset_key": "nyc_ll84_energy_benchmarking", "status": "accepted"},
                {"dataset_key": "nyc_ll97_covered_buildings_list", "status": "accepted"},
            ],
        },
        "motor_028": {"source_register": [{"source_type": "nyc_ll84_energy_benchmarking", "accepted": True}]},
        "motor_014": {
            "financial_exposure_register": [
                {
                    "assumption": "Owner-controllable energy upside exists within the central plant and common-area systems rather than mainly in tenant-controlled loads",
                    "current_support": "Unsupported until tenant metering basis and control boundary are confirmed.",
                    "downside_if_wrong": "Retrofit CAPEX may not improve owner economics.",
                    "financial_consequence": "Remove owner-side energy upside from underwriting until control is validated.",
                }
            ]
        },
        "motor_034": {
            "claim_permission_register": [
                {"claim_name": "numeric_eui_claim", "current_permission": "allowed"},
                {"claim_name": "compliance_screening_claim", "current_permission": "allowed"},
            ]
        },
        "motor_033": {
            "decision_front_actions": [
                {"decision_front": "Compliance investment", "current_status": "VALIDATE FIRST"},
                {"decision_front": "Energy retrofit CAPEX", "current_status": "DEFER"},
            ]
        },
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
            "canonical_asset_context_summary": {
                "screening_supported": False,
                "supported_field_register": [{"field": "address"}, {"field": "asset_class"}],
            },
            "facility_prior": {
                "target_definition": {
                    "target_type": "manufacturing_facility",
                    "target_name": "Wilsonart Temple North Laminate Facility",
                    "jurisdiction_scope": ["US-TX"],
                    "decision_intent": "Evaluate efficiency CAPEX",
                }
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
        "motor_033": {
            "decision_front_actions": [
                {"decision_front": "Process efficiency CAPEX", "current_status": "DEFER"},
            ]
        },
    }


def _logistics_inputs() -> dict:
    return {
        "motor_001": {},
        "motor_007": {
            "target_definition_contract": {
                "target_type": "warehouse_distribution",
                "target_name": "Sunrise Logistics Hub",
                "jurisdiction_scope": ["US-IL"],
                "decision_intent": "asset_screening",
            },
            "target_classification_object": {"target_type": "OPERATING_ASSET", "classification_confidence": "high"},
        },
        "motor_012": {
            "facility_prior": {
                "target_definition": {
                    "target_type": "warehouse_distribution",
                    "target_name": "Sunrise Logistics Hub",
                    "jurisdiction_scope": ["US-IL"],
                    "decision_intent": "asset_screening",
                }
            },
            "asset_field_register": [
                _field("asset_class", "warehouse_distribution"),
                _field("use", "logistics warehouse"),
            ],
            "dataset_coverage_register": [],
        },
        "motor_028": {"source_register": []},
        "motor_051": {
            "cross_layer_congruence_register": [
                {
                    "contradiction": "Area benchmark vs service-level complexity",
                    "layers": ["benchmarking", "operation", "logistics"],
                    "strategic_risk": "Area-only logic can miss the real operational driver.",
                    "possible_redesign": "Normalize service-level intensity before diagnosing inefficiency.",
                    "evidence_state": "CONDITIONAL_HYPOTHESIS",
                }
            ],
            "invalid_problem_frame_register": [
                {
                    "apparent_problem": "high_energy_per_area_means_warehouse_inefficiency",
                    "why_invalid_or_premature": "Service-level complexity may dominate the comparison.",
                    "what_problem_should_be_tested_instead": "Which operational intensity variable defines a fair comparison basis.",
                    "evidence_needed": ["service-level proxy", "dock activity profile", "charging schedule"],
                    "evidence_state": "CONDITIONAL_HYPOTHESIS",
                }
            ],
        },
    }


def _run_lane(inputs: dict) -> dict:
    m39 = Motor039Adapter().run(inputs)
    m37 = Motor037Adapter().run({**inputs, "motor_039": m39})
    m38 = Motor038Adapter().run({**inputs, "motor_039": m39, "motor_037": m37})
    m40 = Motor040Adapter().run({**inputs, "motor_039": m39, "motor_037": m37, "motor_038": m38, "motor_051": inputs.get("motor_051", {})})
    m41 = Motor041Adapter().run({**inputs, "motor_039": m39, "motor_037": m37, "motor_038": m38, "motor_040": m40, "motor_051": inputs.get("motor_051", {})})
    return {"motor_039": m39, "motor_037": m37, "motor_038": m38, "motor_040": m40, "motor_041": m41}


def test_motor_040_building_detects_regulation_vs_control_conflict():
    out = _run_lane(_building_inputs())
    conflicts = out["motor_040"]["cross_layer_conflict_register"]
    names = {row["conflict"] for row in conflicts}
    assert "Regulation vs control boundary" in names
    assert "Finance assumes owner-capturable savings before control is proven" in names


def test_motor_040_manufacturing_detects_process_load_and_maintenance_conflicts():
    out = _run_lane(_manufacturing_inputs())
    conflicts = out["motor_040"]["cross_layer_conflict_register"]
    names = {row["conflict"] for row in conflicts}
    assert "Energy-savings framing vs unresolved process load" in names
    assert "Maintenance and uptime economics may dominate visible energy symptoms" in names


def test_motor_041_building_reframes_problem_around_control_and_compliance():
    out = _run_lane(_building_inputs())
    rows = out["motor_041"]["problem_framing_register"]
    assert any("owner-managed base-building systems" in row["reframed_problem"] for row in rows)
    assert any("LL97" in row["reframed_problem"] or "lease redesign" in row["reframed_problem"] for row in rows)


def test_motor_041_manufacturing_reframes_problem_around_structural_load():
    out = _run_lane(_manufacturing_inputs())
    rows = out["motor_041"]["problem_framing_register"]
    assert any("structural process load" in row["reframed_problem"] for row in rows)
    assert any("maintenance" in row["reframed_problem"].lower() or "uptime" in row["reframed_problem"].lower() for row in rows)


def test_motor_040_uses_congruence_fallback_for_logistics_when_structural_conflict_register_is_empty():
    out = _run_lane(_logistics_inputs())
    conflicts = out["motor_040"]["cross_layer_conflict_register"]
    assert conflicts[0]["conflict"] == "Area benchmark vs service-level complexity"
    assert conflicts[0]["evidence_state"] == "CONDITIONAL_HYPOTHESIS"


def test_motor_041_uses_congruence_problem_frame_for_logistics_when_legacy_frame_is_inadmissible():
    out = _run_lane(_logistics_inputs())
    rows = out["motor_041"]["problem_framing_register"]
    assert rows[0]["stated_problem"] == "high energy per area means warehouse inefficiency"
    assert rows[0]["reframed_problem"] == "Which operational intensity variable defines a fair comparison basis."
