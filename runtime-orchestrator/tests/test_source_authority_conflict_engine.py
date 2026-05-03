from __future__ import annotations

from runtime_orchestrator.adapters.motor_049 import Motor049Adapter
from runtime_orchestrator.congruence_intelligence.source_authority_conflicts import (
    build_authority_precedence_register,
    build_conflict_resolution_outcome_register,
    build_source_conflict_register,
)


def test_source_conflict_engine_resolves_brochure_below_assessor_for_asset_subtype():
    source_register = [
        {
            "source_id": "assessor::sunrise",
            "source_family": "property_record",
            "title": "County assessor dry warehouse record",
            "authority_score": "high",
        },
        {
            "source_id": "brochure::sunrise",
            "source_family": "property_record",
            "title": "Leasing brochure for cold storage opportunity",
            "authority_score": "high",
        },
    ]

    precedence = build_authority_precedence_register(source_register=source_register)
    conflicts = build_source_conflict_register(source_register=source_register)
    outcomes = build_conflict_resolution_outcome_register(source_conflict_register=conflicts)

    by_source = {row["source_id"]: row for row in precedence}
    assert by_source["assessor::sunrise"]["precedence_score"] > by_source["brochure::sunrise"]["precedence_score"]
    assert len(conflicts) == 1
    assert conflicts[0]["conflict_domain"] == "asset_subtype"
    assert conflicts[0]["resolution_state"] == "resolved_to_higher_precedence_source"
    assert conflicts[0]["lead_value"] == "dry_warehouse"
    assert outcomes[0]["claim_upgrade_allowed"] is True


def test_source_conflict_engine_flags_unresolved_high_authority_tariff_conflict():
    source_register = [
        {
            "source_id": "bill::sunrise",
            "source_family": "utility_bill_record",
            "title": "Utility bill with power factor charge and reactive penalty",
            "authority_score": "high",
        },
        {
            "source_id": "tariff::sunrise",
            "source_family": "utility_tariff_record",
            "title": "Utility tariff rider with demand charge exposure",
            "authority_score": "high",
        },
    ]

    conflicts = build_source_conflict_register(source_register=source_register)

    assert len(conflicts) == 1
    assert conflicts[0]["conflict_domain"] == "tariff_driver"
    assert conflicts[0]["resolution_state"] == "unresolved_high_authority_conflict"
    assert conflicts[0]["severity"] == "critical"


def test_motor_049_turns_unresolved_source_conflict_into_promotion_blocker():
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
                "asset_field_register": [],
            },
            "motor_028": {
                "source_register": [
                    {
                        "source_id": "bill::sunrise",
                        "source_family": "utility_bill_record",
                        "title": "Utility bill with power factor charge and reactive penalty",
                        "authority_score": "high",
                    },
                    {
                        "source_id": "tariff::sunrise",
                        "source_family": "utility_tariff_record",
                        "title": "Utility tariff rider with demand charge exposure",
                        "authority_score": "high",
                    },
                ],
                "enriched_data": {},
            },
        }
    )

    assert out["source_conflict_count"] == 1
    assert any(
        row["blocker_code"] == "unresolved_source_authority_conflict"
        for row in out["promotion_blocker_register"]
    )
