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


def _manufacturing_inputs_with_parsed_sources() -> dict:
    return {
        "motor_007": {
            "target_definition_contract": {
                "address_raw": "TEMPLE, TX",
                "jurisdiction_scope": ["US-TX"],
                "target_type": "manufacturing_facility",
                "target_name": "Wilsonart Temple North Laminate Facility",
            },
            "target_classification_object": {
                "target_type": "OPERATING_ASSET",
                "classification_confidence": "high",
            },
        },
        "motor_012": {
            "facility_prior": {
                "target_definition": {
                    "target_type": "manufacturing_facility",
                    "target_name": "Wilsonart Temple North Laminate Facility",
                    "jurisdiction_scope": ["US-TX"],
                }
            },
            "asset_field_register": [
                _field("industry_context", "laminate manufacturing"),
                _field("process_signal", "thermal-mechanical batch process"),
            ],
        },
        "motor_028": {
            "source_register": [
                {
                    "source_id": "utility_bill_record::site",
                    "title": "utility_bill_record",
                    "url": "https://example.test/bill",
                    "source_family": "utility_bill_record",
                },
                {
                    "source_id": "utility_tariff_record::site",
                    "title": "utility_tariff_record",
                    "url": "https://example.test/tariff",
                    "source_family": "utility_tariff_record",
                },
                {
                    "source_id": "permit_record::site",
                    "title": "permit_record",
                    "url": "https://example.test/permit",
                    "source_family": "permit_record",
                },
            ],
            "enriched_data": {
                "extended_sources": {
                    "utility_bill_record": {
                        "records": [
                            {
                                "service_type": "electricity",
                                "billing_period": "2026-01",
                                "charge_type": "demand_charge",
                                "charge_amount": "12840",
                                "demand_kw": "940",
                            }
                        ]
                    },
                    "utility_tariff_record": {
                        "records": [
                            {
                                "rate_class": "large_general_service",
                                "power_factor": "0.89",
                                "pf_charge": "present",
                            }
                        ]
                    },
                    "permit_record": {
                        "records": [
                            {
                                "permit_type": "Air permit",
                                "permit_id": "RN100215631",
                                "process_domain": "combustion and emissions-relevant systems",
                            }
                        ]
                    },
                }
            },
        },
    }


def _building_public_inputs() -> dict:
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
        "motor_028": {
            "source_register": [
                {
                    "source_id": "nyc_ll84::site",
                    "title": "nyc_ll84_energy_benchmarking",
                    "url": "https://example.test/ll84",
                    "source_family": "benchmarking_disclosure_record",
                },
                {
                    "source_id": "nyc_dob::site",
                    "title": "permit_record",
                    "url": "https://example.test/dob",
                    "source_family": "permit_record",
                },
            ],
            "enriched_data": {
                "extended_sources": {
                    "permit_record": {
                        "records": [
                            {
                                "permit_type": "LL97 filing context",
                                "permit_summary": "LL84/LL97 covered-building context",
                            }
                        ]
                    }
                }
            },
        },
    }


def test_motor_049_parses_bill_tariff_and_permit_detail_into_runtime_registers():
    out = Motor049Adapter().run(_manufacturing_inputs_with_parsed_sources())

    assert out["utility_charge_breakdown_count"] >= 2
    assert out["tariff_exposure_count"] >= 2
    assert out["permit_to_system_count"] >= 2
    assert out["regulated_process_scope_count"] >= 2

    demand_rows = [row for row in out["utility_charge_breakdown_register"] if row["charge_type"] == "demand_charge"]
    assert demand_rows
    assert demand_rows[0]["demand_kw"] == "940"

    tariff_rows = [row for row in out["tariff_exposure_register"] if row["exposure_type"] == "pf_or_reactive_exposure"]
    assert tariff_rows

    permit_rows = [row for row in out["permit_to_system_register"] if "thermal process" in row["physical_domain"] or "combustion" in row["physical_domain"]]
    assert permit_rows


def test_motor_049_does_not_fabricate_bill_or_tariff_breakdown_from_public_building_context():
    out = Motor049Adapter().run(_building_public_inputs())

    assert out["utility_charge_breakdown_count"] == 0
    assert out["tariff_exposure_count"] == 0
    assert out["permit_to_system_count"] >= 1
    permit_pack = out["operational_intake_pack"]["permit_detail_pack"]
    assert permit_pack["current_state"] == "public_context_only"
