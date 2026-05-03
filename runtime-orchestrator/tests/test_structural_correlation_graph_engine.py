from __future__ import annotations

from runtime_orchestrator.adapters.motor_049 import Motor049Adapter
from runtime_orchestrator.adapters.motor_050 import Motor050Adapter
from runtime_orchestrator.adapters.motor_051 import Motor051Adapter
from runtime_orchestrator.congruence_intelligence.correlation_engine import (
    build_correlation_priority_register,
    build_gold_nugget_candidate_register,
    build_structural_correlation_graph,
)


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
            "facility_prior": {"target_definition": {"target_type": "warehouse_distribution"}},
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
                {"need_id": "mhe_charging_and_mechanical_clues", "discovery_need": "Look for motive-power charging and roof/HVAC/mechanical clues."},
                {"need_id": "operator_boundary_and_control", "discovery_need": "Confirm tenant / operator boundary and who controls docks, charging, and schedules."},
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


def _run(inputs: dict) -> dict:
    m49 = Motor049Adapter().run(inputs)
    m50 = Motor050Adapter().run({**inputs, "motor_049": m49})
    return Motor051Adapter().run({**inputs, "motor_049": m49, "motor_050": m50})


def test_structural_correlation_graph_builds_multi_layer_rows_and_gold_nugget_candidates():
    out = _run(_warehouse_inputs())

    correlations = {row["correlation"] for row in out["structural_correlation_register"]}
    assert "MHE charging + demand tariff + operating schedule" in correlations
    assert "Dock activity + climate + HVAC/refrigeration duty" in correlations
    assert "Operator control + utility payer + CAPEX boundary" in correlations

    graph = out["structural_correlation_graph"]
    assert len(graph) >= 4
    assert all(row["layers_connected"] for row in graph)
    assert any("tariff design problem disguised as energy inefficiency" in row["possible_gold_nugget"] for row in graph)

    priorities = out["correlation_priority_register"]
    assert priorities
    assert priorities[0]["priority_score"] >= priorities[-1]["priority_score"]

    nuggets = out["gold_nugget_candidate_register"]
    assert any("wrong denominator" in row["gold_nugget_candidate"].lower() or "tariff design problem" in row["gold_nugget_candidate"].lower() for row in nuggets)


def test_cross_layer_congruence_keeps_dominant_contradiction_and_adds_supporting_correlation_count():
    out = _run(_warehouse_inputs())

    contradictions = {row["contradiction"]: row for row in out["cross_layer_congruence_register"]}
    assert "Area benchmark vs service-level complexity" in contradictions
    assert contradictions["Area benchmark vs service-level complexity"]["supporting_correlation_count"] >= 1


def test_correlation_sidecars_can_be_built_from_register_directly():
    graph = build_structural_correlation_graph(
        structural_correlation_register=[
            {
                "correlation": "MHE charging + demand tariff + operating schedule",
                "layers_connected": ["logistics", "tariff", "finance", "operation"],
                "strategic_meaning": "The issue may be demand orchestration, not annual energy efficiency.",
                "evidence_needed": ["utility bills", "charging schedule", "MHE inventory"],
                "possible_gold_nugget": "If charging drives peak demand, the asset may have a tariff design problem disguised as energy inefficiency.",
                "evidence_state": "CONDITIONAL_HYPOTHESIS",
            }
        ]
    )
    priorities = build_correlation_priority_register(structural_correlation_graph=graph)
    nuggets = build_gold_nugget_candidate_register(structural_correlation_graph=graph)
    assert graph[0]["correlation_id"] == "corr_01"
    assert priorities[0]["priority_score"] > 0
    assert "tariff design problem" in nuggets[0]["gold_nugget_candidate"]
