from __future__ import annotations

from runtime_orchestrator.adapters.motor_049 import Motor049Adapter
from runtime_orchestrator.congruence_intelligence.entity_resolution import (
    build_asset_boundary_resolution_register,
    build_entity_conflict_register,
    build_entity_resolution_register,
)


def _target_definition() -> dict:
    return {
        "target_name": "Sunrise Logistics Hub",
        "target_identifier": "sunrise-logistics-hub-2026",
        "address_raw": "1450 Logistics Parkway, Dallas, TX 75201",
        "target_type": "warehouse_distribution",
        "jurisdiction_scope": ["US-TX"],
        "owner_entity": "Warehouse Income REIT",
        "operator_entity": "Sunrise Logistics Operations LLC",
    }


def test_entity_resolution_accepts_coherent_asset_owner_and_operator_rows():
    source_register = [
        {
            "source_id": "listing::sunrise",
            "source_family": "geospatial_public_record",
            "title": "Sunrise Logistics Hub assessor listing",
            "asset_name": "Sunrise Logistics Hub",
        },
        {
            "source_id": "operator::sunrise",
            "source_family": "operator_input_record",
            "title": "Operator site note",
            "operator_name": "Sunrise Logistics Operations LLC",
        },
        {
            "source_id": "issuer::sunrise",
            "source_family": "issuer_financial_record",
            "title": "Issuer filing context",
            "owner_name": "Warehouse Income REIT",
        },
        {
            "source_id": "lease::sunrise",
            "source_family": "lease_matrix_record",
            "title": "Lease responsibility matrix",
            "asset_name": "Sunrise Logistics Hub",
        },
    ]

    entity_resolution_register = build_entity_resolution_register(
        target_definition=_target_definition(),
        source_register=source_register,
    )
    entity_conflict_register = build_entity_conflict_register(
        entity_resolution_register=entity_resolution_register,
    )
    boundary_register = build_asset_boundary_resolution_register(
        target_definition=_target_definition(),
        entity_resolution_register=entity_resolution_register,
        entity_conflict_register=entity_conflict_register,
    )

    assert len(entity_resolution_register) == 4
    assert entity_conflict_register == []
    assert any(row["resolution_state"] == "resolved_asset_match_l4" for row in entity_resolution_register)
    assert any(row["resolution_state"] == "resolved_operator_match_l3" for row in entity_resolution_register)
    assert any(row["resolution_state"] == "resolved_owner_match_l3" for row in entity_resolution_register)
    boundary_map = {row["boundary_dimension"]: row["boundary_state"] for row in boundary_register}
    assert boundary_map["physical_asset_boundary"] == "bounded"
    assert boundary_map["operational_control_boundary"] in {"bounded", "partially_bounded"}


def test_entity_resolution_flags_foreign_asset_conflict_as_critical():
    entity_resolution_register = build_entity_resolution_register(
        target_definition=_target_definition(),
        source_register=[
            {
                "source_id": "bill::foreign",
                "source_family": "utility_bill_record",
                "title": "Utility statement",
                "asset_name": "Other Logistics Hub",
            }
        ],
    )
    entity_conflict_register = build_entity_conflict_register(
        entity_resolution_register=entity_resolution_register,
    )

    assert len(entity_conflict_register) == 1
    assert entity_conflict_register[0]["severity"] == "critical"
    assert entity_conflict_register[0]["conflict_type"] == "foreign_asset_conflict"


def test_motor_049_emits_entity_resolution_and_conflict_registers():
    out = Motor049Adapter().run(
        {
            "motor_007": {
                "target_definition_contract": {
                    **_target_definition(),
                },
                "target_classification_object": {
                    "target_type": "OPERATING_ASSET",
                    "classification_confidence": "high",
                },
            },
            "motor_012": {
                "facility_prior": {"target_definition": {**_target_definition()}},
                "asset_field_register": [],
            },
            "motor_028": {
                "source_register": [
                    {
                        "source_id": "assessor::sunrise",
                        "title": "Sunrise Logistics Hub assessor record",
                        "source_family": "geospatial_public_record",
                        "asset_name": "Sunrise Logistics Hub",
                    },
                    {
                        "source_id": "bill::foreign",
                        "title": "Utility bill for another facility",
                        "source_family": "utility_bill_record",
                        "asset_name": "Other Logistics Hub",
                    },
                ],
                "enriched_data": {},
            },
        }
    )

    assert out["entity_resolution_count"] == 2
    assert out["entity_conflict_count"] == 1
    assert out["entity_resolution_state"] == "critical_conflict"
    assert any(row["boundary_state"] == "conflicted" for row in out["asset_boundary_resolution_register"])
