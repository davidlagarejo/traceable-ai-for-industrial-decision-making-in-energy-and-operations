from __future__ import annotations

from runtime_orchestrator.adapters.motor_016 import _build_structural_intelligence_summary
from runtime_orchestrator.adapters.motor_016 import _compose_client_facing_body_sections
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
from runtime_orchestrator.adapters.motor_051 import Motor051Adapter
from runtime_orchestrator.executive_thesis import _build_thesis_constellation_register
from runtime_orchestrator.executive_thesis import _top_gold_nugget_rows


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
    m51 = Motor051Adapter().run(inputs)
    m39 = Motor039Adapter().run(inputs)
    m37 = Motor037Adapter().run({**inputs, "motor_039": m39})
    m38 = Motor038Adapter().run({**inputs, "motor_039": m39, "motor_037": m37})
    m40 = Motor040Adapter().run({**inputs, "motor_039": m39, "motor_037": m37, "motor_038": m38, "motor_051": m51})
    m41 = Motor041Adapter().run({**inputs, "motor_039": m39, "motor_037": m37, "motor_038": m38, "motor_040": m40})
    m42 = Motor042Adapter().run({**inputs, "motor_039": m39, "motor_037": m37, "motor_038": m38})
    m43 = Motor043Adapter().run({**inputs, "motor_039": m39, "motor_042": m42})
    m44 = Motor044Adapter().run({**inputs, "motor_038": m38, "motor_040": m40, "motor_041": m41, "motor_043": m43})
    m45 = Motor045Adapter().run({**inputs, "motor_038": m38, "motor_040": m40, "motor_041": m41, "motor_044": m44})
    m46 = Motor046Adapter().run({**inputs, "motor_038": m38, "motor_040": m40, "motor_041": m41, "motor_044": m44})
    return {
        "motor_051": m51,
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
    assert len(thesis["top_actions"]) <= 5
    assert thesis["hidden_assumption_at_risk"].startswith("The working assumption is that the actor facing the burden")
    assert "control-boundary problem" in thesis["surprising_but_evidenced_takeaway"]
    assert "value-capture boundary is closed" in thesis["why_current_question_is_premature"]
    assert thesis["interpretive_signal_register"][0]["signal_type"] == "boundary_misalignment"
    assert thesis["dominant_contradiction_selection_basis"]["total_rank_score"] >= thesis["rejected_contradiction_candidates"][0]["selection_basis"]["total_rank_score"]
    assert thesis["thesis_ranked_conflict_register"][0]["conflict"] == "Regulation vs control boundary"
    assert thesis["thesis_constellation_register"][0]["element_type"] == "dominant_contradiction"
    assert any(row["element_type"] == "challenger_hypothesis" for row in thesis["thesis_constellation_register"])
    assert thesis["correlation_constellation_register"]
    assert thesis["correlation_constellation_register"][0]["linked_conflict"] == "Regulation vs control boundary"
    assert {row["pack_family"] for row in thesis["evidence_pack_register"]} >= {
        "primary_discriminator_pack",
        "fair_comparison_pack",
    }


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
    assert thesis["evidence_pack_register"] == []
    assert thesis["thesis_constellation_register"] == []
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


def test_motor_048_preserves_outline_for_conditional_structural_intelligence():
    out = Motor048Adapter().run(
        {
            "motor_034": {
                "canonical_problem_frame": {
                    "leading_structural_output_mode": "Decision-Blocked Asset Brief",
                },
                "claim_contract_register": [],
                "report_output_mode_classifier_table": [
                    {
                        "canonical_output_mode": "Decision-Blocked Asset Brief",
                        "selected_for_publication": True,
                        "classification_state": "selected_primary_default",
                    }
                ],
            },
            "motor_047": {
                "executive_thesis": {
                    "report_mode": "Decision-Blocked Asset Brief",
                    "thesis_state": "conditional_structural_intelligence",
                    "conditional_intelligence_reason": "Local closure remains blocked, but bounded structural intelligence survives.",
                    "dominant_lens": "Regulation vs control boundary",
                    "supporting_modes": [],
                    "gold_nugget_authority_state": "skill_primary",
                    "gold_nugget_source_register": "motor_054.authoritative_gold_nugget_register",
                    "top_actions": [
                        {
                            "action": "Request Minimum Evidence",
                            "status": "ACT NOW",
                            "why": "Discriminate the structural boundary before closing local claims.",
                            "maps_to": ["tenant metering map", "utility bills"],
                        }
                    ],
                }
            },
        }
    )

    outline = out["main_report_outline"]
    assert outline["compression_state"] == "conditional_intelligence_compressed"
    assert outline["sections"]
    assert outline["max_primary_sections"] == 12
    assert outline["sections"][0]["title"] == "Executive Structural Thesis"
    assert any(
        row["decision_type"] == "conditional_intelligence_preserved"
        for row in out["compression_decision_log"]
    )


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
    assert summary["gold_nugget_authority_state"] == m47["executive_thesis"]["gold_nugget_authority_state"]
    assert summary["gold_nugget_source_register"] == m47["executive_thesis"]["gold_nugget_source_register"]


def test_structural_executive_summary_carries_conditional_intelligence_fields():
    summary = _build_structural_executive_summary(
        {
            "canonical_problem_frame": {
                "stated_problem": "High landlord energy intensity implies an efficiency retrofit.",
                "reframed_problem": "The decision may depend on who controls the dominant load boundary.",
                "dominant_conflict": "Area benchmark vs control boundary",
            },
            "structural_reasoning_path": {
                "reasoning_path": "structural_first",
                "problem_frame_active": True,
            },
            "executive_thesis": {
                "thesis_state": "conditional_structural_intelligence",
                "local_claim_closure_state": "blocked",
                "conditional_intelligence_available": True,
                "conditional_intelligence_reason": "Local closure remains blocked, but bounded structural intelligence survives.",
                "reframed_problem": "Need to distinguish owner-side burden from tenant-driven load.",
                "dominant_contradiction": "Regulation vs control boundary",
                "why_current_question_is_premature": "The current framing jumps to retrofit before the denominator is normalized.",
                "what_reality_feature_changes_the_decision": "Tenant metering map + lease responsibility matrix + utility bills.",
                "dominant_operational_misunderstanding": "Capital may be targeting the wrong variable.",
                "hidden_system_boundary_error": "The hidden boundary error is assuming that the burdened actor controls the dominant load.",
                "invalid_comparison_risk": "Peer comparison remains invalid until service intensity and control boundary are normalized.",
                "dominant_loss_logic": "The dominant hidden loss may be governance and metering opacity rather than equipment inefficiency.",
                "surprising_but_evidenced_takeaway": "The problem may not be energy inefficiency at all.",
                "top_gold_nuggets": [
                    {"gold_nugget": "This may be a wrong-denominator problem before it is an efficiency problem."}
                ],
                "top_actions": [{"action": "Request Minimum Evidence", "status": "ACT NOW"}],
                "minimum_discriminating_evidence": ["tenant metering map", "lease responsibility matrix", "utility bills"],
                "correlation_constellation_register": [
                    {
                        "linked_conflict": "Regulation vs control boundary",
                        "correlation": "Tenant metering opacity + lease boundary + LL97 visibility",
                        "strategic_meaning": "The billing and regulatory surface can look owner-ready before the controllable value boundary is proven.",
                        "evidence_needed": ["tenant metering map", "lease responsibility matrix", "LL97 filing basis"],
                    }
                ],
                "evidence_pack_register": [
                    {
                        "pack_family": "primary_discriminator_pack",
                        "evidence_items": ["tenant metering map", "lease responsibility matrix", "utility bills"],
                    },
                    {
                        "pack_family": "fair_comparison_pack",
                        "evidence_items": ["service intensity proxy", "control boundary"],
                    },
                ],
                "thesis_constellation_register": [
                    {
                        "element_type": "dominant_contradiction",
                        "statement": "Regulation vs control boundary",
                    },
                    {
                        "element_type": "challenger_hypothesis",
                        "statement": "Area benchmark vs service-level complexity",
                    },
                ],
            },
        }
    )

    assert summary["thesis_state"] == "conditional_structural_intelligence"
    assert summary["local_claim_closure_state"] == "blocked"
    assert summary["conditional_intelligence_available"] is True
    assert "wrong variable" in summary["dominant_operational_misunderstanding"].lower()
    assert "control boundary" in summary["invalid_comparison_risk"].lower()
    assert "wrong-denominator" in summary["top_gold_nuggets"][0].lower()
    assert summary["correlation_constellation_register"][0]["linked_conflict"] == "Regulation vs control boundary"
    assert len(summary["evidence_pack_register"]) == 2
    assert summary["thesis_constellation_register"][0]["element_type"] == "dominant_contradiction"
    assert summary["conditional_opportunity_pathways"]


def test_structural_executive_summary_uses_visible_claim_integrity_register():
    summary = _build_structural_executive_summary(
        {
            "executive_thesis": {
                "thesis_state": "conditional_structural_intelligence",
            },
            "claim_contract_register": [
                {"claim_id": "roi_claim", "permission": "prohibited"},
                {"claim_id": "peer_superiority_claim", "permission": "prohibited"},
                {"claim_id": "structural_hypothesis_claim", "permission": "allowed"},
            ],
            "deduplicated_claim_map": {
                "executive_structural_thesis": [
                    "roi_claim",
                    "structural_hypothesis_claim",
                ],
                "peer_comparison": [
                    "peer_superiority_claim",
                    "structural_hypothesis_claim",
                ],
            },
        }
    )

    assert summary["visible_claim_count"] == 4
    assert summary["visible_blocked_claim_count"] == 2
    by_section = {
        row["section_key"]: row
        for row in summary["visible_claim_integrity_register"]
    }
    assert by_section["executive_structural_thesis"]["blocked_claim_ids"] == ["roi_claim"]
    assert by_section["peer_comparison"]["blocked_claim_ids"] == ["peer_superiority_claim"]


def test_client_facing_sections_embed_conditional_strategic_intelligence():
    body_sections = _compose_client_facing_body_sections(
        main_report_outline={
            "sections": [
                {"section_key": "executive_structural_thesis", "title": "Executive Structural Thesis"},
                {"section_key": "dominant_variables", "title": "Dominant Variables"},
                {"section_key": "financial_exposure", "title": "Financial Exposure Under Uncertainty"},
                {"section_key": "peer_comparison", "title": "Peer / Competitive Comparison"},
                {"section_key": "tad", "title": "TAD — Immediate Action Priority"},
                {"section_key": "conditional_redesign", "title": "Conditional Redesign Pathway"},
                {"section_key": "claim_permissions", "title": "Claim Permissions / What Not To Do"},
            ]
        },
        executive_thesis={
            "thesis_state": "conditional_structural_intelligence",
            "local_claim_closure_state": "blocked",
            "conditional_intelligence_reason": "Local closure remains blocked, but bounded structural intelligence survives.",
            "declared_problem": "High landlord energy intensity implies a base-building inefficiency problem.",
            "reframed_problem": "The denominator may be wrong until service intensity and control boundary are normalized.",
            "dominant_contradiction": "Area benchmark vs service-level complexity",
            "hidden_assumption_at_risk": "That area intensity is the dominant causal variable.",
            "why_current_question_is_premature": "The framing jumps to retrofit before the comparison basis is normalized.",
            "what_reality_feature_changes_the_decision": "Dock intensity + charging window + utility bills.",
            "why_it_matters": "Capital can target the wrong variable.",
            "dominant_risk": "Retrofit CAPEX can miss the actual decision bottleneck.",
            "surprising_but_evidenced_takeaway": "The problem may not be energy.",
            "dominant_lens": "Service intensity vs control boundary",
            "supporting_modes": ["Competitive Positioning Brief"],
            "what_is_admissible_now": ["Request Minimum Evidence"],
            "what_is_not_admissible": ["ROI remains prohibited"],
            "dominant_operational_misunderstanding": "Capital may be targeting the wrong variable.",
            "hidden_system_boundary_error": "The visible payer and the controllable load boundary may not be the same thing.",
            "invalid_comparison_risk": "Area-based peer comparison remains structurally invalid until dock activity and charging windows are normalized.",
            "dominant_loss_logic": "The dominant hidden loss may be charging-window demand structure rather than generic kWh waste.",
            "minimum_discriminating_evidence": ["dock activity profile", "charging schedule", "utility bills"],
            "primary_financial_exposure": {
                "structural_assumption": "Owner-controllable savings exist before the tariff and control boundary are normalized.",
                "evidence_state": "CONDITIONAL_HYPOTHESIS",
                "financial_exposure_if_wrong": "CAPEX can target the wrong variable and miss the controllable economic boundary.",
                "evidence_needed": ["tenant/operator control map", "charging tariff interval data", "utility bills"],
                "allowed_financial_output": ["scenario framing", "capital-at-risk framing"],
                "prohibited_financial_output": ["ROI", "IRR", "NPV", "payback"],
            },
            "primary_peer_comparison": {
                "peer_type": "service-intensity-normalized logistics peers",
                "comparison_mode": "archetypal_screening_only",
                "evidence_state": "ARCHETYPAL_PRIOR",
                "transferability": "conditional",
                "what_it_proves": "What a fair comparison would need.",
                "peer_requirement_rows": [
                    {
                        "peer_requirement": "Subtype and service model",
                        "status": "required",
                        "why_it_matters": "Dry vs fulfillment vs cold-chain changes the denominator.",
                        "missing_evidence": "service model, temperature regime",
                    }
                ],
                "candidate_peer_frame_register": [
                    {
                        "candidate_peer_frame": "high-service dry fulfillment node",
                        "candidate_state": "conditional_until_service_intensity_is_bounded",
                        "why_it_matters": "Tests whether movement intensity invalidates area-first logic.",
                    }
                ],
                "better_practice_delta_register": [
                    {
                        "practice_delta": "Charging-window orchestration",
                        "why_plausible": "A peer can look better because demand peaks are scheduled.",
                        "evidence_needed": "charger timing, tariff intervals",
                    }
                ],
                "peer_superiority_block_reason": "Peer superiority remains prohibited until service intensity and control boundary are bounded.",
            },
            "top_dominant_variables": [
                {
                    "variable": "charging-window demand concentration",
                    "layer": "operational",
                    "evidence_state": "ARCHETYPAL_PRIOR",
                    "why_it_could_matter": "It can dominate demand charges before HVAC efficiency matters.",
                    "decision_impact": "Can invert retrofit priority.",
                }
            ],
            "top_gold_nuggets": [
                {"gold_nugget": "This may be a wrong-denominator problem before it is an efficiency problem."},
                {"gold_nugget": "If charging windows dominate cost, tariff orchestration matters more than generic EUI logic."},
            ],
            "thesis_constellation_register": [
                {
                    "element_type": "challenger_hypothesis",
                    "title": "Challenger hypothesis",
                    "statement": "Dock thermal exchange may dominate HVAC interpretation.",
                    "why_it_matters": "HVAC retrofit can attack the wrong variable.",
                    "differentiator": "This attacks the dock-driven thermal boundary rather than annual kWh intensity.",
                    "evidence_pack_family": "loss_falsification_pack",
                },
                {
                    "element_type": "alternative_variable_candidate",
                    "title": "Alternative variable candidate",
                    "statement": "Charging-window demand concentration",
                    "why_it_matters": "Demand charges can dominate economics before HVAC spend matters.",
                    "differentiator": "This shifts the case from area efficiency to tariff timing.",
                    "evidence_pack_family": "primary_discriminator_pack",
                },
            ],
            "evidence_pack_register": [
                {
                    "pack_family": "primary_discriminator_pack",
                    "pack_title": "Primary discriminator pack",
                    "evidence_items": ["dock activity profile", "charging schedule", "utility bills"],
                    "unlocks": ["local structural closure", "capital logic discrimination"],
                    "why": "This is the minimum pack that changes the meaning of the case.",
                    "evidence_state": "CONDITIONAL_HYPOTHESIS",
                },
                {
                    "pack_family": "fair_comparison_pack",
                    "pack_title": "Fair comparison pack",
                    "evidence_items": ["dock density", "service intensity proxy", "charging profile"],
                    "unlocks": ["fair comparison admissibility", "bounded peer screening"],
                    "why": "These fields decide whether comparison logic is valid at all.",
                    "evidence_state": "CONDITIONAL_HYPOTHESIS",
                },
            ],
            "correlation_constellation_register": [
                {
                    "linked_conflict": "Area benchmark vs service-level complexity",
                    "correlation": "Dock activity + climate + HVAC/refrigeration duty",
                    "strategic_meaning": "Thermal loss interpretation can collapse if dock-driven exchange dominates envelope intuition.",
                    "evidence_needed": ["dock activity profile", "temperature-duty map", "utility bills"],
                },
                {
                    "linked_conflict": "Area benchmark vs service-level complexity",
                    "correlation": "MHE charging + demand tariff + operating schedule",
                    "strategic_meaning": "Demand timing can dominate economics before generic EUI logic matters.",
                    "evidence_needed": ["charging schedule", "utility bills", "tariff interval data"],
                },
            ],
        },
        client_facing_tad={
            "actions": [
                {
                    "action": "Request Minimum Evidence",
                    "status": "ACT NOW",
                    "decision_front": "REQUEST MINIMUM EVIDENCE",
                    "trigger": "missing_operational_context",
                    "trigger_family": "measurement_path",
                    "why": "Normalize the denominator first.",
                    "financial_exposure": "Wrong-variable spend can happen before the denominator is normalized.",
                    "evidence_needed": "dock activity profile + charging schedule + utility bills",
                    "action_posture": "ACT NOW",
                    "evidence_pack_family": "primary_discriminator_pack",
                    "maps_to": "dock activity profile; charging schedule; utility bills",
                    "prohibited_action": "Do not underwrite retrofit ROI.",
                    "prohibited_action_class": "roi_or_transferability_block",
                }
            ]
        },
        problem_framing_register=[],
        system_abstraction={},
        cross_layer_conflict_register=[],
        claim_contract_register=[],
    )

    by_title = {
        row["title"]: "\n".join(
            [
                str(block.get("content_en") or block.get("content") or "").strip()
                for block in list(row.get("blocks", []) or [])
                if str(block.get("content_en") or block.get("content") or "").strip()
            ]
        )
        for row in body_sections
    }

    assert "Conditional Intelligence Reason" in by_title["Executive Structural Thesis"]
    assert "Strategic Reading" in by_title["Executive Structural Thesis"]
    assert "Capital-at-Risk Logic" in by_title["Executive Structural Thesis"]
    assert "Strategic Gold Nugget" in by_title["Executive Structural Thesis"]
    assert "Rival Thesis Constellation" in by_title["Executive Structural Thesis"]
    assert "Dock thermal exchange may dominate HVAC interpretation." in by_title["Executive Structural Thesis"]
    assert "Differentiated Evidence Packs" in by_title["Executive Structural Thesis"]
    assert "Correlation Constellation Signals" in by_title["Executive Structural Thesis"]
    assert "MHE charging + demand tariff + operating schedule" in by_title["Executive Structural Thesis"]
    assert "Primary discriminator pack" in by_title["Executive Structural Thesis"]
    assert "Dominant Loss Logic" in by_title["Dominant Variables"]
    assert "Financial Logic Pack" in by_title["Financial Exposure Under Uncertainty"]
    assert "Strategic Reading" in by_title["Financial Exposure Under Uncertainty"]
    assert "Cost-of-Wrong-Question" in by_title["Financial Exposure Under Uncertainty"]
    assert "Linked Structural Lanes" in by_title["Financial Exposure Under Uncertainty"]
    assert "Invalid Comparison Risk" in by_title["Peer / Competitive Comparison"]
    assert "Comparison Reading" in by_title["Peer / Competitive Comparison"]
    assert "Comparison Gate" in by_title["Peer / Competitive Comparison"]
    assert "Fair Comparison Pack" in by_title["Peer / Competitive Comparison"]
    assert "Linked Comparison Lanes" in by_title["Peer / Competitive Comparison"]
    assert "Peer Requirements" in by_title["Peer / Competitive Comparison"]
    assert "Candidate Peer Frames" in by_title["Peer / Competitive Comparison"]
    assert "Better-Practice Deltas" in by_title["Peer / Competitive Comparison"]
    assert "Decision Reading" in by_title["TAD — Immediate Action Priority"]
    assert "Protect Capital From" in by_title["TAD — Immediate Action Priority"]
    assert "Trigger Pack" in by_title["TAD — Immediate Action Priority"]
    assert "Protects Against" in by_title["TAD — Immediate Action Priority"]
    assert "Decision Front" in by_title["TAD — Immediate Action Priority"]
    assert "Trigger Family" in by_title["TAD — Immediate Action Priority"]
    assert "Financial Exposure" in by_title["TAD — Immediate Action Priority"]
    assert "No-Go Class" in by_title["TAD — Immediate Action Priority"]
    assert "Alternative Conditional Pathways" in by_title["Conditional Redesign Pathway"]
    assert "Local Closure State" in by_title["Claim Permissions / What Not To Do"]


def test_client_facing_executive_thesis_surface_compacts_semantic_duplicates_without_killing_real_challengers():
    body_sections = _compose_client_facing_body_sections(
        main_report_outline={
            "sections": [
                {"section_key": "executive_structural_thesis", "title": "Executive Structural Thesis"},
            ]
        },
        executive_thesis={
            "thesis_state": "conditional_structural_intelligence",
            "local_claim_closure_state": "blocked",
            "conditional_intelligence_reason": "Local closure remains blocked, but bounded structural intelligence survives.",
            "declared_problem": "High area energy use implies inefficiency.",
            "reframed_problem": "The denominator may be wrong until service intensity is normalized.",
            "dominant_contradiction": "Wrong denominator vs real operating driver",
            "hidden_assumption_at_risk": "That area-normalized energy intensity explains the economics.",
            "why_current_question_is_premature": "The framing jumps to retrofit before the denominator is normalized.",
            "what_reality_feature_changes_the_decision": "Service intensity + dock activity + bills.",
            "why_it_matters": "Capital can chase the wrong variable.",
            "dominant_risk": "CAPEX can target the wrong variable.",
            "surprising_but_evidenced_takeaway": "The problem may not be generic energy waste.",
            "dominant_lens": "denominator vs service intensity",
            "top_gold_nuggets": [
                {"gold_nugget": "Wrong denominator can distort capital allocation before any retrofit is sized."},
                {"gold_nugget": "Capital allocation can be distorted when the denominator is wrong before retrofit sizing."},
            ],
            "thesis_constellation_register": [
                {
                    "element_type": "challenger_hypothesis",
                    "title": "Challenger hypothesis",
                    "statement": "A denominator-first framing can misread service intensity as waste.",
                    "why_it_matters": "Benchmark logic can fail before equipment logic starts.",
                    "differentiator": "This preserves a rival lane about service intensity rather than only repeating the lead contradiction.",
                    "evidence_pack_family": "fair_comparison_pack",
                },
                {
                    "element_type": "alternative_variable_candidate",
                    "title": "Alternative variable candidate",
                    "statement": "wrong denominator",
                    "why_it_matters": "The denominator may be the actual decision bottleneck.",
                    "differentiator": "Peer framing changes first.",
                    "evidence_pack_family": "primary_discriminator_pack",
                },
            ],
            "evidence_pack_register": [
                {
                    "pack_family": "primary_discriminator_pack",
                    "pack_title": "Primary discriminator pack",
                    "evidence_items": ["service intensity proxy", "utility bills"],
                    "unlocks": ["local structural closure", "capital logic discrimination"],
                    "why": "This is the minimum pack that changes the denominator meaning of the case.",
                    "evidence_state": "CONDITIONAL_HYPOTHESIS",
                },
                {
                    "pack_family": "fair_comparison_pack",
                    "pack_title": "Fair comparison pack",
                    "evidence_items": ["service intensity proxy", "peer subtype"],
                    "unlocks": ["fair comparison admissibility", "bounded peer screening"],
                    "why": "These fields decide whether comparison logic is valid at all.",
                    "evidence_state": "CONDITIONAL_HYPOTHESIS",
                },
            ],
            "correlation_constellation_register": [
                {
                    "linked_conflict": "Wrong denominator vs real operating driver",
                    "correlation": "service intensity + benchmark choice",
                    "strategic_meaning": "Comparison can fail if the denominator is wrong.",
                    "evidence_needed": ["service intensity proxy", "peer subtype"],
                },
                {
                    "linked_conflict": "Wrong denominator vs real operating driver",
                    "correlation": "service intensity + benchmark frame",
                    "strategic_meaning": "Benchmark logic can fail if the denominator is wrong.",
                    "evidence_needed": ["service intensity proxy", "benchmark basis"],
                },
            ],
        },
        client_facing_tad={"actions": []},
        problem_framing_register=[],
        system_abstraction={},
        cross_layer_conflict_register=[],
        claim_contract_register=[],
    )

    section = body_sections[0]
    content = "\n".join(
        [
            str(block.get("content_en") or block.get("content") or "").strip()
            for block in list(section.get("blocks", []) or [])
            if str(block.get("content_en") or block.get("content") or "").strip()
        ]
    )
    summary = section["thesis_surface_compaction_summary"]
    register = section["thesis_surface_compaction_register"]
    readout_register = section["thesis_surface_readout_register"]

    assert summary["initial_gold_nugget_count"] == 2
    assert summary["retained_gold_nugget_count"] == 1
    assert summary["retained_constellation_count"] == 1
    assert summary["suppressed_count"] >= 2
    assert readout_register
    assert any(row["signal"] == "Framing Risk" for row in readout_register)
    assert "Wrong denominator can distort capital allocation before any retrofit is sized." in content
    assert "Capital allocation can be distorted when the denominator is wrong before retrofit sizing." not in content
    assert "A denominator-first framing can misread service intensity as waste." in content
    assert "Strategic Reading" in content
    assert "Strategic Gold Nugget Set" not in content
    assert any(
        row["lane"] == "gold_nugget" and row["state"] == "suppressed_semantic_overlap"
        for row in register
    )


def test_top_gold_nugget_rows_prefers_theme_diversity_before_duplicates():
    rows = _top_gold_nugget_rows(
        [
            {"nugget_id": "n1", "gold_nugget": "Wrong denominator can distort the whole case."},
            {"nugget_id": "n2", "gold_nugget": "Another denominator warning with different wording."},
            {"nugget_id": "n3", "gold_nugget": "Control boundary can leak value before CAPEX pays back."},
            {"nugget_id": "n4", "gold_nugget": "Demand peaks can dominate cost before kWh does."},
        ],
        gold_nugget_strength_register=[
            {
                "nugget_id": "n1",
                "nugget_theme": "comparison_reframe",
                "selection_priority_score": 12,
                "cross_layer_breadth_score": 4,
                "strength_label": "deep_strategic",
            },
            {
                "nugget_id": "n2",
                "nugget_theme": "comparison_reframe",
                "selection_priority_score": 11,
                "cross_layer_breadth_score": 4,
                "strength_label": "strong",
            },
            {
                "nugget_id": "n3",
                "nugget_theme": "boundary_reframe",
                "selection_priority_score": 10,
                "cross_layer_breadth_score": 3,
                "strength_label": "strong",
            },
            {
                "nugget_id": "n4",
                "nugget_theme": "tariff_orchestration",
                "selection_priority_score": 9,
                "cross_layer_breadth_score": 3,
                "strength_label": "strong",
            },
        ],
        limit=3,
    )

    assert [row["nugget_id"] for row in rows] == ["n1", "n3", "n4"]


def test_top_gold_nugget_rows_compacts_semantic_duplicates_even_across_different_themes():
    rows = _top_gold_nugget_rows(
        [
            {"nugget_id": "n1", "gold_nugget": "Wrong denominator can distort capital allocation before any retrofit is sized."},
            {"nugget_id": "n2", "gold_nugget": "Capital allocation can be distorted when the denominator is wrong before retrofit sizing."},
            {"nugget_id": "n3", "gold_nugget": "Control boundary can leak value before owner-funded CAPEX pays back."},
        ],
        gold_nugget_strength_register=[
            {
                "nugget_id": "n1",
                "nugget_theme": "comparison_reframe",
                "selection_priority_score": 12,
                "cross_layer_breadth_score": 4,
                "strength_label": "deep_strategic",
            },
            {
                "nugget_id": "n2",
                "nugget_theme": "capital_logic",
                "selection_priority_score": 11,
                "cross_layer_breadth_score": 4,
                "strength_label": "strong",
            },
            {
                "nugget_id": "n3",
                "nugget_theme": "boundary_reframe",
                "selection_priority_score": 10,
                "cross_layer_breadth_score": 3,
                "strength_label": "strong",
            },
        ],
        limit=3,
    )

    assert [row["nugget_id"] for row in rows] == ["n1", "n3"]


def test_thesis_constellation_register_compacts_semantically_overlapping_optional_rows():
    rows = _build_thesis_constellation_register(
        primary_conflict={
            "conflict": "Wrong denominator obscures the real operational driver.",
            "evidence_state": "CONDITIONAL_HYPOTHESIS",
            "why_it_matters": "Capital can chase the wrong denominator.",
            "layers_involved": ["finance", "operation"],
        },
        ranked_conflicts=[
            {
                "conflict": "Wrong denominator obscures the real operational driver.",
                "evidence_state": "CONDITIONAL_HYPOTHESIS",
                "why_it_matters": "Capital can chase the wrong denominator.",
                "layers_involved": ["finance", "operation"],
            },
            {
                "conflict": "A denominator-first framing can misread service intensity as waste.",
                "evidence_state": "CONDITIONAL_HYPOTHESIS",
                "why_it_matters": "Benchmark logic can fail before equipment logic starts.",
                "layers_involved": ["benchmarking", "operation"],
            },
        ],
        top_variables=[
            {
                "variable": "wrong denominator",
                "layer": "benchmarking",
                "evidence_state": "CONDITIONAL_HYPOTHESIS",
                "why_it_could_matter": "The denominator may be the actual decision bottleneck.",
                "decision_impact": "Peer framing changes first.",
            }
        ],
        invalid_comparison_risk="Area-based comparison may be invalid before service intensity is normalized.",
        dominant_loss_logic="The visible issue may sit in framing and denominator logic before any physical loss mechanism is proven.",
        hidden_system_boundary_error="Owner and operator may not capture the same value stream.",
        top_gold_nuggets=[
            {
                "gold_nugget": "Wrong denominator can distort capital allocation before physical redesign starts.",
                "evidence_state": "CONDITIONAL_HYPOTHESIS",
            }
        ],
        evidence_pack_register=[{"pack_family": "primary_discriminator_pack"}],
    )

    strategic_nuggets = [row for row in rows if row["element_type"] == "strategic_nugget"]
    challenger_rows = [row for row in rows if row["element_type"] == "challenger_hypothesis"]
    assert len(challenger_rows) == 1
    assert strategic_nuggets == []


def test_structural_intelligence_summary_propagates_outline_gold_nugget_authority():
    inputs = _building_inputs()
    lane = _run_structural_lane(inputs)
    m34 = Motor034Adapter().run({**inputs, **lane})
    m33 = _mock_motor_033()
    m47 = Motor047Adapter().run({**inputs, **lane, "motor_034": m34, "motor_033": m33})
    m48 = Motor048Adapter().run({"motor_034": m34, "motor_047": m47})

    summary = _build_structural_intelligence_summary(
        {
            "canonical_problem_frame": m34["canonical_problem_frame"],
            "executive_thesis": m47["executive_thesis"],
            "main_report_outline": m48["main_report_outline"],
            "client_facing_tad": m48["client_facing_tad"],
            "system_abstraction": lane["motor_037"]["system_abstraction"],
            "dominant_variable_register": lane["motor_038"]["dominant_variable_register"],
            "evidence_state_by_layer_register": lane["motor_045"].get("evidence_state_by_layer_register", []),
            "cross_layer_conflict_register": lane["motor_040"]["cross_layer_conflict_register"],
            "problem_framing_register": lane["motor_041"]["problem_framing_register"],
            "structural_benchmark_register": lane["motor_042"]["structural_benchmark_register"],
            "competitive_comparison_register": lane["motor_043"]["competitive_comparison_register"],
            "conditional_redesign_register": lane["motor_044"]["conditional_redesign_register"],
            "structural_financial_exposure_register": lane["motor_045"]["structural_financial_exposure_register"],
            "minimum_evidence_for_discrimination_register": lane["motor_046"]["minimum_evidence_for_discrimination_register"],
            "structural_claim_permission_register": m34["structural_claim_permission_register"],
            "structural_output_mode_classifier_table": m34["structural_output_mode_classifier_table"],
            "expanded_structural_tad_action_register": m33["expanded_structural_tad_action_register"],
        }
    )

    assert summary["gold_nugget_authority_state"] == m48["main_report_outline"]["gold_nugget_authority_state"]
    assert summary["gold_nugget_source_register"] == m48["main_report_outline"]["gold_nugget_source_register"]
    assert summary["dominant_variable_count"] >= 1
