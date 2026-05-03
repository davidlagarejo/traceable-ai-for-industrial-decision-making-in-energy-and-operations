from __future__ import annotations

from runtime_orchestrator.adapters.motor_049 import Motor049Adapter
from runtime_orchestrator.congruence_intelligence import (
    RESEARCH_LIBRARY_VERSION,
    asset_family_dossier,
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


def _building_inputs() -> dict:
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
            "asset_field_register": [
                _field("asset_class", "commercial_building"),
            ],
        },
        "motor_028": {
            "source_register": [
                {
                    "source_id": "nyc_pluto::one-vanderbilt",
                    "title": "NYC PLUTO",
                    "url": "https://example.test/pluto",
                    "source_family": "geospatial_public_record",
                },
                {
                    "source_id": "nyc_ll84::one-vanderbilt",
                    "title": "NYC LL84",
                    "url": "https://example.test/ll84",
                    "source_family": "benchmarking_disclosure_record",
                },
            ]
        },
    }


def test_motor_049_emits_versioned_research_dossier_and_coverage_register():
    out = Motor049Adapter().run(_building_inputs())

    dossier = out["asset_family_research_dossier"]
    coverage = out["family_research_coverage_register"]

    assert out["research_library_version"] == RESEARCH_LIBRARY_VERSION
    assert dossier["asset_family"] == "commercial_building"
    assert dossier["productization_state"] == "versioned_seeded_dossier"
    assert dossier["research_library_version"] == RESEARCH_LIBRARY_VERSION
    assert any(row["coverage_domain"] == "valid_normalization_bases" and row["coverage_state"] == "covered" for row in coverage)
    assert any(row["coverage_domain"] == "minimum_local_evidence_classes" and row["coverage_state"] == "covered" for row in coverage)
    assert out["family_research_coverage_count"] == len(coverage)
    assert out["family_research_gap_count"] == len(out["family_research_gap_register"])


def test_motor_049_emits_authoritative_source_acquisition_trace_and_gap_state():
    out = Motor049Adapter().run(_building_inputs())

    trace = out["authoritative_source_acquisition_trace"]
    gaps = out["family_source_gap_register"]

    assert any(row["source_family"] == "geospatial_public_record" and row["coverage_state"] == "observed_in_case" for row in trace)
    assert any(row["source_family"] == "technical_sourcebook_record" and row["coverage_state"] == "selected_unobserved_in_case" for row in trace)
    assert out["family_source_refresh_state"] == "case_source_coverage_partial"
    assert any(row["source_family"] == "technical_sourcebook_record" for row in gaps)
    assert out["authoritative_source_acquisition_count"] == len(trace)
    assert out["family_source_gap_count"] == len(gaps)


def test_infrastructure_node_dossier_is_available_in_library():
    dossier = asset_family_dossier("infrastructure_node")

    assert dossier["asset_family"] == "infrastructure_node"
    assert dossier["productization_state"] == "versioned_seeded_dossier"
    assert "service continuity" in " ".join(dossier["valid_normalization_bases"]).lower()
    assert dossier["research_library_version"] == RESEARCH_LIBRARY_VERSION
