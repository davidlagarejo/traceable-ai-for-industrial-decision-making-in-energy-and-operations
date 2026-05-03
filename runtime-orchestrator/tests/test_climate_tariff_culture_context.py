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


def _manufacturing_inputs(with_local_ops: bool) -> dict:
    source_register = [
        {"source_id": "climate::site", "source_family": "climate_normals_record", "title": "Climate"},
        {"source_id": "tariff::site", "source_family": "utility_tariff_record", "title": "Tariff"},
    ]
    if with_local_ops:
        source_register += [
            {"source_id": "operator::site", "source_family": "operator_input_record", "title": "Operator input"},
            {"source_id": "maint::site", "source_family": "maintenance_log_record", "title": "Maintenance log"},
        ]
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
        "motor_028": {"source_register": source_register},
    }


def _run(inputs: dict) -> tuple[dict, dict]:
    m49 = Motor049Adapter().run(inputs)
    m50 = Motor050Adapter().run({**inputs, "motor_049": m49})
    m51 = Motor051Adapter().run({**inputs, "motor_049": m49, "motor_050": m50})
    m52 = Motor052Adapter().run({**inputs, "motor_049": m49, "motor_050": m50, "motor_051": m51})
    m53 = Motor053Adapter().run({**inputs, "motor_049": m49, "motor_050": m50, "motor_051": m51, "motor_052": m52})
    return m49, m53


def test_motor_053_treats_climate_as_structural_context_and_tariff_as_cost_context():
    _, out = _run(_manufacturing_inputs(with_local_ops=False))

    assert out["climate_location_context_register"][0]["evidence_state"] == "OBSERVED_FACT"
    assert out["utility_tariff_context_register"][0]["plausible_cost_logic"].startswith("Tariff structure can make demand")


def test_motor_053_keeps_culture_as_proxy_and_upgrades_with_local_ops_signals():
    _, weak = _run(_manufacturing_inputs(with_local_ops=False))
    _, stronger = _run(_manufacturing_inputs(with_local_ops=True))

    assert weak["culture_execution_proxy_register"][0]["evidence_state"] == "WEAK_SIGNAL"
    assert stronger["culture_execution_proxy_register"][0]["evidence_state"] == "CONDITIONAL_HYPOTHESIS"
