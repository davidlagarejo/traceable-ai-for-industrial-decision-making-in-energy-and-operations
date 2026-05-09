"""Adapter for motor_024 — Governance Event & Exception Registry.

Records every significant event in the pipeline run for full audit trail.
This is the motor that answers "why did an error occur" and "what happened
at each step".

Records:
- Motor execution events (started, completed, failed, cached)
- Quality gate events (passed, failed, with reason)
- Stub execution events (which motors ran as stubs)
- Evidence coverage gaps
- Claim activation events
- Score computation events
- Publishing decisions

Every event has: event_id, event_type, motor_id, timestamp, description,
severity (info/warning/error/critical), traceable_inputs, outcome.
"""
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from typing import Any

from .base import BaseMotorAdapter
from ..ingestion_learning import (
    build_case_delta_register,
    build_ingestion_learning_register,
    build_next_ingestion_priority_update,
    build_source_yield_memory,
)
try:
    from ..zlab_skill.loader import load_registry_bundle
    from ..zlab_skill.validator_engine import apply_validators_for_scope
except Exception:
    load_registry_bundle = None
    apply_validators_for_scope = None

# Severity levels
_SEV_INFO = "info"
_SEV_WARNING = "warning"
_SEV_ERROR = "error"
_SEV_CRITICAL = "critical"


def _normalize_evidence_key(value: str) -> str:
    text = " ".join(str(value or "").strip().lower().split())
    if not text:
        return ""
    replacements = (
        ("major energy-using equipment", "systems_inventory"),
        ("process line", "systems_inventory"),
        ("controls system inventory", "systems_inventory"),
        ("utility bills", "utility_fuel_records"),
        ("utility / fuel", "utility_fuel_records"),
        ("fuel profile", "utility_fuel_records"),
        ("meter map", "utility_fuel_records"),
        ("throughput profile", "operating_profile"),
        ("shift schedule", "operating_profile"),
        ("operating schedule", "operating_profile"),
        ("gfa", "scale_geometry"),
        ("building area", "scale_geometry"),
        ("rentable area", "scale_geometry"),
    )
    for signal, token in replacements:
        if signal in text:
            return token
    return text


_CRITICAL_CONTEXT_ISSUE_CODES = {
    "legacy_ll97_reference",
    "legacy_local_law_97_reference",
    "legacy_operational_intelligence_report",
    "legacy_operational_decision_intelligence_report",
    "legacy_technical_decision_intelligence_report",
    "legacy_empire_state_reference",
    "legacy_350_fifth_reference",
    "legacy_800_boylston_reference",
    "legacy_pier_1_reference",
    "legacy_universe_blvd_reference",
    "legacy_main_avenue_reference",
    "legacy_boston_properties_reference",
    "legacy_prologis_reference",
    "legacy_nextera_reference",
    "legacy_general_electric_reference",
    "legacy_esrt_reference",
    "legacy_bxp_reference",
    "legacy_pld_reference",
    "legacy_nee_reference",
    "legacy_tdir_reference",
    "legacy_building_leasing_semantics",
    "legacy_building_reletting_semantics",
    "legacy_building_subletting_semantics",
    "legacy_building_anchor_tenant_semantics",
    "legacy_building_common_area_semantics",
    "legacy_building_rentable_area_semantics",
    "legacy_building_tenant_driven_semantics",
    "invalid_zero_gfa",
    "invalid_blank_eui",
    "invalid_blank_eui_unspecified",
    "invalid_zero_eui",
    "invalid_unspecified_fuel",
    "invalid_unspecified_systems",
    "invalid_not_confirmed",
    "instruction_leakage_chart",
    "instruction_leakage_text",
    "instruction_leakage_prose",
}


def _build_report_preflight_register(
    m14: dict[str, Any],
    m16: dict[str, Any],
    m34: dict[str, Any],
    m36: dict[str, Any],
) -> dict[str, Any]:
    claim_permission_register = list(m34.get("claim_permission_register", []) or [])
    claim_permission_summary = dict(m14.get("claim_permission_summary", {}) or {})
    minimum_evidence_unlock_map = list(m14.get("minimum_evidence_unlock_map", []) or [])
    scenario_space = list(m14.get("scenario_space", []) or [])
    report_package = dict(m16.get("report_package", {}) or {})
    context_integrity_scan = dict(report_package.get("context_integrity_scan", {}) or {})
    case_adaptation_memo = dict(report_package.get("case_adaptation_memo", {}) or {})
    case_metadata = dict(report_package.get("case_metadata", {}) or {})
    executive_thesis = dict(report_package.get("executive_thesis", {}) or {})
    context_integrity_issues = list(context_integrity_scan.get("issues", []) or [])
    consistency_failures = list(m36.get("critical_failures", []) or [])
    consistency_can_render = bool(m36.get("can_render_pdf", True))

    matrix_counts = {"allowed": 0, "conditional": 0, "prohibited": 0, "deferred": 0}
    for row in claim_permission_register:
        state = str(row.get("current_permission", "")).lower()
        if state in matrix_counts:
            matrix_counts[state] += 1

    summary_counts = {
        "allowed": int(claim_permission_summary.get("allowed", 0) or 0),
        "conditional": int(claim_permission_summary.get("conditional", 0) or 0),
        "prohibited": int(claim_permission_summary.get("prohibited", 0) or 0),
        "deferred": int(claim_permission_summary.get("deferred", 0) or 0),
    }
    claim_counts_match = summary_counts == matrix_counts

    incomplete_claim_rows: list[dict[str, Any]] = []
    for row in claim_permission_register:
        missing_fields: list[str] = []
        required_evidence = row.get("required_evidence", None)
        dependency_variables = row.get("dependency_variables", None)
        upgrade_path = row.get("upgrade_path", None)
        if not isinstance(required_evidence, list) or not required_evidence:
            missing_fields.append("required_evidence")
        if not isinstance(dependency_variables, list):
            missing_fields.append("dependency_variables")
        if str(row.get("current_permission", "")).lower() == "conditional":
            if not isinstance(upgrade_path, list) or not upgrade_path:
                missing_fields.append("upgrade_path")
        if missing_fields:
            incomplete_claim_rows.append(
                {
                    "claim_name": row.get("claim_name", ""),
                    "missing_fields": missing_fields,
                }
            )

    seen_evidence: dict[str, str] = {}
    duplicate_evidence_items: list[str] = []
    for row in minimum_evidence_unlock_map:
        item = str(row.get("evidence_item", "")).strip()
        key = _normalize_evidence_key(item)
        if not key:
            continue
        if key in seen_evidence:
            duplicate_evidence_items.append(item)
            continue
        seen_evidence[key] = item

    scenario_missing_fields: list[dict[str, Any]] = []
    for idx, row in enumerate(scenario_space, 1):
        missing = []
        if not str(row.get("financial_meaning", "")).strip():
            missing.append("financial_meaning")
        if not str(row.get("what_would_falsify_it", "")).strip():
            missing.append("what_would_falsify_it")
        if not str(row.get("evidence_needed", "")).strip():
            missing.append("evidence_needed")
        if missing:
            scenario_missing_fields.append(
                {
                    "index": idx,
                    "scenario": row.get("scenario", ""),
                    "missing_fields": missing,
                }
            )

    critical_failures: list[dict[str, Any]] = []
    checks: list[dict[str, Any]] = []

    scenario_signature_seed = {
        "document_visible_type": str(case_metadata.get("document_visible_type", "")).strip(),
        "gold_nugget_authority_state": str(executive_thesis.get("gold_nugget_authority_state", "")).strip(),
        "minimum_discriminating_evidence": list(executive_thesis.get("minimum_discriminating_evidence", []) or []),
        "failure_reasons": list(case_adaptation_memo.get("failure_reasons", []) or []),
        "case_rows": list(case_adaptation_memo.get("rows", []) or [])[:6],
    }
    scenario_signature = hashlib.sha1(
        json.dumps(scenario_signature_seed, sort_keys=True, ensure_ascii=True).encode("utf-8")
    ).hexdigest()
    report_output_validation_row = {
        "scenario_signature": scenario_signature,
        "template_contamination_failure": bool(case_adaptation_memo.get("template_contamination_failure", False)),
        "template_contamination_state": (
            "contaminated"
            if bool(case_adaptation_memo.get("template_contamination_failure", False))
            else "clear"
        ),
        "document_visible_type": str(case_metadata.get("document_visible_type", "")).strip(),
        "gold_nugget_authority_state": str(executive_thesis.get("gold_nugget_authority_state", "")).strip(),
    }
    try:
        registry_bundle = load_registry_bundle() if load_registry_bundle is not None else {}
    except Exception:
        registry_bundle = {}
    report_output_validation_register = (
        apply_validators_for_scope(
            [report_output_validation_row],
            scope="report_output",
            registry_bundle=registry_bundle,
        )
        if apply_validators_for_scope is not None
        else [dict(report_output_validation_row, validator_state="not_run", validator_findings=[])]
    )
    report_output_validator_row = dict((report_output_validation_register or [{}])[0] or {})

    def _append_check(name: str, passed: bool, error: str = "", location: str = "", critical: bool = False) -> None:
        checks.append(
            {
                "lint_check": name,
                "passed": passed,
                "error": error,
                "location": location,
                "critical": critical,
            }
        )
        if critical and not passed:
            critical_failures.append(
                {
                    "check": name,
                    "error": error,
                    "location": location,
                }
            )

    _append_check(
        "claim_permission_counts_match",
        claim_counts_match,
        error=(
            f"summary={summary_counts} matrix={matrix_counts}"
            if not claim_counts_match
            else ""
        ),
        location="motor_014.claim_permission_summary vs motor_034.claim_permission_register",
        critical=True,
    )
    _append_check(
        "claim_permission_contract_complete",
        len(incomplete_claim_rows) == 0,
        error=json.dumps(incomplete_claim_rows[:6]) if incomplete_claim_rows else "",
        location="motor_034.claim_permission_register",
        critical=True,
    )
    _append_check(
        "scenario_contract_complete",
        len(scenario_missing_fields) == 0,
        error=json.dumps(scenario_missing_fields[:4]) if scenario_missing_fields else "",
        location="motor_014.scenario_space",
        critical=True,
    )
    _append_check(
        "minimum_evidence_pack_deduped",
        len(duplicate_evidence_items) == 0,
        error=", ".join(duplicate_evidence_items[:6]),
        location="motor_014.minimum_evidence_unlock_map",
        critical=True,
    )
    render_eligible = bool(context_integrity_scan.get("render_eligible", True))
    critical_context_issues = [
        issue for issue in context_integrity_issues
        if str(issue.get("issue_code", "")).strip() in _CRITICAL_CONTEXT_ISSUE_CODES
    ]
    literal_lint_hits = [
        issue for issue in context_integrity_issues
        if str(issue.get("issue_code", "")).strip() in {
            "instruction_leakage_chart",
            "instruction_leakage_text",
            "instruction_leakage_prose",
            "instruction_leakage_reader_takeaway",
            "instruction_leakage_technical_reference_data",
            "instruction_leakage_epistemic_marker",
            "instruction_leakage_chapter_marker",
        }
    ]
    factual_integrity_hits = [
        issue for issue in context_integrity_issues
        if str(issue.get("issue_code", "")).strip() in {
            "invalid_zero_gfa",
            "invalid_blank_eui",
            "invalid_blank_eui_unspecified",
            "invalid_zero_eui",
            "invalid_unspecified_fuel",
            "invalid_unspecified_systems",
            "invalid_not_confirmed",
        }
    ]
    legacy_context_hits = [
        issue for issue in context_integrity_issues
        if str(issue.get("issue_code", "")).strip() not in {
            "instruction_leakage_chart",
            "instruction_leakage_text",
            "instruction_leakage_prose",
            "instruction_leakage_reader_takeaway",
            "instruction_leakage_technical_reference_data",
            "instruction_leakage_epistemic_marker",
            "instruction_leakage_chapter_marker",
            "invalid_zero_gfa",
            "invalid_blank_eui",
            "invalid_blank_eui_unspecified",
            "invalid_zero_eui",
            "invalid_unspecified_fuel",
            "invalid_unspecified_systems",
            "invalid_not_confirmed",
        }
    ]
    _append_check(
        "context_integrity_render_eligible",
        render_eligible,
        error="Context integrity scan marked report as not render-eligible." if not render_eligible else "",
        location="motor_016.report_package.context_integrity_scan",
        critical=True,
    )
    _append_check(
        "critical_context_issue_codes_clear",
        len(critical_context_issues) == 0,
        error=json.dumps(critical_context_issues[:6]) if critical_context_issues else "",
        location="motor_016.report_package.context_integrity_scan.issues",
        critical=True,
    )
    _append_check(
        "literal_instruction_leakage_clear",
        len(literal_lint_hits) == 0,
        error=json.dumps(literal_lint_hits[:6]) if literal_lint_hits else "",
        location="motor_016.report_package.context_integrity_scan.issues",
        critical=True,
    )
    _append_check(
        "factual_blank_or_zero_field_leakage_clear",
        len(factual_integrity_hits) == 0,
        error=json.dumps(factual_integrity_hits[:6]) if factual_integrity_hits else "",
        location="motor_016.report_package.context_integrity_scan.issues",
        critical=True,
    )
    _append_check(
        "wrong_asset_or_jurisdiction_or_regulation_clear",
        len(legacy_context_hits) == 0,
        error=json.dumps(legacy_context_hits[:6]) if legacy_context_hits else "",
        location="motor_016.report_package.context_integrity_scan.issues",
        critical=True,
    )
    adaptation_failure = bool(case_adaptation_memo.get("template_contamination_failure", False))
    _append_check(
        "case_adaptation_memo_present",
        bool(case_adaptation_memo.get("rows")),
        error="Case adaptation memo missing or empty.",
        location="motor_016.report_package.case_adaptation_memo",
        critical=True,
    )
    _append_check(
        "template_contamination_failure",
        not adaptation_failure,
        error="; ".join(case_adaptation_memo.get("failure_reasons", [])[:4]) if adaptation_failure else "",
        location="motor_016.report_package.case_adaptation_memo",
        critical=True,
    )
    _append_check(
        "report_output_validators_passed",
        str(report_output_validator_row.get("validator_state", "")).strip() != "blocked",
        error="; ".join(
            str(row.get("message", "")).strip()
            for row in list(report_output_validator_row.get("validator_findings", []) or [])
            if str(row.get("message", "")).strip()
        ),
        location="zlab_skill.report_output_validation_register",
        critical=True,
    )
    _append_check(
        "system_consistency_validator_passed",
        consistency_can_render,
        error="; ".join(str(row.get("message", "")) for row in consistency_failures[:4]),
        location="motor_036.consistency_register",
        critical=True,
    )

    return {
        "checks": checks,
        "critical_failure_count": len(critical_failures),
        "critical_failures": critical_failures,
        "claim_permission_counts_match": claim_counts_match,
        "claim_permission_contract_complete": len(incomplete_claim_rows) == 0,
        "matrix_claim_counts": matrix_counts,
        "summary_claim_counts": summary_counts,
        "incomplete_claim_rows": incomplete_claim_rows,
        "duplicate_evidence_items": duplicate_evidence_items,
        "scenario_missing_fields": scenario_missing_fields,
        "render_eligible": render_eligible,
        "critical_context_issues": critical_context_issues,
        "literal_lint_hits": literal_lint_hits,
        "factual_integrity_hits": factual_integrity_hits,
        "legacy_context_hits": legacy_context_hits,
        "system_consistency_failures": consistency_failures,
        "system_consistency_passed": consistency_can_render,
        "report_output_validation_register": report_output_validation_register,
        "report_output_validator_state": str(report_output_validator_row.get("validator_state", "")).strip(),
        "report_output_validator_findings": list(report_output_validator_row.get("validator_findings", []) or []),
        "case_adaptation_summary": {
            "substantive_dimension_count": int(case_adaptation_memo.get("substantive_dimension_count", 0) or 0),
            "required_dimension_count": int(case_adaptation_memo.get("required_dimension_count", 0) or 0),
            "template_contamination_failure": adaptation_failure,
            "failure_reasons": list(case_adaptation_memo.get("failure_reasons", []) or []),
        },
        "passed": len(critical_failures) == 0,
    }


def _build_phase_self_evaluation_register(
    pipeline: dict[str, Any],
    m07: dict[str, Any],
    m12: dict[str, Any],
    m14: dict[str, Any],
    m28: dict[str, Any],
    m33: dict[str, Any],
    m34: dict[str, Any],
    report_preflight_register: dict[str, Any],
) -> dict[str, Any]:
    case_id = str(pipeline.get("case_id", "")).strip()
    target_definition = dict(m07.get("target_definition_contract", {}) or {})
    target_name = (
        str(target_definition.get("target_name", "")).strip()
        or str(target_definition.get("target_label", "")).strip()
        or case_id
    )
    recommended_report_type = str(
        m34.get("report_readiness_register", {}).get("report_type_allowed", [None])[0]
        or m07.get("recommended_report_type", "")
    ).strip()
    target_type = str((m07.get("target_classification_object", {}) or {}).get("target_type", "")).strip()

    asset_field_register = list(m12.get("asset_field_register", []) or [])
    minimum_evidence_unlock_map = list(m14.get("minimum_evidence_unlock_map", []) or [])
    financial_exposure_register = list(m14.get("financial_exposure_register", []) or [])
    scenario_space = list(m14.get("scenario_space", []) or [])
    decision_front_actions = list((m33.get("tad_preliminary", {}) or {}).get("decision_front_actions", []) or [])
    routing_plan_compliance = dict(m28.get("routing_plan_compliance", {}) or {})
    cluster_profile = dict(m34.get("cluster_report_readiness_profile", {}) or {})
    allowed_report_types = list((m34.get("report_readiness_register", {}) or {}).get("report_type_allowed", []) or [])
    adaptation_summary = dict(report_preflight_register.get("case_adaptation_summary", {}) or {})

    def _result(resolved: bool, partial: bool) -> str:
        if resolved:
            return "resolved"
        if partial:
            return "partially_resolved"
        return "unresolved"

    rows: list[dict[str, Any]] = []

    strong_public_screening_possible = bool(cluster_profile.get("strong_public_screening_possible", False))
    classification_only_type = recommended_report_type in {
        "Entity Address Classification Brief",
        "Target Clarification Brief",
    }
    report_type_resolved = (
        (classification_only_type and target_type in {"CORPORATE_HEADQUARTERS", "AMBIGUOUS_TARGET", "REGISTERED_AGENT_OR_MAILING_ADDRESS"})
        or (strong_public_screening_possible and "Compliance / Investment Screening Brief" in allowed_report_types)
    )
    report_type_partial = bool(allowed_report_types) or bool(recommended_report_type)
    rows.append(
        {
            "phase": "report_type_graduation",
            "change_implemented": "Multidimensional report-type classification now distinguishes classification-only, blocked, exploratory, and screening-grade states.",
            "test_run": case_id or target_name,
            "result": _result(report_type_resolved, report_type_partial),
            "remaining_gap": (
                ""
                if report_type_resolved
                else "Case remains bounded below screening threshold or still depends on early blocked identity posture."
            ),
        }
    )

    support_flags_present = any(
        any(key in row for key in ("identity_supported", "physical_substrate_supported", "operating_substrate_supported", "regulatory_supported"))
        for row in asset_field_register
    )
    support_note_present = any(
        "identity only" in str(row.get("notes", "")).lower()
        for row in asset_field_register
    )
    rows.append(
        {
            "phase": "field_support_semantics",
            "change_implemented": "Field rows now separate identity support from physical, operating, and regulatory substrate support.",
            "test_run": case_id or target_name,
            "result": _result(support_flags_present and (support_note_present or asset_field_register), bool(asset_field_register)),
            "remaining_gap": "" if support_flags_present else "Asset field register does not yet expose the semantic support flags required for strict substrate interpretation.",
        }
    )

    routing_resolved = (
        bool(routing_plan_compliance.get("routing_ready", False))
        and len(routing_plan_compliance.get("mandatory_sources_missing_from_executor", []) or []) == 0
        and int(routing_plan_compliance.get("accepted_routed_sources", 0) or 0) > 0
    )
    routing_partial = bool(routing_plan_compliance.get("total_routed_sources", 0) or routing_plan_compliance.get("routing_ready", False))
    rows.append(
        {
            "phase": "public_source_routing",
            "change_implemented": "Routing is now jurisdiction-, asset-, and decision-sensitive, with executor compliance tracked against mandatory sources.",
            "test_run": case_id or target_name,
            "result": _result(routing_resolved, routing_partial),
            "remaining_gap": (
                ""
                if routing_resolved
                else "One or more mandatory routed sources remain unexecuted or no asset-level routed source was accepted."
            ),
        }
    )

    claim_match = bool(report_preflight_register.get("claim_permission_counts_match", False))
    rows.append(
        {
            "phase": "claim_permission_consistency",
            "change_implemented": "Governance summary, claim matrix, and downstream publication now share a hard consistency gate.",
            "test_run": case_id or target_name,
            "result": _result(claim_match, False),
            "remaining_gap": "" if claim_match else "Claim permission summary still diverges from the matrix and blocks publication.",
        }
    )

    canonical_statuses = {
        str(row.get("current_status", "")).strip()
        for row in decision_front_actions
        if str(row.get("current_status", "")).strip()
    }
    tad_resolved = len(canonical_statuses & {"ACT NOW", "VALIDATE FIRST", "INVESTIGATE", "DEFER", "NO-GO"}) >= 2
    tad_partial = bool(decision_front_actions)
    rows.append(
        {
            "phase": "tad_graduation",
            "change_implemented": "TAD now uses differentiated admissibility states with explicit prohibited actions and variable bottlenecks.",
            "test_run": case_id or target_name,
            "result": _result(tad_resolved, tad_partial),
            "remaining_gap": "" if tad_resolved else "Decision fronts are still too flat or missing case-specific posture differentiation.",
        }
    )

    duplicate_evidence_items = list(report_preflight_register.get("duplicate_evidence_items", []) or [])
    evidence_count = len(minimum_evidence_unlock_map)
    evidence_resolved = evidence_count > 0 and evidence_count <= 10 and not duplicate_evidence_items
    evidence_partial = evidence_count > 0
    rows.append(
        {
            "phase": "minimum_evidence_pack",
            "change_implemented": "Minimum Evidence Pack now deduplicates by semantic unlock-equivalence and prioritizes by decision value.",
            "test_run": case_id or target_name,
            "result": _result(evidence_resolved, evidence_partial),
            "remaining_gap": "" if evidence_resolved else "Evidence pack is empty, oversized, or still contains duplicate unlock items.",
        }
    )

    financial_resolved = all(
        str(row.get("downside_if_wrong", "")).strip() and str(row.get("financial_consequence", "")).strip()
        for row in financial_exposure_register
    ) if financial_exposure_register else False
    financial_partial = bool(financial_exposure_register)
    rows.append(
        {
            "phase": "financial_exposure_translation",
            "change_implemented": "Financial uncertainty is translated into downside exposure without manufacturing unsupported ROI.",
            "test_run": case_id or target_name,
            "result": _result(financial_resolved, financial_partial),
            "remaining_gap": "" if financial_resolved else "Financial exposure rows are absent or still fail to state downside and consequence explicitly.",
        }
    )

    scenario_missing_fields = list(report_preflight_register.get("scenario_missing_fields", []) or [])
    scenario_resolved = bool(scenario_space) and len(scenario_missing_fields) == 0
    scenario_partial = bool(scenario_space)
    rows.append(
        {
            "phase": "scenario_contracts",
            "change_implemented": "Scenario rows are now linked to decisions and evidence, with falsification and financial meaning required.",
            "test_run": case_id or target_name,
            "result": _result(scenario_resolved, scenario_partial),
            "remaining_gap": "" if scenario_resolved else "Scenarios remain incomplete or missing financial meaning / falsification conditions.",
        }
    )

    preflight_passed = bool(report_preflight_register.get("passed", False))
    adaptation_ok = not bool(adaptation_summary.get("template_contamination_failure", False))
    adaptation_rows_present = int(adaptation_summary.get("substantive_dimension_count", 0) or 0) > 0
    rows.append(
        {
            "phase": "preflight_and_case_adaptation",
            "change_implemented": "The pipeline now blocks PDF publication on critical lint, coherence, or template-contamination failures.",
            "test_run": case_id or target_name,
            "result": _result(preflight_passed and adaptation_ok, preflight_passed or adaptation_rows_present),
            "remaining_gap": "" if preflight_passed and adaptation_ok else "Critical preflight failure or template contamination still prevents safe publication.",
        }
    )

    summary = {
        "total_phases": len(rows),
        "resolved": sum(1 for row in rows if row["result"] == "resolved"),
        "partially_resolved": sum(1 for row in rows if row["result"] == "partially_resolved"),
        "unresolved": sum(1 for row in rows if row["result"] == "unresolved"),
        "overall_result": (
            "resolved"
            if all(row["result"] == "resolved" for row in rows)
            else "partially_resolved"
            if any(row["result"] == "resolved" for row in rows)
            else "unresolved"
        ),
        "recommended_report_type": recommended_report_type,
        "target_type": target_type,
        "case_id": case_id,
        "target_name": target_name,
    }

    return {
        "rows": rows,
        "summary": summary,
    }


def _event_id(motor_id: str, event_type: str, index: int) -> str:
    key = f"{motor_id}:{event_type}:{index}"
    return "evt:" + hashlib.md5(key.encode()).hexdigest()[:10]


def _audit_hash(events: list[dict]) -> str:
    """Compute a deterministic hash over all events for integrity verification."""
    payload = json.dumps(
        [{"event_id": e.get("event_id"), "outcome": e.get("outcome")} for e in events],
        sort_keys=True,
    )
    return "audit:" + hashlib.sha256(payload.encode()).hexdigest()[:16]


class Motor024Adapter(BaseMotorAdapter):
    @property
    def motor_id(self) -> str:
        return "motor_024"

    @property
    def input_motor_ids(self) -> list[str]:
        return [
            "motor_001",
            "motor_002",
            "motor_007",
            "motor_009",
            "motor_028",
            "motor_012",
            "motor_034",
            "motor_013",
            "motor_014",
            "motor_019",
            "motor_020",
            "motor_015",
            "motor_016",
            "motor_036",
            "motor_017",
            "motor_027",
            "motor_033",
        ]

    def _run_impl(self, inputs: dict[str, Any]) -> dict[str, Any]:
        produced_at = datetime.now(timezone.utc).isoformat()
        events: list[dict] = []
        evt_counter = 0
        pipeline = inputs.get("__pipeline__", {}) if isinstance(inputs.get("__pipeline__", {}), dict) else {}
        runtime = inputs.get("__runtime__", {}) if isinstance(inputs.get("__runtime__", {}), dict) else {}
        runtime_results = runtime.get("motor_results", {}) if isinstance(runtime.get("motor_results", {}), dict) else {}
        runtime_truth = runtime.get("truth_summary", {}) if isinstance(runtime.get("truth_summary", {}), dict) else {}

        def _add_event(
            event_type: str,
            motor_id: str,
            description: str,
            severity: str,
            traceable_inputs: dict,
            outcome: str,
            extra: dict | None = None,
        ) -> None:
            nonlocal evt_counter
            evt_counter += 1
            ev = {
                "event_id": _event_id(motor_id, event_type, evt_counter),
                "event_type": event_type,
                "motor_id": motor_id,
                "timestamp": produced_at,
                "description": description,
                "severity": severity,
                "traceable_inputs": traceable_inputs,
                "outcome": outcome,
            }
            if extra:
                ev.update(extra)
            events.append(ev)

        # ── 1. Contracts validation (motor_001) ────────────────────────────────
        m01 = inputs.get("motor_001", {})
        validated_contracts = m01.get("validated_contracts", [])
        rejected_contracts = m01.get("rejected_contracts", [])
        total_contracts = m01.get("total_input", 0)

        _add_event(
            event_type="motor_completed",
            motor_id="motor_001",
            description=f"Phase contract registry: {len(validated_contracts)}/{total_contracts} contracts validated.",
            severity=_SEV_INFO if not rejected_contracts else _SEV_WARNING,
            traceable_inputs={"total_input": total_contracts},
            outcome="completed",
            extra={"validated_count": len(validated_contracts), "rejected_count": len(rejected_contracts)},
        )

        for rejected in rejected_contracts:
            _add_event(
                event_type="contract_rejected",
                motor_id="motor_001",
                description=f"Contract rejected: phase_id={rejected.get('phase_id')} — {rejected.get('reason')}",
                severity=_SEV_ERROR,
                traceable_inputs={"phase_id": rejected.get("phase_id")},
                outcome="rejected",
            )

        # ── 2. Versioned objects (motor_002) ────────────────────────────────────
        m02 = inputs.get("motor_002", {})
        versioned_objects = m02.get("versioned_objects", [])
        total_versioned = m02.get("total_versioned", len(versioned_objects))

        _add_event(
            event_type="motor_completed",
            motor_id="motor_002",
            description=f"Versioned object registry: {total_versioned} objects registered.",
            severity=_SEV_INFO,
            traceable_inputs={"total_versioned": total_versioned},
            outcome="completed",
        )

        # ── 3. Source-quality + asset-context gate events ──────────────────────
        m28 = inputs.get("motor_028", {})
        m34 = inputs.get("motor_034", {}) if isinstance(inputs.get("motor_034", {}), dict) else {}
        m36 = inputs.get("motor_036", {}) if isinstance(inputs.get("motor_036", {}), dict) else {}
        if m28 and not m28.get("__stub__"):
            source_quality_gate_passed = bool(m28.get("quality_gate_passed", False))
            source_register = list(m28.get("source_register", []) or [])
            contamination_log = list(m28.get("contamination_log", []) or [])
            routing_plan_compliance = dict(m28.get("routing_plan_compliance", {}) or {})
            mandatory_source_gaps = list(routing_plan_compliance.get("mandatory_sources_missing_from_executor", []) or [])
            _add_event(
                event_type="source_quality_gate",
                motor_id="motor_028",
                description=(
                    "Source discovery quality gate "
                    + ("passed." if source_quality_gate_passed else "did not pass.")
                ),
                severity=_SEV_INFO if source_quality_gate_passed else _SEV_WARNING,
                traceable_inputs={
                    "attempted_sources": (m28.get("discovery_summary", {}) or {}).get("attempted"),
                    "admitted_sources": (m28.get("discovery_summary", {}) or {}).get("admitted"),
                },
                outcome="passed" if source_quality_gate_passed else "degraded",
            )
            if source_register:
                _add_event(
                    event_type="source_scope_separation_registered",
                    motor_id="motor_028",
                    description=(
                        f"Source register built with {len(source_register)} source row(s); "
                        f"{len([row for row in source_register if row.get('accepted')])} accepted and "
                        f"{len([row for row in source_register if not row.get('accepted')])} rejected/deferred."
                    ),
                    severity=_SEV_INFO,
                    traceable_inputs={"source_register_count": len(source_register)},
                    outcome="registered",
                )
            if routing_plan_compliance:
                _add_event(
                    event_type="source_routing_plan_registered",
                    motor_id="motor_028",
                    description=(
                        f"Source routing plan compliance evaluated across {routing_plan_compliance.get('total_routed_sources', 0)} routed source(s)."
                    ),
                    severity=_SEV_INFO if not mandatory_source_gaps else _SEV_WARNING,
                    traceable_inputs={
                        "mandatory_source_gap_count": len(mandatory_source_gaps),
                        "mandatory_sources_missing_from_executor": mandatory_source_gaps,
                    },
                    outcome="passed" if not mandatory_source_gaps else "degraded",
                )
            if mandatory_source_gaps:
                _add_event(
                    event_type="mandatory_source_execution_gap",
                    motor_id="motor_028",
                    description=(
                        "Mandatory routed public source(s) were not executed by discovery: "
                        + ", ".join(mandatory_source_gaps[:6])
                    ),
                    severity=_SEV_ERROR,
                    traceable_inputs={
                        "mandatory_sources_missing_from_executor": mandatory_source_gaps,
                    },
                    outcome="missing_executor_coverage",
                )
            for entry in contamination_log:
                _add_event(
                    event_type="ingestion_contamination_detected",
                    motor_id="motor_028",
                    description=str(entry.get("detail") or entry.get("detected_issue") or "Ingestion contamination risk detected."),
                    severity=_SEV_WARNING if str(entry.get("severity", "")).strip().lower() != "high" else _SEV_ERROR,
                    traceable_inputs={"affected_field": entry.get("affected_field", "")},
                    outcome="rejected_source",
                )
        if m34 and not m34.get("__stub__"):
            variable_maturity_register = list(m34.get("variable_maturity_register", []) or [])
            claim_permission_register = list(m34.get("claim_permission_register", []) or [])
            decision_permission_register = list(m34.get("decision_permission_register", []) or [])
            report_readiness_register = dict(m34.get("report_readiness_register", {}) or {})
            _add_event(
                event_type="variable_maturity_registered",
                motor_id="motor_034",
                description=f"Evidence maturity assigned to {len(variable_maturity_register)} variable(s).",
                severity=_SEV_INFO,
                traceable_inputs={"variable_count": len(variable_maturity_register)},
                outcome="registered",
            )
            blocked_claims = [
                row for row in claim_permission_register
                if str(row.get("current_permission", "")).lower() in {"prohibited", "deferred"}
            ]
            if blocked_claims:
                _add_event(
                    event_type="claim_permission_constraints_registered",
                    motor_id="motor_034",
                    description=f"{len(blocked_claims)} claim class(es) remain blocked by variable maturity bottlenecks.",
                    severity=_SEV_WARNING,
                    traceable_inputs={"blocked_claims": [row.get('claim_name', '') for row in blocked_claims[:6]]},
                    outcome="bounded",
                )
            if report_readiness_register:
                _add_event(
                    event_type="report_readiness_registered",
                    motor_id="motor_034",
                    description=str(report_readiness_register.get("reason") or "Report readiness registered from evidence maturity engine."),
                    severity=_SEV_INFO if report_readiness_register.get("report_type_allowed") else _SEV_WARNING,
                    traceable_inputs={
                        "report_type_allowed": report_readiness_register.get("report_type_allowed", []),
                        "report_type_prohibited": report_readiness_register.get("report_type_prohibited", []),
                    },
                    outcome="registered",
                )

        m07 = inputs.get("motor_007", {})
        if m07 and not m07.get("__stub__"):
            evaluated = m07.get("evaluated_entities", [])
            fit_count = m07.get("total_fit", 0)
            total_evaluated = m07.get("total_evaluated", 0)
            fitness_rate = m07.get("fitness_rate", 0.0)
            target_scope_fitness = m07.get("target_scope_fitness", 0.0)
            target_definition = m07.get("target_definition_contract", {})
            target_admissibility_state = m07.get("target_admissibility_state", runtime.get("target_admissibility_state"))
            subject_gate_passed = bool(m07.get("subject_gate_passed", runtime.get("subject_gate_passed")))
            subject_gate_reason_register = m07.get("subject_gate_reason_register", runtime.get("subject_gate_reason_register", []))
            allowed_report_classes = m07.get("allowed_report_classes", runtime.get("allowed_report_classes", []))
            asset_context_readiness = m07.get("asset_context_readiness", runtime.get("asset_context_readiness"))
            report_identity_state = m07.get("report_identity_state", runtime.get("report_identity_state"))
            dominant_evidence_scope = m07.get("dominant_evidence_scope", runtime.get("dominant_evidence_scope"))
            missing_clusters = m07.get("missing_observable_clusters", runtime.get("missing_observable_clusters", []))

            _add_event(
                event_type="subject_admissibility_gate",
                motor_id="motor_007",
                description=(
                    f"Subject admissibility evaluated as {target_admissibility_state}; "
                    + ("asset pipeline gate passed." if subject_gate_passed else "asset pipeline gate not passed.")
                ),
                severity=_SEV_INFO if subject_gate_passed else _SEV_WARNING,
                traceable_inputs={
                    "target_admissibility_state": target_admissibility_state,
                    "allowed_report_classes": allowed_report_classes,
                },
                outcome="passed" if subject_gate_passed else "degraded",
            )
            for reason in subject_gate_reason_register:
                _add_event(
                    event_type="subject_gate_reason",
                    motor_id="motor_007",
                    description=str(reason.get("message", "Subject gate reason registered.")),
                    severity=_SEV_WARNING if reason.get("severity") != "error" else _SEV_ERROR,
                    traceable_inputs={"code": reason.get("code")},
                    outcome=reason.get("code", "reason_registered"),
                )

            asset_context_gate_passed = target_scope_fitness >= 0.67
            _add_event(
                event_type="asset_context_gate",
                motor_id="motor_007",
                description=(
                    f"Asset context gate evaluation: readiness={asset_context_readiness}, "
                    f"scope_fitness={target_scope_fitness:.2f}, entity_fit={fit_count}/{total_evaluated} "
                    f"(rate={fitness_rate:.2f})."
                ),
                severity=_SEV_INFO if asset_context_gate_passed else _SEV_WARNING,
                traceable_inputs={
                    "total_evaluated": total_evaluated,
                    "fitness_rate": fitness_rate,
                    "target_scope_fitness": target_scope_fitness,
                },
                outcome="passed" if asset_context_gate_passed else "degraded",
                extra={
                    "fitness_rate": fitness_rate,
                    "fit_count": fit_count,
                    "asset_context_readiness": asset_context_readiness,
                },
            )

            # Flag unfit entities
            unfit = [e for e in evaluated if e.get("fitness_status") == "unfit"]
            for entity in unfit:
                _add_event(
                    event_type="entity_unfit",
                    motor_id="motor_007",
                    description=(
                        f"Entity {entity.get('entity_id', 'unknown')} is unfit "
                        f"(score={entity.get('fitness_score', 0):.2f})."
                    ),
                    severity=_SEV_WARNING,
                    traceable_inputs={"entity_id": entity.get("entity_id"), "fitness_score": entity.get("fitness_score")},
                    outcome="unfit",
                )
            _add_event(
                event_type="asset_context_profile",
                motor_id="motor_007",
                description=(
                    f"Asset context readiness evaluated as {asset_context_readiness} "
                    f"for target_scope={target_definition.get('target_scope', 'unknown')}."
                ),
                severity=_SEV_INFO if asset_context_readiness in ("asset_context_operable", "asset_context_hardened") else _SEV_WARNING,
                traceable_inputs={
                    "target_scope": target_definition.get("target_scope"),
                    "target_type": target_definition.get("target_type"),
                },
                outcome=asset_context_readiness or "unknown",
                extra={
                    "report_identity_state": report_identity_state,
                    "dominant_evidence_scope": dominant_evidence_scope,
                    "missing_observable_clusters": missing_clusters,
                    "target_admissibility_state": target_admissibility_state,
                },
            )
            if not subject_gate_passed:
                _add_event(
                    event_type="subject_mismatch_detected",
                    motor_id="motor_007",
                    description=(
                        "The declared case cannot yet proceed as a bounded asset case; document identity must remain degraded."
                    ),
                    severity=_SEV_WARNING,
                    traceable_inputs={
                        "target_admissibility_state": target_admissibility_state,
                        "allowed_report_classes": allowed_report_classes,
                    },
                    outcome="degrade_report_identity",
                )
            if target_definition.get("target_scope") == "asset" and asset_context_readiness in (
                "issuer_context_only",
                "location_only",
                "asset_context_insufficient",
            ):
                _add_event(
                    event_type="technical_underpopulation_detected",
                    motor_id="motor_007",
                    description=(
                        "Asset-scoped case lacks enough physical and operational observables to justify a full technical asset-brief surface."
                    ),
                    severity=_SEV_WARNING,
                    traceable_inputs={"missing_observable_clusters": missing_clusters},
                    outcome="degrade_report_identity",
                )
            if target_definition.get("target_scope") == "asset" and dominant_evidence_scope in (
                "issuer_context_dominant",
                "mixed_scope_with_issuer_bias",
            ):
                _add_event(
                    event_type="issuer_dominance_detected",
                    motor_id="motor_007",
                    description=(
                        "Issuer-level context is dominating an asset-scoped case; no-compensation safeguards should constrain publication."
                    ),
                    severity=_SEV_WARNING,
                    traceable_inputs={"dominant_evidence_scope": dominant_evidence_scope},
                    outcome="publication_review_required",
                )
            target_classification_object = m07.get("target_classification_object", {})
            if target_classification_object:
                _add_event(
                    event_type="target_classification_registered",
                    motor_id="motor_007",
                    description=(
                        f"Target classified as {target_classification_object.get('target_type', 'UNKNOWN')} "
                        f"with confidence {target_classification_object.get('classification_confidence', 'unknown')}."
                    ),
                    severity=_SEV_INFO if subject_gate_passed else _SEV_WARNING,
                    traceable_inputs={"recommended_report_type": m07.get("recommended_report_type", "")},
                    outcome="registered",
                )
        elif m07.get("__stub__"):
            _add_event(
                event_type="stub_execution",
                motor_id="motor_007",
                description="motor_007 ran as stub — quality evaluation not performed.",
                severity=_SEV_WARNING,
                traceable_inputs={},
                outcome="stub",
            )

        m12 = inputs.get("motor_012", {})
        if m12 and not m12.get("__stub__"):
            asset_field_register = list(m12.get("asset_field_register", []) or [])
            missing_evidence_register = list(m12.get("missing_evidence_register", []) or [])
            blocking_fields = [row for row in asset_field_register if row.get("status") == "BLOCKING_FIELD"]
            if asset_field_register:
                _add_event(
                    event_type="field_admissibility_matrix_built",
                    motor_id="motor_012",
                    description=(
                        f"Asset field admissibility matrix built with {len(asset_field_register)} field row(s), "
                        f"including {len(blocking_fields)} blocking field(s)."
                    ),
                    severity=_SEV_INFO if not blocking_fields else _SEV_WARNING,
                    traceable_inputs={"asset_field_register_count": len(asset_field_register)},
                    outcome="registered",
                )
            if missing_evidence_register:
                _add_event(
                    event_type="missing_evidence_register_built",
                    motor_id="motor_012",
                    description=(
                        f"Missing evidence register built with {len(missing_evidence_register)} critical request item(s)."
                    ),
                    severity=_SEV_WARNING,
                    traceable_inputs={"missing_evidence_count": len(missing_evidence_register)},
                    outcome="registered",
                )

        # ── 4. Source change events (motor_009, via inputs chain) ──────────────
        m09 = inputs.get("motor_009", {})
        if m09 and not m09.get("__stub__"):
            change_events = m09.get("change_detection_events", [])
            new_sources = m09.get("new_sources", 0)
            updated_sources = m09.get("updated_sources", 0)

            _add_event(
                event_type="motor_completed",
                motor_id="motor_009",
                description=(
                    f"Source change detection: {new_sources} new, {updated_sources} updated, "
                    f"{m09.get('unchanged_sources', 0)} unchanged."
                ),
                severity=_SEV_INFO if (new_sources + updated_sources) == 0 else _SEV_WARNING,
                traceable_inputs={"total_events": m09.get("total_events", 0)},
                outcome="completed",
                extra={"new_sources": new_sources, "updated_sources": updated_sources},
            )

            if new_sources > 0 or updated_sources > 0:
                _add_event(
                    event_type="source_change_detected",
                    motor_id="motor_009",
                    description=(
                        f"{new_sources + updated_sources} source(s) changed — "
                        "downstream inference cases may need re-evaluation."
                    ),
                    severity=_SEV_WARNING,
                    traceable_inputs={"changed_sources": new_sources + updated_sources},
                    outcome="re_evaluation_required",
                )
        elif m09 and m09.get("__stub__"):
            _add_event(
                event_type="stub_execution",
                motor_id="motor_009",
                description="motor_009 ran as stub — source change detection not performed.",
                severity=_SEV_WARNING,
                traceable_inputs={},
                outcome="stub",
            )

        # ── 5. Claim activation events (motor_013, via inputs chain) ───────────
        m13 = inputs.get("motor_013", {})
        if m13 and not m13.get("__stub__"):
            activation_log = m13.get("activation_log", [])
            total_activated = m13.get("total_activated", 0)
            total_latent = m13.get("total_latent", 0)

            _add_event(
                event_type="claim_activation",
                motor_id="motor_013",
                description=(
                    f"Inference case activation: {total_activated}/{total_latent} cases activated "
                    f"(rate={m13.get('activation_rate', 0):.2f})."
                ),
                severity=_SEV_INFO,
                traceable_inputs={"total_latent": total_latent, "facility_prior_id": m13.get("facility_prior_id")},
                outcome="completed",
                extra={
                    "total_activated": total_activated,
                    "cases_by_family": m13.get("cases_by_family", {}),
                },
            )

            # Log each non-activated case as info
            not_activated = [a for a in activation_log if a.get("status") == "not_activated"]
            if not_activated:
                _add_event(
                    event_type="cases_not_activated",
                    motor_id="motor_013",
                    description=f"{len(not_activated)} latent case(s) did not activate (triggers not satisfied).",
                    severity=_SEV_INFO,
                    traceable_inputs={"case_ids": [a.get("case_id") for a in not_activated]},
                    outcome="not_activated",
                )
        elif m13 and m13.get("__stub__"):
            _add_event(
                event_type="stub_execution",
                motor_id="motor_013",
                description="motor_013 ran as stub — claim activation not performed.",
                severity=_SEV_WARNING,
                traceable_inputs={},
                outcome="stub",
            )

        # ── 6. Score computation events (motor_014, via inputs chain) ──────────
        m14 = inputs.get("motor_014", {})
        if m14 and not m14.get("__stub__"):
            inference_records = m14.get("inference_records", [])
            conflicts = m14.get("conflict_register", [])
            tensions = m14.get("tension_records", [])
            opps = m14.get("opportunity_candidates", [])
            gaps = m14.get("evidence_gap_register", [])

            _add_event(
                event_type="score_computation",
                motor_id="motor_014",
                description=(
                    f"Decision Core scoring: {len(inference_records)} records scored. "
                    f"Conflicts: {len(conflicts)}, Tensions: {len(tensions)}, "
                    f"Opportunities: {len(opps)}, Evidence gaps: {len(gaps)}."
                ),
                severity=_SEV_INFO if not conflicts else _SEV_WARNING,
                traceable_inputs={"inference_records": len(inference_records)},
                outcome="completed",
                extra={
                    "blocking_conflicts": len(conflicts),
                    "open_tensions": len(tensions),
                    "composite_reading": m14.get("composite_reading", {}).get("decision_state", ""),
                },
            )

            # Log blocking conflicts as errors
            for conflict in conflicts:
                _add_event(
                    event_type="blocking_conflict_registered",
                    motor_id="motor_014",
                    description=f"BLOCKING CONFLICT: {conflict.get('conflict_id')} — {conflict.get('conflict_name')}",
                    severity=_SEV_ERROR,
                    traceable_inputs={"conflict_id": conflict.get("conflict_id"), "case_id": conflict.get("inference_case_id")},
                    outcome="blocking",
                    extra={"blocking_status": conflict.get("blocking_status", "")},
                )
        elif m14 and m14.get("__stub__"):
            _add_event(
                event_type="stub_execution",
                motor_id="motor_014",
                description="motor_014 ran as stub — Decision Core scoring not performed.",
                severity=_SEV_WARNING,
                traceable_inputs={},
                outcome="stub",
            )

        # ── 7. Scan runtime truth and inputs for stub / partial executions ─────
        stub_register: list[dict] = []
        seen_stub_motors: set[str] = set()
        for runtime_mid, runtime_entry in runtime_results.items():
            if not isinstance(runtime_entry, dict):
                continue
            truth_state = runtime_entry.get("truth_state", "")
            if truth_state not in ("stub", "cached_stub", "completed_stub"):
                continue
            stub_reason = (
                "placeholder_contract"
                if runtime_entry.get("implementation_state") == "placeholder"
                else "runtime_stub_output"
            )
            stub_register.append({
                "motor_id": runtime_mid,
                "stub_reason": stub_reason,
                "inputs_received": [],
                "truth_state": truth_state,
                "implementation_state": runtime_entry.get("implementation_state", ""),
            })
            seen_stub_motors.add(runtime_mid)
            _add_event(
                event_type="stub_execution",
                motor_id=runtime_mid,
                description=f"{runtime_mid} recorded as {truth_state} in runtime truth.",
                severity=_SEV_WARNING,
                traceable_inputs={"stub_motor": runtime_mid, "truth_state": truth_state},
                outcome="stub",
            )
        for input_key, input_val in inputs.items():
            if input_key.startswith("__"):
                continue
            if isinstance(input_val, dict) and input_val.get("__stub__"):
                if input_key in seen_stub_motors:
                    continue
                stub_register.append({
                    "motor_id": input_key,
                    "stub_reason": input_val.get("reason", "not_implemented"),
                    "inputs_received": input_val.get("input_motor_ids_received", []),
                    "truth_state": "stub",
                })
                _add_event(
                    event_type="stub_execution",
                    motor_id=input_key,
                    description=f"{input_key} ran as stub: {input_val.get('reason', 'not implemented')}",
                    severity=_SEV_WARNING,
                    traceable_inputs={"stub_motor": input_key},
                    outcome="stub",
                )

        for runtime_mid, runtime_entry in runtime_results.items():
            if not isinstance(runtime_entry, dict):
                continue
            if runtime_entry.get("status", "") != "failed":
                continue
            _add_event(
                event_type="motor_failed",
                motor_id=runtime_mid,
                description=f"{runtime_mid} failed during pipeline execution.",
                severity=_SEV_ERROR,
                traceable_inputs={"truth_state": runtime_entry.get("truth_state", "")},
                outcome="failed",
                extra={"error": runtime_entry.get("error", "")},
            )

        # ── 8. Evidence coverage gap events ────────────────────────────────────
        m12 = inputs.get("motor_012", {})
        m20 = inputs.get("motor_020", {})
        traceability_missing_segments: list[str] = []
        if m12 and not m12.get("__stub__"):
            fp = m12.get("facility_prior", {})
            uncertainty_markers = fp.get("uncertainty_markers", [])
            if uncertainty_markers:
                _add_event(
                    event_type="evidence_coverage_gap",
                    motor_id="motor_012",
                    description=(
                        f"{len(uncertainty_markers)} uncertainty marker(s) in facility_prior. "
                        "These represent known evidence gaps for this analysis run."
                    ),
                    severity=_SEV_WARNING,
                    traceable_inputs={"marker_count": len(uncertainty_markers)},
                    outcome="documented",
                    extra={
                        "uncertainty_dimensions": [m.get("dimension") for m in uncertainty_markers],
                    },
                )
            evidence_lineage = m12.get("evidence_lineage", fp.get("evidence_lineage", {}))
            if evidence_lineage:
                _add_event(
                    event_type="traceability_registered",
                    motor_id="motor_012",
                    description="Source-to-facility_prior evidence lineage registered.",
                    severity=_SEV_INFO,
                    traceable_inputs={"lineage_id": evidence_lineage.get("lineage_id", "")},
                    outcome="registered",
                )
            else:
                traceability_missing_segments.append("motor_012.evidence_lineage")
                _add_event(
                    event_type="traceability_gap",
                    motor_id="motor_012",
                    description="facility_prior produced without evidence_lineage.",
                    severity=_SEV_ERROR,
                    traceable_inputs={"facility_prior_id": fp.get("facility_prior_id", "")},
                    outcome="missing_traceability",
                )
            compliance_case = m12.get("compliance_applicability_case", fp.get("compliance_applicability_case", {}))
            if compliance_case:
                posture = compliance_case.get("compliance_posture_state", "")
                applicability = compliance_case.get("applicability_state", "")
                _add_event(
                    event_type="regulatory_screening_registered",
                    motor_id="motor_012",
                    description=(
                        f"Regulatory applicability screening registered with posture={posture} "
                        f"and applicability_state={applicability}."
                    ),
                    severity=_SEV_INFO,
                    traceable_inputs={"primary_regulation": compliance_case.get("jurisdiction_trace_record", {}).get("primary_regulation", "")},
                    outcome="registered",
                    extra={
                        "regulatory_posture_state": posture,
                        "applicability_state": applicability,
                    },
                )
                if posture in {"trigger_plausible", "trigger_partially_supported", "applicability_likely", "compliance_open"}:
                    _add_event(
                        event_type="regulatory_posture_open",
                        motor_id="motor_012",
                        description="Regulatory posture remains open — compliance closure is not admissible from current public data.",
                        severity=_SEV_WARNING,
                        traceable_inputs={"primary_regulation": compliance_case.get("jurisdiction_trace_record", {}).get("primary_regulation", "")},
                        outcome="open",
                    )

        # ── 8b. Traceability propagation events ───────────────────────────────
        m14_lineage = m14.get("decision_core_lineage", {}) if isinstance(m14, dict) else {}
        if m14 and not m14.get("__stub__"):
            if m14_lineage:
                _add_event(
                    event_type="traceability_registered",
                    motor_id="motor_014",
                    description="facility_prior-to-decision_core lineage registered.",
                    severity=_SEV_INFO,
                    traceable_inputs={"lineage_id": m14_lineage.get("lineage_id", "")},
                    outcome="registered",
                )
            else:
                traceability_missing_segments.append("motor_014.decision_core_lineage")
                _add_event(
                    event_type="traceability_gap",
                    motor_id="motor_014",
                    description="Decision Core output missing decision_core_lineage.",
                    severity=_SEV_ERROR,
                    traceable_inputs={"facility_prior_id": m14.get("facility_prior_id", "")},
                    outcome="missing_traceability",
                )

        m15 = inputs.get("motor_015", {})
        if m15 and not m15.get("__stub__"):
            traceability_register = m15.get("traceability_register", {})
            if traceability_register:
                _add_event(
                    event_type="traceability_registered",
                    motor_id="motor_015",
                    description="Decision Core-to-output block traceability register present.",
                    severity=_SEV_INFO,
                    traceable_inputs={"traceability_id": traceability_register.get("traceability_id", "")},
                    outcome="registered",
                )
            else:
                traceability_missing_segments.append("motor_015.traceability_register")
                _add_event(
                    event_type="traceability_gap",
                    motor_id="motor_015",
                    description="Output blocks produced without traceability_register.",
                    severity=_SEV_ERROR,
                    traceable_inputs={"facility_prior_id": m15.get("facility_prior_id", "")},
                    outcome="missing_traceability",
                )

        m16 = inputs.get("motor_016", {})
        if m16 and not m16.get("__stub__"):
            report_package = m16.get("report_package", {})
            report_traceability = report_package.get("report_traceability", {})
            context_integrity_scan = report_package.get("context_integrity_scan", {})
            if report_traceability:
                _add_event(
                    event_type="traceability_registered",
                    motor_id="motor_016",
                    description="Report package includes report_traceability metadata.",
                    severity=_SEV_INFO,
                    traceable_inputs={"report_traceability_id": report_traceability.get("report_traceability_id", "")},
                    outcome="registered",
                )
            else:
                traceability_missing_segments.append("motor_016.report_package.report_traceability")
                _add_event(
                    event_type="traceability_gap",
                    motor_id="motor_016",
                    description="Report package missing report_traceability metadata.",
                    severity=_SEV_ERROR,
                    traceable_inputs={"package_id": report_package.get("package_id", "")},
                    outcome="missing_traceability",
                )
            report_product_state = report_package.get("report_product_state", "")
            document_type = report_package.get("document_type", "")
            mandatory_body_sections = report_package.get("mandatory_body_sections", [])
            if report_product_state == "decision_admissibility":
                required_titles = {
                    "Executive Decision-Admissibility Brief",
                    "Asset Context Readiness",
                    "Investment Uncertainty Map",
                    "Minimum Evidence Pack",
                    "Scenario Space Under Current Uncertainty",
                    "Blocking Conflicts",
                    "Inference Case Register",
                    "Regulatory / Normative Screening",
                    "TAD — Decision-Admissibility Layer",
                    "Next Best Questions",
                }
                missing_titles = sorted(required_titles - set(mandatory_body_sections))
                if missing_titles:
                    _add_event(
                        event_type="mandatory_section_missing",
                        motor_id="motor_016",
                        description="Decision-admissibility report package is missing mandatory body sections.",
                        severity=_SEV_ERROR,
                        traceable_inputs={"missing_titles": missing_titles, "document_type": document_type},
                        outcome="degraded",
                    )
                else:
                    _add_event(
                        event_type="mandatory_sections_registered",
                        motor_id="motor_016",
                        description="Decision-admissibility report package includes mandatory body sections.",
                        severity=_SEV_INFO,
                        traceable_inputs={"document_type": document_type},
                        outcome="registered",
                    )
            if context_integrity_scan:
                if context_integrity_scan.get("render_eligible", True):
                    _add_event(
                        event_type="context_integrity_passed",
                        motor_id="motor_016",
                        description="Report content integrity scan passed before rendering.",
                        severity=_SEV_INFO,
                        traceable_inputs={"issue_count": context_integrity_scan.get("issue_count", 0)},
                        outcome="passed",
                    )
                else:
                    for issue in context_integrity_scan.get("issues", []):
                        _add_event(
                            event_type="context_contamination_detected",
                            motor_id="motor_016",
                            description=issue.get("message", "Context integrity issue detected."),
                            severity=_SEV_ERROR,
                            traceable_inputs={
                                "issue_code": issue.get("issue_code", ""),
                                "section_id": issue.get("section_id", ""),
                                "matched_text": issue.get("matched_text", ""),
                            },
                            outcome="blocked",
                        )

        m19 = inputs.get("motor_019", {})
        if m19 and not m19.get("__stub__"):
            llm_summary = m19.get("llm_governance_summary", {})
            sections_rendered = llm_summary.get("sections_rendered", m19.get("total_sections_written", 0))
            fallback_sections = llm_summary.get("fallback_sections", 0)
            lint_failures = llm_summary.get("lint_failures", 0)
            budget_exhausted = llm_summary.get("budget_exhausted", False)
            _add_event(
                event_type="llm_render_registered",
                motor_id="motor_019",
                description=f"LLM narrative layer rendered {sections_rendered} section(s).",
                severity=_SEV_INFO if fallback_sections == 0 and lint_failures == 0 else _SEV_WARNING,
                traceable_inputs={"sections_rendered": sections_rendered},
                outcome="completed",
                extra={
                    "fallback_sections": fallback_sections,
                    "lint_failures": lint_failures,
                },
            )
            if fallback_sections > 0:
                _add_event(
                    event_type="llm_fallback_registered",
                    motor_id="motor_019",
                    description=f"{fallback_sections} section(s) used deterministic fallback instead of free LLM prose.",
                    severity=_SEV_WARNING,
                    traceable_inputs={"fallback_sections": fallback_sections},
                    outcome="degraded",
                )
            if lint_failures > 0:
                _add_event(
                    event_type="llm_policy_breach_blocked",
                    motor_id="motor_019",
                    description=f"{lint_failures} section(s) failed LLM policy lint and were downgraded before publication.",
                    severity=_SEV_WARNING,
                    traceable_inputs={"lint_failures": lint_failures},
                    outcome="degraded",
                )
            if budget_exhausted:
                _add_event(
                    event_type="llm_budget_exhausted",
                    motor_id="motor_019",
                    description="LLM writing budget exhausted before all requested sections were freely rendered.",
                    severity=_SEV_WARNING,
                    traceable_inputs={"sections_rendered": sections_rendered},
                    outcome="degraded",
                )

        # ── 8c. Belief revision / propagation consequences ───────────────────
        if m20 and not m20.get("__stub__"):
            belief_revisions = m20.get("belief_revision_register", [])
            publication_consequences = m20.get("publication_consequence_register", [])
            if belief_revisions:
                _add_event(
                    event_type="belief_revision_registered",
                    motor_id="motor_020",
                    description=f"{len(belief_revisions)} belief revision event(s) registered for downstream review.",
                    severity=_SEV_WARNING,
                    traceable_inputs={"affected_case_count": m20.get("affected_case_count", len(belief_revisions))},
                    outcome="registered",
                )
            for consequence in publication_consequences:
                pub_cons = consequence.get("publication_consequence", "")
                severity = _SEV_WARNING if pub_cons in {"hold_for_validation", "publish_with_degradation"} else _SEV_ERROR if pub_cons == "freeze_publication" else _SEV_INFO
                outcome = "freeze_recommended" if pub_cons == "freeze_publication" else pub_cons or "registered"
                _add_event(
                    event_type="publication_consequence_registered",
                    motor_id="motor_020",
                    description=(
                        f"Propagation consequence {pub_cons} registered for output {consequence.get('output_id', '')}."
                    ),
                    severity=severity,
                    traceable_inputs={"output_id": consequence.get("output_id", ""), "case_id": consequence.get("case_id", "")},
                    outcome=outcome,
                )

        # ── 9. Deliverable readiness events (motor_017 / motor_027) ──────────
        m17 = inputs.get("motor_017", {})
        m27 = inputs.get("motor_027", {})
        final_report_ready = True
        if m17:
            pdf_path = str(m17.get("pdf_path", "") or "")
            m17_ok = m17.get("compilation_status") == "success" and bool(pdf_path)
            _add_event(
                event_type="render_status",
                motor_id="motor_017",
                description="Document rendering completed successfully." if m17_ok else "Document rendering did not produce a usable PDF.",
                severity=_SEV_INFO if m17_ok else _SEV_ERROR,
                traceable_inputs={"pdf_path": pdf_path},
                outcome="completed" if m17_ok else "incomplete",
            )
            final_report_ready = final_report_ready and m17_ok
        if m27:
            output_path = str(
                m27.get("output_path", "")
                or m27.get("pdf_output_path", "")
                or m27.get("pdf_source_path", "")
                or ""
            )
            delivered = bool(m27.get("delivered"))
            m27_ok = delivered and bool(output_path)
            _add_event(
                event_type="delivery_status",
                motor_id="motor_027",
                description="Artifact delivery completed successfully." if m27_ok else "Artifact delivery did not produce a final deliverable.",
                severity=_SEV_INFO if m27_ok else _SEV_ERROR,
                traceable_inputs={"output_path": output_path},
                outcome="completed" if m27_ok else "incomplete",
            )
            delivery_manifest = m27.get("delivery_manifest", {})
            if m27_ok and delivery_manifest.get("traceability_summary"):
                _add_event(
                    event_type="traceability_registered",
                    motor_id="motor_027",
                    description="Delivery manifest includes traceability summary.",
                    severity=_SEV_INFO,
                    traceable_inputs={"output_path": output_path, "report_traceability_id": delivery_manifest.get("traceability_summary", {}).get("report_traceability_id", "")},
                    outcome="registered",
                )
            elif m27_ok:
                traceability_missing_segments.append("motor_027.delivery_manifest.traceability_summary")
                _add_event(
                    event_type="traceability_gap",
                    motor_id="motor_027",
                    description="Delivered artifact missing traceability summary in delivery manifest.",
                    severity=_SEV_ERROR,
                    traceable_inputs={"output_path": output_path},
                    outcome="missing_traceability",
                )
            final_report_ready = final_report_ready and m27_ok

        # ── Compute pipeline health summary ────────────────────────────────────
        error_events = [e for e in events if e["severity"] in (_SEV_ERROR, _SEV_CRITICAL)]
        warning_events = [e for e in events if e["severity"] == _SEV_WARNING]
        source_quality_events = [e for e in events if e["event_type"] == "source_quality_gate"]
        source_quality_gate_passed = all(
            e.get("outcome") == "passed" for e in source_quality_events
        ) if source_quality_events else True
        subject_gate_events = [e for e in events if e["event_type"] == "subject_admissibility_gate"]
        subject_gate_passed = all(
            e.get("outcome") == "passed" for e in subject_gate_events
        ) if subject_gate_events else bool(runtime.get("subject_gate_passed", False))
        asset_context_gate_events = [e for e in events if e["event_type"] == "asset_context_gate"]
        asset_context_gate_passed = all(
            e.get("outcome") == "passed" for e in asset_context_gate_events
        ) if asset_context_gate_events else True
        quality_gate_passed = all(
            e.get("outcome") == "passed" for e in quality_events
        ) if (quality_events := source_quality_events) else True
        m19_summary = inputs.get("motor_019", {}).get("llm_governance_summary", {}) if isinstance(inputs.get("motor_019", {}), dict) else {}
        report_preflight_register = _build_report_preflight_register(
            m14 if isinstance(m14, dict) else {},
            inputs.get("motor_016", {}) if isinstance(inputs.get("motor_016", {}), dict) else {},
            m34 if isinstance(m34, dict) else {},
            m36 if isinstance(m36, dict) else {},
        )
        phase_self_evaluation_register = _build_phase_self_evaluation_register(
            pipeline if isinstance(pipeline, dict) else {},
            m07 if isinstance(m07, dict) else {},
            m12 if isinstance(m12, dict) else {},
            m14 if isinstance(m14, dict) else {},
            m28 if isinstance(m28, dict) else {},
            inputs.get("motor_033", {}) if isinstance(inputs.get("motor_033", {}), dict) else {},
            m34 if isinstance(m34, dict) else {},
            report_preflight_register,
        )
        source_yield_memory_register = build_source_yield_memory(
            list((m28 or {}).get("source_family_coverage_table", []) or []),
            dict(runtime.get("previous_run_summary", {}) or {}),
        )
        case_delta_register = build_case_delta_register(
            runtime if isinstance(runtime, dict) else {},
            m20 if isinstance(m20, dict) else {},
            m28 if isinstance(m28, dict) else {},
            m34 if isinstance(m34, dict) else {},
            report_preflight_register,
            phase_self_evaluation_register,
        )
        next_ingestion_priority_update = build_next_ingestion_priority_update(
            m12 if isinstance(m12, dict) else {},
            m14 if isinstance(m14, dict) else {},
            m20 if isinstance(m20, dict) else {},
            m28 if isinstance(m28, dict) else {},
            case_delta_register,
            source_yield_memory_register,
        )
        ingestion_learning_register = build_ingestion_learning_register(
            runtime if isinstance(runtime, dict) else {},
            case_delta_register,
            source_yield_memory_register,
            next_ingestion_priority_update,
            report_preflight_register,
            m20 if isinstance(m20, dict) else {},
        )
        if report_preflight_register.get("passed"):
            _add_event(
                event_type="report_preflight_registered",
                motor_id="motor_024",
                description="Report preflight passed all critical consistency and lint checks.",
                severity=_SEV_INFO,
                traceable_inputs={"check_count": len(report_preflight_register.get("checks", []))},
                outcome="passed",
            )
        else:
            _add_event(
                event_type="report_preflight_failed",
                motor_id="motor_024",
                description="Report preflight found critical consistency or lint failures before PDF publication.",
                severity=_SEV_ERROR,
                traceable_inputs={"critical_failures": report_preflight_register.get("critical_failures", [])[:4]},
                outcome="hold_for_validation",
            )
        _add_event(
            event_type="phase_self_evaluation_registered",
            motor_id="motor_024",
            description="Per-run self-evaluation register generated for current report hardening phases.",
            severity=_SEV_INFO,
            traceable_inputs={
                "overall_result": phase_self_evaluation_register.get("summary", {}).get("overall_result", ""),
                "resolved": phase_self_evaluation_register.get("summary", {}).get("resolved", 0),
                "partially_resolved": phase_self_evaluation_register.get("summary", {}).get("partially_resolved", 0),
                "unresolved": phase_self_evaluation_register.get("summary", {}).get("unresolved", 0),
            },
            outcome=phase_self_evaluation_register.get("summary", {}).get("overall_result", "unknown"),
        )
        _add_event(
            event_type="ingestion_learning_registered",
            motor_id="motor_024",
            description="Cross-run ingestion learning register updated with case delta, source yield memory, and next-ingestion priorities.",
            severity=_SEV_INFO,
            traceable_inputs={
                "previous_run_id": ingestion_learning_register.get("summary", {}).get("previous_run_id", ""),
                "net_progress_state": ingestion_learning_register.get("summary", {}).get("net_progress_state", ""),
                "priority_count": ingestion_learning_register.get("summary", {}).get("priority_count", 0),
            },
            outcome=ingestion_learning_register.get("summary", {}).get("net_progress_state", "initial_run"),
        )
        final_report_ready = final_report_ready and bool(report_preflight_register.get("passed", False))

        # Coverage completeness: rough estimate based on stub count
        total_known_motors = max(len(runtime_results), 34)
        stubs_active = len(stub_register)
        coverage_completeness = round((total_known_motors - stubs_active) / total_known_motors, 2)

        m34_summary = m34.get("maturity_summary", {}) if isinstance(m34.get("maturity_summary", {}), dict) else {}
        claim_permission_register = list(m34.get("claim_permission_register", []) or [])
        decision_permission_register = list(m34.get("decision_permission_register", []) or [])
        report_readiness_register = dict(m34.get("report_readiness_register", {}) or {})
        blocked_claim_count = len(
            [
                row for row in claim_permission_register
                if str(row.get("current_permission", "")).lower() in {"prohibited", "deferred"}
            ]
        )

        pipeline_health = {
            "total_events": len(events),
            "errors": len(error_events),
            "warnings": len(warning_events),
            "stubs_active": stubs_active,
            "quality_gate_passed": quality_gate_passed,
            "source_quality_gate_passed": source_quality_gate_passed,
            "subject_gate_passed": subject_gate_passed,
            "asset_context_gate_passed": asset_context_gate_passed,
            "coverage_completeness": coverage_completeness,
            "blocking_conflicts": len(
                [e for e in events if e["event_type"] == "blocking_conflict_registered"]
            ),
            "belief_revision_events": len(
                [e for e in events if e["event_type"] == "belief_revision_registered"]
            ),
            "llm_fallback_sections": m19_summary.get("fallback_sections", 0),
            "llm_lint_failures": m19_summary.get("lint_failures", 0),
            "llm_budget_exhausted": bool(m19_summary.get("budget_exhausted", False)),
            "report_preflight_passed": bool(report_preflight_register.get("passed", False)),
            "report_preflight_critical_failure_count": int(report_preflight_register.get("critical_failure_count", 0) or 0),
            "report_preflight_failures": list(report_preflight_register.get("critical_failures", []) or []),
            "phase_self_evaluation_summary": dict(phase_self_evaluation_register.get("summary", {}) or {}),
            "previous_run_id": ingestion_learning_register.get("summary", {}).get("previous_run_id", ""),
            "case_delta_net_progress_state": case_delta_register.get("net_progress_state", ""),
            "source_yield_productive_count": int(source_yield_memory_register.get("productive_source_count", 0) or 0),
            "source_yield_low_count": len(source_yield_memory_register.get("low_yield_sources", []) or []),
            "next_ingestion_priority_count": int(next_ingestion_priority_update.get("priority_count", 0) or 0),
            "next_ingestion_top_priority_action": next_ingestion_priority_update.get("top_priority_action", ""),
            "publication_freeze_recommended": any(
                e["event_type"] == "publication_consequence_registered"
                and e.get("outcome") == "freeze_recommended"
                for e in events
            ),
            "regulatory_open_cases": len(
                [e for e in events if e["event_type"] == "regulatory_posture_open"]
            ),
            "final_report_ready": final_report_ready,
            "traceability_chain_complete": len(traceability_missing_segments) == 0,
            "traceability_missing_segments": traceability_missing_segments,
            "target_scope": m07.get("target_definition_contract", {}).get("target_scope", runtime.get("target_definition", {}).get("target_scope")),
            "target_type": m07.get("target_definition_contract", {}).get("target_type", runtime.get("target_definition", {}).get("target_type")),
            "target_admissibility_state": m07.get("target_admissibility_state", runtime.get("target_admissibility_state")),
            "allowed_report_classes": m07.get("allowed_report_classes", runtime.get("allowed_report_classes", [])),
            "asset_context_readiness": m07.get("asset_context_readiness", runtime.get("asset_context_readiness")),
            "report_identity_state": m07.get("report_identity_state", runtime.get("report_identity_state")),
            "dominant_evidence_scope": m07.get("dominant_evidence_scope", runtime.get("dominant_evidence_scope")),
            "missing_observable_clusters": m07.get("missing_observable_clusters", runtime.get("missing_observable_clusters", [])),
            "target_classification_object": m07.get("target_classification_object", {}),
            "recommended_report_type": m07.get("recommended_report_type", runtime.get("recommended_report_type")),
            "prohibited_report_types": m07.get("prohibited_report_types", runtime.get("prohibited_report_types", [])),
            "source_register_count": len(m28.get("source_register", []) or []),
            "accepted_source_count": len([row for row in (m28.get("source_register", []) or []) if row.get("accepted")]),
            "rejected_source_count": len([row for row in (m28.get("source_register", []) or []) if not row.get("accepted")]),
            "routing_plan_total": int((m28.get("routing_plan_compliance", {}) or {}).get("total_routed_sources", 0) or 0),
            "mandatory_source_gap_count": len(((m28.get("routing_plan_compliance", {}) or {}).get("mandatory_sources_missing_from_executor", []) or [])),
            "mandatory_sources_missing_from_executor": list(((m28.get("routing_plan_compliance", {}) or {}).get("mandatory_sources_missing_from_executor", []) or [])),
            "routing_plan_gate_passed": len(((m28.get("routing_plan_compliance", {}) or {}).get("mandatory_sources_missing_from_executor", []) or [])) == 0,
            "contamination_log_count": len(m28.get("contamination_log", []) or []),
            "asset_field_register_count": len(m12.get("asset_field_register", []) or []),
            "missing_evidence_count": len(m12.get("missing_evidence_register", []) or []),
            "blocking_field_count": len([row for row in (m12.get("asset_field_register", []) or []) if row.get("status") == "BLOCKING_FIELD"]),
            "variable_maturity_count": len(m34.get("variable_maturity_register", []) or []),
            "claim_permission_block_count": blocked_claim_count,
            "decision_permission_count": len(decision_permission_register),
            "key_variable_bottlenecks": list(m34_summary.get("key_bottlenecks", [])),
            "report_readiness_allowed": report_readiness_register.get("report_type_allowed", []),
            "report_readiness_prohibited": report_readiness_register.get("report_type_prohibited", []),
            "report_readiness_reason": report_readiness_register.get("reason", ""),
            "subject_mismatch_detected": any(
                e["event_type"] == "subject_mismatch_detected" for e in events
            ),
            "technical_underpopulation_detected": any(
                e["event_type"] == "technical_underpopulation_detected" for e in events
            ),
            "issuer_dominance_detected": any(
                e["event_type"] == "issuer_dominance_detected" for e in events
            ),
            "mandatory_section_missing_detected": any(
                e["event_type"] == "mandatory_section_missing" for e in events
            ),
            "context_contamination_detected": any(
                e["event_type"] == "context_contamination_detected" for e in events
            ),
            "implemented_contract": runtime_truth.get("implemented_contract", 0),
            "placeholder_contract": runtime_truth.get("placeholder_contract", 0),
            "completed_real": runtime_truth.get("completed_real", 0),
            "cached_real": runtime_truth.get("cached_real", 0),
            "cached_stub": runtime_truth.get("cached_stub", 0),
        }

        # Sort events by event_type for deterministic ordering
        sorted_events = sorted(events, key=lambda e: (e.get("event_type", ""), e.get("event_id", "")))

        audit_id = _audit_hash(sorted_events)

        return {
            "governance_event_log": sorted_events,
            "exception_register": error_events,
            "stub_execution_register": stub_register,
            "pipeline_health_summary": pipeline_health,
            "report_preflight_register": report_preflight_register,
            "phase_self_evaluation_register": phase_self_evaluation_register,
            "case_delta_register": case_delta_register,
            "source_yield_memory_register": source_yield_memory_register,
            "next_ingestion_priority_update": next_ingestion_priority_update,
            "ingestion_learning_register": ingestion_learning_register,
            "runtime_truth_summary": runtime_truth,
            "runtime_motor_results": runtime_results,
            "audit_trail_id": audit_id,
            "total_events": len(sorted_events),
            "produced_at": produced_at,
        }
