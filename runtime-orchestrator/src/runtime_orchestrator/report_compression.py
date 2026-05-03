from __future__ import annotations

from typing import Any

from .output_taxonomy import canonicalize_output_mode

_CLIENT_FACING_SECTION_BLUEPRINT = [
    ("executive_structural_thesis", "Executive Structural Thesis", ["Executive Structural Brief"]),
    ("reframed_problem", "Reframed Problem", ["What the Client Thinks the Problem Is", "What the System Thinks the Problem Might Actually Be"]),
    ("dominant_structural_contradiction", "Dominant Structural Contradiction", ["Cross-Layer Contradictions"]),
    ("system_abstraction_snapshot", "System Abstraction Snapshot", ["System Abstraction Map"]),
    ("dominant_variables", "Dominant Variables", ["Dominant Variables"]),
    ("scenario_space", "Scenario Space", ["Scenario Space"]),
    ("financial_exposure", "Financial Exposure Under Uncertainty", ["Financial Exposure Under Uncertainty"]),
    ("peer_comparison", "Peer / Competitive Comparison", ["Competitive / Peer Comparison"]),
    ("conditional_redesign", "Conditional Redesign Pathway", ["Conditional Redesign Pathways"]),
    ("minimum_evidence", "Minimum Evidence for Discrimination", ["Minimum Evidence for Discrimination"]),
    ("tad", "TAD — Immediate Action Priority", ["TAD — Action Priority"]),
    ("claim_permissions", "Claim Permissions / What Not To Do", ["What Not To Do Yet"]),
]

_LEGACY_APPENDIX_SECTIONS = [
    "Blocking Conflicts",
    "Validation Architecture",
    "Inference Case Map",
    "Tension Map",
    "Conditional Opportunities",
    "Evidence & Source Traceability",
    "Asset Context Prior and Raw Source Map",
]

_PROMPT_BLOCK_COMPRESSED_MAPPING = [
    ("Executive Strategic Shock", "Executive Structural Thesis", "primary_body_section", ""),
    ("What Looks Like the Problem", "Reframed Problem", "body_embedded_existing_section", ""),
    ("What May Actually Be the Problem", "Reframed Problem", "primary_body_section", ""),
    ("Fair Comparison Check", "Peer / Competitive Comparison", "primary_body_section", ""),
    ("System Abstraction Map", "System Abstraction Snapshot", "primary_body_section", ""),
    ("Universal Process Map", "System Abstraction Snapshot", "body_embedded_existing_section", "Congruence Technical Registers"),
    ("Dominant Variables", "Dominant Variables", "primary_body_section", ""),
    ("Cross-Layer Congruence Map", "Dominant Structural Contradiction", "primary_body_section", ""),
    ("Structural Correlations", "Dominant Variables", "body_embedded_existing_section", "Congruence Technical Registers"),
    ("Hidden Loss Pattern Hypotheses", "Dominant Variables", "body_embedded_existing_section", "Congruence Technical Registers"),
    ("Maintenance Reality", "Conditional Redesign Pathway", "body_embedded_existing_section", "Congruence Technical Registers"),
    ("Measurement / Hardware Minimality Strategy", "Minimum Evidence for Discrimination", "body_embedded_existing_section", "Congruence Technical Registers"),
    ("Power Quality / Reactive Logic", "Minimum Evidence for Discrimination", "body_embedded_existing_section", "Congruence Technical Registers"),
    ("Leakage / Treasure Hunt Logic", "Minimum Evidence for Discrimination", "body_embedded_existing_section", "Congruence Technical Registers"),
    ("Regulatory-Permit-Physics Signals", "Dominant Structural Contradiction", "body_embedded_existing_section", "Congruence Technical Registers"),
    ("Finance-to-Physics Translation", "Financial Exposure Under Uncertainty", "body_embedded_existing_section", "Congruence Technical Registers"),
    ("Strategic Gold Nuggets", "Executive Structural Thesis", "body_embedded_existing_section", ""),
    ("Conditional Redesign Pathways", "Conditional Redesign Pathway", "primary_body_section", ""),
    ("Minimum Evidence to Discriminate", "Minimum Evidence for Discrimination", "primary_body_section", ""),
    ("TAD Strategic Action Priority", "TAD — Immediate Action Priority", "primary_body_section", ""),
    ("What Not To Do Yet", "Claim Permissions / What Not To Do", "primary_body_section", ""),
    ("Claim Permissions", "Claim Permissions / What Not To Do", "body_embedded_existing_section", ""),
    ("Traceability", "Evidence & Source Traceability", "appendix_support_register", "Evidence & Source Traceability"),
]


def _text(value: Any) -> str:
    return str(value or "").strip()


def _dedupe(values: list[str]) -> list[str]:
    seen: set[str] = set()
    out: list[str] = []
    for value in values:
        text = _text(value)
        if not text or text in seen:
            continue
        seen.add(text)
        out.append(text)
    return out


def _supporting_modes(executive_thesis: dict[str, Any]) -> list[str]:
    return _dedupe([_text(value) for value in list(executive_thesis.get("supporting_modes", []) or [])])


def _congruence_visibility_register(executive_thesis: dict[str, Any]) -> list[dict[str, str]]:
    visibility_spec = [
        (
            "dominant_operational_misunderstanding",
            "executive_structural_thesis",
            "Executive Structural Thesis",
            "Thesis sharpening only; do not create a standalone congruence section.",
        ),
        (
            "hidden_system_boundary_error",
            "dominant_structural_contradiction",
            "Dominant Structural Contradiction",
            "Boundary mistakes stay subordinate to the dominant contradiction.",
        ),
        (
            "invalid_comparison_risk",
            "peer_comparison",
            "Peer / Competitive Comparison",
            "Comparison risk is visible only as a guardrail on peer logic.",
        ),
        (
            "dominant_loss_logic",
            "dominant_variables",
            "Dominant Variables",
            "Loss logic surfaces only when it sharpens the variable hierarchy.",
        ),
        (
            "measurement_minimality_take",
            "minimum_evidence",
            "Minimum Evidence for Discrimination",
            "Measurement logic stays in the evidence section, not as a hardware appendix in the body.",
        ),
        (
            "regulatory_physics_take",
            "dominant_structural_contradiction",
            "Dominant Structural Contradiction",
            "Regulatory-physics logic is shown only when it clarifies the contradiction.",
        ),
        (
            "finance_to_physics_take",
            "financial_exposure",
            "Financial Exposure Under Uncertainty",
            "Finance-to-physics logic sharpens exposure without creating a finance appendix in the body.",
        ),
        (
            "maintenance_reality_take",
            "conditional_redesign",
            "Conditional Redesign Pathway",
            "Maintenance reality is visible only if it changes redesign or action sequencing.",
        ),
    ]
    rows: list[dict[str, str]] = []
    for field_name, section_key, section_title, reason in visibility_spec:
        value = _text(executive_thesis.get(field_name))
        if not value:
            continue
        rows.append(
            {
                "field_name": field_name,
                "section_key": section_key,
                "section_title": section_title,
                "visibility_state": "body_embedded_existing_section",
                "reason": reason,
            }
        )
    return rows


def _client_facing_tad(executive_thesis: dict[str, Any]) -> dict[str, Any]:
    actions = list(executive_thesis.get("top_actions", []) or [])[:5]
    return {
        "action_count": len(actions),
        "actions": actions,
        "compression_state": "compressed_client_facing",
    }


def _inadmissible_client_facing_tad() -> dict[str, Any]:
    return {
        "action_count": 0,
        "actions": [],
        "compression_state": "inadmissible_bypass",
    }


def _appendix_map(executive_thesis: dict[str, Any]) -> list[dict[str, str]]:
    appendix_rows = [
        {
            "title": title,
            "reason": "Technical support detail should not compete with the client-facing thesis.",
            "compression_rule": "appendix_only_when_structural_equivalent_exists",
        }
        for title in _LEGACY_APPENDIX_SECTIONS
    ]
    if executive_thesis.get("supporting_modes"):
        appendix_rows.append(
            {
                "title": "Supporting Structural Lenses",
                "reason": "Supporting modes should remain subordinate lenses, not co-equal primaries.",
                "compression_rule": "lens_not_primary_mode",
            }
        )
    if _congruence_visibility_register(executive_thesis):
        appendix_rows.append(
            {
                "title": "Congruence Technical Registers",
                "reason": "Congruence evidence survives as appendix support while only thesis-relevant takes stay embedded in existing body sections.",
                "compression_rule": "congruence_support_not_primary_body",
            }
        )
    return appendix_rows


def _section_demotions_register(executive_thesis: dict[str, Any]) -> list[dict[str, str]]:
    rows = [
        {
            "title": title,
            "destination": "appendix",
            "reason": "A structurally equivalent or more client-facing thesis section already exists in the body.",
            "compression_rule": "appendix_only_when_structural_equivalent_exists",
        }
        for title in _LEGACY_APPENDIX_SECTIONS
    ]
    if executive_thesis.get("supporting_modes"):
        rows.append(
            {
                "title": "Supporting Structural Lenses",
                "destination": "appendix",
                "reason": "Supporting modes remain subordinate lenses and cannot compete with the visible primary mode.",
                "compression_rule": "lens_not_primary_mode",
            }
        )
    if _congruence_visibility_register(executive_thesis):
        rows.append(
            {
                "title": "Congruence Technical Registers",
                "destination": "appendix",
                "reason": "Full congruence substrate detail must not turn back into a parallel body narrative.",
                "compression_rule": "congruence_support_not_primary_body",
            }
        )
    return rows


def _body_to_appendix_justification_map(executive_thesis: dict[str, Any]) -> dict[str, list[str]]:
    mapping = {
        "Executive Structural Thesis": [
            "Blocking Conflicts",
            "Validation Architecture",
        ],
        "Dominant Structural Contradiction": [
            "Tension Map",
            "Blocking Conflicts",
        ],
        "Conditional Redesign Pathway": [
            "Conditional Opportunities",
        ],
        "Claim Permissions / What Not To Do": [
            "Evidence & Source Traceability",
        ],
    }
    if _congruence_visibility_register(executive_thesis):
        mapping["Executive Structural Thesis"].append("Congruence Technical Registers")
        mapping["Minimum Evidence for Discrimination"] = ["Congruence Technical Registers"]
        mapping["Peer / Competitive Comparison"] = ["Congruence Technical Registers"]
        mapping["Financial Exposure Under Uncertainty"] = ["Congruence Technical Registers"]
    return mapping


def _compression_decision_log(
    *,
    executive_thesis: dict[str, Any],
    visible_report_mode: str,
    sections: list[dict[str, Any]],
    appendix_map: list[dict[str, str]],
    congruence_visibility_register: list[dict[str, str]],
) -> list[dict[str, Any]]:
    log = [
        {
            "decision_type": "primary_mode_selection",
            "selected_mode": visible_report_mode,
            "dominant_lens": _text(executive_thesis.get("dominant_lens")),
            "reason": "Client-facing body must be governed by one visible mode and one dominant lens.",
        },
        {
            "decision_type": "body_budget",
            "selected_body_section_count": len(sections),
            "max_primary_sections": len(_CLIENT_FACING_SECTION_BLUEPRINT),
            "reason": "Only thesis-dominant material survives into the main body.",
        },
        {
            "decision_type": "appendix_demotions",
            "demoted_section_count": len(appendix_map),
            "reason": "Technical detail survives, but only as support material outside the main body.",
        },
        {
            "decision_type": "supporting_modes_subordinated",
            "supporting_modes": _supporting_modes(executive_thesis),
            "reason": "Supporting structural lenses remain visible but cannot compete with the primary client-facing report mode.",
        },
    ]
    if congruence_visibility_register:
        log.append(
            {
                "decision_type": "congruence_selective_promotion",
                "visible_congruence_signal_count": len(congruence_visibility_register),
                "visible_congruence_fields": [row["field_name"] for row in congruence_visibility_register],
                "reason": "Only thesis-relevant congruence signals are embedded into existing sections; full congruence registers remain appendix-only.",
            }
        )
    return log


def _prompt_block_mapping_register() -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for prompt_block_title, mapped_section_title, coverage_state, appendix_title in _PROMPT_BLOCK_COMPRESSED_MAPPING:
        reason = {
            "primary_body_section": "This prompt block survives as a first-class client-facing section in the compressed body.",
            "body_embedded_existing_section": "This prompt block is covered inside an existing body section to preserve thesis sovereignty and body compression.",
            "appendix_support_register": "This prompt block remains available only as support material because it must not compete with the main client-facing narrative.",
        }.get(coverage_state, "Covered through compressed report hierarchy.")
        rows.append(
            {
                "prompt_block_title": prompt_block_title,
                "mapped_section_title": mapped_section_title,
                "coverage_state": coverage_state,
                "appendix_title": appendix_title,
                "reason": reason,
            }
        )
    return rows


def _deduplicated_claim_map(
    executive_thesis: dict[str, Any],
    claim_contract_register: list[dict[str, Any]],
    congruence_claim_contract_register: list[dict[str, Any]],
) -> dict[str, list[str]]:
    prohibited_claim_ids = [
        _text(row.get("claim_id"))
        for row in claim_contract_register
        if _text(row.get("permission")).lower() == "prohibited" and _text(row.get("claim_id"))
    ]
    congruence_claim_ids = [_text(row.get("claim_id")) for row in congruence_claim_contract_register if _text(row.get("claim_id"))]
    return {
        "executive_structural_thesis": _dedupe(["public_asset_identity_claim", "financial_exposure_claim", "congruence_gold_nugget_claim"]),
        "conditional_redesign": _dedupe(["redesign_hypothesis_claim", "congruence_action_priority_claim"]),
        "financial_exposure": _dedupe(["financial_exposure_claim", "congruence_finance_physics_claim"]),
        "peer_comparison": _dedupe(["peer_comparison_claim", "congruence_invalid_comparison_claim"]),
        "minimum_evidence": _dedupe(["minimum_evidence_claim", "congruence_measurement_minimality_claim"]),
        "tad": _dedupe(["TAD_action_claim", "congruence_action_priority_claim"]),
        "claim_permissions": _dedupe(prohibited_claim_ids + congruence_claim_ids)[:8],
        "dominant_lens": [_text(executive_thesis.get("dominant_lens"))] if _text(executive_thesis.get("dominant_lens")) else [],
    }


def _is_inadmissible_thesis(executive_thesis: dict[str, Any]) -> bool:
    return _text(executive_thesis.get("thesis_state")) == "inadmissible_thesis"


def build_report_compression(  # noqa: PLR0913
    *,
    executive_thesis: dict[str, Any],
    canonical_problem_frame: dict[str, Any],
    claim_contract_register: list[dict[str, Any]],
    report_output_mode_classifier_table: list[dict[str, Any]],
    congruence_claim_contract_register: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    congruence_claim_contract_register = list(congruence_claim_contract_register or [])
    visible_report_mode = canonicalize_output_mode(
        executive_thesis.get("report_mode")
        or canonical_problem_frame.get("leading_structural_output_mode")
        or ""
    )
    if _is_inadmissible_thesis(executive_thesis):
        reason = _text(executive_thesis.get("inadmissibility_reason"))
        return {
            "visible_report_mode": visible_report_mode,
            "dominant_lens": "",
            "supporting_modes": [],
            "max_primary_sections": 0,
            "compression_state": "inadmissible_bypass",
            "sections": [],
            "body_section_titles": [],
            "appendix_map": [],
            "section_authority_map": {},
            "deduplicated_claim_map": {},
            "client_facing_tad": _inadmissible_client_facing_tad(),
            "congruence_visibility_register": [],
            "section_demotions_register": [],
            "body_to_appendix_justification_map": {},
            "prompt_block_mapping_register": [],
            "compression_decision_log": [
                {
                    "decision_type": "inadmissible_bypass",
                    "selected_mode": visible_report_mode,
                    "thesis_state": "inadmissible_thesis",
                    "reason": reason,
                }
            ],
            "report_output_mode_classifier_count": len(report_output_mode_classifier_table),
        }
    supporting_modes = _supporting_modes(executive_thesis)
    appendix_map = _appendix_map(executive_thesis)
    section_demotions_register = _section_demotions_register(executive_thesis)
    congruence_visibility_register = _congruence_visibility_register(executive_thesis)
    sections = [
        {
            "order": index,
            "section_key": section_key,
            "title": title,
            "render_targets": render_targets,
        }
        for index, (section_key, title, render_targets) in enumerate(_CLIENT_FACING_SECTION_BLUEPRINT, start=1)
    ]
    return {
        "visible_report_mode": visible_report_mode,
        "dominant_lens": _text(executive_thesis.get("dominant_lens")),
        "supporting_modes": supporting_modes,
        "max_primary_sections": len(_CLIENT_FACING_SECTION_BLUEPRINT),
        "compression_state": "thesis_compressed",
        "sections": sections,
        "body_section_titles": [row["title"] for row in sections],
        "appendix_map": appendix_map,
        "section_authority_map": {
            "executive_structural_thesis": "motor_047.executive_thesis / motor_054.strategic_gold_nugget_register",
            "reframed_problem": "motor_047.executive_thesis / motor_041.problem_framing_register",
            "dominant_structural_contradiction": "motor_047.executive_thesis / motor_040.cross_layer_conflict_register / motor_051.cross_layer_congruence_register / motor_053.regulatory_physics_register",
            "system_abstraction_snapshot": "motor_037.system_abstraction",
            "dominant_variables": "motor_038.dominant_variable_register / motor_052.loss_pattern_hypothesis_register",
            "scenario_space": "motor_014.scenario_space",
            "financial_exposure": "motor_045.structural_financial_exposure_register / motor_053.finance_physics_dependency_register",
            "peer_comparison": "motor_043.competitive_comparison_register / motor_051.invalid_comparison_risk_register",
            "conditional_redesign": "motor_044.conditional_redesign_register / motor_052.maintenance_reality_register",
            "minimum_evidence": "motor_046.minimum_evidence_for_discrimination_register / motor_052.measurement_strategy_register / motor_054.congruence_action_priority_register",
            "tad": "motor_033.expanded_structural_tad_action_register / motor_054.congruence_action_priority_register",
            "claim_permissions": "motor_034.claim_contract_register / motor_034.claim_permission_register / motor_054.congruence_claim_contract_register",
        },
        "deduplicated_claim_map": _deduplicated_claim_map(
            executive_thesis,
            claim_contract_register,
            congruence_claim_contract_register,
        ),
        "client_facing_tad": _client_facing_tad(executive_thesis),
        "congruence_visibility_register": congruence_visibility_register,
        "section_demotions_register": section_demotions_register,
        "body_to_appendix_justification_map": _body_to_appendix_justification_map(executive_thesis),
        "prompt_block_mapping_register": _prompt_block_mapping_register(),
        "compression_decision_log": _compression_decision_log(
            executive_thesis=executive_thesis,
            visible_report_mode=visible_report_mode,
            sections=sections,
            appendix_map=appendix_map,
            congruence_visibility_register=congruence_visibility_register,
        ),
        "report_output_mode_classifier_count": len(report_output_mode_classifier_table),
    }
