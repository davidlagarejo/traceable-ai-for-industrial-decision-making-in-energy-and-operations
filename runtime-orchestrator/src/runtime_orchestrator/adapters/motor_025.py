"""Adapter for motor_025 — Epistemic Governance Layer.

Maintains the canonical 3-axis epistemic status tuple for every material
output of the pipeline:
  Axis A — phase_presence_state:
    absent | scaffolded | present_preliminary | present_decision_supporting |
    present_hardened | present_verified_component
  Axis B — claim_support_state:
    unsupported | hypothesis | indication | screening_grade | decision_grade |
    partially_hardened | verification_ready | verification_supported | verified
  Axis C — publication_state:
    block | hold_for_validation | publish_with_degradation |
    publish_bounded | publish_strong_bounded

For the current pipeline state (Phase 1 data = Decision-grade public data):
- Phases 1-2: present_decision_supporting / decision_grade / publish_bounded
- Phase 3 (report): present_decision_supporting / decision_grade / publish_bounded
- Phases 4-8 in preliminary form: present_preliminary / screening_grade / publish_bounded

Also computes the framework_constraint string for the report and validates
that no output exceeds its claim_support_state ceiling.
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from ..output_taxonomy import (
    CANONICAL_VISIBLE_OUTPUT_MODES,
    canonicalize_output_mode,
    canonicalize_output_mode_list,
    output_mode_alias_policy,
)
from .base import BaseMotorAdapter

# ── Axis definitions ──────────────────────────────────────────────────────────

_AXIS_A_ORDER = [
    "absent",
    "scaffolded",
    "present_preliminary",
    "present_decision_supporting",
    "present_hardened",
    "present_verified_component",
]

_AXIS_B_ORDER = [
    "unsupported",
    "hypothesis",
    "indication",
    "screening_grade",
    "decision_grade",
    "partially_hardened",
    "verification_ready",
    "verification_supported",
    "verified",
]

_AXIS_C_ORDER = [
    "block",
    "hold_for_validation",
    "publish_with_degradation",
    "publish_bounded",
    "publish_strong_bounded",
]

# Publication state ordering (index = permissiveness)
_AXIS_C_INDEX = {s: i for i, s in enumerate(_AXIS_C_ORDER)}
_AXIS_B_INDEX = {s: i for i, s in enumerate(_AXIS_B_ORDER)}

_VISIBLE_REPORT_TYPES = set(CANONICAL_VISIBLE_OUTPUT_MODES)


def _canonical_report_type_label(report_type: str | None, fallback: str | None = None) -> str:
    report_label = str(report_type or "").strip()
    if report_label:
        return report_label
    fallback_label = str(fallback or "").strip()
    if fallback_label:
        return fallback_label
    return canonicalize_output_mode(report_type)


def _canonical_output_mode_label(report_type: str | None, fallback: str | None = None) -> str:
    return _canonical_report_type_label(report_type, fallback)

# ── Phase → canonical epistemic state mapping ─────────────────────────────────
# Based on Phase 1 data = Decision-grade public data
_PHASE_EPISTEMIC_MAP: dict[str, dict[str, str]] = {
    # Phase 1: Inputs and contracts
    "phase_1_inputs": {
        "phase_presence_state": "present_decision_supporting",
        "claim_support_state": "decision_grade",
        "publication_state": "publish_bounded",
        "intended_use": "Structured public context. Traceable inputs.",
        "domain_of_validity": "Decision-grade inputs from public and declared sources.",
    },
    # Phase 2: Parsing, enrichment, versioning
    "phase_2_parsing": {
        "phase_presence_state": "present_decision_supporting",
        "claim_support_state": "decision_grade",
        "publication_state": "publish_bounded",
        "intended_use": "Parsed and enriched public data. Source-traceable.",
        "domain_of_validity": "Public data parsed and enriched without site verification.",
    },
    # Phase 3: Report / governed asset brief
    "phase_3_report": {
        "phase_presence_state": "present_decision_supporting",
        "claim_support_state": "decision_grade",
        "publication_state": "publish_bounded",
        "intended_use": "Decision Intelligence Report. For preparatory analysis only.",
        "domain_of_validity": "Decision-grade: proportional claims, no verified diagnoses.",
    },
    # Phase 4: Verification bridge (preliminary)
    "phase_4_verification_bridge": {
        "phase_presence_state": "present_preliminary",
        "claim_support_state": "screening_grade",
        "publication_state": "publish_bounded",
        "intended_use": "Preliminary propagation map. Not for final decisions.",
        "domain_of_validity": "Screening-grade: impact tracing only, not verification.",
    },
    # Phase 5: Field data integration (absent at Phase 1)
    "phase_5_field_data": {
        "phase_presence_state": "absent",
        "claim_support_state": "unsupported",
        "publication_state": "block",
        "intended_use": "Not yet active. Requires field validation data.",
        "domain_of_validity": "Not applicable — no field data available.",
    },
    # Phase 6: Hardening
    "phase_6_hardening": {
        "phase_presence_state": "absent",
        "claim_support_state": "unsupported",
        "publication_state": "block",
        "intended_use": "Not yet active. Requires Phase 5 completion.",
        "domain_of_validity": "Not applicable.",
    },
    # Phase 7: Validation architecture
    "phase_7_validation": {
        "phase_presence_state": "present_preliminary",
        "claim_support_state": "screening_grade",
        "publication_state": "publish_bounded",
        "intended_use": "Preliminary validation agenda. Ordering is indicative, not final.",
        "domain_of_validity": "Screening-grade agenda based on Decision-grade inference.",
    },
    # Phase 8: Publishing
    "phase_8_publishing": {
        "phase_presence_state": "present_preliminary",
        "claim_support_state": "decision_grade",
        "publication_state": "publish_bounded",
        "intended_use": "Report delivery. Subject to epistemic ceiling of upstream phases.",
        "domain_of_validity": "Decision-grade output package.",
    },
}

# ── Output-level epistemic register entries ───────────────────────────────────
# Maps output_id → base epistemic state. Dynamic adjustments applied per run.
_BASE_OUTPUT_REGISTER: dict[str, dict[str, str]] = {
    "facility_prior":           {"phase": "phase_1_inputs",    "upgrade_requirements": "Site survey or operator-confirmed data"},
    "inference_case_register":  {"phase": "phase_1_inputs",    "upgrade_requirements": "Field validation of each case"},
    "decision_core":            {"phase": "phase_1_inputs",    "upgrade_requirements": "Validation of all blocking conflicts"},
    "validation_queue":         {"phase": "phase_7_validation","upgrade_requirements": "Execute validation agenda items"},
    "next_best_questions":      {"phase": "phase_7_validation","upgrade_requirements": "Obtain answers to each question"},
    "opportunity_candidates":   {"phase": "phase_1_inputs",    "upgrade_requirements": "Confirm value pathway via field evidence"},
    "tension_records":          {"phase": "phase_1_inputs",    "upgrade_requirements": "Resolve each tension through validation"},
    "conflict_register":        {"phase": "phase_1_inputs",    "upgrade_requirements": "Resolve blocking conflicts — mandatory before advancement"},
    "evidence_gap_register":    {"phase": "phase_7_validation","upgrade_requirements": "Fill each evidence gap"},
    "benchmark_bundle":         {"phase": "phase_2_parsing",   "upgrade_requirements": "Replace with site-measured EUI data"},
    "jurisdiction_bundle":      {"phase": "phase_1_inputs",    "upgrade_requirements": "Confirm regulatory applicability with formal authority"},
    "regulatory_flag_bundle":   {"phase": "phase_1_inputs",    "upgrade_requirements": "Obtain official compliance determination"},
    "compliance_applicability_case": {"phase": "phase_7_validation", "upgrade_requirements": "Confirm trigger fields, thresholds, and current compliance filing"},
    "system_asset_hypotheses":  {"phase": "phase_1_inputs",    "upgrade_requirements": "Site survey of each declared system"},
    "propagation_map":          {"phase": "phase_4_verification_bridge", "upgrade_requirements": "Execute re-evaluation for each flagged case"},
    "belief_revision_register": {"phase": "phase_4_verification_bridge", "upgrade_requirements": "Resolve each downgrade / hold / block propagation event"},
    "report_package":           {"phase": "phase_3_report",    "upgrade_requirements": "Advance underlying cases to Verification-grade"},
    "pdf_output":               {"phase": "phase_8_publishing","upgrade_requirements": "Advance underlying analytical outputs"},
    "governance_event_log":     {"phase": "phase_8_publishing","upgrade_requirements": "Resolve all error/critical events"},
}

_REPORT_IDENTITY_REFINEMENT_TYPES = {
    "Decision-Blocked Asset Brief",
    "Exploratory Prior Brief",
    "Compliance / Investment Screening Brief",
    "Full Technical Decision Intelligence Report",
}


def _build_epistemic_status_entry(
    output_id: str,
    base_phase: str,
    extra_downgrade_triggers: list[str],
    has_blocking_conflicts: bool,
    stubs_active: int,
) -> dict:
    """Build the full epistemic status entry for an output."""
    phase_data = _PHASE_EPISTEMIC_MAP.get(base_phase, _PHASE_EPISTEMIC_MAP["phase_1_inputs"])

    phase_presence_state = phase_data["phase_presence_state"]
    claim_support_state = phase_data["claim_support_state"]
    publication_state = phase_data["publication_state"]

    # Apply downgrade rules
    # Blocking conflicts: specific analytical claim outputs are held for validation,
    # but the report itself must still circulate to communicate those conflicts.
    # The report IS the vehicle for disclosing blocking conflicts to the analyst.
    if has_blocking_conflicts:
        if output_id == "conflict_register":
            # Conflicts themselves: publish_bounded with BLOCKING marker (not held —
            # they need to be visible in the report exactly because they are blocking)
            publication_state = "publish_bounded"
            claim_support_state = "decision_grade"
        elif output_id in ("decision_core", "inference_case_register"):
            # Decision outputs that DEPEND on resolving conflicts: hold
            publication_state = "hold_for_validation"
            claim_support_state = "indication"
        elif output_id in ("report_package", "pdf_output"):
            # Report circulates bounded — conflicts are explicitly disclosed within it
            publication_state = "publish_bounded"

    if stubs_active > 5 and output_id in ("report_package", "pdf_output", "governance_event_log"):
        publication_state = "publish_with_degradation"

    # Determine closure_state
    if publication_state == "block":
        closure_state = "blocked"
    elif publication_state == "hold_for_validation":
        closure_state = "held"
    elif has_blocking_conflicts:
        closure_state = "open_with_blockers"
    else:
        closure_state = "open"

    # Downgrade triggers for this output
    downgrade_triggers = list(extra_downgrade_triggers)
    if has_blocking_conflicts:
        downgrade_triggers.append("Blocking conflicts active — report circulates bounded with conflict disclosure")
    if stubs_active > 0:
        downgrade_triggers.append(f"{stubs_active} motor(s) running as stubs")

    upgrade_req = _BASE_OUTPUT_REGISTER.get(output_id, {}).get("upgrade_requirements", "")

    return {
        "phase_presence_state": phase_presence_state,
        "claim_support_state": claim_support_state,
        "publication_state": publication_state,
        "closure_state": closure_state,
        "intended_use": phase_data.get("intended_use", ""),
        "domain_of_validity": phase_data.get("domain_of_validity", ""),
        "upgrade_requirements": upgrade_req,
        "downgrade_triggers": downgrade_triggers,
    }


def _derive_epistemic_grade(
    claim_support_states: list[str],
    has_blocking_conflicts: bool,
) -> str:
    """Derive overall epistemic grade from the set of claim support states."""
    if has_blocking_conflicts:
        return "Decision-grade (unresolved conflicts)"
    # Find the minimum (most conservative) claim_support_state in the register
    if not claim_support_states:
        return "Decision-grade"
    min_idx = min(_AXIS_B_INDEX.get(s, 0) for s in claim_support_states)
    min_state = _AXIS_B_ORDER[min_idx]
    if min_state in ("verified", "verification_supported"):
        return "Verification-grade"
    if min_state in ("partially_hardened", "verification_ready"):
        return "Hardened-grade"
    if min_state == "decision_grade":
        return "Decision-grade"
    return "Preliminary"


def _derive_publication_ceiling(publication_states: list[str]) -> str:
    """Derive the most conservative publication state across all outputs."""
    if not publication_states:
        return "publish_bounded"
    min_idx = min(_AXIS_C_INDEX.get(s, 3) for s in publication_states)
    return _AXIS_C_ORDER[min_idx]


def _refine_report_identity(
    *,
    target_admissibility_state: str | None,
    report_identity_state: str | None,
    recommended_report_type: str | None,
    report_readiness_allowed: list[str] | None,
) -> tuple[str, str]:
    current_identity = str(report_identity_state or "").strip()
    current_recommendation = str(recommended_report_type or "").strip()
    readiness_allowed = [str(item).strip() for item in (report_readiness_allowed or []) if str(item).strip()]
    if (
        current_identity in {"Address Candidate Brief", "Site Candidate Brief"}
        and current_recommendation in readiness_allowed
    ):
        return current_recommendation, current_recommendation
    if target_admissibility_state not in {"bounded_asset", "bounded_asset_with_operable_context"}:
        return current_identity, current_recommendation
    refined = next((item for item in readiness_allowed if item in _REPORT_IDENTITY_REFINEMENT_TYPES), "")
    if not refined:
        return current_identity, current_recommendation
    return refined, refined


class Motor025Adapter(BaseMotorAdapter):
    @property
    def motor_id(self) -> str:
        return "motor_025"

    @property
    def input_motor_ids(self) -> list[str]:
        return ["motor_001", "motor_034", "motor_022", "motor_024"]

    def _run_impl(self, inputs: dict[str, Any]) -> dict[str, Any]:
        produced_at = datetime.now(timezone.utc).isoformat()
        runtime = inputs.get("__runtime__", {}) if isinstance(inputs.get("__runtime__", {}), dict) else {}

        # Read upstream inputs
        m01 = inputs.get("motor_001", {})
        m34 = inputs.get("motor_034", {}) if isinstance(inputs.get("motor_034", {}), dict) else {}
        m22 = inputs.get("motor_022", {})  # conformance stub — may not be real
        m24 = inputs.get("motor_024", {})

        # Derive pipeline health from governance events
        governance_log = m24.get("governance_event_log", [])
        pipeline_health = m24.get("pipeline_health_summary", {})
        runtime_truth = m24.get("runtime_truth_summary", runtime.get("truth_summary", {}))
        stub_register = m24.get("stub_execution_register", [])
        exception_register = m24.get("exception_register", [])

        stubs_active = (
            runtime_truth.get("stub", 0)
            + runtime_truth.get("cached_stub", 0)
            + runtime_truth.get("completed_stub", 0)
        ) or len(stub_register)
        errors_count = pipeline_health.get("errors", len(exception_register))
        blocking_conflicts = pipeline_health.get("blocking_conflicts", 0)
        quality_gate_passed = pipeline_health.get(
            "source_quality_gate_passed",
            pipeline_health.get("quality_gate_passed", True),
        )
        final_report_ready = pipeline_health.get("final_report_ready", True)
        traceability_chain_complete = pipeline_health.get("traceability_chain_complete", True)
        traceability_missing_segments = pipeline_health.get("traceability_missing_segments", [])
        publication_freeze_recommended = pipeline_health.get("publication_freeze_recommended", False)
        regulatory_open_cases = pipeline_health.get("regulatory_open_cases", 0)
        belief_revision_events = pipeline_health.get("belief_revision_events", 0)
        llm_fallback_sections = pipeline_health.get("llm_fallback_sections", 0)
        llm_lint_failures = pipeline_health.get("llm_lint_failures", 0)
        llm_budget_exhausted = pipeline_health.get("llm_budget_exhausted", False)
        report_preflight_passed = bool(pipeline_health.get("report_preflight_passed", True))
        report_preflight_critical_failure_count = int(pipeline_health.get("report_preflight_critical_failure_count", 0) or 0)
        report_preflight_failures = list(pipeline_health.get("report_preflight_failures", []) or [])
        target_scope = pipeline_health.get("target_scope", runtime.get("target_definition", {}).get("target_scope"))
        target_type = pipeline_health.get("target_type", runtime.get("target_definition", {}).get("target_type"))
        target_admissibility_state = pipeline_health.get("target_admissibility_state", runtime.get("target_admissibility_state"))
        allowed_report_classes = pipeline_health.get("allowed_report_classes", runtime.get("allowed_report_classes", []))
        subject_gate_passed = bool(pipeline_health.get("subject_gate_passed", runtime.get("subject_gate_passed", False)))
        asset_context_readiness = pipeline_health.get("asset_context_readiness", runtime.get("asset_context_readiness"))
        report_identity_state = pipeline_health.get("report_identity_state", runtime.get("report_identity_state"))
        dominant_evidence_scope = pipeline_health.get("dominant_evidence_scope", runtime.get("dominant_evidence_scope"))
        missing_observable_clusters = pipeline_health.get(
            "missing_observable_clusters",
            runtime.get("missing_observable_clusters", []),
        )
        subject_mismatch_detected = bool(pipeline_health.get("subject_mismatch_detected", False))
        technical_underpopulation_detected = bool(pipeline_health.get("technical_underpopulation_detected", False))
        issuer_dominance_detected = bool(pipeline_health.get("issuer_dominance_detected", False))
        mandatory_section_missing_detected = bool(pipeline_health.get("mandatory_section_missing_detected", False))
        context_contamination_detected = bool(pipeline_health.get("context_contamination_detected", False))
        target_classification_object = pipeline_health.get("target_classification_object", {})
        recommended_report_type = pipeline_health.get("recommended_report_type", runtime.get("recommended_report_type"))
        early_report_type_gate = str(recommended_report_type or report_identity_state or "").strip()
        prohibited_report_types = pipeline_health.get("prohibited_report_types", runtime.get("prohibited_report_types", []))
        source_register_count = int(pipeline_health.get("source_register_count", 0) or 0)
        routing_plan_total = int(pipeline_health.get("routing_plan_total", 0) or 0)
        mandatory_source_gap_count = int(pipeline_health.get("mandatory_source_gap_count", 0) or 0)
        mandatory_sources_missing_from_executor = list(pipeline_health.get("mandatory_sources_missing_from_executor", []) or [])
        routing_plan_gate_passed = bool(pipeline_health.get("routing_plan_gate_passed", mandatory_source_gap_count == 0))
        contamination_log_count = int(pipeline_health.get("contamination_log_count", 0) or 0)
        asset_field_register_count = int(pipeline_health.get("asset_field_register_count", 0) or 0)
        missing_evidence_count = int(pipeline_health.get("missing_evidence_count", 0) or 0)
        blocking_field_count = int(pipeline_health.get("blocking_field_count", 0) or 0)
        claim_permission_block_count = int(pipeline_health.get("claim_permission_block_count", 0) or 0)
        key_variable_bottlenecks = list(pipeline_health.get("key_variable_bottlenecks", []) or [])
        report_readiness_allowed = list(pipeline_health.get("report_readiness_allowed", []) or [])
        report_readiness_prohibited = list(pipeline_health.get("report_readiness_prohibited", []) or [])
        report_readiness_reason = str(pipeline_health.get("report_readiness_reason", "") or "")
        claim_permission_register = list(m34.get("claim_permission_register", []) or [])
        decision_permission_register = list(m34.get("decision_permission_register", []) or [])
        structural_output_mode_summary = dict(m34.get("structural_output_mode_summary", {}) or {})
        structural_primary_promotion_gate = dict(m34.get("structural_primary_promotion_gate", {}) or {})
        report_output_mode_classifier_table = list(m34.get("report_output_mode_classifier_table", []) or [])
        canonical_problem_frame = dict(m34.get("canonical_problem_frame", {}) or {})
        early_recommended_report_type = recommended_report_type
        report_identity_state, recommended_report_type = _refine_report_identity(
            target_admissibility_state=target_admissibility_state,
            report_identity_state=report_identity_state,
            recommended_report_type=recommended_report_type,
            report_readiness_allowed=report_readiness_allowed,
        )
        maturity_refined_report_type = str(report_identity_state or recommended_report_type or "").strip()
        report_type_override_reason = ""
        if early_report_type_gate and maturity_refined_report_type and early_report_type_gate != maturity_refined_report_type:
            report_type_override_reason = report_readiness_reason or (
                "Evidence-maturity readiness refined the early report gate."
            )
        final_published_report_type = maturity_refined_report_type
        selected_output_mode_row = next(
            (
                row for row in report_output_mode_classifier_table
                if bool(row.get("selected_for_publication", False))
            ),
            {},
        )
        selected_visible_output_mode = str(selected_output_mode_row.get("visible_output_mode", "") or "").strip()
        selected_canonical_output_mode = str(selected_output_mode_row.get("canonical_output_mode", "") or "").strip()
        if selected_visible_output_mode in _VISIBLE_REPORT_TYPES:
            final_published_report_type = selected_visible_output_mode
            report_identity_state = selected_visible_output_mode
            recommended_report_type = selected_visible_output_mode
            selected_basis = str(selected_output_mode_row.get("selection_basis", "") or "").strip()
            if selected_basis:
                report_type_override_reason = selected_basis
        elif bool(structural_primary_promotion_gate.get("override_allowed", False)):
            elected_mode = str(structural_primary_promotion_gate.get("elected_primary_report_type", "") or "").strip()
            if elected_mode in _VISIBLE_REPORT_TYPES:
                final_published_report_type = elected_mode
                report_identity_state = elected_mode
                recommended_report_type = elected_mode
                if report_type_override_reason:
                    report_type_override_reason += " Structural promotion gate elected the requested primary structural mode."
                else:
                    report_type_override_reason = str(structural_primary_promotion_gate.get("reason", "") or "")

        has_blocking_conflicts = blocking_conflicts > 0

        # Derive downgrade triggers common to all outputs
        common_downgrade_triggers: list[str] = []
        if errors_count > 0:
            common_downgrade_triggers.append(f"{errors_count} error event(s) in governance log")
        if not quality_gate_passed:
            common_downgrade_triggers.append("Source discovery quality gate not passed")
        if not final_report_ready:
            common_downgrade_triggers.append("Final report deliverable is incomplete or missing")
        if not traceability_chain_complete:
            common_downgrade_triggers.append(
                "Traceability chain incomplete: " + ", ".join(traceability_missing_segments)
            )
        if publication_freeze_recommended:
            common_downgrade_triggers.append(
                "Belief revision layer recommends freezing publication pending downstream re-evaluation"
            )
        if regulatory_open_cases > 0:
            common_downgrade_triggers.append(
                f"{regulatory_open_cases} regulatory posture case(s) remain open — compliance closure is not admissible"
            )
        if belief_revision_events > 0:
            common_downgrade_triggers.append(
                f"{belief_revision_events} belief revision event(s) require downstream review"
            )
        if llm_fallback_sections > 0:
            common_downgrade_triggers.append(
                f"{llm_fallback_sections} LLM section(s) required deterministic fallback"
            )
        if llm_lint_failures > 0:
            common_downgrade_triggers.append(
                f"{llm_lint_failures} LLM section(s) failed policy lint before publication"
            )
        if llm_budget_exhausted:
            common_downgrade_triggers.append(
                "LLM writing budget exhausted before all requested sections were freely rendered"
            )
        if not report_preflight_passed:
            common_downgrade_triggers.append(
                f"Report preflight failed {report_preflight_critical_failure_count} critical check(s) before PDF publication."
            )
        if not subject_gate_passed:
            common_downgrade_triggers.append(
                f"Subject gate not passed: target admissibility remains {target_admissibility_state or 'unknown'}."
            )
        if allowed_report_classes and report_identity_state and report_identity_state not in allowed_report_classes:
            common_downgrade_triggers.append(
                f"Report identity {report_identity_state} exceeds allowed classes for current subject state."
            )
        if target_scope == "asset" and asset_context_readiness in (
            "issuer_context_only",
            "location_only",
            "asset_context_insufficient",
        ):
            common_downgrade_triggers.append(
                f"Asset-scoped case remains {asset_context_readiness}; physical and operational substrate is not yet sufficient for a full technical asset brief."
            )
        if issuer_dominance_detected:
            common_downgrade_triggers.append(
                f"Dominant evidence scope is {dominant_evidence_scope}; issuer context is outrunning asset context."
            )
        if technical_underpopulation_detected and missing_observable_clusters:
            common_downgrade_triggers.append(
                "Missing observable clusters: " + ", ".join(missing_observable_clusters)
            )
        if subject_mismatch_detected:
            common_downgrade_triggers.append(
                "Declared case still behaves as issuer/address/site candidate rather than bounded asset."
            )
        if mandatory_section_missing_detected:
            common_downgrade_triggers.append(
                "Decision-admissibility product surface is missing one or more mandatory body sections."
            )
        if context_contamination_detected:
            common_downgrade_triggers.append(
                "Context contamination or invalid visible field detected in the report surface."
            )
        if contamination_log_count > 0:
            common_downgrade_triggers.append(
                f"{contamination_log_count} ingestion contamination event(s) were rejected before asset-level use."
            )
        if source_register_count == 0:
            common_downgrade_triggers.append(
                "No governed source register was preserved from discovery."
            )
        if mandatory_source_gap_count > 0:
            common_downgrade_triggers.append(
                "Mandatory routed source(s) were not executed by discovery: "
                + ", ".join(mandatory_sources_missing_from_executor[:6])
            )
        if blocking_field_count > 0:
            common_downgrade_triggers.append(
                f"{blocking_field_count} critical asset field(s) remain blocking."
            )
        if claim_permission_block_count > 0:
            common_downgrade_triggers.append(
                f"{claim_permission_block_count} claim class(es) remain blocked by variable-maturity bottlenecks."
            )
        if report_readiness_reason:
            common_downgrade_triggers.append(report_readiness_reason)
        if missing_evidence_count > 0:
            common_downgrade_triggers.append(
                f"{missing_evidence_count} minimum evidence request item(s) remain open."
            )
        if recommended_report_type and report_identity_state and recommended_report_type != report_identity_state:
            common_downgrade_triggers.append(
                f"Scraping-layer recommendation is {recommended_report_type}, while runtime identity is {report_identity_state}."
            )
        if report_identity_state and report_identity_state in prohibited_report_types:
            common_downgrade_triggers.append(
                f"Current report identity {report_identity_state} is explicitly prohibited by the scraping admissibility layer."
            )
        if report_identity_state and report_readiness_prohibited and report_identity_state in report_readiness_prohibited:
            common_downgrade_triggers.append(
                f"Current report identity {report_identity_state} is prohibited by the evidence-maturity readiness layer."
            )

        # Build epistemic status register for all known outputs
        epistemic_status_register: dict[str, dict] = {}
        for output_id, base_info in _BASE_OUTPUT_REGISTER.items():
            base_phase = base_info["phase"]
            epistemic_status_register[output_id] = _build_epistemic_status_entry(
                output_id=output_id,
                base_phase=base_phase,
                extra_downgrade_triggers=list(common_downgrade_triggers),
                has_blocking_conflicts=has_blocking_conflicts,
                stubs_active=stubs_active,
            )

        if not final_report_ready:
            for output_id in ("report_package", "pdf_output"):
                if output_id in epistemic_status_register:
                    epistemic_status_register[output_id]["publication_state"] = "hold_for_validation"
                    epistemic_status_register[output_id]["closure_state"] = "held"
                    epistemic_status_register[output_id]["downgrade_triggers"].append(
                        "Final report deliverable incomplete — publishable closure not admissible"
                    )
        if not report_preflight_passed:
            for output_id in ("report_package", "pdf_output"):
                if output_id in epistemic_status_register:
                    epistemic_status_register[output_id]["publication_state"] = "hold_for_validation"
                    epistemic_status_register[output_id]["closure_state"] = "held"
                    epistemic_status_register[output_id]["downgrade_triggers"].append(
                        "Critical report preflight check failed before PDF publication."
                    )
        if not traceability_chain_complete:
            for output_id in ("report_package", "pdf_output", "governance_event_log"):
                if output_id in epistemic_status_register:
                    epistemic_status_register[output_id]["publication_state"] = "hold_for_validation"
                    epistemic_status_register[output_id]["closure_state"] = "held"
                    epistemic_status_register[output_id]["downgrade_triggers"].append(
                        "Traceability chain incomplete — publication beyond validation hold is not admissible"
                    )
        if mandatory_source_gap_count > 0:
            for output_id in ("report_package", "pdf_output"):
                if output_id in epistemic_status_register:
                    epistemic_status_register[output_id]["publication_state"] = "hold_for_validation"
                    epistemic_status_register[output_id]["closure_state"] = "held"
                    epistemic_status_register[output_id]["downgrade_triggers"].append(
                        "Mandatory routed public sources were not executed by discovery; publication must wait for routing coverage closure."
                    )
        if publication_freeze_recommended:
            for output_id in ("report_package", "pdf_output", "governance_event_log"):
                if output_id in epistemic_status_register:
                    epistemic_status_register[output_id]["publication_state"] = "hold_for_validation"
                    epistemic_status_register[output_id]["closure_state"] = "held"
                    epistemic_status_register[output_id]["downgrade_triggers"].append(
                        "Belief revision layer recommended freeze_publication for at least one downstream output"
                    )
        if allowed_report_classes and report_identity_state and report_identity_state not in allowed_report_classes:
            for output_id in ("report_package", "pdf_output"):
                if output_id in epistemic_status_register:
                    epistemic_status_register[output_id]["publication_state"] = "hold_for_validation"
                    epistemic_status_register[output_id]["closure_state"] = "held"
                    epistemic_status_register[output_id]["downgrade_triggers"].append(
                        "Report identity exceeds classes allowed by the subject admissibility gate"
                    )
        if report_identity_state and report_readiness_prohibited and report_identity_state in report_readiness_prohibited:
            for output_id in ("report_package", "pdf_output"):
                if output_id in epistemic_status_register:
                    epistemic_status_register[output_id]["publication_state"] = "hold_for_validation"
                    epistemic_status_register[output_id]["closure_state"] = "held"
                    epistemic_status_register[output_id]["downgrade_triggers"].append(
                        "Report identity exceeds evidence-maturity readiness ceiling."
                    )
        if llm_lint_failures > 0:
            for output_id in ("report_package", "pdf_output"):
                if output_id in epistemic_status_register:
                    epistemic_status_register[output_id]["publication_state"] = "publish_with_degradation"
                    epistemic_status_register[output_id]["downgrade_triggers"].append(
                        "LLM output required lint-based downgrade before publication"
                    )
        if llm_budget_exhausted or llm_fallback_sections > 0:
            for output_id in ("report_package", "pdf_output"):
                if output_id in epistemic_status_register and epistemic_status_register[output_id]["publication_state"] == "publish_bounded":
                    epistemic_status_register[output_id]["publication_state"] = "publish_with_degradation"
                    epistemic_status_register[output_id]["downgrade_triggers"].append(
                        "LLM layer fell back to deterministic text for part of the report"
                    )
        if target_scope == "asset" and asset_context_readiness in (
            "issuer_context_only",
            "location_only",
            "asset_context_insufficient",
            "asset_context_minimal",
        ):
            for output_id in ("report_package", "pdf_output"):
                if output_id in epistemic_status_register:
                    if epistemic_status_register[output_id]["publication_state"] == "publish_bounded":
                        epistemic_status_register[output_id]["publication_state"] = "publish_with_degradation"
                    epistemic_status_register[output_id]["downgrade_triggers"].append(
                        f"Report identity degraded to {report_identity_state} because asset context is only {asset_context_readiness}."
                    )
        if mandatory_section_missing_detected:
            for output_id in ("report_package", "pdf_output"):
                if output_id in epistemic_status_register:
                    epistemic_status_register[output_id]["publication_state"] = "hold_for_validation"
                    epistemic_status_register[output_id]["closure_state"] = "held"
                    epistemic_status_register[output_id]["downgrade_triggers"].append(
                        "Mandatory product sections missing from the rendered decision-admissibility report."
                    )
        if context_contamination_detected:
            for output_id in ("report_package", "pdf_output"):
                if output_id in epistemic_status_register:
                    epistemic_status_register[output_id]["publication_state"] = "hold_for_validation"
                    epistemic_status_register[output_id]["closure_state"] = "held"
                    epistemic_status_register[output_id]["downgrade_triggers"].append(
                        "Context contamination guard triggered; document is not admissible for delivery."
                    )
        if "compliance_applicability_case" in epistemic_status_register and regulatory_open_cases > 0:
            epistemic_status_register["compliance_applicability_case"]["claim_support_state"] = "screening_grade"
            epistemic_status_register["compliance_applicability_case"]["publication_state"] = "publish_bounded"
            epistemic_status_register["compliance_applicability_case"]["closure_state"] = "open"
            epistemic_status_register["compliance_applicability_case"]["downgrade_triggers"].append(
                "Regulatory posture remains open; applicability screening is admissible but compliance closure is not"
            )

        # Conformance check from motor_022 (if real)
        conformance_violations: list[str] = []
        if not m22.get("__stub__"):
            violations = m22.get("conformance_violations", [])
            conformance_violations = violations
            if violations:
                common_downgrade_triggers.append(
                    f"{len(violations)} conformance violation(s) detected"
                )
                # Apply hold to affected outputs
                for v in violations:
                    affected_output = v.get("output_id", "")
                    if affected_output in epistemic_status_register:
                        epistemic_status_register[affected_output]["publication_state"] = "hold_for_validation"
                        epistemic_status_register[affected_output]["downgrade_triggers"].append(
                            f"Conformance violation: {v.get('description', '')}"
                        )

        # Derive blocked outputs
        blocked_outputs = [
            oid for oid, entry in epistemic_status_register.items()
            if entry.get("publication_state") in ("block", "hold_for_validation")
        ]

        # Derive overall publication_ceiling from DELIVERABLE outputs only
        # (internal held outputs like decision_core don't constrain the report ceiling)
        _DELIVERABLE_OUTPUTS = {"report_package", "pdf_output", "output_block_register", "governance_event_log"}
        deliverable_pub_states = [
            e.get("publication_state", "publish_bounded")
            for oid, e in epistemic_status_register.items()
            if oid in _DELIVERABLE_OUTPUTS and e.get("publication_state") not in ("block",)
        ]
        if not deliverable_pub_states:
            deliverable_pub_states = [
                e.get("publication_state", "publish_bounded")
                for e in epistemic_status_register.values()
                if e.get("publication_state") != "block"
            ]
        publication_ceiling = _derive_publication_ceiling(deliverable_pub_states)

        # Derive overall epistemic grade
        all_claim_states = [
            e.get("claim_support_state", "decision_grade")
            for e in epistemic_status_register.values()
        ]
        epistemic_grade = _derive_epistemic_grade(all_claim_states, has_blocking_conflicts)

        # Build framework_constraint string
        constraint_parts = [
            "This pipeline output is produced under the ZLab Operational Truth Framework.",
            f"Epistemic grade: {epistemic_grade}.",
            f"Publication ceiling: {publication_ceiling.replace('_', ' ').title()}.",
            "All claims are conditional on validation requirements stated in the report.",
            "No output constitutes a verified diagnosis, compliance determination, or recommendation.",
        ]
        if has_blocking_conflicts:
            constraint_parts.append(
                f"{blocking_conflicts} BLOCKING CONFLICT(S) active — "
                "epistemic advancement on dependent outputs is halted until resolved."
            )
        if not final_report_ready:
            constraint_parts.append(
                "Final report delivery is incomplete — output package must be treated as partial."
            )
        if not traceability_chain_complete:
            constraint_parts.append(
                "Traceability chain is incomplete — report and PDF must be held until lineage gaps are resolved."
            )
        if publication_freeze_recommended:
            constraint_parts.append(
                "Propagation logic identified downstream outputs that must be frozen pending re-evaluation."
            )
        if regulatory_open_cases > 0:
            constraint_parts.append(
                "Regulatory applicability may be screened, but compliance posture remains open and non-closing."
            )
        if stubs_active > 0:
            constraint_parts.append(
                f"{stubs_active} motor(s) running as stubs — pipeline operating with partial functionality."
            )
        if target_scope:
            constraint_parts.append(
                f"Target scope: {target_scope}. Target type: {target_type or 'unspecified'}."
            )
        if target_admissibility_state:
            constraint_parts.append(
                f"Target admissibility state: {target_admissibility_state}."
            )
        if report_identity_state:
            constraint_parts.append(
                f"Admissible document identity at current support level: {report_identity_state}."
            )
        if issuer_dominance_detected:
            constraint_parts.append(
                "Issuer-level context currently outweighs asset-level context; finance and issuer disclosures must remain subordinated."
            )
        if target_classification_object:
            constraint_parts.append(
                f"Scraping classification: {target_classification_object.get('target_type', 'UNKNOWN')} "
                f"({target_classification_object.get('classification_confidence', 'unknown')} confidence)."
            )
        if blocking_field_count > 0:
            constraint_parts.append(
                f"{blocking_field_count} blocking asset field(s) remain unresolved."
            )
        if key_variable_bottlenecks:
            constraint_parts.append(
                "Key variable bottlenecks: " + ", ".join(key_variable_bottlenecks[:6]) + "."
            )

        framework_constraint = " ".join(constraint_parts)

        return {
            "epistemic_status_register": epistemic_status_register,
            "framework_constraint": framework_constraint,
            "publication_ceiling": publication_ceiling,
            "epistemic_grade": epistemic_grade,
            "blocked_outputs": blocked_outputs,
            "conformance_violations": conformance_violations,
            "stubs_active": stubs_active,
            "blocking_conflicts": blocking_conflicts,
            "publication_freeze_recommended": publication_freeze_recommended,
            "regulatory_open_cases": regulatory_open_cases,
            "belief_revision_events": belief_revision_events,
            "report_preflight_passed": report_preflight_passed,
            "report_preflight_critical_failure_count": report_preflight_critical_failure_count,
            "report_preflight_failures": report_preflight_failures,
            "target_scope": target_scope,
            "target_type": target_type,
            "target_admissibility_state": target_admissibility_state,
            "allowed_report_classes": allowed_report_classes,
            "subject_gate_passed": subject_gate_passed,
            "asset_context_readiness": asset_context_readiness,
            "report_identity_state": report_identity_state,
            "report_type_trace": {
                "early_report_type_gate_internal": early_report_type_gate,
                "early_report_type_gate": _canonical_report_type_label(early_report_type_gate, early_recommended_report_type),
                "maturity_refined_report_type_internal": maturity_refined_report_type,
                "maturity_refined_report_type": _canonical_report_type_label(maturity_refined_report_type, recommended_report_type),
                "final_published_report_type_internal": final_published_report_type,
                "final_published_report_type": _canonical_report_type_label(final_published_report_type, recommended_report_type),
                "final_published_output_mode_canonical": selected_canonical_output_mode or _canonical_output_mode_label(final_published_report_type, recommended_report_type),
                "report_output_mode_classifier_count": len(report_output_mode_classifier_table),
                "report_type_override_reason": report_type_override_reason,
                "secondary_structural_output_modes": list(structural_output_mode_summary.get("activated_secondary_modes", []) or []),
                "blocked_secondary_structural_output_modes": list(structural_output_mode_summary.get("blocked_secondary_modes", []) or []),
                "secondary_output_mode_policy_note": str(structural_output_mode_summary.get("policy_note", "") or ""),
                "eligible_primary_structural_output_modes": list(structural_output_mode_summary.get("eligible_primary_modes", []) or []),
                "non_promotable_primary_structural_output_modes": list(structural_output_mode_summary.get("non_promotable_primary_modes", []) or []),
                "leading_primary_structural_output_mode": str(structural_output_mode_summary.get("leading_primary_promotion_candidate", "") or ""),
                "primary_structural_mode_policy_note": str(structural_output_mode_summary.get("primary_promotion_policy_note", "") or ""),
                "structural_primary_promotion_state": str(structural_primary_promotion_gate.get("promotion_state", "") or ""),
                "requested_structural_primary_mode": str(structural_primary_promotion_gate.get("requested_structural_primary_mode", "") or ""),
                "default_reasoning_path": str(
                    structural_primary_promotion_gate.get("default_reasoning_path", "")
                    or canonical_problem_frame.get("reasoning_path", "")
                    or "legacy_decision_gating_only"
                ),
                "canonical_problem_frame_active": bool(
                    structural_primary_promotion_gate.get("problem_frame_active", canonical_problem_frame.get("problem_frame_active", False))
                ),
                "structural_sovereignty_state": (
                    "structural_first_default"
                    if str(
                        structural_primary_promotion_gate.get("default_reasoning_path", "")
                        or canonical_problem_frame.get("reasoning_path", "")
                    ).strip() == "structural_first"
                    else "legacy_decision_gating_only"
                ),
                "default_structural_output_mode": str(
                    structural_primary_promotion_gate.get("default_structural_output_mode", "")
                    or canonical_problem_frame.get("leading_structural_output_mode", "")
                    or ""
                ),
                "stated_problem": str(canonical_problem_frame.get("stated_problem", "") or ""),
                "reframed_problem": str(canonical_problem_frame.get("reframed_problem", "") or ""),
                "dominant_structural_conflict": str(canonical_problem_frame.get("dominant_conflict", "") or ""),
                "minimum_evidence_to_discriminate": str(canonical_problem_frame.get("minimum_evidence_to_discriminate", "") or ""),
            },
            "dominant_evidence_scope": dominant_evidence_scope,
            "missing_observable_clusters": missing_observable_clusters,
            "traceability_chain_complete": traceability_chain_complete,
            "traceability_missing_segments": traceability_missing_segments,
            "mandatory_section_missing_detected": mandatory_section_missing_detected,
            "context_contamination_detected": context_contamination_detected,
            "target_classification_object": target_classification_object,
            "recommended_report_type": recommended_report_type,
            "recommended_report_type_visible": canonicalize_output_mode(recommended_report_type),
            "recommended_report_type_canonical": canonicalize_output_mode(recommended_report_type),
            "recommended_report_type_alias_policy": output_mode_alias_policy(recommended_report_type),
            "prohibited_report_types": prohibited_report_types,
            "prohibited_report_types_canonical": canonicalize_output_mode_list(prohibited_report_types),
            "report_readiness_allowed": report_readiness_allowed,
            "report_readiness_prohibited": report_readiness_prohibited,
            "allowed_report_classes_canonical": canonicalize_output_mode_list(allowed_report_classes),
            "visible_output_taxonomy_policy": {
                "canonical_visible_labels_only": True,
                "compatibility_aliases_internal_only": True,
                "policy": "Compatibility aliases may persist in upstream raw fields, but visible runtime/report/manifest surfaces must use canonical labels only.",
            },
            "report_readiness_reason": report_readiness_reason,
            "source_register_count": source_register_count,
            "routing_plan_total": routing_plan_total,
            "mandatory_source_gap_count": mandatory_source_gap_count,
            "mandatory_sources_missing_from_executor": mandatory_sources_missing_from_executor,
            "routing_plan_gate_passed": routing_plan_gate_passed,
            "asset_field_register_count": asset_field_register_count,
            "missing_evidence_count": missing_evidence_count,
            "blocking_field_count": blocking_field_count,
            "claim_permission_block_count": claim_permission_block_count,
            "key_variable_bottlenecks": key_variable_bottlenecks,
            "claim_permission_register": claim_permission_register,
            "decision_permission_register": decision_permission_register,
            "structural_output_mode_summary": structural_output_mode_summary,
            "report_output_mode_classifier_table": report_output_mode_classifier_table,
            "structural_primary_promotion_gate": structural_primary_promotion_gate,
            "total_outputs_registered": len(epistemic_status_register),
            "produced_at": produced_at,
        }
