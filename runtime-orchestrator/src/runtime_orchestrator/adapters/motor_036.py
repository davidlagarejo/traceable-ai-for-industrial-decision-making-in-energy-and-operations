"""Adapter for motor_036 — System Consistency Validator.

Validates that structurally authoritative outputs remain coherent across
motors before rendering proceeds.
"""
from __future__ import annotations

import re
from typing import Any

from ..output_taxonomy import canonicalize_output_mode
from ..structural_intelligence import CANONICAL_EVIDENCE_LAYERS
from .base import BaseMotorAdapter

_CANONICAL_OUTPUT_MODES = {
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

_THESIS_TOKEN_STOPWORDS = {
    "the",
    "and",
    "with",
    "that",
    "this",
    "from",
    "into",
    "what",
    "when",
    "where",
    "while",
    "under",
    "over",
    "before",
    "after",
    "between",
    "than",
    "will",
    "would",
    "should",
    "could",
    "can",
    "may",
    "might",
    "need",
    "needs",
    "must",
    "still",
    "very",
    "more",
    "most",
    "only",
    "real",
    "current",
    "problem",
    "question",
}


def _find_section_content(report_package: dict[str, Any], title: str) -> str:
    approved_views = dict(report_package.get("approved_views", {}) or {})
    report_view = approved_views.get(report_package.get("primary_view_key", "report_view")) or approved_views.get("report_view", {})
    for section in list(report_view.get("body_sections", []) or []) + list(report_view.get("appendix_sections", []) or []):
        if str(section.get("title", "")).strip() != title:
            continue
        blocks = list(section.get("blocks", []) or [])
        if not blocks:
            return ""
        return str(blocks[0].get("content", "") or "")
    return ""


def _find_section(report_package: dict[str, Any], title: str) -> dict[str, Any]:
    approved_views = dict(report_package.get("approved_views", {}) or {})
    report_view = approved_views.get(report_package.get("primary_view_key", "report_view")) or approved_views.get("report_view", {})
    for section in list(report_view.get("body_sections", []) or []) + list(report_view.get("appendix_sections", []) or []):
        if str(section.get("title", "")).strip() == title:
            return dict(section)
    return {}


def _find_first_section(report_package: dict[str, Any], titles: list[str]) -> dict[str, Any]:
    for title in titles:
        section = _find_section(report_package, title)
        if section:
            return section
    return {}


def _find_first_section_content(report_package: dict[str, Any], titles: list[str]) -> str:
    for title in titles:
        content = _find_section_content(report_package, title)
        if content:
            return content
    return ""


def _matrix_counts(claim_permission_register: list[dict[str, Any]]) -> dict[str, int]:
    counts = {"allowed": 0, "conditional": 0, "prohibited": 0, "deferred": 0}
    for row in claim_permission_register:
        state = str(row.get("current_permission", "")).strip().lower()
        if state in counts:
            counts[state] += 1
    return counts


def _summary_counts(claim_permission_summary: dict[str, Any]) -> dict[str, int]:
    return {
        "allowed": int(claim_permission_summary.get("allowed_count", claim_permission_summary.get("allowed", 0)) or 0),
        "conditional": int(claim_permission_summary.get("conditional_count", claim_permission_summary.get("conditional", 0)) or 0),
        "prohibited": int(claim_permission_summary.get("prohibited_count", claim_permission_summary.get("prohibited", 0)) or 0),
        "deferred": int(claim_permission_summary.get("deferred_count", claim_permission_summary.get("deferred", 0)) or 0),
    }


def _observed_asset_field(asset_field_register: list[dict[str, Any]], field_name: str) -> bool:
    target = str(field_name).strip().lower()
    for row in asset_field_register:
        if str(row.get("field", "")).strip().lower() != target:
            continue
        if str(row.get("status", "")).strip() != "OBSERVED":
            continue
        if str(row.get("scope", "")).strip() != "ASSET_LEVEL":
            continue
        return True
    return False


def _visible_field_has_value(content: str, label: str) -> bool:
    pattern = re.compile(rf"{re.escape(label)}\s*:\s*(.*?)($|\n)")
    match = pattern.search(str(content or ""))
    if not match:
        return False
    value = str(match.group(1) or "").strip()
    if not value:
        return False
    return not value.startswith("NOT OBSERVED")


def _expected_chapter_files(report_package: dict[str, Any]) -> list[str]:
    approved_views = dict(report_package.get("approved_views", {}) or {})
    report_view = approved_views.get(report_package.get("primary_view_key", "report_view")) or approved_views.get("report_view", {})
    body_sections = list(report_view.get("body_sections", []) or [])
    appendix_sections = list(report_view.get("appendix_sections", []) or [])
    return [
        "00-Brief.tex",
        *[f"{str(sec.get('chapter_id', 'CX')).strip()}.tex" for sec in body_sections],
        *[f"{str(sec.get('chapter_id', 'AX')).strip()}.tex" for sec in appendix_sections],
    ]


def _section_titles(report_package: dict[str, Any]) -> set[str]:
    approved_views = dict(report_package.get("approved_views", {}) or {})
    report_view = approved_views.get(report_package.get("primary_view_key", "report_view")) or approved_views.get("report_view", {})
    return {
        str(section.get("title", "")).strip()
        for section in list(report_view.get("body_sections", []) or []) + list(report_view.get("appendix_sections", []) or [])
        if str(section.get("title", "")).strip()
    }


def _visible_excerpt(section: dict[str, Any]) -> str:
    blocks = list(section.get("blocks", []) or [])
    content = " ".join(str(block.get("content", "") or "") for block in blocks if isinstance(block, dict)).strip()
    if not content:
        return ""
    for line in content.splitlines():
        text = str(line).strip()
        if not text:
            continue
        if len(set(text)) == 1:
            continue
        return text[:220]
    return ""


def _section_visible_text(section: dict[str, Any]) -> str:
    blocks = list(section.get("blocks", []) or [])
    return " ".join(
        str(block.get("content", "") or "").strip()
        for block in blocks
        if isinstance(block, dict) and str(block.get("content", "") or "").strip()
    ).strip()


def _target_definition_from_inputs(m12: dict[str, Any], inputs: dict[str, Any]) -> dict[str, Any]:
    facility_prior = dict(m12.get("facility_prior", {}) or {})
    candidate = facility_prior.get("target_definition")
    if isinstance(candidate, dict) and candidate:
        return candidate
    candidate = inputs.get("motor_007", {}).get("target_definition_contract")
    if isinstance(candidate, dict) and candidate:
        return candidate
    candidate = inputs.get("__runtime__", {}).get("target_definition")
    if isinstance(candidate, dict) and candidate:
        return candidate
    return {}


def _dataset_keys(m12: dict[str, Any], inputs: dict[str, Any]) -> set[str]:
    keys: set[str] = set()
    for row in list(m12.get("dataset_coverage_register", []) or []):
        key = str(row.get("dataset_key", "")).strip().lower()
        status = str(row.get("status", "")).strip().lower()
        if key and status in {"accepted", "screened", "observed"}:
            keys.add(key)
    for row in list(inputs.get("motor_028", {}).get("source_register", []) or []):
        if not bool(row.get("accepted", False)):
            continue
        source_type = str(row.get("source_type", row.get("title", ""))).strip().lower()
        source_family = str(row.get("source_family", "")).strip().lower()
        if source_type:
            keys.add(source_type)
        if source_family:
            keys.add(source_family)
    for row in list((inputs.get("motor_016", {}) or {}).get("report_package", {}).get("source_family_coverage_table", []) or []):
        if not bool(row.get("found", True)):
            continue
        key = str(row.get("source_name", row.get("source_family", ""))).strip().lower()
        if key:
            keys.add(key)
    return keys


def _activated_source_keys(
    source_register: list[dict[str, Any]],
    search_attempt_ledger: list[dict[str, Any]],
) -> set[str]:
    keys: set[str] = set()
    for row in list(source_register or []):
        for value in (
            row.get("source_family"),
            row.get("source_type"),
            row.get("title"),
        ):
            normalized = str(value or "").strip().lower()
            if normalized:
                keys.add(normalized)
    for row in list(search_attempt_ledger or []):
        for value in (
            row.get("source_family"),
            row.get("query_family"),
            row.get("source_type"),
        ):
            normalized = str(value or "").strip().lower()
            if normalized:
                keys.add(normalized)
    return keys


def _source_row_matches_activation(row: dict[str, Any], activated_source_keys: set[str]) -> bool:
    row_keys = {
        str(row.get("source_family", "")).strip().lower(),
        str(row.get("source_name", "")).strip().lower(),
    }
    row_keys = {key for key in row_keys if key}
    if row_keys.intersection(activated_source_keys):
        return True
    for row_key in row_keys:
        for active_key in activated_source_keys:
            if not row_key or not active_key:
                continue
            if active_key in row_key or row_key in active_key:
                return True
    return False


def _contains_any(text: str, tokens: list[str]) -> bool:
    lowered = str(text or "").strip().lower()
    return any(token in lowered for token in tokens)


def _semantic_tokens(value: Any) -> set[str]:
    return {
        token
        for token in re.findall(r"[a-z0-9]+", str(value or "").strip().lower())
        if len(token) >= 3 and token not in _THESIS_TOKEN_STOPWORDS
    }


def _semantic_overlap(left: Any, right: Any) -> bool:
    left_tokens = _semantic_tokens(left)
    right_tokens = _semantic_tokens(right)
    if not left_tokens or not right_tokens:
        return False
    return bool(left_tokens.intersection(right_tokens))


def _target_thesis_text(anchor_type: str, executive_thesis: dict[str, Any]) -> str:
    anchor = str(anchor_type or "").strip()
    if anchor == "dominant_contradiction":
        return str(executive_thesis.get("dominant_contradiction", "") or "").strip()
    if anchor == "reframed_problem":
        return str(executive_thesis.get("reframed_problem", "") or "").strip()
    if anchor == "minimum_discriminating_evidence":
        values = [
            str(value).strip()
            for value in list(executive_thesis.get("minimum_discriminating_evidence", []) or [])
            if str(value).strip()
        ]
        return " ".join(values)
    return ""


def _section_references_dominant_thesis(section: dict[str, Any], executive_thesis: dict[str, Any]) -> bool:
    anchor_type = str(section.get("thesis_anchor_type", "")).strip()
    anchor_text = str(section.get("thesis_anchor_text", "")).strip()
    if anchor_type not in {"dominant_contradiction", "reframed_problem", "minimum_discriminating_evidence"}:
        return False
    if not anchor_text:
        return False
    target_text = _target_thesis_text(anchor_type, executive_thesis)
    if not target_text:
        return False
    visible_text = _section_visible_text(section)
    return _semantic_overlap(anchor_text, target_text) or _semantic_overlap(visible_text, target_text)


def _append_check(
    checks: list[dict[str, Any]],
    failures: list[dict[str, Any]],
    *,
    check_id: str,
    passed: bool,
    severity: str,
    message: str,
    location: str,
) -> None:
    checks.append(
        {
            "check_id": check_id,
            "passed": passed,
            "severity": severity,
            "message": message,
            "location": location,
        }
    )
    if not passed and severity == "critical":
        failures.append(
            {
                "check_id": check_id,
                "message": message,
                "location": location,
            }
        )


class Motor036Adapter(BaseMotorAdapter):
    @property
    def motor_id(self) -> str:
        return "motor_036"

    @property
    def input_motor_ids(self) -> list[str]:
        return [
            "motor_012",
            "motor_014",
            "motor_016",
            "motor_028",
            "motor_033",
            "motor_034",
            "motor_037",
            "motor_043",
            "motor_044",
            "motor_045",
            "motor_046",
            "motor_049",
            "motor_051",
            "motor_052",
            "motor_053",
            "motor_054",
        ]

    def _run_impl(self, inputs: dict[str, Any]) -> dict[str, Any]:
        m12 = inputs.get("motor_012", {}) if isinstance(inputs.get("motor_012", {}), dict) else {}
        m14 = inputs.get("motor_014", {}) if isinstance(inputs.get("motor_014", {}), dict) else {}
        m16 = inputs.get("motor_016", {}) if isinstance(inputs.get("motor_016", {}), dict) else {}
        m33 = inputs.get("motor_033", {}) if isinstance(inputs.get("motor_033", {}), dict) else {}
        m34 = inputs.get("motor_034", {}) if isinstance(inputs.get("motor_034", {}), dict) else {}
        m37 = inputs.get("motor_037", {}) if isinstance(inputs.get("motor_037", {}), dict) else {}
        m49 = inputs.get("motor_049", {}) if isinstance(inputs.get("motor_049", {}), dict) else {}
        m51 = inputs.get("motor_051", {}) if isinstance(inputs.get("motor_051", {}), dict) else {}
        m52 = inputs.get("motor_052", {}) if isinstance(inputs.get("motor_052", {}), dict) else {}
        m53 = inputs.get("motor_053", {}) if isinstance(inputs.get("motor_053", {}), dict) else {}
        m54 = inputs.get("motor_054", {}) if isinstance(inputs.get("motor_054", {}), dict) else {}

        report_package = dict(m16.get("report_package", {}) or {})
        report_assets = list(report_package.get("assets", []) or [])
        asset_field_register = list(m12.get("asset_field_register", []) or [])
        declared_input_downgrade_register = list(
            m12.get("declared_input_downgrade_register", m49.get("declared_input_downgrade_register", [])) or []
        )
        context_integrity_scan = dict(report_package.get("context_integrity_scan", {}) or {})
        cross_case_contamination_scan = dict(report_package.get("cross_case_contamination_scan", {}) or {})
        chart_case_match_register = list(report_package.get("chart_case_match_register", []) or [])
        source_family_coverage_table = list(report_package.get("source_family_coverage_table", []) or [])
        empty_section_policy_register = list(report_package.get("empty_section_policy_register", []) or [])
        section_population_status_register = list(report_package.get("section_population_status_register", []) or [])
        section_explanation_fallback_register = list(report_package.get("section_explanation_fallback_register", []) or [])
        claim_permission_register = list(
            m14.get("claim_permission_register", m34.get("claim_permission_register", [])) or []
        )
        claim_permission_summary = dict(m14.get("claim_permission_summary", {}) or {})
        scenario_evidence_link_register = list(m14.get("scenario_evidence_link_register", []) or [])
        decision_front_actions = list(m33.get("decision_front_actions", []) or [])
        report_type_classifier_table = list(m34.get("report_type_classifier_table", []) or [])
        report_output_mode_classifier_table = list(m34.get("report_output_mode_classifier_table", []) or [])
        local_evidence_binding_register = list(m49.get("local_evidence_binding_register", []) or [])
        asset_family_research_profile = dict(m49.get("asset_family_research_profile", {}) or {})
        entity_resolution_register = list(m49.get("entity_resolution_register", []) or [])
        entity_conflict_register = list(m49.get("entity_conflict_register", []) or [])
        asset_boundary_resolution_register = list(m49.get("asset_boundary_resolution_register", []) or [])
        invalid_problem_frame_register = list(m51.get("invalid_problem_frame_register", []) or [])
        invalid_comparison_risk_register = list(m51.get("invalid_comparison_risk_register", []) or [])
        loss_pattern_hypothesis_register = list(m52.get("loss_pattern_hypothesis_register", []) or [])
        maintenance_reality_register = list(m52.get("maintenance_reality_register", []) or [])
        measurement_strategy_register = list(m52.get("measurement_strategy_register", []) or [])
        hardware_minimality_register = list(m52.get("hardware_minimality_register", []) or [])
        regulatory_physics_register = list(m53.get("regulatory_physics_register", []) or [])
        finance_physics_dependency_register = list(m53.get("finance_physics_dependency_register", []) or [])
        strategic_gold_nugget_register = list(m54.get("strategic_gold_nugget_register", []) or [])
        congruence_action_priority_register = list(m54.get("congruence_action_priority_register", []) or [])
        congruence_claim_contract_register = list(m54.get("congruence_claim_contract_register", []) or [])
        congruence_claim_ids = {
            str(row.get("claim_id", "")).strip()
            for row in congruence_claim_contract_register
            if str(row.get("claim_id", "")).strip()
        }
        structural_output_mode_classifier_table = list(m34.get("structural_output_mode_classifier_table", []) or [])
        structural_output_mode_summary = dict(m34.get("structural_output_mode_summary", {}) or {})
        structural_primary_promotion_gate = dict(m34.get("structural_primary_promotion_gate", {}) or {})
        structural_claim_permission_register = list(m34.get("structural_claim_permission_register", []) or [])
        claim_contract_register = list(m34.get("claim_contract_register", report_package.get("claim_contract_register", [])) or [])
        section_claim_trace_register = list(report_package.get("section_claim_trace_register", []) or [])
        competitive_comparison_register = list(inputs.get("motor_043", {}).get("competitive_comparison_register", []) or [])
        conditional_redesign_register = list(inputs.get("motor_044", {}).get("conditional_redesign_register", []) or [])
        structural_financial_exposure_register = list(inputs.get("motor_045", {}).get("structural_financial_exposure_register", []) or [])
        evidence_state_by_layer_register = list(
            inputs.get("motor_045", {}).get(
                "evidence_state_by_layer_register",
                (report_package.get("structural_intelligence_registers", {}) or {}).get("evidence_state_by_layer_register", []),
            )
            or []
        )
        minimum_evidence_for_discrimination_register = list(inputs.get("motor_046", {}).get("minimum_evidence_for_discrimination_register", []) or [])
        expanded_structural_tad_action_register = list(m33.get("expanded_structural_tad_action_register", []) or [])
        canonical_asset_context_summary = dict(
            m14.get("canonical_asset_context_summary", m34.get("canonical_asset_context_summary", {})) or {}
        )
        target_definition = _target_definition_from_inputs(m12, inputs)
        target_type = str(target_definition.get("target_type", "")).strip().lower()
        jurisdiction_scope = [str(item).strip().upper() for item in list(target_definition.get("jurisdiction_scope", []) or []) if str(item).strip()]
        dataset_keys = _dataset_keys(m12, inputs)
        system_abstraction = dict(m37.get("system_abstraction", {}) or {})
        source_register = list(inputs.get("motor_028", {}).get("source_register", []) or [])
        search_attempt_ledger = list(inputs.get("motor_028", {}).get("search_attempt_ledger", []) or [])
        section_titles = _section_titles(report_package)

        executive_content = _find_first_section_content(
            report_package,
            ["Framework Context & Executive Brief", "Executive Structural Thesis", "Executive Structural Brief"],
        )
        cross_layer_conflict_content = _find_section_content(report_package, "Cross-Layer Contradictions")
        operational_identity_content = _find_section_content(report_package, "Operational Identity")
        governance_content = _find_section_content(report_package, "Governance Status")
        scenario_section = _find_first_section(report_package, ["Scenario Space Under Current Uncertainty", "Scenario Space"])
        tad_section = _find_first_section(report_package, ["TAD — Decision-Admissibility Layer", "TAD — Action Priority"])
        structural_executive_summary = dict(report_package.get("structural_executive_summary", {}) or {})
        executive_thesis = dict(report_package.get("executive_thesis", {}) or {})
        main_report_outline = dict(report_package.get("main_report_outline", {}) or {})
        appendix_map = list(report_package.get("appendix_map", []) or [])
        client_facing_tad = dict(report_package.get("client_facing_tad", {}) or {})
        client_facing_body_titles = [
            str(title).strip()
            for title in list(report_package.get("client_facing_body_titles", []) or [])
            if str(title).strip()
        ]
        visible_type = str(
            report_package.get("case_metadata", {}).get("document_visible_type")
            or report_package.get("document_type", "")
        ).strip()
        case_fingerprint = str(report_package.get("case_metadata", {}).get("case_fingerprint", "") or "").strip()
        visible_type_canonical = canonicalize_output_mode(visible_type)
        planned_chapter_inventory = dict(report_package.get("planned_chapter_inventory", {}) or {})
        render_section_contract = dict(report_package.get("render_section_contract", {}) or {})
        approved_views = dict(report_package.get("approved_views", {}) or {})
        report_view = approved_views.get(report_package.get("primary_view_key", "report_view")) or approved_views.get("report_view", {})
        body_sections = list(report_view.get("body_sections", []) or [])
        appendix_sections = list(report_view.get("appendix_sections", []) or [])
        body_titles = [
            str(section.get("title", "")).strip()
            for section in body_sections
            if str(section.get("title", "")).strip()
        ]
        body_section_ids: set[str] = set()
        for section in body_sections:
            section_id = str(section.get("section_id", "")).strip()
            chapter_id = str(section.get("chapter_id", "")).strip()
            if section_id:
                body_section_ids.add(section_id)
            if chapter_id:
                body_section_ids.add(chapter_id)
                body_section_ids.add(chapter_id.lower())
        appendix_titles = [
            str(section.get("title", "")).strip()
            for section in appendix_sections
            if str(section.get("title", "")).strip()
        ]
        outline_sections = list(main_report_outline.get("sections", []) or [])
        outline_titles = [
            str(row.get("title", "")).strip()
            for row in outline_sections
            if str(row.get("title", "")).strip()
        ]
        outline_render_targets = [
            str(title).strip()
            for row in outline_sections
            for title in list(row.get("render_targets", []) or [])
            if str(title).strip()
        ]
        expected_body_titles = client_facing_body_titles or outline_titles

        checks: list[dict[str, Any]] = []
        failures: list[dict[str, Any]] = []

        required_thesis_fields = (
            ("declared_problem", "reframed_problem", "report_mode", "thesis_state", "inadmissibility_reason")
            if str(executive_thesis.get("thesis_state", "")).strip() == "inadmissible_thesis"
            else ("declared_problem", "reframed_problem", "dominant_contradiction", "minimum_discriminating_evidence", "report_mode")
        )
        inadmissible_thesis = str(executive_thesis.get("thesis_state", "")).strip() == "inadmissible_thesis"
        missing_thesis_fields = [
            field_name
            for field_name in required_thesis_fields
            if (
                field_name not in executive_thesis
                or (
                    isinstance(executive_thesis.get(field_name), list)
                    and not list(executive_thesis.get(field_name) or [])
                )
                or (
                    not isinstance(executive_thesis.get(field_name), list)
                    and not str(executive_thesis.get(field_name) or "").strip()
                )
            )
        ]
        _append_check(
            checks,
            failures,
            check_id="executive_thesis_exists",
            passed=not missing_thesis_fields,
            severity="critical",
            message=f"Executive thesis is missing required dominant fields: {missing_thesis_fields}.",
            location="motor_047.executive_thesis / motor_016.report_package.executive_thesis",
        )
        _append_check(
            checks,
            failures,
            check_id="executive_thesis_correctly_inadmissible",
            passed=(
                not inadmissible_thesis
                or (
                    not str(executive_thesis.get("dominant_contradiction", "")).strip()
                    and not str(executive_thesis.get("dominant_lens", "")).strip()
                    and not list(executive_thesis.get("minimum_discriminating_evidence", []) or [])
                    and str(executive_thesis.get("inadmissibility_reason", "")).strip()
                )
            ),
            severity="critical",
            message="Inadmissible thesis state must suppress structural contradiction, lens, and evidence-pack claims while exposing an explicit inadmissibility reason.",
            location="motor_047.executive_thesis",
        )

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
        interpretive_required = visible_type in thesis_driven_types and not inadmissible_thesis
        required_interpretive_fields = (
            "hidden_assumption_at_risk",
            "why_current_question_is_premature",
            "what_reality_feature_changes_the_decision",
            "capital_logic_if_assumption_holds",
            "capital_logic_if_assumption_breaks",
            "surprising_but_evidenced_takeaway",
            "dominant_lens",
            "interpretive_signal_register",
        )
        missing_interpretive_fields: list[str] = []
        if interpretive_required:
            for field_name in required_interpretive_fields:
                value = executive_thesis.get(field_name)
                if field_name == "interpretive_signal_register":
                    if not isinstance(value, list) or not value:
                        missing_interpretive_fields.append(field_name)
                elif not str(value or "").strip():
                    missing_interpretive_fields.append(field_name)
        _append_check(
            checks,
            failures,
            check_id="executive_thesis_interpretive_fields_complete",
            passed=(not interpretive_required or not missing_interpretive_fields),
            severity="critical",
            message=(
                "Executive thesis is missing interpretive-strength fields required for client-facing hierarchy. "
                f"missing={missing_interpretive_fields}"
            ),
            location="motor_047.executive_thesis / motor_016.report_package.executive_thesis",
        )

        congruence_bridge_required = (
            not inadmissible_thesis
            and bool(
                invalid_problem_frame_register
                or invalid_comparison_risk_register
                or measurement_strategy_register
                or loss_pattern_hypothesis_register
                or regulatory_physics_register
                or finance_physics_dependency_register
                or strategic_gold_nugget_register
                or congruence_action_priority_register
            )
        )
        required_congruence_fields = (
            "dominant_operational_misunderstanding",
            "hidden_system_boundary_error",
            "invalid_comparison_risk",
            "dominant_loss_logic",
            "measurement_minimality_take",
            "regulatory_physics_take",
            "finance_to_physics_take",
            "maintenance_reality_take",
        )
        missing_congruence_fields = [
            field_name
            for field_name in required_congruence_fields
            if not str(executive_thesis.get(field_name, "") or "").strip()
        ]
        _append_check(
            checks,
            failures,
            check_id="executive_thesis_congruence_bridge_complete",
            passed=(not congruence_bridge_required or not missing_congruence_fields),
            severity="critical",
            message=(
                "Executive thesis is missing congruence-bridge fields even though congruence intelligence is active. "
                f"missing={missing_congruence_fields}"
            ),
            location="motor_047.executive_thesis / motor_054.* / motor_016.report_package.executive_thesis",
        )

        selection_basis = dict(executive_thesis.get("dominant_contradiction_selection_basis", {}) or {})
        ranked_conflicts = list(executive_thesis.get("thesis_ranked_conflict_register", []) or [])
        dominant_lens = str(executive_thesis.get("dominant_lens", "") or "").strip()
        selection_basis_present = (
            not interpretive_required
            or (
                selection_basis
                and ranked_conflicts
                and str(ranked_conflicts[0].get("conflict", "") or "").strip()
                == str(executive_thesis.get("dominant_contradiction", "") or "").strip()
                and (
                    dominant_lens == str(executive_thesis.get("dominant_contradiction", "") or "").strip()
                    or _semantic_overlap(dominant_lens, executive_thesis.get("dominant_contradiction", ""))
                )
            )
        )
        _append_check(
            checks,
            failures,
            check_id="dominant_thesis_selection_basis_present",
            passed=(inadmissible_thesis or selection_basis_present),
            severity="critical",
            message=(
                "Dominant thesis selection basis is missing, inconsistent, or detached from the chosen contradiction. "
                f"selection_basis_keys={sorted(selection_basis.keys())}; "
                f"ranked_conflicts={len(ranked_conflicts)}; dominant_lens={dominant_lens!r}"
            ),
            location="motor_047.executive_thesis",
        )

        outline_mode = str(main_report_outline.get("visible_report_mode", "")).strip()
        outline_mode_canonical = canonicalize_output_mode(outline_mode)
        outline_section_limit = int(main_report_outline.get("max_primary_sections", 0) or 0)
        compression_state = str(main_report_outline.get("compression_state", "")).strip()
        missing_outline_fields = []
        if not outline_mode:
            missing_outline_fields.append("visible_report_mode")
        if not outline_titles and compression_state != "inadmissible_bypass":
            missing_outline_fields.append("sections")
        if outline_section_limit <= 0 and compression_state != "inadmissible_bypass":
            missing_outline_fields.append("max_primary_sections")
        _append_check(
            checks,
            failures,
            check_id="main_report_outline_exists",
            passed=not missing_outline_fields,
            severity="critical",
            message=f"Main report outline is missing required fields: {missing_outline_fields}.",
            location="motor_048.main_report_outline / motor_016.report_package.main_report_outline",
        )

        _append_check(
            checks,
            failures,
            check_id="main_report_outline_matches_visible_mode",
            passed=(not outline_mode or outline_mode_canonical == visible_type_canonical),
            severity="critical",
            message=f"Main report outline visible mode {outline_mode!r} does not match visible report type {visible_type!r}.",
            location="motor_048.main_report_outline.visible_report_mode / motor_016.report_package.case_metadata.document_visible_type",
        )
        thesis_report_mode = canonicalize_output_mode(str(executive_thesis.get("report_mode", "") or "").strip())
        _append_check(
            checks,
            failures,
            check_id="report_mode_consistency_match",
            passed=(
                (not outline_mode or outline_mode_canonical == visible_type_canonical)
                and (not thesis_report_mode or thesis_report_mode == visible_type_canonical)
            ),
            severity="critical",
            message=(
                "Visible report mode, compressed outline mode, and executive thesis report mode are inconsistent. "
                f"visible={visible_type!r}; outline={outline_mode!r}; thesis={executive_thesis.get('report_mode', '')!r}"
            ),
            location="motor_047.executive_thesis.report_mode / motor_048.main_report_outline.visible_report_mode / motor_016.report_package.case_metadata.document_visible_type",
        )
        _append_check(
            checks,
            failures,
            check_id="inadmissible_thesis_bypass_consistent",
            passed=(
                not inadmissible_thesis
                or (
                    compression_state == "inadmissible_bypass"
                    and not outline_titles
                    and outline_section_limit == 0
                    and not client_facing_body_titles
                    and int(client_facing_tad.get("action_count", 0) or 0) == 0
                )
            ),
            severity="critical",
            message="Inadmissible thesis must activate compression bypass, zero primary body sections, and zero client-facing TAD actions.",
            location="motor_048.main_report_outline / motor_048.client_facing_tad / motor_016.report_package",
        )

        _append_check(
            checks,
            failures,
            check_id="client_facing_tad_limited",
            passed=int(client_facing_tad.get("action_count", 0) or 0) <= 5,
            severity="critical",
            message=f"Client-facing TAD exceeds five actions: {int(client_facing_tad.get('action_count', 0) or 0)}.",
            location="motor_048.client_facing_tad / motor_016.report_package.client_facing_tad",
        )

        tad_actions = list(client_facing_tad.get("actions", []) or [])
        invalid_tad_actions = [
            idx
            for idx, row in enumerate(tad_actions)
            if not str(row.get("action", "")).strip()
            or not str(row.get("maps_to", "")).strip()
        ]
        _append_check(
            checks,
            failures,
            check_id="client_facing_tad_actions_mapped",
            passed=not invalid_tad_actions,
            severity="critical",
            message=f"Client-facing TAD actions are missing action text or thesis mapping at rows {invalid_tad_actions}.",
            location="motor_048.client_facing_tad.actions",
        )

        outline_order_matches = (
            not expected_body_titles
            or body_titles == expected_body_titles
        )
        _append_check(
            checks,
            failures,
            check_id="body_sections_follow_main_outline_priority",
            passed=outline_order_matches,
            severity="critical",
            message=(
                "Body sections do not honor the compressed main outline priority. "
                f"expected_body={expected_body_titles}; actual_body={body_titles}"
            ),
            location="motor_016.report_package.approved_views.report_view.body_sections / main_report_outline",
        )

        duplicate_outline_titles = sorted({title for title in outline_titles if outline_titles.count(title) > 1})
        _append_check(
            checks,
            failures,
            check_id="main_report_outline_section_count_bounded",
            passed=not duplicate_outline_titles and (outline_section_limit <= 0 or len(outline_titles) <= outline_section_limit),
            severity="critical",
            message=(
                "Main report outline exceeds its section cap or duplicates titles. "
                f"count={len(outline_titles)}; cap={outline_section_limit}; duplicates={duplicate_outline_titles}"
            ),
            location="motor_048.main_report_outline.sections",
        )

        _append_check(
            checks,
            failures,
            check_id="client_facing_body_section_count_bounded",
            passed=(outline_section_limit <= 0 or len(body_titles) <= outline_section_limit),
            severity="critical",
            message=(
                "Client-facing body exceeds the allowed section cap. "
                f"body_count={len(body_titles)}; cap={outline_section_limit}; body_titles={body_titles}"
            ),
            location="motor_016.report_package.approved_views.report_view.body_sections",
        )

        legacy_duplicate_titles = {
            "Blocking Conflicts",
            "Validation Architecture",
            "Inference Case Map",
            "Tension Map",
            "Conditional Opportunities",
            "Financial Context",
            "Energy Profile & Normative Constraints",
        }
        legacy_titles_still_in_body = sorted(legacy_duplicate_titles & set(body_titles))
        _append_check(
            checks,
            failures,
            check_id="legacy_duplicate_sections_demoted_from_body",
            passed=(compression_state == "inadmissible_bypass" or not legacy_titles_still_in_body),
            severity="critical",
            message=f"Legacy technical sections still compete in the client-facing body: {legacy_titles_still_in_body}.",
            location="motor_016.report_package.approved_views.report_view.body_sections",
        )

        forbidden_body_titles = {
            "Claim Permission Matrix",
            "Source Traceability",
            "Public Source Coverage Table",
            "Evidence & Source Traceability",
        }
        forbidden_titles_in_body = sorted(forbidden_body_titles & set(body_titles))
        _append_check(
            checks,
            failures,
            check_id="full_technical_registers_demoted_from_body",
            passed=not forbidden_titles_in_body,
            severity="critical",
            message=f"Full technical registers still appear in the client-facing body: {forbidden_titles_in_body}.",
            location="motor_016.report_package.approved_views.report_view.body_sections",
        )

        body_integrity_issues = [
            issue
            for issue in list(context_integrity_scan.get("issues", []) or [])
            if str(issue.get("section_id", "")).strip() in body_section_ids
        ]
        _append_check(
            checks,
            failures,
            check_id="client_facing_body_integrity_scan_passed",
            passed=not body_integrity_issues,
            severity="critical",
            message=f"Body contains integrity-scan issues: {[issue.get('issue_code') for issue in body_integrity_issues][:8]}.",
            location="motor_016.report_package.context_integrity_scan / report_view.body_sections",
        )

        raw_leakage_patterns = (
            r"\bclaim_id\b",
            r"\bclaim_family\b",
            r"\bsource_id\b",
            r"\bsection_id\b",
            r"\bblock_id\b",
            r"\bmotor_\d+\b",
            r"::",
            r"\bnot_observed::",
            r"\blegacy_maturity_lane\b",
            r"\bdataset_key\b",
            r"\brender_targets\b",
            r"\bllm_[a-z_]+\b",
        )
        body_raw_leakage_hits: list[str] = []
        for section in body_sections:
            visible_text = _section_visible_text(section)
            if not visible_text:
                continue
            if any(re.search(pattern, visible_text, flags=re.IGNORECASE) for pattern in raw_leakage_patterns):
                body_raw_leakage_hits.append(str(section.get("title", "")).strip())
        _append_check(
            checks,
            failures,
            check_id="client_facing_body_free_of_raw_technical_leakage",
            passed=not body_raw_leakage_hits,
            severity="critical",
            message=f"Client-facing body leaks raw technical identifiers in sections: {body_raw_leakage_hits}.",
            location="motor_016.report_package.approved_views.report_view.body_sections",
        )

        orphan_sections = [
            str(section.get("title", "")).strip()
            for section in body_sections
            if not _section_references_dominant_thesis(section, executive_thesis)
        ]
        _append_check(
            checks,
            failures,
            check_id="body_sections_anchor_to_dominant_thesis",
            passed=(inadmissible_thesis or not orphan_sections),
            severity="critical",
            message=f"Client-facing body contains sections that are not anchored to the dominant thesis: {orphan_sections}.",
            location="motor_016.report_package.approved_views.report_view.body_sections",
        )

        appendix_title_collisions = sorted(set(body_titles).intersection(set(appendix_titles)))
        _append_check(
            checks,
            failures,
            check_id="appendix_sections_do_not_compete_with_body",
            passed=not appendix_title_collisions,
            severity="critical",
            message=(
                "Appendix titles collide with client-facing body titles and compete with the primary narrative. "
                f"collisions={appendix_title_collisions}"
            ),
            location="motor_016.report_package.approved_views.report_view.appendix_sections",
        )

        duplicate_excerpts = sorted(
            {
                excerpt
                for excerpt in {
                    _visible_excerpt(section)
                    for section in body_sections
                }
                if excerpt
                and [
                    _visible_excerpt(section)
                    for section in body_sections
                ].count(excerpt) > 2
            }
        )
        _append_check(
            checks,
            failures,
            check_id="body_redundancy_bounded",
            passed=not duplicate_excerpts,
            severity="critical",
            message=f"Client-facing body repeats the same visible excerpt across too many sections: {duplicate_excerpts[:4]}.",
            location="motor_016.report_package.approved_views.report_view.body_sections",
        )

        matrix_counts = _matrix_counts(claim_permission_register)
        summary_counts = _summary_counts(claim_permission_summary)
        _append_check(
            checks,
            failures,
            check_id="claim_summary_vs_matrix",
            passed=summary_counts == matrix_counts,
            severity="critical",
            message=f"Claim summary {summary_counts} diverges from matrix {matrix_counts}.",
            location="motor_014.claim_permission_summary vs motor_034.claim_permission_register",
        )
        _append_check(
            checks,
            failures,
            check_id="claim_summary_count_match",
            passed=summary_counts == matrix_counts,
            severity="critical",
            message=f"Claim summary counts {summary_counts} do not match the governing permission matrix {matrix_counts}.",
            location="motor_014.claim_permission_summary vs motor_034.claim_permission_register",
        )

        expected_claim_ids = {
            str(row.get("claim_name", "")).strip()
            for row in claim_permission_register
            if str(row.get("claim_name", "")).strip()
        } | {
            str(row.get("claim", "")).strip()
            for row in structural_claim_permission_register
            if str(row.get("claim", "")).strip()
        }
        contract_map = {
            str(row.get("claim_id", "")).strip(): row
            for row in claim_contract_register
            if str(row.get("claim_id", "")).strip()
        }
        required_contract_fields = (
            "statement",
            "evidence_state",
            "supporting_sources",
            "assumptions",
            "falsification_condition",
            "minimum_evidence_required",
            "allowed_use",
            "prohibited_use",
        )
        incomplete_contracts: list[str] = []
        for claim_id in sorted(expected_claim_ids & set(contract_map)):
            row = contract_map[claim_id]
            for field_name in required_contract_fields:
                value = row.get(field_name)
                if isinstance(value, list):
                    if not value:
                        incomplete_contracts.append(f"{claim_id}:{field_name}")
                elif not str(value or "").strip():
                    incomplete_contracts.append(f"{claim_id}:{field_name}")
        missing_contracts = sorted(expected_claim_ids - set(contract_map))
        _append_check(
            checks,
            failures,
            check_id="claim_contract_register_complete",
            passed=not missing_contracts and not incomplete_contracts,
            severity="critical",
            message=(
                "Claim contract register is missing required rows or fields. "
                f"missing={missing_contracts}; incomplete={incomplete_contracts[:8]}"
            ),
            location="motor_034.claim_contract_register",
        )
        required_statement_trace_fields = (
            "section_id",
            "section_title",
            "section_surface",
            "block_id",
            "claim_id",
            "visible_statement_excerpt",
            "statement",
            "evidence_state",
            "supporting_sources",
            "assumptions",
            "falsification_condition",
            "minimum_evidence_required",
            "allowed_use",
            "prohibited_use",
            "permission",
        )
        incomplete_statement_traces: list[str] = []
        for idx, row in enumerate(section_claim_trace_register):
            for field_name in required_statement_trace_fields:
                value = row.get(field_name)
                if isinstance(value, list):
                    if field_name in {"supporting_sources", "minimum_evidence_required"} and value == []:
                        incomplete_statement_traces.append(f"{idx}:{field_name}")
                    if field_name in {"allowed_use", "prohibited_use", "assumptions"} and value is None:
                        incomplete_statement_traces.append(f"{idx}:{field_name}")
                elif not str(value or "").strip():
                    incomplete_statement_traces.append(f"{idx}:{field_name}")
        missing_statement_trace_contracts = sorted(
            {
                str(row.get("claim_id", "")).strip()
                for row in section_claim_trace_register
                if str(row.get("claim_id", "")).strip() and str(row.get("claim_id", "")).strip() not in contract_map
            }
        )
        _append_check(
            checks,
            failures,
            check_id="visible_claim_statement_traces_complete",
            passed=not missing_statement_trace_contracts and not incomplete_statement_traces,
            severity="critical",
            message=(
                "Visible claim statement traces are missing contract backing or required fields. "
                f"missing_claims={missing_statement_trace_contracts}; incomplete={incomplete_statement_traces[:8]}"
            ),
            location="motor_016.report_package.section_claim_trace_register",
        )
        required_claim_surface_titles = {
            "Framework Context & Executive Brief",
            "Executive Structural Brief",
            "Operational Identity",
            "System Abstraction Map",
            "Dominant Variables",
            "Cross-Layer Contradictions",
            "Scenario Space",
            "Scenario Space Under Current Uncertainty",
            "Financial Exposure Under Uncertainty",
            "Financial Context",
            "Competitive / Peer Comparison",
            "Structural Benchmarking & Competitive Comparison",
            "Conditional Redesign Pathways",
            "Conditional Redesign & Structural Financial Exposure",
            "Minimum Evidence for Discrimination",
            "TAD — Action Priority",
            "TAD — Decision-Admissibility Layer",
            "What Not To Do Yet",
            "Claim Permission Matrix",
            "Structural Claim Permissions, Output Modes & Expanded TAD",
            "Source Traceability",
            "Public Source Coverage Table",
        }
        trace_titles = {
            str(row.get("section_title", "")).strip()
            for row in section_claim_trace_register
            if str(row.get("section_title", "")).strip()
        }
        missing_claim_surface_traces = sorted(
            title for title in section_titles
            if title in required_claim_surface_titles and title not in trace_titles
        )
        _append_check(
            checks,
            failures,
            check_id="claim_surface_sections_have_statement_traces",
            passed=(compression_state == "inadmissible_bypass" or not missing_claim_surface_traces),
            severity="critical",
            message=f"Visible claim-bearing sections are missing statement-level claim traces: {missing_claim_surface_traces}.",
            location="motor_016.report_package.approved_views.report_view / section_claim_trace_register",
        )

        structural_lane_active = any(
            [
                structural_claim_permission_register,
                competitive_comparison_register,
                conditional_redesign_register,
                structural_financial_exposure_register,
                expanded_structural_tad_action_register,
                report_package.get("structural_intelligence_summary"),
            ]
        )
        if structural_lane_active:
            required_layer_fields = (
                "evidence_state",
                "dominant_open_questions",
                "observed_support",
                "structural_risk_if_wrong",
            )
            layer_map = {
                str(row.get("layer", "")).strip(): row
                for row in evidence_state_by_layer_register
                if str(row.get("layer", "")).strip()
            }
            missing_layers = [layer for layer in CANONICAL_EVIDENCE_LAYERS if layer not in layer_map]
            incomplete_layers: list[str] = []
            for layer in sorted(set(CANONICAL_EVIDENCE_LAYERS) & set(layer_map)):
                row = layer_map[layer]
                for field_name in required_layer_fields:
                    value = row.get(field_name)
                    if field_name == "observed_support":
                        if not isinstance(value, list):
                            incomplete_layers.append(f"{layer}:{field_name}")
                    elif isinstance(value, list):
                        if not value:
                            incomplete_layers.append(f"{layer}:{field_name}")
                    elif not str(value or "").strip():
                        incomplete_layers.append(f"{layer}:{field_name}")
            _append_check(
                checks,
                failures,
                check_id="evidence_state_by_layer_register_complete",
                passed=not missing_layers and not incomplete_layers,
                severity="critical",
                message=(
                    "Evidence-state-by-layer register is missing required layers or fields. "
                    f"missing={missing_layers}; incomplete={incomplete_layers[:8]}"
                ),
                location="motor_045.evidence_state_by_layer_register",
            )

        if target_type == "manufacturing_facility" and structural_lane_active:
            regulatory_text = " ".join(
                [
                    str((system_abstraction.get("regulatory_exposure", {}) or {}).get("statement", "")).strip(),
                    str(m12.get("compliance_applicability_case", {})).strip(),
                    " ".join(sorted(dataset_keys)),
                ]
            ).lower()
            building_only_tokens = ["ashrae", "ll84", "ll97", "pluto", "dob", "dof", "local law", "building emissions"]
            industrial_tokens = ["tceq", "epa", "echo", "air permit", "emissions", "voc", "wastewater", "permit", "industrial"]
            collapsed_to_building_only = _contains_any(regulatory_text, building_only_tokens) and not _contains_any(regulatory_text, industrial_tokens)
            _append_check(
                checks,
                failures,
                check_id="manufacturing_regulatory_frame_not_building_only",
                passed=not collapsed_to_building_only,
                severity="critical",
                message="Manufacturing case still collapses to a building-only regulatory frame instead of an industrial permit/emissions frame.",
                location="motor_037.system_abstraction.regulatory_exposure / motor_012.dataset_coverage_register",
            )

        is_nyc_commercial = target_type == "commercial_building" and any(code.startswith("US-NY-NYC") for code in jurisdiction_scope)
        if is_nyc_commercial and structural_lane_active:
            required_dataset_groups = {
                "pluto": {"nyc_pluto", "nyc_pluto_property"},
                "ll84": {"nyc_ll84_benchmarking", "nyc_ll84_energy_benchmarking"},
                "ll97": {"nyc_ll97_emissions", "nyc_ll97_covered_buildings_list", "nyc_ll97_public_filing_candidate"},
                "dob": {"nyc_dob_permits", "permit_record"},
                "dof": {"nyc_dof_property_record", "property_record"},
            }
            missing_groups = [
                label
                for label, aliases in required_dataset_groups.items()
                if not (aliases & dataset_keys)
            ]
            _append_check(
                checks,
                failures,
                check_id="nyc_commercial_required_public_datasets_active",
                passed=not missing_groups,
                severity="critical",
                message=f"NYC commercial structural case is missing required public-domain packs: {missing_groups}.",
                location="motor_012.dataset_coverage_register / motor_028.source_register",
            )

        required_render_contract_fields = (
            "canonical_output_mode",
            "structural_primary",
            "uses_structural_executive_summary",
            "body_section_titles",
            "appendix_section_titles",
            "required_body_sections",
            "required_appendix_sections",
            "resolved_body_sections",
            "resolved_appendix_sections",
            "policy_note",
        )
        missing_render_contract_fields = [
            field_name
            for field_name in required_render_contract_fields
            if field_name not in render_section_contract
        ]
        render_contract_complete = (
            not missing_render_contract_fields
            and canonicalize_output_mode(render_section_contract.get("canonical_output_mode", "")) == visible_type_canonical
        )
        _append_check(
            checks,
            failures,
            check_id="output_mode_render_contract_complete",
            passed=render_contract_complete,
            severity="critical",
            message=(
                "Render section contract is missing required fields or diverges from the visible output mode. "
                f"missing={missing_render_contract_fields}; visible_type={visible_type!r}; "
                f"contract_mode={str(render_section_contract.get('canonical_output_mode', '')).strip()!r}"
            ),
            location="motor_016.report_package.render_section_contract",
        )

        required_body_sections = [
            str(title).strip()
            for title in list(render_section_contract.get("required_body_sections", []) or [])
            if str(title).strip()
        ]
        required_appendix_sections = [
            str(title).strip()
            for title in list(render_section_contract.get("required_appendix_sections", []) or [])
            if str(title).strip()
        ]
        missing_required_body_sections = [
            title for title in required_body_sections if title not in body_titles
        ]
        misplaced_required_body_sections = [
            title for title in required_body_sections if title in appendix_titles
        ]
        missing_required_appendix_sections = [
            title for title in required_appendix_sections if title not in appendix_titles
        ]
        _append_check(
            checks,
            failures,
            check_id="structural_primary_body_contract_satisfied",
            passed=(
                compression_state == "inadmissible_bypass"
                or
                render_contract_complete
                and not missing_required_body_sections
                and not misplaced_required_body_sections
                and not missing_required_appendix_sections
            ),
            severity="critical",
            message=(
                "Render contract required sections are missing or misplaced. "
                f"missing_body={missing_required_body_sections}; misplaced_body={misplaced_required_body_sections}; "
                f"missing_appendix={missing_required_appendix_sections}"
            ),
            location="motor_016.report_package.approved_views.report_view",
        )

        resolved_body_sections = [
            str(title).strip()
            for title in list(render_section_contract.get("resolved_body_sections", []) or [])
            if str(title).strip()
        ]
        resolved_appendix_sections = [
            str(title).strip()
            for title in list(render_section_contract.get("resolved_appendix_sections", []) or [])
            if str(title).strip()
        ]
        planned_body_titles = [
            str(title).strip()
            for title in list(planned_chapter_inventory.get("body_section_titles", []) or [])
            if str(title).strip()
        ]
        planned_appendix_titles = [
            str(title).strip()
            for title in list(planned_chapter_inventory.get("appendix_section_titles", []) or [])
            if str(title).strip()
        ]
        planned_inventory_output_mode = str(
            planned_chapter_inventory.get("canonical_output_mode", "")
        ).strip()
        _append_check(
            checks,
            failures,
            check_id="selected_output_mode_sections_match_render_inventory",
            passed=(
                render_contract_complete
                and body_titles == resolved_body_sections
                and appendix_titles == resolved_appendix_sections
                and planned_body_titles == body_titles
                and planned_appendix_titles == appendix_titles
                and canonicalize_output_mode(planned_inventory_output_mode) == visible_type_canonical
            ),
            severity="critical",
            message=(
                "Render inventory diverges from the selected output-mode section contract. "
                f"body_titles={body_titles}; resolved_body={resolved_body_sections}; "
                f"appendix_titles={appendix_titles}; resolved_appendix={resolved_appendix_sections}; "
                f"planned_body={planned_body_titles}; planned_appendix={planned_appendix_titles}; "
                f"planned_mode={planned_inventory_output_mode!r}; visible_type={visible_type!r}"
            ),
            location="motor_016.report_package.planned_chapter_inventory / render_section_contract",
        )

        structural_primary_types = {
            "Structural Contradiction Brief",
            "System Redesign Hypothesis Brief",
            "Competitive Positioning Brief",
            "TAD Action Priority Brief",
        }
        if visible_type in structural_primary_types:
            missing_sections = sorted(set(required_body_sections) - section_titles)
            structural_executive_present = (
                ("Executive Structural Brief" in body_titles or "Executive Structural Thesis" in body_titles)
                and (
                    not bool(render_section_contract.get("uses_structural_executive_summary", False))
                    or "STRUCTURAL READ" in executive_content
                    or "DOMINANT CONTRADICTION" in executive_content.upper()
                )
            )
            _append_check(
                checks,
                failures,
                check_id="structural_report_sections_present",
                passed=render_contract_complete and not missing_sections and structural_executive_present,
                severity="critical",
                message=(
                    "Structural report is missing required structural sections or executive structural read. "
                    f"missing={missing_sections}; structural_executive_present={structural_executive_present}"
                ),
                location="motor_016.report_package.approved_views.report_view",
            )
        dominant_structural_conflict = str(structural_executive_summary.get("dominant_structural_conflict", "")).strip()
        missing_visible_structural_conflict = bool(dominant_structural_conflict) and (
            not cross_layer_conflict_content
            or "No cross-layer contradiction" in cross_layer_conflict_content
            or "No cross-layer contradictions were produced." in cross_layer_conflict_content
        )
        _append_check(
            checks,
            failures,
            check_id="dominant_structural_conflict_visible",
            passed=not missing_visible_structural_conflict,
            severity="critical",
            message=(
                "A dominant structural conflict is active in the executive structural summary, "
                "but the visible Cross-Layer Contradictions section is empty or suppressed."
            ),
            location="motor_016.report_package.approved_views.report_view[Cross-Layer Contradictions]",
        )

        rendered_claim_requirements: set[str] = set()
        rendered_claim_requirements.update(
            str(row.get("claim_id", "")).strip()
            for row in section_claim_trace_register
            if str(row.get("claim_id", "")).strip()
        )
        if visible_type == "Compliance / Investment Screening Brief":
            rendered_claim_requirements.add("compliance_screening_claim")
        if _visible_field_has_value(operational_identity_content, "Declared EUI Note"):
            rendered_claim_requirements.add("numeric_eui_claim")
        if (
            "Structural Benchmarking & Competitive Comparison" in section_titles
            or "Competitive / Peer Comparison" in section_titles
        ) and competitive_comparison_register:
            rendered_claim_requirements.add("peer_comparison_claim")
        if (
            "Conditional Redesign & Structural Financial Exposure" in section_titles
            or "Conditional Redesign Pathways" in section_titles
        ) and conditional_redesign_register:
            rendered_claim_requirements.add("redesign_hypothesis_claim")
        if (
            "Conditional Redesign & Structural Financial Exposure" in section_titles
            or "Financial Exposure Under Uncertainty" in section_titles
        ) and structural_financial_exposure_register:
            rendered_claim_requirements.add("financial_exposure_claim")
        if (
            "TAD — Decision-Admissibility Layer" in section_titles
            or "TAD — Action Priority" in section_titles
        ) and (expanded_structural_tad_action_register or tad_section):
            rendered_claim_requirements.add("TAD_action_claim")
        missing_rendered_claim_contracts = sorted(
            claim_id for claim_id in rendered_claim_requirements if claim_id not in contract_map
        )
        _append_check(
            checks,
            failures,
            check_id="rendered_claims_have_claim_contracts",
            passed=not missing_rendered_claim_contracts,
            severity="critical",
            message=f"Rendered claim surfaces are missing matching claim contracts: {missing_rendered_claim_contracts}.",
            location="motor_016.report_package / motor_034.claim_contract_register",
        )

        if matrix_counts["allowed"] or matrix_counts["conditional"] or matrix_counts["prohibited"]:
            governance_counts_text = (
                f"{matrix_counts['allowed']} allowed / {matrix_counts['conditional']} conditional / {matrix_counts['prohibited']} prohibited"
            )
            _append_check(
                checks,
                failures,
                check_id="governance_summary_vs_matrix",
                passed=governance_counts_text in governance_content,
                severity="critical",
                message="Governance appendix does not reflect the claim-permission matrix counts.",
                location="motor_016.report_package.approved_views.report_view.appendix_sections[Governance Status]",
            )

        if visible_type == "Compliance / Investment Screening Brief":
            blocked_language = (
                "EPISTEMIC STATE: ASSET CONTEXT INSUFFICIENT" in executive_content
                or "EPISTEMIC STATE: ASSET TECHNICAL INSUFFICIENCY" in executive_content
                or "remains blocked until at least these clusters are clarified" in executive_content
            )
            _append_check(
                checks,
                failures,
                check_id="report_type_vs_executive_brief",
                passed=not blocked_language,
                severity="critical",
                message="Executive brief still speaks as fully blocked even though the published report type is screening.",
                location="motor_016.report_package.approved_views.report_view.body_sections[Framework Context & Executive Brief]",
            )

        positive_tad_posture = any(
            str(row.get("current_status", "")).strip().upper() in {"ACT NOW", "VALIDATE FIRST"}
            or str(row.get("recommended_posture", "")).strip().lower() in {"act_now", "validation_first"}
            for row in decision_front_actions
        )
        if positive_tad_posture:
            blocked_language = (
                "EPISTEMIC STATE: ASSET CONTEXT INSUFFICIENT" in executive_content
                or "EPISTEMIC STATE: ASSET TECHNICAL INSUFFICIENCY" in executive_content
                or "remains blocked until at least these clusters are clarified" in executive_content
            )
            _append_check(
                checks,
                failures,
                check_id="tad_vs_executive_brief",
                passed=not blocked_language,
                severity="critical",
                message="TAD contains ACT NOW or VALIDATE FIRST fronts, but the executive brief still presents the case as fully blocked.",
                location="motor_033.decision_front_actions vs motor_016.report_package.approved_views.report_view.body_sections[Framework Context & Executive Brief]",
            )
            if tad_section:
                tad_content = _find_first_section_content(
                    report_package,
                    ["TAD — Decision-Admissibility Layer", "TAD — Action Priority"],
                )
                _append_check(
                    checks,
                    failures,
                    check_id="tad_section_vs_decision_front_actions",
                    passed=("ACT NOW" in tad_content) or ("VALIDATE FIRST" in tad_content),
                    severity="critical",
                    message="Visible TAD section does not reflect the positive decision-front posture emitted by motor_033.",
                    location="motor_016.report_package.approved_views.report_view.appendix_sections[TAD — Decision-Admissibility Layer]",
                )

        if operational_identity_content and _observed_asset_field(asset_field_register, "GFA"):
            _append_check(
                checks,
                failures,
                check_id="asset_field_gfa_vs_operational_identity",
                passed="Gross Floor Area   : NOT OBSERVED" not in operational_identity_content,
                severity="critical",
                message="Operational Identity still marks GFA as not observed despite asset-level public support.",
                location="motor_016.report_package.approved_views.report_view.body_sections[Operational Identity]",
            )
        if operational_identity_content and _observed_asset_field(asset_field_register, "year_built"):
            _append_check(
                checks,
                failures,
                check_id="asset_field_year_built_vs_operational_identity",
                passed="Year Built         : NOT OBSERVED" not in operational_identity_content,
                severity="critical",
                message="Operational Identity still marks year built as not observed despite asset-level public support.",
                location="motor_016.report_package.approved_views.report_view.body_sections[Operational Identity]",
            )
        if operational_identity_content and _observed_asset_field(asset_field_register, "floor_count"):
            _append_check(
                checks,
                failures,
                check_id="asset_field_floor_count_vs_operational_identity",
                passed=_visible_field_has_value(operational_identity_content, "Total Floors"),
                severity="critical",
                message="Operational Identity still omits total floors despite asset-level public support.",
                location="motor_016.report_package.approved_views.report_view.body_sections[Operational Identity]",
            )
        if operational_identity_content and (_observed_asset_field(asset_field_register, "parcel_id") or _observed_asset_field(asset_field_register, "property_id")):
            _append_check(
                checks,
                failures,
                check_id="asset_field_parcel_id_vs_operational_identity",
                passed=_visible_field_has_value(operational_identity_content, "Parcel / Property ID"),
                severity="critical",
                message="Operational Identity still omits parcel/property ID despite asset-level public support.",
                location="motor_016.report_package.approved_views.report_view.body_sections[Operational Identity]",
            )
        if operational_identity_content and _observed_asset_field(asset_field_register, "current_EUI"):
            _append_check(
                checks,
                failures,
                check_id="asset_field_current_eui_vs_operational_identity",
                passed=_visible_field_has_value(operational_identity_content, "Declared EUI Note"),
                severity="critical",
                message="Operational Identity still omits current EUI despite asset-level public support.",
                location="motor_016.report_package.approved_views.report_view.body_sections[Operational Identity]",
            )

        geometry_supported = "geometry_size_cluster" in list(canonical_asset_context_summary.get("supported_clusters", []) or [])
        if operational_identity_content and geometry_supported:
            _append_check(
                checks,
                failures,
                check_id="geometry_cluster_vs_operational_identity",
                passed="Gross Floor Area   : NOT OBSERVED" not in operational_identity_content,
                severity="critical",
                message="Geometry cluster is supported, but Operational Identity still presents scale as missing.",
                location="motor_016.report_package.approved_views.report_view.body_sections[Operational Identity]",
            )

        if report_type_classifier_table:
            classifier_type = str(report_type_classifier_table[0].get("recommended_report_type", "")).strip()
            classifier_type_canonical = canonicalize_output_mode(classifier_type)
            elected_structural_type = str(structural_primary_promotion_gate.get("elected_primary_report_type", "")).strip()
            elected_structural_type_canonical = canonicalize_output_mode(elected_structural_type)
            override_allowed = bool(structural_primary_promotion_gate.get("override_allowed", False))
            _append_check(
                checks,
                failures,
                check_id="classifier_vs_visible_document_type",
                passed=(not classifier_type) or classifier_type_canonical == visible_type_canonical or (override_allowed and elected_structural_type_canonical == visible_type_canonical),
                severity="critical",
                message=f"Classifier recommends '{classifier_type}' but visible report type is '{visible_type}' without a valid structural promotion election.",
                location="motor_034.report_type_classifier_table vs motor_016.report_package.case_metadata.document_visible_type",
            )
            _append_check(
                checks,
                failures,
                check_id="structural_promotion_gate_vs_visible_document_type",
                passed=(not override_allowed and elected_structural_type == "") or (override_allowed and elected_structural_type_canonical == visible_type_canonical),
                severity="critical",
                message="Visible document type diverges from the elected structural primary-promotion gate.",
                location="motor_034.structural_primary_promotion_gate vs motor_016.report_package.case_metadata.document_visible_type",
            )

        if report_output_mode_classifier_table:
            canonical_modes_seen = {
                canonicalize_output_mode(row.get("canonical_output_mode"))
                for row in report_output_mode_classifier_table
                if canonicalize_output_mode(row.get("canonical_output_mode"))
            }
            selected_rows = [
                row for row in report_output_mode_classifier_table
                if bool(row.get("selected_for_publication", False))
            ]
            selected_visible_mode = canonicalize_output_mode(selected_rows[0].get("visible_output_mode", "")) if len(selected_rows) == 1 else ""
            _append_check(
                checks,
                failures,
                check_id="canonical_output_mode_classifier_complete",
                passed=(
                    canonical_modes_seen == _CANONICAL_OUTPUT_MODES
                    and len(selected_rows) == 1
                    and ((not visible_type_canonical) or (not selected_visible_mode) or selected_visible_mode == visible_type_canonical)
                ),
                severity="critical",
                message="Canonical output-mode classifier must cover all nine modes, select exactly one publication row, and match the visible document type.",
                location="motor_034.report_output_mode_classifier_table vs motor_016.report_package.case_metadata.document_visible_type",
            )

        if scenario_evidence_link_register or scenario_section:
            scenario_contract_complete = all(
                str(row.get("scenario", "")).strip()
                and str(row.get("financial_meaning", "")).strip()
                and str(row.get("falsification_condition", "")).strip()
                and str(row.get("linked_evidence_item", "")).strip()
                for row in scenario_evidence_link_register
            )
            _append_check(
                checks,
                failures,
                check_id="scenario_vs_evidence_contract",
                passed=bool(scenario_evidence_link_register) and scenario_contract_complete,
                severity="critical",
                message="Scenario register is missing required evidence linkage, financial meaning, or falsification conditions.",
                location="motor_014.scenario_evidence_link_register",
            )
            scenario_content = _find_first_section_content(
                report_package,
                ["Scenario Space Under Current Uncertainty", "Scenario Space"],
            )
            scenario_section_visible = any(
                str(section.get("title", "")).strip() in {"Scenario Space Under Current Uncertainty", "Scenario Space"}
                for section in body_sections
            )
            scenario_content_normalized = re.sub(r"\s+", " ", str(scenario_content or "")).strip().lower()
            _append_check(
                checks,
                failures,
                check_id="scenario_section_vs_evidence_register",
                passed=(
                    (not scenario_section_visible)
                    or (
                        "evidence needed" in scenario_content_normalized
                        and (
                            "what falsifies it" in scenario_content_normalized
                            or "falsifies it" in scenario_content_normalized
                            or "falsification condition" in scenario_content_normalized
                            or "falsification" in scenario_content_normalized
                        )
                    )
                ),
                severity="critical",
                message="Visible Scenario Space section does not surface the evidence/falsification contract required by the structured scenario register.",
                location="motor_016.report_package.approved_views.report_view.body_sections[Scenario Space]",
            )

        entity_scope_asset_support = [
            row for row in source_family_coverage_table
            if str(row.get("scope", "")).strip() == "ENTITY_LEVEL"
            and "asset-level support" in str(row.get("support_note", "")).strip().lower()
        ]
        _append_check(
            checks,
            failures,
            check_id="source_scope_vs_support_note",
            passed=not entity_scope_asset_support,
            severity="critical",
            message="Public source coverage table still claims asset-level support for an entity-level source.",
            location="motor_016.report_package.source_family_coverage_table",
        )
        owner_entity_level_rows = [
            row
            for row in source_family_coverage_table
            if str(row.get("scope", "")).strip() == "ENTITY_LEVEL"
            and "owner" in {str(item).strip().lower() for item in list(row.get("fields_extracted", []) or [])}
        ]
        owner_suppressed_in_executive = bool(owner_entity_level_rows) and "Owner        :  (NOT OBSERVED" in executive_content
        _append_check(
            checks,
            failures,
            check_id="entity_level_owner_support_not_suppressed",
            passed=not owner_suppressed_in_executive,
            severity="critical",
            message="Executive case identification suppresses owner context even though entity-level owner support is visibly disclosed in the source-coverage table.",
            location="motor_016.report_package.approved_views.report_view.body_sections[Framework Context & Executive Brief]",
        )
        activated_source_keys = _activated_source_keys(source_register, search_attempt_ledger)
        orphan_source_family_rows = [
            row
            for row in source_family_coverage_table
            if (bool(row.get("queried")) or bool(row.get("found")))
            and not _source_row_matches_activation(row, activated_source_keys)
        ]
        _append_check(
            checks,
            failures,
            check_id="source_family_activation_match",
            passed=(not activated_source_keys or not orphan_source_family_rows),
            severity="critical",
            message=(
                "Source-family coverage is surfacing queried/found families that were not activated by the current case search namespace. "
                f"orphan_rows={len(orphan_source_family_rows)}"
            ),
            location="motor_028.source_register / motor_028.search_attempt_ledger / motor_016.report_package.source_family_coverage_table",
        )

        population_state_map = {
            str(row.get("section_title", "")).strip(): str(row.get("population_state", "")).strip()
            for row in section_population_status_register
            if str(row.get("section_title", "")).strip()
        }
        explanation_titles = {
            str(title).strip()
            for row in section_explanation_fallback_register
            for title in list(row.get("section_titles", []) or [])
            if str(title).strip()
        }
        section_fallback_failures: list[str] = []
        for title in ("Competitive / Peer Comparison", "Public Source Coverage Table"):
            section = _find_section(report_package, title)
            if not section:
                continue
            content = _section_visible_text(section).lower()
            state = population_state_map.get(title, "")
            looks_empty = (
                "no competitive-comparison rows were produced" in content
                or "no routed public-source coverage rows were produced" in content
                or "no public source-coverage rows were produced" in content
            )
            if looks_empty and state != "explained_fallback" and title not in explanation_titles:
                section_fallback_failures.append(title)
        _append_check(
            checks,
            failures,
            check_id="section_nonempty_or_explained",
            passed=not section_fallback_failures,
            severity="critical",
            message=(
                "Critical report sections remain empty without governed fallback explanation. "
                f"sections={section_fallback_failures}"
            ),
            location="motor_016.report_package.approved_views.report_view.* / motor_016.report_package.section_population_status_register",
        )

        expected_chapter_files = _expected_chapter_files(report_package)
        planned_files = list(planned_chapter_inventory.get("chapter_files", []) or [])
        _append_check(
            checks,
            failures,
            check_id="planned_chapter_inventory_matches_sections",
            passed=planned_files == expected_chapter_files,
            severity="critical",
            message=f"Planned chapter inventory {planned_files} does not match governed sections {expected_chapter_files}.",
            location="motor_016.report_package.planned_chapter_inventory",
        )
        forbidden_planned = {
            str(name).strip()
            for name in list(planned_chapter_inventory.get("forbidden_template_chapters", []) or [])
            if str(name).strip() in set(planned_files)
        }
        _append_check(
            checks,
            failures,
            check_id="planned_chapter_inventory_excludes_template_scaffolding",
            passed=not forbidden_planned,
            severity="critical",
            message="Planned chapter inventory still includes template/scaffolding chapters.",
            location="motor_016.report_package.planned_chapter_inventory",
        )

        if invalid_comparison_risk_register:
            peer_rows_as_fact = [
                row
                for row in competitive_comparison_register
                if str(row.get("evidence_state", "")).strip() == "OBSERVED_FACT"
            ]
            peer_guardrail_present = (
                bool(str(executive_thesis.get("invalid_comparison_risk", "")).strip())
                and "congruence_invalid_comparison_claim" in congruence_claim_ids
            )
            _append_check(
                checks,
                failures,
                check_id="invalid_comparison_not_used_as_peer_evidence",
                passed=(not peer_rows_as_fact and (inadmissible_thesis or peer_guardrail_present)),
                severity="critical",
                message=(
                    "A structurally invalid comparison is being used as peer evidence, or the thesis/claim guardrail for invalid comparison is missing."
                ),
                location="motor_043.competitive_comparison_register / motor_047.executive_thesis.invalid_comparison_risk / motor_054.congruence_claim_contract_register",
            )

        if measurement_strategy_register or congruence_action_priority_register:
            malformed_measurement_rows = [
                idx
                for idx, row in enumerate(measurement_strategy_register)
                if not str(row.get("hypothesis", "")).strip()
                or not str(row.get("minimum_measurement", "")).strip()
                or not str(row.get("why", "")).strip()
            ]
            measurement_take_required = any(
                str(row.get("strategic_action", "")).strip()
                in {"REQUEST_MINIMUM_EVIDENCE", "MEASURE_ONLY_IF_MATERIAL"}
                for row in congruence_action_priority_register
            )
            _append_check(
                checks,
                failures,
                check_id="measurement_recommendations_require_hypothesis",
                passed=(
                    not malformed_measurement_rows
                    and (
                        not measurement_take_required
                        or inadmissible_thesis
                        or (
                            measurement_strategy_register
                            and bool(str(executive_thesis.get("measurement_minimality_take", "")).strip())
                            and "congruence_measurement_minimality_claim" in congruence_claim_ids
                        )
                    )
                ),
                severity="critical",
                message="Measurement or evidence-minimality recommendations are missing a bounded hypothesis, discriminating measurement, or governed thesis bridge.",
                location="motor_052.measurement_strategy_register / motor_047.executive_thesis.measurement_minimality_take / motor_054.congruence_claim_contract_register",
            )

        if hardware_minimality_register:
            malformed_hardware_rows = [
                idx
                for idx, row in enumerate(hardware_minimality_register)
                if not str(row.get("cheapest_valid_source", "")).strip()
                or not str(row.get("limitation", "")).strip()
                or not str(row.get("upgrade_path", "")).strip()
            ]
            premature_hardware_rows = [
                idx
                for idx, row in enumerate(hardware_minimality_register)
                if str(row.get("cheapest_valid_source", "")).strip().lower() == "temporary analyzer"
                and "only if" not in str(row.get("upgrade_path", "")).strip().lower()
            ]
            _append_check(
                checks,
                failures,
                check_id="hardware_recommendations_follow_cheapest_valid_source_path",
                passed=(not malformed_hardware_rows and not premature_hardware_rows),
                severity="critical",
                message="Hardware minimality is missing cheapest-source discipline or is escalating to hardware before a bounded cheapest valid source path.",
                location="motor_052.hardware_minimality_register",
            )

        if loss_pattern_hypothesis_register:
            invalid_loss_pattern_rows = [
                idx
                for idx, row in enumerate(loss_pattern_hypothesis_register)
                if str(row.get("evidence_state", "")).strip() == "OBSERVED_FACT"
                or str(row.get("pattern_class", "")).strip() != "structural_pattern"
                or not str(row.get("allowed_language", "")).strip()
                or not str(row.get("prohibited_language", "")).strip()
            ]
            _append_check(
                checks,
                failures,
                check_id="loss_patterns_not_presented_as_local_fact",
                passed=not invalid_loss_pattern_rows,
                severity="critical",
                message="Loss-pattern library rows are behaving like local observed diagnosis instead of bounded structural patterns.",
                location="motor_052.loss_pattern_hypothesis_register",
            )

        if regulatory_physics_register:
            invalid_regulatory_rows = [
                idx
                for idx, row in enumerate(regulatory_physics_register)
                if not str(row.get("physical_implication", "")).strip()
                or not list(row.get("what_it_does_not_support", []) or [])
            ]
            _append_check(
                checks,
                failures,
                check_id="permit_signal_not_treated_as_operational_proof",
                passed=not invalid_regulatory_rows,
                severity="critical",
                message="Regulatory or permit signals are missing explicit non-support bounds and risk being treated as proof of current operation.",
                location="motor_053.regulatory_physics_register",
            )

        if finance_physics_dependency_register:
            invalid_finance_rows = [
                idx
                for idx, row in enumerate(finance_physics_dependency_register)
                if not str(row.get("financial_assumption", "")).strip()
                or not str(row.get("physical_dependency", "")).strip()
                or not str(row.get("risk_if_wrong", "")).strip()
                or not list(row.get("evidence_needed", []) or [])
            ]
            _append_check(
                checks,
                failures,
                check_id="finance_claims_bind_to_physical_dependency",
                passed=not invalid_finance_rows,
                severity="critical",
                message="Finance-to-physics rows are missing an explicit physical dependency, risk-if-wrong statement, or minimum evidence pack.",
                location="motor_053.finance_physics_dependency_register",
            )

        if (
            local_evidence_binding_register
            or strategic_gold_nugget_register
            or congruence_action_priority_register
            or congruence_claim_contract_register
        ):
            binding_states = {
                str(row.get("current_local_binding_state", "")).strip()
                for row in local_evidence_binding_register
                if str(row.get("current_local_binding_state", "")).strip()
            }
            non_regulatory_observed_claims = [
                str(row.get("claim_id", "")).strip()
                for row in congruence_claim_contract_register
                if str(row.get("claim_id", "")).strip() != "congruence_regulatory_physics_claim"
                and str(row.get("evidence_state", "")).strip() == "OBSERVED_FACT"
            ]
            public_only_research_mode = str(asset_family_research_profile.get("research_mode", "")).strip() == "public_only_screening"
            _append_check(
                checks,
                failures,
                check_id="research_derived_claims_respect_local_binding",
                passed=(
                    bool(binding_states)
                    and all(state in {
                        "partially_bound",
                        "sufficiently_bound",
                        "public_context_only_unbound",
                        "unbound",
                        "inadmissible_until_asset_identity_bounded",
                    } for state in binding_states)
                    and (
                        not public_only_research_mode
                        or not non_regulatory_observed_claims
                    )
                ),
                severity="critical",
                message=(
                    "Research-derived congruence claims are missing local binding state or are overstating non-regulatory claims as observed fact under public-only screening."
                ),
                location="motor_049.local_evidence_binding_register / motor_054.congruence_claim_contract_register",
            )

        if entity_resolution_register or entity_conflict_register or asset_boundary_resolution_register:
            unresolved_critical_entity_conflicts = [
                row
                for row in entity_conflict_register
                if str(row.get("severity", "")).strip() == "critical"
                and str(row.get("resolution_state", "")).strip() != "resolved_conflict"
            ]
            _append_check(
                checks,
                failures,
                check_id="entity_resolution_conflicts_not_unresolved",
                passed=not unresolved_critical_entity_conflicts,
                severity="critical",
                message=(
                    "Critical entity-resolution conflicts remain unresolved; asset identity or boundary truth is not clean enough for downstream congruence use. "
                    f"conflicts={len(unresolved_critical_entity_conflicts)}"
                ),
                location="motor_049.entity_conflict_register / motor_049.asset_boundary_resolution_register",
            )
            invalid_boundary_rows = [
                row
                for row in asset_boundary_resolution_register
                if not str(row.get("boundary_dimension", "")).strip()
                or not str(row.get("boundary_state", "")).strip()
            ]
            _append_check(
                checks,
                failures,
                check_id="entity_boundary_resolution_rows_complete",
                passed=not invalid_boundary_rows,
                severity="critical",
                message="Asset-boundary resolution rows are missing dimension or state fields.",
                location="motor_049.asset_boundary_resolution_register",
            )

        if asset_field_register or declared_input_downgrade_register:
            promoted_declared_rows = [
                row
                for row in asset_field_register
                if str(row.get("confirmation_state", "")).strip() == "DECLARED_BY_USER"
                and str(row.get("status", "")).strip() not in {"NOT_OBSERVED", "BLOCKING_FIELD"}
                and str(row.get("admissibility", "")).strip() != "DECLARED_INPUT_ONLY"
            ]
            _append_check(
                checks,
                failures,
                check_id="declared_inputs_not_promoted_as_verified_evidence",
                passed=not promoted_declared_rows,
                severity="critical",
                message=(
                    "Declared inputs are being promoted above their downgrade state. "
                    f"promoted_fields={[str(row.get('field', '')).strip() for row in promoted_declared_rows]}"
                ),
                location="motor_012.asset_field_register / motor_012.declared_input_downgrade_register",
            )
            _append_check(
                checks,
                failures,
                check_id="declared_input_not_overpromoted",
                passed=not promoted_declared_rows,
                severity="critical",
                message=(
                    "Declared input remains overpromoted beyond its confirmation ceiling. "
                    f"promoted_fields={[str(row.get('field', '')).strip() for row in promoted_declared_rows]}"
                ),
                location="motor_012.asset_field_register / motor_012.declared_input_downgrade_register",
            )

        chart_assets_in_package = [
            dict(asset)
            for asset in report_assets
            if str(asset.get("asset_type", "")).strip() == "chart"
        ]
        if chart_assets_in_package or chart_case_match_register or cross_case_contamination_scan:
            missing_chart_case_context = [
                idx
                for idx, asset in enumerate(chart_assets_in_package)
                if not str(dict(asset.get("chart_context", {}) or {}).get("case_fingerprint", "")).strip()
            ]
            _append_check(
                checks,
                failures,
                check_id="chart_assets_carry_case_context",
                passed=not missing_chart_case_context,
                severity="critical",
                message=f"Chart assets are missing case-context fingerprint metadata at rows {missing_chart_case_context}.",
                location="motor_016.report_package.assets[*].chart_context",
            )
            critical_chart_case_mismatches = [
                row
                for row in chart_case_match_register
                if str(row.get("severity", "")).strip() == "critical"
            ]
            _append_check(
                checks,
                failures,
                check_id="chart_assets_match_current_case",
                passed=(
                    bool(case_fingerprint)
                    and not critical_chart_case_mismatches
                    and bool(cross_case_contamination_scan.get("render_eligible", not critical_chart_case_mismatches))
                ),
                severity="critical",
                message=(
                    "Chart assets do not match the current case namespace or contamination scan is not render-eligible. "
                    f"critical_chart_case_mismatches={len(critical_chart_case_mismatches)}"
                ),
                location="motor_016.report_package.chart_case_match_register / motor_016.report_package.cross_case_contamination_scan",
            )
            _append_check(
                checks,
                failures,
                check_id="chart_asset_case_match",
                passed=(
                    bool(case_fingerprint)
                    and not critical_chart_case_mismatches
                    and bool(cross_case_contamination_scan.get("render_eligible", not critical_chart_case_mismatches))
                ),
                severity="critical",
                message="Chart assets are not isolated to the current case namespace.",
                location="motor_016.report_package.chart_case_match_register / motor_016.report_package.cross_case_contamination_scan",
            )
            _append_check(
                checks,
                failures,
                check_id="foreign_entity_label_block",
                passed=bool(cross_case_contamination_scan.get("render_eligible", not critical_chart_case_mismatches)),
                severity="critical",
                message="Foreign entity or foreign-case label contamination remains inside chart assets.",
                location="motor_016.report_package.cross_case_contamination_scan",
            )

        if competitive_comparison_register:
            _append_check(
                checks,
                failures,
                check_id="peer_comparison_requires_evidence_state",
                passed=all(str(row.get("evidence_state", "")).strip() for row in competitive_comparison_register),
                severity="critical",
                message="Competitive comparison rows must carry an explicit evidence state.",
                location="motor_043.competitive_comparison_register",
            )

        if conditional_redesign_register:
            _append_check(
                checks,
                failures,
                check_id="conditional_redesign_requires_hypothesis_and_evidence",
                passed=all(
                    str(row.get("hypothesis", "")).strip()
                    and str(row.get("if_confirmed", "")).strip()
                    and str(row.get("if_falsified", "")).strip()
                    and list(row.get("next_evidence", []) or [])
                    for row in conditional_redesign_register
                ),
                severity="critical",
                message="Conditional redesign rows must include hypothesis, confirmation path, falsification path, and next evidence.",
                location="motor_044.conditional_redesign_register",
            )

        if structural_financial_exposure_register:
            _append_check(
                checks,
                failures,
                check_id="structural_financial_outputs_keep_roi_closed",
                passed=all(
                    {"ROI", "IRR", "NPV", "payback", "bankability", "savings claim"} <= set(row.get("prohibited_financial_output", []) or [])
                    for row in structural_financial_exposure_register
                ),
                severity="critical",
                message="Structural financial exposure rows must keep ROI, IRR, NPV, payback, bankability, and savings claims prohibited.",
                location="motor_045.structural_financial_exposure_register",
            )

        if minimum_evidence_for_discrimination_register:
            _append_check(
                checks,
                failures,
                check_id="minimum_evidence_discriminates_rival_hypotheses",
                passed=all(
                    len(list(row.get("rival_hypotheses", []) or [])) >= 2
                    and str(row.get("minimum_evidence", "")).strip()
                    and str(row.get("what_it_confirms", "")).strip()
                    and str(row.get("what_it_falsifies", "")).strip()
                    for row in minimum_evidence_for_discrimination_register
                ),
                severity="critical",
                message="Minimum-evidence rows must discriminate between rival hypotheses, not act as a generic checklist.",
                location="motor_046.minimum_evidence_for_discrimination_register",
            )

        if expanded_structural_tad_action_register and structural_claim_permission_register:
            claim_map = {
                str(row.get("claim", "")).strip(): str(row.get("permission", "")).strip()
                for row in structural_claim_permission_register
                if str(row.get("claim", "")).strip()
            }
            disconnected = []
            for row in expanded_structural_tad_action_register:
                linked_claim = str(row.get("linked_claim", "")).strip()
                status = str(row.get("status", "")).strip()
                if linked_claim in {"peer_comparison_claim", "redesign_hypothesis_claim"} and claim_map.get(linked_claim) == "prohibited" and status in {"COMPARE TO PEERS", "REDESIGN HYPOTHESIS"}:
                    disconnected.append(f"{linked_claim}:{status}")
            _append_check(
                checks,
                failures,
                check_id="expanded_tad_actions_obey_structural_claim_permissions",
                passed=not disconnected,
                severity="critical",
                message="Expanded structural TAD actions are promoting actions that their linked structural claim permissions still prohibit.",
                location="motor_033.expanded_structural_tad_action_register vs motor_034.structural_claim_permission_register",
            )

        if structural_output_mode_classifier_table:
            claim_map = {
                str(row.get("claim", "")).strip(): str(row.get("permission", "")).strip()
                for row in structural_claim_permission_register
                if str(row.get("claim", "")).strip()
            }
            promotion_failures: list[str] = []
            eligible_modes_seen: list[str] = []
            for row in structural_output_mode_classifier_table:
                mode_name = str(row.get("recommended_output_mode", "")).strip()
                promotion_state = str(row.get("primary_promotion_state", "")).strip()
                activation_state = str(row.get("activation_state", "")).strip()
                required_claims = [
                    str(claim).strip()
                    for claim in list(row.get("required_claims", []) or [])
                    if str(claim).strip()
                ]
                if promotion_state == "eligible_primary":
                    eligible_modes_seen.append(mode_name)
                    if activation_state != "activated_secondary":
                        promotion_failures.append(f"{mode_name}:not_active_as_secondary")
                    blocked_claims = [
                        claim for claim in required_claims
                        if claim_map.get(claim) == "prohibited"
                    ]
                    if blocked_claims:
                        promotion_failures.append(
                            f"{mode_name}:claims_prohibited:{','.join(blocked_claims)}"
                        )
            summary_modes = [
                str(mode).strip()
                for mode in list(structural_output_mode_summary.get("eligible_primary_modes", []) or [])
                if str(mode).strip()
            ]
            if summary_modes != eligible_modes_seen:
                promotion_failures.append("summary_mismatch")
            _append_check(
                checks,
                failures,
                check_id="structural_primary_promotion_contract",
                passed=not promotion_failures,
                severity="critical",
                message="Primary structural promotion summary diverges from row-level eligibility or tries to promote a structurally blocked mode.",
                location="motor_034.structural_output_mode_classifier_table / motor_034.structural_output_mode_summary",
            )

        return {
            "consistency_register": checks,
            "critical_failures": failures,
            "blocking_reason_register": list(failures),
            "canonical_report_state": {
                "document_visible_type": visible_type,
                "canonical_asset_context_state": str(
                    canonical_asset_context_summary.get("canonical_asset_context_state", "")
                ).strip(),
                "screening_supported": bool(canonical_asset_context_summary.get("screening_supported", False)),
            },
            "critical_failure_count": len(failures),
            "can_render_pdf": len(failures) == 0,
        }
