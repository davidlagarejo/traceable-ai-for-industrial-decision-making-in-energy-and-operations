from __future__ import annotations

from runtime_orchestrator.adapters.motor_009 import Motor009Adapter
from runtime_orchestrator.adapters.motor_020 import Motor020Adapter


def test_motor_009_emits_disappeared_and_stale_events():
    out = Motor009Adapter().run(
        {
            "motor_008": {
                "source_registry": {
                    "all_sources": [
                        {"source_id": "src_present", "content_hash": "old_hash"},
                        {"source_id": "src_gone", "content_hash": "gone_hash"},
                    ],
                    "staleness_report": [
                        {"source_key": "src_gone", "fresh": False, "age_seconds": 7200, "ttl_seconds": 3600},
                        {"source_key": "src_stale", "fresh": False, "age_seconds": 7200, "ttl_seconds": 3600},
                    ],
                }
            },
            "motor_004": {
                "parsed_objects": [
                    {"source_id": "src_present", "parsed_content": "new content"}
                ]
            },
            "motor_002": {},
        }
    )

    by_source = {row["source_id"]: row for row in out["change_detection_events"]}
    assert by_source["src_present"]["change_type"] == "updated"
    assert by_source["src_gone"]["change_type"] == "disappeared"
    assert by_source["src_stale"]["change_type"] == "stale"
    assert out["disappeared_sources"] == 1
    assert out["stale_sources"] == 1


def test_motor_020_matches_source_family_exactly_without_substring_spillover():
    out = Motor020Adapter().run(
        {
            "motor_002": {"versioned_objects": []},
            "motor_007": {"evaluated_entities": []},
            "motor_009": {
                "change_detection_events": [
                    {
                        "source_id": "nyc_pluto_property",
                        "change_type": "updated",
                        "content_hash": "hash1",
                    }
                ]
            },
            "motor_013": {
                "inference_case_register": [
                    {
                        "case_id": "c_exact",
                        "case_name": "Exact PLUTO case",
                        "claim_family": "tension",
                        "validation_urgency_score": 0.8,
                        "base_support_traces": ["nyc_pluto_property", "AssetIdentity.asset_context_readiness"],
                        "conditional_statement": "PLUTO property record anchors geometry.",
                    },
                    {
                        "case_id": "c_other",
                        "case_name": "Different source family",
                        "claim_family": "tension",
                        "validation_urgency_score": 0.8,
                        "base_support_traces": ["nyc_pluto_property_record", "geometry_proxy"],
                        "conditional_statement": "A different source family should not match by substring.",
                    },
                ]
            },
            "motor_015": {"traceability_register": {}},
            "motor_016": {"report_package": {"report_traceability": {}}},
        }
    )

    assert out["propagation_map"]["nyc_pluto_property"] == ["c_exact"]
    case_ids = {row["case_id"] for row in out["belief_revision_register"]}
    assert case_ids == {"c_exact"}


def test_motor_020_scopes_unmatched_new_source_by_relevance_instead_of_all_cases():
    out = Motor020Adapter().run(
        {
            "motor_002": {
                "versioned_objects": [
                    {"phase_id": "target_definition", "target_type": "manufacturing_facility", "jurisdiction": "US-TX"}
                ]
            },
            "motor_007": {"evaluated_entities": []},
            "motor_009": {
                "change_detection_events": [
                    {
                        "source_id": "tceq_air_permit",
                        "change_type": "new",
                        "content_hash": "hash2",
                    }
                ]
            },
            "motor_013": {
                "inference_case_register": [
                    {
                        "case_id": "c_permit",
                        "case_name": "Permit exposure",
                        "claim_family": "conflict",
                        "validation_urgency_score": 0.9,
                        "base_support_traces": ["RegulatoryContext.air_permit_basis"],
                        "conditional_statement": "Air permit and emissions posture remain unresolved.",
                        "validation_requirement": "Confirm TCEQ air permit basis and emissions profile.",
                    },
                    {
                        "case_id": "c_unrelated",
                        "case_name": "Unrelated building case",
                        "claim_family": "tension",
                        "validation_urgency_score": 0.9,
                        "base_support_traces": ["AssetIdentity.utility_bills"],
                        "conditional_statement": "Utility bills remain missing for the office tower.",
                        "validation_requirement": "Collect utility bills and meter map.",
                    },
                ]
            },
            "motor_015": {"traceability_register": {}},
            "motor_016": {"report_package": {"report_traceability": {}}},
        }
    )

    assert out["propagation_map"]["tceq_air_permit"] == ["c_permit"]
    assert out["re_evaluation_register"][0]["recommended_action"] == "upgrade_candidate"
    assert "relevance heuristics" in out["re_evaluation_register"][0]["propagation_reason"]


def test_motor_020_treats_disappeared_source_as_degrading_event():
    out = Motor020Adapter().run(
        {
            "motor_002": {"versioned_objects": []},
            "motor_007": {"evaluated_entities": []},
            "motor_009": {
                "change_detection_events": [
                    {
                        "source_id": "nyc_ll84_energy_benchmarking",
                        "change_type": "disappeared",
                        "content_hash": "hash3",
                    }
                ]
            },
            "motor_013": {
                "inference_case_register": [
                    {
                        "case_id": "c_ll84",
                        "case_name": "LL84 screening",
                        "claim_family": "conflict",
                        "validation_urgency_score": 0.85,
                        "base_support_traces": ["nyc_ll84_energy_benchmarking"],
                        "conditional_statement": "Benchmarking anchors current public energy posture.",
                    }
                ]
            },
            "motor_015": {"traceability_register": {}},
            "motor_016": {"report_package": {"report_traceability": {}}},
        }
    )

    belief = out["belief_revision_register"][0]
    assert belief["impact_type"] == "source_disappeared"
    assert belief["trigger_type"] == "source_disappeared"
    assert belief["recommended_action"] in {"downgrade", "block"}
    assert belief["publication_consequence"] in {"freeze_publication", "hold_for_validation", "publish_with_degradation"}
