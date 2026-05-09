from __future__ import annotations

from typing import Any

from .output_taxonomy import canonicalize_output_mode

STRUCTURAL_PRIMARY_OUTPUT_MODES = {
    "Structural Contradiction Brief",
    "System Redesign Hypothesis Brief",
    "Competitive Positioning Brief",
    "TAD Action Priority Brief",
}

STRUCTURAL_ALL_BODY_TITLES = [
    "Executive Structural Brief",
    "What the Client Thinks the Problem Is",
    "What the System Thinks the Problem Might Actually Be",
    "System Abstraction Map",
    "Dominant Variables",
    "Evidence State by Layer",
    "Cross-Layer Contradictions",
    "Scenario Space",
    "Financial Exposure Under Uncertainty",
    "Competitive / Peer Comparison",
    "Conditional Redesign Pathways",
    "Minimum Evidence for Discrimination",
    "TAD — Action Priority",
    "What Not To Do Yet",
    "Claim Permission Matrix",
    "Source Traceability",
    "System Consistency Check",
]

LEGACY_BLOCKED_BODY_TITLES = [
    "Framework Context & Executive Brief",
    "Operational Identity",
    "Inference Case Map",
    "Blocking Conflicts",
    "Validation Architecture",
    "Tension Map",
    "Conditional Opportunities",
    "Energy Profile & Normative Constraints",
    "Inference Case Register",
    "Next Best Questions",
]

DECISION_BLOCKED_BODY_TITLES = [
    "Executive Decision-Admissibility Brief",
    "Asset Context Readiness",
    "Investment Uncertainty Map",
    "Blocking Conflicts",
    "Minimum Evidence Pack",
    "Scenario Space Under Current Uncertainty",
    "TAD — Decision-Admissibility Layer",
    "Regulatory / Normative Screening",
    "Inference Case Register",
    "Next Best Questions",
]

LEGACY_TECHNICAL_BODY_TITLES = [
    "Framework Context & Executive Brief",
    "Energy Profile & Normative Constraints",
    "Blocking Conflicts",
    "Inference Case Map",
    "Operational Identity",
    "Tension Map",
    "Validation Architecture",
    "Conditional Opportunities",
    "Financial Context",
]

COMMON_APPENDIX_PRIORITY_TITLES = [
    "Governance Status",
    "Evidence & Source Traceability",
    "Asset Context Prior and Raw Source Map",
    "Detailed Validation Questions",
    "Issuer Financial Context (Subordinated)",
    "Investment Uncertainty Map",
    "Minimum Evidence Pack",
    "Scenario Space Under Current Uncertainty",
    "Asset Context Readiness",
    "Regulatory / Normative Screening",
    "TAD — Decision-Admissibility Layer",
    "Inference Case Register",
    "Next Best Questions",
    "Public Source Coverage Table",
    "Report Type Classifier Table",
    "Industry Adaptation Table",
    "System Abstraction Map",
    "Dominant Variables",
    "Evidence State by Layer",
    "Cross-Layer Contradictions",
    "Problem Framing",
    "Structural Benchmarking & Competitive Comparison",
    "Conditional Redesign & Structural Financial Exposure",
    "Minimum Evidence for Discrimination",
    "Structural Claim Permissions, Output Modes & Expanded TAD",
]


def _support_chart_rule(
    rule_id: str,
    *,
    section_hint: str,
    promote_to: list[str],
    policy_note: str,
    output_modes: list[str] | None = None,
    asset_families: list[str] | None = None,
    chart_asset_ids: list[str] | None = None,
    chart_categories: list[str] | None = None,
    chart_lanes: list[str] | None = None,
    chart_intents: list[str] | None = None,
) -> dict[str, Any]:
    return {
        "rule_id": rule_id,
        "section_hint": str(section_hint or "").strip(),
        "promote_to": [str(value).strip() for value in list(promote_to or []) if str(value).strip()],
        "policy_note": str(policy_note or "").strip(),
        "output_modes": [str(value).strip() for value in list(output_modes or ["*"]) if str(value).strip()],
        "asset_families": [str(value).strip().lower() for value in list(asset_families or ["*"]) if str(value).strip()],
        "chart_asset_ids": [str(value).strip() for value in list(chart_asset_ids or ["*"]) if str(value).strip()],
        "chart_categories": [str(value).strip() for value in list(chart_categories or ["*"]) if str(value).strip()],
        "chart_lanes": [str(value).strip() for value in list(chart_lanes or ["*"]) if str(value).strip()],
        "chart_intents": [str(value).strip() for value in list(chart_intents or ["*"]) if str(value).strip()],
    }


_SUPPORT_CHART_VISIBILITY_RULES = [
    _support_chart_rule(
        "exploratory_validation_lane_to_questions",
        section_hint="c7_validation_architecture",
        promote_to=["a3_priority_questions", "a16_structural_claims_output_modes_and_tad", "a5_evidence_maturity_matrix"],
        output_modes=["Exploratory Prior Brief"],
        chart_lanes=["validation"],
        policy_note="Exploratory validation-lane charts default to detailed questions before evidence maturity because the reader needs the bounded next move first.",
    ),
    _support_chart_rule(
        "screening_validation_lane_to_evidence_maturity",
        section_hint="c7_validation_architecture",
        promote_to=["a5_evidence_maturity_matrix", "a3_priority_questions", "a16_structural_claims_output_modes_and_tad"],
        output_modes=["Compliance / Investment Screening Brief"],
        chart_lanes=["validation"],
        policy_note="Screening validation-lane charts default to evidence-maturity first because claim ceilings matter before operator ask lists.",
    ),
    _support_chart_rule(
        "screening_contradiction_lane_to_cross_layer",
        section_hint="c3_blocking_conflicts",
        promote_to=["a11_cross_layer_contradictions", "a5_evidence_maturity_matrix"],
        output_modes=["Compliance / Investment Screening Brief"],
        chart_lanes=["contradiction"],
        policy_note="Screening contradiction-lane charts default to cross-layer contradictions before evidence maturity because they explain structural coupling directly.",
    ),
    _support_chart_rule(
        "screening_validation_lane_blockers_to_evidence_maturity",
        section_hint="c3_blocking_conflicts",
        promote_to=["a5_evidence_maturity_matrix", "a11_cross_layer_contradictions"],
        output_modes=["Compliance / Investment Screening Brief"],
        chart_lanes=["validation"],
        policy_note="Screening validation-lane blocker charts default to evidence maturity before contradiction reading because they diagnose blocker classes first.",
    ),
    _support_chart_rule(
        "exploratory_comparison_lane_to_benchmarking",
        section_hint="c10_competitive_peer",
        promote_to=["a13_structural_benchmarking_and_competition", "a16_structural_claims_output_modes_and_tad"],
        output_modes=["Exploratory Prior Brief"],
        chart_lanes=["comparison"],
        policy_note="Exploratory comparison-lane charts default to benchmarking-first appendices.",
    ),
    _support_chart_rule(
        "screening_comparison_lane_to_evidence_then_benchmarking",
        section_hint="c10_competitive_peer",
        promote_to=["a5_evidence_maturity_matrix", "a13_structural_benchmarking_and_competition", "a16_structural_claims_output_modes_and_tad"],
        output_modes=["Compliance / Investment Screening Brief"],
        chart_lanes=["comparison"],
        policy_note="Screening comparison-lane charts default to comparability-evidence before benchmarking interpretation.",
    ),
    _support_chart_rule(
        "exploratory_logistics_identity_to_system_map",
        section_hint="c2_operational_identity",
        promote_to=["a9_system_abstraction_map", "a17_evidence_state_by_layer"],
        output_modes=["Exploratory Prior Brief"],
        asset_families=["logistics_warehouse"],
        policy_note="Exploratory logistics cases prioritize system-abstraction visibility because dock/service-level structure is often the gating identity question.",
    ),
    _support_chart_rule(
        "exploratory_cold_chain_energy_to_system_map",
        section_hint="c5_energy_normative",
        promote_to=["a9_system_abstraction_map", "a2_asset_context_prior", "a8_industry_adaptation"],
        output_modes=["Exploratory Prior Brief"],
        asset_families=["cold_chain"],
        policy_note="Exploratory cold-chain cases prioritize system-abstraction before generic context because refrigeration topology changes the asset family and denominator logic.",
    ),
    _support_chart_rule(
        "screening_utility_heavy_energy_to_industry_adaptation",
        section_hint="c5_energy_normative",
        promote_to=["a8_industry_adaptation", "a6_public_source_coverage", "a2_asset_context_prior"],
        output_modes=["Compliance / Investment Screening Brief"],
        asset_families=["utility_heavy_site"],
        policy_note="Utility-heavy screening cases prioritize industry-adaptation framing before generic asset context because tariff and load-shape interpretation are sector-specific.",
    ),
    _support_chart_rule(
        "screening_utility_heavy_validation_to_claim_gate",
        section_hint="c7_validation_architecture",
        promote_to=["a16_structural_claims_output_modes_and_tad", "a5_evidence_maturity_matrix", "a3_priority_questions"],
        output_modes=["Compliance / Investment Screening Brief"],
        asset_families=["utility_heavy_site"],
        policy_note="Utility-heavy screening cases prioritize claim-gating and expanded TAD before generic question lists because tariff and demand claims can outrun evidence quality quickly.",
    ),
    _support_chart_rule(
        "screening_next_best_search_to_priority_questions",
        section_hint="c7_validation_architecture",
        promote_to=["a3_priority_questions", "a5_evidence_maturity_matrix", "a16_structural_claims_output_modes_and_tad"],
        output_modes=["Compliance / Investment Screening Brief"],
        chart_intents=["search_program"],
        policy_note="Even in screening mode, next-best-search charts stay anchored to the detailed-questions appendix because they are operator prompts, not just maturity gates.",
    ),
    _support_chart_rule(
        "exploratory_operational_identity_to_evidence_state",
        section_hint="c2_operational_identity",
        promote_to=["a17_evidence_state_by_layer", "a9_system_abstraction_map"],
        output_modes=["Exploratory Prior Brief"],
        policy_note="Exploratory outputs prioritize evidence-state and system-boundary visibility for operational-identity support charts.",
    ),
    _support_chart_rule(
        "screening_operational_identity_to_source_coverage",
        section_hint="c2_operational_identity",
        promote_to=["a6_public_source_coverage", "a17_evidence_state_by_layer", "a9_system_abstraction_map"],
        output_modes=["Compliance / Investment Screening Brief"],
        policy_note="Screening outputs prioritize public-source coverage and evidence-state transparency for operational-identity support charts.",
    ),
    _support_chart_rule(
        "exploratory_blocking_conflict_to_contradictions",
        section_hint="c3_blocking_conflicts",
        promote_to=["a11_cross_layer_contradictions", "a5_evidence_maturity_matrix"],
        output_modes=["Exploratory Prior Brief"],
        policy_note="Exploratory outputs show blocking-conflict support charts first in the contradiction appendix, with evidence maturity as secondary support.",
    ),
    _support_chart_rule(
        "screening_blocking_conflict_to_evidence_maturity",
        section_hint="c3_blocking_conflicts",
        promote_to=["a5_evidence_maturity_matrix", "a11_cross_layer_contradictions"],
        output_modes=["Compliance / Investment Screening Brief"],
        policy_note="Screening outputs show blocking-conflict support charts first in evidence-maturity context before deeper contradiction analysis.",
    ),
    _support_chart_rule(
        "screening_gap_taxonomy_to_evidence_maturity",
        section_hint="c3_blocking_conflicts",
        promote_to=["a5_evidence_maturity_matrix", "a11_cross_layer_contradictions"],
        output_modes=["Compliance / Investment Screening Brief"],
        chart_categories=["gap_taxonomy"],
        policy_note="Gap-taxonomy charts stay anchored in evidence-maturity first because they explain what kind of blocker exists before interpreting contradiction structure.",
    ),
    _support_chart_rule(
        "screening_causal_dependency_to_contradictions",
        section_hint="c3_blocking_conflicts",
        promote_to=["a11_cross_layer_contradictions", "a5_evidence_maturity_matrix"],
        output_modes=["Compliance / Investment Screening Brief"],
        chart_intents=["contradiction_dependency_map"],
        policy_note="Causal-dependency charts surface first in cross-layer contradictions because they explain why the blocker is structurally coupled, not just missing evidence.",
    ),
    _support_chart_rule(
        "exploratory_energy_normative_to_context",
        section_hint="c5_energy_normative",
        promote_to=["a2_asset_context_prior", "a8_industry_adaptation", "a9_system_abstraction_map"],
        output_modes=["Exploratory Prior Brief"],
        policy_note="Exploratory outputs keep energy-normative support charts anchored in asset context and abstraction.",
    ),
    _support_chart_rule(
        "screening_energy_normative_to_source_coverage",
        section_hint="c5_energy_normative",
        promote_to=["a6_public_source_coverage", "a8_industry_adaptation", "a2_asset_context_prior"],
        output_modes=["Compliance / Investment Screening Brief"],
        policy_note="Screening outputs expose whether energy and normative readings are source-bounded before contextual interpretation.",
    ),
    _support_chart_rule(
        "exploratory_validation_architecture_to_questions",
        section_hint="c7_validation_architecture",
        promote_to=["a3_priority_questions", "a16_structural_claims_output_modes_and_tad", "a5_evidence_maturity_matrix"],
        output_modes=["Exploratory Prior Brief"],
        policy_note="Exploratory outputs surface validation-architecture support charts first as next-question guidance.",
    ),
    _support_chart_rule(
        "screening_validation_architecture_to_evidence_maturity",
        section_hint="c7_validation_architecture",
        promote_to=["a5_evidence_maturity_matrix", "a3_priority_questions", "a16_structural_claims_output_modes_and_tad"],
        output_modes=["Compliance / Investment Screening Brief"],
        policy_note="Screening outputs surface validation-architecture support charts first as evidence-maturity and source-boundedness checks.",
    ),
    _support_chart_rule(
        "exploratory_competitive_peer_to_benchmarking",
        section_hint="c10_competitive_peer",
        promote_to=["a13_structural_benchmarking_and_competition", "a16_structural_claims_output_modes_and_tad"],
        output_modes=["Exploratory Prior Brief"],
        policy_note="Exploratory outputs surface peer-readiness and comparison support charts in benchmarking-first appendices.",
    ),
    _support_chart_rule(
        "screening_competitive_peer_to_evidence_then_benchmarking",
        section_hint="c10_competitive_peer",
        promote_to=["a5_evidence_maturity_matrix", "a13_structural_benchmarking_and_competition", "a16_structural_claims_output_modes_and_tad"],
        output_modes=["Compliance / Investment Screening Brief"],
        policy_note="Screening outputs surface peer-readiness support charts first as comparability-evidence screens before benchmarking interpretation.",
    ),
    _support_chart_rule(
        "generic_framework_brief_to_context",
        section_hint="c1_framework_brief",
        promote_to=["a2_asset_context_prior", "a6_public_source_coverage"],
        policy_note="Framework-context support charts promote into asset-context or source-coverage appendices when the body stays compressed.",
    ),
    _support_chart_rule(
        "generic_operational_identity_to_evidence_or_system",
        section_hint="c2_operational_identity",
        promote_to=["a17_evidence_state_by_layer", "a9_system_abstraction_map"],
        policy_note="Operational-identity support charts promote into evidence-state or system-abstraction appendices when no direct visible slot exists.",
    ),
    _support_chart_rule(
        "generic_blocking_conflict_to_contradictions",
        section_hint="c3_blocking_conflicts",
        promote_to=["a11_cross_layer_contradictions", "a5_evidence_maturity_matrix"],
        policy_note="Blocking-conflict support charts promote into contradiction and evidence-maturity appendices under compressed delivery.",
    ),
    _support_chart_rule(
        "generic_inference_case_to_evidence_or_tad",
        section_hint="c4_inference_case_map",
        promote_to=["a5_evidence_maturity_matrix", "a16_structural_claims_output_modes_and_tad"],
        policy_note="Inference-case support charts promote into evidence-maturity or expanded-TAD appendices when the body does not expose that lane directly.",
    ),
    _support_chart_rule(
        "generic_energy_normative_to_context",
        section_hint="c5_energy_normative",
        promote_to=["a2_asset_context_prior", "a8_industry_adaptation", "a9_system_abstraction_map"],
        policy_note="Energy and normative support charts promote into contextual and abstraction appendices under thesis-first compression.",
    ),
    _support_chart_rule(
        "generic_tension_map_to_redesign",
        section_hint="c6_tension_map",
        promote_to=["a14_conditional_redesign_and_structural_financial_exposure", "a11_cross_layer_contradictions"],
        policy_note="Tension-map support charts promote into redesign and contradiction appendices when the body keeps only the compressed structural summary.",
    ),
    _support_chart_rule(
        "generic_validation_architecture_to_questions",
        section_hint="c7_validation_architecture",
        promote_to=["a3_priority_questions", "a5_evidence_maturity_matrix", "a16_structural_claims_output_modes_and_tad"],
        policy_note="Validation-architecture support charts promote into detailed validation, evidence-maturity, or expanded-TAD appendices.",
    ),
    _support_chart_rule(
        "generic_conditional_opportunity_to_redesign",
        section_hint="c8_conditional_opportunities",
        promote_to=["a14_conditional_redesign_and_structural_financial_exposure", "a16_structural_claims_output_modes_and_tad"],
        policy_note="Conditional-opportunity support charts promote into redesign and expanded-TAD appendices under compressed outputs.",
    ),
    _support_chart_rule(
        "generic_competitive_peer_to_benchmarking",
        section_hint="c10_competitive_peer",
        promote_to=["a13_structural_benchmarking_and_competition", "a16_structural_claims_output_modes_and_tad"],
        policy_note="Peer-readiness and comparison support charts promote into benchmarking and expanded-TAD appendices when peer comparison is not a standalone visible lane.",
    ),
]

HYBRID_STRUCTURAL_FIRST_BODY_TITLES = [
    "Executive Structural Brief",
    "What the System Thinks the Problem Might Actually Be",
    "Cross-Layer Contradictions",
    "System Abstraction Map",
    "Dominant Variables",
    "Scenario Space",
    "Financial Exposure Under Uncertainty",
    "Competitive / Peer Comparison",
    "Conditional Redesign Pathways",
    "Minimum Evidence for Discrimination",
    "TAD — Action Priority",
    "What Not To Do Yet",
    "Claim Permission Matrix",
    "What the Client Thinks the Problem Is",
    "Evidence State by Layer",
    "Framework Context & Executive Brief",
    "Operational Identity",
    "Source Traceability",
    "System Consistency Check",
    "Energy Profile & Normative Constraints",
    "Blocking Conflicts",
    "Validation Architecture",
    "Conditional Opportunities",
    "Inference Case Map",
    "Tension Map",
    "Financial Context",
]

HYBRID_STRUCTURAL_FIRST_REQUIRED_BODY_TITLES = [
    "Executive Structural Brief",
    "What the System Thinks the Problem Might Actually Be",
    "Cross-Layer Contradictions",
    "System Abstraction Map",
    "Dominant Variables",
    "Financial Exposure Under Uncertainty",
    "Competitive / Peer Comparison",
    "Minimum Evidence for Discrimination",
    "TAD — Action Priority",
]


def _dedupe(values: list[str]) -> list[str]:
    seen: set[str] = set()
    out: list[str] = []
    for value in values:
        text = str(value or "").strip()
        if not text or text in seen:
            continue
        seen.add(text)
        out.append(text)
    return out


def _extend_priority(priority: list[str], canonical_full_order: list[str]) -> list[str]:
    return _dedupe(list(priority) + list(canonical_full_order))


def _support_chart_rule_specificity(
    rule: dict[str, Any],
    *,
    canonical_output_mode: str,
    asset_family: str,
    chart_asset_id: str = "",
    chart_category: str = "",
    chart_lane: str = "",
    chart_intent: str = "",
) -> int:
    score = 0
    output_modes = [str(value).strip() for value in list(rule.get("output_modes", []) or [])]
    asset_families = [str(value).strip().lower() for value in list(rule.get("asset_families", []) or [])]
    chart_asset_ids = [str(value).strip() for value in list(rule.get("chart_asset_ids", []) or [])]
    chart_categories = [str(value).strip() for value in list(rule.get("chart_categories", []) or [])]
    chart_lanes = [str(value).strip() for value in list(rule.get("chart_lanes", []) or [])]
    chart_intents = [str(value).strip() for value in list(rule.get("chart_intents", []) or [])]
    if "*" not in output_modes:
        if canonical_output_mode not in output_modes:
            return -1
        score += 2
    if "*" not in asset_families:
        if asset_family not in asset_families:
            return -1
        score += 1
    if "*" not in chart_categories:
        if chart_category:
            if chart_category not in chart_categories:
                return -1
            score += 1
    if "*" not in chart_lanes:
        if chart_lane:
            if chart_lane not in chart_lanes:
                return -1
            score += 1
    if "*" not in chart_intents:
        if chart_intent:
            if chart_intent not in chart_intents:
                return -1
            score += 1
    if "*" not in chart_asset_ids:
        if chart_asset_id:
            if chart_asset_id not in chart_asset_ids:
                return -1
            score += 1
    return score


def get_support_chart_visibility_policy(output_mode: str, asset_family: str = "") -> dict[str, Any]:
    canonical_output_mode = canonicalize_output_mode(output_mode)
    normalized_asset_family = str(asset_family or "").strip().lower()
    matched_rules: list[dict[str, Any]] = []
    section_map: dict[str, list[str]] = {}
    for priority, rule in enumerate(_SUPPORT_CHART_VISIBILITY_RULES):
        specificity = _support_chart_rule_specificity(
            rule,
            canonical_output_mode=canonical_output_mode,
            asset_family=normalized_asset_family,
        )
        if specificity < 0:
            continue
        row = dict(rule)
        row["specificity"] = specificity
        row["priority"] = priority
        matched_rules.append(row)
    matched_rules.sort(key=lambda row: (-int(row.get("specificity", 0)), int(row.get("priority", 0))))
    for row in matched_rules:
        section_hint = str(row.get("section_hint", "")).strip()
        if not section_hint:
            continue
        chart_asset_ids = [str(value).strip() for value in list(row.get("chart_asset_ids", []) or [])]
        chart_categories = [str(value).strip() for value in list(row.get("chart_categories", []) or [])]
        chart_lanes = [str(value).strip() for value in list(row.get("chart_lanes", []) or [])]
        chart_intents = [str(value).strip() for value in list(row.get("chart_intents", []) or [])]
        if "*" not in chart_intents:
            continue
        if "*" not in chart_lanes:
            continue
        if "*" not in chart_categories:
            continue
        if "*" not in chart_asset_ids:
            continue
        targets = section_map.setdefault(section_hint, [])
        for candidate in list(row.get("promote_to", []) or []):
            candidate_text = str(candidate or "").strip()
            if candidate_text and candidate_text not in targets:
                targets.append(candidate_text)
    return {
        "policy_source": "render_section_contract.support_chart_visibility_rules.v1",
        "canonical_output_mode": canonical_output_mode,
        "asset_family": normalized_asset_family,
        "section_map": section_map,
        "policy_register": matched_rules,
    }


def get_support_chart_lane_visibility_policy(output_mode: str) -> dict[str, Any]:
    canonical_output_mode = canonicalize_output_mode(output_mode)
    lane_limits_by_mode = {
        "Exploratory Prior Brief": {
            "appendix": {
                "validation": 2,
                "comparison": 1,
                "contradiction": 2,
                "finance": 1,
                "context": 1,
                "scenario": 1,
                "decision": 1,
                "regulatory": 1,
            },
            "body": {},
        },
        "Compliance / Investment Screening Brief": {
            "appendix": {
                "validation": 2,
                "comparison": 1,
                "contradiction": 1,
                "finance": 1,
                "context": 2,
                "scenario": 1,
                "decision": 1,
                "regulatory": 1,
            },
            "body": {},
        },
    }
    lane_limits = lane_limits_by_mode.get(canonical_output_mode, {"appendix": {}, "body": {}})
    return {
        "policy_source": "render_section_contract.support_chart_lane_visibility.v1",
        "canonical_output_mode": canonical_output_mode,
        "applies_to": "promoted_to_visible_support_section_only",
        "lane_limits": lane_limits,
    }


def get_support_chart_lane_curation_policy(output_mode: str) -> dict[str, Any]:
    canonical_output_mode = canonicalize_output_mode(output_mode)
    defaults_by_mode = {
        "Exploratory Prior Brief": {
            "lane_intent_priority": {
                "validation": [
                    "search_program",
                    "minimum_evidence_request",
                    "validation_priority",
                    "validation_effort_tradeoff",
                    "evidence_gap_diagnosis",
                    "measurement_escalation_gate",
                    "evidence_maturity_progression",
                ],
                "contradiction": [
                    "cross_layer_contradiction_map",
                    "contradiction_dependency_map",
                    "evidence_gap_diagnosis",
                ],
                "comparison": [
                    "comparability_gate",
                    "peer_readiness_gate",
                ],
            },
        },
        "Compliance / Investment Screening Brief": {
            "lane_intent_priority": {
                "validation": [
                    "evidence_gap_diagnosis",
                    "validation_priority",
                    "validation_effort_tradeoff",
                    "evidence_maturity_progression",
                    "minimum_evidence_request",
                    "measurement_escalation_gate",
                    "search_program",
                ],
                "contradiction": [
                    "contradiction_dependency_map",
                    "cross_layer_contradiction_map",
                    "evidence_gap_diagnosis",
                ],
                "comparison": [
                    "peer_readiness_gate",
                    "comparability_gate",
                ],
            },
        },
    }
    section_overrides_by_mode = {
        "Exploratory Prior Brief": {
            "a3_priority_questions": {
                "validation": [
                    "search_program",
                    "minimum_evidence_request",
                    "validation_priority",
                    "validation_effort_tradeoff",
                ],
            },
            "a11_cross_layer_contradictions": {
                "contradiction": [
                    "cross_layer_contradiction_map",
                    "contradiction_dependency_map",
                ],
            },
        },
        "Compliance / Investment Screening Brief": {
            "a3_priority_questions": {
                "validation": [
                    "search_program",
                    "minimum_evidence_request",
                    "validation_priority",
                ],
            },
            "a5_evidence_maturity_matrix": {
                "validation": [
                    "evidence_gap_diagnosis",
                    "validation_priority",
                    "validation_effort_tradeoff",
                    "evidence_maturity_progression",
                    "minimum_evidence_request",
                ],
            },
            "a11_cross_layer_contradictions": {
                "contradiction": [
                    "contradiction_dependency_map",
                    "cross_layer_contradiction_map",
                ],
            },
            "a13_structural_benchmarking_and_competition": {
                "comparison": [
                    "peer_readiness_gate",
                    "comparability_gate",
                ],
            },
        },
    }
    return {
        "policy_source": "render_section_contract.support_chart_lane_curation.v1",
        "canonical_output_mode": canonical_output_mode,
        "default_lane_intent_priority": defaults_by_mode.get(canonical_output_mode, {}).get("lane_intent_priority", {}),
        "section_lane_intent_priority": section_overrides_by_mode.get(canonical_output_mode, {}),
    }


def _contract(
    canonical_output_mode: str,
    *,
    body_priority_titles: list[str],
    body_section_titles: list[str],
    appendix_priority_titles: list[str] | None = None,
    appendix_section_titles: list[str] | None = None,
    required_body_sections: list[str] | None = None,
    required_appendix_sections: list[str] | None = None,
    structural_primary: bool,
    uses_structural_executive_summary: bool,
    policy_note: str,
) -> dict[str, Any]:
    body_priority_titles = _dedupe(body_priority_titles)
    body_section_titles = _dedupe(body_section_titles)
    appendix_priority_titles = _dedupe(appendix_priority_titles or COMMON_APPENDIX_PRIORITY_TITLES)
    appendix_section_titles = _dedupe(appendix_section_titles or appendix_priority_titles)
    required_body_sections = _dedupe(required_body_sections or body_priority_titles)
    required_appendix_sections = _dedupe(required_appendix_sections or [])
    return {
        "canonical_output_mode": canonical_output_mode,
        "structural_primary": structural_primary,
        "uses_structural_executive_summary": uses_structural_executive_summary,
        "body_priority_titles": body_priority_titles,
        "body_section_titles": body_section_titles,
        "appendix_priority_titles": appendix_priority_titles,
        "appendix_section_titles": appendix_section_titles,
        "required_body_sections": required_body_sections,
        "required_appendix_sections": required_appendix_sections,
        "policy_note": policy_note,
    }


def get_render_section_contract(output_mode: str) -> dict[str, Any]:
    mode = canonicalize_output_mode(output_mode)
    structural_appendix_titles = [
        title
        for title in COMMON_APPENDIX_PRIORITY_TITLES
        if title not in STRUCTURAL_ALL_BODY_TITLES
    ]

    contracts = {
        "Target Classification Brief": _contract(
            "Target Classification Brief",
            body_priority_titles=LEGACY_BLOCKED_BODY_TITLES,
            body_section_titles=LEGACY_BLOCKED_BODY_TITLES,
            required_body_sections=[
                "Framework Context & Executive Brief",
                "Operational Identity",
            ],
            required_appendix_sections=["Governance Status"],
            structural_primary=False,
            uses_structural_executive_summary=False,
            policy_note="Classification-only outputs stay bounded to legacy blocked-style body ordering and do not activate first-class structural sections.",
        ),
        "Decision-Blocked Asset Brief": _contract(
            "Decision-Blocked Asset Brief",
            body_priority_titles=DECISION_BLOCKED_BODY_TITLES,
            body_section_titles=DECISION_BLOCKED_BODY_TITLES,
            required_body_sections=DECISION_BLOCKED_BODY_TITLES,
            required_appendix_sections=["Governance Status"],
            structural_primary=False,
            uses_structural_executive_summary=False,
            policy_note="Decision-blocked outputs preserve the decision-admissibility body order and keep structural framing subordinate to readiness and evidence-gap communication.",
        ),
        "Exploratory Prior Brief": _contract(
            "Exploratory Prior Brief",
            body_priority_titles=HYBRID_STRUCTURAL_FIRST_BODY_TITLES,
            body_section_titles=HYBRID_STRUCTURAL_FIRST_BODY_TITLES,
            required_body_sections=HYBRID_STRUCTURAL_FIRST_REQUIRED_BODY_TITLES,
            required_appendix_sections=["Governance Status"],
            structural_primary=False,
            uses_structural_executive_summary=True,
            policy_note="Exploratory outputs expose the structural question in the main body while keeping legacy technical surfaces available as subordinate context.",
        ),
        "Compliance / Investment Screening Brief": _contract(
            "Compliance / Investment Screening Brief",
            body_priority_titles=HYBRID_STRUCTURAL_FIRST_BODY_TITLES,
            body_section_titles=HYBRID_STRUCTURAL_FIRST_BODY_TITLES,
            required_body_sections=HYBRID_STRUCTURAL_FIRST_REQUIRED_BODY_TITLES,
            required_appendix_sections=["Governance Status", "Public Source Coverage Table", "Report Type Classifier Table"],
            structural_primary=False,
            uses_structural_executive_summary=True,
            policy_note="Screening outputs remain bounded by claim ceilings, but the visible body is structural-first rather than appendix-first.",
        ),
        "Structural Contradiction Brief": _contract(
            "Structural Contradiction Brief",
            body_priority_titles=[
                "Executive Structural Brief",
                "What the Client Thinks the Problem Is",
                "What the System Thinks the Problem Might Actually Be",
                "Cross-Layer Contradictions",
                "Evidence State by Layer",
                "Scenario Space",
                "Financial Exposure Under Uncertainty",
                "TAD — Action Priority",
            ],
            body_section_titles=_extend_priority(
                [
                    "Executive Structural Brief",
                    "What the Client Thinks the Problem Is",
                    "What the System Thinks the Problem Might Actually Be",
                    "Cross-Layer Contradictions",
                    "Evidence State by Layer",
                    "Scenario Space",
                    "Financial Exposure Under Uncertainty",
                    "TAD — Action Priority",
                ],
                STRUCTURAL_ALL_BODY_TITLES,
            ),
            appendix_priority_titles=structural_appendix_titles,
            appendix_section_titles=structural_appendix_titles,
            required_body_sections=[
                "Executive Structural Brief",
                "What the Client Thinks the Problem Is",
                "What the System Thinks the Problem Might Actually Be",
                "Cross-Layer Contradictions",
                "Evidence State by Layer",
                "Scenario Space",
                "Financial Exposure Under Uncertainty",
                "TAD — Action Priority",
            ],
            required_appendix_sections=["Governance Status", "Public Source Coverage Table"],
            structural_primary=True,
            uses_structural_executive_summary=True,
            policy_note="Structural contradiction outputs elevate contradiction, layer evidence, scenario meaning, and action priority to the front of the body.",
        ),
        "System Redesign Hypothesis Brief": _contract(
            "System Redesign Hypothesis Brief",
            body_priority_titles=[
                "Executive Structural Brief",
                "System Abstraction Map",
                "Dominant Variables",
                "What the System Thinks the Problem Might Actually Be",
                "Conditional Redesign Pathways",
                "Minimum Evidence for Discrimination",
                "Financial Exposure Under Uncertainty",
                "What Not To Do Yet",
                "TAD — Action Priority",
            ],
            body_section_titles=_extend_priority(
                [
                    "Executive Structural Brief",
                    "System Abstraction Map",
                    "Dominant Variables",
                    "What the System Thinks the Problem Might Actually Be",
                    "Conditional Redesign Pathways",
                    "Minimum Evidence for Discrimination",
                    "Financial Exposure Under Uncertainty",
                    "What Not To Do Yet",
                    "TAD — Action Priority",
                ],
                STRUCTURAL_ALL_BODY_TITLES,
            ),
            appendix_priority_titles=structural_appendix_titles,
            appendix_section_titles=structural_appendix_titles,
            required_body_sections=[
                "Executive Structural Brief",
                "System Abstraction Map",
                "Dominant Variables",
                "Conditional Redesign Pathways",
                "Minimum Evidence for Discrimination",
                "Financial Exposure Under Uncertainty",
                "What Not To Do Yet",
                "TAD — Action Priority",
            ],
            required_appendix_sections=["Governance Status", "Public Source Coverage Table"],
            structural_primary=True,
            uses_structural_executive_summary=True,
            policy_note="Redesign-hypothesis outputs elevate abstraction, dominant variables, redesign paths, and discrimination evidence to the front of the body.",
        ),
        "Competitive Positioning Brief": _contract(
            "Competitive Positioning Brief",
            body_priority_titles=[
                "Executive Structural Brief",
                "What the System Thinks the Problem Might Actually Be",
                "Competitive / Peer Comparison",
                "Dominant Variables",
                "Financial Exposure Under Uncertainty",
                "TAD — Action Priority",
            ],
            body_section_titles=_extend_priority(
                [
                    "Executive Structural Brief",
                    "What the System Thinks the Problem Might Actually Be",
                    "Competitive / Peer Comparison",
                    "Dominant Variables",
                    "Financial Exposure Under Uncertainty",
                    "TAD — Action Priority",
                ],
                STRUCTURAL_ALL_BODY_TITLES,
            ),
            appendix_priority_titles=structural_appendix_titles,
            appendix_section_titles=structural_appendix_titles,
            required_body_sections=[
                "Executive Structural Brief",
                "Competitive / Peer Comparison",
                "Dominant Variables",
                "Financial Exposure Under Uncertainty",
                "TAD — Action Priority",
            ],
            required_appendix_sections=["Governance Status", "Public Source Coverage Table"],
            structural_primary=True,
            uses_structural_executive_summary=True,
            policy_note="Competitive-positioning outputs elevate peer comparison, structural advantage, and action posture to the front of the body.",
        ),
        "TAD Action Priority Brief": _contract(
            "TAD Action Priority Brief",
            body_priority_titles=[
                "Executive Structural Brief",
                "What the System Thinks the Problem Might Actually Be",
                "Minimum Evidence for Discrimination",
                "What Not To Do Yet",
                "TAD — Action Priority",
                "Scenario Space",
                "Financial Exposure Under Uncertainty",
            ],
            body_section_titles=_extend_priority(
                [
                    "Executive Structural Brief",
                    "What the System Thinks the Problem Might Actually Be",
                    "Minimum Evidence for Discrimination",
                    "What Not To Do Yet",
                    "TAD — Action Priority",
                    "Scenario Space",
                    "Financial Exposure Under Uncertainty",
                ],
                STRUCTURAL_ALL_BODY_TITLES,
            ),
            appendix_priority_titles=structural_appendix_titles,
            appendix_section_titles=structural_appendix_titles,
            required_body_sections=[
                "Executive Structural Brief",
                "Minimum Evidence for Discrimination",
                "What Not To Do Yet",
                "TAD — Action Priority",
                "Scenario Space",
                "Financial Exposure Under Uncertainty",
            ],
            required_appendix_sections=["Governance Status", "Public Source Coverage Table"],
            structural_primary=True,
            uses_structural_executive_summary=True,
            policy_note="TAD-priority outputs elevate discrimination evidence, banned premature actions, and the bounded action register to the front of the body.",
        ),
        "Full Technical Decision Intelligence Report": _contract(
            "Full Technical Decision Intelligence Report",
            body_priority_titles=HYBRID_STRUCTURAL_FIRST_BODY_TITLES,
            body_section_titles=HYBRID_STRUCTURAL_FIRST_BODY_TITLES,
            required_body_sections=HYBRID_STRUCTURAL_FIRST_REQUIRED_BODY_TITLES,
            required_appendix_sections=["Governance Status", "Public Source Coverage Table", "Report Type Classifier Table"],
            structural_primary=False,
            uses_structural_executive_summary=True,
            policy_note="Full technical outputs surface the full structural reading directly in the body and keep legacy technical blocks as subordinate supporting context.",
        ),
    }
    return contracts.get(
        mode,
        _contract(
            mode or "Decision-Blocked Asset Brief",
            body_priority_titles=LEGACY_TECHNICAL_BODY_TITLES,
            body_section_titles=LEGACY_TECHNICAL_BODY_TITLES,
            required_body_sections=["Framework Context & Executive Brief"],
            required_appendix_sections=["Governance Status"],
            structural_primary=False,
            uses_structural_executive_summary=False,
            policy_note="Fallback contract; should not be selected in normal governed runtime.",
        ),
    )


def _order_sections_by_titles(
    sections: list[dict[str, Any]],
    ordered_titles: list[str],
) -> list[dict[str, Any]]:
    title_rank = {title: idx for idx, title in enumerate(_dedupe(ordered_titles))}
    return sorted(
        list(sections or []),
        key=lambda section: (
            title_rank.get(str(section.get("title", "")).strip(), 10_000),
            str(section.get("chapter_id", "")).strip(),
        ),
    )


def resolve_render_section_contract(
    output_mode: str,
    body_sections: list[dict[str, Any]],
    appendix_sections: list[dict[str, Any]],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], dict[str, Any]]:
    contract = dict(get_render_section_contract(output_mode))
    ordered_body = _order_sections_by_titles(body_sections, list(contract.get("body_section_titles", []) or []))
    ordered_appendix = _order_sections_by_titles(appendix_sections, list(contract.get("appendix_section_titles", []) or []))
    resolved = {
        **contract,
        "resolved_body_sections": [
            str(section.get("title", "")).strip()
            for section in ordered_body
            if str(section.get("title", "")).strip()
        ],
        "resolved_appendix_sections": [
            str(section.get("title", "")).strip()
            for section in ordered_appendix
            if str(section.get("title", "")).strip()
        ],
    }
    return ordered_body, ordered_appendix, resolved
