from __future__ import annotations

import types

import runtime_orchestrator.adapters.motor_017 as motor_017_module
from runtime_orchestrator.adapters.motor_017 import Motor017Adapter
from runtime_orchestrator.adapters.motor_016 import _attach_claim_contract_traces
from runtime_orchestrator.adapters.motor_036 import Motor036Adapter
from runtime_orchestrator.render_section_contract import resolve_render_section_contract


def _hybrid_structural_body_sections(
    *,
    scenario_content: str = "",
    tad_content: str = "",
    a0_content: str = "",
) -> list[dict]:
    return [
        {"title": "Executive Structural Thesis", "chapter_id": "C1", "thesis_anchor_type": "dominant_contradiction", "thesis_anchor_text": "Regulation vs control boundary", "blocks": [{"content": "Dominant Contradiction: Regulation vs control boundary"}]},
        {"title": "Reframed Problem", "chapter_id": "C2", "thesis_anchor_type": "reframed_problem", "thesis_anchor_text": "Need to distinguish the real structural driver before acting.", "blocks": [{"content": "System Reframe      : Need to distinguish the real structural driver before acting."}]},
        {"title": "Dominant Structural Contradiction", "chapter_id": "C3", "thesis_anchor_type": "dominant_contradiction", "thesis_anchor_text": "Regulation vs control boundary", "blocks": [{"content": "Conflict            : Regulation vs control boundary"}]},
        {"title": "System Abstraction Snapshot", "chapter_id": "C4", "thesis_anchor_type": "reframed_problem", "thesis_anchor_text": "Need to distinguish the real structural driver before acting.", "blocks": [{"content": "Control Structure   : bounded control structure"}]},
        {"title": "Dominant Variables", "chapter_id": "C5", "thesis_anchor_type": "dominant_contradiction", "thesis_anchor_text": "Regulation vs control boundary", "blocks": [{"content": "Variable            : dominant_driver"}]},
        {"title": "Scenario Space", "chapter_id": "C6", "thesis_anchor_type": "minimum_discriminating_evidence", "thesis_anchor_text": "bounded minimum evidence", "blocks": [{"content": scenario_content or "Evidence Needed     : bounded evidence\nFalsification       : bounded falsification"}]},
        {"title": "Financial Exposure Under Uncertainty", "chapter_id": "C7", "thesis_anchor_type": "dominant_contradiction", "thesis_anchor_text": "Regulation vs control boundary", "blocks": [{"content": "Exposure If Wrong    : Owner-only economics may fail."}]},
        {"title": "Peer / Competitive Comparison", "chapter_id": "C8", "thesis_anchor_type": "dominant_contradiction", "thesis_anchor_text": "Regulation vs control boundary", "blocks": [{"content": "Peer Type           : archetypal_peer_pattern\nWhat It Proves      : bounded peer framing"}]},
        {"title": "Conditional Redesign Pathway", "chapter_id": "C9", "thesis_anchor_type": "dominant_contradiction", "thesis_anchor_text": "Regulation vs control boundary", "blocks": [{"content": "Trigger Hypothesis  : tenant-driven loads dominate\nKill Condition      : owner-controlled central plant dominates"}]},
        {"title": "Minimum Evidence for Discrimination", "chapter_id": "C10", "thesis_anchor_type": "minimum_discriminating_evidence", "thesis_anchor_text": "bounded minimum evidence", "blocks": [{"content": "Minimum Evidence    : bounded minimum evidence"}]},
        {"title": "TAD — Immediate Action Priority", "chapter_id": "C11", "thesis_anchor_type": "minimum_discriminating_evidence", "thesis_anchor_text": "bounded minimum evidence", "blocks": [{"content": tad_content or "Action              : Request bounded evidence\nMaps To             : bounded minimum evidence"}]},
        {"title": "Claim Permissions / What Not To Do", "chapter_id": "C12", "thesis_anchor_type": "dominant_contradiction", "thesis_anchor_text": "Regulation vs control boundary", "blocks": [{"content": a0_content or "Not Admissible      : ROI remains prohibited"}]},
    ]


def _report_package(
    exec_content: str,
    c2_content: str,
    a0_content: str,
    document_type: str,
    *,
    scenario_content: str = "",
    tad_content: str = "",
    source_family_coverage_table: list[dict] | None = None,
    extra_body_sections: list[dict] | None = None,
    extra_appendix_sections: list[dict] | None = None,
    body_sections_override: list[dict] | None = None,
    appendix_sections_override: list[dict] | None = None,
    claim_contract_register: list[dict] | None = None,
    executive_thesis: dict | None = None,
    main_report_outline: dict | None = None,
    appendix_map: list[dict] | None = None,
    client_facing_tad: dict | None = None,
) -> dict:
    thesis_driven_types = {
        "Decision-Blocked Asset Brief",
        "Exploratory Prior Brief",
        "Compliance / Investment Screening Brief",
        "Structural Contradiction Brief",
        "System Redesign Hypothesis Brief",
        "Competitive Positioning Brief",
        "TAD Action Priority Brief",
        "Full Technical Decision Intelligence Report",
    }
    uses_thesis_body = document_type in thesis_driven_types
    if body_sections_override:
        body_sections = list(body_sections_override)
    elif uses_thesis_body:
        body_sections = _hybrid_structural_body_sections(
            scenario_content=scenario_content,
            tad_content=tad_content,
            a0_content=a0_content,
        )
    else:
        body_sections = [
            {"title": "Framework Context & Executive Brief", "chapter_id": "C1", "blocks": [{"content": exec_content}]},
            {"title": "Operational Identity", "chapter_id": "C2", "blocks": [{"content": c2_content}]},
        ]
        if scenario_content:
            body_sections.append(
                {
                    "title": "Scenario Space Under Current Uncertainty",
                    "chapter_id": "C6",
                    "blocks": [{"content": scenario_content}],
                }
            )
        body_sections.extend(list(extra_body_sections or []))
    appendix_sections = list(appendix_sections_override or [
        {"title": "Governance Status", "chapter_id": "A0", "blocks": [{"content": a0_content}]},
    ])
    if tad_content and not appendix_sections_override:
        appendix_sections.append(
            {
                "title": "TAD — Decision-Admissibility Layer",
                "chapter_id": "A4",
                "blocks": [{"content": tad_content}],
            }
        )
    if not appendix_sections_override:
        appendix_sections.extend(list(extra_appendix_sections or []))
        if uses_thesis_body:
            appendix_sections.extend(list(extra_body_sections or []))
    default_main_report_outline = main_report_outline or {
        "visible_report_mode": document_type,
        "max_primary_sections": 12,
        "sections": [
            {"section_key": "executive_structural_thesis", "title": "Executive Structural Thesis", "render_targets": ["Executive Structural Brief"]},
            {"section_key": "reframed_problem", "title": "Reframed Problem", "render_targets": ["What the Client Thinks the Problem Is", "What the System Thinks the Problem Might Actually Be"]},
            {"section_key": "dominant_structural_contradiction", "title": "Dominant Structural Contradiction", "render_targets": ["Cross-Layer Contradictions"]},
            {"section_key": "system_abstraction_snapshot", "title": "System Abstraction Snapshot", "render_targets": ["System Abstraction Map"]},
            {"section_key": "dominant_variables", "title": "Dominant Variables", "render_targets": ["Dominant Variables"]},
            {"section_key": "scenario_space", "title": "Scenario Space", "render_targets": ["Scenario Space"]},
            {"section_key": "financial_exposure", "title": "Financial Exposure Under Uncertainty", "render_targets": ["Financial Exposure Under Uncertainty"]},
            {"section_key": "peer_comparison", "title": "Peer / Competitive Comparison", "render_targets": ["Competitive / Peer Comparison"]},
            {"section_key": "conditional_redesign", "title": "Conditional Redesign Pathway", "render_targets": ["Conditional Redesign Pathways"]},
            {"section_key": "minimum_evidence", "title": "Minimum Evidence for Discrimination", "render_targets": ["Minimum Evidence for Discrimination"]},
            {"section_key": "tad", "title": "TAD — Immediate Action Priority", "render_targets": ["TAD — Action Priority"]},
            {"section_key": "claim_permissions", "title": "Claim Permissions / What Not To Do", "render_targets": ["What Not To Do Yet"]},
        ],
        "body_section_titles": [
            "Executive Structural Thesis",
            "Reframed Problem",
            "Dominant Structural Contradiction",
            "System Abstraction Snapshot",
            "Dominant Variables",
            "Scenario Space",
            "Financial Exposure Under Uncertainty",
            "Peer / Competitive Comparison",
            "Conditional Redesign Pathway",
            "Minimum Evidence for Discrimination",
            "TAD — Immediate Action Priority",
            "Claim Permissions / What Not To Do",
        ],
    }
    body_sections, appendix_sections, render_section_contract = resolve_render_section_contract(
        document_type,
        body_sections,
        appendix_sections,
    )
    semantic_body_titles = list(default_main_report_outline.get("body_section_titles", []) or [])
    if semantic_body_titles:
        rank = {title: idx for idx, title in enumerate(semantic_body_titles)}
        body_sections = sorted(
            body_sections,
            key=lambda sec: (rank.get(str(sec.get("title", "")).strip(), 999), str(sec.get("chapter_id", ""))),
        )
        for idx, sec in enumerate(body_sections, start=1):
            sec["chapter_id"] = f"C{idx}"
        next_appendix = 0
        for sec in appendix_sections:
            chapter_id = str(sec.get("chapter_id", "")).strip()
            if chapter_id.startswith("A") and chapter_id[1:].isdigit():
                next_appendix = max(next_appendix, int(chapter_id[1:]))
        seen_appendix_ids: set[str] = set()
        for sec in appendix_sections:
            chapter_id = str(sec.get("chapter_id", "")).strip()
            if chapter_id.startswith("A") and chapter_id not in seen_appendix_ids:
                seen_appendix_ids.add(chapter_id)
                continue
            next_appendix += 1
            sec["chapter_id"] = f"A{next_appendix}"
            seen_appendix_ids.add(sec["chapter_id"])
        render_section_contract["body_priority_titles"] = list(semantic_body_titles)
        render_section_contract["body_section_titles"] = list(semantic_body_titles)
        render_section_contract["required_body_sections"] = list(semantic_body_titles)
        render_section_contract["resolved_body_sections"] = [
            str(sec.get("title", "")).strip()
            for sec in body_sections
            if str(sec.get("title", "")).strip()
        ]
    body_sections, appendix_sections, section_claim_trace_register = _attach_claim_contract_traces(
        body_sections,
        appendix_sections,
        list(claim_contract_register or []),
    )
    default_executive_thesis = executive_thesis or {
        "declared_problem": "Need bounded decision support",
        "reframed_problem": "Need to distinguish the real structural driver before acting.",
        "dominant_contradiction": "Regulation vs control boundary",
        "why_it_matters": "Owner-side capital can fail if the control boundary does not match the regulated boundary.",
        "dominant_risk": "Retrofit or compliance capital may not capture owner economics if tenant-driven loads dominate.",
        "what_is_admissible_now": ["Request bounded evidence"],
        "what_is_not_admissible": ["ROI remains prohibited"],
        "minimum_discriminating_evidence": ["bounded minimum evidence"],
        "conditional_redesign": {
            "redesign_path": "Control-boundary and metering redesign",
            "trigger_hypothesis": "Tenant-driven loads dominate realized economics.",
            "conflict_resolved": "Regulation sits with owner while load control sits with tenant.",
            "economic_logic": "Contractual or metering redesign may precede owner CAPEX.",
            "evidence_needed": ["bounded minimum evidence"],
            "kill_condition": "Owner-controlled dominant systems drive realized load economics.",
        },
        "evidence_state": "CONDITIONAL_HYPOTHESIS",
        "report_mode": document_type,
        "confidence_level": "conditional",
        "top_dominant_variables": [
            {"variable": "owner_control_boundary", "layer": "control/responsibility", "evidence_state": "CONDITIONAL_HYPOTHESIS"},
        ],
        "top_scenarios": [
            {"scenario": "Owner-controlled systems dominate", "decision_impact": "bounded"},
        ],
        "top_actions": [
            {"action": "Request bounded evidence", "status": "ACT NOW"},
        ],
        "dominant_lens": "Regulation vs control boundary",
        "supporting_modes": ["System Redesign Hypothesis Brief"],
        "interpretive_signal_register": [
            {
                "signal": "Apparent energy pressure may still be a control-boundary problem.",
                "why_it_matters": "Capital can be directed at the wrong boundary.",
                "evidence_state": "CONDITIONAL_HYPOTHESIS",
            }
        ],
        "hidden_assumption_at_risk": "Owner controls the load boundary that would capture value.",
        "why_current_question_is_premature": "The current question jumps to retrofit before the control boundary is bounded.",
        "what_reality_feature_changes_the_decision": "Whether owner-controlled systems or tenant-driven loads dominate realized economics.",
        "capital_logic_if_assumption_holds": "If owner-controlled systems dominate, owner-side optimization can be screened.",
        "capital_logic_if_assumption_breaks": "If tenant-driven loads dominate, contractual and metering redesign may precede CAPEX.",
        "surprising_but_evidenced_takeaway": "The apparent energy problem is still a control-boundary problem.",
        "dominant_contradiction_selection_basis": {
            "economic_exposure_score": 5,
            "decision_blocking_score": 4,
            "evidence_discrimination_score": 4,
            "cross_layer_span": 3,
            "canonical_problem_frame_bonus": 1,
            "total_score": 17,
        },
        "thesis_ranked_conflict_register": [
            {
                "conflict": "Regulation vs control boundary",
                "selection_basis": {"total_score": 17},
            }
        ],
        "rejected_contradiction_candidates": [],
    }
    default_client_facing_tad = client_facing_tad or {
        "action_count": 1,
        "actions": [
            {
                "action": "Request bounded evidence",
                "maps_to": "Regulation vs control boundary",
            }
        ],
    }
    return {
        "package_id": "rp:test",
        "document_type": document_type,
        "render_section_contract": render_section_contract,
        "claim_contract_register": list(claim_contract_register or []),
        "section_claim_trace_register": section_claim_trace_register,
        "executive_thesis": default_executive_thesis,
        "main_report_outline": default_main_report_outline,
        "appendix_map": list(appendix_map or []),
        "client_facing_tad": default_client_facing_tad,
        "client_facing_body_titles": list(default_main_report_outline.get("body_section_titles", []) or []),
        "planned_chapter_inventory": {
            "chapter_files": [
                "00-Brief.tex",
                *[f"{sec['chapter_id']}.tex" for sec in body_sections],
                *[f"{sec['chapter_id']}.tex" for sec in appendix_sections],
            ],
            "body_chapter_files": [f"{sec['chapter_id']}.tex" for sec in body_sections],
            "appendix_chapter_files": [f"{sec['chapter_id']}.tex" for sec in appendix_sections],
            "canonical_output_mode": render_section_contract["canonical_output_mode"],
            "body_section_titles": [str(sec.get("title", "")).strip() for sec in body_sections if str(sec.get("title", "")).strip()],
            "appendix_section_titles": [str(sec.get("title", "")).strip() for sec in appendix_sections if str(sec.get("title", "")).strip()],
            "required_body_sections": list(render_section_contract.get("required_body_sections", []) or []),
            "required_appendix_sections": list(render_section_contract.get("required_appendix_sections", []) or []),
            "main_include_targets": [
                "Chapters/00-Brief",
                *[f"Chapters/{sec['chapter_id']}" for sec in body_sections],
                *[f"Chapters/{sec['chapter_id']}" for sec in appendix_sections],
            ],
            "forbidden_template_chapters": [
                "00-Abstract.tex",
                "01-Introduction.tex",
                "02-User-Guide.tex",
                "03-Latex-Tutorial.tex",
            ],
        },
        "case_metadata": {
            "case_id": "case:test",
            "document_visible_type": document_type,
        },
        "approved_views": {
            "report_view": {
                "body_sections": body_sections,
                "appendix_sections": appendix_sections,
            }
        },
        "source_family_coverage_table": source_family_coverage_table or [],
    }


def _claim_contracts(*claim_ids: str) -> list[dict]:
    return [
        {
            "claim_id": claim_id,
            "statement": f"{claim_id} contract",
            "permission": (
                "prohibited"
                if claim_id in {"roi_range_claim", "ROI_claim", "energy_savings_claim", "compliance_closure_claim"}
                else "allowed"
            ),
            "evidence_state": "OBSERVED_FACT",
            "supporting_sources": ["test::source"],
            "assumptions": ["test assumption"],
            "falsification_condition": "test falsification",
            "minimum_evidence_required": ["test evidence"],
            "allowed_use": ["test allowed use"],
            "prohibited_use": ["test prohibited use"],
        }
        for claim_id in claim_ids
    ]


def _evidence_layers() -> list[dict]:
    return [
        {
            "layer": layer,
            "evidence_state": "CONDITIONAL_HYPOTHESIS" if layer != "regulation" else "OBSERVED_FACT",
            "dominant_open_questions": [f"{layer} question"],
            "observed_support": [],
            "structural_risk_if_wrong": f"{layer} risk",
            "linked_conflicts": [],
            "linked_problem_frames": [],
        }
        for layer in (
            "physics",
            "operation",
            "energy",
            "finance",
            "regulation",
            "maintenance",
            "logistics",
            "procurement",
            "commercial",
            "culture",
            "control/responsibility",
            "market/competitiveness",
        )
    ]


def _structural_body_sections() -> list[dict]:
    return _hybrid_structural_body_sections()


def test_motor_036_blocks_structural_incoherence_between_screening_and_visible_sections():
    out = Motor036Adapter().run(
        {
            "motor_012": {
                "asset_field_register": [
                    {"field": "GFA", "value": "1678135", "status": "OBSERVED", "scope": "ASSET_LEVEL"},
                    {"field": "year_built", "value": "2020", "status": "OBSERVED", "scope": "ASSET_LEVEL"},
                    {"field": "floor_count", "value": "60", "status": "OBSERVED", "scope": "ASSET_LEVEL"},
                    {"field": "parcel_id", "value": "1012770027.00000000", "status": "OBSERVED", "scope": "ASSET_LEVEL"},
                    {"field": "current_EUI", "value": "120.5", "status": "OBSERVED", "scope": "ASSET_LEVEL"},
                ]
            },
            "motor_014": {
                "claim_permission_summary": {
                    "allowed_count": 0,
                    "conditional_count": 0,
                    "prohibited_count": 0,
                }
            },
            "motor_034": {
                "claim_permission_register": [
                    {"claim_name": "numeric_eui_claim", "current_permission": "allowed"},
                    {"claim_name": "compliance_screening_claim", "current_permission": "allowed"},
                    {"claim_name": "roi_range_claim", "current_permission": "prohibited"},
                ],
                "claim_contract_register": _claim_contracts(
                    "public_asset_identity_claim",
                    "operational_boundary_claim",
                    "process_driver_claim",
                    "energy_baseline_claim",
                    "numeric_eui_claim",
                    "compliance_screening_claim",
                    "financial_exposure_claim",
                    "peer_comparison_claim",
                    "redesign_hypothesis_claim",
                    "roi_range_claim",
                    "TAD_action_claim",
                ),
                "report_type_classifier_table": [
                    {"recommended_report_type": "Compliance / Investment Screening Brief"}
                ],
                "canonical_asset_context_summary": {
                    "supported_clusters": ["geometry_size_cluster"],
                },
            },
            "motor_016": {
                "report_package": _report_package(
                    exec_content="EPISTEMIC STATE: ASSET CONTEXT INSUFFICIENT — One Vanderbilt remains blocked until at least these clusters are clarified.",
                    c2_content=(
                        "Parcel / Property ID: NOT OBSERVED\n"
                        "Total Floors       : NOT OBSERVED\n"
                        "Gross Floor Area   : NOT OBSERVED\n"
                        "Year Built         : NOT OBSERVED\n"
                        "Declared EUI Note  : NOT OBSERVED"
                    ),
                    a0_content="Claim Permissions     : 0 allowed / 0 conditional / 0 prohibited",
                    document_type="Compliance / Investment Screening Brief",
                )
            },
        }
    )

    assert out["can_render_pdf"] is False
    failure_ids = {row["check_id"] for row in out["critical_failures"]}
    assert "claim_summary_vs_matrix" in failure_ids
    assert "governance_summary_vs_matrix" in failure_ids
    assert "structural_primary_body_contract_satisfied" in failure_ids
    assert "scenario_vs_evidence_contract" in failure_ids
    assert "claim_surface_sections_have_statement_traces" in failure_ids


def test_motor_036_passes_when_visible_sections_match_authoritative_state():
    out = Motor036Adapter().run(
        {
            "motor_012": {
                "asset_field_register": [
                    {"field": "GFA", "value": "1678135", "status": "OBSERVED", "scope": "ASSET_LEVEL"},
                    {"field": "year_built", "value": "2020", "status": "OBSERVED", "scope": "ASSET_LEVEL"},
                    {"field": "floor_count", "value": "60", "status": "OBSERVED", "scope": "ASSET_LEVEL"},
                    {"field": "parcel_id", "value": "1012770027.00000000", "status": "OBSERVED", "scope": "ASSET_LEVEL"},
                    {"field": "current_EUI", "value": "120.5", "status": "OBSERVED", "scope": "ASSET_LEVEL"},
                ]
            },
            "motor_014": {
                "claim_permission_summary": {
                    "allowed_count": 2,
                    "conditional_count": 0,
                    "prohibited_count": 1,
                },
                "scenario_evidence_link_register": [
                    {
                        "scenario": "Owner-controlled central plant dominates",
                        "linked_decision_front": "Compliance investment",
                        "linked_evidence_item": "Tenant metering basis, lease responsibility matrix",
                        "financial_meaning": "Compliance-driven capital may sit with the owner boundary.",
                        "falsification_condition": "Tenant-controlled loads dominate the profile.",
                    }
                ],
            },
            "motor_033": {
                "decision_front_actions": [
                    {
                        "current_status": "VALIDATE FIRST",
                        "recommended_posture": "validation_first",
                    }
                ]
            },
                "motor_034": {
                    "claim_permission_register": [
                        {"claim_name": "numeric_eui_claim", "current_permission": "allowed"},
                        {"claim_name": "compliance_screening_claim", "current_permission": "allowed"},
                        {"claim_name": "roi_range_claim", "current_permission": "prohibited"},
                    ],
                    "claim_contract_register": _claim_contracts(
                        "public_asset_identity_claim",
                        "operational_boundary_claim",
                        "process_driver_claim",
                        "energy_baseline_claim",
                        "numeric_eui_claim",
                        "compliance_screening_claim",
                        "financial_exposure_claim",
                        "peer_comparison_claim",
                        "redesign_hypothesis_claim",
                        "roi_range_claim",
                        "TAD_action_claim",
                    ),
                "report_type_classifier_table": [
                    {"recommended_report_type": "Compliance / Investment Screening Brief"}
                ],
                "canonical_asset_context_summary": {
                    "supported_clusters": ["geometry_size_cluster"],
                },
            },
            "motor_016": {
                "report_package": _report_package(
                    exec_content="EPISTEMIC STATE: SCREENING ADMISSIBLE — One Vanderbilt has sufficient public substrate for screening.",
                    c2_content=(
                        "Parcel / Property ID: 1012770027.00000000\n"
                        "Total Floors       : 60\n"
                        "Gross Floor Area   : 1,678,135 sqft\n"
                        "Year Built         : 2020\n"
                        "Declared EUI Note  : 120.5"
                    ),
                    a0_content="Claim Permissions     : 2 allowed / 0 conditional / 1 prohibited",
                    document_type="Compliance / Investment Screening Brief",
                    scenario_content=(
                        "Scenario Alpha\n"
                        "    Financial Mean.: Compliance-driven capital may sit with the owner boundary.\n"
                        "    Falsifies it   : Tenant-controlled loads dominate the profile.\n"
                        "    Decision front : Compliance investment\n"
                        "    Evidence link  : Tenant metering basis, lease responsibility matrix\n"
                        "    Evidence needed: Tenant metering basis, lease responsibility matrix\n"
                    ),
                    tad_content=(
                        "Decision Front   : Compliance investment\n"
                        "Current Status   : VALIDATE FIRST\n"
                        "Why              : bounded screening only\n"
                        "Required Evidence: Tenant metering basis, lease responsibility matrix\n"
                        "Admissible Action: Bounded screening only\n"
                    ),
                    extra_body_sections=[
                        {"title": "Energy Profile & Normative Constraints", "chapter_id": "C3", "blocks": [{"content": "bounded screening energy profile"}]},
                        {"title": "Blocking Conflicts", "chapter_id": "C4", "blocks": [{"content": "systems and control boundary remain open"}]},
                    ],
                    extra_appendix_sections=[
                        {"title": "Public Source Coverage Table", "chapter_id": "A6", "blocks": [{"content": "bounded source coverage"}]},
                        {"title": "Report Type Classifier Table", "chapter_id": "A7", "blocks": [{"content": "recommended output mode remains screening"}]},
                    ],
                    claim_contract_register=_claim_contracts(
                        "public_asset_identity_claim",
                        "operational_boundary_claim",
                        "process_driver_claim",
                        "energy_baseline_claim",
                        "numeric_eui_claim",
                        "compliance_screening_claim",
                        "financial_exposure_claim",
                        "peer_comparison_claim",
                        "redesign_hypothesis_claim",
                        "roi_range_claim",
                        "TAD_action_claim",
                    ),
                )
            },
        }
    )

    assert out["can_render_pdf"] is True
    assert out["critical_failure_count"] == 0


def test_motor_036_accepts_structural_primary_body_with_prompt_sections():
    structural_body_sections = [
        {"title": "Executive Structural Thesis", "chapter_id": "C1", "thesis_anchor_type": "dominant_contradiction", "thesis_anchor_text": "Regulation vs control boundary", "blocks": [{"content": "Dominant Contradiction: Regulation vs control boundary"}]},
        {"title": "Reframed Problem", "chapter_id": "C2", "thesis_anchor_type": "reframed_problem", "thesis_anchor_text": "Need to distinguish owner-controlled upside from tenant-driven load.", "blocks": [{"content": "System Reframe      : Need to distinguish owner-controlled upside from tenant-driven load."}]},
        {"title": "Dominant Structural Contradiction", "chapter_id": "C3", "thesis_anchor_type": "dominant_contradiction", "thesis_anchor_text": "Regulation vs control boundary", "blocks": [{"content": "Conflict            : Regulation vs control boundary"}]},
        {"title": "System Abstraction Snapshot", "chapter_id": "C4", "thesis_anchor_type": "reframed_problem", "thesis_anchor_text": "Need to distinguish owner-controlled upside from tenant-driven load.", "blocks": [{"content": "Control Structure   : bounded"}]},
        {"title": "Dominant Variables", "chapter_id": "C5", "thesis_anchor_type": "dominant_contradiction", "thesis_anchor_text": "Regulation vs control boundary", "blocks": [{"content": "Variable            : tenant_metering"}]},
        {"title": "Scenario Space", "chapter_id": "C6", "thesis_anchor_type": "minimum_discriminating_evidence", "thesis_anchor_text": "utility bills + tenant metering map", "blocks": [{"content": "Evidence Needed     : utility bills + tenant metering map\nFalsification       : Owner-controlled systems dominate"}]},
        {"title": "Financial Exposure Under Uncertainty", "chapter_id": "C7", "thesis_anchor_type": "dominant_contradiction", "thesis_anchor_text": "Regulation vs control boundary", "blocks": [{"content": "Exposure If Wrong    : Retrofit CAPEX may not improve owner economics."}]},
        {"title": "Peer / Competitive Comparison", "chapter_id": "C8", "thesis_anchor_type": "dominant_contradiction", "thesis_anchor_text": "Regulation vs control boundary", "blocks": [{"content": "Peer Type           : archetypal peer pattern\nWhat It Proves      : bounded peer framing"}]},
        {"title": "Conditional Redesign Pathway", "chapter_id": "C9", "thesis_anchor_type": "dominant_contradiction", "thesis_anchor_text": "Regulation vs control boundary", "blocks": [{"content": "Trigger Hypothesis  : Tenant-driven loads dominate.\nKill Condition      : Owner-controlled systems dominate."}]},
        {"title": "Minimum Evidence for Discrimination", "chapter_id": "C10", "thesis_anchor_type": "minimum_discriminating_evidence", "thesis_anchor_text": "utility bills + tenant metering map", "blocks": [{"content": "Minimum Evidence    : utility bills + tenant metering map"}]},
        {"title": "TAD — Immediate Action Priority", "chapter_id": "C11", "thesis_anchor_type": "minimum_discriminating_evidence", "thesis_anchor_text": "utility bills + tenant metering map", "blocks": [{"content": "Action              : Request tenant metering map\nMaps To             : utility bills + tenant metering map"}]},
        {"title": "Claim Permissions / What Not To Do", "chapter_id": "C12", "thesis_anchor_type": "dominant_contradiction", "thesis_anchor_text": "Regulation vs control boundary", "blocks": [{"content": "Not Admissible      : Do not underwrite owner-only retrofit ROI."}]},
    ]
    out = Motor036Adapter().run(
        {
            "motor_014": {
                "claim_permission_summary": {
                    "allowed_count": 0,
                    "conditional_count": 0,
                    "prohibited_count": 0,
                },
                "scenario_evidence_link_register": [
                    {
                        "scenario": "Tenant loads dominate",
                        "linked_decision_front": "Compliance investment",
                        "linked_evidence_item": "Tenant metering basis",
                        "financial_meaning": "Owner-only retrofit economics weaken.",
                        "falsification_condition": "Owner-controlled systems dominate.",
                    }
                ],
            },
            "motor_033": {
                "expanded_structural_tad_action_register": [
                    {
                        "action": "Request tenant metering map",
                        "status": "ACT NOW",
                        "why": "Needed to close control boundary.",
                        "evidence_state": "CONDITIONAL_HYPOTHESIS",
                        "financial_exposure": "Owner-side CAPEX may miss value if wrong.",
                        "evidence_needed": "Tenant metering map",
                        "prohibited_action": "Do not underwrite owner-only retrofit ROI.",
                    }
                ],
                "decision_front_actions": [{"current_status": "ACT NOW", "recommended_posture": "act_now"}],
            },
            "motor_034": {
                "claim_contract_register": _claim_contracts(
                    "operational_boundary_claim",
                    "process_driver_claim",
                    "peer_comparison_claim",
                    "redesign_hypothesis_claim",
                    "financial_exposure_claim",
                    "TAD_action_claim",
                ),
                "structural_claim_permission_register": [
                    {"claim": "peer_comparison_claim", "permission": "hypothesis_only"},
                    {"claim": "redesign_hypothesis_claim", "permission": "hypothesis_only"},
                    {"claim": "financial_exposure_claim", "permission": "allowed"},
                    {"claim": "TAD_action_claim", "permission": "allowed"},
                ],
                "report_type_classifier_table": [{"recommended_report_type": "Structural Contradiction Brief"}],
            },
            "motor_043": {
                "competitive_comparison_register": [
                    {"better_performer": "Peer tower", "what_they_do_better": "Submetering", "structural_advantage": "Boundary clarity", "why_it_matters": "Captures value", "transferability": "Conditional", "evidence_needed": "Lease comparison", "evidence_state": "ARCHETYPAL_PRIOR"},
                ]
            },
            "motor_044": {
                "conditional_redesign_register": [
                    {"hypothesis": "Tenant-driven loads dominate.", "if_confirmed": "Use lease/submetering redesign.", "if_falsified": "Use base-building optimization.", "next_evidence": ["tenant metering map"]},
                ]
            },
            "motor_045": {
                "structural_financial_exposure_register": [
                    {
                        "structural_assumption": "Owner-controllable savings exist.",
                        "evidence_state": "CONDITIONAL_HYPOTHESIS",
                        "financial_exposure_if_wrong": "Retrofit CAPEX may not improve owner economics.",
                        "evidence_needed": "Tenant metering map + control boundary",
                        "allowed_financial_output": ["scenario framing"],
                        "prohibited_financial_output": ["ROI", "IRR", "NPV", "payback", "bankability", "savings claim"],
                    }
                ],
                "evidence_state_by_layer_register": _evidence_layers(),
            },
            "motor_046": {
                "minimum_evidence_for_discrimination_register": [
                    {
                        "rival_hypotheses": ["Owner-controlled upside dominates.", "Tenant-driven loads dominate."],
                        "minimum_evidence": "utility bills + tenant metering map",
                        "source": "operator request",
                        "what_it_confirms": "Owner-side vs tenant-side value capture",
                        "what_it_falsifies": "Incorrect retrofit thesis",
                        "unlocks": "bounded redesign path",
                    }
                ]
            },
            "motor_016": {
                "report_package": _report_package(
                    exec_content="unused",
                    c2_content="unused",
                    a0_content="unused",
                    document_type="Structural Contradiction Brief",
                    body_sections_override=structural_body_sections,
                    appendix_sections_override=[
                        {"title": "Governance Status", "chapter_id": "A0", "blocks": [{"content": "bounded"}]},
                        {"title": "Public Source Coverage Table", "chapter_id": "A6", "blocks": [{"content": "bounded source coverage"}]},
                    ],
                        claim_contract_register=_claim_contracts(
                            "operational_boundary_claim",
                            "process_driver_claim",
                            "peer_comparison_claim",
                            "redesign_hypothesis_claim",
                            "financial_exposure_claim",
                            "TAD_action_claim",
                        ),
                        executive_thesis={
                            "declared_problem": "Need bounded structural screening",
                            "reframed_problem": "Need to distinguish owner-controlled upside from tenant-driven load.",
                            "dominant_contradiction": "Regulation vs control boundary",
                            "why_it_matters": "Owner-only capital can miss value if tenant-driven loads dominate.",
                            "dominant_risk": "Retrofit CAPEX may not improve owner economics.",
                            "what_is_admissible_now": ["Request tenant metering map"],
                            "what_is_not_admissible": ["Do not underwrite owner-only retrofit ROI."],
                            "minimum_discriminating_evidence": ["utility bills + tenant metering map"],
                            "conditional_redesign": {
                                "redesign_path": "Lease/submetering redesign",
                                "trigger_hypothesis": "Tenant-driven loads dominate.",
                                "conflict_resolved": "Regulation sits with owner while load control sits with tenant.",
                                "economic_logic": "Contractual or metering redesign may precede technical CAPEX.",
                                "evidence_needed": ["utility bills + tenant metering map"],
                                "kill_condition": "Owner-controlled systems dominate.",
                            },
                            "evidence_state": "CONDITIONAL_HYPOTHESIS",
                            "report_mode": "Structural Contradiction Brief",
                            "confidence_level": "conditional",
                            "top_dominant_variables": [
                                {"variable": "tenant_metering", "layer": "control/responsibility", "evidence_state": "CONDITIONAL_HYPOTHESIS"},
                            ],
                            "top_scenarios": [
                                {"scenario": "Tenant loads dominate", "decision_impact": "Owner-only retrofit economics weaken."},
                            ],
                            "top_actions": [
                                {"action": "Request tenant metering map", "status": "ACT NOW"},
                            ],
                            "dominant_lens": "Regulation vs control boundary",
                            "supporting_modes": ["System Redesign Hypothesis Brief"],
                            "interpretive_signal_register": [
                                {
                                    "signal": "The apparent efficiency problem may still be a control-boundary problem.",
                                    "why_it_matters": "Owner-side CAPEX can miss value if tenant-driven loads dominate.",
                                    "evidence_state": "CONDITIONAL_HYPOTHESIS",
                                }
                            ],
                            "hidden_assumption_at_risk": "Owner controls the load boundary that would capture value.",
                            "why_current_question_is_premature": "Retrofit economics remain premature until the control boundary is bounded.",
                            "what_reality_feature_changes_the_decision": "Whether tenant-driven loads or owner-controlled systems dominate realized economics.",
                            "capital_logic_if_assumption_holds": "If owner-controlled systems dominate, owner-side optimization can be screened.",
                            "capital_logic_if_assumption_breaks": "If tenant-driven loads dominate, contractual and metering redesign may precede CAPEX.",
                            "surprising_but_evidenced_takeaway": "The apparent retrofit problem is still a control-boundary problem.",
                            "dominant_contradiction_selection_basis": {
                                "economic_exposure_score": 5,
                                "decision_blocking_score": 4,
                                "evidence_discrimination_score": 4,
                                "cross_layer_span": 3,
                                "canonical_problem_frame_bonus": 1,
                                "total_score": 17,
                            },
                            "thesis_ranked_conflict_register": [
                                {
                                    "conflict": "Regulation vs control boundary",
                                    "selection_basis": {"total_score": 17},
                                }
                            ],
                            "rejected_contradiction_candidates": [],
                        },
                    )
                },
            }
        )

    assert out["can_render_pdf"] is True
    assert out["critical_failure_count"] == 0


def test_motor_036_blocks_incomplete_canonical_output_mode_classifier():
    out = Motor036Adapter().run(
        {
            "motor_014": {
                "claim_permission_summary": {
                    "allowed_count": 0,
                    "conditional_count": 0,
                    "prohibited_count": 0,
                },
            },
            "motor_016": {
                "report_package": _report_package(
                    exec_content="EPISTEMIC STATE: SCREENING ADMISSIBLE",
                    c2_content="Gross Floor Area   : 1,678,135 sqft",
                    a0_content="Claim Permissions     : 0 allowed / 0 conditional / 0 prohibited",
                    document_type="Compliance / Investment Screening Brief",
                )
            },
            "motor_034": {
                "report_type_classifier_table": [{"recommended_report_type": "Compliance / Investment Screening Brief"}],
                "report_output_mode_classifier_table": [
                    {
                        "canonical_output_mode": "Compliance / Investment Screening Brief",
                        "visible_output_mode": "Compliance / Investment Screening Brief",
                        "selected_for_publication": True,
                    },
                    {
                        "canonical_output_mode": "Structural Contradiction Brief",
                        "visible_output_mode": "Structural Contradiction Brief",
                        "selected_for_publication": True,
                    },
                ],
            },
        }
    )

    failure_ids = {row["check_id"] for row in out["critical_failures"]}

    assert out["can_render_pdf"] is False
    assert "canonical_output_mode_classifier_complete" in failure_ids


def test_motor_036_blocks_template_chapter_inventory_contamination():
    pkg = _report_package(
        exec_content="EPISTEMIC STATE: SCREENING ADMISSIBLE — One Vanderbilt has sufficient public substrate for screening.",
        c2_content="Gross Floor Area   : 1,678,135 sqft\nYear Built         : 2020",
        a0_content="Claim Permissions     : 2 allowed / 0 conditional / 1 prohibited",
        document_type="Compliance / Investment Screening Brief",
    )
    pkg["planned_chapter_inventory"]["chapter_files"] = [
        "00-Brief.tex",
        "C1.tex",
        "C2.tex",
        "A0.tex",
        "01-Introduction.tex",
    ]

    out = Motor036Adapter().run(
        {
            "motor_012": {
                "asset_field_register": [
                    {"field": "GFA", "value": "1678135", "status": "OBSERVED", "scope": "ASSET_LEVEL"},
                    {"field": "year_built", "value": "2020", "status": "OBSERVED", "scope": "ASSET_LEVEL"},
                ]
            },
            "motor_014": {
                "claim_permission_summary": {
                    "allowed_count": 2,
                    "conditional_count": 0,
                    "prohibited_count": 1,
                }
            },
            "motor_034": {
                "claim_permission_register": [
                    {"claim_name": "numeric_eui_claim", "current_permission": "allowed"},
                    {"claim_name": "compliance_screening_claim", "current_permission": "allowed"},
                    {"claim_name": "roi_range_claim", "current_permission": "prohibited"},
                ],
                "report_type_classifier_table": [
                    {"recommended_report_type": "Compliance / Investment Screening Brief"}
                ],
                "canonical_asset_context_summary": {
                    "supported_clusters": ["geometry_size_cluster"],
                },
            },
            "motor_016": {"report_package": pkg},
        }
    )

    assert out["can_render_pdf"] is False
    failure_ids = {row["check_id"] for row in out["critical_failures"]}
    assert "planned_chapter_inventory_matches_sections" in failure_ids
    assert "planned_chapter_inventory_excludes_template_scaffolding" in failure_ids


def test_motor_036_blocks_tad_vs_executive_and_scope_vs_support_note_incoherence():
    out = Motor036Adapter().run(
        {
            "motor_012": {
                "asset_field_register": [
                    {"field": "GFA", "value": "1678135", "status": "OBSERVED", "scope": "ASSET_LEVEL"},
                ]
            },
            "motor_014": {
                "claim_permission_summary": {
                    "allowed_count": 2,
                    "conditional_count": 0,
                    "prohibited_count": 1,
                },
                "scenario_evidence_link_register": [
                    {
                        "scenario": "Owner-controlled central plant dominates",
                        "linked_decision_front": "Compliance investment",
                        "linked_evidence_item": "Tenant metering basis, lease responsibility matrix",
                        "financial_meaning": "Compliance-driven capital may sit with the owner boundary.",
                        "falsification_condition": "Tenant-controlled loads dominate the profile.",
                    }
                ],
            },
            "motor_033": {
                "decision_front_actions": [
                    {
                        "current_status": "ACT NOW",
                        "recommended_posture": "act_now",
                    }
                ]
            },
            "motor_034": {
                "claim_permission_register": [
                    {"claim_name": "numeric_eui_claim", "current_permission": "allowed"},
                    {"claim_name": "compliance_screening_claim", "current_permission": "allowed"},
                    {"claim_name": "roi_range_claim", "current_permission": "prohibited"},
                ],
                "report_type_classifier_table": [
                    {"recommended_report_type": "Compliance / Investment Screening Brief"}
                ],
                "canonical_asset_context_summary": {
                    "supported_clusters": ["geometry_size_cluster"],
                },
            },
            "motor_016": {
                "report_package": _report_package(
                    exec_content="EPISTEMIC STATE: ASSET CONTEXT INSUFFICIENT — still fully blocked.",
                    c2_content="Gross Floor Area   : 1,678,135 sqft",
                    a0_content="Claim Permissions     : 2 allowed / 0 conditional / 1 prohibited",
                    document_type="Compliance / Investment Screening Brief",
                    scenario_content=(
                        "Scenario Alpha\n"
                        "    Financial Mean.: Compliance-driven capital may sit with the owner boundary.\n"
                        "    Falsifies it   : Tenant-controlled loads dominate the profile.\n"
                        "    Decision front : Compliance investment\n"
                        "    Evidence link  : Tenant metering basis, lease responsibility matrix\n"
                        "    Evidence needed: Tenant metering basis, lease responsibility matrix\n"
                    ),
                    tad_content=(
                        "Decision Front   : Compliance investment\n"
                        "Current Status   : ACT NOW\n"
                        "Why              : bounded screening only\n"
                        "Required Evidence: Tenant metering basis, lease responsibility matrix\n"
                        "Admissible Action: Bounded screening only\n"
                    ),
                    source_family_coverage_table=[
                        {
                            "source_family": "nyc_dof_property_record",
                            "scope": "ENTITY_LEVEL",
                            "support_note": "Source contributed asset-level support for the listed fields.",
                        }
                    ],
                )
            },
        }
    )

    assert out["can_render_pdf"] is False
    failure_ids = {row["check_id"] for row in out["critical_failures"]}
    assert "source_scope_vs_support_note" in failure_ids


def test_motor_036_blocks_hidden_dominant_structural_conflict():
    pkg = _report_package(
        exec_content="bounded",
        c2_content="bounded",
        a0_content="Claim Permissions     : 0 allowed / 0 conditional / 0 prohibited",
        document_type="Structural Contradiction Brief",
        body_sections_override=_structural_body_sections(),
        appendix_sections_override=[
            {"title": "Governance Status", "chapter_id": "A0", "blocks": [{"content": "bounded"}]},
        ],
        claim_contract_register=_claim_contracts(
            "operational_boundary_claim",
            "process_driver_claim",
            "peer_comparison_claim",
            "redesign_hypothesis_claim",
            "financial_exposure_claim",
            "TAD_action_claim",
        ),
    )
    for section in pkg["approved_views"]["report_view"]["body_sections"]:
        if section["title"] == "Cross-Layer Contradictions":
            section["blocks"][0]["content"] = "No cross-layer contradictions were produced."
    pkg["structural_executive_summary"] = {
        "dominant_structural_conflict": "Finance assumes owner-capturable savings before control is proven"
    }
    out = Motor036Adapter().run(
        {
            "motor_014": {"claim_permission_summary": {"allowed_count": 0, "conditional_count": 0, "prohibited_count": 0}},
            "motor_016": {"report_package": pkg},
        }
    )

    assert out["can_render_pdf"] is False
    failure_ids = {row["check_id"] for row in out["critical_failures"]}
    assert "dominant_structural_conflict_visible" in failure_ids


def test_motor_036_blocks_entity_level_owner_support_suppressed_in_executive():
    pkg = _report_package(
        exec_content="Owner        :  (NOT OBSERVED -- NYSE | CIK 0001040971)",
        c2_content="bounded",
        a0_content="Claim Permissions     : 0 allowed / 0 conditional / 0 prohibited",
        document_type="Compliance / Investment Screening Brief",
        source_family_coverage_table=[
            {
                "source_family": "nyc_dof_property_record",
                "scope": "ENTITY_LEVEL",
                "fields_extracted": ["owner"],
                "support_note": "Source contributed entity-level support for the listed fields.",
            }
        ],
    )
    out = Motor036Adapter().run(
        {
            "motor_014": {"claim_permission_summary": {"allowed_count": 0, "conditional_count": 0, "prohibited_count": 0}},
            "motor_016": {"report_package": pkg},
        }
    )

    assert out["can_render_pdf"] is False
    failure_ids = {row["check_id"] for row in out["critical_failures"]}
    assert "rendered_claims_have_claim_contracts" in failure_ids


def test_motor_036_blocks_incomplete_scenario_evidence_contract():
    out = Motor036Adapter().run(
        {
            "motor_014": {
                "claim_permission_summary": {
                    "allowed_count": 0,
                    "conditional_count": 0,
                    "prohibited_count": 0,
                },
                "scenario_evidence_link_register": [
                    {
                        "scenario": "Scenario Alpha",
                        "linked_decision_front": "Compliance investment",
                        "linked_evidence_item": "",
                        "financial_meaning": "Some downside exists.",
                        "falsification_condition": "",
                    }
                ],
            },
            "motor_016": {
                "report_package": _report_package(
                    exec_content="bounded",
                    c2_content="bounded",
                    a0_content="bounded",
                    document_type="Compliance / Investment Screening Brief",
                    scenario_content="Scenario Alpha\n    Financial Mean.: Some downside exists.\n",
                )
            },
        }
    )

    assert out["can_render_pdf"] is False
    failure_ids = {row["check_id"] for row in out["critical_failures"]}
    assert "scenario_vs_evidence_contract" in failure_ids
    assert "scenario_section_vs_evidence_register" in failure_ids


def test_motor_036_blocks_missing_claim_contract_register():
    out = Motor036Adapter().run(
        {
            "motor_014": {
                "claim_permission_summary": {
                    "allowed_count": 1,
                    "conditional_count": 0,
                    "prohibited_count": 0,
                }
            },
            "motor_034": {
                "claim_permission_register": [
                    {"claim_name": "numeric_eui_claim", "current_permission": "allowed"},
                ],
                "structural_claim_permission_register": [
                    {"claim": "financial_exposure_claim", "permission": "allowed"},
                ],
                "report_type_classifier_table": [
                    {"recommended_report_type": "Compliance / Investment Screening Brief"}
                ],
                "canonical_asset_context_summary": {
                    "supported_clusters": [],
                },
            },
            "motor_016": {
                "report_package": _report_package(
                    exec_content="EPISTEMIC STATE: SCREENING ADMISSIBLE",
                    c2_content="Gross Floor Area   : 1,678,135 sqft",
                    a0_content="Claim Permissions     : 1 allowed / 0 conditional / 0 prohibited",
                    document_type="Compliance / Investment Screening Brief",
                )
            },
        }
    )

    assert out["can_render_pdf"] is False
    failure_ids = {row["check_id"] for row in out["critical_failures"]}
    assert "claim_contract_register_complete" in failure_ids


def test_motor_036_blocks_missing_evidence_state_by_layer_register():
    out = Motor036Adapter().run(
        {
            "motor_014": {
                "claim_permission_summary": {
                    "allowed_count": 1,
                    "conditional_count": 0,
                    "prohibited_count": 0,
                }
            },
            "motor_034": {
                "claim_permission_register": [
                    {"claim_name": "numeric_eui_claim", "current_permission": "allowed"},
                ],
                "claim_contract_register": _claim_contracts("numeric_eui_claim", "financial_exposure_claim"),
                "structural_claim_permission_register": [
                    {"claim": "financial_exposure_claim", "permission": "allowed"},
                ],
                "report_type_classifier_table": [
                    {"recommended_report_type": "Compliance / Investment Screening Brief"}
                ],
                "canonical_asset_context_summary": {
                    "supported_clusters": [],
                },
            },
            "motor_045": {
                "structural_financial_exposure_register": [
                    {
                        "structural_assumption": "Owner-controllable savings exist.",
                        "evidence_state": "CONDITIONAL_HYPOTHESIS",
                        "financial_exposure_if_wrong": "Retrofit CAPEX may not improve owner economics.",
                        "evidence_needed": ["tenant metering map"],
                        "allowed_financial_output": ["scenario framing"],
                        "prohibited_financial_output": ["ROI"],
                    }
                ]
            },
            "motor_016": {
                "report_package": _report_package(
                    exec_content="EPISTEMIC STATE: SCREENING ADMISSIBLE",
                    c2_content="Gross Floor Area   : 1,678,135 sqft",
                    a0_content="Claim Permissions     : 1 allowed / 0 conditional / 0 prohibited",
                    document_type="Compliance / Investment Screening Brief",
                )
            },
        }
    )

    assert out["can_render_pdf"] is False
    failure_ids = {row["check_id"] for row in out["critical_failures"]}
    assert "evidence_state_by_layer_register_complete" in failure_ids


def test_motor_036_blocks_building_only_regulatory_logic_for_manufacturing():
    out = Motor036Adapter().run(
        {
            "motor_012": {
                "facility_prior": {
                    "target_definition": {
                        "target_type": "manufacturing_facility",
                        "jurisdiction_scope": ["US-TX"],
                    }
                },
                "dataset_coverage_register": [
                    {"dataset_key": "nyc_ll84_benchmarking", "status": "accepted"},
                ],
                "compliance_applicability_case": {
                    "rule_family_record": [{"rule_family_name": "ASHRAE 90.1"}],
                },
            },
            "motor_037": {
                "system_abstraction": {
                    "regulatory_exposure": {
                        "statement": "ASHRAE-driven building energy compliance context.",
                    }
                }
            },
            "motor_045": {
                "structural_financial_exposure_register": [
                    {
                        "structural_assumption": "Process energy is correctable waste.",
                        "evidence_state": "CONDITIONAL_HYPOTHESIS",
                        "financial_exposure_if_wrong": "CAPEX can target structural process load.",
                        "evidence_needed": ["throughput by shift"],
                        "allowed_financial_output": ["scenario framing"],
                        "prohibited_financial_output": ["ROI", "IRR", "NPV", "payback", "bankability", "savings claim"],
                    }
                ],
                "evidence_state_by_layer_register": _evidence_layers(),
            },
            "motor_016": {
                "report_package": _report_package(
                    exec_content="STRUCTURAL READ: bounded",
                    c2_content="bounded",
                    a0_content="bounded",
                    document_type="Decision-Blocked Asset Brief",
                )
            },
        }
    )

    assert out["can_render_pdf"] is False
    failure_ids = {row["check_id"] for row in out["critical_failures"]}
    assert "manufacturing_regulatory_frame_not_building_only" in failure_ids


def test_motor_036_blocks_nyc_structural_screening_without_ll84_ll97_pluto_dob_dof():
    out = Motor036Adapter().run(
        {
            "motor_012": {
                "facility_prior": {
                    "target_definition": {
                        "target_type": "commercial_building",
                        "jurisdiction_scope": ["US-NY-NYC"],
                    }
                },
                "dataset_coverage_register": [
                    {"dataset_key": "nyc_pluto_property", "status": "accepted"},
                    {"dataset_key": "nyc_ll84_energy_benchmarking", "status": "accepted"},
                ],
            },
            "motor_014": {
                "claim_permission_summary": {
                    "allowed_count": 1,
                    "conditional_count": 0,
                    "prohibited_count": 0,
                }
            },
            "motor_034": {
                "claim_permission_register": [
                    {"claim_name": "compliance_screening_claim", "current_permission": "allowed"},
                ],
                "claim_contract_register": _claim_contracts("compliance_screening_claim"),
                "structural_claim_permission_register": [
                    {"claim": "financial_exposure_claim", "permission": "allowed"},
                ],
            },
            "motor_045": {
                "structural_financial_exposure_register": [
                    {
                        "structural_assumption": "Owner-controllable savings exist.",
                        "evidence_state": "CONDITIONAL_HYPOTHESIS",
                        "financial_exposure_if_wrong": "Retrofit CAPEX may not improve owner economics.",
                        "evidence_needed": ["tenant metering map"],
                        "allowed_financial_output": ["scenario framing"],
                        "prohibited_financial_output": ["ROI", "IRR", "NPV", "payback", "bankability", "savings claim"],
                    }
                ],
                "evidence_state_by_layer_register": _evidence_layers(),
            },
            "motor_016": {
                "report_package": _report_package(
                    exec_content="EPISTEMIC STATE: SCREENING ADMISSIBLE",
                    c2_content="bounded",
                    a0_content="Claim Permissions     : 1 allowed / 0 conditional / 0 prohibited",
                    document_type="Compliance / Investment Screening Brief",
                )
            },
        }
    )

    assert out["can_render_pdf"] is False
    failure_ids = {row["check_id"] for row in out["critical_failures"]}
    assert "nyc_commercial_required_public_datasets_active" in failure_ids


def test_motor_036_blocks_missing_structural_body_sections():
    out = Motor036Adapter().run(
        {
            "motor_012": {
                "facility_prior": {
                    "target_definition": {
                        "target_type": "commercial_building",
                        "jurisdiction_scope": ["US-NY-NYC"],
                    }
                }
            },
            "motor_034": {
                "claim_contract_register": _claim_contracts("peer_comparison_claim", "financial_exposure_claim", "TAD_action_claim"),
                "structural_claim_permission_register": [
                    {"claim": "peer_comparison_claim", "permission": "hypothesis_only"},
                ],
            },
            "motor_043": {
                "competitive_comparison_register": [
                    {"better_performer": "peer", "what_they_do_better": "submetering", "structural_advantage": "clarity", "why_it_matters": "matters", "transferability": "conditional", "evidence_needed": ["metering"], "evidence_state": "CONDITIONAL_HYPOTHESIS"},
                ]
            },
            "motor_045": {
                "structural_financial_exposure_register": [
                    {
                        "structural_assumption": "Owner-controllable savings exist.",
                        "evidence_state": "CONDITIONAL_HYPOTHESIS",
                        "financial_exposure_if_wrong": "Retrofit CAPEX may not improve owner economics.",
                        "evidence_needed": ["tenant metering map"],
                        "allowed_financial_output": ["scenario framing"],
                        "prohibited_financial_output": ["ROI", "IRR", "NPV", "payback", "bankability", "savings claim"],
                    }
                ],
                "evidence_state_by_layer_register": _evidence_layers(),
            },
            "motor_016": {
                "report_package": _report_package(
                    exec_content="STRUCTURAL READ: bounded structural contradiction framing.",
                    c2_content="bounded",
                    a0_content="bounded",
                    document_type="Structural Contradiction Brief",
                )
            },
        }
    )

    assert out["can_render_pdf"] is False
    failure_ids = {row["check_id"] for row in out["critical_failures"]}
    assert "structural_primary_body_contract_satisfied" in failure_ids


def test_motor_036_blocks_missing_render_section_contract():
    pkg = _report_package(
        exec_content="EPISTEMIC STATE: SCREENING ADMISSIBLE",
        c2_content="Gross Floor Area   : 1,678,135 sqft",
        a0_content="Claim Permissions     : 1 allowed / 0 conditional / 0 prohibited",
        document_type="Compliance / Investment Screening Brief",
    )
    pkg.pop("render_section_contract", None)

    out = Motor036Adapter().run(
        {
            "motor_014": {
                "claim_permission_summary": {
                    "allowed_count": 1,
                    "conditional_count": 0,
                    "prohibited_count": 0,
                }
            },
            "motor_034": {
                "claim_permission_register": [
                    {"claim_name": "compliance_screening_claim", "current_permission": "allowed"},
                ],
                "claim_contract_register": _claim_contracts("compliance_screening_claim"),
                "report_type_classifier_table": [
                    {"recommended_report_type": "Compliance / Investment Screening Brief"}
                ],
            },
            "motor_016": {"report_package": pkg},
        }
    )

    assert out["can_render_pdf"] is False
    failure_ids = {row["check_id"] for row in out["critical_failures"]}
    assert "output_mode_render_contract_complete" in failure_ids


def test_motor_036_blocks_required_structural_body_section_moved_to_appendix():
    body_sections = _structural_body_sections()
    appendix_sections = [
        {"title": "Governance Status", "chapter_id": "A0", "blocks": [{"content": "bounded"}]},
    ]
    moved = body_sections.pop(3)
    moved["chapter_id"] = "A1"
    appendix_sections.append(moved)

    out = Motor036Adapter().run(
        {
            "motor_012": {
                "facility_prior": {
                    "target_definition": {
                        "target_type": "commercial_building",
                        "jurisdiction_scope": ["US-NY-NYC"],
                    }
                },
                "dataset_coverage_register": [
                    {"dataset_key": "nyc_pluto_property", "status": "accepted"},
                    {"dataset_key": "nyc_ll84_energy_benchmarking", "status": "accepted"},
                    {"dataset_key": "nyc_ll97_public_filing_candidate", "status": "accepted"},
                    {"dataset_key": "nyc_dob_permits", "status": "accepted"},
                    {"dataset_key": "nyc_dof_property_record", "status": "accepted"},
                ],
            },
            "motor_034": {
                "claim_contract_register": _claim_contracts("peer_comparison_claim", "financial_exposure_claim", "TAD_action_claim"),
                "structural_claim_permission_register": [
                    {"claim": "peer_comparison_claim", "permission": "hypothesis_only"},
                    {"claim": "financial_exposure_claim", "permission": "allowed"},
                    {"claim": "TAD_action_claim", "permission": "allowed"},
                ],
            },
            "motor_043": {
                "competitive_comparison_register": [
                    {
                        "better_performer": "peer",
                        "what_they_do_better": "submetering",
                        "structural_advantage": "clarity",
                        "why_it_matters": "matters",
                        "transferability": "conditional",
                        "evidence_needed": ["metering"],
                        "evidence_state": "CONDITIONAL_HYPOTHESIS",
                    },
                ]
            },
            "motor_045": {
                "structural_financial_exposure_register": [
                    {
                        "structural_assumption": "Owner-controllable savings exist.",
                        "evidence_state": "CONDITIONAL_HYPOTHESIS",
                        "financial_exposure_if_wrong": "Retrofit CAPEX may not improve owner economics.",
                        "evidence_needed": ["tenant metering map"],
                        "allowed_financial_output": ["scenario framing"],
                        "prohibited_financial_output": ["ROI", "IRR", "NPV", "payback", "bankability", "savings claim"],
                    }
                ],
                "evidence_state_by_layer_register": _evidence_layers(),
            },
            "motor_016": {
                "report_package": _report_package(
                    exec_content="STRUCTURAL READ: bounded structural contradiction framing.",
                    c2_content="bounded",
                    a0_content="bounded",
                    document_type="Structural Contradiction Brief",
                    body_sections_override=body_sections,
                    appendix_sections_override=appendix_sections,
                )
            },
        }
    )

    assert out["can_render_pdf"] is False
    failure_ids = {row["check_id"] for row in out["critical_failures"]}
    assert "structural_primary_body_contract_satisfied" in failure_ids


def test_motor_036_blocks_render_inventory_that_diverges_from_contract_order():
    pkg = _report_package(
        exec_content="EPISTEMIC STATE: SCREENING ADMISSIBLE",
        c2_content="Gross Floor Area   : 1,678,135 sqft",
        a0_content="Claim Permissions     : 1 allowed / 0 conditional / 0 prohibited",
        document_type="Compliance / Investment Screening Brief",
    )
    pkg["render_section_contract"]["resolved_body_sections"] = list(
        reversed(pkg["render_section_contract"]["resolved_body_sections"])
    )

    out = Motor036Adapter().run(
        {
            "motor_014": {
                "claim_permission_summary": {
                    "allowed_count": 1,
                    "conditional_count": 0,
                    "prohibited_count": 0,
                }
            },
            "motor_034": {
                "claim_permission_register": [
                    {"claim_name": "compliance_screening_claim", "current_permission": "allowed"},
                ],
                "claim_contract_register": _claim_contracts("compliance_screening_claim"),
                "report_type_classifier_table": [
                    {"recommended_report_type": "Compliance / Investment Screening Brief"}
                ],
            },
            "motor_016": {"report_package": pkg},
        }
    )

    assert out["can_render_pdf"] is False
    failure_ids = {row["check_id"] for row in out["critical_failures"]}
    assert "selected_output_mode_sections_match_render_inventory" in failure_ids


def test_motor_036_blocks_rendered_claims_without_claim_contracts():
    out = Motor036Adapter().run(
        {
            "motor_012": {
                "asset_field_register": [
                    {"field": "current_EUI", "value": "120.5", "status": "OBSERVED", "scope": "ASSET_LEVEL"},
                ]
            },
            "motor_014": {
                "claim_permission_summary": {
                    "allowed_count": 2,
                    "conditional_count": 0,
                    "prohibited_count": 0,
                }
            },
            "motor_034": {
                "claim_permission_register": [
                    {"claim_name": "numeric_eui_claim", "current_permission": "allowed"},
                    {"claim_name": "compliance_screening_claim", "current_permission": "allowed"},
                ],
                "claim_contract_register": _claim_contracts("numeric_eui_claim"),
                "report_type_classifier_table": [
                    {"recommended_report_type": "Compliance / Investment Screening Brief"}
                ],
            },
            "motor_016": {
                "report_package": _report_package(
                    exec_content="EPISTEMIC STATE: SCREENING ADMISSIBLE",
                    c2_content="Declared EUI Note  : 120.5",
                    a0_content="Claim Permissions     : 2 allowed / 0 conditional / 0 prohibited",
                    document_type="Compliance / Investment Screening Brief",
                )
            },
        }
    )

    assert out["can_render_pdf"] is False
    failure_ids = {row["check_id"] for row in out["critical_failures"]}
    assert "rendered_claims_have_claim_contracts" in failure_ids


def test_motor_036_blocks_missing_executive_thesis_fields():
    pkg = _report_package(
        exec_content="EPISTEMIC STATE: SCREENING ADMISSIBLE",
        c2_content="Declared EUI Note  : 120.5",
        a0_content="Claim Permissions     : 2 allowed / 0 conditional / 0 prohibited",
        document_type="Compliance / Investment Screening Brief",
        executive_thesis={
            "declared_problem": "Need bounded decision support",
            "reframed_problem": "Need to distinguish owner-side control boundary.",
            "dominant_contradiction": "",
            "minimum_discriminating_evidence": [],
            "report_mode": "Compliance / Investment Screening Brief",
        },
    )
    out = Motor036Adapter().run(
        {
            "motor_012": {"asset_field_register": []},
            "motor_014": {"claim_permission_summary": {"allowed_count": 0, "conditional_count": 0, "prohibited_count": 0}},
            "motor_034": {
                "claim_permission_register": [],
                "claim_contract_register": [],
                "report_type_classifier_table": [{"recommended_report_type": "Compliance / Investment Screening Brief"}],
                "report_output_mode_classifier_table": [
                    {
                        "canonical_output_mode": "Compliance / Investment Screening Brief",
                        "selected_for_publication": True,
                        "classification_state": "selected_primary_default",
                    }
                ],
            },
            "motor_016": {"report_package": pkg},
        }
    )

    assert out["can_render_pdf"] is False
    failure_ids = {row["check_id"] for row in out["critical_failures"]}
    assert "executive_thesis_exists" in failure_ids


def test_motor_036_accepts_correctly_inadmissible_thesis_bypass():
    pkg = _report_package(
        exec_content="Address candidate only.",
        c2_content="Address declared only.",
        a0_content="Claim Permissions     : 0 allowed / 0 conditional / 0 prohibited",
        document_type="Entity Address Classification Brief",
        executive_thesis={
            "declared_problem": "Need bounded target understanding before structural interpretation.",
            "reframed_problem": "Structural interpretation remains premature because the case is not yet bounded enough to support a dominant contradiction.",
            "dominant_contradiction": "",
            "why_it_matters": "Structural thesis remains inadmissible until the case crosses the problem-framing threshold for structural interpretation.",
            "dominant_risk": "A structural thesis here would overstate what the system actually knows about the case.",
            "hidden_assumption_at_risk": "",
            "why_current_question_is_premature": "Structural thesis remains inadmissible until the case crosses the problem-framing threshold for structural interpretation.",
            "what_reality_feature_changes_the_decision": "",
            "capital_logic_if_assumption_holds": "",
            "capital_logic_if_assumption_breaks": "",
            "surprising_but_evidenced_takeaway": "",
            "what_is_admissible_now": [],
            "what_is_not_admissible": [],
            "minimum_discriminating_evidence": [],
            "minimum_discriminating_evidence_source": "",
            "minimum_discriminating_evidence_unlocks": [],
            "conditional_redesign": {},
            "evidence_state": "INADMISSIBLE_CLAIM",
            "report_mode": "Target Classification Brief",
            "confidence_level": "inadmissible",
            "top_dominant_variables": [],
            "top_scenarios": [],
            "top_actions": [],
            "dominant_lens": "",
            "supporting_modes": [],
            "primary_financial_exposure": {},
            "primary_peer_comparison": {},
            "interpretive_signal_register": [],
            "dominant_contradiction_selection_basis": {},
            "thesis_ranked_conflict_register": [],
            "rejected_contradiction_candidates": [],
            "thesis_state": "inadmissible_thesis",
            "inadmissibility_reason": "Structural thesis remains inadmissible until the case crosses the problem-framing threshold for structural interpretation.",
        },
        main_report_outline={
            "visible_report_mode": "Target Classification Brief",
            "dominant_lens": "",
            "supporting_modes": [],
            "max_primary_sections": 0,
            "compression_state": "inadmissible_bypass",
            "sections": [],
            "body_section_titles": [],
        },
        client_facing_tad={
            "action_count": 0,
            "actions": [],
            "compression_state": "inadmissible_bypass",
        },
    )
    out = Motor036Adapter().run(
        {
            "motor_014": {"claim_permission_summary": {"allowed_count": 0, "conditional_count": 0, "prohibited_count": 0}},
            "motor_034": {
                "claim_permission_register": [],
                "claim_contract_register": [],
                "report_type_classifier_table": [{"recommended_report_type": "Target Classification Brief"}],
                "report_output_mode_classifier_table": [
                    {"canonical_output_mode": "Target Classification Brief", "visible_output_mode": "Entity Address Classification Brief", "selected_for_publication": True},
                    {"canonical_output_mode": "Decision-Blocked Asset Brief", "visible_output_mode": "Decision-Blocked Asset Brief", "selected_for_publication": False},
                    {"canonical_output_mode": "Exploratory Prior Brief", "visible_output_mode": "Exploratory Prior Brief", "selected_for_publication": False},
                    {"canonical_output_mode": "Compliance / Investment Screening Brief", "visible_output_mode": "Compliance / Investment Screening Brief", "selected_for_publication": False},
                    {"canonical_output_mode": "Structural Contradiction Brief", "visible_output_mode": "Structural Contradiction Brief", "selected_for_publication": False},
                    {"canonical_output_mode": "System Redesign Hypothesis Brief", "visible_output_mode": "System Redesign Hypothesis Brief", "selected_for_publication": False},
                    {"canonical_output_mode": "Competitive Positioning Brief", "visible_output_mode": "Competitive Positioning Brief", "selected_for_publication": False},
                    {"canonical_output_mode": "TAD Action Priority Brief", "visible_output_mode": "TAD Action Priority Brief", "selected_for_publication": False},
                    {"canonical_output_mode": "Full Technical Decision Intelligence Report", "visible_output_mode": "Full Technical Decision Intelligence Report", "selected_for_publication": False},
                ],
            },
            "motor_016": {"report_package": pkg},
        }
    )

    assert out["can_render_pdf"] is True
    assert out["critical_failure_count"] == 0


def test_motor_036_skips_congruence_thesis_bridge_requirements_under_inadmissible_bypass():
    pkg = _report_package(
        exec_content="Address candidate only.",
        c2_content="Address declared only.",
        a0_content="Claim Permissions     : 0 allowed / 0 conditional / 0 prohibited",
        document_type="Entity Address Classification Brief",
        executive_thesis={
            "declared_problem": "Need bounded target understanding before structural interpretation.",
            "reframed_problem": "Structural interpretation remains premature because the case is not yet bounded enough to support a dominant contradiction.",
            "dominant_contradiction": "",
            "why_it_matters": "Structural thesis remains inadmissible until the case crosses the problem-framing threshold for structural interpretation.",
            "dominant_risk": "A structural thesis here would overstate what the system actually knows about the case.",
            "hidden_assumption_at_risk": "",
            "why_current_question_is_premature": "Structural thesis remains inadmissible until the case crosses the problem-framing threshold for structural interpretation.",
            "what_reality_feature_changes_the_decision": "",
            "capital_logic_if_assumption_holds": "",
            "capital_logic_if_assumption_breaks": "",
            "surprising_but_evidenced_takeaway": "",
            "what_is_admissible_now": [],
            "what_is_not_admissible": [],
            "minimum_discriminating_evidence": [],
            "minimum_discriminating_evidence_source": "",
            "minimum_discriminating_evidence_unlocks": [],
            "conditional_redesign": {},
            "evidence_state": "INADMISSIBLE_CLAIM",
            "report_mode": "Target Classification Brief",
            "confidence_level": "inadmissible",
            "top_dominant_variables": [],
            "top_scenarios": [],
            "top_actions": [],
            "dominant_lens": "",
            "supporting_modes": [],
            "primary_financial_exposure": {},
            "primary_peer_comparison": {},
            "interpretive_signal_register": [],
            "dominant_contradiction_selection_basis": {},
            "thesis_ranked_conflict_register": [],
            "rejected_contradiction_candidates": [],
            "thesis_state": "inadmissible_thesis",
            "inadmissibility_reason": "Structural thesis remains inadmissible until the case crosses the problem-framing threshold for structural interpretation.",
        },
        main_report_outline={
            "visible_report_mode": "Target Classification Brief",
            "dominant_lens": "",
            "supporting_modes": [],
            "max_primary_sections": 0,
            "compression_state": "inadmissible_bypass",
            "sections": [],
            "body_section_titles": [],
        },
        client_facing_tad={
            "action_count": 0,
            "actions": [],
            "compression_state": "inadmissible_bypass",
        },
    )
    out = Motor036Adapter().run(
        {
            "motor_014": {
                "claim_permission_summary": {"allowed_count": 0, "conditional_count": 0, "prohibited_count": 0},
                "scenario_evidence_link_register": [
                    {
                        "scenario": "owner-controlled systems dominate",
                        "financial_meaning": "Owner-side action only matters if the case ever becomes structurally admissible.",
                        "falsification_condition": "The case never crosses the structural-bounding threshold.",
                        "linked_evidence_item": "bounded target evidence",
                    }
                ],
            },
            "motor_034": {
                "claim_permission_register": [],
                "claim_contract_register": [],
                "report_type_classifier_table": [{"recommended_report_type": "Target Classification Brief"}],
                "report_output_mode_classifier_table": [
                    {"canonical_output_mode": "Target Classification Brief", "visible_output_mode": "Entity Address Classification Brief", "selected_for_publication": True},
                    {"canonical_output_mode": "Decision-Blocked Asset Brief", "visible_output_mode": "Decision-Blocked Asset Brief", "selected_for_publication": False},
                    {"canonical_output_mode": "Exploratory Prior Brief", "visible_output_mode": "Exploratory Prior Brief", "selected_for_publication": False},
                    {"canonical_output_mode": "Compliance / Investment Screening Brief", "visible_output_mode": "Compliance / Investment Screening Brief", "selected_for_publication": False},
                    {"canonical_output_mode": "Structural Contradiction Brief", "visible_output_mode": "Structural Contradiction Brief", "selected_for_publication": False},
                    {"canonical_output_mode": "System Redesign Hypothesis Brief", "visible_output_mode": "System Redesign Hypothesis Brief", "selected_for_publication": False},
                    {"canonical_output_mode": "Competitive Positioning Brief", "visible_output_mode": "Competitive Positioning Brief", "selected_for_publication": False},
                    {"canonical_output_mode": "TAD Action Priority Brief", "visible_output_mode": "TAD Action Priority Brief", "selected_for_publication": False},
                    {"canonical_output_mode": "Full Technical Decision Intelligence Report", "visible_output_mode": "Full Technical Decision Intelligence Report", "selected_for_publication": False},
                ],
            },
            "motor_043": {
                "competitive_comparison_register": [
                    {
                        "peer_type": "Archetypal peer pattern",
                        "evidence_state": "ARCHETYPAL_PRIOR",
                        "transferability": "conditional only if the case becomes structurally admissible",
                    }
                ]
            },
            "motor_051": {
                "invalid_comparison_risk_register": [
                    {
                        "risk_name": "premature_peer_equivalence",
                        "risk_level": "high",
                        "trigger": "Comparable peer framing would be invalid before the target is structurally bounded.",
                        "required_normalization": ["bounded target evidence"],
                    }
                ]
            },
            "motor_052": {
                "measurement_strategy_register": [
                    {
                        "hypothesis": "target_must_be_bounded_before_structural_measurement",
                        "minimum_measurement": "bounded target evidence",
                        "why": "The first step is target bounding, not broader measurement.",
                    }
                ]
            },
            "motor_054": {
                "congruence_action_priority_register": [
                    {
                        "strategic_action": "REQUEST_MINIMUM_EVIDENCE",
                        "status": "VALIDATE FIRST",
                        "why": "Structural interpretation is still inadmissible.",
                        "gold_nugget": "Bound the target before promoting any structural comparison or measurement lane.",
                        "evidence_needed": ["bounded target evidence"],
                        "prohibited_action": "Do not act on a structural thesis yet.",
                    }
                ],
                "congruence_claim_contract_register": [],
            },
            "motor_016": {"report_package": pkg},
        }
    )

    failure_ids = {row["check_id"] for row in out["critical_failures"]}
    assert "scenario_section_vs_evidence_register" not in failure_ids
    assert "invalid_comparison_not_used_as_peer_evidence" not in failure_ids
    assert "measurement_recommendations_require_hypothesis" not in failure_ids


def test_motor_036_blocks_missing_interpretive_thesis_fields():
    pkg = _report_package(
        exec_content="EPISTEMIC STATE: SCREENING ADMISSIBLE",
        c2_content="Declared EUI Note  : 120.5",
        a0_content="Claim Permissions     : 2 allowed / 0 conditional / 0 prohibited",
        document_type="Compliance / Investment Screening Brief",
        executive_thesis={
            "declared_problem": "Need bounded decision support",
            "reframed_problem": "Need to distinguish owner-side control boundary.",
            "dominant_contradiction": "Regulation vs control boundary",
            "minimum_discriminating_evidence": ["tenant metering map"],
            "report_mode": "Compliance / Investment Screening Brief",
            "dominant_lens": "Regulation vs control boundary",
            "interpretive_signal_register": [],
            "hidden_assumption_at_risk": "",
            "why_current_question_is_premature": "",
            "what_reality_feature_changes_the_decision": "",
            "capital_logic_if_assumption_holds": "",
            "capital_logic_if_assumption_breaks": "",
            "surprising_but_evidenced_takeaway": "",
            "dominant_contradiction_selection_basis": {"total_score": 9},
            "thesis_ranked_conflict_register": [{"conflict": "Regulation vs control boundary", "selection_basis": {"total_score": 9}}],
        },
    )
    out = Motor036Adapter().run(
        {
            "motor_012": {"asset_field_register": []},
            "motor_014": {"claim_permission_summary": {"allowed_count": 0, "conditional_count": 0, "prohibited_count": 0}},
            "motor_034": {
                "claim_permission_register": [],
                "claim_contract_register": [],
                "report_type_classifier_table": [{"recommended_report_type": "Compliance / Investment Screening Brief"}],
                "report_output_mode_classifier_table": [
                    {
                        "canonical_output_mode": "Compliance / Investment Screening Brief",
                        "selected_for_publication": True,
                        "classification_state": "selected_primary_default",
                    }
                ],
            },
            "motor_016": {"report_package": pkg},
        }
    )

    assert out["can_render_pdf"] is False
    failure_ids = {row["check_id"] for row in out["critical_failures"]}
    assert "executive_thesis_interpretive_fields_complete" in failure_ids


def test_motor_036_blocks_missing_dominant_thesis_selection_basis():
    pkg = _report_package(
        exec_content="EPISTEMIC STATE: SCREENING ADMISSIBLE",
        c2_content="Declared EUI Note  : 120.5",
        a0_content="Claim Permissions     : 2 allowed / 0 conditional / 0 prohibited",
        document_type="Compliance / Investment Screening Brief",
        executive_thesis={
            **_report_package(
                exec_content="x",
                c2_content="x",
                a0_content="x",
                document_type="Compliance / Investment Screening Brief",
            )["executive_thesis"],
            "dominant_contradiction_selection_basis": {},
            "thesis_ranked_conflict_register": [],
            "dominant_lens": "Unrelated lens",
        },
    )
    out = Motor036Adapter().run(
        {
            "motor_012": {"asset_field_register": []},
            "motor_014": {"claim_permission_summary": {"allowed_count": 0, "conditional_count": 0, "prohibited_count": 0}},
            "motor_034": {
                "claim_permission_register": [],
                "claim_contract_register": [],
                "report_type_classifier_table": [{"recommended_report_type": "Compliance / Investment Screening Brief"}],
                "report_output_mode_classifier_table": [
                    {
                        "canonical_output_mode": "Compliance / Investment Screening Brief",
                        "selected_for_publication": True,
                        "classification_state": "selected_primary_default",
                    }
                ],
            },
            "motor_016": {"report_package": pkg},
        }
    )

    assert out["can_render_pdf"] is False
    failure_ids = {row["check_id"] for row in out["critical_failures"]}
    assert "dominant_thesis_selection_basis_present" in failure_ids


def test_motor_036_blocks_client_facing_tad_above_limit():
    pkg = _report_package(
        exec_content="EPISTEMIC STATE: SCREENING ADMISSIBLE",
        c2_content="Declared EUI Note  : 120.5",
        a0_content="Claim Permissions     : 2 allowed / 0 conditional / 0 prohibited",
        document_type="Compliance / Investment Screening Brief",
        client_facing_tad={
            "action_count": 6,
            "actions": [
                {"action": f"Action {idx}", "maps_to": "Regulation vs control boundary"}
                for idx in range(1, 7)
            ],
        },
    )
    out = Motor036Adapter().run(
        {
            "motor_012": {"asset_field_register": []},
            "motor_014": {"claim_permission_summary": {"allowed_count": 0, "conditional_count": 0, "prohibited_count": 0}},
            "motor_034": {
                "claim_permission_register": [],
                "claim_contract_register": [],
                "report_type_classifier_table": [{"recommended_report_type": "Compliance / Investment Screening Brief"}],
                "report_output_mode_classifier_table": [
                    {
                        "canonical_output_mode": "Compliance / Investment Screening Brief",
                        "selected_for_publication": True,
                        "classification_state": "selected_primary_default",
                    }
                ],
            },
            "motor_016": {"report_package": pkg},
        }
    )

    assert out["can_render_pdf"] is False
    failure_ids = {row["check_id"] for row in out["critical_failures"]}
    assert "client_facing_tad_limited" in failure_ids


def test_motor_036_blocks_legacy_duplicate_sections_in_body():
    pkg = _report_package(
        exec_content="EPISTEMIC STATE: SCREENING ADMISSIBLE",
        c2_content="Declared EUI Note  : 120.5",
        a0_content="Claim Permissions     : 2 allowed / 0 conditional / 0 prohibited",
        document_type="Compliance / Investment Screening Brief",
        body_sections_override=[
            {"title": "Executive Structural Brief", "section_id": "c5", "chapter_id": "C5", "blocks": [{"content": "STRUCTURAL READ"}]},
            {"title": "Blocking Conflicts", "section_id": "c3", "chapter_id": "C3", "blocks": [{"content": "legacy duplicate body"}]},
            {"title": "Cross-Layer Contradictions", "section_id": "c11", "chapter_id": "C11", "blocks": [{"content": "Conflict            : Regulation vs control boundary"}]},
        ],
    )
    out = Motor036Adapter().run(
        {
            "motor_012": {"asset_field_register": []},
            "motor_014": {"claim_permission_summary": {"allowed_count": 0, "conditional_count": 0, "prohibited_count": 0}},
            "motor_034": {
                "claim_permission_register": [],
                "claim_contract_register": [],
                "report_type_classifier_table": [{"recommended_report_type": "Compliance / Investment Screening Brief"}],
                "report_output_mode_classifier_table": [
                    {
                        "canonical_output_mode": "Compliance / Investment Screening Brief",
                        "selected_for_publication": True,
                        "classification_state": "selected_primary_default",
                    }
                ],
            },
            "motor_016": {"report_package": pkg},
        }
    )

    assert out["can_render_pdf"] is False
    failure_ids = {row["check_id"] for row in out["critical_failures"]}
    assert "legacy_duplicate_sections_demoted_from_body" in failure_ids


def test_motor_036_blocks_body_sections_with_unmatched_thesis_anchor_text():
    body_sections = _structural_body_sections()
    body_sections[4]["thesis_anchor_text"] = "unrelated commercial vanity metric"
    body_sections[4]["blocks"] = [{"content": "Variable            : unrelated commercial vanity metric"}]
    pkg = _report_package(
        exec_content="EPISTEMIC STATE: SCREENING ADMISSIBLE",
        c2_content="Declared EUI Note  : 120.5",
        a0_content="Claim Permissions     : 2 allowed / 0 conditional / 0 prohibited",
        document_type="Compliance / Investment Screening Brief",
        body_sections_override=body_sections,
    )
    out = Motor036Adapter().run(
        {
            "motor_012": {"asset_field_register": []},
            "motor_014": {"claim_permission_summary": {"allowed_count": 0, "conditional_count": 0, "prohibited_count": 0}},
            "motor_034": {
                "claim_permission_register": [],
                "claim_contract_register": [],
                "report_type_classifier_table": [{"recommended_report_type": "Compliance / Investment Screening Brief"}],
                "report_output_mode_classifier_table": [
                    {
                        "canonical_output_mode": "Compliance / Investment Screening Brief",
                        "selected_for_publication": True,
                        "classification_state": "selected_primary_default",
                    }
                ],
            },
            "motor_016": {"report_package": pkg},
        }
    )

    assert out["can_render_pdf"] is False
    failure_ids = {row["check_id"] for row in out["critical_failures"]}
    assert "body_sections_anchor_to_dominant_thesis" in failure_ids


def test_motor_036_blocks_appendix_titles_that_compete_with_body():
    body_sections = _structural_body_sections()
    appendix_sections = [
        {"title": "Governance Status", "chapter_id": "A0", "blocks": [{"content": "bounded"}]},
        {"title": "Dominant Variables", "chapter_id": "A1", "blocks": [{"content": "technical duplicate"}]},
    ]
    pkg = _report_package(
        exec_content="EPISTEMIC STATE: SCREENING ADMISSIBLE",
        c2_content="Declared EUI Note  : 120.5",
        a0_content="Claim Permissions     : 2 allowed / 0 conditional / 0 prohibited",
        document_type="Compliance / Investment Screening Brief",
        body_sections_override=body_sections,
        appendix_sections_override=appendix_sections,
    )
    out = Motor036Adapter().run(
        {
            "motor_012": {"asset_field_register": []},
            "motor_014": {"claim_permission_summary": {"allowed_count": 0, "conditional_count": 0, "prohibited_count": 0}},
            "motor_034": {
                "claim_permission_register": [],
                "claim_contract_register": [],
                "report_type_classifier_table": [{"recommended_report_type": "Compliance / Investment Screening Brief"}],
                "report_output_mode_classifier_table": [
                    {
                        "canonical_output_mode": "Compliance / Investment Screening Brief",
                        "selected_for_publication": True,
                        "classification_state": "selected_primary_default",
                    }
                ],
            },
            "motor_016": {"report_package": pkg},
        }
    )

    assert out["can_render_pdf"] is False
    failure_ids = {row["check_id"] for row in out["critical_failures"]}
    assert "appendix_sections_do_not_compete_with_body" in failure_ids


def test_motor_036_blocks_body_integrity_scan_issues():
    pkg = _report_package(
        exec_content="EPISTEMIC STATE: SCREENING ADMISSIBLE",
        c2_content="Declared EUI Note  : 120.5",
        a0_content="Claim Permissions     : 2 allowed / 0 conditional / 0 prohibited",
        document_type="Compliance / Investment Screening Brief",
    )
    pkg["context_integrity_scan"] = {
        "scan_status": "blocked",
        "issue_count": 1,
        "render_eligible": False,
        "issues": [
            {
                "issue_code": "instruction_leakage_reader_takeaway",
                "severity": "error",
                "section_id": "c5",
                "matched_text": "READER TAKEAWAY",
                "message": "Internal prompt instruction leaked into visible report.",
            }
        ],
    }
    out = Motor036Adapter().run(
        {
            "motor_012": {"asset_field_register": []},
            "motor_014": {"claim_permission_summary": {"allowed_count": 0, "conditional_count": 0, "prohibited_count": 0}},
            "motor_034": {
                "claim_permission_register": [],
                "claim_contract_register": [],
                "report_type_classifier_table": [{"recommended_report_type": "Compliance / Investment Screening Brief"}],
                "report_output_mode_classifier_table": [
                    {
                        "canonical_output_mode": "Compliance / Investment Screening Brief",
                        "selected_for_publication": True,
                        "classification_state": "selected_primary_default",
                    }
                ],
            },
            "motor_016": {"report_package": pkg},
        }
    )

    assert out["can_render_pdf"] is False
    failure_ids = {row["check_id"] for row in out["critical_failures"]}
    assert "client_facing_body_integrity_scan_passed" in failure_ids


def test_motor_017_blocks_render_when_motor_036_fails():
    out = Motor017Adapter().run(
        {
            "motor_016": {
                "report_package": _report_package(
                    exec_content="ok",
                    c2_content="ok",
                    a0_content="ok",
                    document_type="Compliance / Investment Screening Brief",
                )
            },
            "motor_036": {
                "can_render_pdf": False,
                "critical_failures": [
                    {"message": "Executive brief still speaks as fully blocked."}
                ],
            },
        }
    )

    assert out["compilation_status"] == "blocked"
    assert out["pdf_path"] == ""
    assert "fully blocked" in out["blocking_reason"]


def test_motor_017_purges_template_chapters_from_job_dir(tmp_path, monkeypatch):
    template_dir = tmp_path / "template"
    output_dir = tmp_path / "output"
    chapters_dir = template_dir / "Chapters"
    (template_dir / "Metadata").mkdir(parents=True, exist_ok=True)
    (template_dir / "Matter").mkdir(parents=True, exist_ok=True)
    (template_dir / "Bibliography").mkdir(parents=True, exist_ok=True)
    (template_dir / "Configurations").mkdir(parents=True, exist_ok=True)
    chapters_dir.mkdir(parents=True, exist_ok=True)
    for name in ("00-Abstract.tex", "01-Introduction.tex", "02-User-Guide.tex", "03-Latex-Tutorial.tex"):
        (chapters_dir / name).write_text("template", encoding="utf-8")
    (chapters_dir / "Appendices").mkdir(parents=True, exist_ok=True)
    (chapters_dir / "Annexes").mkdir(parents=True, exist_ok=True)

    monkeypatch.setattr(motor_017_module, "_TEMPLATE_DIR", template_dir)
    monkeypatch.setattr(motor_017_module, "_OUTPUT_DIR", output_dir)

    def _fake_run(cmd, cwd, capture_output, text, timeout):
        pdf_path = motor_017_module.Path(cwd) / "main.pdf"
        pdf_path.write_bytes(b"%PDF-1.4\n% fake pdf\n")
        return types.SimpleNamespace(returncode=0, stdout="", stderr="")

    monkeypatch.setattr(motor_017_module.subprocess, "run", _fake_run)

    out = Motor017Adapter().run(
        {
            "motor_016": {
                "report_package": _report_package(
                    exec_content="EPISTEMIC STATE: SCREENING ADMISSIBLE — bounded screening only.",
                    c2_content="Gross Floor Area   : 1,678,135 sqft\nYear Built         : 2020",
                    a0_content="Claim Permissions     : 2 allowed / 0 conditional / 1 prohibited",
                    document_type="Compliance / Investment Screening Brief",
                    extra_body_sections=[
                        {"title": "Energy Profile & Normative Constraints", "chapter_id": "C3", "blocks": [{"content": "bounded screening energy profile"}]},
                        {"title": "Blocking Conflicts", "chapter_id": "C4", "blocks": [{"content": "systems and control boundary remain open"}]},
                    ],
                    extra_appendix_sections=[
                        {"title": "Public Source Coverage Table", "chapter_id": "A6", "blocks": [{"content": "bounded source coverage"}]},
                        {"title": "Report Type Classifier Table", "chapter_id": "A7", "blocks": [{"content": "recommended output mode remains screening"}]},
                    ],
                )
            },
            "motor_036": {"can_render_pdf": True, "critical_failures": []},
        }
    )

    assert out["compilation_status"] == "success"
    written_inventory = set(out["written_chapter_inventory"])
    assert {"00-Brief.tex", "A0.tex", "A6.tex", "A7.tex", "C1.tex", "C6.tex", "C12.tex"} <= written_inventory
    written_dir = output_dir / out["render_job_id"] / "Chapters"
    assert not (written_dir / "01-Introduction.tex").exists()
    assert not (written_dir / "02-User-Guide.tex").exists()
    assert not (written_dir / "03-Latex-Tutorial.tex").exists()
    assert not (written_dir / "Appendices").exists()
    assert not (written_dir / "Annexes").exists()
