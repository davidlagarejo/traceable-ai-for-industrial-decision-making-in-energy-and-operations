from __future__ import annotations

from runtime_orchestrator.adapters.motor_049 import Motor049Adapter
from runtime_orchestrator.adapters.motor_050 import Motor050Adapter
from runtime_orchestrator.adapters.motor_051 import Motor051Adapter
from runtime_orchestrator.adapters.motor_052 import Motor052Adapter
from runtime_orchestrator.adapters.motor_053 import Motor053Adapter
from runtime_orchestrator.adapters.motor_054 import Motor054Adapter


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
        "motor_028": {
            "source_register": [
                {"source_id": "permit::site", "source_family": "permit_record", "title": "Permit"},
                {"source_id": "reg::site", "source_family": "regulatory_coverage_record", "title": "Reg coverage"},
            ]
        },
    }


def _run(inputs: dict) -> dict:
    m49 = Motor049Adapter().run(inputs)
    m50 = Motor050Adapter().run({**inputs, "motor_049": m49})
    m51 = Motor051Adapter().run({**inputs, "motor_049": m49, "motor_050": m50})
    m52 = Motor052Adapter().run({**inputs, "motor_049": m49, "motor_050": m50, "motor_051": m51})
    m53 = Motor053Adapter().run({**inputs, "motor_049": m49, "motor_050": m50, "motor_051": m51, "motor_052": m52})
    return Motor054Adapter().run({
        **inputs,
        "motor_049": m49,
        "motor_050": m50,
        "motor_051": m51,
        "motor_052": m52,
        "motor_053": m53,
    })


def test_motor_054_emits_governed_congruence_claim_contracts():
    out = _run(_manufacturing_inputs())

    contracts = {row["claim_id"]: row for row in out["congruence_claim_contract_register"]}
    assert "congruence_invalid_comparison_claim" in contracts
    assert "congruence_measurement_minimality_claim" in contracts
    assert "congruence_regulatory_physics_claim" in contracts
    assert "congruence_finance_physics_claim" in contracts
    for claim in contracts.values():
        assert claim["evidence_state"]
        assert claim["supporting_sources"]
        assert claim["falsification_condition"]
        assert claim["minimum_evidence_required"] is not None
        assert claim["allowed_use"] is not None
        assert claim["prohibited_use"] is not None
