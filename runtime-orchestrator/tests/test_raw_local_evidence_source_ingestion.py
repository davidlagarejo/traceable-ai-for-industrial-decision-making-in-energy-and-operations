from __future__ import annotations

from runtime_orchestrator.adapters.motor_049 import Motor049Adapter
from runtime_orchestrator.congruence_intelligence.raw_local_evidence_sources import (
    build_raw_local_evidence_source_register,
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


def _raw_document_pipeline() -> dict:
    return {
        "facility_inputs": {
            "input_12_raw_local_evidence": {
                "documents": [
                    {
                        "document_id": "bill-jan",
                        "document_type": "utility_bill_pdf",
                        "title": "January electric bill",
                        "extracted_records": [
                            {
                                "source_id": "bill::jan",
                                "service_type": "electricity",
                                "billing_period": "2026-01",
                                "charge_type": "demand_charge",
                                "charge_amount": "12840",
                                "demand_kw": "940",
                            }
                        ],
                    },
                    {
                        "document_id": "lease-boundary",
                        "document_type": "lease responsibility matrix",
                        "title": "Owner / tenant load split",
                        "extracted_fields": {
                            "responsibility_split": "owner retains central systems; tenant plug loads separately billed",
                            "metering_scope": "owner house meter plus tenant submeters",
                        },
                    },
                    {
                        "document_id": "cmms-export",
                        "document_type": "cmms export",
                        "title": "Open workorder export",
                        "extracted_fields": {
                            "program_signal": "workorders triaged weekly",
                            "repeat_failure_signal": "no chronic unresolved alarms",
                        },
                    },
                ]
            }
        }
    }


def _logistics_raw_local_inputs() -> dict:
    return {
        "__pipeline__": {
            "facility_inputs": {
                "input_12_raw_local_evidence": {
                    "documents": [
                        {
                            "document_id": "bill-jan",
                            "document_type": "utility bill pdf",
                            "title": "January utility statement",
                            "extracted_records": [
                                {
                                    "source_id": "bill::logistics::jan",
                                    "statement_name": "Electric utility statement",
                                    "service_type": "electricity",
                                    "charge_type": "demand_charge",
                                    "charge_amount": "12000",
                                    "demand_kw": "780",
                                }
                            ],
                        },
                        {
                            "document_id": "dock-schedule",
                            "document_type": "throughput and schedule worksheet",
                            "title": "Dock turns and operating schedule",
                            "extracted_fields": {
                                "dock_turns_per_day": "250",
                                "operating_pattern": "24/6",
                            },
                        },
                        {
                            "document_id": "equipment-list",
                            "document_type": "equipment inventory",
                            "title": "Handling equipment inventory",
                            "extracted_records": [
                                {
                                    "critical_system": "forklift charging",
                                    "fleet_count": "80",
                                }
                            ],
                        },
                        {
                            "document_id": "submeter-map",
                            "document_type": "metering boundary map",
                            "title": "Charging and dock load submeters",
                            "extracted_fields": {
                                "metering_scope": "charging submeter and dock-door panel split",
                                "shared_loads": "house lighting remains shared",
                            },
                        },
                        {
                            "document_id": "permit-packet",
                            "document_type": "permit summary",
                            "title": "Fire and equipment permit summary",
                            "extracted_records": [
                                {
                                    "permit_id": "permit::warehouse::1",
                                    "permit_type": "warehouse equipment permit",
                                }
                            ],
                        },
                        {
                            "document_id": "maintenance-program",
                            "document_type": "maintenance contract",
                            "title": "Dock and charging PM agreement",
                            "extracted_fields": {
                                "pm_program": "quarterly dock and charging PM",
                                "system_scope": "dock equipment and charging rooms",
                            },
                        },
                        {
                            "document_id": "cmms-export",
                            "document_type": "cmms export",
                            "title": "Open workorder export",
                            "extracted_fields": {
                                "open_workorders": "8",
                                "program_signal": "weekly reliability review",
                            },
                        },
                    ]
                }
            }
        },
        "motor_007": {
            "target_definition_contract": {
                "address_raw": "1450 Logistics Parkway, Joliet, IL 60436",
                "jurisdiction_scope": ["US-IL"],
                "target_type": "warehouse_distribution",
                "target_name": "Sunrise Logistics Hub",
                "target_identifier": "sunrise-logistics-hub",
            },
            "target_classification_object": {"target_type": "OPERATING_ASSET", "classification_confidence": "high"},
        },
        "motor_012": {
            "facility_prior": {"target_definition": {"target_type": "warehouse_distribution", "jurisdiction_scope": ["US-IL"]}},
            "asset_field_register": [_field("asset_class", "warehouse_distribution"), _field("use", "logistics warehouse")],
        },
        "motor_028": {"source_register": [], "enriched_data": {}},
    }


def _text_only_pipeline() -> dict:
    return {
        "facility_inputs": {
            "input_12_raw_local_evidence": {
                "documents": [
                    {
                        "document_id": "bill-text",
                        "document_type": "utility bill pdf",
                        "title": "Electric utility bill",
                        "text_excerpt": "Demand charge $12,840. Peak 940 kW. Billing period 2026-01. Electricity service.",
                    },
                    {
                        "document_id": "schedule-text",
                        "document_type": "throughput schedule worksheet",
                        "title": "Dock activity profile",
                        "text_excerpt": "Operating pattern 24/6. Dock turns per day 250.",
                    },
                    {
                        "document_id": "maintenance-text",
                        "document_type": "maintenance contract",
                        "title": "PM agreement",
                        "text_excerpt": "Quarterly preventive maintenance for dock equipment and charging rooms.",
                    },
                ]
            }
        }
    }


def _complex_text_only_pipeline() -> dict:
    return {
        "facility_inputs": {
            "input_12_raw_local_evidence": {
                "documents": [
                    {
                        "document_id": "tariff-text",
                        "document_type": "utility tariff pdf",
                        "title": "Large General Service Tariff",
                        "text_excerpt": (
                            "Rate class DS-3. Service class large general service. "
                            "15-minute billing demand applies. On-peak hours 12:00-18:00. "
                            "Power factor penalty applies below 0.90. Demand ratchet 75% of prior summer peak."
                        ),
                    },
                    {
                        "document_id": "lease-text",
                        "document_type": "lease responsibility matrix",
                        "title": "Owner tenant responsibility schedule",
                        "text_excerpt": (
                            "Owner responsible for central plant, roof HVAC and house lighting. "
                            "Tenant responsible for plug loads, forklift chargers and process equipment. "
                            "Tenant loads separately billed through submeters; shared house meter retained by owner."
                        ),
                    },
                    {
                        "document_id": "maintenance-log-text",
                        "document_type": "maintenance log",
                        "title": "Charging and dock maintenance log",
                        "text_excerpt": (
                            "Monthly PM completed for dock equipment and charging rooms. "
                            "Repeat charger fault on line 2 noted. 6 open workorders remain. "
                            "No chronic unresolved alarms. Downtime limited to 2 hours this month."
                        ),
                    },
                    {
                        "document_id": "cmms-text",
                        "document_type": "cmms export",
                        "title": "Reliability backlog summary",
                        "text_excerpt": "CMMS backlog 6 open workorders. Weekly reliability review for charging systems.",
                    },
                ]
            }
        }
    }


def _messy_text_only_pipeline() -> dict:
    return {
        "facility_inputs": {
            "input_12_raw_local_evidence": {
                "documents": [
                    {
                        "document_id": "tariff-ocr",
                        "document_type": "utility tariff scan",
                        "title": "LGS rate schedule",
                        "text_excerpt": (
                            "RATE SCH: GS-2\n"
                            "SVC CLS: LGS\n"
                            "BILL DET 30 MIN KW\n"
                            "ON PK 13:00-19:00\n"
                            "PF billed if below 95%\n"
                            "4CP tag applies and prior summer peak ratchet remains at 75%.\n"
                        ),
                    },
                    {
                        "document_id": "lease-ocr",
                        "document_type": "lease responsibility matrix",
                        "title": "LL/Tnt responsibility table",
                        "text_excerpt": (
                            "LL resp: base bldg HVAC, CAM lights, house meter.\n"
                            "Tnt resp: FL chargers + plug load.\n"
                            "3PL operator controls dock sched and charger timing.\n"
                            "Direct metered tenant chargers; common area remains on LL meter.\n"
                        ),
                    },
                    {
                        "document_id": "maint-ocr",
                        "document_type": "maintenance log",
                        "title": "Dock / charger PM log",
                        "text_excerpt": (
                            "QTRLY PM complete for dock doors and chargers.\n"
                            "WO open: 11.\n"
                            "Recurring nuisance trip on charger #4.\n"
                            "DT 3.5 hrs this month.\n"
                            "IR scan complete.\n"
                        ),
                    },
                    {
                        "document_id": "bill-ocr",
                        "document_type": "utility bill scan",
                        "title": "Electric statement Jan 2026",
                        "text_excerpt": "Billed Demand 880 KW. Amount $14,250. Jan 2026 electricity service.",
                    },
                ]
            }
        }
    }


def _logistics_semistructured_inputs() -> dict:
    return {
        "__pipeline__": {
            "facility_inputs": {
                "input_12_raw_local_evidence": {
                    "documents": [
                        {
                            "document_id": "bill-text",
                            "document_type": "utility bill pdf",
                            "title": "Electric utility statement",
                            "text_excerpt": "Demand charge $12,840. Peak 940 kW. Billing period 2026-01. Electricity service.",
                        },
                        {
                            "document_id": "tariff-text",
                            "document_type": "utility tariff pdf",
                            "title": "Large General Service Tariff",
                            "text_excerpt": (
                                "Rate class DS-3. Service class large general service. "
                                "15-minute billing demand applies. On-peak hours 12:00-18:00. "
                                "Power factor penalty applies below 0.90."
                            ),
                        },
                        {
                            "document_id": "schedule-text",
                            "document_type": "throughput schedule worksheet",
                            "title": "Dock activity profile",
                            "text_excerpt": "Operating pattern 24/6. Dock turns per day 250.",
                        },
                        {
                            "document_id": "equipment-text",
                            "document_type": "equipment inventory",
                            "title": "Handling equipment inventory",
                            "text_excerpt": "Forklift charging fleet count 80. Conveyor and dock equipment served from charging panels.",
                        },
                        {
                            "document_id": "lease-text",
                            "document_type": "lease responsibility matrix",
                            "title": "Owner tenant responsibility schedule",
                            "text_excerpt": (
                                "Owner responsible for house lighting and shared dock systems. "
                                "Tenant responsible for forklift chargers and plug loads. "
                                "Tenant loads separately billed through submeters; shared house meter retained by owner."
                            ),
                        },
                        {
                            "document_id": "submeter-text",
                            "document_type": "metering boundary map",
                            "title": "Charging and dock load submeters",
                            "text_excerpt": "Submetering boundary includes charging rooms and dock-door panels. Shared house lighting remains on owner meter.",
                        },
                        {
                            "document_id": "maintenance-text",
                            "document_type": "maintenance log",
                            "title": "Charging and dock maintenance log",
                            "text_excerpt": (
                                "Quarterly PM completed for dock equipment and charging rooms. "
                                "Repeat charger fault on line 2 noted. 6 open workorders remain."
                            ),
                        },
                        {
                            "document_id": "cmms-text",
                            "document_type": "cmms export",
                            "title": "Reliability backlog summary",
                            "text_excerpt": "CMMS backlog 6 open workorders. Weekly reliability review for charging systems.",
                        },
                        {
                            "document_id": "permit-text",
                            "document_type": "permit summary",
                            "title": "Fire and equipment permit summary",
                            "text_excerpt": "Permit summary for warehouse equipment and charging room fire systems.",
                        },
                    ]
                }
            }
        },
        "motor_007": {
            "target_definition_contract": {
                "address_raw": "1450 Logistics Parkway, Joliet, IL 60436",
                "jurisdiction_scope": ["US-IL"],
                "target_type": "warehouse_distribution",
                "target_name": "Sunrise Logistics Hub",
                "target_identifier": "sunrise-logistics-hub",
                "owner_entity": "Sunrise Logistics Properties LLC",
                "operator_entity": "Sunrise Distribution Services LLC",
            },
            "target_classification_object": {"target_type": "OPERATING_ASSET", "classification_confidence": "high"},
        },
        "motor_012": {
            "facility_prior": {"target_definition": {"target_type": "warehouse_distribution", "jurisdiction_scope": ["US-IL"]}},
            "asset_field_register": [_field("asset_class", "warehouse_distribution"), _field("use", "logistics warehouse")],
        },
        "motor_028": {"source_register": [], "enriched_data": {}},
    }


def test_build_raw_local_evidence_source_register_infers_and_preserves_payloads():
    rows = build_raw_local_evidence_source_register(
        pipeline=_raw_document_pipeline(),
        target_definition={"target_identifier": "test-asset"},
    )

    by_family = {row["source_family"]: row for row in rows}
    assert "utility_bill_record" in by_family
    assert "lease_matrix_record" in by_family
    assert "cmms_record" in by_family

    utility_payload = by_family["utility_bill_record"]["payload"]
    assert utility_payload["records"][0]["demand_kw"] == "940"
    lease_payload = by_family["lease_matrix_record"]["payload"]
    assert lease_payload["responsibility_split"].startswith("owner retains")


def test_build_raw_local_evidence_source_register_parses_text_only_documents():
    rows = build_raw_local_evidence_source_register(
        pipeline=_text_only_pipeline(),
        target_definition={"target_identifier": "text-only-asset"},
    )

    by_family = {row["source_family"]: row for row in rows}
    utility_payload = by_family["utility_bill_record"]["payload"]["records"][0]
    schedule_payload = by_family["schedule_record"]["payload"]
    maintenance_payload = by_family["maintenance_contract_record"]["payload"]

    assert utility_payload["charge_type"] == "demand_charge"
    assert utility_payload["demand_kw"] == "940"
    assert utility_payload["billing_period"] == "2026-01"
    assert schedule_payload["operating_pattern"] == "24/6"
    assert schedule_payload["dock_turns_per_day"] == "250"
    assert maintenance_payload["pm_program"] == "quarterly"


def test_build_raw_local_evidence_source_register_parses_complex_semistructured_tariff_lease_and_maintenance_docs():
    rows = build_raw_local_evidence_source_register(
        pipeline=_complex_text_only_pipeline(),
        target_definition={"target_identifier": "complex-text-asset"},
    )

    by_family = {row["source_family"]: row for row in rows}
    tariff_payload = by_family["utility_tariff_record"]["payload"]["records"][0]
    lease_payload = by_family["lease_matrix_record"]["payload"]
    maintenance_payload = by_family["maintenance_log_record"]["payload"]
    cmms_payload = by_family["cmms_record"]["payload"]

    assert tariff_payload["rate_class"] == "DS-3"
    assert tariff_payload["pf_charge"] == "present"
    assert tariff_payload["power_factor_threshold"] == "0.90"
    assert tariff_payload["demand_window"] == "15-minute billing demand"
    assert tariff_payload["on_peak_window"] == "12:00-18:00"

    assert lease_payload["owner_scope"].startswith("central plant")
    assert lease_payload["tenant_scope"].startswith("plug loads")
    assert "separately billed" in lease_payload["metering_scope"].lower()
    assert lease_payload["control_boundary"] == "Owner and tenant burden split is explicitly described."

    assert maintenance_payload["pm_program"] == "monthly"
    assert "Repeat charger fault" in maintenance_payload["repeat_failure_signal"]
    assert maintenance_payload["open_workorders"] == "6"
    assert "dock equipment" in maintenance_payload["critical_system"]
    assert "Weekly reliability review" in cmms_payload["notes"]


def test_build_raw_local_evidence_source_register_parses_messy_ocr_like_tariff_lease_and_maintenance_docs():
    rows = build_raw_local_evidence_source_register(
        pipeline=_messy_text_only_pipeline(),
        target_definition={"target_identifier": "messy-text-asset"},
    )

    by_family = {row["source_family"]: row for row in rows}
    tariff_payload = by_family["utility_tariff_record"]["payload"]["records"][0]
    lease_payload = by_family["lease_matrix_record"]["payload"]
    maintenance_payload = by_family["maintenance_log_record"]["payload"]
    utility_payload = by_family["utility_bill_record"]["payload"]["records"][0]

    assert tariff_payload["rate_class"] == "GS-2"
    assert tariff_payload["service_class"] == "LGS"
    assert "30 MIN KW" in tariff_payload["demand_window"]
    assert "13:00-19:00" in tariff_payload["on_peak_window"]
    assert tariff_payload["power_factor_threshold"] == "95%"
    assert "4CP" in tariff_payload["coincident_peak_signal"]
    assert "prior summer peak ratchet" in tariff_payload["demand_ratchet_signal"]

    assert lease_payload["owner_scope"].startswith("base bldg HVAC")
    assert lease_payload["tenant_scope"].startswith("FL chargers")
    assert lease_payload["operator_scope"].startswith("dock sched")
    assert "Direct metered tenant chargers" in lease_payload["metering_scope"]

    assert maintenance_payload["pm_program"] == "quarterly"
    assert maintenance_payload["open_workorders"] == "11"
    assert "Recurring nuisance trip" in maintenance_payload["repeat_failure_signal"]
    assert "DT 3.5 hrs" in maintenance_payload["downtime_signal"]
    assert "IR scan complete" in maintenance_payload["notes"]

    assert utility_payload["demand_kw"] == "880"
    assert utility_payload["billing_period"] == "2026-01"


def test_motor_049_promotes_logistics_case_from_raw_local_documents_only():
    out = Motor049Adapter().run(_logistics_raw_local_inputs())

    assert out["selected_asset_family"] == "logistics_warehouse"
    assert out["structured_local_source_count"] == 0
    assert out["raw_local_source_count"] >= 7
    assert out["research_mode"] == "operator_integrated_congruence"
    assert out["evidence_mode_state"] == "operator_integrated_congruence"
    assert out["promotion_blocker_count"] == 0
    assert out["utility_charge_breakdown_count"] >= 1
    assert out["maintenance_proof_evidence_count"] >= 2
    assert out["operational_intake_pack"]["throughput_schedule_pack"]["current_state"] in {"partially_evidenced", "evidenced"}
    assert out["operational_intake_pack"]["equipment_inventory_pack"]["current_state"] in {"partially_evidenced", "evidenced"}


def test_motor_049_promotes_logistics_case_from_semistructured_text_documents_only():
    out = Motor049Adapter().run(_logistics_semistructured_inputs())

    assert out["selected_asset_family"] == "logistics_warehouse"
    assert out["raw_local_source_count"] >= 9
    assert out["tariff_exposure_count"] >= 1
    assert out["control_boundary_evidence_count"] >= 3
    assert out["maintenance_proof_evidence_count"] >= 3
    assert out["research_mode"] == "operator_integrated_congruence"
    assert out["evidence_mode_state"] == "operator_integrated_congruence"
    assert out["promotion_blocker_count"] == 0

    rows = {row["claim_key"]: row for row in out["local_evidence_binding_register"]}
    assert rows["logistics_service_complexity"]["current_local_binding_state"] == "sufficiently_bound"
