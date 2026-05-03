from __future__ import annotations

from runtime_orchestrator.adapters.motor_016 import _build_structural_executive_summary
from runtime_orchestrator.adapters.motor_034 import Motor034Adapter
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
from runtime_orchestrator.adapters.motor_047 import Motor047Adapter
from runtime_orchestrator.adapters.motor_048 import Motor048Adapter


def _field(
    field: str,
    value,
    *,
    source_id: str | None = None,
) -> dict:
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
            },
            "dataset_coverage_register": [
                {"dataset_key": "nyc_pluto", "status": "accepted"},
                {"dataset_key": "nyc_ll84_benchmarking", "status": "accepted"},
                {"dataset_key": "nyc_ll97_emissions", "status": "accepted"},
                {"dataset_key": "nyc_dob_permits", "status": "accepted"},
                {"dataset_key": "nyc_dof_property_record", "status": "accepted"},
            ],
        },
        "motor_014": {
            "scenario_space": [
                {
                    "scenario": "Tenant-driven loads dominate realized economics.",
                    "financial_meaning": "Owner-only retrofit economics weaken.",
                    "evidence_needed": "Tenant metering map + utility bills",
                    "falsification_condition": "Owner-controlled central plant dominates load.",
                },
                {
                    "scenario": "Owner-controlled central plant dominates the load boundary.",
                    "financial_meaning": "Owner-side optimization may become investable.",
                    "evidence_needed": "Central plant topology + meter boundary",
                    "falsification_condition": "Tenant-metered load dominates.",
                },
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


def _mock_motor_033() -> dict:
    return {
        "expanded_structural_tad_action_register": [
            {
                "action": "Request discriminating evidence pack",
                "status": "ACT NOW",
                "why": "This evidence set discriminates the rival structural hypotheses with the highest value of information.",
                "evidence_state": "CONDITIONAL_HYPOTHESIS",
                "financial_exposure": "Retrofit CAPEX may not improve owner economics.",
                "evidence_needed": "Utility bills + tenant metering map + BMS / central plant topology + LL97 filing basis",
                "prohibited_action": "Do not close savings, ROI, or redesign claims before this evidence arrives.",
                "linked_claim": "TAD_action_claim",
            },
            {
                "action": "Compare against structural peers",
                "status": "COMPARE TO PEERS",
                "why": "Peer comparison can clarify whether the bottleneck is technology, control boundary, or contract architecture.",
                "evidence_state": "CONDITIONAL_HYPOTHESIS",
                "financial_exposure": "Peer assumptions can overstate transferability if evidence is weak.",
                "evidence_needed": "Tenant metering map, lease responsibility matrix, BMS / central plant topology, LL97 filing basis",
                "prohibited_action": "Do not state peer superiority as fact without evidence state and transferability bounds.",
                "linked_claim": "peer_comparison_claim",
            },
            {
                "action": "Advance bounded redesign hypothesis",
                "status": "REDESIGN HYPOTHESIS",
                "why": "A redesign path is useful only as a falsifiable hypothesis under current evidence.",
                "evidence_state": "CONDITIONAL_HYPOTHESIS",
                "financial_exposure": "Owner-only retrofit CAPEX may miss the value boundary.",
                "evidence_needed": "Tenant metering map, lease responsibility matrix, BMS / central plant topology, after-hours occupancy profile",
                "prohibited_action": "Do not present redesign as a final recommendation.",
                "linked_claim": "redesign_hypothesis_claim",
            },
            {
                "action": "Build detailed system model / digital twin",
                "status": "DO NOT MODEL YET",
                "why": "Do not model complexity before the dominant variables and control boundaries are sufficiently bounded.",
                "evidence_state": "CONDITIONAL_HYPOTHESIS",
                "financial_exposure": "Modeling irrelevant complexity wastes time and money.",
                "evidence_needed": "Utility bills + tenant metering map",
                "prohibited_action": "Do not commit modeling effort to irrelevant complexity before the dominant variables are discriminated.",
                "linked_claim": "TAD_action_claim",
            },
        ],
    }


def test_motor_047_builds_one_vanderbilt_executive_thesis():
    inputs = _building_inputs()
    lane = _run_structural_lane(inputs)
    m34 = Motor034Adapter().run({**inputs, **lane})
    m33 = _mock_motor_033()
    out = Motor047Adapter().run({**inputs, **lane, "motor_034": m34, "motor_033": m33})
    thesis = out["executive_thesis"]

    assert thesis["dominant_contradiction"] == "Regulation vs control boundary"
    assert "owner-managed base-building systems" in thesis["reframed_problem"]
    assert thesis["minimum_discriminating_evidence"]
    assert thesis["report_mode"] == "Compliance / Investment Screening Brief"
    assert len(thesis["top_dominant_variables"]) <= 3
    assert len(thesis["top_actions"]) <= 3
    assert thesis["hidden_assumption_at_risk"].startswith("The working assumption is that the actor facing the burden")
    assert "control-boundary problem" in thesis["surprising_but_evidenced_takeaway"]
    assert "value-capture boundary is closed" in thesis["why_current_question_is_premature"]
    assert thesis["interpretive_signal_register"][0]["signal_type"] == "boundary_misalignment"
    assert thesis["dominant_contradiction_selection_basis"]["total_rank_score"] >= thesis["rejected_contradiction_candidates"][0]["selection_basis"]["total_rank_score"]
    assert thesis["thesis_ranked_conflict_register"][0]["conflict"] == "Regulation vs control boundary"


def test_motor_047_preserves_ranked_and_rejected_conflict_candidates():
    inputs = _building_inputs()
    lane = _run_structural_lane(inputs)
    m34 = Motor034Adapter().run({**inputs, **lane})
    m33 = _mock_motor_033()
    out = Motor047Adapter().run({**inputs, **lane, "motor_034": m34, "motor_033": m33})
    thesis = out["executive_thesis"]

    ranked = thesis["thesis_ranked_conflict_register"]
    rejected = thesis["rejected_contradiction_candidates"]

    assert len(ranked) >= 2
    assert rejected
    assert ranked[0]["selection_basis"]["total_rank_score"] >= ranked[1]["selection_basis"]["total_rank_score"]
    assert all(row["conflict"] != thesis["dominant_contradiction"] for row in rejected)


def test_motor_047_emits_boundary_misalignment_interpretive_signal_for_one_vanderbilt():
    inputs = _building_inputs()
    lane = _run_structural_lane(inputs)
    m34 = Motor034Adapter().run({**inputs, **lane})
    m33 = _mock_motor_033()
    out = Motor047Adapter().run({**inputs, **lane, "motor_034": m34, "motor_033": m33})
    thesis = out["executive_thesis"]

    signal_types = [row["signal_type"] for row in thesis["interpretive_signal_register"]]
    assert "boundary_misalignment" in signal_types
    assert "false_capex_logic" in signal_types
    assert thesis["capital_logic_if_assumption_breaks"].startswith("Retrofit CAPEX may reduce site energy")


def test_motor_047_emits_inadmissible_thesis_for_unbounded_target_case():
    out = Motor047Adapter().run(
        {
            "motor_034": {
                "canonical_problem_frame": {
                    "stated_problem": "Need to understand whether the address is a target worth screening.",
                    "reframed_problem": "",
                    "dominant_conflict": "",
                    "reasoning_path": "legacy_decision_gating_only",
                    "problem_frame_active": False,
                },
                "claim_contract_register": [],
                "report_output_mode_classifier_table": [
                    {
                        "canonical_output_mode": "Target Classification Brief",
                        "selected_for_publication": True,
                        "classification_state": "selected_primary_default",
                    }
                ],
            },
            "motor_037": {
                "system_abstraction": {
                    "selected_archetype_id": "target_not_yet_structurally_modelable",
                }
            },
            "motor_038": {"dominant_variable_register": []},
            "motor_040": {"cross_layer_conflict_register": []},
            "motor_041": {"problem_framing_register": []},
            "motor_043": {"competitive_comparison_register": []},
            "motor_044": {"conditional_redesign_register": []},
            "motor_045": {"structural_financial_exposure_register": []},
            "motor_046": {"minimum_evidence_for_discrimination_register": []},
            "motor_014": {"scenario_space": []},
            "motor_033": {"expanded_structural_tad_action_register": []},
        }
    )
    thesis = out["executive_thesis"]

    assert thesis["thesis_state"] == "inadmissible_thesis"
    assert thesis["report_mode"] == "Target Classification Brief"
    assert thesis["dominant_contradiction"] == ""
    assert thesis["dominant_lens"] == ""
    assert thesis["hidden_assumption_at_risk"] == ""
    assert thesis["surprising_but_evidenced_takeaway"] == ""
    assert thesis["what_is_admissible_now"] == []
    assert thesis["minimum_discriminating_evidence"] == []
    assert "Structural thesis remains inadmissible" in thesis["inadmissibility_reason"]


def test_motor_048_builds_compressed_outline_and_client_facing_tad():
    inputs = _building_inputs()
    lane = _run_structural_lane(inputs)
    m34 = Motor034Adapter().run({**inputs, **lane})
    m33 = _mock_motor_033()
    m47 = Motor047Adapter().run({**inputs, **lane, "motor_034": m34, "motor_033": m33})
    out = Motor048Adapter().run({"motor_034": m34, "motor_047": m47})

    outline = out["main_report_outline"]
    client_facing_tad = out["client_facing_tad"]
    appendix_map = out["appendix_map"]
    compression_decision_log = out["compression_decision_log"]
    section_demotions_register = out["section_demotions_register"]
    body_to_appendix_justification_map = out["body_to_appendix_justification_map"]
    prompt_block_mapping_register = out["prompt_block_mapping_register"]

    assert outline["visible_report_mode"] == "Compliance / Investment Screening Brief"
    assert outline["max_primary_sections"] == 12
    assert len(outline["sections"]) == 12
    assert outline["sections"][0]["title"] == "Executive Structural Thesis"
    assert outline["sections"][-1]["title"] == "Claim Permissions / What Not To Do"
    assert client_facing_tad["action_count"] <= 5
    assert [row["title"] for row in appendix_map[:3]] == [
        "Blocking Conflicts",
        "Validation Architecture",
        "Inference Case Map",
    ]
    assert compression_decision_log[0]["decision_type"] == "primary_mode_selection"
    assert compression_decision_log[1]["decision_type"] == "body_budget"
    assert section_demotions_register[0]["destination"] == "appendix"
    assert "Executive Structural Thesis" in body_to_appendix_justification_map
    assert len(prompt_block_mapping_register) == 23
    assert any(
        row["prompt_block_title"] == "Claim Permissions" and row["mapped_section_title"] == "Claim Permissions / What Not To Do"
        for row in prompt_block_mapping_register
    )


def test_motor_048_bypasses_structural_outline_for_inadmissible_thesis():
    out = Motor048Adapter().run(
        {
            "motor_034": {
                "canonical_problem_frame": {
                    "leading_structural_output_mode": "",
                },
                "claim_contract_register": [],
                "report_output_mode_classifier_table": [
                    {
                        "canonical_output_mode": "Target Classification Brief",
                        "selected_for_publication": True,
                        "classification_state": "selected_primary_default",
                    }
                ],
            },
            "motor_047": {
                "executive_thesis": {
                    "report_mode": "Target Classification Brief",
                    "thesis_state": "inadmissible_thesis",
                    "inadmissibility_reason": "Structural thesis remains inadmissible until the case crosses the problem-framing threshold for structural interpretation.",
                }
            },
        }
    )

    outline = out["main_report_outline"]
    assert outline["visible_report_mode"] == "Target Classification Brief"
    assert outline["compression_state"] == "inadmissible_bypass"
    assert outline["sections"] == []
    assert outline["body_section_titles"] == []
    assert outline["max_primary_sections"] == 0
    assert out["client_facing_tad"]["action_count"] == 0
    assert out["compression_decision_log"][0]["decision_type"] == "inadmissible_bypass"
    assert out["prompt_block_mapping_register"] == []


def test_structural_executive_summary_prefers_executive_thesis_fields():
    inputs = _building_inputs()
    lane = _run_structural_lane(inputs)
    m34 = Motor034Adapter().run({**inputs, **lane})
    m33 = _mock_motor_033()
    m47 = Motor047Adapter().run({**inputs, **lane, "motor_034": m34, "motor_033": m33})

    summary = _build_structural_executive_summary(
        {
            "canonical_problem_frame": m34["canonical_problem_frame"],
            "structural_reasoning_path": {
                "reasoning_path": "structural_first",
                "problem_frame_active": True,
            },
            "problem_framing_register": lane["motor_041"]["problem_framing_register"],
            "cross_layer_conflict_register": lane["motor_040"]["cross_layer_conflict_register"],
            "structural_output_mode_classifier_table": m34["structural_output_mode_classifier_table"],
            "structural_output_mode_summary": m34["structural_output_mode_summary"],
            "expanded_structural_tad_action_register": m33["expanded_structural_tad_action_register"],
            "executive_thesis": m47["executive_thesis"],
        }
    )

    assert "owner-managed base-building systems" in summary["primary_reframed_problem"]
    assert summary["dominant_structural_conflict"] == "Regulation vs control boundary"
    assert summary["primary_structural_action"] == "Request discriminating evidence pack"
    assert "owner economics" in summary["dominant_risk"]
