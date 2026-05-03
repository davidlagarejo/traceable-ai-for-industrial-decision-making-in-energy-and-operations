from __future__ import annotations

from runtime_orchestrator.adapters.motor_034 import Motor034Adapter
from runtime_orchestrator.adapters.motor_049 import Motor049Adapter
from runtime_orchestrator.congruence_intelligence.declared_input_governor import (
    annotate_asset_field_register,
    build_declared_input_downgrade_register,
)


def _field(
    field: str,
    value,
    *,
    status: str = "OBSERVED",
    scope: str = "ASSET_LEVEL",
    authority_score: str = "declared_input",
    admissibility: str = "DECLARED_INPUT_ONLY",
    source_id: str | None = None,
) -> dict:
    return {
        "field": field,
        "value": value,
        "status": status,
        "source_id": source_id or f"declared_input::{field}",
        "source_family": "",
        "source_title": "",
        "scope": scope,
        "authority_score": authority_score,
        "recency": "current",
        "admissibility": admissibility,
        "notes": "",
    }


def _m34_inputs(asset_fields: list[dict]) -> dict:
    return {
        "motor_007": {
            "target_definition_contract": {
                "address_raw": "1450 Logistics Parkway, Dallas, TX 75201",
                "jurisdiction_scope": ["US-TX"],
                "target_type": "warehouse_distribution",
            },
            "target_classification_object": {
                "target_type": "OPERATING_ASSET",
                "classification_confidence": "high",
            },
            "technical_substrate_readiness": "partial",
            "recommended_report_type": "Decision-Blocked Asset Brief",
        },
        "motor_012": {
            "asset_field_register": asset_fields,
            "missing_evidence_register": [],
            "canonical_asset_context_summary": {
                "canonical_asset_context_state": "location_only",
                "screening_supported": False,
                "supported_clusters": [],
                "missing_clusters": ["identity_cluster", "geometry_size_cluster", "regulatory_cluster"],
                "supported_field_register": [],
            },
            "compliance_applicability_case": {
                "rule_family_record": [],
                "trigger_field_register": [],
                "applicability_state": "unknown",
                "compliance_posture_state": "unknown",
                "screening_basis_register": [],
            },
        },
        "motor_028": {"source_register": []},
    }


def _find_variable(output: dict, variable_name: str) -> dict:
    return next(row for row in output["variable_maturity_register"] if row["variable_name"] == variable_name)


def test_declared_input_governor_marks_rows_and_builds_downgrade_register():
    rows = annotate_asset_field_register(
        [
            _field("address", "1450 Logistics Parkway, Dallas, TX 75201"),
            _field(
                "GFA",
                "420000",
                authority_score="high",
                admissibility="CONFIRMED_ASSET_LEVEL",
                source_id="county_assessor::sunrise",
            ),
        ]
    )

    by_field = {row["field"]: row for row in rows}
    downgrade_register = build_declared_input_downgrade_register(rows)

    assert by_field["address"]["confirmation_state"] == "DECLARED_BY_USER"
    assert by_field["address"]["admissibility"] == "DECLARED_INPUT_ONLY"
    assert by_field["GFA"]["confirmation_state"] == "AUTHORITY_CONFIRMED"
    assert len(downgrade_register) == 1
    assert downgrade_register[0]["field"] == "address"
    assert downgrade_register[0]["max_maturity_level"] == 1


def test_motor_034_caps_declared_input_rows_at_l1():
    declared_rows = annotate_asset_field_register(
        [
            _field("GFA", "420000"),
            _field("address", "1450 Logistics Parkway, Dallas, TX 75201"),
        ]
    )

    out = Motor034Adapter().run(_m34_inputs(declared_rows))

    assert _find_variable(out, "GFA")["maturity_level"] == 1
    assert _find_variable(out, "address")["maturity_level"] == 1


def test_motor_049_propagates_declared_input_downgrade_register():
    declared_rows = annotate_asset_field_register(
        [
            _field("address", "1450 Logistics Parkway, Dallas, TX 75201"),
            _field("asset_class", "warehouse_distribution"),
        ]
    )
    downgrade_register = build_declared_input_downgrade_register(declared_rows)

    out = Motor049Adapter().run(
        {
            "motor_007": {
                "target_definition_contract": {
                    "target_name": "Sunrise Logistics Hub",
                    "target_identifier": "sunrise-logistics-hub-2026",
                    "address_raw": "1450 Logistics Parkway, Dallas, TX 75201",
                    "target_type": "warehouse_distribution",
                    "jurisdiction_scope": ["US-TX"],
                },
                "target_classification_object": {
                    "target_type": "OPERATING_ASSET",
                    "classification_confidence": "high",
                },
            },
            "motor_012": {
                "facility_prior": {},
                "asset_field_register": declared_rows,
                "declared_input_downgrade_register": downgrade_register,
            },
            "motor_028": {
                "source_register": [],
                "enriched_data": {},
            },
        }
    )

    assert out["declared_input_downgrade_count"] == 2
    assert len(out["operational_intake_pack"]["declared_input_downgrade_register"]) == 2
