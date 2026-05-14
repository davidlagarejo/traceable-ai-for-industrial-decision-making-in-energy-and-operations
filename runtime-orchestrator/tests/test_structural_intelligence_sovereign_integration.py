from __future__ import annotations

import json
from pathlib import Path

from runtime_orchestrator.adapters.motor_013 import Motor013Adapter
from runtime_orchestrator.adapters.motor_014 import Motor014Adapter
from runtime_orchestrator.adapters.motor_033 import Motor033Adapter
from runtime_orchestrator.adapters.motor_025 import Motor025Adapter
from runtime_orchestrator.adapters.motor_034 import Motor034Adapter
from runtime_orchestrator.adapters.motor_036 import Motor036Adapter
from runtime_orchestrator.adapters.motor_037 import Motor037Adapter
from runtime_orchestrator.adapters.motor_038 import Motor038Adapter
from runtime_orchestrator.adapters.motor_039 import Motor039Adapter
from runtime_orchestrator.adapters.motor_040 import Motor040Adapter
from runtime_orchestrator.adapters.motor_041 import Motor041Adapter
from runtime_orchestrator.adapters.motor_042 import Motor042Adapter
from runtime_orchestrator.adapters.motor_043 import Motor043Adapter
from runtime_orchestrator.adapters.motor_044 import Motor044Adapter
from runtime_orchestrator.adapters.motor_045 import Motor045Adapter
from runtime_orchestrator.adapters.motor_046 import Motor046Adapter

_INPUTS_DIR = Path(__file__).resolve().parents[1] / "inputs"


def _field(
    field: str,
    value,
    *,
    status: str = "OBSERVED",
    scope: str = "ASSET_LEVEL",
    authority_score: str = "high",
    admissibility: str = "CONFIRMED_ASSET_LEVEL",
    source_id: str | None = None,
) -> dict:
    return {
        "field": field,
        "value": value,
        "status": status,
        "source_id": source_id or f"test::{field}",
        "scope": scope,
        "authority_score": authority_score,
        "recency": "current",
        "admissibility": admissibility,
        "notes": "",
    }


def _building_inputs() -> dict:
    observed_gfa = "1678135"
    return {
        "motor_001": {},
        "motor_007": {
            "target_definition_contract": {
                "address_raw": "ONE VANDERBILT AVE, NEW YORK, NY 10017",
                "jurisdiction_scope": ["US-NY-NYC"],
                "target_type": "commercial_building",
                "target_name": "One Vanderbilt",
                "decision_intent": "Assess LL97 and retrofit pathway",
            },
            "target_classification_object": {
                "target_type": "OPERATING_ASSET",
                "classification_confidence": "high",
            },
            "technical_substrate_readiness": "partial",
            "recommended_report_type": "Decision-Blocked Asset Brief",
        },
        "motor_008": {},
        "motor_010": {},
        "motor_011": {},
        "motor_012": {
            "canonical_asset_context_summary": {
                "screening_supported": True,
                "supported_field_register": [
                    {"field": "address"},
                    {"field": "GFA"},
                    {"field": "floor_count"},
                    {"field": "current_EUI"},
                    {"field": "parcel_id"},
                ],
            },
            "facility_prior": {
                "target_definition": {
                    "target_type": "commercial_building",
                    "target_name": "One Vanderbilt",
                    "jurisdiction_scope": ["US-NY-NYC"],
                    "decision_intent": "Assess LL97 and retrofit pathway",
                }
            },
            "asset_field_register": [
                _field("address", "ONE VANDERBILT AVE, NEW YORK, NY 10017"),
                _field("asset_class", "commercial_building"),
                _field("GFA", observed_gfa, source_id="nyc_pluto::one-vanderbilt"),
                _field("floor_count", "73", source_id="nyc_pluto::one-vanderbilt"),
                _field("current_EUI", "72.1", source_id="nyc_ll84::one-vanderbilt"),
                _field("parcel_id", "1012970001", source_id="nyc_dof::one-vanderbilt"),
            ],
            "missing_evidence_register": [],
            "compliance_applicability_case": {
                "rule_family_record": [{"rule_family_name": "NYC Local Law 97"}],
                "trigger_field_register": [
                    {"field_name": "jurisdiction_codes", "field_state": "observed"},
                    {"field_name": "GFA_sqft", "field_state": "observed"},
                ],
                "applicability_state": "trigger_partially_supported",
                "compliance_posture_state": "covered_building_pathway_observed",
                "screening_basis_register": [
                    {
                        "basis_name": "regulated_floor_area_basis",
                        "basis_value": observed_gfa,
                        "basis_unit": "sqft",
                    },
                    {
                        "basis_name": "ll97_compliance_period",
                        "basis_value": "2024-2029",
                        "basis_unit": "",
                    },
                    {
                        "basis_name": "ll97_penalty_rate",
                        "basis_value": 268,
                        "basis_unit": "USD_per_metric_ton_CO2e",
                    },
                ],
            },
            "dataset_coverage_register": [
                {"dataset_key": "nyc_pluto", "status": "accepted"},
                {"dataset_key": "nyc_ll84_benchmarking", "status": "accepted"},
                {"dataset_key": "nyc_ll97_emissions", "status": "accepted"},
                {"dataset_key": "nyc_dob_permits", "status": "accepted"},
                {"dataset_key": "nyc_dof_property_record", "status": "accepted"},
            ],
        },
        "motor_028": {
            "source_register": [
                {
                    "source_id": "nyc_pluto::one-vanderbilt",
                    "title": "NYC PLUTO",
                    "url": "https://example.test/pluto",
                    "authority_score": "high",
                    "scope": "ASSET_LEVEL",
                    "accepted": True,
                    "source_family": "geospatial_public_record",
                },
                {
                    "source_id": "nyc_ll84::one-vanderbilt",
                    "title": "NYC LL84 benchmarking",
                    "url": "https://example.test/ll84",
                    "authority_score": "high",
                    "scope": "ASSET_LEVEL",
                    "accepted": True,
                    "source_family": "benchmarking_disclosure_record",
                },
                {
                    "source_id": "nyc_dof::one-vanderbilt",
                    "title": "NYC DOF property record",
                    "url": "https://example.test/dof",
                    "authority_score": "high",
                    "scope": "ASSET_LEVEL",
                    "accepted": True,
                    "source_family": "property_record",
                },
            ]
        },
        "motor_014": {
            "financial_exposure_register": [
                {
                    "assumption": "Owner-controllable energy upside exists within the central plant and common-area systems rather than mainly in tenant-controlled loads",
                    "current_support": "Unsupported until tenant metering basis and control boundary are confirmed.",
                    "downside_if_wrong": "Retrofit CAPEX may not improve owner economics.",
                    "financial_consequence": "Remove owner-side energy upside from underwriting until control is validated.",
                }
            ]
        },
        "motor_033": {
            "decision_front_actions": [
                {"decision_front": "Compliance investment", "current_status": "VALIDATE FIRST"},
                {"decision_front": "Energy retrofit CAPEX", "current_status": "DEFER"},
            ]
        },
        "motor_034": {
            "claim_permission_register": [
                {"claim_name": "numeric_eui_claim", "current_permission": "allowed"},
                {"claim_name": "compliance_screening_claim", "current_permission": "allowed"},
            ]
        },
        "motor_035": {},
    }


def _run_structural_lane(inputs: dict) -> dict:
    m39 = Motor039Adapter().run(inputs)
    m37 = Motor037Adapter().run({**inputs, "motor_039": m39})
    m38 = Motor038Adapter().run({**inputs, "motor_039": m39, "motor_037": m37})
    m40 = Motor040Adapter().run({**inputs, "motor_039": m39, "motor_037": m37, "motor_038": m38})
    m41 = Motor041Adapter().run({**inputs, "motor_039": m39, "motor_037": m37, "motor_038": m38, "motor_040": m40})
    m42 = Motor042Adapter().run({**inputs, "motor_039": m39, "motor_037": m37, "motor_038": m38})
    m43 = Motor043Adapter().run({**inputs, "motor_039": m39, "motor_042": m42})
    m44 = Motor044Adapter().run({**inputs, "motor_038": m38, "motor_040": m40, "motor_041": m41, "motor_043": m43})
    m45 = Motor045Adapter().run({**inputs, "motor_038": m38, "motor_040": m40, "motor_041": m41, "motor_044": m44})
    m46 = Motor046Adapter().run({**inputs, "motor_038": m38, "motor_040": m40, "motor_041": m41, "motor_044": m44})
    return {
        "motor_039": m39,
        "motor_037": m37,
        "motor_038": m38,
        "motor_040": m40,
        "motor_041": m41,
        "motor_042": m42,
        "motor_043": m43,
        "motor_044": m44,
        "motor_045": m45,
        "motor_046": m46,
    }


def _manufacturing_inputs() -> dict:
    return {
        "motor_001": {},
        "motor_007": {
            "target_definition_contract": {
                "target_type": "manufacturing_facility",
                "target_name": "Wilsonart Temple North Laminate Facility",
                "jurisdiction_scope": ["US-TX"],
                "decision_intent": "Evaluate efficiency CAPEX",
            },
            "target_classification_object": {
                "target_type": "OPERATING_ASSET",
                "classification_confidence": "high",
            },
            "technical_substrate_readiness": "partial",
            "recommended_report_type": "Decision-Blocked Asset Brief",
        },
        "motor_008": {},
        "motor_010": {},
        "motor_011": {},
        "motor_012": {
            "canonical_asset_context_summary": {
                "screening_supported": False,
                "supported_field_register": [
                    {"field": "asset_class"},
                    {"field": "operating_schedule"},
                    {"field": "process_flow"},
                ],
            },
            "facility_prior": {
                "target_definition": {
                    "target_type": "manufacturing_facility",
                    "target_name": "Wilsonart Temple North Laminate Facility",
                    "jurisdiction_scope": ["US-TX"],
                    "decision_intent": "Evaluate efficiency CAPEX",
                },
                "asset_name": "Wilsonart Temple North Laminate Facility",
                "facility_prior_id": "fp:wilsonart-structural-default",
                "entities": {
                    "Facility": {
                        "jurisdiction": ["US-TX"],
                    },
                    "RegulatoryContext": {
                        "primary_regulation": "TCEQ air permit context",
                        "regulatory_flags": ["permit_screening"],
                    },
                    "AssetIdentity": {
                        "asset_context_readiness": "partial",
                        "missing_observable_clusters": ["utility_bills_cluster", "control_boundary_cluster"],
                    },
                },
                "missing_evidence_register": [],
                "minimum_evidence_pack_seed": [],
                "target_admissibility_state": "bounded_asset",
                "subject_gate_passed": True,
            },
            "asset_field_register": [
                _field("asset_class", "manufacturing_facility", source_id="tceq_facility_record::wilsonart"),
                _field("process_flow", "Public process description for laminate production", source_id="company_facility_page::wilsonart"),
                _field("load_driver", "Laminate pressing and curing duty", source_id="company_facility_page::wilsonart"),
                _field("operating_schedule", "proxy: multi-shift manufacturing operations", source_id="company_facility_page::wilsonart"),
            ],
            "missing_evidence_register": [],
            "dataset_coverage_register": [
                {"dataset_key": "tceq_permits_and_emissions", "status": "accepted"},
            ],
        },
        "motor_028": {
            "source_register": [
                {
                    "source_id": "tceq_air_permit::wilsonart",
                    "title": "TCEQ permit record",
                    "url": "https://example.test/tceq",
                    "authority_score": "high",
                    "scope": "ASSET_LEVEL",
                    "accepted": True,
                    "source_family": "permit_record",
                },
                {
                    "source_id": "company_facility_page::wilsonart",
                    "title": "Wilsonart facility page",
                    "url": "https://example.test/wilsonart",
                    "authority_score": "medium",
                    "scope": "ASSET_LEVEL",
                    "accepted": True,
                    "source_family": "operator_disclosure",
                },
            ]
        },
        "motor_035": {},
    }


def _non_operating_address_inputs() -> dict:
    return {
        "motor_001": {},
        "motor_007": {
            "target_definition_contract": {
                "address_raw": "PIER 1 BAY 1, SAN FRANCISCO, CA, 94111",
                "target_type": "warehouse_distribution",
                "target_name": "PLD Corporate HQ",
                "jurisdiction_scope": ["US-CA-SF"],
                "decision_intent": "Clarify whether target is an operating asset or a mailing/address candidate",
            },
            "target_classification_object": {
                "target_type": "CORPORATE_HEADQUARTERS",
                "classification_confidence": "high",
            },
            "technical_substrate_readiness": "insufficient",
            "recommended_report_type": "Target Classification Brief",
        },
        "motor_008": {},
        "motor_010": {},
        "motor_011": {},
        "motor_012": {
            "canonical_asset_context_summary": {
                "screening_supported": False,
                "supported_field_register": [],
            },
            "facility_prior": {
                "target_definition": {
                    "target_type": "warehouse_distribution",
                    "target_name": "PLD Corporate HQ",
                    "jurisdiction_scope": ["US-CA-SF"],
                    "decision_intent": "Clarify whether target is an operating asset or a mailing/address candidate",
                }
            },
            "asset_field_register": [],
            "missing_evidence_register": [
                {"missing_field": "asset_identity"},
                {"missing_field": "operating_substrate"},
            ],
            "dataset_coverage_register": [],
        },
        "motor_028": {"source_register": []},
        "motor_035": {},
    }


def _run_structural_default_reasoning_case(
    inputs: dict,
    *,
    recommended_report_type: str,
) -> tuple[dict, dict, dict, dict]:
    lane = _run_structural_lane(inputs)
    m34 = Motor034Adapter().run({**inputs, **lane})
    m13 = Motor013Adapter().run(
        {
            "motor_012": inputs["motor_012"],
            "motor_007": {
                "target_admissibility_state": "bounded_asset",
                "subject_gate_passed": True,
            },
        }
    )
    m14 = Motor014Adapter().run(
        {
            "motor_013": m13,
            "motor_012": inputs["motor_012"],
            "motor_034": m34,
            "motor_038": lane["motor_038"],
            "motor_040": lane["motor_040"],
            "motor_046": lane["motor_046"],
            "motor_007": {
                "target_admissibility_state": "bounded_asset",
                "subject_gate_passed": True,
            },
            "motor_001": {},
            "motor_037": lane["motor_037"],
            "motor_041": lane["motor_041"],
        }
    )
    m33 = Motor033Adapter().run(
        {
            "motor_014": m14,
            "motor_015": {},
            "motor_034": m34,
            "motor_012": inputs["motor_012"],
            "motor_038": lane["motor_038"],
            "motor_040": lane["motor_040"],
            "motor_041": lane["motor_041"],
            "motor_042": lane["motor_042"],
            "motor_043": lane["motor_043"],
            "motor_044": lane["motor_044"],
            "motor_045": lane["motor_045"],
            "motor_046": lane["motor_046"],
        }
    )
    m25 = Motor025Adapter().run(
        {
            "__runtime__": {
                "target_admissibility_state": "bounded_asset",
                "subject_gate_passed": True,
                "asset_context_readiness": "asset_context_partial",
                "recommended_report_type": recommended_report_type,
                "report_identity_state": recommended_report_type,
                "allowed_report_classes": [
                    "Decision-Blocked Asset Brief",
                    "Compliance / Investment Screening Brief",
                ],
                "target_definition": {
                    "target_scope": "asset",
                    "target_type": inputs["motor_007"]["target_definition_contract"]["target_type"],
                    "decision_intent": inputs["motor_007"]["target_definition_contract"].get("decision_intent", ""),
                    "report_intent": inputs["motor_007"]["target_definition_contract"].get("report_intent", ""),
                },
            },
            "motor_001": {},
            "motor_022": {},
            "motor_024": {
                "pipeline_health_summary": {
                    "quality_gate_passed": True,
                    "source_quality_gate_passed": True,
                    "final_report_ready": True,
                    "traceability_chain_complete": True,
                    "report_preflight_passed": True,
                    "target_scope": "asset",
                    "target_type": inputs["motor_007"]["target_definition_contract"]["target_type"],
                    "target_admissibility_state": "bounded_asset",
                    "allowed_report_classes": [
                        "Decision-Blocked Asset Brief",
                        "Compliance / Investment Screening Brief",
                    ],
                    "subject_gate_passed": True,
                    "asset_context_readiness": "asset_context_partial",
                    "report_identity_state": recommended_report_type,
                    "recommended_report_type": recommended_report_type,
                    "report_readiness_allowed": [recommended_report_type],
                    "report_readiness_reason": "Structural reasoning is active by default while visible publication remains governed.",
                },
            },
            "motor_034": m34,
        }
    )
    return m34, m14, m33, m25


def _report_package(document_type: str) -> dict:
    body_sections = [
        {
            "title": "Framework Context & Executive Brief",
            "chapter_id": "C1",
            "blocks": [{"content": "EPISTEMIC STATE: SCREENING ADMISSIBLE — public screening is bounded but not decision-grade."}],
        },
        {
            "title": "Operational Identity",
            "chapter_id": "C2",
            "blocks": [{"content": "Parcel / Property ID: 1012970001\nTotal Floors       : 73\nGross Floor Area   : 1,678,135 sqft\nYear Built         : 2020\nDeclared EUI Note  : 72.1"}],
        },
        {
            "title": "Scenario Space Under Current Uncertainty",
            "chapter_id": "C6",
            "blocks": [{"content": "Scenario Alpha\nEvidence link  : utility bills + tenant metering map + BMS / central plant topology + LL97 filing basis\nEvidence needed: utility bills + tenant metering map + BMS / central plant topology + LL97 filing basis\nFalsifies it   : Tenant-controlled loads dominate the profile.\n"}],
        },
    ]
    appendix_sections = [
        {
            "title": "Governance Status",
            "chapter_id": "A0",
            "blocks": [{"content": "Claim Permissions     : 3 allowed / 0 conditional / 8 prohibited"}],
        },
        {
            "title": "TAD — Decision-Admissibility Layer",
            "chapter_id": "A4",
            "blocks": [{"content": "Decision Front   : Compliance investment\nCurrent Status   : VALIDATE FIRST\nAdmissible Action: bounded screening only\nACT NOW\nVALIDATE FIRST"}],
        },
    ]
    return {
        "document_type": document_type,
        "case_metadata": {"document_visible_type": document_type},
        "approved_views": {
            "report_view": {
                "body_sections": body_sections,
                "appendix_sections": appendix_sections,
            }
        },
        "planned_chapter_inventory": {
            "chapter_files": ["00-Brief.tex", "C1.tex", "C2.tex", "C6.tex", "A0.tex", "A4.tex"],
            "forbidden_template_chapters": [
                "00-Abstract.tex",
                "01-Introduction.tex",
                "02-User-Guide.tex",
                "03-Latex-Tutorial.tex",
            ],
        },
        "source_family_coverage_table": [
            {
                "source_family": "property_record",
                "scope": "ENTITY_LEVEL",
                "support_note": "Source contributed entity-level support and not physical operating substrate.",
            }
        ],
    }


def test_motor_034_emits_structural_claim_permissions_and_output_modes():
    inputs = _building_inputs()
    lane = _run_structural_lane(inputs)
    out = Motor034Adapter().run({**inputs, **lane})

    claim_map = {
        row["claim"]: row["permission"]
        for row in out["structural_claim_permission_register"]
    }
    modes = {
        row["recommended_output_mode"]
        for row in out["structural_output_mode_classifier_table"]
    }
    activation_states = {
        row["recommended_output_mode"]: row["activation_state"]
        for row in out["structural_output_mode_classifier_table"]
    }

    assert claim_map["ROI_claim"] == "prohibited"
    assert claim_map["redesign_hypothesis_claim"] == "hypothesis_only"
    assert claim_map["peer_comparison_claim"] == "hypothesis_only"
    assert claim_map["compliance_screening_claim"] in {"allowed", "screening_only"}
    assert "Structural Contradiction Brief" in modes
    assert "System Redesign Hypothesis Brief" in modes
    assert "Competitive Positioning Brief" in modes
    assert "TAD Action Priority Brief" in modes
    assert activation_states["Structural Contradiction Brief"] == "activated_secondary"
    assert activation_states["System Redesign Hypothesis Brief"] == "activated_secondary"
    assert activation_states["Competitive Positioning Brief"] == "activated_secondary"
    assert activation_states["TAD Action Priority Brief"] == "activated_secondary"
    assert out["structural_output_mode_summary"]["primary_report_type"] == "Compliance / Investment Screening Brief"
    assert out["structural_output_mode_summary"]["activation_count"] == 4
    assert out["structural_output_mode_summary"]["blocked_count"] == 0
    assert "Competitive Positioning Brief" in out["structural_output_mode_summary"]["activated_secondary_modes"]
    assert out["structural_output_mode_summary"]["eligible_primary_count"] >= 1
    assert "Competitive Positioning Brief" in out["structural_output_mode_summary"]["eligible_primary_modes"]
    assert out["structural_output_mode_summary"]["leading_primary_promotion_candidate"] in {
        "Structural Contradiction Brief",
        "System Redesign Hypothesis Brief",
        "Competitive Positioning Brief",
        "TAD Action Priority Brief",
    }
    assert "secondary governed surfaces" in out["structural_output_mode_summary"]["policy_note"]
    assert "sovereign classifier explicitly elects it" in out["structural_output_mode_summary"]["primary_promotion_policy_note"]
    assert out["structural_primary_promotion_gate"]["promotion_state"] == "structural_first_default_active"
    assert out["structural_primary_promotion_gate"]["override_allowed"] is False
    assert out["structural_primary_promotion_gate"]["default_reasoning_path"] == "structural_first"
    unified_modes = {
        row["canonical_output_mode"]
        for row in out["report_output_mode_classifier_table"]
    }
    assert unified_modes == {
        "Target Classification Brief",
        "Decision-Blocked Asset Brief",
        "Exploratory Prior Brief",
        "Compliance / Investment Screening Brief",
        "Structural Contradiction Brief",
        "System Redesign Hypothesis Brief",
        "Competitive Positioning Brief",
        "TAD Action Priority Brief",
        "Full Technical Decision Intelligence Report",
    }
    selected_rows = [row for row in out["report_output_mode_classifier_table"] if row["selected_for_publication"]]
    assert len(selected_rows) == 1
    assert selected_rows[0]["canonical_output_mode"] == "Compliance / Investment Screening Brief"
    assert selected_rows[0]["visible_output_mode"] == "Compliance / Investment Screening Brief"


def test_single_output_mode_classifier_covers_all_nine_modes():
    inputs = _building_inputs()
    lane = _run_structural_lane(inputs)
    out = Motor034Adapter().run({**inputs, **lane})

    rows = out["report_output_mode_classifier_table"]
    selected_rows = [row for row in rows if row["selected_for_publication"]]
    canonical_modes = {row["canonical_output_mode"] for row in rows}

    assert len(rows) == 9
    assert len(selected_rows) == 1
    assert canonical_modes == {
        "Target Classification Brief",
        "Decision-Blocked Asset Brief",
        "Exploratory Prior Brief",
        "Compliance / Investment Screening Brief",
        "Structural Contradiction Brief",
        "System Redesign Hypothesis Brief",
        "Competitive Positioning Brief",
        "TAD Action Priority Brief",
        "Full Technical Decision Intelligence Report",
    }
    assert selected_rows[0]["visible_output_mode"] == "Compliance / Investment Screening Brief"
    assert selected_rows[0]["classification_state"] == "selected_primary_default"


def test_motor_034_emits_universal_claim_contract_register():
    inputs = _building_inputs()
    lane = _run_structural_lane(inputs)
    out = Motor034Adapter().run({**inputs, **lane})

    contract_map = {
        row["claim_id"]: row
        for row in out["claim_contract_register"]
    }

    for claim_id in ("numeric_eui_claim", "compliance_screening_claim", "financial_exposure_claim", "TAD_action_claim"):
        assert claim_id in contract_map
        row = contract_map[claim_id]
        assert row["statement"]
        assert row["evidence_state"]
        assert row["supporting_sources"]
        assert row["assumptions"]
        assert row["falsification_condition"]
        assert row["minimum_evidence_required"]
        assert row["allowed_use"]
        assert row["prohibited_use"]

    assert out["maturity_summary"]["claim_contract_count"] == len(out["claim_contract_register"])


def test_motor_033_emits_expanded_structural_tad_actions():
    inputs = _building_inputs()
    lane = _run_structural_lane(inputs)
    m34 = Motor034Adapter().run({**inputs, **lane})
    m33 = Motor033Adapter().run(
        {
            **inputs,
            **lane,
            "motor_014": {
                "inference_records": [],
                "conflict_register": [],
                "validation_queue": [],
                "decision_front_register": [],
            },
            "motor_015": {},
            "motor_034": m34,
        }
    )

    statuses = {row["status"] for row in m33["expanded_structural_tad_action_register"]}

    assert "ACT NOW" in statuses
    assert "COMPARE TO PEERS" in statuses
    assert "REDESIGN HYPOTHESIS" in statuses
    # V8 P4: tad_claim_sync canonical-izes status to DO_NOT_MODEL_YET
    # (underscore form from tad_action_registry). Accept either form
    # (some upstream code still emits the spaced label).
    assert ("DO_NOT_MODEL_YET" in statuses) or ("DO NOT MODEL YET" in statuses)


def test_motor_036_blocks_structural_lane_contract_failures():
    inputs = _building_inputs()
    lane = _run_structural_lane(inputs)
    m34 = Motor034Adapter().run({**inputs, **lane})
    m33 = Motor033Adapter().run(
        {
            **inputs,
            **lane,
            "motor_014": {
                "inference_records": [],
                "conflict_register": [],
                "validation_queue": [],
                "decision_front_register": [],
                "claim_permission_summary": {
                    "allowed_count": 3,
                    "conditional_count": 0,
                    "prohibited_count": 8,
                },
                "scenario_evidence_link_register": [
                    {
                        "scenario": "Owner-controlled base-building systems dominate.",
                        "linked_decision_front": "Compliance investment",
                        "linked_evidence_item": "utility bills + tenant metering map + BMS / central plant topology + LL97 filing basis",
                        "financial_meaning": "Owner-side capital logic may be valid.",
                        "falsification_condition": "Tenant-controlled loads dominate the profile.",
                    }
                ],
            },
            "motor_015": {},
            "motor_034": m34,
        }
    )

    broken_m34 = {**m34}
    broken_m34["structural_claim_permission_register"] = [
        {
            **row,
            "permission": "prohibited" if row["claim"] == "peer_comparison_claim" else row["permission"],
        }
        for row in m34["structural_claim_permission_register"]
    ]
    broken_m33 = {**m33}
    broken_m33["expanded_structural_tad_action_register"] = [
        {
            **row,
            "status": "COMPARE TO PEERS" if row["linked_claim"] == "peer_comparison_claim" else row["status"],
        }
        for row in m33["expanded_structural_tad_action_register"]
    ]
    broken_m44 = {
        "conditional_redesign_register": [
            {
                "hypothesis": "Tenant loads dominate the profile.",
                "evidence_state": "CONDITIONAL_HYPOTHESIS",
                "if_confirmed": "Keep redesign bounded to lease/submetering logic.",
                "if_falsified": "Shift focus back to base-building systems.",
                "next_evidence": [],
            }
        ]
    }
    broken_m45 = {
        "structural_financial_exposure_register": [
            {
                "structural_assumption": "Owner-controllable savings exist.",
                "prohibited_financial_output": ["IRR", "NPV", "payback", "bankability", "savings claim"],
            }
        ]
    }
    broken_m46 = {
        "minimum_evidence_for_discrimination_register": [
            {
                "rival_hypotheses": ["Owner-controlled base-building upside dominates."],
                "minimum_evidence": "utility bills + tenant metering map",
                "what_it_confirms": "Owner control is plausible.",
                "what_it_falsifies": "Tenant dominance is weak.",
            }
        ]
    }

    out = Motor036Adapter().run(
        {
            "motor_012": inputs["motor_012"],
            "motor_014": {
                "claim_permission_summary": {
                    "allowed_count": 3,
                    "conditional_count": 0,
                    "prohibited_count": 8,
                },
                "scenario_evidence_link_register": [
                    {
                        "scenario": "Owner-controlled base-building systems dominate.",
                        "linked_decision_front": "Compliance investment",
                        "linked_evidence_item": "utility bills + tenant metering map + BMS / central plant topology + LL97 filing basis",
                        "financial_meaning": "Owner-side capital logic may be valid.",
                        "falsification_condition": "Tenant-controlled loads dominate the profile.",
                    }
                ],
            },
            "motor_016": {"report_package": _report_package("Compliance / Investment Screening Brief")},
            "motor_033": broken_m33,
            "motor_034": broken_m34,
            "motor_043": lane["motor_043"],
            "motor_044": broken_m44,
            "motor_045": broken_m45,
            "motor_046": broken_m46,
        }
    )

    failure_ids = {row["check_id"] for row in out["critical_failures"]}

    assert out["can_render_pdf"] is False
    assert "conditional_redesign_requires_hypothesis_and_evidence" in failure_ids
    assert "structural_financial_outputs_keep_roi_closed" in failure_ids
    assert "minimum_evidence_discriminates_rival_hypotheses" in failure_ids
    assert "expanded_tad_actions_obey_structural_claim_permissions" in failure_ids


def test_motor_025_exposes_secondary_structural_output_modes_in_report_type_trace():
    out = Motor025Adapter().run(
        {
            "__runtime__": {
                "target_admissibility_state": "bounded_asset",
                "subject_gate_passed": True,
                "asset_context_readiness": "asset_context_partial",
                "recommended_report_type": "Compliance / Investment Screening Brief",
                "report_identity_state": "Compliance / Investment Screening Brief",
                "allowed_report_classes": [
                    "Decision-Blocked Asset Brief",
                    "Compliance / Investment Screening Brief",
                ],
                "target_definition": {
                    "target_scope": "asset",
                    "target_type": "commercial_building",
                },
            },
            "motor_001": {},
            "motor_022": {},
            "motor_024": {
                "pipeline_health_summary": {
                    "quality_gate_passed": True,
                    "source_quality_gate_passed": True,
                    "final_report_ready": True,
                    "traceability_chain_complete": True,
                    "report_preflight_passed": True,
                    "target_scope": "asset",
                    "target_type": "commercial_building",
                    "target_admissibility_state": "bounded_asset",
                    "allowed_report_classes": [
                        "Decision-Blocked Asset Brief",
                        "Compliance / Investment Screening Brief",
                    ],
                    "subject_gate_passed": True,
                    "asset_context_readiness": "asset_context_partial",
                    "report_identity_state": "Compliance / Investment Screening Brief",
                    "recommended_report_type": "Compliance / Investment Screening Brief",
                    "report_readiness_allowed": ["Compliance / Investment Screening Brief"],
                    "report_readiness_prohibited": ["Full Technical Decision Intelligence Report"],
                    "report_readiness_reason": "Public screening is admissible but control-boundary evidence is incomplete.",
                },
            },
            "motor_034": {
                "claim_permission_register": [],
                "decision_permission_register": [],
                "structural_output_mode_summary": {
                    "primary_report_type": "Compliance / Investment Screening Brief",
                    "activated_secondary_modes": [
                        "Structural Contradiction Brief",
                        "Competitive Positioning Brief",
                    ],
                    "blocked_secondary_modes": ["System Redesign Hypothesis Brief"],
                    "policy_note": "Structural output modes are secondary governed surfaces. They cannot override the primary report type or the claim-permission ceiling.",
                    "eligible_primary_modes": [
                        "Structural Contradiction Brief",
                        "Competitive Positioning Brief",
                    ],
                    "non_promotable_primary_modes": ["System Redesign Hypothesis Brief"],
                    "leading_primary_promotion_candidate": "Structural Contradiction Brief",
                    "primary_promotion_policy_note": "Primary structural promotion remains advisory until the sovereign classifier explicitly elects it. Eligible modes cannot override the currently published report type without a dedicated promotion gate.",
                    "activation_count": 2,
                    "blocked_count": 1,
                    "eligible_primary_count": 2,
                },
                "structural_primary_promotion_gate": {
                    "base_primary_report_type": "Compliance / Investment Screening Brief",
                    "requested_structural_primary_mode": "Structural Contradiction Brief",
                    "request_basis": "explicit_target_request",
                    "promotion_state": "elected_primary_structural_mode",
                    "eligible_primary_modes": [
                        "Structural Contradiction Brief",
                        "Competitive Positioning Brief",
                    ],
                    "elected_primary_report_type": "Structural Contradiction Brief",
                    "override_allowed": True,
                    "reason": "Structural primary-mode promotion was explicitly requested and passed the governed eligibility gate.",
                },
            },
        }
    )

    trace = out["report_type_trace"]

    assert trace["final_published_report_type"] == "Structural Contradiction Brief"
    assert trace["secondary_structural_output_modes"] == [
        "Structural Contradiction Brief",
        "Competitive Positioning Brief",
    ]
    assert trace["blocked_secondary_structural_output_modes"] == [
        "System Redesign Hypothesis Brief"
    ]
    assert "secondary governed surfaces" in trace["secondary_output_mode_policy_note"]
    assert trace["eligible_primary_structural_output_modes"] == [
        "Structural Contradiction Brief",
        "Competitive Positioning Brief",
    ]
    assert trace["non_promotable_primary_structural_output_modes"] == [
        "System Redesign Hypothesis Brief"
    ]
    assert trace["leading_primary_structural_output_mode"] == "Structural Contradiction Brief"
    assert "dedicated promotion gate" in trace["primary_structural_mode_policy_note"]
    assert trace["structural_primary_promotion_state"] == "elected_primary_structural_mode"
    assert trace["requested_structural_primary_mode"] == "Structural Contradiction Brief"
    assert out["structural_output_mode_summary"]["activation_count"] == 2


def test_motor_025_keeps_primary_report_type_when_no_structural_promotion_is_requested():
    inputs = _building_inputs()
    lane = _run_structural_lane(inputs)
    m34 = Motor034Adapter().run({**inputs, **lane})

    out = Motor025Adapter().run(
        {
            "__runtime__": {
                "target_admissibility_state": "bounded_asset",
                "subject_gate_passed": True,
                "asset_context_readiness": "asset_context_partial",
                "recommended_report_type": "Compliance / Investment Screening Brief",
                "report_identity_state": "Compliance / Investment Screening Brief",
                "allowed_report_classes": [
                    "Decision-Blocked Asset Brief",
                    "Compliance / Investment Screening Brief",
                ],
                "target_definition": {
                    "target_scope": "asset",
                    "target_type": "commercial_building",
                    "decision_intent": "asset_screening",
                    "report_intent": "asset_preverification_screening",
                },
            },
            "motor_001": {},
            "motor_022": {},
            "motor_024": {
                "pipeline_health_summary": {
                    "quality_gate_passed": True,
                    "source_quality_gate_passed": True,
                    "final_report_ready": True,
                    "traceability_chain_complete": True,
                    "report_preflight_passed": True,
                    "target_scope": "asset",
                    "target_type": "commercial_building",
                    "target_admissibility_state": "bounded_asset",
                    "allowed_report_classes": [
                        "Decision-Blocked Asset Brief",
                        "Compliance / Investment Screening Brief",
                    ],
                    "subject_gate_passed": True,
                    "asset_context_readiness": "asset_context_partial",
                    "report_identity_state": "Compliance / Investment Screening Brief",
                    "recommended_report_type": "Compliance / Investment Screening Brief",
                    "report_readiness_allowed": ["Compliance / Investment Screening Brief"],
                    "report_readiness_reason": "Public screening remains the bounded primary mode.",
                },
            },
            "motor_034": m34,
        }
    )

    trace = out["report_type_trace"]

    assert out["recommended_report_type"] == "Compliance / Investment Screening Brief"
    assert trace["final_published_report_type"] == "Compliance / Investment Screening Brief"
    assert trace["structural_primary_promotion_state"] == "structural_first_default_active"
    assert trace["requested_structural_primary_mode"] == ""
    assert trace["default_reasoning_path"] == "structural_first"
    assert trace["structural_sovereignty_state"] == "structural_first_default"
    assert trace["canonical_problem_frame_active"] is True
    assert trace["reframed_problem"] != ""


def test_structural_lane_is_default_reasoning_path_for_nyc_screening_case():
    m34, m14, m33, m25 = _run_structural_default_reasoning_case(
        _building_inputs(),
        recommended_report_type="Compliance / Investment Screening Brief",
    )

    assert m34["canonical_problem_frame"]["reasoning_path"] == "structural_first"
    assert m14["structural_reasoning_path"]["reasoning_path"] == "structural_first"
    assert m33["tad_preliminary"]["primary_reasoning_path"] == "structural_first"
    assert m33["tad_preliminary"]["structural_problem_frame_active"] is True
    assert m25["report_type_trace"]["default_reasoning_path"] == "structural_first"
    assert m25["report_type_trace"]["structural_sovereignty_state"] == "structural_first_default"
    assert m25["report_type_trace"]["final_published_report_type"] == "Compliance / Investment Screening Brief"


def test_structural_lane_is_default_reasoning_path_for_manufacturing_case():
    m34, m14, m33, m25 = _run_structural_default_reasoning_case(
        _manufacturing_inputs(),
        recommended_report_type="Decision-Blocked Asset Brief",
    )

    assert m34["canonical_problem_frame"]["reasoning_path"] == "structural_first"
    assert m14["structural_reasoning_path"]["reasoning_path"] == "structural_first"
    assert m33["tad_preliminary"]["primary_reasoning_path"] == "structural_first"
    assert m33["tad_preliminary"]["structural_problem_frame_active"] is True
    assert m25["report_type_trace"]["default_reasoning_path"] == "structural_first"
    assert m25["report_type_trace"]["structural_sovereignty_state"] == "structural_first_default"
    assert m25["report_type_trace"]["final_published_report_type"] == "Decision-Blocked Asset Brief"


def test_non_operating_address_case_does_not_overpromote_after_structural_sovereignty_shift():
    inputs = _non_operating_address_inputs()
    lane = _run_structural_lane(inputs)
    m34 = Motor034Adapter().run({**inputs, **lane})

    out = Motor025Adapter().run(
        {
            "__runtime__": {
                "target_admissibility_state": "address_candidate_only",
                "subject_gate_passed": False,
                "asset_context_readiness": "asset_context_insufficient",
                "recommended_report_type": "Target Classification Brief",
                "report_identity_state": "Target Classification Brief",
                "allowed_report_classes": ["Target Classification Brief"],
                "target_definition": {
                    "target_scope": "address_candidate",
                    "target_type": "warehouse_distribution",
                    "decision_intent": "Clarify whether target is an operating asset or a mailing/address candidate",
                },
            },
            "motor_001": {},
            "motor_022": {},
            "motor_024": {
                "pipeline_health_summary": {
                    "quality_gate_passed": True,
                    "source_quality_gate_passed": True,
                    "final_report_ready": True,
                    "traceability_chain_complete": True,
                    "report_preflight_passed": True,
                    "target_scope": "address_candidate",
                    "target_type": "warehouse_distribution",
                    "target_admissibility_state": "address_candidate_only",
                    "allowed_report_classes": ["Target Classification Brief"],
                    "subject_gate_passed": False,
                    "asset_context_readiness": "asset_context_insufficient",
                    "report_identity_state": "Target Classification Brief",
                    "recommended_report_type": "Target Classification Brief",
                    "report_readiness_allowed": ["Target Classification Brief"],
                    "report_readiness_reason": "Non-operating target remains bounded to classification-only output.",
                },
            },
            "motor_034": m34,
        }
    )

    assert lane["motor_039"]["selected_archetype_id"] == "target_not_yet_structurally_modelable"
    assert out["report_type_trace"]["final_published_report_type"] == "Target Classification Brief"
    assert out["report_type_trace"]["structural_sovereignty_state"] == "legacy_decision_gating_only"
    assert out["report_type_trace"]["structural_primary_promotion_state"] != "elected_primary_structural_mode"


def test_motor_025_can_elect_structural_primary_mode_when_explicitly_requested():
    inputs = _building_inputs()
    inputs["motor_007"]["target_definition_contract"] = {
        **inputs["motor_007"]["target_definition_contract"],
        "report_intent": "competitive_positioning_brief",
        "decision_intent": "competitive_positioning",
    }
    inputs["motor_012"]["facility_prior"]["target_definition"] = {
        **inputs["motor_012"]["facility_prior"]["target_definition"],
        "report_intent": "competitive_positioning_brief",
        "decision_intent": "competitive_positioning",
    }
    lane = _run_structural_lane(inputs)
    m34 = Motor034Adapter().run({**inputs, **lane})

    out = Motor025Adapter().run(
        {
            "__runtime__": {
                "target_admissibility_state": "bounded_asset",
                "subject_gate_passed": True,
                "asset_context_readiness": "asset_context_partial",
                "recommended_report_type": "Compliance / Investment Screening Brief",
                "report_identity_state": "Compliance / Investment Screening Brief",
                "allowed_report_classes": [
                    "Decision-Blocked Asset Brief",
                    "Compliance / Investment Screening Brief",
                ],
                "target_definition": {
                    "target_scope": "asset",
                    "target_type": "commercial_building",
                    "report_intent": "competitive_positioning_brief",
                    "decision_intent": "competitive_positioning",
                },
            },
            "motor_001": {},
            "motor_022": {},
            "motor_024": {
                "pipeline_health_summary": {
                    "quality_gate_passed": True,
                    "source_quality_gate_passed": True,
                    "final_report_ready": True,
                    "traceability_chain_complete": True,
                    "report_preflight_passed": True,
                    "target_scope": "asset",
                    "target_type": "commercial_building",
                    "target_admissibility_state": "bounded_asset",
                    "allowed_report_classes": [
                        "Decision-Blocked Asset Brief",
                        "Compliance / Investment Screening Brief",
                    ],
                    "subject_gate_passed": True,
                    "asset_context_readiness": "asset_context_partial",
                    "report_identity_state": "Compliance / Investment Screening Brief",
                    "recommended_report_type": "Compliance / Investment Screening Brief",
                    "report_readiness_allowed": ["Compliance / Investment Screening Brief"],
                    "report_readiness_reason": "Primary screening remains valid unless an eligible structural mode is explicitly elected.",
                },
            },
            "motor_034": m34,
        }
    )

    trace = out["report_type_trace"]

    assert m34["structural_primary_promotion_gate"]["promotion_state"] == "elected_primary_structural_mode"
    assert m34["structural_primary_promotion_gate"]["elected_primary_report_type"] == "Competitive Positioning Brief"
    assert out["recommended_report_type"] == "Competitive Positioning Brief"
    assert trace["final_published_report_type"] == "Competitive Positioning Brief"
    assert trace["structural_primary_promotion_state"] == "elected_primary_structural_mode"
    assert trace["requested_structural_primary_mode"] == "Competitive Positioning Brief"


def _load_official_inputs(filename: str) -> dict:
    with (_INPUTS_DIR / filename).open("r", encoding="utf-8") as handle:
        return json.load(handle)


def _run_primary_promotion_from_official_fixture(
    fixture_name: str,
    *,
    expected_report_type: str,
) -> tuple[dict, dict]:
    fixture = _load_official_inputs(fixture_name)
    target_definition = fixture["target_definition_contract"]
    inputs = _building_inputs()
    inputs["motor_007"]["target_definition_contract"] = {
        **inputs["motor_007"]["target_definition_contract"],
        **target_definition,
    }
    inputs["motor_012"]["facility_prior"]["target_definition"] = {
        **inputs["motor_012"]["facility_prior"]["target_definition"],
        **target_definition,
    }
    lane = _run_structural_lane(inputs)
    m34 = Motor034Adapter().run({**inputs, **lane})
    m25 = Motor025Adapter().run(
        {
            "__runtime__": {
                "target_admissibility_state": "bounded_asset",
                "subject_gate_passed": True,
                "asset_context_readiness": "asset_context_partial",
                "recommended_report_type": "Compliance / Investment Screening Brief",
                "report_identity_state": "Compliance / Investment Screening Brief",
                "allowed_report_classes": [
                    "Decision-Blocked Asset Brief",
                    "Compliance / Investment Screening Brief",
                ],
                "target_definition": {
                    "target_scope": "asset",
                    "target_type": "commercial_building",
                    "report_intent": target_definition.get("report_intent", ""),
                    "decision_intent": target_definition.get("decision_intent", ""),
                    "structural_output_mode_request": target_definition.get("structural_output_mode_request", ""),
                },
            },
            "motor_001": {},
            "motor_022": {},
            "motor_024": {
                "pipeline_health_summary": {
                    "quality_gate_passed": True,
                    "source_quality_gate_passed": True,
                    "final_report_ready": True,
                    "traceability_chain_complete": True,
                    "report_preflight_passed": True,
                    "target_scope": "asset",
                    "target_type": "commercial_building",
                    "target_admissibility_state": "bounded_asset",
                    "allowed_report_classes": [
                        "Decision-Blocked Asset Brief",
                        "Compliance / Investment Screening Brief",
                    ],
                    "subject_gate_passed": True,
                    "asset_context_readiness": "asset_context_partial",
                    "report_identity_state": "Compliance / Investment Screening Brief",
                    "recommended_report_type": "Compliance / Investment Screening Brief",
                    "report_readiness_allowed": ["Compliance / Investment Screening Brief"],
                    "report_readiness_reason": "Primary screening remains valid unless an eligible structural mode is explicitly elected.",
                },
            },
            "motor_034": m34,
        }
    )
    assert m34["structural_primary_promotion_gate"]["elected_primary_report_type"] == expected_report_type
    assert m25["report_type_trace"]["final_published_report_type"] == expected_report_type
    return fixture, m25


def test_official_structural_primary_input_fixtures_encode_explicit_requests():
    contradiction = _load_official_inputs("ova_structural_contradiction_inputs.json")
    competitive = _load_official_inputs("ova_competitive_positioning_inputs.json")
    tad = _load_official_inputs("ova_tad_action_priority_inputs.json")
    redesign = _load_official_inputs("mfg_wilsonart_system_redesign_inputs.json")

    assert contradiction["target_definition_contract"]["structural_output_mode_request"] == "Structural Contradiction Brief"
    assert contradiction["target_definition_contract"]["report_intent"] == "structural_contradiction_brief"
    assert contradiction["target_definition_contract"]["decision_intent"] == "structural_contradiction"

    assert competitive["target_definition_contract"]["structural_output_mode_request"] == "Competitive Positioning Brief"
    assert competitive["target_definition_contract"]["report_intent"] == "competitive_positioning_brief"
    assert competitive["target_definition_contract"]["decision_intent"] == "competitive_positioning"

    assert tad["target_definition_contract"]["structural_output_mode_request"] == "TAD Action Priority Brief"
    assert tad["target_definition_contract"]["report_intent"] == "tad_action_priority_brief"
    assert tad["target_definition_contract"]["decision_intent"] == "action_priority"

    assert redesign["target_definition_contract"]["structural_output_mode_request"] == "System Redesign Hypothesis Brief"
    assert redesign["target_definition_contract"]["report_intent"] == "system_redesign_hypothesis_brief"
    assert redesign["target_definition_contract"]["decision_intent"] == "process_redesign"


def test_official_ova_competitive_fixture_promotes_competitive_positioning_brief():
    fixture, out = _run_primary_promotion_from_official_fixture(
        "ova_competitive_positioning_inputs.json",
        expected_report_type="Competitive Positioning Brief",
    )

    assert fixture["facility_inputs"]["input_10_main_concern"]["decision_type"] == "competitive_positioning"
    assert out["report_type_trace"]["requested_structural_primary_mode"] == "Competitive Positioning Brief"


def test_official_ova_tad_fixture_promotes_tad_action_priority_brief():
    fixture, out = _run_primary_promotion_from_official_fixture(
        "ova_tad_action_priority_inputs.json",
        expected_report_type="TAD Action Priority Brief",
    )

    assert fixture["facility_inputs"]["input_10_main_concern"]["decision_type"] == "action_priority"
    assert out["report_type_trace"]["requested_structural_primary_mode"] == "TAD Action Priority Brief"


def test_official_ova_structural_contradiction_fixture_promotes_structural_contradiction_brief():
    fixture, out = _run_primary_promotion_from_official_fixture(
        "ova_structural_contradiction_inputs.json",
        expected_report_type="Structural Contradiction Brief",
    )

    assert fixture["facility_inputs"]["input_10_main_concern"]["decision_type"] == "structural_contradiction"
    assert out["report_type_trace"]["requested_structural_primary_mode"] == "Structural Contradiction Brief"
