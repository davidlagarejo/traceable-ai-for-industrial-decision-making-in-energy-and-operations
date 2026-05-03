from __future__ import annotations

from runtime_orchestrator.adapters.motor_049 import Motor049Adapter
from runtime_orchestrator.adapters.motor_050 import Motor050Adapter
from runtime_orchestrator.adapters.motor_051 import Motor051Adapter
from runtime_orchestrator.adapters.motor_052 import Motor052Adapter


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


def _manufacturing_inputs(*, with_maintenance_sources: bool) -> dict:
    source_register = []
    if with_maintenance_sources:
        source_register = [
            {"source_id": "maintenance_log::site", "source_family": "maintenance_log_record", "title": "Maintenance log"},
            {"source_id": "maintenance_contract::site", "source_family": "maintenance_contract_record", "title": "PM contract"},
            {"source_id": "utility_bill::site", "source_family": "utility_bill_record", "title": "Utility bill"},
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
            "facility_prior": {"target_definition": {"target_type": "manufacturing_facility"}},
            "asset_field_register": [_field("asset_class", "manufacturing_facility")],
        },
        "motor_028": {"source_register": source_register},
    }


def _run(inputs: dict) -> tuple[dict, dict]:
    m49 = Motor049Adapter().run(inputs)
    m50 = Motor050Adapter().run({**inputs, "motor_049": m49})
    m51 = Motor051Adapter().run({**inputs, "motor_049": m49, "motor_050": m50})
    m52 = Motor052Adapter().run({**inputs, "motor_049": m49, "motor_050": m50, "motor_051": m51})
    return m49, m52


def test_motor_052_marks_maintenance_not_evidenced_and_downtime_risk_for_public_only_manufacturing():
    m49, out = _run(_manufacturing_inputs(with_maintenance_sources=False))

    claims = {row["reality_claim"] for row in out["maintenance_reality_register"]}
    assert "maintenance maturity not evidenced" in claims
    assert "reactive-maintenance risk plausible" in claims
    assert "downtime economics may dominate visible energy symptoms" in claims
    assert m49["operational_intake_pack"]["maintenance_maturity_pack"]["current_state"] == "not_yet_evidenced"


def test_motor_052_recognizes_partial_maintenance_evidence_when_local_sources_exist():
    m49, out = _run(_manufacturing_inputs(with_maintenance_sources=True))

    claims = {row["reality_claim"] for row in out["maintenance_reality_register"]}
    assert "maintenance maturity partially evidenced" in claims
    assert m49["operational_intake_pack"]["maintenance_maturity_pack"]["current_state"] == "partially_evidenced"
    assert out["maintenance_proof_gap_count"] > 0
    assert out["downtime_dependency_count"] > 0
