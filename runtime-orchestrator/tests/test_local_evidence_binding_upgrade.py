from __future__ import annotations

from runtime_orchestrator.adapters.motor_049 import Motor049Adapter


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


def _building_with_local_boundary_and_maintenance_inputs() -> dict:
    return {
        "motor_007": {
            "target_definition_contract": {
                "address_raw": "ONE VANDERBILT AVE, NEW YORK, NY 10017",
                "jurisdiction_scope": ["US-NY-NYC"],
                "target_type": "commercial_building",
                "target_name": "One Vanderbilt",
                "owner_entity": "Owner LLC",
                "operator_entity": "Operator LLC",
            },
            "target_classification_object": {
                "target_type": "OPERATING_ASSET",
                "classification_confidence": "high",
            },
        },
        "motor_012": {
            "facility_prior": {
                "target_definition": {
                    "target_type": "commercial_building",
                    "target_name": "One Vanderbilt",
                    "jurisdiction_scope": ["US-NY-NYC"],
                    "owner_entity": "Owner LLC",
                    "operator_entity": "Operator LLC",
                }
            },
            "asset_field_register": [
                _field("asset_class", "commercial_building"),
            ],
        },
        "motor_028": {
            "source_register": [
                {
                    "source_id": "bills::site",
                    "title": "Utility bills",
                    "url": "https://example.test/bills",
                    "source_family": "utility_bill_record",
                },
                {
                    "source_id": "lease::site",
                    "title": "Lease matrix",
                    "url": "https://example.test/lease",
                    "source_family": "lease_matrix_record",
                },
                {
                    "source_id": "submeter::site",
                    "title": "Submetering map",
                    "url": "https://example.test/submeter",
                    "source_family": "submetering_record",
                },
                {
                    "source_id": "maintenance::site",
                    "title": "Maintenance contract",
                    "url": "https://example.test/maintenance",
                    "source_family": "maintenance_contract_record",
                },
                {
                    "source_id": "cmms::site",
                    "title": "CMMS export",
                    "url": "https://example.test/cmms",
                    "source_family": "cmms_record",
                },
            ],
            "enriched_data": {
                "extended_sources": {
                    "utility_bill_record": {
                        "records": [
                            {
                                "source_id": "bill::ov::2026-01",
                                "statement_name": "Electric utility statement",
                                "service_type": "electricity",
                                "charge_type": "demand_charge",
                                "charge_amount": "12000",
                                "demand_kw": "1100",
                            }
                        ]
                    },
                    "lease_matrix_record": {
                        "records": [
                            {
                                "source_id": "lease::ov",
                                "responsibility_split": "tenant plug loads billed separately; owner central plant retained",
                            }
                        ]
                    },
                    "submetering_record": {
                        "records": [
                            {
                                "source_id": "submeter::ov",
                                "metering_scope": "tenant submeters plus owner house meter",
                                "shared_loads": "base building loads remain owner-metered",
                            }
                        ]
                    },
                    "maintenance_contract_record": {
                        "records": [
                            {
                                "source_id": "maintenance::ov",
                                "pm_program": "monthly central plant PM",
                                "system_scope": "central plant and controls",
                            }
                        ]
                    },
                    "cmms_record": {
                        "records": [
                            {
                                "source_id": "cmms::ov",
                                "program_signal": "controls workorders tracked weekly",
                                "repeat_failure_signal": "no chronic unresolved alarms",
                            }
                        ]
                    },
                }
            },
        },
    }


def _public_building_inputs() -> dict:
    return {
        "motor_007": {
            "target_definition_contract": {
                "address_raw": "ONE VANDERBILT AVE, NEW YORK, NY 10017",
                "jurisdiction_scope": ["US-NY-NYC"],
                "target_type": "commercial_building",
                "target_name": "One Vanderbilt",
            },
            "target_classification_object": {
                "target_type": "OPERATING_ASSET",
                "classification_confidence": "high",
            },
        },
        "motor_012": {
            "facility_prior": {
                "target_definition": {
                    "target_type": "commercial_building",
                    "target_name": "One Vanderbilt",
                    "jurisdiction_scope": ["US-NY-NYC"],
                }
            },
            "asset_field_register": [_field("asset_class", "commercial_building")],
        },
        "motor_028": {"source_register": []},
    }


def test_motor_049_extracts_boundary_and_maintenance_evidence_and_upgrades_binding():
    out = Motor049Adapter().run(_building_with_local_boundary_and_maintenance_inputs())

    assert out["control_boundary_evidence_count"] >= 3
    assert out["maintenance_proof_evidence_count"] >= 3
    assert out["operational_intake_pack"]["control_boundary_pack"]["current_state"] == "evidenced"
    assert out["operational_intake_pack"]["maintenance_maturity_pack"]["current_state"] == "evidenced"

    rows = {row["claim_key"]: row for row in out["local_evidence_binding_register"]}
    assert rows["commercial_building_control_boundary"]["current_local_binding_state"] == "sufficiently_bound"
    assert "control_boundary_evidence_register" in rows["commercial_building_control_boundary"]["binding_basis"]
    assert rows["commercial_building_benchmark_vs_roi"]["current_local_binding_state"] in {"partially_bound", "sufficiently_bound"}

    confidence = {row["claim_key"]: row["local_truth_confidence"] for row in out["local_truth_confidence_register"]}
    assert confidence["commercial_building_control_boundary"] == "bounded_strong_local_truth"


def test_motor_049_keeps_public_only_building_claims_unbound_without_local_evidence():
    out = Motor049Adapter().run(_public_building_inputs())

    rows = {row["claim_key"]: row for row in out["local_evidence_binding_register"]}
    assert rows["commercial_building_control_boundary"]["current_local_binding_state"] == "public_context_only_unbound"
    assert out["control_boundary_evidence_count"] == 0
    assert out["maintenance_proof_evidence_count"] == 0
