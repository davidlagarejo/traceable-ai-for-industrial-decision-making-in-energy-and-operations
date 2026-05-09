"""Adapter for motor_016 — Report Package Assembly Engine.

Assembles a governed asset brief from:
  - motor_015: output blocks (Phase 3 governed)
  - motor_014: inference records and all analytical objects
  - motor_012: facility_prior (systems, energy, regulatory)
  - motor_019: LLM-written narratives (one per section, no duplicates)
  - motor_028: live financial data (SEC EDGAR)
  - motor_018: chart assets (optional)

Phase 3 section architecture:
  C1  Framework Context & Executive Brief
  C2  Operational Identity
  C3  Blocking Conflicts               [epistemic: BLOCKING_CONFLICT]
  C4  Inference Case Map               [epistemic: INFERRED]
  C5  Energy Profile & Normative Constraints  [epistemic: HYPOTHESIS | REQUIRES_VALIDATION]
  C6  Tension Map                      [epistemic: INFERRED]
  C7  Validation Architecture          [epistemic: REQUIRES_VALIDATION]
  C8  Conditional Opportunities        [epistemic: CONDITIONAL]
  C9  Financial Context                [epistemic: DIRECT_EVIDENCE | CONSOLIDATED]
  A1  Evidence & Source Traceability   [appendix]
  A2  Facility Prior                   [appendix]
  A3  Priority Questions               [appendix]

Phase 3 law:
  - No visible section may say more than upstream output_blocks support.
  - Epistemic inheritance mandatory: each section carries epistemic_marker.
  - LLM narrative is embedded per section with English and Spanish variants.
  - Financial data is subordinated context: always last body chapter (C9).
  - Blocking conflicts are always third chapter (C3) — high visibility by contract.
"""
from __future__ import annotations

import hashlib
import re
from datetime import datetime, timezone
from typing import Any

from ..asset_contracts import derive_effective_case_id
from ..congruence_intelligence.case_isolation import (
    build_case_namespace_register,
    build_chart_case_match_register,
    build_cross_case_contamination_scan,
    stamp_chart_asset_case_context,
)
from ..congruence_intelligence.empty_section_policy import (
    apply_empty_section_policy,
    build_empty_section_policy_register,
    build_section_explanation_fallback_register,
    build_section_population_status_register,
)
from ..output_taxonomy import canonicalize_output_mode
from ..render_section_contract import (
    STRUCTURAL_PRIMARY_OUTPUT_MODES,
    get_support_chart_lane_curation_policy,
    get_support_chart_lane_visibility_policy,
    get_support_chart_visibility_policy,
    resolve_render_section_contract,
)
from ..public_data_routing.asset_type_router import route_for_asset_type
from ..zlab_skill.runtime_bridge import (
    build_skill_first_runtime_analysis_registers,
    build_skill_first_package_support_context,
    build_skill_first_report_package_context,
)
from .base import BaseMotorAdapter


def _find_block(blocks: list[dict], block_type: str) -> dict:
    return next((b for b in blocks if b.get("block_type") == block_type), {})


def _fmt_usd(v) -> str:
    if v is None:
        return "NOT OBSERVED"
    if abs(v) >= 1e9:
        return f"${v/1e9:.2f}B"
    if abs(v) >= 1e6:
        return f"${v/1e6:.1f}M"
    return f"${v:,.0f}"


def _field_priority_score(row: dict[str, Any]) -> int:
    score = 0
    if str(row.get("status", "")).strip() == "OBSERVED":
        score += 5
    if str(row.get("scope", "")).strip() == "ASSET_LEVEL":
        score += 4
    if str(row.get("admissibility", "")).strip() == "CONFIRMED_ASSET_LEVEL":
        score += 4
    if bool(row.get("physical_substrate_supported")):
        score += 3
    if bool(row.get("operating_substrate_supported")):
        score += 3
    if bool(row.get("regulatory_supported")):
        score += 2
    if bool(row.get("identity_supported")):
        score += 1
    authority = str(row.get("authority_score", "")).strip().lower()
    if authority == "high":
        score += 2
    elif authority == "medium":
        score += 1
    return score


def _best_asset_field_row(
    asset_field_register: list[dict[str, Any]],
    *field_names: str,
) -> dict[str, Any]:
    names = {str(name).strip().lower() for name in field_names if str(name).strip()}
    candidates = [
        row
        for row in asset_field_register
        if str(row.get("field", "")).strip().lower() in names
    ]
    if not candidates:
        return {}
    return max(candidates, key=_field_priority_score)


def _asset_field_text(
    asset_field_register: list[dict[str, Any]],
    *field_names: str,
    default: str = "NOT OBSERVED",
) -> str:
    row = _best_asset_field_row(asset_field_register, *field_names)
    value = row.get("value") if isinstance(row, dict) else ""
    text = str(value).strip()
    return text or default


def _asset_field_int(
    asset_field_register: list[dict[str, Any]],
    *field_names: str,
) -> int | None:
    raw = _asset_field_text(asset_field_register, *field_names, default="")
    cleaned = re.sub(r"[^0-9]", "", raw)
    if not cleaned:
        return None
    try:
        return int(cleaned)
    except ValueError:
        return None


def _dedupe_preserve_order(values: list[str]) -> list[str]:
    seen: set[str] = set()
    out: list[str] = []
    for value in values:
        text = str(value or "").strip()
        if not text or text in seen:
            continue
        seen.add(text)
        out.append(text)
    return out


def _renumber_body_sections(body_sections: list[dict[str, Any]]) -> list[dict[str, Any]]:
    renumbered: list[dict[str, Any]] = []
    for idx, section in enumerate(list(body_sections or []), start=1):
        row = dict(section)
        row["chapter_id"] = f"C{idx}"
        renumbered.append(row)
    return renumbered


def _normalize_appendix_chapter_ids(appendix_sections: list[dict[str, Any]]) -> list[dict[str, Any]]:
    normalized: list[dict[str, Any]] = []
    seen_ids: set[str] = set()
    next_idx = 0
    for section in list(appendix_sections or []):
        chapter_id = str(section.get("chapter_id", "")).strip()
        if chapter_id.startswith("A") and chapter_id[1:].isdigit():
            next_idx = max(next_idx, int(chapter_id[1:]))
    for section in list(appendix_sections or []):
        row = dict(section)
        chapter_id = str(row.get("chapter_id", "")).strip()
        if chapter_id.startswith("A") and chapter_id not in seen_ids:
            seen_ids.add(chapter_id)
            normalized.append(row)
            continue
        next_idx += 1
        row["chapter_id"] = f"A{next_idx}"
        seen_ids.add(row["chapter_id"])
        normalized.append(row)
    return normalized


def _fmt_optional_number(value: int | None, suffix: str = "") -> str:
    if value is None:
        return "NOT OBSERVED"
    return f"{value:,}{suffix}"


def _urgency_label(score: float) -> str:
    if score >= 0.90:
        return "CRITICAL"
    if score >= 0.80:
        return "HIGH"
    if score >= 0.65:
        return "MEDIUM"
    return "LOW"


def _family_label(family: str) -> str:
    return {
        "plausible_hypothesis": "Plausible Hypothesis",
        "tension":              "Material Tension",
        "conflict":             "Hard Conflict [BLOCKING]",
        "opportunity":          "Candidate Opportunity",
        "evidence_gap":         "Evidence Gap",
    }.get(family, family.replace("_", " ").title())


def _sep(char: str = "-", width: int = 72) -> str:
    return char * width


def _sanitize_visible_text(text: str, language: str = "en") -> str:
    if not isinstance(text, str) or not text:
        return text
    sanitized = text
    replacements = [
        (r":\s*N/A\b", ": NOT OBSERVED"),
        (r":\s*UNSPECIFIED\b", ": NOT OBSERVED"),
        (r":\s*NOT CONFIRMED\b", ": NOT OBSERVED"),
        (r"\bN/A\b", "NOT OBSERVED"),
        (r"\bUNSPECIFIED\b", "NOT OBSERVED"),
        (r"\bNot confirmed\b", "NOT OBSERVED"),
        (r"\b0 sqft\b", "NOT OBSERVED — BLOCKING IF USED"),
        (r"\b0 SQFT\b", "NOT OBSERVED — BLOCKING IF USED"),
    ]
    if language == "es":
        replacements.extend([
            (r"\bTDIR PRELIMINARY\b", "lectura técnica preliminar del activo"),
            (r"\bDECISION-GRADE TDIR\b", "reporte técnico del activo en grado de decisión"),
            (r"\bTECHNICAL DECISION INTELLIGENCE REPORT\s*\(TDIR\)\b", "reporte técnico del activo"),
            (r"\bTECHNICAL DECISION INTELLIGENCE REPORT\b", "reporte técnico del activo"),
            (r"\bOPERATIONAL DECISION INTELLIGENCE REPORT\b", "brief de admisibilidad de decisión del activo"),
            (r"\bTDIR\b", "técnica del activo"),
        ])
    else:
        replacements.extend([
            (r"\bTDIR PRELIMINARY\b", "preliminary technical asset brief"),
            (r"\bDECISION-GRADE TDIR\b", "decision-grade technical asset report"),
            (r"\bTECHNICAL DECISION INTELLIGENCE REPORT\s*\(TDIR\)\b", "technical asset report"),
            (r"\bTECHNICAL DECISION INTELLIGENCE REPORT\b", "technical asset report"),
            (r"\bOPERATIONAL DECISION INTELLIGENCE REPORT\b", "asset decision-admissibility brief"),
            (r"\bTDIR\b", "asset-level technical"),
        ])
    for pattern, replacement in replacements:
        sanitized = re.sub(pattern, replacement, sanitized, flags=re.IGNORECASE)
    return sanitized


def _sanitize_non_local_regulatory_text(text: str, is_nyc_case: bool) -> str:
    if is_nyc_case or not isinstance(text, str) or not text:
        return text
    sanitized = text
    replacements = [
        (r"\bLOCAL LAW 97\b", "local building emissions rule"),
        (r"\bLL97\b", "local building emissions rule"),
        (r"\bLOCAL LAW 84\b", "public benchmarking disclosure"),
        (r"\bLL84\b", "public benchmarking disclosure"),
        (r"\bARTICLE 320\b", "public compliance pathway"),
        (r"\bARTICLE 321\b", "public compliance pathway"),
        (r"\bCOVERED BUILDINGS LIST\b", "official covered-buildings register"),
        (r"\bBEAM\b", "official emissions-reporting platform"),
        (r"\bNYC-ADJUSTED\b", "adjusted benchmark"),
        (r"\bNYC\b", "local"),
    ]
    for pattern, replacement in replacements:
        sanitized = re.sub(pattern, replacement, sanitized, flags=re.IGNORECASE)
    return sanitized


def _sanitize_section(section: dict[str, Any]) -> dict[str, Any]:
    sanitized = dict(section)
    for key in ("title", "llm_text", "llm_text_en"):
        sanitized[key] = _sanitize_visible_text(str(sanitized.get(key, "") or ""), language="en")
    sanitized["llm_text_es"] = _sanitize_visible_text(str(sanitized.get("llm_text_es", "") or ""), language="es")
    blocks = []
    for block in sanitized.get("blocks", []):
        if not isinstance(block, dict):
            blocks.append(block)
            continue
        block_copy = dict(block)
        block_copy["content"] = _sanitize_visible_text(str(block_copy.get("content", "") or ""), language="en")
        blocks.append(block_copy)
    sanitized["blocks"] = blocks
    return sanitized


def _sanitize_sections(sections: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [_sanitize_section(section) for section in sections]


def _adaptation_family(target_type: str) -> str:
    target_type = str(target_type or "").strip().lower()
    if target_type in {"industrial_plant", "manufacturing_facility", "food_processing_facility", "cold_chain_facility"}:
        return "manufacturing"
    if target_type in {"warehouse_distribution"}:
        return "logistics"
    if target_type in {"infrastructure_node"}:
        return "infrastructure"
    if target_type in {"oil_gas_upstream_site", "oil_gas_midstream_facility", "oil_gas_downstream_facility"}:
        return "oil_gas"
    return "building"


def _family_adaptation_change(target_type: str) -> str:
    family = _adaptation_family(target_type)
    if family == "manufacturing":
        return "Activates process-duty, throughput, permit, and utility-support logic instead of generic building retrofit framing."
    if family == "logistics":
        return "Activates dock, refrigeration, throughput-window, and occupancy-boundary logic instead of generic office assumptions."
    if family == "infrastructure":
        return "Activates topology, dispatch, redundancy, and resilience logic instead of generic building systems logic."
    if family == "oil_gas":
        return "Activates unit-duty, turnaround, flare/fuel, and emissions-basis logic instead of generic building energy logic."
    return "Activates geometry, occupancy, lease/control boundary, HVAC/BMS, and local building-compliance logic."


def _planned_chapter_inventory(
    body_sections: list[dict[str, Any]],
    appendix_sections: list[dict[str, Any]],
    render_section_contract: dict[str, Any] | None = None,
) -> dict[str, Any]:
    body_files = [f"{str(sec.get('chapter_id', 'CX')).strip()}.tex" for sec in body_sections]
    appendix_files = [f"{str(sec.get('chapter_id', 'AX')).strip()}.tex" for sec in appendix_sections]
    chapter_files = ["00-Brief.tex", *body_files, *appendix_files]
    return {
        "chapter_files": chapter_files,
        "body_chapter_files": body_files,
        "appendix_chapter_files": appendix_files,
        "main_include_targets": [
            "Chapters/00-Brief",
            *[f"Chapters/{str(sec.get('chapter_id', 'CX')).strip()}" for sec in body_sections],
            *[f"Chapters/{str(sec.get('chapter_id', 'AX')).strip()}" for sec in appendix_sections],
        ],
        "forbidden_template_chapters": [
            "00-Abstract.tex",
            "01-Introduction.tex",
            "02-User-Guide.tex",
            "03-Latex-Tutorial.tex",
        ],
        "canonical_output_mode": str((render_section_contract or {}).get("canonical_output_mode", "") or ""),
        "body_section_titles": [
            str(sec.get("title", "")).strip()
            for sec in body_sections
            if str(sec.get("title", "")).strip()
        ],
        "appendix_section_titles": [
            str(sec.get("title", "")).strip()
            for sec in appendix_sections
            if str(sec.get("title", "")).strip()
        ],
        "required_body_sections": list((render_section_contract or {}).get("required_body_sections", []) or []),
        "required_appendix_sections": list((render_section_contract or {}).get("required_appendix_sections", []) or []),
    }


def _build_structural_intelligence_summary(bundle: dict[str, Any]) -> dict[str, Any]:
    canonical_problem_frame = dict(bundle.get("canonical_problem_frame", {}) or {})
    executive_thesis = dict(bundle.get("executive_thesis", {}) or {})
    main_report_outline = dict(bundle.get("main_report_outline", {}) or {})
    client_facing_tad = dict(bundle.get("client_facing_tad", {}) or {})
    gold_nugget_authority_state = str(
        main_report_outline.get("gold_nugget_authority_state")
        or executive_thesis.get("gold_nugget_authority_state")
        or "legacy_primary_skill_shadow"
    ).strip()
    gold_nugget_source_register = str(
        main_report_outline.get("gold_nugget_source_register")
        or executive_thesis.get("gold_nugget_source_register")
        or ""
    ).strip()
    return {
        "system_abstraction_fields": len(dict(bundle.get("system_abstraction", {}) or {})),
        "dominant_variable_count": len(list(bundle.get("dominant_variable_register", []) or [])),
        "evidence_state_by_layer_count": len(list(bundle.get("evidence_state_by_layer_register", []) or [])),
        "cross_layer_conflict_count": len(list(bundle.get("cross_layer_conflict_register", []) or [])),
        "problem_framing_count": len(list(bundle.get("problem_framing_register", []) or [])),
        "structural_benchmark_count": len(list(bundle.get("structural_benchmark_register", []) or [])),
        "competitive_comparison_count": len(list(bundle.get("competitive_comparison_register", []) or [])),
        "conditional_redesign_count": len(list(bundle.get("conditional_redesign_register", []) or [])),
        "structural_financial_exposure_count": len(list(bundle.get("structural_financial_exposure_register", []) or [])),
        "minimum_evidence_discrimination_count": len(list(bundle.get("minimum_evidence_for_discrimination_register", []) or [])),
        "structural_claim_permission_count": len(list(bundle.get("structural_claim_permission_register", []) or [])),
        "structural_output_mode_count": len(list(bundle.get("structural_output_mode_classifier_table", []) or [])),
        "expanded_structural_tad_action_count": len(list(bundle.get("expanded_structural_tad_action_register", []) or [])),
        "canonical_problem_frame_active": bool(canonical_problem_frame.get("problem_frame_active", False)),
        "executive_thesis_present": bool(executive_thesis),
        "thesis_constellation_count": len(list(executive_thesis.get("thesis_constellation_register", []) or [])),
        "evidence_pack_family_count": len(list(executive_thesis.get("evidence_pack_register", []) or [])),
        "gold_nugget_authority_state": gold_nugget_authority_state,
        "gold_nugget_source_register": gold_nugget_source_register,
        "compressed_main_section_count": len(list(main_report_outline.get("sections", []) or [])),
        "client_facing_tad_action_count": int(client_facing_tad.get("action_count", 0) or 0),
    }


def _build_visible_claim_integrity_register(
    *,
    claim_contract_register: list[dict[str, Any]],
    deduplicated_claim_map: dict[str, Any],
) -> list[dict[str, Any]]:
    prohibited_ids = {
        str(row.get("claim_id", "")).strip()
        for row in list(claim_contract_register or [])
        if str(row.get("claim_id", "")).strip()
        and str(row.get("permission", "")).strip().lower() == "prohibited"
    }
    rows: list[dict[str, Any]] = []
    for section_key, values in dict(deduplicated_claim_map or {}).items():
        claim_ids = [
            str(value).strip()
            for value in list(values or [])
            if str(value).strip()
        ]
        blocked_ids = [claim_id for claim_id in claim_ids if claim_id in prohibited_ids]
        rows.append(
            {
                "section_key": str(section_key).strip(),
                "visible_claim_ids": claim_ids,
                "visible_claim_count": len(claim_ids),
                "blocked_claim_ids": blocked_ids,
                "blocked_claim_count": len(blocked_ids),
            }
        )
    return rows


def _build_structural_executive_summary(bundle: dict[str, Any]) -> dict[str, Any]:
    canonical_problem_frame = dict(bundle.get("canonical_problem_frame", {}) or {})
    structural_reasoning_path = dict(bundle.get("structural_reasoning_path", {}) or {})
    executive_thesis = dict(bundle.get("executive_thesis", {}) or {})
    main_report_outline = dict(bundle.get("main_report_outline", {}) or {})
    problem_rows = list(bundle.get("problem_framing_register", []) or [])
    conflict_rows = list(bundle.get("cross_layer_conflict_register", []) or [])
    mode_rows = list(bundle.get("structural_output_mode_classifier_table", []) or [])
    mode_summary = dict(bundle.get("structural_output_mode_summary", {}) or {})
    action_rows = list(bundle.get("expanded_structural_tad_action_register", []) or [])
    legacy_claim_contract_register = list(bundle.get("claim_contract_register", []) or [])
    governed_claim_contract_register = list(
        executive_thesis.get("governed_claim_contract_register", []) or []
    )
    # Merge legacy (motor_034) and governed (motor_054) claim registers.
    # Governed takes precedence per claim_id because it carries the
    # four-state epistemic vocabulary and explicit falsification_condition.
    # See RECOVERY_BACKLOG.md R-W03.
    claim_contract_register = _merge_claim_contract_registers(
        legacy_claim_contract_register,
        governed_claim_contract_register,
    )
    deduplicated_claim_map = dict(bundle.get("deduplicated_claim_map", {}) or {})
    primary_action = next(
        (
            row for row in action_rows
            if str(row.get("status", "")).strip() in {"ACT NOW", "VALIDATE FIRST", "COMPARE TO PEERS", "REDESIGN HYPOTHESIS", "DO NOT MODEL YET"}
        ),
        action_rows[0] if action_rows else {},
    )
    activated_modes = list(mode_summary.get("activated_secondary_modes", []) or [])
    blocked_modes = list(mode_summary.get("blocked_secondary_modes", []) or [])
    promotable_modes = list(mode_summary.get("eligible_primary_modes", []) or [])
    gold_nugget_authority_state = str(
        main_report_outline.get("gold_nugget_authority_state")
        or executive_thesis.get("gold_nugget_authority_state")
        or "legacy_primary_skill_shadow"
    ).strip()
    gold_nugget_source_register = str(
        main_report_outline.get("gold_nugget_source_register")
        or executive_thesis.get("gold_nugget_source_register")
        or ""
    ).strip()
    top_gold_nuggets = [
        str((row or {}).get("gold_nugget", "")).strip()
        for row in list(executive_thesis.get("top_gold_nuggets", []) or [])
        if str((row or {}).get("gold_nugget", "")).strip()
    ]
    thesis_constellation_register = list(executive_thesis.get("thesis_constellation_register", []) or [])
    correlation_constellation_register = list(executive_thesis.get("correlation_constellation_register", []) or [])
    evidence_pack_register = list(executive_thesis.get("evidence_pack_register", []) or [])
    visible_claim_integrity_register = _build_visible_claim_integrity_register(
        claim_contract_register=claim_contract_register,
        deduplicated_claim_map=deduplicated_claim_map,
    )
    visible_blocked_claim_count = sum(
        int(row.get("blocked_claim_count", 0) or 0)
        for row in visible_claim_integrity_register
    )
    visible_claim_count = sum(
        int(row.get("visible_claim_count", 0) or 0)
        for row in visible_claim_integrity_register
    )
    conditional_opportunity_pathways = _build_conditional_opportunity_fallbacks(executive_thesis)
    return {
        "thesis_state": str(executive_thesis.get("thesis_state", "")).strip(),
        "local_claim_closure_state": str(executive_thesis.get("local_claim_closure_state", "")).strip(),
        "conditional_intelligence_available": bool(executive_thesis.get("conditional_intelligence_available", False)),
        "conditional_intelligence_reason": str(executive_thesis.get("conditional_intelligence_reason", "")).strip(),
        "structural_mode_candidates": activated_modes or [
            str(row.get("recommended_output_mode", "")).strip()
            for row in mode_rows
            if str(row.get("recommended_output_mode", "")).strip()
        ],
        "default_reasoning_path": str(
            structural_reasoning_path.get("reasoning_path")
            or canonical_problem_frame.get("reasoning_path")
            or "legacy_decision_gating_only"
        ),
        "problem_frame_active": bool(
            structural_reasoning_path.get("problem_frame_active", canonical_problem_frame.get("problem_frame_active", False))
        ),
        "blocked_structural_modes": blocked_modes,
        "promotable_primary_structural_modes": promotable_modes,
        "leading_primary_structural_mode": str(mode_summary.get("leading_primary_promotion_candidate", "") or ""),
        "gold_nugget_authority_state": gold_nugget_authority_state,
        "gold_nugget_source_register": gold_nugget_source_register,
        "stated_problem": str(executive_thesis.get("declared_problem", "")).strip()
        or str(canonical_problem_frame.get("stated_problem", "")).strip()
        or (str((problem_rows[0] or {}).get("stated_problem", "")).strip() if problem_rows else ""),
        "primary_reframed_problem": str(executive_thesis.get("reframed_problem", "")).strip()
        or str(canonical_problem_frame.get("reframed_problem", "")).strip()
        or (str((problem_rows[0] or {}).get("reframed_problem", "")).strip() if problem_rows else ""),
        "dominant_structural_conflict": str(executive_thesis.get("dominant_contradiction", "")).strip()
        or str(canonical_problem_frame.get("dominant_conflict", "")).strip()
        or (str((conflict_rows[0] or {}).get("conflict", "")).strip() if conflict_rows else ""),
        "minimum_evidence_to_discriminate": (
            "; ".join([str(item).strip() for item in list(executive_thesis.get("minimum_discriminating_evidence", []) or []) if str(item).strip()])
            or str(canonical_problem_frame.get("minimum_evidence_to_discriminate", "")).strip()
        ),
        "primary_structural_action": str(
            ((executive_thesis.get("top_actions", []) or [{}])[0] or {}).get("action", "")
        ).strip() or str(primary_action.get("action", "")).strip(),
        "primary_structural_action_status": str(
            ((executive_thesis.get("top_actions", []) or [{}])[0] or {}).get("status", "")
        ).strip() or str(primary_action.get("status", "")).strip(),
        "why_current_question_is_premature": str(executive_thesis.get("why_current_question_is_premature", "")).strip(),
        "what_reality_feature_changes_the_decision": str(
            executive_thesis.get("what_reality_feature_changes_the_decision", "")
        ).strip(),
        "dominant_risk": str(executive_thesis.get("dominant_risk", "")).strip(),
        "why_it_matters": str(executive_thesis.get("why_it_matters", "")).strip(),
        "surprising_but_evidenced_takeaway": str(
            executive_thesis.get("surprising_but_evidenced_takeaway", "")
        ).strip(),
        "dominant_operational_misunderstanding": str(
            executive_thesis.get("dominant_operational_misunderstanding", "")
        ).strip(),
        "hidden_system_boundary_error": str(executive_thesis.get("hidden_system_boundary_error", "")).strip(),
        "invalid_comparison_risk": str(executive_thesis.get("invalid_comparison_risk", "")).strip(),
        "dominant_loss_logic": str(executive_thesis.get("dominant_loss_logic", "")).strip(),
        "top_gold_nuggets": top_gold_nuggets[:8],
        "thesis_constellation_register": thesis_constellation_register,
        "correlation_constellation_register": correlation_constellation_register[:5],
        "evidence_pack_register": evidence_pack_register,
        "visible_claim_integrity_register": visible_claim_integrity_register,
        "visible_blocked_claim_count": visible_blocked_claim_count,
        "visible_claim_count": visible_claim_count,
        "conditional_opportunity_pathways": conditional_opportunity_pathways,
        "not_admissible_actions": list(executive_thesis.get("what_is_not_admissible", []) or []),
        "supporting_modes": list(executive_thesis.get("supporting_modes", []) or []),
        "report_mode": str(executive_thesis.get("report_mode", "")).strip(),
        "bounded_note": (
            "These structural readings remain conditional and do not override claim permissions, report type, or validation gates."
            if any([problem_rows, conflict_rows, mode_rows, action_rows, canonical_problem_frame])
            else ""
        ),
    }


def _build_conditional_opportunity_fallbacks(executive_thesis: dict[str, Any]) -> list[dict[str, Any]]:
    executive_thesis = dict(executive_thesis or {})

    def _clean(items: Any, *, limit: int | None = None) -> list[str]:
        if isinstance(items, list):
            values = [str(item).strip() for item in items if str(item).strip()]
        else:
            text = str(items or "").strip()
            values = [text] if text else []
        deduped: list[str] = []
        seen: set[str] = set()
        for value in values:
            if value in seen:
                continue
            seen.add(value)
            deduped.append(value)
            if limit is not None and len(deduped) >= limit:
                break
        return deduped

    def _append(
        rows: list[dict[str, Any]],
        *,
        name: str,
        opportunity_type: str,
        statement: str,
        dependencies: list[str],
        validation_requirement: str,
    ) -> None:
        text = str(statement or "").strip()
        if not text:
            return
        deps = _clean(dependencies, limit=4)
        rows.append(
            {
                "opportunity_id": f"fallback_{len(rows) + 1:02d}",
                "opportunity_name": name,
                "opportunity_type": opportunity_type,
                "plausibility_score": 0.74,
                "decision_relevance_score": 0.87,
                "validation_urgency_score": 0.91
                if str(executive_thesis.get("local_claim_closure_state", "")).strip() == "blocked"
                else 0.76,
                "conditional_statement": text,
                "dependency_assumptions": deps,
                "validation_requirement": validation_requirement,
            }
        )

    thesis_state = str(executive_thesis.get("thesis_state", "")).strip()
    strategic_signal_present = any(
        str(executive_thesis.get(key, "")).strip()
        for key in [
            "dominant_operational_misunderstanding",
            "hidden_system_boundary_error",
            "invalid_comparison_risk",
            "dominant_loss_logic",
            "surprising_but_evidenced_takeaway",
        ]
    ) or bool(executive_thesis.get("conditional_redesign"))
    if thesis_state not in {"conditional_structural_intelligence", "admissible_structural_thesis"} and not strategic_signal_present:
        return []

    minimum_evidence = _clean(executive_thesis.get("minimum_discriminating_evidence", []), limit=4)
    validation_requirement = (
        "; ".join(minimum_evidence)
        or str(executive_thesis.get("why_current_question_is_premature", "")).strip()
        or "Bound the dominant discriminator before closing local claims."
    )
    rows: list[dict[str, Any]] = []
    dominant_misunderstanding = str(executive_thesis.get("dominant_operational_misunderstanding", "")).strip()
    hidden_boundary_error = str(executive_thesis.get("hidden_system_boundary_error", "")).strip()
    invalid_comparison_risk = str(executive_thesis.get("invalid_comparison_risk", "")).strip()
    dominant_loss_logic = str(executive_thesis.get("dominant_loss_logic", "")).strip()
    surprising_takeaway = str(executive_thesis.get("surprising_but_evidenced_takeaway", "")).strip()
    decision_trigger = str(executive_thesis.get("what_reality_feature_changes_the_decision", "")).strip()
    conditional_redesign = dict(executive_thesis.get("conditional_redesign", {}) or {})

    if dominant_misunderstanding or invalid_comparison_risk:
        _append(
            rows,
            name="Reframe the comparison before sizing action",
            opportunity_type="comparison_reframe",
            statement=(
                "If the current denominator or peer frame is wrong, capital can target the wrong variable before the asset is normalized."
            ),
            dependencies=[dominant_misunderstanding, invalid_comparison_risk, decision_trigger],
            validation_requirement=validation_requirement,
        )
    if hidden_boundary_error or decision_trigger:
        _append(
            rows,
            name="Rebound the control boundary before underwriting value capture",
            opportunity_type="boundary_reframe",
            statement=(
                "If the burdened actor and the controllable load boundary are not the same thing, underwriting can over-assign savings or CAPEX to the wrong operator."
            ),
            dependencies=[hidden_boundary_error, decision_trigger],
            validation_requirement=validation_requirement,
        )
    if dominant_loss_logic or surprising_takeaway:
        _append(
            rows,
            name="Test whether the visible problem is structural, not generic energy waste",
            opportunity_type="structural_loss_hypothesis",
            statement=dominant_loss_logic or surprising_takeaway,
            dependencies=[surprising_takeaway, dominant_loss_logic, decision_trigger],
            validation_requirement=validation_requirement,
        )
    redesign_direction = str(
        conditional_redesign.get("redesign_direction") or conditional_redesign.get("economic_logic") or ""
    ).strip()
    if redesign_direction:
        _append(
            rows,
            name="Pursue redesign only after the trigger hypothesis survives falsification",
            opportunity_type="conditional_redesign",
            statement=redesign_direction,
            dependencies=[
                str(conditional_redesign.get("trigger_hypothesis") or conditional_redesign.get("hypothesis") or "").strip(),
                str(conditional_redesign.get("kill_condition") or "").strip(),
            ],
            validation_requirement=(
                "; ".join(_clean(conditional_redesign.get("evidence_needed", []), limit=4))
                or validation_requirement
            ),
        )
    return rows[:4]


_CASE_ADAPTATION_REFERENCE_FINGERPRINTS: list[dict[str, Any]] = [
    {
        "reference_key": "one_vanderbilt_nyc_screening",
        "case_tokens": ["ONE VANDERBILT", "1 VANDERBILT"],
        "family": "building",
        "report_mode": "screening",
        "target_type": "commercial_building",
        "jurisdiction": {"state": "NY", "city": "New York"},
        "accepted_sources": [
            "nyc_dof_property_record",
            "nyc_pluto_property",
            "nyc_ll84_energy_benchmarking",
            "nyc_dob_permits",
            "nyc_ll97_covered_buildings_list",
        ],
        "strong_clusters": ["identity_cluster", "geometry_size_cluster", "regulatory_cluster"],
        "weak_clusters": ["systems_cluster", "control_boundary_cluster", "financial_boundary_cluster"],
        "decision_fronts": [
            "Acquisition underwriting with energy upside",
            "Energy retrofit CAPEX",
            "Compliance investment",
            "Seller/operator evidence request",
        ],
        "scenario_headlines": [
            "Public building evidence supports screening-grade compliance posture but not closure."
        ],
    },
    {
        "reference_key": "los_angeles_large_office_public_context",
        "case_tokens": ["111 SOUTH GRAND AVENUE", "111 S GRAND AVE"],
        "family": "building",
        "report_mode": "blocked",
        "target_type": "commercial_building",
        "jurisdiction": {"state": "CA", "city": "Los Angeles"},
        "accepted_sources": [
            "la_county_assessor_property_record",
            "la_building_permits",
            "ca_title24_guidance",
            "utility_ladwp_or_sce_service_territory",
        ],
        "strong_clusters": ["identity_cluster", "geometry_size_cluster"],
        "weak_clusters": ["fuel_energy_cluster", "systems_cluster", "control_boundary_cluster"],
        "decision_fronts": [
            "Acquisition underwriting with energy upside",
            "Energy retrofit CAPEX",
            "Seller/operator evidence request",
        ],
        "scenario_headlines": [
            "Public building context exists, but asset-level energy and control evidence remain insufficient."
        ],
    },
    {
        "reference_key": "wilsonart_temple_manufacturing_blocked",
        "case_tokens": ["WILSONART TEMPLE NORTH LAMINATE FACILITY", "10501 N HK DODGEN LOOP"],
        "family": "manufacturing",
        "report_mode": "blocked",
        "target_type": "manufacturing_facility",
        "jurisdiction": {"state": "TX", "city": "Temple"},
        "accepted_sources": [
            "tceq_permits_and_emissions",
            "bell_cad_property_search_portal",
            "temple_permit_records_context",
        ],
        "strong_clusters": ["identity_cluster", "regulatory_cluster"],
        "weak_clusters": ["geometry_size_cluster", "fuel_energy_cluster", "systems_cluster", "control_boundary_cluster"],
        "decision_fronts": [
            "Operator evidence request",
            "Environmental or permit-driven investment",
            "Process efficiency or utility-support CAPEX",
            "Process redesign",
        ],
        "scenario_headlines": [
            "Process load may be structural rather than discretionary waste."
        ],
    },
    {
        "reference_key": "generic_process_manufacturing_reference",
        "case_tokens": ["FOOD PROCESSING", "PROCESS MANUFACTURING"],
        "family": "manufacturing",
        "report_mode": "blocked",
        "target_type": "manufacturing_facility",
        "jurisdiction": {"state": "CA", "city": "Oakland"},
        "accepted_sources": [
            "ca_state_environmental_permits",
            "baaqmd_permit_portal_context",
            "county_assessor_or_appraisal_property_record",
        ],
        "strong_clusters": ["identity_cluster"],
        "weak_clusters": ["geometry_size_cluster", "operating_regime_cluster", "systems_cluster", "control_boundary_cluster"],
        "decision_fronts": [
            "Operator evidence request",
            "Environmental or permit-driven investment",
            "Process efficiency or utility-support CAPEX",
        ],
        "scenario_headlines": [
            "Permit and utility context exist, but process evidence is still insufficient for CAPEX-grade action."
        ],
    },
]


def _normalize_comparison_text(value: str) -> str:
    return " ".join(str(value or "").strip().upper().split())


def _report_mode_from_readiness(report_readiness_register: dict[str, Any]) -> str:
    allowed = [canonicalize_output_mode(str(item).strip()) for item in (report_readiness_register.get("report_type_allowed", []) or []) if str(item).strip()]
    if "Compliance / Investment Screening Brief" in allowed:
        return "screening"
    if "Exploratory Prior Brief" in allowed:
        return "exploratory"
    if "Target Classification Brief" in allowed:
        return "classification"
    if "Full Technical Decision Intelligence Report" in allowed:
        return "full_technical"
    return "blocked"


def _same_reference_case(case_label: str, reference: dict[str, Any]) -> bool:
    normalized_label = _normalize_comparison_text(case_label)
    tokens = [_normalize_comparison_text(token) for token in reference.get("case_tokens", []) or [] if _normalize_comparison_text(token)]
    return any(token and token in normalized_label for token in tokens)


def _compare_case_adaptation_fingerprint(
    fingerprint: dict[str, Any],
    *,
    case_label: str,
    report_mode: str,
) -> dict[str, Any]:
    high_value_dimensions = {
        "target_type",
        "jurisdiction",
        "source_coverage",
        "strong_clusters",
        "decision_fronts",
        "scenario_headlines",
        "report_mode",
    }
    comparables = [
        reference
        for reference in _CASE_ADAPTATION_REFERENCE_FINGERPRINTS
        if reference.get("family") == fingerprint.get("family")
        and not _same_reference_case(case_label, reference)
    ]

    comparison_rows: list[dict[str, Any]] = []
    for reference in comparables:
        differing_dimensions: list[str] = []
        if str(reference.get("target_type", "")).strip() != str(fingerprint.get("target_type", "")).strip():
            differing_dimensions.append("target_type")
        ref_jurisdiction = dict(reference.get("jurisdiction", {}) or {})
        current_jurisdiction = dict(fingerprint.get("jurisdiction", {}) or {})
        if ref_jurisdiction.get("state") != current_jurisdiction.get("state") or ref_jurisdiction.get("city") != current_jurisdiction.get("city"):
            differing_dimensions.append("jurisdiction")
        if sorted(reference.get("accepted_sources", []) or []) != sorted(fingerprint.get("accepted_sources", []) or []):
            differing_dimensions.append("source_coverage")
        if sorted(reference.get("strong_clusters", []) or []) != sorted(fingerprint.get("strong_clusters", []) or []):
            differing_dimensions.append("strong_clusters")
        if sorted(reference.get("weak_clusters", []) or []) != sorted(fingerprint.get("weak_clusters", []) or []):
            differing_dimensions.append("weak_clusters")
        if sorted(reference.get("decision_fronts", []) or []) != sorted(fingerprint.get("decision_fronts", []) or []):
            differing_dimensions.append("decision_fronts")
        if sorted(reference.get("decision_front_statuses", []) or []) != sorted(fingerprint.get("decision_front_statuses", []) or []):
            differing_dimensions.append("decision_front_statuses")
        if sorted(reference.get("scenario_headlines", []) or []) != sorted(fingerprint.get("scenario_headlines", []) or []):
            differing_dimensions.append("scenario_headlines")
        if sorted(reference.get("bottlenecks", []) or []) != sorted(fingerprint.get("bottlenecks", []) or []):
            differing_dimensions.append("bottlenecks")
        if str(reference.get("report_mode", "")).strip() != report_mode:
            differing_dimensions.append("report_mode")

        comparison_rows.append(
            {
                "reference_key": reference.get("reference_key", ""),
                "reference_family": reference.get("family", ""),
                "reference_report_mode": reference.get("report_mode", ""),
                "difference_count": len(differing_dimensions),
                "differing_dimensions": differing_dimensions,
            }
        )

    comparison_rows = sorted(
        comparison_rows,
        key=lambda row: (
            int(row.get("difference_count", 999)),
            str(row.get("reference_key", "")),
        ),
    )
    closest = comparison_rows[0] if comparison_rows else {}
    closest_difference_count = int(closest.get("difference_count", 0) or 0)
    closest_high_value_difference_count = sum(
        1
        for dimension in list(closest.get("differing_dimensions", []) or [])
        if dimension in high_value_dimensions
    )
    comparison_failure = bool(comparison_rows) and (
        closest_difference_count < 2
        or closest_high_value_difference_count == 0
    )
    failure_reason = ""
    if comparison_failure:
        if closest_high_value_difference_count == 0:
            failure_reason = (
                "Case adaptation fingerprint remains too close to comparable reference "
                f"{closest.get('reference_key', '')}; only low-signal divergence is visible."
            )
        else:
            failure_reason = (
                "Case adaptation fingerprint remains too close to comparable reference "
                f"{closest.get('reference_key', '')} across structured dimensions."
            )
    return {
        "reference_count": len(comparison_rows),
        "rows": comparison_rows,
        "closest_reference_key": str(closest.get("reference_key", "")).strip(),
        "closest_reference_difference_count": closest_difference_count,
        "closest_high_value_difference_count": closest_high_value_difference_count,
        "closest_reference_differences": list(closest.get("differing_dimensions", []) or []),
        "comparison_failure": comparison_failure,
        "failure_reason": failure_reason,
    }


def _build_case_adaptation_diversity_register(
    *,
    accepted_sources: list[str],
    decision_front_register: list[dict[str, Any]],
    scenario_space: list[dict[str, Any]],
    strong_clusters: list[str],
    weak_clusters: list[str],
    bottlenecks: list[str],
) -> list[dict[str, Any]]:
    unique_sources = _dedupe_preserve_order(accepted_sources)
    unique_fronts = _dedupe_preserve_order(
        [str(row.get("decision_front", "")).strip() for row in decision_front_register if str(row.get("decision_front", "")).strip()]
    )
    unique_statuses = _dedupe_preserve_order(
        [str(row.get("current_status", "")).strip() for row in decision_front_register if str(row.get("current_status", "")).strip()]
    )
    nonempty_scenarios = [
        row for row in scenario_space
        if str(row.get("scenario", "")).strip() or str(row.get("financial_meaning", "")).strip()
    ]

    rows: list[dict[str, Any]] = []

    def _append(
        *,
        dimension: str,
        score: int,
        minimum_score: int,
        observed_state: str,
        detail: str,
        why_it_matters: str,
    ) -> None:
        rows.append(
            {
                "dimension": dimension,
                "score": score,
                "minimum_score": minimum_score,
                "passes": score >= minimum_score,
                "observed_state": observed_state,
                "detail": detail,
                "why_it_matters": why_it_matters,
            }
        )

    _append(
        dimension="source_family_diversity",
        score=min(len(unique_sources), 3),
        minimum_score=2,
        observed_state=(
            "strong" if len(unique_sources) >= 3
            else "bounded" if len(unique_sources) >= 2
            else "thin"
        ),
        detail=f"{len(unique_sources)} accepted source families visible in the adaptation memo.",
        why_it_matters="Multiple source families reduce the risk that the report is only rephrasing one public surface.",
    )
    _append(
        dimension="decision_front_diversity",
        score=min(len(unique_fronts), 3) + (1 if len(unique_statuses) >= 2 else 0),
        minimum_score=3,
        observed_state=(
            "strong" if len(unique_fronts) >= 3 and len(unique_statuses) >= 2
            else "bounded" if len(unique_fronts) >= 2
            else "thin"
        ),
        detail=(
            f"{len(unique_fronts)} decision fronts across {len(unique_statuses)} action postures."
        ),
        why_it_matters="A strong report should show more than one action lane and more than one posture under uncertainty.",
    )
    _append(
        dimension="cluster_tension_diversity",
        score=int(bool(strong_clusters)) + int(bool(weak_clusters)),
        minimum_score=2,
        observed_state=(
            "strong" if strong_clusters and weak_clusters
            else "thin"
        ),
        detail=(
            f"Strong clusters: {len(strong_clusters)}; weak clusters: {len(weak_clusters)}."
        ),
        why_it_matters="The report should show both what is already bounded and what still blocks closure.",
    )
    scenario_score = int(bool(nonempty_scenarios))
    if len(nonempty_scenarios) >= 2:
        scenario_score += 1
    if any(str(row.get("financial_meaning", "")).strip() for row in nonempty_scenarios):
        scenario_score += 1
    _append(
        dimension="scenario_tension_diversity",
        score=scenario_score,
        minimum_score=2,
        observed_state=(
            "strong" if scenario_score >= 3
            else "bounded" if scenario_score >= 2
            else "thin"
        ),
        detail=(
            f"{len(nonempty_scenarios)} bounded scenarios with "
            f"{sum(1 for row in nonempty_scenarios if str(row.get('financial_meaning', '')).strip())} explicit financial meanings."
        ),
        why_it_matters="The report should carry at least one real strategic fork, not just a single static thesis sentence.",
    )
    _append(
        dimension="bottleneck_specificity",
        score=min(len(bottlenecks), 2),
        minimum_score=1,
        observed_state=(
            "strong" if len(bottlenecks) >= 2
            else "bounded" if len(bottlenecks) == 1
            else "thin"
        ),
        detail=f"{len(bottlenecks)} named bottleneck variables surfaced.",
        why_it_matters="A non-template report should expose the limiting variables it thinks actually govern the case.",
    )
    return rows


def _build_case_adaptation_memo(
    *,
    target_definition: dict[str, Any],
    jurisdiction_resolution: dict[str, Any],
    source_register: list[dict[str, Any]],
    cluster_maturity_register: list[dict[str, Any]],
    decision_front_register: list[dict[str, Any]],
    scenario_space: list[dict[str, Any]],
    report_readiness_register: dict[str, Any],
    variable_bottleneck_register: list[dict[str, Any]],
) -> dict[str, Any]:
    target_type = str(target_definition.get("target_type", "") or "").strip().lower()
    family = _adaptation_family(target_type)
    report_mode = _report_mode_from_readiness(report_readiness_register)
    case_label = (
        str(target_definition.get("target_name", "")).strip()
        or str(target_definition.get("target_label", "")).strip()
        or str(target_definition.get("address_raw", "")).strip()
    )
    rows: list[dict[str, str]] = []

    rows.append(
        {
            "dimension": "asset_type_logic",
            "case_specific_finding": f"Target typed as {target_type or 'unknown'} with family {family}.",
            "how_it_changes_the_report": _family_adaptation_change(target_type),
        }
    )

    state = str(jurisdiction_resolution.get("state", "") or "").strip()
    city = str(jurisdiction_resolution.get("city", "") or "").strip()
    utility = str(jurisdiction_resolution.get("utility", "") or "").strip()
    regulatory_stack = [str(item).strip() for item in (jurisdiction_resolution.get("regulatory_stack") or []) if str(item).strip()]
    if state or city or utility or regulatory_stack:
        rows.append(
            {
                "dimension": "jurisdiction_logic",
                "case_specific_finding": (
                    f"Jurisdiction resolved to {city or 'unknown city'}, {state or 'unknown state'}"
                    + (f" with utility territory {utility}." if utility else ".")
                ),
                "how_it_changes_the_report": (
                    "Routes public-data families and regulatory framing through "
                    + (", ".join(regulatory_stack[:4]) if regulatory_stack else "the resolved jurisdiction stack")
                    + " instead of generic national context."
                ),
            }
        )

    accepted_sources = []
    for row in source_register:
        if row.get("accepted"):
            source_id = str(row.get("source_id", "")).strip()
            label = str(row.get("source_name") or row.get("source_key") or "").strip()
            if not label and source_id:
                label = source_id.split("::", 1)[0]
            if not label:
                label = str(row.get("title", "")).strip()
            if label and label not in accepted_sources:
                accepted_sources.append(label)
    if accepted_sources:
        rows.append(
            {
                "dimension": "source_coverage",
                "case_specific_finding": "Accepted public sources: " + ", ".join(accepted_sources[:5]) + ".",
                "how_it_changes_the_report": "Limits supported claims to the physical or regulatory substrate actually observed in these source families.",
            }
        )

    strong_clusters = [
        str(row.get("cluster_id") or row.get("cluster") or "").strip()
        for row in cluster_maturity_register
        if int(row.get("level", 0) or 0) >= 3 and str(row.get("cluster_id") or row.get("cluster") or "").strip()
    ]
    weak_clusters = [
        str(row.get("cluster_id") or row.get("cluster") or "").strip()
        for row in cluster_maturity_register
        if int(row.get("level", 0) or 0) <= 1 and str(row.get("cluster_id") or row.get("cluster") or "").strip()
    ]
    if strong_clusters or weak_clusters:
        rows.append(
            {
                "dimension": "evidence_maturity",
                "case_specific_finding": (
                    "Strong clusters: "
                    + (", ".join(strong_clusters[:4]) if strong_clusters else "none")
                    + ". Weak clusters: "
                    + (", ".join(weak_clusters[:4]) if weak_clusters else "none")
                    + "."
                ),
                "how_it_changes_the_report": str(report_readiness_register.get("reason") or "Changes the admissible report class and the ceiling on numeric, compliance, and CAPEX claims.").strip(),
            }
        )

    if decision_front_register:
        fronts = []
        for row in decision_front_register[:4]:
            front = str(row.get("decision_front", "")).strip()
            status = str(row.get("current_status", "")).strip()
            if front:
                fronts.append(f"{front}={status}")
        if fronts:
            rows.append(
                {
                    "dimension": "decision_layer",
                    "case_specific_finding": "Decision fronts currently resolve as " + "; ".join(fronts) + ".",
                    "how_it_changes_the_report": "Shapes TAD into graded action posture rather than a flat defer/no-go surface.",
                }
            )

    if scenario_space:
        lead = scenario_space[0]
        rows.append(
            {
                "dimension": "dominant_scenario",
                "case_specific_finding": str(lead.get("scenario", "")).strip() or "Scenario space active.",
                "how_it_changes_the_report": (
                    str(lead.get("financial_meaning", "")).strip()
                    or "Changes which downside and evidence-falsification path lead the case."
                ),
            }
        )

    bottlenecks = _dedupe_preserve_order([
        str(row.get("variable_name") or row.get("decision_name") or "").strip()
        for row in variable_bottleneck_register[:4]
        if str(row.get("variable_name") or row.get("decision_name") or "").strip()
    ])
    if bottlenecks:
        rows.append(
            {
                "dimension": "dominant_bottlenecks",
                "case_specific_finding": "Current bottlenecks: " + ", ".join(bottlenecks) + ".",
                "how_it_changes_the_report": "Keeps blocked claims, evidence requests, and screening posture aligned to the true limiting variables.",
            }
        )

    present_dimensions = {row["dimension"] for row in rows if row.get("case_specific_finding") and row.get("how_it_changes_the_report")}
    required_dimensions = {"asset_type_logic", "jurisdiction_logic", "source_coverage", "evidence_maturity", "decision_layer", "dominant_scenario"}
    failure_reasons: list[str] = []
    if len(present_dimensions & required_dimensions) < 5:
        failure_reasons.append("Case adaptation memo does not cover enough critical adaptation dimensions.")
    if not accepted_sources:
        failure_reasons.append("No accepted source coverage available for case-specific adaptation memo.")
    if family == "manufacturing":
        front_names = " ".join(str(row.get("decision_front", "")).lower() for row in decision_front_register)
        if "process" not in front_names and "utility" not in front_names:
            failure_reasons.append("Manufacturing case did not activate process/utility-specific decision fronts.")
    if family == "building":
        front_names = " ".join(str(row.get("decision_front", "")).lower() for row in decision_front_register)
        if "acquisition underwriting" not in front_names and "energy retrofit" not in front_names and "compliance investment" not in front_names:
            failure_reasons.append("Building case did not activate building-specific capital or compliance fronts.")

    adaptation_fingerprint = {
        "target_type": target_type,
        "family": family,
        "report_mode": report_mode,
        "jurisdiction": {
            "state": state,
            "city": city,
        },
        "accepted_sources": accepted_sources[:5],
        "strong_clusters": strong_clusters[:4],
        "weak_clusters": weak_clusters[:4],
        "decision_fronts": [str(row.get("decision_front", "")).strip() for row in decision_front_register[:4] if str(row.get("decision_front", "")).strip()],
        "decision_front_statuses": [str(row.get("current_status", "")).strip() for row in decision_front_register[:4] if str(row.get("current_status", "")).strip()],
        "scenario_headlines": [str(row.get("scenario", "")).strip() for row in scenario_space[:2] if str(row.get("scenario", "")).strip()],
        "bottlenecks": bottlenecks[:4],
    }

    diversity_register = _build_case_adaptation_diversity_register(
        accepted_sources=accepted_sources,
        decision_front_register=decision_front_register,
        scenario_space=scenario_space,
        strong_clusters=strong_clusters,
        weak_clusters=weak_clusters,
        bottlenecks=bottlenecks,
    )
    diversity_score = sum(1 for row in diversity_register if bool(row.get("passes")))
    diversity_target_score = 4
    diversity_failure = diversity_score < diversity_target_score
    rows.append(
        {
            "dimension": "structural_diversity",
            "case_specific_finding": (
                f"Structured diversity score is {diversity_score}/{len(diversity_register)} "
                f"against a target of {diversity_target_score}."
            ),
            "how_it_changes_the_report": (
                "Protects against reports that technically adapt to the case but still read too flat, single-lane, or template-like."
            ),
        }
    )
    if diversity_failure:
        failure_reasons.append(
            "Case adaptation memo lacks enough structural diversity across sources, decision fronts, scenarios, and bottleneck variables."
        )

    comparison_summary = _compare_case_adaptation_fingerprint(
        adaptation_fingerprint,
        case_label=case_label,
        report_mode=report_mode,
    )
    if comparison_summary.get("reference_count", 0):
        rows.append(
            {
                "dimension": "comparative_case_divergence",
                "case_specific_finding": (
                    f"Closest comparable reference is {comparison_summary.get('closest_reference_key', 'unknown')} "
                    f"with differences across {', '.join(comparison_summary.get('closest_reference_differences', []) or ['none'])}."
                ),
                "how_it_changes_the_report": "Blocks superficial template reuse by requiring structured divergence from comparable cases.",
            }
        )
    if comparison_summary.get("comparison_failure"):
        failure_reasons.append(str(comparison_summary.get("failure_reason", "")).strip())

    return {
        "rows": rows,
        "diversity_register": diversity_register,
        "diversity_score": diversity_score,
        "diversity_target_score": diversity_target_score,
        "diversity_failure": diversity_failure,
        "substantive_dimension_count": len(present_dimensions),
        "required_dimension_count": len(required_dimensions),
        "template_contamination_failure": bool(failure_reasons),
        "failure_reasons": failure_reasons,
        "adaptation_fingerprint": adaptation_fingerprint,
        "comparison_summary": comparison_summary,
        "comparison_register": list(comparison_summary.get("rows", []) or []),
    }


def _build_source_family_coverage_table(
    base_rows: list[dict[str, Any]],
    asset_field_register: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    field_rows_by_source_type: dict[str, list[dict[str, Any]]] = {}
    for row in asset_field_register:
        source_id = str(row.get("source_id", "")).strip()
        source_type = source_id.split("::", 1)[0] if source_id else ""
        if source_type:
            field_rows_by_source_type.setdefault(source_type, []).append(row)

    coverage_rows: list[dict[str, Any]] = []
    for row in base_rows:
        matched_source_types = list(row.get("matched_source_types", []) or [])
        supporting_rows = [
            field_row
            for source_type in matched_source_types
            for field_row in field_rows_by_source_type.get(source_type, [])
            if str(field_row.get("status", "")).strip() == "OBSERVED"
        ]
        extracted_fields: list[str] = []
        for field_row in supporting_rows:
            field_name = str(field_row.get("field", "")).strip()
            if field_name and field_name not in extracted_fields:
                extracted_fields.append(field_name)

        physical_support = any(bool(field_row.get("physical_substrate_supported")) for field_row in supporting_rows)
        operating_support = any(bool(field_row.get("operating_substrate_supported")) for field_row in supporting_rows)
        regulatory_support = any(bool(field_row.get("regulatory_supported")) for field_row in supporting_rows)
        identity_support = any(bool(field_row.get("identity_supported")) for field_row in supporting_rows)

        expected_fields = list(row.get("fields_expected", []) or [])
        missing = [field_name for field_name in expected_fields if field_name not in extracted_fields]
        scope = str(row.get("scope", "")).strip()

        if row.get("found") and identity_support and not (physical_support or operating_support or regulatory_support):
            support_note = "Source confirms identity only, not physical operating substrate."
        elif row.get("found") and extracted_fields and scope == "ENTITY_LEVEL":
            support_note = "Source contributed entity-level support for the listed fields."
        elif row.get("found") and extracted_fields:
            support_note = "Source contributed asset-level support for the listed fields."
        elif row.get("found"):
            support_note = "Source found, but no downstream supported fields were admitted."
        elif row.get("queried"):
            support_note = "Source queried, but no admissible payload was found."
        else:
            support_note = "Source required by routing plan but not executed by the current executor."

        coverage_rows.append(
            {
                "source_family": row.get("source_family", ""),
                "source_name": row.get("source_name", ""),
                "priority": row.get("priority", ""),
                "queried": bool(row.get("queried", False)),
                "found": bool(row.get("found", False)),
                "authority": row.get("authority", ""),
                "scope": scope,
                "fields_expected": expected_fields,
                "fields_extracted": extracted_fields,
                "missing": missing,
                "matched_source_types": matched_source_types,
                "support_note": support_note,
            }
        )
    return coverage_rows


def _build_industry_adaptation_table(
    *,
    target_type: str,
    requestable_evidence_items: list[dict[str, Any]],
    scenario_space: list[dict[str, Any]],
    financial_exposure_rows: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    route = route_for_asset_type(target_type)
    route_name = str(getattr(route, "route_name", "") or "").strip() if route else ""
    routing_notes = list(getattr(route, "routing_notes", []) or []) if route else []
    primary_anchors = list(getattr(route, "primary_decision_anchors", []) or []) if route else []

    data_needs: list[str] = []
    for row in requestable_evidence_items:
        item = str(row.get("evidence_item", "")).strip()
        if item and item not in data_needs:
            data_needs.append(item)
        if len(data_needs) >= 6:
            break

    specific_risks: list[str] = []
    for row in financial_exposure_rows:
        risk = str(row.get("downside_if_wrong", "")).strip()
        if risk and risk not in specific_risks:
            specific_risks.append(risk)
        if len(specific_risks) >= 4:
            break
    for row in scenario_space:
        risk = str(row.get("financial_meaning", "")).strip()
        if risk and risk not in specific_risks:
            specific_risks.append(risk)
        if len(specific_risks) >= 4:
            break

    activated_logic_parts = []
    if route_name:
        activated_logic_parts.append(route_name)
    if primary_anchors:
        activated_logic_parts.append("Anchors: " + ", ".join(primary_anchors[:4]))
    if routing_notes:
        activated_logic_parts.append("Routing notes: " + " ".join(routing_notes[:4]))

    return [
        {
            "asset_type": str(target_type or "unknown").strip() or "unknown",
            "activated_industry_logic": " ".join(activated_logic_parts).strip() or "No asset-specific route declared.",
            "specific_data_needs": data_needs,
            "specific_risks": specific_risks,
        }
    ]


def _wrap_text(text: str, prefix: str = "  ", width: int = 68) -> list[str]:
    """Word-wrap text with a leading prefix, returning lines."""
    words = text.split()
    lines = []
    line = prefix
    for word in words:
        if len(line) + len(word) + 1 > width + len(prefix):
            lines.append(line)
            line = prefix + word + " "
        else:
            line += word + " "
    if line.strip():
        lines.append(line)
    return lines


_THESIS_SURFACE_CONCEPT_MARKER_MAP = {
    "denominator_reframe": {"denominator", "benchmark", "comparison", "peer", "intensity"},
    "boundary_reframe": {"boundary", "owner", "tenant", "control", "capture", "payer", "meter"},
    "tariff_logic": {"tariff", "demand", "peak", "charging", "schedule"},
    "thermal_exchange": {"dock", "infiltration", "thermal", "refrigeration", "hvac", "envelope"},
    "maintenance_reality": {"maintenance", "downtime", "reliability", "uptime"},
    "model_prematurity": {"model", "sensor", "digital", "instrumentation", "twin"},
}


def _thesis_surface_tokens(*values: Any) -> set[str]:
    tokens: set[str] = set()
    for value in values:
        queue = list(value) if isinstance(value, list) else [value]
        for item in queue:
            text = str(item or "").strip().lower()
            if not text:
                continue
            for token in re.split(r"[^a-z0-9]+", text):
                if len(token) >= 4:
                    tokens.add(token)
    return tokens


def _thesis_surface_concept_markers(*values: Any) -> set[str]:
    tokens = _thesis_surface_tokens(*values)
    markers: set[str] = set()
    for marker, required_tokens in _THESIS_SURFACE_CONCEPT_MARKER_MAP.items():
        if tokens.intersection(required_tokens):
            markers.add(marker)
    return markers


def _thesis_surface_overlap_ratio(left: Any, right: Any) -> float:
    left_tokens = _thesis_surface_tokens(left)
    right_tokens = _thesis_surface_tokens(right)
    if not left_tokens or not right_tokens:
        return 0.0
    shared = len(left_tokens.intersection(right_tokens))
    return shared / max(min(len(left_tokens), len(right_tokens)), 1)


def _thesis_surface_shared_token_count(left: Any, right: Any) -> int:
    return len(_thesis_surface_tokens(left).intersection(_thesis_surface_tokens(right)))


def _thesis_surface_is_semantically_redundant(
    candidate: Any,
    existing_values: list[Any],
    *,
    threshold: float = 0.65,
    allow_marker_collapse: bool = True,
    marker_overlap_token_floor: int = 1,
) -> bool:
    candidate_markers = _thesis_surface_concept_markers(candidate)
    for existing in list(existing_values or []):
        if _thesis_surface_overlap_ratio(candidate, existing) >= threshold:
            return True
        if not allow_marker_collapse:
            continue
        shared_markers = candidate_markers.intersection(_thesis_surface_concept_markers(existing))
        if shared_markers and _thesis_surface_shared_token_count(candidate, existing) >= marker_overlap_token_floor:
            return True
    return False


def _compact_executive_thesis_surface(
    *,
    spine_signals: list[str],
    strategic_gold_nuggets: list[str],
    thesis_constellation_focus: list[dict[str, Any]],
    differentiated_evidence_packs: list[dict[str, Any]],
    correlation_constellation_register: list[dict[str, Any]],
) -> dict[str, Any]:
    retained_spine_signals = [str(value).strip() for value in list(spine_signals or []) if str(value).strip()]
    compaction_register: list[dict[str, Any]] = []

    def _record(
        lane: str,
        label: str,
        text: str,
        *,
        state: str,
        reason: str,
        overlap_anchor: str = "",
    ) -> None:
        compaction_register.append(
            {
                "lane": lane,
                "label": label,
                "text": text,
                "state": state,
                "reason": reason,
                "overlap_anchor": overlap_anchor,
            }
        )

    def _first_redundant_anchor(
        signature: str,
        *,
        threshold: float,
        allow_marker_collapse: bool,
        marker_overlap_token_floor: int = 1,
    ) -> str:
        for existing in retained_spine_signals:
            if _thesis_surface_overlap_ratio(signature, existing) >= threshold:
                return existing
            if not allow_marker_collapse:
                continue
            shared_markers = _thesis_surface_concept_markers(signature).intersection(
                _thesis_surface_concept_markers(existing)
            )
            if shared_markers and _thesis_surface_shared_token_count(signature, existing) >= marker_overlap_token_floor:
                return existing
        return ""

    compacted_gold_nuggets: list[str] = []
    for nugget in list(strategic_gold_nuggets or []):
        text = str(nugget or "").strip()
        if not text:
            continue
        redundant_anchor = _first_redundant_anchor(
            text,
            threshold=0.58,
            allow_marker_collapse=True,
        )
        if redundant_anchor:
            if not compacted_gold_nuggets:
                compacted_gold_nuggets.append(text)
                retained_spine_signals.append(text)
                _record(
                    "gold_nugget",
                    "strategic_gold_nugget",
                    text,
                    state="retained_lane_floor",
                    reason="At least one bounded executive nugget remains visible even when it sharpens an already visible thesis spine.",
                    overlap_anchor=redundant_anchor,
                )
                continue
            _record(
                "gold_nugget",
                "strategic_gold_nugget",
                text,
                state="suppressed_semantic_overlap",
                reason="Strategic nugget repeats the already visible thesis spine.",
                overlap_anchor=redundant_anchor,
            )
            continue
        compacted_gold_nuggets.append(text)
        retained_spine_signals.append(text)
        _record(
            "gold_nugget",
            "strategic_gold_nugget",
            text,
            state="retained_visible_surface",
            reason="Strategic nugget adds executive novelty beyond the retained thesis spine.",
        )

    compacted_constellation: list[dict[str, Any]] = []
    for row in list(thesis_constellation_focus or []):
        element_type = str((row or {}).get("element_type", "")).strip()
        statement = str((row or {}).get("statement", "")).strip()
        signature = " ".join(
            value
            for value in [
                statement,
                str((row or {}).get("why_it_matters", "")).strip(),
                str((row or {}).get("differentiator", "")).strip(),
            ]
            if value
        )
        if not signature:
            continue
        allow_marker_collapse = element_type != "challenger_hypothesis"
        redundant_anchor = _first_redundant_anchor(
            signature,
            threshold=0.76 if element_type == "challenger_hypothesis" else 0.62,
            allow_marker_collapse=allow_marker_collapse,
            marker_overlap_token_floor=2 if element_type == "challenger_hypothesis" else 1,
        )
        if redundant_anchor:
            _record(
                "thesis_constellation",
                element_type or "constellation_lane",
                statement or signature,
                state="suppressed_semantic_overlap",
                reason=(
                    "Constellation row repeats the retained thesis spine."
                    if allow_marker_collapse
                    else "Challenger lane is only suppressed when it is genuinely overlapping, not merely concept-adjacent."
                ),
                overlap_anchor=redundant_anchor,
            )
            continue
        compacted_constellation.append(row)
        retained_spine_signals.append(signature)
        _record(
            "thesis_constellation",
            element_type or "constellation_lane",
            statement or signature,
            state="retained_visible_surface",
            reason="Constellation row adds a distinct rival or alternative structural lane.",
        )

    compacted_evidence_packs: list[dict[str, Any]] = []
    for idx, row in enumerate(list(differentiated_evidence_packs or [])):
        signature = " ".join(
            [
                str((row or {}).get("pack_title", "")).strip(),
                str((row or {}).get("why", "")).strip(),
                "; ".join(str(value).strip() for value in list((row or {}).get("unlocks", []) or []) if str(value).strip()),
                "; ".join(str(value).strip() for value in list((row or {}).get("evidence_items", []) or []) if str(value).strip()),
            ]
        ).strip()
        if not signature:
            continue
        redundant_anchor = _first_redundant_anchor(
            signature,
            threshold=0.76,
            allow_marker_collapse=True,
        )
        if redundant_anchor and idx > 0:
            _record(
                "evidence_pack",
                str((row or {}).get("pack_family", "")).strip() or "evidence_pack",
                str((row or {}).get("pack_title", "")).strip() or signature,
                state="suppressed_semantic_overlap",
                reason="Evidence pack repeats already visible discriminator logic.",
                overlap_anchor=redundant_anchor,
            )
            continue
        compacted_evidence_packs.append(row)
        retained_spine_signals.append(signature)
        _record(
            "evidence_pack",
            str((row or {}).get("pack_family", "")).strip() or "evidence_pack",
            str((row or {}).get("pack_title", "")).strip() or signature,
            state="retained_visible_surface",
            reason="Evidence pack adds distinct discriminator or proof logic.",
        )

    compacted_correlation_rows: list[dict[str, Any]] = []
    retained_correlation_signatures: list[str] = []
    for idx, row in enumerate(list(correlation_constellation_register or [])):
        signature = " ".join(
            [
                str((row or {}).get("correlation", "")).strip(),
                str((row or {}).get("strategic_meaning", "")).strip(),
                "; ".join(str(value).strip() for value in list((row or {}).get("evidence_needed", []) or []) if str(value).strip()),
            ]
        ).strip()
        if not signature:
            continue
        redundant_anchor = ""
        for existing in retained_correlation_signatures:
            if _thesis_surface_is_semantically_redundant(
                signature,
                [existing],
                threshold=0.74,
                allow_marker_collapse=True,
                marker_overlap_token_floor=2,
            ):
                redundant_anchor = existing
                break
        if redundant_anchor and idx > 0:
            _record(
                "correlation_constellation",
                "correlation_signal",
                str((row or {}).get("correlation", "")).strip() or signature,
                state="suppressed_semantic_overlap",
                reason="Correlation row restates already visible structural meaning.",
                overlap_anchor=redundant_anchor,
            )
            continue
        compacted_correlation_rows.append(row)
        retained_correlation_signatures.append(signature)
        retained_spine_signals.append(signature)
        _record(
            "correlation_constellation",
            "correlation_signal",
            str((row or {}).get("correlation", "")).strip() or signature,
            state="retained_visible_surface",
            reason="Correlation row adds distinct multi-layer reinforcement.",
        )

    summary = {
        "initial_gold_nugget_count": len(list(strategic_gold_nuggets or [])),
        "retained_gold_nugget_count": len(compacted_gold_nuggets),
        "initial_constellation_count": len(list(thesis_constellation_focus or [])),
        "retained_constellation_count": len(compacted_constellation),
        "initial_evidence_pack_count": len(list(differentiated_evidence_packs or [])),
        "retained_evidence_pack_count": len(compacted_evidence_packs),
        "initial_correlation_count": len(list(correlation_constellation_register or [])),
        "retained_correlation_count": len(compacted_correlation_rows),
        "suppressed_count": len(
            [row for row in compaction_register if str(row.get("state", "")).strip() == "suppressed_semantic_overlap"]
        ),
        "retained_count": len(
            [row for row in compaction_register if str(row.get("state", "")).strip() == "retained_visible_surface"]
        ),
    }

    return {
        "strategic_gold_nuggets": compacted_gold_nuggets,
        "thesis_constellation_focus": compacted_constellation,
        "differentiated_evidence_packs": compacted_evidence_packs,
        "correlation_constellation_register": compacted_correlation_rows,
        "thesis_surface_compaction_register": compaction_register,
        "thesis_surface_compaction_summary": summary,
    }


def _section(  # noqa: PLR0913
    sid: str,
    chapter_id: str,
    chapter_number: int,
    title: str,
    audience: str,
    section_type: str,
    epistemic_marker: str,
    llm_text: str,
    block_id: str,
    content: list[str],
    content_en: list[str] | None = None,
    content_es: list[str] | None = None,
    llm_text_en: str | None = None,
    llm_text_es: str | None = None,
    chart_ref: str = "",
    chart_b64: str = "",
    chart_b64_list: list[str] | None = None,
) -> dict:
    return {
        "section_id":      sid,
        "chapter_id":      chapter_id,
        "chapter_number":  str(chapter_number).zfill(2),
        "title":           title,
        "audience":        audience,
        "section_type":    section_type,
        "epistemic_marker": epistemic_marker,
        "llm_text":        llm_text,
        "llm_text_en":     llm_text if llm_text_en is None else llm_text_en,
        "llm_text_es":     llm_text if llm_text_es is None else llm_text_es,
        "chart_ref":       chart_ref,
        "chart_b64":       chart_b64,
        "chart_b64_list":  chart_b64_list or ([chart_b64] if chart_b64 else []),
        "block_ref":       block_id,
        "blocks":          [{
            "block_id": block_id,
            "content": "\n".join(content),
            "content_en": "\n".join(content_en if content_en is not None else content),
            "content_es": "\n".join(content_es if content_es is not None else content),
        }],
    }


def _is_structural_primary_output_type(report_type: str) -> bool:
    return str(report_type).strip() in STRUCTURAL_PRIMARY_OUTPUT_MODES


def _merge_structural_first_body_sections(
    legacy_body_sections: list[dict[str, Any]],
    structural_body_sections: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    preferred_titles = {
        "Framework Context & Executive Brief",
        "Operational Identity",
        "Energy Profile & Normative Constraints",
        "Blocking Conflicts",
        "Validation Architecture",
        "Conditional Opportunities",
        "Inference Case Map",
        "Tension Map",
        "Financial Context",
    }
    merged: list[dict[str, Any]] = []
    seen_titles: set[str] = set()
    preferred_legacy = [
        section
        for section in list(legacy_body_sections or [])
        if str(section.get("title", "")).strip() in preferred_titles
    ]
    for section in preferred_legacy + list(structural_body_sections or []) + list(legacy_body_sections or []):
        title = str(section.get("title", "")).strip()
        if not title or title in seen_titles:
            continue
        seen_titles.add(title)
        merged.append(section)
    return merged


def _outline_render_targets(main_report_outline: dict[str, Any]) -> list[str]:
    titles: list[str] = []
    for row in list(main_report_outline.get("sections", []) or []):
        render_targets = list(row.get("render_targets", []) or [])
        for title in render_targets:
            text = str(title).strip()
            if text:
                titles.append(text)
    return titles


def _compose_client_facing_body_sections(  # noqa: PLR0913
    *,
    main_report_outline: dict[str, Any],
    executive_thesis: dict[str, Any],
    client_facing_tad: dict[str, Any],
    problem_framing_register: list[dict[str, Any]],
    system_abstraction: dict[str, Any],
    cross_layer_conflict_register: list[dict[str, Any]],
    claim_contract_register: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    if not main_report_outline:
        return []

    def _text(value: Any, default: str = "NOT OBSERVED") -> str:
        text = str(value or "").strip()
        return text or default

    def _list_text(values: Any, default: str = "NONE") -> str:
        if isinstance(values, list):
            items = [str(value).strip() for value in values if str(value).strip()]
            return "; ".join(items) if items else default
        text = str(values or "").strip()
        return text or default

    def _system_field(key: str) -> tuple[str, str, str]:
        row = dict(system_abstraction.get(key, {}) or {})
        statement = _text(row.get("statement"))
        evidence_state = _text(row.get("evidence_state"))
        minimum_evidence = _list_text(row.get("minimum_evidence_required"))
        return statement, evidence_state, minimum_evidence

    primary_problem = dict(problem_framing_register[0] if problem_framing_register else {})
    if not primary_problem:
        primary_problem = {
            "stated_problem": _text(executive_thesis.get("declared_problem")),
            "reframed_problem": _text(executive_thesis.get("reframed_problem")),
            "why_original_framing_may_be_wrong": _text(executive_thesis.get("why_current_question_is_premature")),
            "strategic_risk": _text(executive_thesis.get("why_it_matters")) or _text(executive_thesis.get("dominant_risk")),
        }
    primary_conflict = dict(cross_layer_conflict_register[0] if cross_layer_conflict_register else {})
    if not primary_conflict:
        primary_conflict = {
            "conflict": _text(executive_thesis.get("dominant_contradiction")),
            "layers_involved": list(
                (
                    (executive_thesis.get("thesis_ranked_conflict_register", []) or [{}])[0] or {}
                ).get("layers_involved", [])
                or []
            ),
            "why_it_matters": _text(executive_thesis.get("why_it_matters")),
            "what_confirms_it": _list_text(executive_thesis.get("minimum_discriminating_evidence", []), default="NONE BOUNDED"),
            "what_falsifies_it": _text(executive_thesis.get("what_reality_feature_changes_the_decision")),
            "potential_redesign_direction": _text((executive_thesis.get("conditional_redesign", {}) or {}).get("redesign_direction")),
        }
    primary_financial = dict(executive_thesis.get("primary_financial_exposure", {}) or {})
    primary_peer = dict(executive_thesis.get("primary_peer_comparison", {}) or {})
    primary_redesign = dict(executive_thesis.get("conditional_redesign", {}) or {})
    peer_requirement_rows = list(primary_peer.get("peer_requirement_rows", []) or [])
    candidate_peer_frames = list(primary_peer.get("candidate_peer_frame_register", []) or [])
    better_practice_deltas = list(primary_peer.get("better_practice_delta_register", []) or [])
    peer_superiority_block_reason = _text(primary_peer.get("peer_superiority_block_reason"))
    top_variables = list(executive_thesis.get("top_dominant_variables", []) or [])
    top_scenarios = list(executive_thesis.get("top_scenarios", []) or [])
    top_actions = list((client_facing_tad or {}).get("actions", []) or [])
    conditional_pathways = list(
        executive_thesis.get("conditional_opportunity_pathways", [])
        or _build_conditional_opportunity_fallbacks(executive_thesis)
    )
    thesis_constellation_register = list(executive_thesis.get("thesis_constellation_register", []) or [])
    correlation_constellation_register = list(executive_thesis.get("correlation_constellation_register", []) or [])
    evidence_pack_register = list(executive_thesis.get("evidence_pack_register", []) or [])
    strategic_gold_nuggets = [
        str((row or {}).get("gold_nugget", "")).strip()
        for row in list(executive_thesis.get("top_gold_nuggets", []) or [])
        if str((row or {}).get("gold_nugget", "")).strip()
    ][:8]
    prohibited_claims = [
        str(value).strip()
        for value in list(executive_thesis.get("what_is_not_admissible", []) or [])
        if str(value).strip()
    ]
    admissible_actions = [
        str(value).strip()
        for value in list(executive_thesis.get("what_is_admissible_now", []) or [])
        if str(value).strip()
    ]
    supporting_modes = [
        str(value).strip()
        for value in list(executive_thesis.get("supporting_modes", []) or [])
        if str(value).strip()
    ]

    claim_permission_summary = {
        "allowed": 0,
        "conditional": 0,
        "prohibited": 0,
    }
    for row in list(claim_contract_register or []):
        permission = str(row.get("permission", "")).strip().lower()
        if permission == "allowed":
            claim_permission_summary["allowed"] += 1
        elif permission in {"conditional", "screening_only", "hypothesis_only"}:
            claim_permission_summary["conditional"] += 1
        elif permission == "prohibited":
            claim_permission_summary["prohibited"] += 1

    evidence_state = _text(executive_thesis.get("evidence_state"), default="uncertain")
    dominant_lens = _text(executive_thesis.get("dominant_lens"), default="NOT OBSERVED")
    thesis_state = _text(executive_thesis.get("thesis_state"), default="inadmissible_thesis")
    local_claim_closure_state = _text(executive_thesis.get("local_claim_closure_state"), default="unknown")
    conditional_intelligence_reason = _text(executive_thesis.get("conditional_intelligence_reason"), default="")
    minimum_evidence = list(executive_thesis.get("minimum_discriminating_evidence", []) or [])
    minimum_evidence_text = _list_text(minimum_evidence, default="NONE BOUNDED")
    evidence_unlocks = _list_text(
        executive_thesis.get("minimum_discriminating_evidence_unlocks", []),
        default="NONE BOUNDED",
    )
    report_mode = _text(main_report_outline.get("visible_report_mode") or executive_thesis.get("report_mode"))

    section_anchors = {
        "executive_structural_thesis": (
            "dominant_contradiction",
            _text(executive_thesis.get("dominant_contradiction")),
        ),
        "reframed_problem": (
            "reframed_problem",
            _text(executive_thesis.get("reframed_problem")),
        ),
        "dominant_structural_contradiction": (
            "dominant_contradiction",
            _text(executive_thesis.get("dominant_contradiction")),
        ),
        "system_abstraction_snapshot": (
            "reframed_problem",
            _text(executive_thesis.get("reframed_problem")),
        ),
        "dominant_variables": (
            "dominant_contradiction",
            _text(executive_thesis.get("dominant_contradiction")),
        ),
        "scenario_space": (
            "minimum_discriminating_evidence",
            minimum_evidence_text,
        ),
        "financial_exposure": (
            "dominant_contradiction",
            _text(executive_thesis.get("dominant_contradiction")),
        ),
        "peer_comparison": (
            "dominant_contradiction",
            _text(executive_thesis.get("dominant_contradiction")),
        ),
        "conditional_redesign": (
            "dominant_contradiction",
            _text(executive_thesis.get("dominant_contradiction")),
        ),
        "minimum_evidence": (
            "minimum_discriminating_evidence",
            minimum_evidence_text,
        ),
        "tad": (
            "minimum_discriminating_evidence",
            minimum_evidence_text,
        ),
        "claim_permissions": (
            "dominant_contradiction",
            _text(executive_thesis.get("dominant_contradiction")),
        ),
    }

    thesis_constellation_focus = [
        row
        for row in thesis_constellation_register
        if str((row or {}).get("element_type", "")).strip()
        not in {"dominant_contradiction", "strategic_nugget"}
    ][:8]

    differentiated_evidence_packs = evidence_pack_register[:4]
    thesis_surface_compaction = _compact_executive_thesis_surface(
        spine_signals=[
            _text(executive_thesis.get("reframed_problem"), default=""),
            _text(executive_thesis.get("dominant_contradiction"), default=""),
            _text(executive_thesis.get("why_current_question_is_premature"), default=""),
            conditional_intelligence_reason,
            _text(executive_thesis.get("dominant_operational_misunderstanding"), default=""),
            _text(executive_thesis.get("hidden_system_boundary_error"), default=""),
            _text(executive_thesis.get("why_it_matters"), default=""),
            _text(executive_thesis.get("dominant_risk"), default=""),
            _text(executive_thesis.get("surprising_but_evidenced_takeaway"), default=""),
        ],
        strategic_gold_nuggets=strategic_gold_nuggets,
        thesis_constellation_focus=thesis_constellation_focus,
        differentiated_evidence_packs=differentiated_evidence_packs,
        correlation_constellation_register=correlation_constellation_register[:4],
    )
    strategic_gold_nuggets = list(thesis_surface_compaction.get("strategic_gold_nuggets", []) or [])
    thesis_constellation_focus = list(thesis_surface_compaction.get("thesis_constellation_focus", []) or [])
    differentiated_evidence_packs = list(thesis_surface_compaction.get("differentiated_evidence_packs", []) or [])
    correlation_constellation_register = list(
        thesis_surface_compaction.get("correlation_constellation_register", []) or []
    )
    thesis_surface_compaction_register = list(
        thesis_surface_compaction.get("thesis_surface_compaction_register", []) or []
    )
    thesis_surface_compaction_summary = dict(
        thesis_surface_compaction.get("thesis_surface_compaction_summary", {}) or {}
    )

    def _build_surface_readout_rows(
        rows: list[dict[str, str]],
        *,
        protected_signals: set[str] | None = None,
        threshold: float = 0.66,
    ) -> list[dict[str, str]]:
        compacted_rows: list[dict[str, str]] = []
        retained_signatures: list[str] = []
        protected = {str(value).strip() for value in list(protected_signals or set()) if str(value).strip()}
        for row in rows:
            signal = _text(row.get("signal"), default="")
            statement = _text(row.get("statement"), default="")
            why_now = _text(row.get("why_now"), default="")
            if not signal or not statement:
                continue
            signature = " ".join(value for value in [signal, statement, why_now] if value)
            if signal in protected and not any(_text(existing.get("signal"), default="") == signal for existing in compacted_rows):
                compacted_rows.append({"signal": signal, "statement": statement, "why_now": why_now})
                retained_signatures.append(signature)
                continue
            if _thesis_surface_is_semantically_redundant(
                signature,
                retained_signatures,
                threshold=threshold,
                allow_marker_collapse=True,
                marker_overlap_token_floor=2,
            ):
                continue
            compacted_rows.append({"signal": signal, "statement": statement, "why_now": why_now})
            retained_signatures.append(signature)
        return compacted_rows

    thesis_surface_readout_register: list[dict[str, str]] = []

    def _append_thesis_surface_readout(signal: str, statement: str, *, why_now: str = "") -> None:
        clean_statement = _text(statement, default="")
        if not clean_statement:
            return
        thesis_surface_readout_register.append(
            {
                "signal": signal,
                "statement": clean_statement,
                "why_now": _text(why_now, default=""),
            }
        )

    top_variable_row = dict(top_variables[0] if top_variables else {})
    top_variable_name = _text(top_variable_row.get("variable"), default="")
    top_variable_why = _text(
        top_variable_row.get("why_it_could_matter") or top_variable_row.get("decision_impact"),
        default="",
    )

    _append_thesis_surface_readout(
        "Framing Risk",
        _text(primary_problem.get("why_original_framing_may_be_wrong")),
        why_now=_text(executive_thesis.get("reframed_problem")),
    )
    _append_thesis_surface_readout(
        "Dominant Variable Shift",
        top_variable_why or _text(executive_thesis.get("dominant_operational_misunderstanding")),
        why_now=top_variable_name or _text(executive_thesis.get("dominant_contradiction")),
    )
    _append_thesis_surface_readout(
        "Capital-at-Risk Logic",
        _text(primary_financial.get("financial_exposure_if_wrong"))
        or _text(executive_thesis.get("dominant_risk")),
        why_now=_text(executive_thesis.get("capital_logic_if_assumption_breaks")),
    )
    _append_thesis_surface_readout(
        "Comparison / Boundary Warning",
        _text(executive_thesis.get("invalid_comparison_risk"))
        or _text(executive_thesis.get("hidden_system_boundary_error")),
        why_now=_text(executive_thesis.get("hidden_system_boundary_error")),
    )
    _append_thesis_surface_readout(
        "Minimum Evidence Pivot",
        _text(executive_thesis.get("what_reality_feature_changes_the_decision"))
        or minimum_evidence_text,
        why_now=minimum_evidence_text,
    )

    # Avoid a long block of quasi-duplicate strategic readouts on the visible surface.
    thesis_surface_readout_register = _build_surface_readout_rows(
        thesis_surface_readout_register,
        protected_signals={
            "Framing Risk",
            "Dominant Variable Shift",
            "Capital-at-Risk Logic",
            "Minimum Evidence Pivot",
        },
        threshold=0.66,
    )[:5]

    financial_surface_readout_register = _build_surface_readout_rows(
        [
            {
                "signal": "Cost-of-Wrong-Question",
                "statement": _text(primary_financial.get("financial_exposure_if_wrong"))
                or _text(executive_thesis.get("dominant_risk")),
                "why_now": _text(primary_financial.get("structural_assumption")),
            },
            {
                "signal": "Boundary / Capture Logic",
                "statement": _text(executive_thesis.get("hidden_system_boundary_error"))
                or _text(primary_financial.get("structural_assumption")),
                "why_now": _text(executive_thesis.get("capital_logic_if_assumption_breaks")),
            },
            {
                "signal": "Evidence Pivot",
                "statement": _list_text(primary_financial.get("evidence_needed", []), default=""),
                "why_now": _list_text(primary_financial.get("allowed_financial_output", []), default=""),
            },
        ],
        protected_signals={"Cost-of-Wrong-Question", "Evidence Pivot"},
        threshold=0.68,
    )[:3]

    peer_surface_readout_register = _build_surface_readout_rows(
        [
            {
                "signal": "Comparison Gate",
                "statement": _text(executive_thesis.get("invalid_comparison_risk")),
                "why_now": _text(primary_peer.get("what_it_proves")),
            },
            {
                "signal": "Valid Peer Frame",
                "statement": _text((candidate_peer_frames[0] if candidate_peer_frames else {}).get("candidate_peer_frame")),
                "why_now": _text((candidate_peer_frames[0] if candidate_peer_frames else {}).get("why_it_matters")),
            },
            {
                "signal": "Practice Delta To Test",
                "statement": _text((better_practice_deltas[0] if better_practice_deltas else {}).get("practice_delta")),
                "why_now": _text((better_practice_deltas[0] if better_practice_deltas else {}).get("why_plausible")),
            },
        ],
        protected_signals={"Comparison Gate"},
        threshold=0.68,
    )[:3]

    tad_surface_readout_register = _build_surface_readout_rows(
        [
            {
                "signal": "Decision Front",
                "statement": _text((top_actions[0] if top_actions else {}).get("decision_front")),
                "why_now": _text((top_actions[0] if top_actions else {}).get("why")),
            },
            {
                "signal": "Protect Capital From",
                "statement": _text((top_actions[0] if top_actions else {}).get("financial_exposure")),
                "why_now": _text((top_actions[0] if top_actions else {}).get("prohibited_action_class")),
            },
            {
                "signal": "Do Not Do Yet",
                "statement": _text((top_actions[0] if top_actions else {}).get("prohibited_action")),
                "why_now": _text((top_actions[0] if top_actions else {}).get("evidence_needed")),
            },
        ],
        protected_signals={"Decision Front", "Do Not Do Yet"},
        threshold=0.68,
    )[:3]

    section_surface_readout_map = {
        "executive_structural_thesis": thesis_surface_readout_register,
        "financial_exposure": financial_surface_readout_register,
        "peer_comparison": peer_surface_readout_register,
        "tad": tad_surface_readout_register,
    }

    def _token_set(*values: Any) -> set[str]:
        tokens: set[str] = set()
        for value in values:
            queue = list(value) if isinstance(value, list) else [value]
            for item in queue:
                text = str(item or "").strip().lower()
                if not text:
                    continue
                for token in re.split(r"[^a-z0-9]+", text):
                    if len(token) >= 4:
                        tokens.add(token)
        return tokens

    def _best_pack(
        *signals: Any,
        preferred_families: list[str] | None = None,
    ) -> dict[str, Any]:
        preferred = [str(value).strip() for value in list(preferred_families or []) if str(value).strip()]
        for family in preferred:
            for row in evidence_pack_register:
                if _text(row.get("pack_family")) == family:
                    return row
        signal_tokens = _token_set(*signals)
        best_row: dict[str, Any] = {}
        best_score = -1
        for row in evidence_pack_register:
            row_tokens = _token_set(
                row.get("pack_title"),
                row.get("pack_family"),
                row.get("evidence_items", []),
                row.get("unlocks", []),
                row.get("why"),
            )
            score = len(signal_tokens.intersection(row_tokens))
            if score > best_score:
                best_score = score
                best_row = row
        return best_row

    def _constellation_rows_for_pack(
        pack_family: str,
        *,
        preferred_types: list[str] | None = None,
        limit: int = 3,
    ) -> list[dict[str, Any]]:
        rows = [
            row
            for row in thesis_constellation_register
            if _text(row.get("evidence_pack_family")) == pack_family
        ]
        preferred = [str(value).strip() for value in list(preferred_types or []) if str(value).strip()]
        if preferred:
            rows.sort(
                key=lambda row: (
                    0 if _text(row.get("element_type")) in preferred else 1,
                    thesis_constellation_register.index(row),
                )
            )
        return rows[:limit]

    fair_comparison_pack = _best_pack(
        primary_peer.get("peer_type"),
        primary_peer.get("what_it_proves"),
        executive_thesis.get("invalid_comparison_risk"),
        preferred_families=["fair_comparison_pack"],
    )
    financial_logic_pack = _best_pack(
        primary_financial.get("structural_assumption"),
        primary_financial.get("financial_exposure_if_wrong"),
        executive_thesis.get("hidden_system_boundary_error"),
        executive_thesis.get("dominant_risk"),
        preferred_families=["control_boundary_pack", "capital_logic_pack"],
    )

    def _section_from_lines(
        *,
        idx: int,
        section_key: str,
        title: str,
        content_en: list[str],
        content_es: list[str],
    ) -> dict[str, Any]:
        anchor_type, anchor_text = section_anchors.get(section_key, ("reframed_problem", _text(executive_thesis.get("reframed_problem"))))
        row = _section(
            sid=f"cf_{section_key}",
            chapter_id=f"C{idx}",
            chapter_number=idx,
            title=title,
            audience="executive",
            section_type="body",
            epistemic_marker="CLIENT_FACING_THESIS",
            llm_text="",
            block_id=f"b_{section_key}",
            content=content_en,
            content_en=content_en,
            content_es=content_es,
        )
        row["outline_section_key"] = section_key
        row["thesis_anchor_type"] = anchor_type
        row["thesis_anchor_text"] = anchor_text
        if section_key == "executive_structural_thesis":
            row["thesis_surface_compaction_register"] = thesis_surface_compaction_register
            row["thesis_surface_compaction_summary"] = thesis_surface_compaction_summary
            row["thesis_surface_readout_register"] = thesis_surface_readout_register
        if section_key in section_surface_readout_map:
            row["section_surface_readout_register"] = list(section_surface_readout_map.get(section_key, []) or [])
        return row

    composed: list[dict[str, Any]] = []
    for idx, outline_row in enumerate(list(main_report_outline.get("sections", []) or []), start=1):
        section_key = str(outline_row.get("section_key", "")).strip()
        title = str(outline_row.get("title", "")).strip()
        if not title or not section_key:
            continue
        if section_key == "executive_structural_thesis":
            content_en = [
                _sep("="),
                "EXECUTIVE STRUCTURAL THESIS",
                _sep("="),
                "",
                f"  Declared Problem     : {_text(executive_thesis.get('declared_problem'))}",
                f"  Reframed Problem     : {_text(executive_thesis.get('reframed_problem'))}",
                f"  Thesis State         : {thesis_state}",
                f"  Local Claim Closure  : {local_claim_closure_state}",
                f"  Dominant Contradiction: {_text(executive_thesis.get('dominant_contradiction'))}",
                f"  Hidden Assumption At Risk: {_text(executive_thesis.get('hidden_assumption_at_risk'))}",
                f"  Why The Question Is Premature: {_text(executive_thesis.get('why_current_question_is_premature'))}",
                f"  Conditional Intelligence Reason: {conditional_intelligence_reason or 'NOT OBSERVED'}",
                f"  Dominant Misunderstanding: {_text(executive_thesis.get('dominant_operational_misunderstanding'))}",
                f"  Hidden Boundary Error: {_text(executive_thesis.get('hidden_system_boundary_error'))}",
                f"  Reality Feature That Changes The Decision: {_text(executive_thesis.get('what_reality_feature_changes_the_decision'))}",
                f"  Why It Matters       : {_text(executive_thesis.get('why_it_matters'))}",
                f"  Immediate Action     : {_list_text(admissible_actions, default='NONE BOUNDED')}",
                f"  Prohibited Actions   : {_list_text(prohibited_claims, default='NONE BOUNDED')}",
                f"  Financial Exposure If Wrong: {_text(executive_thesis.get('dominant_risk'))}",
                f"  Capital Logic If It Holds: {_text(executive_thesis.get('capital_logic_if_assumption_holds'))}",
                f"  Capital Logic If It Breaks: {_text(executive_thesis.get('capital_logic_if_assumption_breaks'))}",
                f"  Surprising But Evidenced Takeaway: {_text(executive_thesis.get('surprising_but_evidenced_takeaway'))}",
                f"  Primary Strategic Gold Nugget: {_text(strategic_gold_nuggets[0] if strategic_gold_nuggets else '', default='NONE BOUNDED')}",
                f"  Evidence State       : {evidence_state}",
                f"  Visible Report Mode  : {report_mode}",
                f"  Dominant Lens        : {dominant_lens}",
                f"  Supporting Modes     : {_list_text(supporting_modes, default='NONE')}",
                "",
            ]
            if thesis_surface_readout_register:
                content_en += ["  Strategic Reading:", ""]
                for row in thesis_surface_readout_register:
                    content_en += [
                        f"    - {_text(row.get('signal'))}: {_text(row.get('statement'))}",
                    ]
                    if _text(row.get("why_now"), default=""):
                        content_en += [f"      Why Now : {_text(row.get('why_now'))}"]
                    content_en += [""]
            if len(strategic_gold_nuggets) > 1:
                content_en += ["  Strategic Gold Nugget Set:", ""]
                for nugget in strategic_gold_nuggets[:8]:
                    content_en += [
                        f"    - {nugget}",
                        "",
                    ]
            if thesis_constellation_focus:
                content_en += ["  Rival Thesis Constellation:", ""]
                for row in thesis_constellation_focus:
                    content_en += [
                        f"    - {_text(row.get('title'))}: {_text(row.get('statement'))}",
                        f"      Why It Matters : {_text(row.get('why_it_matters'))}",
                        f"      Differentiator : {_text(row.get('differentiator'))}",
                        f"      Evidence Pack  : {_text(row.get('evidence_pack_family'), default='NONE BOUNDED')}",
                        "",
                    ]
            if differentiated_evidence_packs:
                content_en += ["  Differentiated Evidence Packs:", ""]
                for row in differentiated_evidence_packs:
                    content_en += [
                        f"    - {_text(row.get('pack_title'))} [{_text(row.get('evidence_state'), default='CONDITIONAL_HYPOTHESIS')}]",
                        f"      Evidence : {_list_text(row.get('evidence_items', []), default='NONE BOUNDED')}",
                        f"      Unlocks  : {_list_text(row.get('unlocks', []), default='NONE BOUNDED')}",
                        f"      Why      : {_text(row.get('why'))}",
                        "",
                    ]
            if correlation_constellation_register:
                content_en += ["  Correlation Constellation Signals:", ""]
                for row in correlation_constellation_register[:4]:
                    content_en += [
                        f"    - {_text(row.get('correlation'))}",
                        f"      Linked Conflict : {_text(row.get('linked_conflict'))}",
                        f"      Strategic Meaning: {_text(row.get('strategic_meaning'))}",
                        f"      Evidence Needed : {_list_text(row.get('evidence_needed', []), default='NONE BOUNDED')}",
                        "",
                    ]
            content_es = [
                _sep("="),
                "TESIS ESTRUCTURAL EJECUTIVA",
                _sep("="),
                "",
                f"  Problema Declarado   : {_text(executive_thesis.get('declared_problem'))}",
                f"  Problema Reencuadrado: {_text(executive_thesis.get('reframed_problem'))}",
                f"  Estado de la Tesis   : {thesis_state}",
                f"  Cierre de Claim Local: {local_claim_closure_state}",
                f"  Contradicción Dominante: {_text(executive_thesis.get('dominant_contradiction'))}",
                f"  Suposición en Riesgo : {_text(executive_thesis.get('hidden_assumption_at_risk'))}",
                f"  Por Qué la Pregunta Es Prematura: {_text(executive_thesis.get('why_current_question_is_premature'))}",
                f"  Razón de Inteligencia Condicional: {conditional_intelligence_reason or 'NO OBSERVADA'}",
                f"  Malentendido Dominante: {_text(executive_thesis.get('dominant_operational_misunderstanding'))}",
                f"  Error Oculto de Frontera: {_text(executive_thesis.get('hidden_system_boundary_error'))}",
                f"  Rasgo de la Realidad que Cambia la Decisión: {_text(executive_thesis.get('what_reality_feature_changes_the_decision'))}",
                f"  Por Qué Importa      : {_text(executive_thesis.get('why_it_matters'))}",
                f"  Acción Inmediata     : {_list_text(admissible_actions, default='NINGUNA ACOTADA')}",
                f"  Acciones Prohibidas  : {_list_text(prohibited_claims, default='NINGUNA ACOTADA')}",
                f"  Exposición Si Es Falso: {_text(executive_thesis.get('dominant_risk'))}",
                f"  Lógica de Capital Si Se Confirma: {_text(executive_thesis.get('capital_logic_if_assumption_holds'))}",
                f"  Lógica de Capital Si Se Rompe: {_text(executive_thesis.get('capital_logic_if_assumption_breaks'))}",
                f"  Hallazgo Sorprendente Pero Sustentado: {_text(executive_thesis.get('surprising_but_evidenced_takeaway'))}",
                f"  Gold Nugget Estratégico Primario: {_text(strategic_gold_nuggets[0] if strategic_gold_nuggets else '', default='NINGUNO ACOTADO')}",
                f"  Estado de Evidencia  : {evidence_state}",
                f"  Modo Visible         : {report_mode}",
                f"  Lente Dominante      : {dominant_lens}",
                f"  Modos de Soporte     : {_list_text(supporting_modes, default='NINGUNO')}",
                "",
            ]
            if thesis_surface_readout_register:
                content_es += ["  Lectura Estratégica:", ""]
                for row in thesis_surface_readout_register:
                    content_es += [
                        f"    - {_text(row.get('signal'))}: {_text(row.get('statement'))}",
                    ]
                    if _text(row.get("why_now"), default=""):
                        content_es += [f"      Por Qué Ahora: {_text(row.get('why_now'))}"]
                    content_es += [""]
            if len(strategic_gold_nuggets) > 1:
                content_es += ["  Set de Gold Nuggets Estratégicos:", ""]
                for nugget in strategic_gold_nuggets[:8]:
                    content_es += [
                        f"    - {nugget}",
                        "",
                    ]
            if thesis_constellation_focus:
                content_es += ["  Constelación de Hipótesis Rivales:", ""]
                for row in thesis_constellation_focus:
                    content_es += [
                        f"    - {_text(row.get('title'))}: {_text(row.get('statement'))}",
                        f"      Por Qué Importa : {_text(row.get('why_it_matters'))}",
                        f"      Diferenciador   : {_text(row.get('differentiator'))}",
                        f"      Pack de Evidencia: {_text(row.get('evidence_pack_family'), default='NINGUNO ACOTADO')}",
                        "",
                    ]
            if correlation_constellation_register:
                content_es += ["  Señales de Constelación de Correlaciones:", ""]
                for row in correlation_constellation_register[:4]:
                    content_es += [
                        f"    - {_text(row.get('correlation'))}",
                        f"      Conflicto Vinculado: {_text(row.get('linked_conflict'))}",
                        f"      Significado Estratégico: {_text(row.get('strategic_meaning'))}",
                        f"      Evidencia Necesaria : {_list_text(row.get('evidence_needed', []), default='NINGUNA ACOTADA')}",
                        "",
                    ]
            if differentiated_evidence_packs:
                content_es += ["  Packs de Evidencia Diferenciados:", ""]
                for row in differentiated_evidence_packs:
                    content_es += [
                        f"    - {_text(row.get('pack_title'))} [{_text(row.get('evidence_state'), default='CONDITIONAL_HYPOTHESIS')}]",
                        f"      Evidencia : {_list_text(row.get('evidence_items', []), default='NINGUNA ACOTADA')}",
                        f"      Desbloquea: {_list_text(row.get('unlocks', []), default='NINGUNA ACOTADA')}",
                        f"      Por Qué   : {_text(row.get('why'))}",
                        "",
                    ]
        elif section_key == "reframed_problem":
            content_en = [
                _sep("="),
                "REFRAMED PROBLEM",
                _sep("="),
                "",
                f"  Client-Stated Problem: {_text(executive_thesis.get('declared_problem'))}",
                f"  System Reframe      : {_text(executive_thesis.get('reframed_problem'))}",
                f"  Why Original Framing May Be Wrong: {_text(primary_problem.get('why_original_framing_may_be_wrong'))}",
                f"  Strategic Risk      : {_text(primary_problem.get('strategic_risk'))}",
                "",
            ]
            content_es = [
                _sep("="),
                "PROBLEMA REENCUADRADO",
                _sep("="),
                "",
                f"  Problema Declarado por el Cliente: {_text(executive_thesis.get('declared_problem'))}",
                f"  Reencuadre del Sistema: {_text(executive_thesis.get('reframed_problem'))}",
                f"  Por Qué el Marco Original Puede Estar Mal: {_text(primary_problem.get('why_original_framing_may_be_wrong'))}",
                f"  Riesgo Estratégico  : {_text(primary_problem.get('strategic_risk'))}",
                "",
            ]
        elif section_key == "dominant_structural_contradiction":
            content_en = [
                _sep("="),
                "DOMINANT STRUCTURAL CONTRADICTION",
                _sep("="),
                "",
                f"  Conflict            : {_text(primary_conflict.get('conflict'))}",
                f"  Layers Involved     : {_list_text(primary_conflict.get('layers_involved', []))}",
                f"  Why It Matters      : {_text(primary_conflict.get('why_it_matters'))}",
                f"  What Confirms It    : {_text(primary_conflict.get('what_confirms_it'))}",
                f"  What Falsifies It   : {_text(primary_conflict.get('what_falsifies_it'))}",
                f"  Potential Redesign  : {_text(primary_conflict.get('potential_redesign_direction'))}",
                "",
            ]
            content_es = [
                _sep("="),
                "CONTRADICCIÓN ESTRUCTURAL DOMINANTE",
                _sep("="),
                "",
                f"  Conflicto           : {_text(primary_conflict.get('conflict'))}",
                f"  Capas Involucradas  : {_list_text(primary_conflict.get('layers_involved', []))}",
                f"  Por Qué Importa     : {_text(primary_conflict.get('why_it_matters'))}",
                f"  Qué la Confirma     : {_text(primary_conflict.get('what_confirms_it'))}",
                f"  Qué la Falsifica    : {_text(primary_conflict.get('what_falsifies_it'))}",
                f"  Rediseño Potencial  : {_text(primary_conflict.get('potential_redesign_direction'))}",
                "",
            ]
        elif section_key == "system_abstraction_snapshot":
            asset_type, asset_type_state, asset_type_minimum = _system_field("asset_type")
            business_function, business_state, business_minimum = _system_field("business_function")
            value_mechanism, value_state, value_minimum = _system_field("value_creation_mechanism")
            control_structure, control_state, control_minimum = _system_field("control_structure")
            regulatory_exposure, regulatory_state, regulatory_minimum = _system_field("regulatory_exposure")
            content_en = [
                _sep("="),
                "SYSTEM ABSTRACTION SNAPSHOT",
                _sep("="),
                "",
                f"  Asset Type          : {asset_type} [{asset_type_state}]",
                f"  Business Function   : {business_function} [{business_state}]",
                f"  Value Mechanism     : {value_mechanism} [{value_state}]",
                f"  Control Structure   : {control_structure} [{control_state}]",
                f"  Regulatory Exposure : {regulatory_exposure} [{regulatory_state}]",
                f"  Minimum Evidence    : {_list_text([asset_type_minimum, business_minimum, value_minimum, control_minimum, regulatory_minimum], default='NONE BOUNDED')}",
                "",
            ]
            content_es = [
                _sep("="),
                "FOTOGRAFÍA DE LA ABSTRACCIÓN DEL SISTEMA",
                _sep("="),
                "",
                f"  Tipo de Activo      : {asset_type} [{asset_type_state}]",
                f"  Función de Negocio  : {business_function} [{business_state}]",
                f"  Mecanismo de Valor  : {value_mechanism} [{value_state}]",
                f"  Estructura de Control: {control_structure} [{control_state}]",
                f"  Exposición Regulatoria: {regulatory_exposure} [{regulatory_state}]",
                f"  Evidencia Mínima    : {_list_text([asset_type_minimum, business_minimum, value_minimum, control_minimum, regulatory_minimum], default='NINGUNA ACOTADA')}",
                "",
            ]
        elif section_key == "dominant_variables":
            content_en = [_sep("="), "DOMINANT VARIABLES", _sep("="), ""]
            content_es = [_sep("="), "VARIABLES DOMINANTES", _sep("="), ""]
            if not top_variables:
                content_en += ["  No dominant variable rows were selected into the thesis.", ""]
                content_es += ["  No se seleccionaron variables dominantes para la tesis.", ""]
            for row in top_variables:
                content_en += [
                    f"  Variable            : {_text(row.get('variable'))}",
                    f"  Layer               : {_text(row.get('layer'))}",
                    f"  Evidence State      : {_text(row.get('evidence_state'))}",
                    f"  Why It Could Matter : {_text(row.get('why_it_could_matter'))}",
                    f"  Decision Impact     : {_text(row.get('decision_impact'))}",
                    "",
                ]
                content_es += [
                    f"  Variable            : {_text(row.get('variable'))}",
                    f"  Capa                : {_text(row.get('layer'))}",
                    f"  Estado de Evidencia : {_text(row.get('evidence_state'))}",
                    f"  Por Qué Podría Importar: {_text(row.get('why_it_could_matter'))}",
                    f"  Impacto en la Decisión: {_text(row.get('decision_impact'))}",
                    "",
                ]
            dominant_loss_logic = _text(executive_thesis.get("dominant_loss_logic"), default="")
            if dominant_loss_logic:
                content_en += [f"  Dominant Loss Logic : {dominant_loss_logic}", ""]
                content_es += [f"  Lógica Dominante de Pérdida: {dominant_loss_logic}", ""]
        elif section_key == "scenario_space":
            content_en = [_sep("="), "SCENARIO SPACE", _sep("="), ""]
            content_es = [_sep("="), "ESPACIO DE ESCENARIOS", _sep("="), ""]
            if not top_scenarios:
                content_en += ["  No thesis-priority scenarios were selected.", ""]
                content_es += ["  No se seleccionaron escenarios prioritarios para la tesis.", ""]
            for row in top_scenarios:
                content_en += [
                    f"  Scenario            : {_text(row.get('scenario'))}",
                    f"  Financial Meaning   : {_text(row.get('financial_meaning'))}",
                    f"  Evidence Needed     : {_text(row.get('evidence_needed'))}",
                    f"  Falsification       : {_text(row.get('falsification_condition'))}",
                    "",
                ]
                content_es += [
                    f"  Escenario           : {_text(row.get('scenario'))}",
                    f"  Sentido Financiero  : {_text(row.get('financial_meaning'))}",
                    f"  Evidencia Necesaria : {_text(row.get('evidence_needed'))}",
                    f"  Falsación           : {_text(row.get('falsification_condition'))}",
                    "",
                ]
        elif section_key == "financial_exposure":
            financial_support_rows = _constellation_rows_for_pack(
                _text(financial_logic_pack.get("pack_family")),
                preferred_types=["boundary_failure", "dominant_variable_candidate", "alternative_variable_candidate"],
                limit=3,
            )
            content_en = [
                _sep("="),
                "FINANCIAL EXPOSURE UNDER UNCERTAINTY",
                _sep("="),
                "",
                f"  Structural Assumption: {_text(primary_financial.get('structural_assumption'))}",
                f"  Evidence State       : {_text(primary_financial.get('evidence_state'))}",
                f"  Exposure If Wrong    : {_text(primary_financial.get('financial_exposure_if_wrong'))}",
                f"  Evidence Needed      : {_list_text(primary_financial.get('evidence_needed', []), default='NONE BOUNDED')}",
                f"  Allowed Output       : {_list_text(primary_financial.get('allowed_financial_output', []), default='NONE BOUNDED')}",
                f"  Prohibited Output    : {_list_text(primary_financial.get('prohibited_financial_output', []), default='NONE BOUNDED')}",
                "",
            ]
            if financial_surface_readout_register:
                content_en += ["  Strategic Reading:", ""]
                for row in financial_surface_readout_register:
                    content_en += [
                        f"    - {_text(row.get('signal'))}: {_text(row.get('statement'))}",
                    ]
                    if _text(row.get("why_now"), default=""):
                        content_en += [f"      Why Now : {_text(row.get('why_now'))}"]
                    content_en += [""]
            if financial_logic_pack:
                content_en += [
                    "  Financial Logic Pack:",
                    "",
                    f"    - {_text(financial_logic_pack.get('pack_title'))}",
                    f"      Evidence : {_list_text(financial_logic_pack.get('evidence_items', []), default='NONE BOUNDED')}",
                    f"      Unlocks  : {_list_text(financial_logic_pack.get('unlocks', []), default='NONE BOUNDED')}",
                    f"      Why      : {_text(financial_logic_pack.get('why'))}",
                    "",
                ]
            if financial_support_rows:
                content_en += ["  Linked Structural Lanes:", ""]
                for row in financial_support_rows:
                    content_en += [
                        f"    - {_text(row.get('title'))}: {_text(row.get('statement'))}",
                        f"      Why It Matters : {_text(row.get('why_it_matters'))}",
                        "",
                    ]
            content_es = [
                _sep("="),
                "EXPOSICIÓN FINANCIERA BAJO INCERTIDUMBRE",
                _sep("="),
                "",
                f"  Supuesto Estructural : {_text(primary_financial.get('structural_assumption'))}",
                f"  Estado de Evidencia  : {_text(primary_financial.get('evidence_state'))}",
                f"  Exposición Si Es Falso: {_text(primary_financial.get('financial_exposure_if_wrong'))}",
                f"  Evidencia Necesaria  : {_list_text(primary_financial.get('evidence_needed', []), default='NINGUNA ACOTADA')}",
                f"  Salida Permitida     : {_list_text(primary_financial.get('allowed_financial_output', []), default='NINGUNA ACOTADA')}",
                f"  Salida Prohibida     : {_list_text(primary_financial.get('prohibited_financial_output', []), default='NINGUNA ACOTADA')}",
                "",
            ]
            if financial_surface_readout_register:
                content_es += ["  Lectura Estratégica:", ""]
                for row in financial_surface_readout_register:
                    content_es += [
                        f"    - {_text(row.get('signal'))}: {_text(row.get('statement'))}",
                    ]
                    if _text(row.get("why_now"), default=""):
                        content_es += [f"      Por Qué Ahora: {_text(row.get('why_now'))}"]
                    content_es += [""]
            if financial_logic_pack:
                content_es += [
                    "  Pack de Lógica Financiera:",
                    "",
                    f"    - {_text(financial_logic_pack.get('pack_title'))}",
                    f"      Evidencia : {_list_text(financial_logic_pack.get('evidence_items', []), default='NINGUNA ACOTADA')}",
                    f"      Desbloquea: {_list_text(financial_logic_pack.get('unlocks', []), default='NINGUNA ACOTADA')}",
                    f"      Por Qué   : {_text(financial_logic_pack.get('why'))}",
                    "",
                ]
            if financial_support_rows:
                content_es += ["  Carriles Estructurales Vinculados:", ""]
                for row in financial_support_rows:
                    content_es += [
                        f"    - {_text(row.get('title'))}: {_text(row.get('statement'))}",
                        f"      Por Qué Importa : {_text(row.get('why_it_matters'))}",
                        "",
                    ]
        elif section_key == "peer_comparison":
            peer_type = _text(primary_peer.get("peer_type") or primary_peer.get("comparison_mode"))
            source_reference = _text(primary_peer.get("source_reference"), default="")
            what_it_does_not_prove = _text(primary_peer.get("what_it_does_not_prove"))
            peer_requirement_rows = list(primary_peer.get("peer_requirement_rows", []) or [])
            candidate_peer_frames = list(primary_peer.get("candidate_peer_frame_register", []) or [])
            better_practice_deltas = list(primary_peer.get("better_practice_delta_register", []) or [])
            peer_superiority_block_reason = _text(primary_peer.get("peer_superiority_block_reason"))
            if primary_peer and not source_reference and _text(primary_peer.get("evidence_state")) != "OBSERVED_FACT":
                what_it_does_not_prove = (
                    "Archetypal peer pattern, not observed competitor evidence."
                    if what_it_does_not_prove == "NOT OBSERVED"
                    else what_it_does_not_prove
                )
            peer_support_rows = _constellation_rows_for_pack(
                _text(fair_comparison_pack.get("pack_family")),
                preferred_types=["comparison_failure", "challenger_hypothesis", "alternative_variable_candidate"],
                limit=3,
            )
            if not peer_support_rows and (_text(executive_thesis.get("invalid_comparison_risk")) or fair_comparison_pack):
                peer_support_rows = [
                    {
                        "title": "Comparison failure",
                        "statement": _text(executive_thesis.get("invalid_comparison_risk")),
                        "differentiator": _text(fair_comparison_pack.get("why"))
                        or "This attacks comparability before it attacks local equipment performance.",
                    }
                ]
            content_en = [
                _sep("="),
                "PEER / COMPETITIVE COMPARISON",
                _sep("="),
                "",
                f"  Peer Type           : {peer_type}",
                f"  Evidence State      : {_text(primary_peer.get('evidence_state'))}",
                f"  Transferability     : {_text(primary_peer.get('transferability'))}",
                f"  What It Proves      : {_text(primary_peer.get('what_it_proves'))}",
                f"  What It Does Not Prove: {what_it_does_not_prove}",
                f"  Invalid Comparison Risk: {_text(executive_thesis.get('invalid_comparison_risk'))}",
                f"  Source              : {source_reference or 'Archetypal / bounded structural pattern only'}",
                "",
            ]
            if peer_surface_readout_register:
                content_en += ["  Comparison Reading:", ""]
                for row in peer_surface_readout_register:
                    content_en += [
                        f"    - {_text(row.get('signal'))}: {_text(row.get('statement'))}",
                    ]
                    if _text(row.get("why_now"), default=""):
                        content_en += [f"      Why Now : {_text(row.get('why_now'))}"]
                    content_en += [""]
            if fair_comparison_pack:
                content_en += [
                    "  Fair Comparison Pack:",
                    "",
                    f"    - {_text(fair_comparison_pack.get('pack_title'))}",
                    f"      Evidence : {_list_text(fair_comparison_pack.get('evidence_items', []), default='NONE BOUNDED')}",
                    f"      Unlocks  : {_list_text(fair_comparison_pack.get('unlocks', []), default='NONE BOUNDED')}",
                    f"      Why      : {_text(fair_comparison_pack.get('why'))}",
                    "",
                ]
            if peer_support_rows:
                content_en += ["  Linked Comparison Lanes:", ""]
                for row in peer_support_rows:
                    content_en += [
                        f"    - {_text(row.get('title'))}: {_text(row.get('statement'))}",
                        f"      Differentiator : {_text(row.get('differentiator'))}",
                        "",
                    ]
            if peer_requirement_rows:
                content_en += ["  Peer Requirements:", ""]
                for row in peer_requirement_rows[:4]:
                    content_en += [
                        f"    - {_text(row.get('peer_requirement'))} [{_text(row.get('status'), default='required')}]",
                        f"      Why It Matters : {_text(row.get('why_it_matters'))}",
                        f"      Missing        : {_text(row.get('missing_evidence'))}",
                        "",
                    ]
            if candidate_peer_frames:
                content_en += ["  Candidate Peer Frames:", ""]
                for row in candidate_peer_frames[:3]:
                    content_en += [
                        f"    - {_text(row.get('candidate_peer_frame'))}",
                        f"      State          : {_text(row.get('candidate_state'))}",
                        f"      Why It Matters : {_text(row.get('why_it_matters'))}",
                        "",
                    ]
            if better_practice_deltas:
                content_en += ["  Better-Practice Deltas:", ""]
                for row in better_practice_deltas[:3]:
                    content_en += [
                        f"    - {_text(row.get('practice_delta'))}",
                        f"      Why Plausible  : {_text(row.get('why_plausible'))}",
                        f"      Evidence Needed: {_text(row.get('evidence_needed'))}",
                        "",
                    ]
            if peer_superiority_block_reason:
                content_en += [
                    f"  Peer Superiority Block: {peer_superiority_block_reason}",
                    "",
                ]
            content_es = [
                _sep("="),
                "COMPARACIÓN CON PARES / COMPETITIVA",
                _sep("="),
                "",
                f"  Tipo de Par         : {peer_type}",
                f"  Estado de Evidencia : {_text(primary_peer.get('evidence_state'))}",
                f"  Transferibilidad    : {_text(primary_peer.get('transferability'))}",
                f"  Qué Demuestra       : {_text(primary_peer.get('what_it_proves'))}",
                f"  Qué No Demuestra    : {what_it_does_not_prove}",
                f"  Riesgo de Comparación Inválida: {_text(executive_thesis.get('invalid_comparison_risk'))}",
                f"  Fuente              : {source_reference or 'Patrón arquetípico / acotado, no competidor observado'}",
                "",
            ]
            if peer_surface_readout_register:
                content_es += ["  Lectura de Comparación:", ""]
                for row in peer_surface_readout_register:
                    content_es += [
                        f"    - {_text(row.get('signal'))}: {_text(row.get('statement'))}",
                    ]
                    if _text(row.get("why_now"), default=""):
                        content_es += [f"      Por Qué Ahora: {_text(row.get('why_now'))}"]
                    content_es += [""]
            if fair_comparison_pack:
                content_es += [
                    "  Pack de Comparabilidad Justa:",
                    "",
                    f"    - {_text(fair_comparison_pack.get('pack_title'))}",
                    f"      Evidencia : {_list_text(fair_comparison_pack.get('evidence_items', []), default='NINGUNA ACOTADA')}",
                    f"      Desbloquea: {_list_text(fair_comparison_pack.get('unlocks', []), default='NINGUNA ACOTADA')}",
                    f"      Por Qué   : {_text(fair_comparison_pack.get('why'))}",
                    "",
                ]
            if peer_support_rows:
                content_es += ["  Carriles Vinculados de Comparación:", ""]
                for row in peer_support_rows:
                    content_es += [
                        f"    - {_text(row.get('title'))}: {_text(row.get('statement'))}",
                        f"      Diferenciador : {_text(row.get('differentiator'))}",
                        "",
                    ]
            if peer_requirement_rows:
                content_es += ["  Requisitos del Peer:", ""]
                for row in peer_requirement_rows[:4]:
                    content_es += [
                        f"    - {_text(row.get('peer_requirement'))} [{_text(row.get('status'), default='required')}]",
                        f"      Por Qué Importa : {_text(row.get('why_it_matters'))}",
                        f"      Faltante        : {_text(row.get('missing_evidence'))}",
                        "",
                    ]
            if candidate_peer_frames:
                content_es += ["  Marcos Candidatos de Peer:", ""]
                for row in candidate_peer_frames[:3]:
                    content_es += [
                        f"    - {_text(row.get('candidate_peer_frame'))}",
                        f"      Estado         : {_text(row.get('candidate_state'))}",
                        f"      Por Qué Importa: {_text(row.get('why_it_matters'))}",
                        "",
                    ]
            if better_practice_deltas:
                content_es += ["  Deltas de Mejor Práctica:", ""]
                for row in better_practice_deltas[:3]:
                    content_es += [
                        f"    - {_text(row.get('practice_delta'))}",
                        f"      Por Qué Es Plausible: {_text(row.get('why_plausible'))}",
                        f"      Evidencia Necesaria : {_text(row.get('evidence_needed'))}",
                        "",
                    ]
            if peer_superiority_block_reason:
                content_es += [
                    f"  Bloqueo de Superioridad del Peer: {peer_superiority_block_reason}",
                    "",
                ]
        elif section_key == "conditional_redesign":
            content_en = [
                _sep("="),
                "CONDITIONAL REDESIGN PATHWAY",
                _sep("="),
                "",
                f"  Trigger Hypothesis  : {_text(primary_redesign.get('trigger_hypothesis') or primary_redesign.get('hypothesis'))}",
                f"  Evidence State      : {_text(primary_redesign.get('evidence_state'))}",
                f"  Conflict Resolved   : {_text(primary_redesign.get('conflict_resolved'))}",
                f"  Economic Logic      : {_text(primary_redesign.get('economic_logic'))}",
                f"  Evidence Needed     : {_list_text(primary_redesign.get('evidence_needed', []), default='NONE BOUNDED')}",
                f"  Redesign Direction  : {_text(primary_redesign.get('redesign_direction'))}",
                f"  Kill Condition      : {_text(primary_redesign.get('kill_condition'))}",
                "",
            ]
            if conditional_pathways:
                content_en += ["  Alternative Conditional Pathways:", ""]
                for row in conditional_pathways:
                    content_en += [
                        f"    - {row.get('opportunity_name', '')}",
                        f"      Statement : {_text(row.get('conditional_statement'))}",
                        f"      Validate  : {_text(row.get('validation_requirement'))}",
                        "",
                    ]
            content_es = [
                _sep("="),
                "RUTA CONDICIONAL DE REDISEÑO",
                _sep("="),
                "",
                f"  Hipótesis Gatillo   : {_text(primary_redesign.get('trigger_hypothesis') or primary_redesign.get('hypothesis'))}",
                f"  Estado de Evidencia : {_text(primary_redesign.get('evidence_state'))}",
                f"  Conflicto que Resuelve: {_text(primary_redesign.get('conflict_resolved'))}",
                f"  Lógica Económica    : {_text(primary_redesign.get('economic_logic'))}",
                f"  Evidencia Necesaria : {_list_text(primary_redesign.get('evidence_needed', []), default='NINGUNA ACOTADA')}",
                f"  Dirección de Rediseño: {_text(primary_redesign.get('redesign_direction'))}",
                f"  Condición de Muerte : {_text(primary_redesign.get('kill_condition'))}",
                "",
            ]
            if conditional_pathways:
                content_es += ["  Vías Condicionales Alternativas:", ""]
                for row in conditional_pathways:
                    content_es += [
                        f"    - {row.get('opportunity_name', '')}",
                        f"      Enunciado : {_text(row.get('conditional_statement'))}",
                        f"      Validar   : {_text(row.get('validation_requirement'))}",
                        "",
                    ]
        elif section_key == "minimum_evidence":
            content_en = [
                _sep("="),
                "MINIMUM EVIDENCE FOR DISCRIMINATION",
                _sep("="),
                "",
                f"  Minimum Evidence    : {minimum_evidence_text}",
                f"  Source              : {_text(executive_thesis.get('minimum_discriminating_evidence_source'))}",
                f"  Unlocks             : {evidence_unlocks}",
                "",
            ]
            content_es = [
                _sep("="),
                "EVIDENCIA MÍNIMA PARA DISCRIMINACIÓN",
                _sep("="),
                "",
                f"  Evidencia Mínima    : {minimum_evidence_text}",
                f"  Fuente              : {_text(executive_thesis.get('minimum_discriminating_evidence_source'))}",
                f"  Desbloquea          : {evidence_unlocks}",
                "",
            ]
        elif section_key == "tad":
            content_en = [_sep("="), "TAD — IMMEDIATE ACTION PRIORITY", _sep("="), ""]
            content_es = [_sep("="), "TAD — PRIORIDAD DE ACCIÓN INMEDIATA", _sep("="), ""]
            if not top_actions:
                content_en += ["  No client-facing TAD actions were selected.", ""]
                content_es += ["  No se seleccionaron acciones TAD cliente-facing.", ""]
            if tad_surface_readout_register:
                content_en += ["  Decision Reading:", ""]
                for row in tad_surface_readout_register:
                    content_en += [
                        f"    - {_text(row.get('signal'))}: {_text(row.get('statement'))}",
                    ]
                    if _text(row.get("why_now"), default=""):
                        content_en += [f"      Why Now : {_text(row.get('why_now'))}"]
                    content_en += [""]
                content_es += ["  Lectura de Decisión:", ""]
                for row in tad_surface_readout_register:
                    content_es += [
                        f"    - {_text(row.get('signal'))}: {_text(row.get('statement'))}",
                    ]
                    if _text(row.get("why_now"), default=""):
                        content_es += [f"      Por Qué Ahora: {_text(row.get('why_now'))}"]
                    content_es += [""]
            for row in top_actions:
                linked_pack = _best_pack(
                    row.get("action"),
                    row.get("why"),
                    row.get("evidence_needed"),
                    row.get("maps_to"),
                )
                linked_pack_family = _text(linked_pack.get("pack_family"))
                linked_lanes = _constellation_rows_for_pack(
                    linked_pack_family,
                    preferred_types=["challenger_hypothesis", "comparison_failure", "boundary_failure", "dominant_variable_candidate"],
                    limit=2,
                )
                content_en += [
                    f"  Action              : {_text(row.get('action'))}",
                    f"  Status              : {_text(row.get('status'))}",
                    f"  Decision Front      : {_text(row.get('decision_front'))}",
                    f"  Trigger Signal      : {_text(row.get('trigger'))}",
                    f"  Trigger Family      : {_text(row.get('trigger_family'))}",
                    f"  Why                 : {_text(row.get('why'))}",
                    f"  Financial Exposure  : {_text(row.get('financial_exposure'))}",
                    f"  Evidence Needed     : {_text(row.get('evidence_needed'))}",
                    f"  Action Posture      : {_text(row.get('action_posture'))}",
                    f"  Maps To             : {_text(row.get('maps_to'))}",
                    f"  Prohibited Action   : {_text(row.get('prohibited_action'))}",
                    f"  No-Go Class         : {_text(row.get('prohibited_action_class'))}",
                    "",
                ]
                if linked_pack:
                    content_en += [
                        f"  Trigger Pack        : {_text(linked_pack.get('pack_title'))}",
                        f"  Pack Family         : {_text(row.get('evidence_pack_family')) or _text(linked_pack.get('pack_family'))}",
                        f"  Pack Unlocks        : {_list_text(linked_pack.get('unlocks', []), default='NONE BOUNDED')}",
                        "",
                    ]
                if linked_lanes:
                    content_en += ["  Protects Against    :", ""]
                    for lane_row in linked_lanes:
                        content_en += [
                            f"    - {_text(lane_row.get('title'))}: {_text(lane_row.get('statement'))}",
                            "",
                        ]
                content_es += [
                    f"  Acción              : {_text(row.get('action'))}",
                    f"  Estado              : {_text(row.get('status'))}",
                    f"  Frente de Decisión  : {_text(row.get('decision_front'))}",
                    f"  Señal Gatillo       : {_text(row.get('trigger'))}",
                    f"  Familia de Gatillo  : {_text(row.get('trigger_family'))}",
                    f"  Por Qué             : {_text(row.get('why'))}",
                    f"  Exposición Financiera: {_text(row.get('financial_exposure'))}",
                    f"  Evidencia Necesaria : {_text(row.get('evidence_needed'))}",
                    f"  Postura de Acción   : {_text(row.get('action_posture'))}",
                    f"  Mapea a             : {_text(row.get('maps_to'))}",
                    f"  Acción Prohibida    : {_text(row.get('prohibited_action'))}",
                    f"  Clase de No-Go      : {_text(row.get('prohibited_action_class'))}",
                    "",
                ]
                if linked_pack:
                    content_es += [
                        f"  Pack Gatillo        : {_text(linked_pack.get('pack_title'))}",
                        f"  Familia del Pack    : {_text(row.get('evidence_pack_family')) or _text(linked_pack.get('pack_family'))}",
                        f"  Desbloquea el Pack  : {_list_text(linked_pack.get('unlocks', []), default='NINGUNA ACOTADA')}",
                        "",
                    ]
                if linked_lanes:
                    content_es += ["  Protege Contra      :", ""]
                    for lane_row in linked_lanes:
                        content_es += [
                            f"    - {_text(lane_row.get('title'))}: {_text(lane_row.get('statement'))}",
                            "",
                        ]
        else:
            content_en = [
                _sep("="),
                "CLAIM PERMISSIONS / WHAT NOT TO DO",
                _sep("="),
                "",
                f"  Admissible Now      : {_list_text(admissible_actions, default='NONE BOUNDED')}",
                f"  Not Admissible      : {_list_text(prohibited_claims, default='NONE BOUNDED')}",
                f"  Local Closure State : {local_claim_closure_state}",
                f"  Conditional Intelligence: {conditional_intelligence_reason or 'NONE BOUNDED'}",
                f"  Claim Ceiling Counts: allowed={claim_permission_summary['allowed']} | conditional={claim_permission_summary['conditional']} | prohibited={claim_permission_summary['prohibited']}",
                f"  Minimum Evidence Gate: {minimum_evidence_text}",
                "",
            ]
            content_es = [
                _sep("="),
                "PERMISOS DE CLAIMS / QUÉ NO HACER",
                _sep("="),
                "",
                f"  Admisible Ahora     : {_list_text(admissible_actions, default='NINGUNO ACOTADO')}",
                f"  No Admisible        : {_list_text(prohibited_claims, default='NINGUNO ACOTADO')}",
                f"  Estado del Cierre Local: {local_claim_closure_state}",
                f"  Inteligencia Condicional: {conditional_intelligence_reason or 'NINGUNA ACOTADA'}",
                f"  Conteo del Techo de Claims: permitidos={claim_permission_summary['allowed']} | condicionales={claim_permission_summary['conditional']} | prohibidos={claim_permission_summary['prohibited']}",
                f"  Puerta de Evidencia Mínima: {minimum_evidence_text}",
                "",
            ]
        composed.append(
            _section_from_lines(
                idx=idx,
                section_key=section_key,
                title=title,
                content_en=content_en,
                content_es=content_es,
            )
        )
    return composed


def _prioritize_body_sections_by_outline(
    body_sections: list[dict[str, Any]],
    main_report_outline: dict[str, Any],
) -> list[dict[str, Any]]:
    preferred_titles = [
        str(title).strip()
        for title in list(main_report_outline.get("body_section_titles", []) or [])
        if str(title).strip()
    ] or _outline_render_targets(main_report_outline)
    if not preferred_titles:
        return list(body_sections or [])
    body_by_title = {
        str(section.get("title", "")).strip(): section
        for section in list(body_sections or [])
        if str(section.get("title", "")).strip()
    }
    ordered: list[dict[str, Any]] = []
    seen_titles: set[str] = set()
    for title in preferred_titles:
        section = body_by_title.get(title)
        if section and title not in seen_titles:
            seen_titles.add(title)
            ordered.append(section)
    for section in list(body_sections or []):
        title = str(section.get("title", "")).strip()
        if not title or title in seen_titles:
            continue
        seen_titles.add(title)
        ordered.append(section)
    return ordered


_LEGACY_DUPLICATE_BODY_TITLES = {
    "Blocking Conflicts",
    "Validation Architecture",
    "Inference Case Map",
    "Tension Map",
    "Conditional Opportunities",
    "Financial Context",
    "Energy Profile & Normative Constraints",
}

_SECTION_SURFACE_DENSITY_PROTECTED_KEYS = {
    "executive_structural_thesis",
    "reframed_problem",
    "dominant_structural_contradiction",
    "system_abstraction_snapshot",
    "dominant_variables",
    "scenario_space",
    "financial_exposure",
    "peer_comparison",
    "conditional_redesign",
    "minimum_evidence",
    "tad",
}

_SECTION_SURFACE_DENSITY_PROTECTED_TITLES = {
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
}

_SECTION_SURFACE_DENSITY_PLACEHOLDER_TOKENS = (
    "not observed",
    "none bounded",
    "blocking if used",
    "no client-facing tad actions were selected",
    "no se seleccionaron acciones tad cliente-facing",
    "this section is intentionally explained rather than left empty",
    "esta sección se explica explícitamente en vez de quedar vacía",
    "no attempt metadata was recorded",
)

_SECTION_SURFACE_DENSITY_SIGNAL_TOKENS = (
    "contradiction",
    "reframed",
    "variable",
    "scenario",
    "evidence",
    "peer",
    "comparison",
    "financial",
    "trigger",
    "risk",
    "action",
    "pack",
    "correlation",
    "boundary",
    "tad",
)

_SECTION_SURFACE_STRATEGIC_SIGNAL_TOKENS = (
    "wrong variable",
    "wrong denominator",
    "wrong boundary",
    "reframed problem",
    "dominant contradiction",
    "financial exposure",
    "peer requirement",
    "peer superiority block",
    "better-practice",
    "correlation constellation",
    "trigger family",
    "decision front",
    "no-go class",
    "minimum evidence",
    "capital logic",
)

_SECTION_SURFACE_INVENTORY_TITLE_HINTS = (
    "source traceability",
    "evidence & source traceability",
    "claim permission",
    "claim permissions",
    "source family coverage",
    "requestable evidence",
    "traceability",
)

_SECTION_SURFACE_INVENTORY_TOKENS = (
    "status",
    "state",
    "register",
    "traceability",
    "lineage",
    "provider",
    "reference",
    "packet",
    "source",
    "permission",
    "policy",
    "contract",
    "coverage",
    "authority",
    "family",
    "required",
    "requestable",
    "allowed",
    "prohibited",
    "blocked",
)

_SECTION_SURFACE_REDUNDANCY_STOPWORDS = {
    "section",
    "signal",
    "signals",
    "state",
    "bounded",
    "observed",
    "logic",
    "profile",
    "surface",
    "strategic",
    "evidence",
    "appendix",
    "technical",
    "executive",
    "pack",
    "trigger",
}

def _resolve_chart_visibility_policy_entry(
    section_hint: str,
    visible_section_ids: set[str],
    support_chart_visibility_policy: dict[str, Any] | None = None,
    chart_asset: dict[str, Any] | None = None,
) -> dict[str, Any]:
    normalized_hint = str(section_hint or "").strip()
    chart_asset_id = str((chart_asset or {}).get("asset_id", "")).strip()
    chart_category = str((chart_asset or {}).get("chart_category", "")).strip()
    chart_lane = str((chart_asset or {}).get("chart_lane", "")).strip()
    chart_intent = str((chart_asset or {}).get("chart_intent", "")).strip()
    if not normalized_hint:
        return {
            "resolved_section_hint": "",
            "visibility_policy_state": "empty_hint",
            "policy_rule_id": "",
            "policy_source": str((support_chart_visibility_policy or {}).get("policy_source", "") or ""),
            "policy_note": "",
        }
    if normalized_hint in visible_section_ids:
        return {
            "resolved_section_hint": normalized_hint,
            "visibility_policy_state": "direct_visible_match",
            "policy_rule_id": "direct_visible_match",
            "policy_source": str((support_chart_visibility_policy or {}).get("policy_source", "") or ""),
            "policy_note": "Section hint already resolves to a visible body or appendix section.",
        }
    policy_register = list((support_chart_visibility_policy or {}).get("policy_register", []) or [])
    applicable_rules: list[dict[str, Any]] = []
    for matching_rule in policy_register:
        if str(matching_rule.get("section_hint", "")).strip() != normalized_hint:
            continue
        chart_asset_ids = [
            str(value).strip()
            for value in list(matching_rule.get("chart_asset_ids", []) or [])
        ]
        chart_categories = [
            str(value).strip()
            for value in list(matching_rule.get("chart_categories", []) or [])
        ]
        chart_lanes = [
            str(value).strip()
            for value in list(matching_rule.get("chart_lanes", []) or [])
        ]
        chart_intents = [
            str(value).strip()
            for value in list(matching_rule.get("chart_intents", []) or [])
        ]
        if "*" not in chart_categories and chart_category not in chart_categories:
            continue
        if "*" not in chart_lanes and chart_lane not in chart_lanes:
            continue
        if "*" not in chart_intents and chart_intent not in chart_intents:
            continue
        if "*" not in chart_asset_ids and chart_asset_id not in chart_asset_ids:
            continue
        chart_specificity_bonus = 0
        if "*" not in chart_categories and chart_category in chart_categories:
            chart_specificity_bonus += 1
        if "*" not in chart_lanes and chart_lane in chart_lanes:
            chart_specificity_bonus += 1
        if "*" not in chart_intents and chart_intent in chart_intents:
            chart_specificity_bonus += 1
        if "*" not in chart_asset_ids and chart_asset_id in chart_asset_ids:
            chart_specificity_bonus += 1
        row = dict(matching_rule)
        row["_chart_specificity_bonus"] = chart_specificity_bonus
        applicable_rules.append(row)
    applicable_rules.sort(
        key=lambda row: (
            -(int(row.get("specificity", 0)) + int(row.get("_chart_specificity_bonus", 0))),
            int(row.get("priority", 0)),
        )
    )
    for matching_rule in applicable_rules:
        for candidate in list(matching_rule.get("promote_to", []) or []):
            candidate = str(candidate or "").strip()
            if candidate not in visible_section_ids:
                continue
            return {
                "resolved_section_hint": candidate,
                "visibility_policy_state": "promoted_to_visible_support_section",
                "policy_rule_id": str(matching_rule.get("rule_id", "")).strip(),
                "policy_source": str((support_chart_visibility_policy or {}).get("policy_source", "") or ""),
                "policy_note": str(matching_rule.get("policy_note", "")).strip(),
            }
    return {
        "resolved_section_hint": normalized_hint,
        "visibility_policy_state": "no_visible_mapping_found",
        "policy_rule_id": "",
        "policy_source": str((support_chart_visibility_policy or {}).get("policy_source", "") or ""),
        "policy_note": "",
    }


def _resolve_chart_visibility_section_hint(
    section_hint: str,
    visible_section_ids: set[str],
    support_chart_visibility_policy: dict[str, Any] | None = None,
    chart_asset: dict[str, Any] | None = None,
) -> tuple[str, str]:
    row = _resolve_chart_visibility_policy_entry(
        section_hint,
        visible_section_ids,
        support_chart_visibility_policy=support_chart_visibility_policy,
        chart_asset=chart_asset,
    )
    return str(row.get("resolved_section_hint", "")).strip(), str(row.get("visibility_policy_state", "")).strip()


def _lane_visibility_limit(
    support_chart_lane_visibility_policy: dict[str, Any] | None,
    *,
    surface_type: str,
    chart_lane: str,
) -> int | None:
    lane_limits = dict((support_chart_lane_visibility_policy or {}).get("lane_limits", {}) or {})
    surface_limits = dict(lane_limits.get(str(surface_type or "").strip(), {}) or {})
    if not chart_lane:
        return None
    raw = surface_limits.get(chart_lane)
    if raw is None:
        return None
    try:
        return int(raw)
    except (TypeError, ValueError):
        return None


def _resolve_support_chart_lane_curation_entry(
    *,
    resolved_section_hint: str,
    chart_asset: dict[str, Any] | None,
    support_chart_lane_curation_policy: dict[str, Any] | None,
) -> dict[str, Any]:
    target_section_hint = str(resolved_section_hint or "").strip()
    chart_lane = str((chart_asset or {}).get("chart_lane", "")).strip()
    chart_intent = str((chart_asset or {}).get("chart_intent", "")).strip()
    policy_source = str((support_chart_lane_curation_policy or {}).get("policy_source", "") or "")
    if not target_section_hint or not chart_lane:
        return {
            "lane_curation_state": "not_applicable",
            "lane_curation_rank": None,
            "lane_curation_rule_scope": "",
            "lane_curation_priority_source": policy_source,
        }
    section_priority_map = dict(
        (support_chart_lane_curation_policy or {}).get("section_lane_intent_priority", {}) or {}
    )
    default_priority_map = dict(
        (support_chart_lane_curation_policy or {}).get("default_lane_intent_priority", {}) or {}
    )
    section_priorities = dict(section_priority_map.get(target_section_hint, {}) or {})
    prioritized_intents = list(section_priorities.get(chart_lane, []) or [])
    curation_scope = "section_lane_intent_priority"
    if not prioritized_intents:
        prioritized_intents = list(default_priority_map.get(chart_lane, []) or [])
        curation_scope = "default_lane_intent_priority"
    if not prioritized_intents:
        return {
            "lane_curation_state": "uncurated_lane_order",
            "lane_curation_rank": None,
            "lane_curation_rule_scope": "",
            "lane_curation_priority_source": policy_source,
        }
    fallback_rank = len(prioritized_intents) + 100
    if chart_intent in prioritized_intents:
        return {
            "lane_curation_state": f"{curation_scope}_match",
            "lane_curation_rank": prioritized_intents.index(chart_intent),
            "lane_curation_rule_scope": curation_scope,
            "lane_curation_priority_source": policy_source,
        }
    return {
        "lane_curation_state": f"{curation_scope}_fallback",
        "lane_curation_rank": fallback_rank,
        "lane_curation_rule_scope": curation_scope,
        "lane_curation_priority_source": policy_source,
    }


def _order_section_chart_records(
    records: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    direct_records: list[dict[str, Any]] = []
    promoted_by_lane: dict[str, list[dict[str, Any]]] = {}
    lane_order: list[str] = []
    for record in list(records or []):
        policy_state = str(record.get("policy_state", "")).strip()
        if policy_state != "promoted_to_visible_support_section":
            direct_records.append(record)
            continue
        chart_lane = str(record.get("chart_lane", "")).strip() or "__uncategorized__"
        if chart_lane not in promoted_by_lane:
            lane_order.append(chart_lane)
            promoted_by_lane[chart_lane] = []
        promoted_by_lane[chart_lane].append(record)
    ordered: list[dict[str, Any]] = sorted(
        direct_records,
        key=lambda row: int(row.get("original_index", 0)),
    )
    for chart_lane in lane_order:
        ordered.extend(
            sorted(
                promoted_by_lane.get(chart_lane, []),
                key=lambda row: (
                    1 if row.get("lane_curation_rank") is None else 0,
                    int(row.get("lane_curation_rank", 0) or 0),
                    int(row.get("original_index", 0)),
                ),
            )
        )
    return ordered


def _apply_support_chart_lane_visibility_cap(
    *,
    policy_state: str,
    resolved_section_hint: str,
    chart_asset: dict[str, Any] | None,
    section_surface_map: dict[str, str],
    support_chart_lane_visibility_policy: dict[str, Any] | None,
    lane_visibility_counts: dict[tuple[str, str, str], int],
) -> dict[str, Any]:
    chart_lane = str((chart_asset or {}).get("chart_lane", "")).strip()
    lane_surface_type = str(section_surface_map.get(str(resolved_section_hint or "").strip(), "")).strip()
    lane_limit = _lane_visibility_limit(
        support_chart_lane_visibility_policy,
        surface_type=lane_surface_type,
        chart_lane=chart_lane,
    )
    effective_visible_section_hint = str(resolved_section_hint or "").strip()
    lane_visibility_state = "not_applicable"
    if policy_state == "promoted_to_visible_support_section" and lane_surface_type:
        if lane_limit is None:
            lane_visibility_state = "visible_without_lane_cap"
        else:
            lane_key = (lane_surface_type, str(resolved_section_hint or "").strip(), chart_lane)
            current_count = lane_visibility_counts.get(lane_key, 0)
            if current_count >= lane_limit:
                lane_visibility_state = "suppressed_by_lane_cap"
                effective_visible_section_hint = ""
            else:
                lane_visibility_counts[lane_key] = current_count + 1
                lane_visibility_state = "visible_within_lane_cap"
    elif policy_state == "direct_visible_match":
        lane_visibility_state = "direct_visible_match_not_capped"
    return {
        "effective_visible_section_hint": effective_visible_section_hint,
        "lane_visibility_state": lane_visibility_state,
        "lane_visibility_surface_type": lane_surface_type,
        "lane_visibility_limit": lane_limit,
    }


def _apply_chart_strategic_surface_gate(
    *,
    resolved_chart_asset_list_map: dict[str, list[dict[str, Any]]] | None,
    body_section_ids: set[str] | None,
    appendix_section_ids: list[str] | None = None,
    appendix_demote_section_id: str = "",
) -> tuple[dict[str, list[dict[str, Any]]], list[dict[str, Any]], dict[str, Any]]:
    normalized_map: dict[str, list[dict[str, Any]]] = {
        str(section_id).strip(): [dict(row or {}) for row in list(chart_rows or [])]
        for section_id, chart_rows in dict(resolved_chart_asset_list_map or {}).items()
        if str(section_id).strip()
    }
    normalized_body_section_ids = {
        str(section_id).strip() for section_id in set(body_section_ids or set()) if str(section_id).strip()
    }
    normalized_appendix_section_ids = [
        str(section_id).strip()
        for section_id in list(appendix_section_ids or [])
        if str(section_id).strip()
    ]
    appendix_demote_target = str(appendix_demote_section_id or "").strip()
    if not appendix_demote_target and normalized_appendix_section_ids:
        appendix_demote_target = normalized_appendix_section_ids[0]
    body_assets = [
        asset
        for section_id, chart_rows in normalized_map.items()
        if section_id in normalized_body_section_ids
        for asset in list(chart_rows or [])
    ]
    thesis_critical_count = sum(
        1 for asset in body_assets if str(asset.get("strategic_value_tier", "")).strip() == "thesis_critical"
    )
    strategic_support_count = sum(
        1 for asset in body_assets if str(asset.get("strategic_value_tier", "")).strip() == "strategic_support"
    )
    supportive_context_count = sum(
        1 for asset in body_assets if str(asset.get("strategic_value_tier", "")).strip() == "supportive_context"
    )
    decorative_risk_body_count = sum(
        1 for asset in body_assets if str(asset.get("strategic_value_tier", "")).strip() == "decorative_risk"
    )
    body_strategic_anchor_count = thesis_critical_count + strategic_support_count
    body_gate_activated = thesis_critical_count >= 3 and body_strategic_anchor_count >= 4
    gate_reason = (
        "Body surface already carries enough thesis-critical and strategic-support charts to suppress decorative-risk charts."
        if body_gate_activated
        else "Body surface does not yet carry enough strategic charts to suppress decorative-risk charts."
    )

    filtered_map: dict[str, list[dict[str, Any]]] = {}
    policy_register: list[dict[str, Any]] = []
    decorative_risk_body_count_suppressed = 0
    decorative_risk_body_count_demoted = 0
    decorative_risk_body_count_visible = 0
    demoted_appendix_assets: dict[str, list[dict[str, Any]]] = {}

    for section_id, chart_rows in normalized_map.items():
        is_body_section = section_id in normalized_body_section_ids
        filtered_rows: list[dict[str, Any]] = []
        for original_index, asset in enumerate(list(chart_rows or [])):
            resolved_asset = dict(asset or {})
            strategic_value_tier = str(resolved_asset.get("strategic_value_tier", "")).strip() or "unclassified"
            if is_body_section and body_gate_activated and strategic_value_tier == "decorative_risk":
                if appendix_demote_target:
                    strategic_surface_policy_state = "demoted_decorative_risk_to_appendix"
                    strategic_surface_policy_reason = (
                        "Body surface already has enough strategic charts; this lower-value chart is preserved in appendix instead of remaining in the primary surface."
                    )
                    resolved_asset["demoted_from_section_id"] = section_id
                    resolved_asset["demoted_to_section_id"] = appendix_demote_target
                    demoted_appendix_assets.setdefault(appendix_demote_target, []).append(resolved_asset)
                    decorative_risk_body_count_demoted += 1
                else:
                    strategic_surface_policy_state = "suppressed_decorative_risk_from_body"
                    strategic_surface_policy_reason = gate_reason
                    decorative_risk_body_count_suppressed += 1
            elif is_body_section and body_gate_activated:
                strategic_surface_policy_state = "visible_body_strategic_after_gate"
                strategic_surface_policy_reason = "Strategic or contextual chart remains visible in the primary body surface."
                if strategic_value_tier == "decorative_risk":
                    decorative_risk_body_count_visible += 1
                filtered_rows.append(resolved_asset)
            elif is_body_section:
                strategic_surface_policy_state = "visible_body_without_strategic_gate"
                strategic_surface_policy_reason = gate_reason
                if strategic_value_tier == "decorative_risk":
                    decorative_risk_body_count_visible += 1
                filtered_rows.append(resolved_asset)
            else:
                strategic_surface_policy_state = "appendix_or_non_body_exempt"
                strategic_surface_policy_reason = "Strategic surface gate applies only to primary body sections."
                filtered_rows.append(resolved_asset)

            resolved_asset["strategic_surface_policy_state"] = strategic_surface_policy_state
            resolved_asset["strategic_surface_policy_reason"] = strategic_surface_policy_reason
            policy_register.append({
                "section_id": section_id,
                "asset_id": str(resolved_asset.get("asset_id", "")).strip(),
                "original_index": original_index,
                "strategic_value_tier": strategic_value_tier,
                "strategic_surface_policy_state": strategic_surface_policy_state,
                "strategic_surface_policy_reason": strategic_surface_policy_reason,
                "body_gate_activated": body_gate_activated,
                "demoted_to_section_id": str(resolved_asset.get("demoted_to_section_id", "")).strip(),
            })
        filtered_map[section_id] = filtered_rows

    for section_id, moved_assets in demoted_appendix_assets.items():
        filtered_map.setdefault(section_id, []).extend(moved_assets)

    summary = {
        "body_gate_activated": body_gate_activated,
        "body_gate_reason": gate_reason,
        "appendix_demote_target": appendix_demote_target,
        "thesis_critical_body_count": thesis_critical_count,
        "strategic_support_body_count": strategic_support_count,
        "supportive_context_body_count": supportive_context_count,
        "decorative_risk_body_count_before": decorative_risk_body_count,
        "decorative_risk_body_count_suppressed": decorative_risk_body_count_suppressed,
        "decorative_risk_body_count_demoted": decorative_risk_body_count_demoted,
        "decorative_risk_body_count_visible": decorative_risk_body_count_visible,
        "body_strategic_anchor_count": body_strategic_anchor_count,
    }
    return filtered_map, policy_register, summary


def _rebuild_chart_surface_maps(
    resolved_chart_asset_list_map: dict[str, list[dict[str, Any]]] | None,
) -> tuple[dict[str, str], dict[str, str], dict[str, list[str]]]:
    section_chart_map: dict[str, str] = {}
    chart_b64_map: dict[str, str] = {}
    chart_b64_list_map: dict[str, list[str]] = {}
    for section_id, chart_rows in dict(resolved_chart_asset_list_map or {}).items():
        normalized_section_id = str(section_id).strip()
        if not normalized_section_id:
            continue
        normalized_chart_rows = [dict(row or {}) for row in list(chart_rows or [])]
        chart_b64_list_map[normalized_section_id] = [
            str(row.get("image_b64", "") or "")
            for row in normalized_chart_rows
            if str(row.get("image_b64", "") or "").strip()
        ]
        if normalized_chart_rows:
            first_row = normalized_chart_rows[0]
            section_chart_map[normalized_section_id] = str(first_row.get("asset_id", "")).strip()
            chart_b64_map[normalized_section_id] = str(first_row.get("image_b64", "") or "")
    return section_chart_map, chart_b64_map, chart_b64_list_map


def _demote_legacy_duplicate_sections(
    body_sections: list[dict[str, Any]],
    appendix_sections: list[dict[str, Any]],
    *,
    structural_first_default_active: bool,
    main_report_outline: dict[str, Any],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    if not structural_first_default_active or not main_report_outline:
        return list(body_sections or []), list(appendix_sections or [])
    body_kept: list[dict[str, Any]] = []
    appendix_out = list(appendix_sections or [])
    appendix_titles = {
        str(section.get("title", "")).strip()
        for section in appendix_out
        if str(section.get("title", "")).strip()
    }
    for section in list(body_sections or []):
        title = str(section.get("title", "")).strip()
        if title in _LEGACY_DUPLICATE_BODY_TITLES:
            if title not in appendix_titles:
                appendix_out.append({**section, "section_type": "appendix"})
                appendix_titles.add(title)
            continue
        body_kept.append(section)
    return body_kept, appendix_out


def _disambiguate_appendix_titles_against_body(
    body_sections: list[dict[str, Any]],
    appendix_sections: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    body_titles = {
        str(section.get("title", "")).strip()
        for section in list(body_sections or [])
        if str(section.get("title", "")).strip()
    }
    appendix_title_aliases = {
        "Dominant Variables": "Dominant Variables — Technical Register",
        "Minimum Evidence for Discrimination": "Minimum Evidence for Discrimination — Technical Register",
    }
    normalized_appendix_sections: list[dict[str, Any]] = []
    for section in list(appendix_sections or []):
        title = str(section.get("title", "")).strip()
        if title and title in body_titles:
            section = {
                **section,
                "title": appendix_title_aliases.get(title, f"{title} — Technical Appendix"),
            }
        normalized_appendix_sections.append(section)
    return normalized_appendix_sections


def _section_visible_excerpt(section: dict[str, Any]) -> str:
    blocks = list(section.get("blocks", []) or [])
    content = str((blocks[0] or {}).get("content", "") if blocks else "").strip()
    if not content:
        return ""
    for line in content.splitlines():
        stripped = str(line).strip()
        if not stripped:
            continue
        if len(set(stripped)) == 1:
            continue
        return stripped
    return ""


def _section_visible_lines(section: dict[str, Any]) -> list[str]:
    lines: list[str] = []
    for block in list(section.get("blocks", []) or []):
        content = str((block or {}).get("content", "")).strip()
        if not content:
            continue
        for line in content.splitlines():
            stripped = str(line).strip()
            if not stripped:
                continue
            if len(set(stripped)) == 1:
                continue
            lines.append(stripped)
    return lines


def _section_surface_density_profile(section: dict[str, Any]) -> dict[str, Any]:
    visible_lines = _section_visible_lines(section)
    placeholder_lines = [
        line
        for line in visible_lines
        if any(token in line.lower() for token in _SECTION_SURFACE_DENSITY_PLACEHOLDER_TOKENS)
    ]
    substantive_lines = [
        line
        for line in visible_lines
        if line not in placeholder_lines
    ]
    signal_line_count = sum(
        1
        for line in substantive_lines
        if any(token in line.lower() for token in _SECTION_SURFACE_DENSITY_SIGNAL_TOKENS)
    )
    chart_assets = list(section.get("chart_assets", []) or [])
    chart_count = len(chart_assets) + (1 if str(section.get("chart_ref", "")).strip() else 0)
    llm_present = any(
        str(section.get(field, "")).strip()
        for field in ("llm_text", "llm_text_en", "llm_text_es")
    )
    density_score = (
        len(substantive_lines)
        + min(signal_line_count, 4)
        + min(chart_count, 2)
        + (1 if llm_present else 0)
        - min(len(placeholder_lines), 2)
    )
    return {
        "visible_line_count": len(visible_lines),
        "substantive_line_count": len(substantive_lines),
        "placeholder_line_count": len(placeholder_lines),
        "signal_line_count": signal_line_count,
        "chart_count": chart_count,
        "llm_present": llm_present,
        "density_score": density_score,
    }


def _section_surface_strategic_profile(section: dict[str, Any]) -> dict[str, Any]:
    visible_lines = _section_visible_lines(section)
    title = str(section.get("title", "")).strip().lower()
    outline_key = str(section.get("outline_section_key", "")).strip()
    anchor_type = str(section.get("thesis_anchor_type", "")).strip()
    chart_assets = list(section.get("chart_assets", []) or [])
    chart_count = len(chart_assets) + (1 if str(section.get("chart_ref", "")).strip() else 0)
    signal_hits = sum(
        1
        for line in visible_lines
        if any(token in line.lower() for token in _SECTION_SURFACE_STRATEGIC_SIGNAL_TOKENS)
    )
    thesis_anchor_bonus = 2 if anchor_type else 0
    outline_key_bonus = 2 if outline_key in _SECTION_SURFACE_DENSITY_PROTECTED_KEYS else 0
    title_bonus = 2 if title in {value.lower() for value in _SECTION_SURFACE_DENSITY_PROTECTED_TITLES} else 0
    chart_bonus = min(chart_count, 2)
    strategic_value_score = signal_hits + thesis_anchor_bonus + outline_key_bonus + title_bonus + chart_bonus
    if strategic_value_score >= 8:
        strategic_value_tier = "thesis_critical"
    elif strategic_value_score >= 5:
        strategic_value_tier = "strategic_support"
    elif strategic_value_score >= 3:
        strategic_value_tier = "supportive_context"
    else:
        strategic_value_tier = "surface_optional"
    return {
        "strategic_signal_hits": signal_hits,
        "thesis_anchor_type": anchor_type,
        "outline_key_bonus": outline_key_bonus,
        "title_bonus": title_bonus,
        "chart_count": chart_count,
        "strategic_value_score": strategic_value_score,
        "strategic_value_tier": strategic_value_tier,
    }


def _section_surface_redundancy_tokens(section: dict[str, Any]) -> set[str]:
    title = str(section.get("title", "")).strip().lower()
    outline_key = str(section.get("outline_section_key", "")).strip().lower()
    anchor_text = str(section.get("thesis_anchor_text", "")).strip().lower()
    values = [title, outline_key, anchor_text, *_section_visible_lines(section)]
    tokens: set[str] = set()
    for value in values:
        text = str(value or "").strip().lower()
        if not text:
            continue
        for token in re.split(r"[^a-z0-9]+", text):
            if len(token) < 4 or token in _SECTION_SURFACE_REDUNDANCY_STOPWORDS:
                continue
            tokens.add(token)
    return tokens


def _section_surface_inventory_profile(section: dict[str, Any]) -> dict[str, Any]:
    visible_lines = _section_visible_lines(section)
    title = str(section.get("title", "")).strip().lower()
    strategic_profile = dict(
        section.get("section_surface_strategic_profile", {}) or _section_surface_strategic_profile(section)
    )
    readout_register = list(section.get("section_surface_readout_register", []) or [])
    label_like_line_count = sum(
        1
        for line in visible_lines
        if ":" in line and len(str(line).split(":", 1)[0].split()) <= 6
    )
    narrative_line_count = sum(
        1
        for line in visible_lines
        if len(re.findall(r"[A-Za-z0-9]+", str(line))) >= 7 and ":" not in str(line).split(" ", 1)[0]
    )
    inventory_token_hits = sum(
        1
        for line in visible_lines
        if any(token in str(line).lower() for token in _SECTION_SURFACE_INVENTORY_TOKENS)
    )
    title_hint = any(hint in title for hint in _SECTION_SURFACE_INVENTORY_TITLE_HINTS)
    readout_signal_count = sum(
        1
        for row in readout_register
        if str((row or {}).get("label", "")).strip() and str((row or {}).get("value", "")).strip()
    )
    label_like_ratio = label_like_line_count / max(len(visible_lines), 1)
    inventory_score = (
        label_like_line_count
        + min(inventory_token_hits, 4)
        + (2 if title_hint else 0)
    )
    narrative_score = (
        narrative_line_count
        + min(readout_signal_count, 2)
        + min(int(strategic_profile.get("strategic_signal_hits", 0) or 0), 2)
        + (1 if bool(strategic_profile.get("chart_count", 0)) else 0)
    )
    inventory_heavy = (
        len(visible_lines) >= 2
        and label_like_ratio >= 0.5
        and inventory_score >= 6
        and readout_signal_count == 0
        and narrative_score <= 2
    )
    return {
        "visible_line_count": len(visible_lines),
        "label_like_line_count": label_like_line_count,
        "label_like_ratio": round(label_like_ratio, 3),
        "narrative_line_count": narrative_line_count,
        "inventory_token_hits": inventory_token_hits,
        "title_hint": title_hint,
        "readout_signal_count": readout_signal_count,
        "inventory_score": inventory_score,
        "narrative_score": narrative_score,
        "strategic_value_tier": str(strategic_profile.get("strategic_value_tier", "")).strip(),
        "inventory_heavy": inventory_heavy,
    }


def _apply_section_surface_density_gate(
    *,
    body_sections: list[dict[str, Any]],
    appendix_sections: list[dict[str, Any]],
    required_body_titles: set[str] | None = None,
    minimum_body_sections: int = 10,
    min_substantive_lines: int = 6,
    min_density_score: int = 9,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]], dict[str, Any]]:
    retained_body: list[dict[str, Any]] = []
    appended_appendix: list[dict[str, Any]] = list(appendix_sections or [])
    policy_rows: list[dict[str, Any]] = []
    thin_candidate_count = 0
    demoted_to_appendix_count = 0
    retained_by_density_count = 0
    retained_protected_count = 0
    retained_by_body_floor_count = 0
    total_body_sections = len(list(body_sections or []))
    normalized_required_titles = {
        str(title).strip()
        for title in set(required_body_titles or set())
        if str(title).strip()
    }

    for idx, section in enumerate(list(body_sections or [])):
        row = dict(section)
        title = str(row.get("title", "")).strip()
        outline_key = str(row.get("outline_section_key", "")).strip()
        profile = _section_surface_density_profile(row)
        remaining_body_if_demoted = len(retained_body) + (total_body_sections - idx - 1)
        is_protected = (
            outline_key in _SECTION_SURFACE_DENSITY_PROTECTED_KEYS
            or title in _SECTION_SURFACE_DENSITY_PROTECTED_TITLES
            or title in normalized_required_titles
        )
        is_thin = (
            profile["substantive_line_count"] < min_substantive_lines
            or profile["density_score"] < min_density_score
        )
        policy_state = "retained_body_sufficient_density"
        policy_reason = "Section carries enough strategic density to remain in the primary body surface."
        destination_surface = "body"

        if is_protected:
            policy_state = "retained_body_core_section"
            policy_reason = "Section remains in the primary body because it is part of the protected strategic spine."
            retained_protected_count += 1
        elif is_thin and remaining_body_if_demoted < minimum_body_sections:
            policy_state = "retained_body_due_to_minimum_surface_floor"
            policy_reason = "Section is thin, but demoting it would undercut the minimum body-surface floor."
            thin_candidate_count += 1
            retained_by_body_floor_count += 1
        elif is_thin:
            policy_state = "demoted_thin_body_section_to_appendix"
            policy_reason = "Section is too thin for the main surface and is preserved in appendix instead of flattening the body."
            destination_surface = "appendix"
            thin_candidate_count += 1
            demoted_row = {
                **row,
                "section_type": "appendix",
                "demoted_from_surface": "body",
                "demoted_to_surface": "appendix",
                "section_surface_density_state": "demoted_thin_body_section_to_appendix",
                "section_surface_density_profile": dict(profile),
            }
            appended_appendix.append(demoted_row)
            demoted_to_appendix_count += 1
        else:
            retained_by_density_count += 1

        policy_entry = {
            "section_id": str(row.get("section_id", "")).strip(),
            "section_title": title,
            "outline_section_key": outline_key,
            "section_type": str(row.get("section_type", "")).strip(),
            "protected": is_protected,
            "density_score": profile["density_score"],
            "substantive_line_count": profile["substantive_line_count"],
            "placeholder_line_count": profile["placeholder_line_count"],
            "signal_line_count": profile["signal_line_count"],
            "chart_count": profile["chart_count"],
            "llm_present": profile["llm_present"],
            "thin_candidate": is_thin,
            "policy_state": policy_state,
            "policy_reason": policy_reason,
            "destination_surface": destination_surface,
        }
        policy_rows.append(policy_entry)

        if destination_surface == "body":
            retained_row = {
                **row,
                "section_surface_density_state": policy_state,
                "section_surface_density_profile": dict(profile),
            }
            retained_body.append(retained_row)

    summary = {
        "minimum_body_sections": minimum_body_sections,
        "min_substantive_lines": min_substantive_lines,
            "min_density_score": min_density_score,
            "required_body_title_count": len(normalized_required_titles),
            "total_body_sections_evaluated": total_body_sections,
        "thin_candidate_count": thin_candidate_count,
        "demoted_to_appendix_count": demoted_to_appendix_count,
        "retained_by_density_count": retained_by_density_count,
        "retained_protected_count": retained_protected_count,
        "retained_by_body_floor_count": retained_by_body_floor_count,
    }
    return retained_body, appended_appendix, policy_rows, summary


def _apply_section_strategic_surface_gate(
    *,
    body_sections: list[dict[str, Any]],
    appendix_sections: list[dict[str, Any]],
    required_body_titles: set[str] | None = None,
    minimum_body_sections: int = 10,
    minimum_high_value_sections: int = 6,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]], dict[str, Any]]:
    retained_body: list[dict[str, Any]] = []
    appended_appendix: list[dict[str, Any]] = list(appendix_sections or [])
    policy_rows: list[dict[str, Any]] = []
    normalized_required_titles = {
        str(title).strip()
        for title in set(required_body_titles or set())
        if str(title).strip()
    }
    strategic_profiles = [
        _section_surface_strategic_profile(section)
        for section in list(body_sections or [])
    ]
    high_value_available = sum(
        1
        for profile in strategic_profiles
        if str(profile.get("strategic_value_tier", "")).strip() in {"thesis_critical", "strategic_support"}
    )
    total_body_sections = len(list(body_sections or []))
    demoted_to_appendix_count = 0
    retained_protected_count = 0
    retained_low_value_due_to_floor_count = 0
    retained_low_value_due_to_surface_depth_count = 0

    for idx, section in enumerate(list(body_sections or [])):
        row = dict(section)
        title = str(row.get("title", "")).strip()
        outline_key = str(row.get("outline_section_key", "")).strip()
        profile = strategic_profiles[idx]
        remaining_body_if_demoted = len(retained_body) + (total_body_sections - idx - 1)
        is_protected = (
            outline_key in _SECTION_SURFACE_DENSITY_PROTECTED_KEYS
            or title in _SECTION_SURFACE_DENSITY_PROTECTED_TITLES
            or title in normalized_required_titles
        )
        low_value_optional = str(profile.get("strategic_value_tier", "")).strip() == "surface_optional"
        policy_state = "retained_strategic_surface_section"
        policy_reason = "Section carries enough strategic value to remain on the primary surface."
        destination_surface = "body"

        if is_protected:
            policy_state = "retained_strategic_core_section"
            policy_reason = "Section remains because it belongs to the protected strategic or contract-required spine."
            retained_protected_count += 1
        elif low_value_optional and high_value_available < minimum_high_value_sections:
            policy_state = "retained_surface_optional_due_to_surface_depth"
            policy_reason = "Section is low-value optional, but the current body does not yet have enough high-value sections to absorb the demotion."
            retained_low_value_due_to_surface_depth_count += 1
        elif low_value_optional and remaining_body_if_demoted < minimum_body_sections:
            policy_state = "retained_surface_optional_due_to_minimum_surface_floor"
            policy_reason = "Section is low-value optional, but demoting it would collapse the minimum body-surface floor."
            retained_low_value_due_to_floor_count += 1
        elif low_value_optional:
            policy_state = "demoted_low_value_optional_section_to_appendix"
            policy_reason = "Section is populated but strategically optional; appendix preserves it without flattening the body surface."
            destination_surface = "appendix"
            demoted_row = {
                **row,
                "section_type": "appendix",
                "demoted_from_surface": "body",
                "demoted_to_surface": "appendix",
                "section_surface_strategic_state": policy_state,
                "section_surface_strategic_profile": dict(profile),
            }
            appended_appendix.append(demoted_row)
            demoted_to_appendix_count += 1

        policy_entry = {
            "section_id": str(row.get("section_id", "")).strip(),
            "section_title": title,
            "outline_section_key": outline_key,
            "protected": is_protected,
            "strategic_value_score": profile["strategic_value_score"],
            "strategic_value_tier": profile["strategic_value_tier"],
            "strategic_signal_hits": profile["strategic_signal_hits"],
            "chart_count": profile["chart_count"],
            "policy_state": policy_state,
            "policy_reason": policy_reason,
            "destination_surface": destination_surface,
        }
        policy_rows.append(policy_entry)
        if destination_surface == "body":
            retained_row = {
                **row,
                "section_surface_strategic_state": policy_state,
                "section_surface_strategic_profile": dict(profile),
            }
            retained_body.append(retained_row)

    summary = {
        "minimum_body_sections": minimum_body_sections,
        "minimum_high_value_sections": minimum_high_value_sections,
        "required_body_title_count": len(normalized_required_titles),
        "total_body_sections_evaluated": total_body_sections,
        "high_value_available": high_value_available,
        "demoted_to_appendix_count": demoted_to_appendix_count,
        "retained_protected_count": retained_protected_count,
        "retained_low_value_due_to_floor_count": retained_low_value_due_to_floor_count,
        "retained_low_value_due_to_surface_depth_count": retained_low_value_due_to_surface_depth_count,
    }
    return retained_body, appended_appendix, policy_rows, summary


def _apply_section_strategic_redundancy_gate(
    *,
    body_sections: list[dict[str, Any]],
    appendix_sections: list[dict[str, Any]],
    required_body_titles: set[str] | None = None,
    minimum_body_sections: int = 10,
    minimum_high_value_sections: int = 6,
    redundancy_overlap_threshold: float = 0.6,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]], dict[str, Any]]:
    retained_body: list[dict[str, Any]] = []
    appended_appendix: list[dict[str, Any]] = list(appendix_sections or [])
    policy_rows: list[dict[str, Any]] = []
    normalized_required_titles = {
        str(title).strip()
        for title in set(required_body_titles or set())
        if str(title).strip()
    }
    strategic_profiles = [
        dict(section.get("section_surface_strategic_profile", {}) or _section_surface_strategic_profile(section))
        for section in list(body_sections or [])
    ]
    redundancy_tokens = [
        _section_surface_redundancy_tokens(section)
        for section in list(body_sections or [])
    ]
    high_value_available = sum(
        1
        for profile in strategic_profiles
        if str(profile.get("strategic_value_tier", "")).strip() in {"thesis_critical", "strategic_support"}
    )
    total_body_sections = len(list(body_sections or []))
    demoted_to_appendix_count = 0
    retained_protected_count = 0
    retained_low_value_due_to_floor_count = 0
    retained_low_value_due_to_surface_depth_count = 0
    retained_low_overlap_count = 0
    accumulated_spine_tokens: set[str] = set()

    for idx, section in enumerate(list(body_sections or [])):
        row = dict(section)
        title = str(row.get("title", "")).strip()
        outline_key = str(row.get("outline_section_key", "")).strip()
        profile = strategic_profiles[idx]
        row_tokens = redundancy_tokens[idx]
        remaining_body_if_demoted = len(retained_body) + (total_body_sections - idx - 1)
        is_protected = (
            outline_key in _SECTION_SURFACE_DENSITY_PROTECTED_KEYS
            or title in _SECTION_SURFACE_DENSITY_PROTECTED_TITLES
            or title in normalized_required_titles
        )
        low_value_optional = str(profile.get("strategic_value_tier", "")).strip() in {"surface_optional", "supportive_context"}
        overlap_score = 0.0
        if row_tokens and accumulated_spine_tokens:
            overlap_score = len(row_tokens.intersection(accumulated_spine_tokens)) / max(len(row_tokens), 1)
        highly_redundant = overlap_score >= redundancy_overlap_threshold
        policy_state = "retained_nonredundant_surface_section"
        policy_reason = "Section carries distinct enough value to remain on the primary surface."
        destination_surface = "body"

        if is_protected:
            policy_state = "retained_redundancy_protected_section"
            policy_reason = "Section remains because it belongs to the protected strategic or contract-required spine."
            retained_protected_count += 1
        elif not low_value_optional:
            policy_state = "retained_higher_value_surface_section"
            policy_reason = "Section is not surface-optional, so redundancy alone cannot demote it."
        elif not highly_redundant:
            policy_state = "retained_low_value_but_nonredundant_section"
            policy_reason = "Section is optional but still adds sufficiently distinct signal to the primary surface."
            retained_low_overlap_count += 1
        elif high_value_available < minimum_high_value_sections:
            policy_state = "retained_redundant_optional_due_to_surface_depth"
            policy_reason = "Section is redundant and optional, but the body does not yet have enough high-value sections to absorb the demotion."
            retained_low_value_due_to_surface_depth_count += 1
        elif remaining_body_if_demoted < minimum_body_sections:
            policy_state = "retained_redundant_optional_due_to_minimum_surface_floor"
            policy_reason = "Section is redundant and optional, but demoting it would collapse the minimum body-surface floor."
            retained_low_value_due_to_floor_count += 1
        else:
            policy_state = "demoted_redundant_optional_section_to_appendix"
            policy_reason = "Section is strategically optional and materially overlaps the retained thesis spine; appendix preserves it without repeating the body."
            destination_surface = "appendix"
            demoted_row = {
                **row,
                "section_type": "appendix",
                "demoted_from_surface": "body",
                "demoted_to_surface": "appendix",
                "section_surface_redundancy_state": policy_state,
                "section_surface_redundancy_profile": {
                    "overlap_score": overlap_score,
                    "redundancy_overlap_threshold": redundancy_overlap_threshold,
                    "token_count": len(row_tokens),
                    "shared_token_count": len(row_tokens.intersection(accumulated_spine_tokens)),
                    "strategic_value_tier": str(profile.get("strategic_value_tier", "")).strip(),
                },
            }
            appended_appendix.append(demoted_row)
            demoted_to_appendix_count += 1

        policy_entry = {
            "section_id": str(row.get("section_id", "")).strip(),
            "section_title": title,
            "outline_section_key": outline_key,
            "protected": is_protected,
            "strategic_value_tier": str(profile.get("strategic_value_tier", "")).strip(),
            "low_value_optional": low_value_optional,
            "overlap_score": overlap_score,
            "overlap_threshold": redundancy_overlap_threshold,
            "token_count": len(row_tokens),
            "shared_token_count": len(row_tokens.intersection(accumulated_spine_tokens)),
            "highly_redundant": highly_redundant,
            "policy_state": policy_state,
            "policy_reason": policy_reason,
            "destination_surface": destination_surface,
        }
        policy_rows.append(policy_entry)

        if destination_surface == "body":
            retained_row = {
                **row,
                "section_surface_redundancy_state": policy_state,
                "section_surface_redundancy_profile": {
                    "overlap_score": overlap_score,
                    "redundancy_overlap_threshold": redundancy_overlap_threshold,
                    "token_count": len(row_tokens),
                    "shared_token_count": len(row_tokens.intersection(accumulated_spine_tokens)),
                    "strategic_value_tier": str(profile.get("strategic_value_tier", "")).strip(),
                },
            }
            retained_body.append(retained_row)
            if is_protected or str(profile.get("strategic_value_tier", "")).strip() in {"thesis_critical", "strategic_support"}:
                accumulated_spine_tokens.update(row_tokens)

    summary = {
        "minimum_body_sections": minimum_body_sections,
        "minimum_high_value_sections": minimum_high_value_sections,
        "redundancy_overlap_threshold": redundancy_overlap_threshold,
        "required_body_title_count": len(normalized_required_titles),
        "total_body_sections_evaluated": total_body_sections,
        "high_value_available": high_value_available,
        "demoted_to_appendix_count": demoted_to_appendix_count,
        "retained_protected_count": retained_protected_count,
        "retained_low_value_due_to_floor_count": retained_low_value_due_to_floor_count,
        "retained_low_value_due_to_surface_depth_count": retained_low_value_due_to_surface_depth_count,
        "retained_low_overlap_count": retained_low_overlap_count,
    }
    return retained_body, appended_appendix, policy_rows, summary


def _apply_section_inventory_surface_gate(
    *,
    body_sections: list[dict[str, Any]],
    appendix_sections: list[dict[str, Any]],
    required_body_titles: set[str] | None = None,
    minimum_body_sections: int = 10,
    minimum_high_value_sections: int = 6,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]], dict[str, Any]]:
    retained_body: list[dict[str, Any]] = []
    appended_appendix: list[dict[str, Any]] = list(appendix_sections or [])
    policy_rows: list[dict[str, Any]] = []
    normalized_required_titles = {
        str(title).strip()
        for title in set(required_body_titles or set())
        if str(title).strip()
    }
    strategic_profiles = [
        dict(section.get("section_surface_strategic_profile", {}) or _section_surface_strategic_profile(section))
        for section in list(body_sections or [])
    ]
    inventory_profiles = [
        _section_surface_inventory_profile(section)
        for section in list(body_sections or [])
    ]
    high_value_available = sum(
        1
        for profile in strategic_profiles
        if str(profile.get("strategic_value_tier", "")).strip() in {"thesis_critical", "strategic_support"}
    )
    total_body_sections = len(list(body_sections or []))
    demoted_to_appendix_count = 0
    retained_protected_count = 0
    retained_low_value_due_to_floor_count = 0
    retained_low_value_due_to_surface_depth_count = 0
    retained_readout_surface_count = 0
    retained_noninventory_optional_count = 0

    for idx, section in enumerate(list(body_sections or [])):
        row = dict(section)
        title = str(row.get("title", "")).strip()
        outline_key = str(row.get("outline_section_key", "")).strip()
        strategic_profile = strategic_profiles[idx]
        inventory_profile = inventory_profiles[idx]
        remaining_body_if_demoted = len(retained_body) + (total_body_sections - idx - 1)
        is_protected = (
            outline_key in _SECTION_SURFACE_DENSITY_PROTECTED_KEYS
            or title in _SECTION_SURFACE_DENSITY_PROTECTED_TITLES
            or title in normalized_required_titles
        )
        low_value_optional = str(strategic_profile.get("strategic_value_tier", "")).strip() in {
            "surface_optional",
            "supportive_context",
        }
        inventory_heavy = bool(inventory_profile.get("inventory_heavy", False))
        readout_signal_count = int(inventory_profile.get("readout_signal_count", 0) or 0)
        policy_state = "retained_noninventory_surface_section"
        policy_reason = "Section does not read as a registry-like surface and can remain in the primary body."
        destination_surface = "body"

        if is_protected:
            policy_state = "retained_inventory_protected_section"
            policy_reason = "Section remains because it belongs to the protected strategic or contract-required spine."
            retained_protected_count += 1
        elif not low_value_optional:
            policy_state = "retained_higher_value_surface_section"
            policy_reason = "Section is not surface-optional, so inventory tone alone cannot demote it."
        elif readout_signal_count > 0:
            policy_state = "retained_optional_section_with_readout_surface"
            policy_reason = "Section is optional but still carries an explicit strategic readout, so it remains on the primary surface."
            retained_readout_surface_count += 1
        elif not inventory_heavy:
            policy_state = "retained_optional_but_noninventory_section"
            policy_reason = "Section is optional, but it does not collapse into a registry-like surface."
            retained_noninventory_optional_count += 1
        elif high_value_available < minimum_high_value_sections:
            policy_state = "retained_inventory_optional_due_to_surface_depth"
            policy_reason = "Section is registry-like and optional, but the current body does not yet have enough high-value sections to absorb the demotion."
            retained_low_value_due_to_surface_depth_count += 1
        elif remaining_body_if_demoted < minimum_body_sections:
            policy_state = "retained_inventory_optional_due_to_minimum_surface_floor"
            policy_reason = "Section is registry-like and optional, but demoting it would collapse the minimum body-surface floor."
            retained_low_value_due_to_floor_count += 1
        else:
            policy_state = "demoted_inventory_like_optional_section_to_appendix"
            policy_reason = "Section is strategically optional and reads more like a governed register than a primary-surface insight layer, so appendix preserves it instead."
            destination_surface = "appendix"
            demoted_row = {
                **row,
                "section_type": "appendix",
                "demoted_from_surface": "body",
                "demoted_to_surface": "appendix",
                "section_surface_inventory_state": policy_state,
                "section_surface_inventory_profile": dict(inventory_profile),
            }
            appended_appendix.append(demoted_row)
            demoted_to_appendix_count += 1

        policy_entry = {
            "section_id": str(row.get("section_id", "")).strip(),
            "section_title": title,
            "outline_section_key": outline_key,
            "protected": is_protected,
            "strategic_value_tier": str(strategic_profile.get("strategic_value_tier", "")).strip(),
            "low_value_optional": low_value_optional,
            "inventory_heavy": inventory_heavy,
            "inventory_score": inventory_profile["inventory_score"],
            "narrative_score": inventory_profile["narrative_score"],
            "label_like_ratio": inventory_profile["label_like_ratio"],
            "label_like_line_count": inventory_profile["label_like_line_count"],
            "inventory_token_hits": inventory_profile["inventory_token_hits"],
            "readout_signal_count": readout_signal_count,
            "policy_state": policy_state,
            "policy_reason": policy_reason,
            "destination_surface": destination_surface,
        }
        policy_rows.append(policy_entry)

        if destination_surface == "body":
            retained_row = {
                **row,
                "section_surface_inventory_state": policy_state,
                "section_surface_inventory_profile": dict(inventory_profile),
            }
            retained_body.append(retained_row)

    summary = {
        "minimum_body_sections": minimum_body_sections,
        "minimum_high_value_sections": minimum_high_value_sections,
        "required_body_title_count": len(normalized_required_titles),
        "total_body_sections_evaluated": total_body_sections,
        "high_value_available": high_value_available,
        "demoted_to_appendix_count": demoted_to_appendix_count,
        "retained_protected_count": retained_protected_count,
        "retained_low_value_due_to_floor_count": retained_low_value_due_to_floor_count,
        "retained_low_value_due_to_surface_depth_count": retained_low_value_due_to_surface_depth_count,
        "retained_readout_surface_count": retained_readout_surface_count,
        "retained_noninventory_optional_count": retained_noninventory_optional_count,
    }
    return retained_body, appended_appendix, policy_rows, summary


def _merge_claim_contract_registers(
    legacy_register: list[dict[str, Any]],
    governed_register: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """Combine the legacy claim register (motor_034) with the governed one
    (motor_054.congruence_claim_contract_register) for unified rendering.

    Rules:
      - Same claim_id present in both: governed wins (it carries the
        four-state vocabulary and explicit falsification_condition).
      - claim_id only in governed: appended after the legacy entries so
        legacy ordering is preserved for backward-compatibility.
      - claim_id only in legacy: kept as-is.

    Returns a new list; inputs are not mutated.
    """
    governed_by_id = {
        str(row.get("claim_id", "")).strip(): dict(row)
        for row in (governed_register or [])
        if str(row.get("claim_id", "")).strip()
    }
    seen_ids: set[str] = set()
    merged: list[dict[str, Any]] = []
    for row in (legacy_register or []):
        claim_id = str(row.get("claim_id", "")).strip()
        if not claim_id:
            merged.append(dict(row))
            continue
        if claim_id in governed_by_id:
            merged.append(governed_by_id[claim_id])
        else:
            merged.append(dict(row))
        seen_ids.add(claim_id)
    for claim_id, governed_row in governed_by_id.items():
        if claim_id in seen_ids:
            continue
        merged.append(governed_row)
    return merged


def _candidate_claim_ids_for_section(
    title: str,
    claim_contract_register: list[dict[str, Any]],
) -> list[str]:
    contract_map = {
        str(row.get("claim_id", "")).strip(): row
        for row in claim_contract_register
        if str(row.get("claim_id", "")).strip()
    }
    if not contract_map:
        return []
    permission_filtered = [
        claim_id
        for claim_id, row in contract_map.items()
        if str(row.get("permission", "")).strip().lower() in {"prohibited", "screening_only", "hypothesis_only"}
    ]
    prohibited_use_filtered = [
        claim_id
        for claim_id, row in contract_map.items()
        if list(row.get("prohibited_use", []) or [])
    ]
    title_map = {
        "Framework Context & Executive Brief": [
            "public_asset_identity_claim",
            "compliance_screening_claim",
            "financial_exposure_claim",
            "TAD_action_claim",
        ],
        "Executive Structural Thesis": [
            "compliance_screening_claim",
            "financial_exposure_claim",
            "TAD_action_claim",
        ],
        "Executive Structural Brief": [
            "compliance_screening_claim",
            "financial_exposure_claim",
            "peer_comparison_claim",
            "redesign_hypothesis_claim",
            "TAD_action_claim",
        ],
        "Reframed Problem": [
            "operational_boundary_claim",
            "process_driver_claim",
        ],
        "Operational Identity": [
            "public_asset_identity_claim",
            "operational_boundary_claim",
            "energy_baseline_claim",
        ],
        "Dominant Structural Contradiction": [
            "redesign_hypothesis_claim",
            "financial_exposure_claim",
        ],
        "System Abstraction Snapshot": [
            "operational_boundary_claim",
            "process_driver_claim",
        ],
        "System Abstraction Map": [
            "operational_boundary_claim",
            "process_driver_claim",
        ],
        "Dominant Variables": [
            "process_driver_claim",
            "energy_baseline_claim",
            "operational_boundary_claim",
        ],
        "Evidence State by Layer": [
            "financial_exposure_claim",
            "redesign_hypothesis_claim",
        ],
        "Cross-Layer Contradictions": [
            "redesign_hypothesis_claim",
            "financial_exposure_claim",
        ],
        "Scenario Space": [
            "financial_exposure_claim",
        ],
        "Scenario Space Under Current Uncertainty": [
            "financial_exposure_claim",
        ],
        "Financial Exposure Under Uncertainty": [
            "financial_exposure_claim",
        ],
        "Financial Context": [
            "financial_exposure_claim",
        ],
        "Peer / Competitive Comparison": [
            "peer_comparison_claim",
            "competitive_advantage_claim",
        ],
        "Competitive / Peer Comparison": [
            "peer_comparison_claim",
            "competitive_advantage_claim",
        ],
        "Conditional Redesign Pathway": [
            "redesign_hypothesis_claim",
            "redesign_recommendation_claim",
        ],
        "Structural Benchmarking & Competitive Comparison": [
            "peer_comparison_claim",
            "competitive_advantage_claim",
        ],
        "Conditional Redesign Pathways": [
            "redesign_hypothesis_claim",
            "redesign_recommendation_claim",
        ],
        "Conditional Redesign & Structural Financial Exposure": [
            "redesign_hypothesis_claim",
            "financial_exposure_claim",
        ],
        "Minimum Evidence for Discrimination": [
            "TAD_action_claim",
        ],
        "TAD — Immediate Action Priority": [
            "TAD_action_claim",
        ],
        "TAD — Action Priority": [
            "TAD_action_claim",
        ],
        "TAD — Decision-Admissibility Layer": [
            "TAD_action_claim",
        ],
        "Claim Permissions / What Not To Do": permission_filtered or prohibited_use_filtered or sorted(contract_map),
        "What Not To Do Yet": permission_filtered or prohibited_use_filtered or sorted(contract_map),
        "Claim Permission Matrix": sorted(contract_map),
        "Structural Claim Permissions, Output Modes & Expanded TAD": sorted(contract_map),
        "Source Traceability": sorted(
            claim_id
            for claim_id, row in contract_map.items()
            if list(row.get("supporting_sources", []) or [])
        ),
        "Public Source Coverage Table": sorted(
            claim_id
            for claim_id, row in contract_map.items()
            if list(row.get("supporting_sources", []) or [])
        ),
    }
    return [
        claim_id
        for claim_id in title_map.get(title, [])
        if claim_id in contract_map
    ]


def _attach_claim_contract_traces(
    body_sections: list[dict[str, Any]],
    appendix_sections: list[dict[str, Any]],
    claim_contract_register: list[dict[str, Any]],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]:
    contract_map = {
        str(row.get("claim_id", "")).strip(): dict(row)
        for row in claim_contract_register
        if str(row.get("claim_id", "")).strip()
    }
    trace_rows: list[dict[str, Any]] = []

    def _annotate(section: dict[str, Any], surface: str) -> dict[str, Any]:
        annotated = dict(section)
        title = str(section.get("title", "")).strip()
        excerpt = _section_visible_excerpt(section)
        claim_ids = _candidate_claim_ids_for_section(title, claim_contract_register)
        blocks = list(section.get("blocks", []) or [])
        first_block = dict((blocks[0] or {})) if blocks else {}
        section_id = str(section.get("section_id", "")).strip() or str(section.get("chapter_id", "")).strip()
        block_id = (
            str(section.get("block_ref", "")).strip()
            or str(first_block.get("block_id", "")).strip()
            or f"{str(section.get('chapter_id', '')).strip() or 'section'}:0"
        )
        traces: list[dict[str, Any]] = []
        for claim_id in claim_ids:
            contract_row = dict(contract_map.get(claim_id, {}) or {})
            trace_row = {
                "section_id": section_id,
                "section_title": title,
                "section_surface": surface,
                "block_id": block_id,
                "claim_id": claim_id,
                "visible_statement_excerpt": excerpt,
                "statement": str(contract_row.get("statement", "")).strip(),
                "evidence_state": str(contract_row.get("evidence_state", "")).strip(),
                "supporting_sources": list(contract_row.get("supporting_sources", []) or []),
                "assumptions": list(contract_row.get("assumptions", []) or []),
                "falsification_condition": str(contract_row.get("falsification_condition", "")).strip(),
                "minimum_evidence_required": list(contract_row.get("minimum_evidence_required", []) or []),
                "allowed_use": list(contract_row.get("allowed_use", []) or []),
                "prohibited_use": list(contract_row.get("prohibited_use", []) or []),
                "permission": (
                    str(contract_row.get("permission", "")).strip()
                    or str(contract_row.get("current_permission", "")).strip()
                    or "allowed"
                ),
            }
            traces.append(trace_row)
            trace_rows.append(trace_row)
        annotated["claim_refs"] = claim_ids
        annotated["claim_traces"] = traces
        return annotated

    annotated_body = [_annotate(section, "body") for section in list(body_sections or [])]
    annotated_appendix = [_annotate(section, "appendix") for section in list(appendix_sections or [])]
    return annotated_body, annotated_appendix, trace_rows


def _build_structural_intelligence_appendices(bundle: dict[str, Any]) -> list[dict[str, Any]]:
    system_abstraction = dict(bundle.get("system_abstraction", {}) or {})
    dominant_variable_register = list(bundle.get("dominant_variable_register", []) or [])
    evidence_state_by_layer_register = list(bundle.get("evidence_state_by_layer_register", []) or [])
    cross_layer_conflict_register = list(bundle.get("cross_layer_conflict_register", []) or [])
    problem_framing_register = list(bundle.get("problem_framing_register", []) or [])
    structural_benchmark_register = list(bundle.get("structural_benchmark_register", []) or [])
    competitive_comparison_register = list(bundle.get("competitive_comparison_register", []) or [])
    conditional_redesign_register = list(bundle.get("conditional_redesign_register", []) or [])
    structural_financial_exposure_register = list(bundle.get("structural_financial_exposure_register", []) or [])
    minimum_evidence_for_discrimination_register = list(bundle.get("minimum_evidence_for_discrimination_register", []) or [])
    structural_claim_permission_register = list(bundle.get("structural_claim_permission_register", []) or [])
    structural_output_mode_classifier_table = list(bundle.get("structural_output_mode_classifier_table", []) or [])
    expanded_structural_tad_action_register = list(bundle.get("expanded_structural_tad_action_register", []) or [])

    if not any(
        [
            system_abstraction,
            dominant_variable_register,
            evidence_state_by_layer_register,
            cross_layer_conflict_register,
            problem_framing_register,
            structural_benchmark_register,
            competitive_comparison_register,
            conditional_redesign_register,
            structural_financial_exposure_register,
            minimum_evidence_for_discrimination_register,
            structural_claim_permission_register,
            structural_output_mode_classifier_table,
            expanded_structural_tad_action_register,
        ]
    ):
        return []

    sections: list[dict[str, Any]] = []
    a9 = [_sep("="), "SYSTEM ABSTRACTION MAP", _sep("="), ""]
    if not system_abstraction:
        a9 += ["  No structural abstraction fields were produced.", ""]
    else:
        for key in [
            "asset_type",
            "business_function",
            "value_creation_mechanism",
            "dominant_process_type",
            "dominant_physical_drivers",
            "dominant_operational_drivers",
            "control_structure",
            "constraint_structure",
            "economic_driver",
            "regulatory_exposure",
            "evidence_maturity",
        ]:
            row = system_abstraction.get(key)
            if not isinstance(row, dict):
                continue
            a9 += [
                f"  Field             : {key}",
                f"  Statement         : {row.get('statement', '')}",
                f"  Evidence State    : {row.get('evidence_state', '')}",
                f"  Supporting Source : {', '.join(row.get('supporting_sources', []) or []) or 'NONE'}",
                f"  Falsifies it      : {row.get('falsification_condition', '')}",
                f"  Minimum Evidence  : {', '.join(row.get('minimum_evidence_required', []) or []) or 'NONE'}",
                "",
            ]
    sections.append(_section("a9_system_abstraction_map", "A9", 9, "System Abstraction Map", "technical", "appendix", "STRUCTURAL_LANE | MIXED_EVIDENCE", "", "b_structural_system_abstraction", a9))

    a10 = [_sep("="), "DOMINANT VARIABLES", _sep("="), ""]
    if not dominant_variable_register:
        a10 += ["  No dominant-variable rows were produced.", ""]
    for row in dominant_variable_register:
        a10 += [
            f"  Variable          : {row.get('variable', '')}",
            f"  Layer             : {row.get('layer', '')}",
            f"  Dominance         : {row.get('dominance', '')}",
            f"  Evidence State    : {row.get('evidence_state', '')}",
            f"  Why It Matters    : {row.get('why_it_could_matter', '')}",
            f"  Confirms It       : {row.get('what_confirms_it', '')}",
            f"  Falsifies It      : {row.get('what_falsifies_it', '')}",
            f"  Decision Impact   : {row.get('decision_impact', '')}",
            "",
        ]
    sections.append(_section("a10_dominant_variables", "A10", 10, "Dominant Variables", "technical", "appendix", "STRUCTURAL_LANE | DOMINANT_VARIABLES", "", "b_structural_dominant_variables", a10))

    a17 = [_sep("="), "EVIDENCE STATE BY LAYER", _sep("="), ""]
    if not evidence_state_by_layer_register:
        a17 += ["  No layer-evidence rows were produced.", ""]
    for row in evidence_state_by_layer_register:
        a17 += [
            f"  Layer             : {row.get('layer', '')}",
            f"  Evidence State    : {row.get('evidence_state', '')}",
            f"  Observed Support  : {', '.join(row.get('observed_support', []) or []) or 'NONE'}",
            f"  Open Questions    : {', '.join(row.get('dominant_open_questions', []) or []) or 'NONE'}",
            f"  Structural Risk   : {row.get('structural_risk_if_wrong', '')}",
            f"  Linked Conflicts  : {', '.join(row.get('linked_conflicts', []) or []) or 'NONE'}",
            f"  Linked Framing    : {', '.join(row.get('linked_problem_frames', []) or []) or 'NONE'}",
            "",
        ]
    sections.append(_section("a17_evidence_state_by_layer", "A17", 17, "Evidence State by Layer", "technical", "appendix", "STRUCTURAL_LANE | LAYER_EVIDENCE", "", "b_structural_evidence_state_by_layer", a17))

    a11 = [_sep("="), "CROSS-LAYER CONTRADICTIONS", _sep("="), ""]
    if not cross_layer_conflict_register:
        a11 += ["  No cross-layer contradictions were produced.", ""]
    for row in cross_layer_conflict_register:
        a11 += [
            f"  Conflict          : {row.get('conflict', '')}",
            f"  Layers Involved   : {', '.join(row.get('layers_involved', []) or []) or 'NONE'}",
            f"  Evidence State    : {row.get('evidence_state', '')}",
            f"  Why It Matters    : {row.get('why_it_matters', '')}",
            f"  Confirms It       : {row.get('what_confirms_it', '')}",
            f"  Falsifies It      : {row.get('what_falsifies_it', '')}",
            f"  Redesign Direction: {row.get('potential_redesign_direction', '')}",
            "",
        ]
    sections.append(_section("a11_cross_layer_contradictions", "A11", 11, "Cross-Layer Contradictions", "technical", "appendix", "STRUCTURAL_LANE | CONDITIONAL", "", "b_structural_cross_layer_conflicts", a11))

    a12 = [_sep("="), "PROBLEM FRAMING", _sep("="), ""]
    if not problem_framing_register:
        a12 += ["  No problem-framing rows were produced.", ""]
    for row in problem_framing_register:
        a12 += [
            f"  Stated Problem    : {row.get('stated_problem', '')}",
            f"  Reframed Problem  : {row.get('reframed_problem', '')}",
            f"  Why Reframe       : {row.get('why_original_framing_may_be_wrong', '')}",
            f"  Evidence Needed   : {row.get('evidence_needed', '')}",
            f"  Strategic Risk    : {row.get('strategic_risk', '')}",
            f"  Linked Layers     : {', '.join(row.get('linked_layers', []) or []) or 'NONE'}",
            "",
        ]
    sections.append(_section("a12_problem_framing", "A12", 12, "Problem Framing", "executive", "appendix", "STRUCTURAL_LANE | REFRAMING", "", "b_structural_problem_framing", a12))

    a13 = [_sep("="), "STRUCTURAL BENCHMARKING & COMPETITIVE COMPARISON", _sep("="), "", _sep("-"), "STRUCTURAL BENCHMARKING", _sep("-"), ""]
    if not structural_benchmark_register:
        a13 += ["  No structural benchmarking rows were produced.", ""]
    for row in structural_benchmark_register:
        a13 += [
            f"  Dimension         : {row.get('dimension', '')}",
            f"  Subject Asset     : {row.get('subject_asset', '')}",
            f"  Peer / Benchmark  : {row.get('peer_or_benchmark', '')}",
            f"  Difference        : {row.get('difference', '')}",
            f"  Evidence State    : {row.get('evidence_state', '')}",
            f"  Interpretation    : {row.get('interpretation', '')}",
            "",
        ]
    a13 += [_sep("-"), "COMPETITIVE COMPARISON", _sep("-"), ""]
    if not competitive_comparison_register:
        a13 += ["  No competitive-comparison rows were produced.", ""]
    for row in competitive_comparison_register:
        a13 += [
            f"  Better Performer  : {row.get('better_performer', '')}",
            f"  What They Do Better: {row.get('what_they_do_better', '')}",
            f"  Structural Advantage: {row.get('structural_advantage', '')}",
            f"  Why It Matters    : {row.get('why_it_matters', '')}",
            f"  Transferability   : {row.get('transferability', '')}",
            f"  Evidence Needed   : {row.get('evidence_needed', '')}",
            f"  Evidence State    : {row.get('evidence_state', '')}",
            "",
        ]
    sections.append(_section("a13_structural_benchmarking_and_competition", "A13", 13, "Structural Benchmarking & Competitive Comparison", "technical", "appendix", "STRUCTURAL_LANE | COMPARISON", "", "b_structural_benchmarking_competition", a13))

    a14 = [_sep("="), "CONDITIONAL REDESIGN & STRUCTURAL FINANCIAL EXPOSURE", _sep("="), "", _sep("-"), "CONDITIONAL REDESIGN", _sep("-"), ""]
    if not conditional_redesign_register:
        a14 += ["  No conditional-redesign rows were produced.", ""]
    for row in conditional_redesign_register:
        a14 += [
            f"  Hypothesis        : {row.get('hypothesis', '')}",
            f"  Evidence State    : {row.get('evidence_state', '')}",
            f"  If Confirmed      : {row.get('if_confirmed', '')}",
            f"  Redesign Direction: {row.get('redesign_direction', '')}",
            f"  If Falsified      : {row.get('if_falsified', '')}",
            f"  Next Evidence     : {', '.join(row.get('next_evidence', []) or []) or 'NONE'}",
            "",
        ]
    a14 += [_sep("-"), "STRUCTURAL FINANCIAL EXPOSURE", _sep("-"), ""]
    if not structural_financial_exposure_register:
        a14 += ["  No structural financial-exposure rows were produced.", ""]
    for row in structural_financial_exposure_register:
        a14 += [
            f"  Structural Assumption : {row.get('structural_assumption', '')}",
            f"  Evidence State        : {row.get('evidence_state', '')}",
            f"  Exposure If Wrong     : {row.get('financial_exposure_if_wrong', '')}",
            f"  Evidence Needed       : {row.get('evidence_needed', '')}",
            f"  Allowed Output        : {', '.join(row.get('allowed_financial_output', []) or []) or 'NONE'}",
            f"  Prohibited Output     : {', '.join(row.get('prohibited_financial_output', []) or []) or 'NONE'}",
            "",
        ]
    sections.append(_section("a14_conditional_redesign_and_structural_financial_exposure", "A14", 14, "Conditional Redesign & Structural Financial Exposure", "technical", "appendix", "STRUCTURAL_LANE | CONDITIONAL", "", "b_structural_redesign_finance", a14))

    a15 = [_sep("="), "MINIMUM EVIDENCE FOR DISCRIMINATION", _sep("="), ""]
    if not minimum_evidence_for_discrimination_register:
        a15 += ["  No discrimination-evidence rows were produced.", ""]
    for row in minimum_evidence_for_discrimination_register:
        a15 += [
            f"  Rival Hypotheses  : {', '.join(row.get('rival_hypotheses', []) or []) or 'NONE'}",
            f"  Minimum Evidence  : {row.get('minimum_evidence', '')}",
            f"  Source            : {row.get('source', '')}",
            f"  Confirms          : {row.get('what_it_confirms', '')}",
            f"  Falsifies         : {row.get('what_it_falsifies', '')}",
            f"  Unlocks           : {row.get('unlocks', '')}",
            "",
        ]
    sections.append(_section("a15_minimum_evidence_for_discrimination", "A15", 15, "Minimum Evidence for Discrimination", "technical", "appendix", "STRUCTURAL_LANE | DISCRIMINATION", "", "b_structural_minimum_evidence_discrimination", a15))

    a16 = [_sep("="), "STRUCTURAL CLAIM PERMISSIONS, OUTPUT MODES & EXPANDED TAD", _sep("="), "", _sep("-"), "STRUCTURAL CLAIM PERMISSIONS", _sep("-"), ""]
    if not structural_claim_permission_register:
        a16 += ["  No structural claim-permission rows were produced.", ""]
    for row in structural_claim_permission_register:
        a16 += [
            f"  Claim             : {row.get('claim', '')}",
            f"  Permission        : {row.get('permission', '')}",
            f"  Evidence Required : {', '.join(row.get('evidence_required', []) or []) or 'NONE'}",
            f"  Current Evidence  : {row.get('current_evidence', '')}",
            f"  Allowed Language  : {row.get('allowed_language', '')}",
            f"  Forbidden Language: {row.get('forbidden_language', '')}",
            "",
        ]
    a16 += [_sep("-"), "STRUCTURAL OUTPUT MODES", _sep("-"), ""]
    if not structural_output_mode_classifier_table:
        a16 += ["  No structural output-mode rows were produced.", ""]
    for row in structural_output_mode_classifier_table:
        a16 += [
            f"  Asset             : {row.get('asset', '')}",
            f"  Output Mode       : {row.get('recommended_output_mode', '')}",
            f"  Activation State  : {row.get('activation_state', '')}",
            f"  Why               : {row.get('why', '')}",
            "",
        ]
    a16 += [_sep("-"), "EXPANDED STRUCTURAL TAD ACTIONS", _sep("-"), ""]
    if not expanded_structural_tad_action_register:
        a16 += ["  No expanded structural TAD actions were produced.", ""]
    for row in expanded_structural_tad_action_register:
        a16 += [
            f"  Action            : {row.get('action', '')}",
            f"  Status            : {row.get('status', '')}",
            f"  Why               : {row.get('why', '')}",
            f"  Evidence State    : {row.get('evidence_state', '')}",
            f"  Financial Exposure: {row.get('financial_exposure', '')}",
            f"  Evidence Needed   : {row.get('evidence_needed', '')}",
            f"  Prohibited Action : {row.get('prohibited_action', '')}",
            "",
        ]
    sections.append(_section("a16_structural_claims_output_modes_and_tad", "A16", 16, "Structural Claim Permissions, Output Modes & Expanded TAD", "technical", "appendix", "GOVERNED_REGISTER", "", "b_structural_claims_output_modes_tad", a16))

    return sections


def _build_structural_primary_body_sections(  # noqa: PLR0913
    document_label: str,
    main_warning: str,
    allowed_use: list[str],
    prohibited_use: list[str],
    structural_executive_summary: dict[str, Any],
    client_concern: dict[str, Any],
    system_abstraction: dict[str, Any],
    dominant_variable_register: list[dict[str, Any]],
    evidence_state_by_layer_register: list[dict[str, Any]],
    cross_layer_conflict_register: list[dict[str, Any]],
    scenario_space: list[dict[str, Any]],
    structural_financial_exposure_register: list[dict[str, Any]],
    structural_benchmark_register: list[dict[str, Any]],
    competitive_comparison_register: list[dict[str, Any]],
    conditional_redesign_register: list[dict[str, Any]],
    minimum_evidence_for_discrimination_register: list[dict[str, Any]],
    expanded_structural_tad_action_register: list[dict[str, Any]],
    client_facing_tad: dict[str, Any],
    claim_contract_register: list[dict[str, Any]],
    source_family_coverage_table: list[dict[str, Any]],
    problem_framing_register: list[dict[str, Any]],
    llm_lookup: dict[str, str],
    llm_lookup_en: dict[str, str],
    llm_lookup_es: dict[str, str],
) -> list[dict[str, Any]]:
    def _join(values: Any, default: str = "NONE") -> str:
        if isinstance(values, list):
            cleaned = [str(v).strip() for v in values if str(v).strip()]
            return ", ".join(cleaned) if cleaned else default
        text = str(values or "").strip()
        return text or default

    structural_executive_summary = dict(structural_executive_summary or {})
    stated_problem = (
        str(structural_executive_summary.get("stated_problem", "")).strip()
        or str(client_concern.get("primary_concern", "")).strip()
        or "Problem statement not explicitly supplied at intake."
    )
    client_subconcerns = [str(item).strip() for item in list(client_concern.get("sub_concerns", []) or []) if str(item).strip()]
    primary_action = str(structural_executive_summary.get("primary_structural_action", "")).strip()
    primary_action_status = str(structural_executive_summary.get("primary_structural_action_status", "")).strip()
    leading_mode = str(structural_executive_summary.get("leading_primary_structural_mode", "")).strip()
    default_reasoning_path = str(structural_executive_summary.get("default_reasoning_path", "")).strip() or "legacy_decision_gating_only"
    problem_frame_active = bool(structural_executive_summary.get("problem_frame_active", False))

    c1 = [
        _sep("="),
        document_label.upper(),
        _sep("="),
        "",
        _sep("-"),
        "STRUCTURAL READ",
        _sep("-"),
        "",
        f"  Visible Output Mode : {document_label}",
        f"  Main Warning        : {main_warning}",
        f"  Reasoning Path      : {default_reasoning_path}",
        f"  Problem Frame Active: {'YES' if problem_frame_active else 'NO'}",
        f"  Leading Structural Mode: {leading_mode or 'NONE'}",
        f"  Thesis State        : {structural_executive_summary.get('thesis_state', '')}",
        f"  Local Claim Closure : {structural_executive_summary.get('local_claim_closure_state', '')}",
        f"  Reframed Problem    : {structural_executive_summary.get('primary_reframed_problem', '')}",
        f"  Dominant Conflict   : {structural_executive_summary.get('dominant_structural_conflict', '')}",
        f"  Why Premature       : {structural_executive_summary.get('why_current_question_is_premature', '')}",
        f"  Wrong Variable Risk : {structural_executive_summary.get('dominant_operational_misunderstanding', '')}",
        f"  Boundary Error      : {structural_executive_summary.get('hidden_system_boundary_error', '')}",
        f"  Invalid Comparison  : {structural_executive_summary.get('invalid_comparison_risk', '')}",
        f"  Dominant Loss Logic : {structural_executive_summary.get('dominant_loss_logic', '')}",
        f"  Why It Matters      : {structural_executive_summary.get('why_it_matters', '')}",
        f"  Dominant Risk       : {structural_executive_summary.get('dominant_risk', '')}",
        f"  Strategic Nugget    : {_join(structural_executive_summary.get('top_gold_nuggets', []), default='NONE BOUNDED')}",
        f"  Priority Action     : {primary_action} [{primary_action_status}]",
        f"  Not Admissible      : {_join(structural_executive_summary.get('not_admissible_actions', []), default='NONE BOUNDED')}",
        f"  Constraint          : {structural_executive_summary.get('bounded_note', '')}",
        "",
        "  This report treats structural understanding as the decision object.",
        "  It does not close verification, ROI, savings, compliance closure, or investment recommendations beyond the current claim ceiling.",
        "",
        f"  Allowed Use         : {'; '.join(allowed_use)}",
        f"  Prohibited Use      : {'; '.join(prohibited_use)}",
        "",
    ]
    c1_es = [
        _sep("="),
        document_label.upper(),
        _sep("="),
        "",
        _sep("-"),
        "LECTURA ESTRUCTURAL",
        _sep("-"),
        "",
        f"  Modo Visible de Salida : {document_label}",
        f"  Advertencia Principal  : {main_warning}",
        f"  Ruta de Razonamiento   : {default_reasoning_path}",
        f"  Marco del Problema Activo: {'SÍ' if problem_frame_active else 'NO'}",
        f"  Modo Estructural Líder : {leading_mode or 'NINGUNO'}",
        f"  Estado de la Tesis    : {structural_executive_summary.get('thesis_state', '')}",
        f"  Cierre de Claim Local : {structural_executive_summary.get('local_claim_closure_state', '')}",
        f"  Problema Reencuadrado  : {structural_executive_summary.get('primary_reframed_problem', '')}",
        f"  Conflicto Dominante    : {structural_executive_summary.get('dominant_structural_conflict', '')}",
        f"  Por Qué Es Prematuro   : {structural_executive_summary.get('why_current_question_is_premature', '')}",
        f"  Riesgo de Variable Equivocada: {structural_executive_summary.get('dominant_operational_misunderstanding', '')}",
        f"  Error de Frontera      : {structural_executive_summary.get('hidden_system_boundary_error', '')}",
        f"  Comparación Inválida   : {structural_executive_summary.get('invalid_comparison_risk', '')}",
        f"  Lógica Dominante de Pérdida: {structural_executive_summary.get('dominant_loss_logic', '')}",
        f"  Por Qué Importa        : {structural_executive_summary.get('why_it_matters', '')}",
        f"  Riesgo Dominante       : {structural_executive_summary.get('dominant_risk', '')}",
        f"  Gold Nugget Estratégico: {_join(structural_executive_summary.get('top_gold_nuggets', []), default='NINGUNO ACOTADO')}",
        f"  Acción Prioritaria     : {primary_action} [{primary_action_status}]",
        f"  No Admisible           : {_join(structural_executive_summary.get('not_admissible_actions', []), default='NINGÚN CIERRE ADICIONAL ACOTADO')}",
        f"  Restricción            : {structural_executive_summary.get('bounded_note', '')}",
        "",
        "  Este informe trata la comprensión estructural como el verdadero objeto de decisión.",
        "  No cierra verificación, ROI, savings, cierre de compliance ni recomendaciones de inversión más allá del techo actual de claims.",
        "",
        f"  Uso Permitido          : {'; '.join(allowed_use)}",
        f"  Uso Prohibido          : {'; '.join(prohibited_use)}",
        "",
    ]

    c2 = [
        _sep("="),
        "WHAT THE CLIENT THINKS THE PROBLEM IS",
        _sep("="),
        "",
        f"  Stated Problem      : {stated_problem}",
        "",
    ]
    c2_es = [
        _sep("="),
        "LO QUE EL CLIENTE CREE QUE ES EL PROBLEMA",
        _sep("="),
        "",
        f"  Problema Declarado    : {stated_problem}",
        "",
    ]
    if client_subconcerns:
        c2 += ["  Sub-Concerns:", *[f"    - {item}" for item in client_subconcerns], ""]
        c2_es += ["  Subpreocupaciones:", *[f"    - {item}" for item in client_subconcerns], ""]
    else:
        c2 += ["  Sub-Concerns      : NONE OBSERVED", ""]
        c2_es += ["  Subpreocupaciones : NINGUNA OBSERVADA", ""]

    c3 = [_sep("="), "WHAT THE SYSTEM THINKS THE PROBLEM MIGHT ACTUALLY BE", _sep("="), ""]
    c3_es = [_sep("="), "LO QUE EL SISTEMA CREE QUE EL PROBLEMA PODRÍA SER REALMENTE", _sep("="), ""]
    if not problem_framing_register:
        c3 += ["  No problem-reframing rows were produced.", ""]
        c3_es += ["  No se produjeron filas de reencuadre del problema.", ""]
    for row in problem_framing_register:
        c3 += [
            f"  Stated Problem      : {row.get('stated_problem', '')}",
            f"  Reframed Problem    : {row.get('reframed_problem', '')}",
            f"  Why Reframe         : {row.get('why_original_framing_may_be_wrong', '')}",
            f"  Evidence Needed     : {_join(row.get('evidence_needed', []))}",
            f"  Strategic Risk      : {row.get('strategic_risk', '')}",
            "",
        ]
        c3_es += [
            f"  Problema Declarado  : {row.get('stated_problem', '')}",
            f"  Problema Reencuadrado: {row.get('reframed_problem', '')}",
            f"  Por Qué Reencuadrar : {row.get('why_original_framing_may_be_wrong', '')}",
            f"  Evidencia Necesaria : {_join(row.get('evidence_needed', []))}",
            f"  Riesgo Estratégico  : {row.get('strategic_risk', '')}",
            "",
        ]

    c4 = [_sep("="), "SYSTEM ABSTRACTION MAP", _sep("="), ""]
    for key in [
        "asset_type",
        "business_function",
        "value_creation_mechanism",
        "dominant_process_type",
        "dominant_physical_drivers",
        "dominant_operational_drivers",
        "control_structure",
        "constraint_structure",
        "economic_driver",
        "regulatory_exposure",
        "evidence_maturity",
    ]:
        row = system_abstraction.get(key)
        if not isinstance(row, dict):
            continue
        c4 += [
            f"  Field               : {key}",
            f"  Statement           : {row.get('statement', '')}",
            f"  Evidence State      : {row.get('evidence_state', '')}",
            f"  Supporting Sources  : {_join(row.get('supporting_sources', []))}",
            f"  Falsification       : {row.get('falsification_condition', '')}",
            f"  Minimum Evidence    : {_join(row.get('minimum_evidence_required', []))}",
            "",
        ]
    if len(c4) == 4:
        c4 += ["  No system-abstraction fields were produced.", ""]

    c5 = [_sep("="), "DOMINANT VARIABLES", _sep("="), ""]
    if not dominant_variable_register:
        c5 += ["  No dominant-variable rows were produced.", ""]
    for row in dominant_variable_register:
        c5 += [
            f"  Variable            : {row.get('variable', '')}",
            f"  Layer               : {row.get('layer', '')}",
            f"  Dominance           : {row.get('dominance', '')}",
            f"  Evidence State      : {row.get('evidence_state', '')}",
            f"  Why It Could Matter : {row.get('why_it_could_matter', '')}",
            f"  What Confirms It    : {row.get('what_confirms_it', '')}",
            f"  What Falsifies It   : {row.get('what_falsifies_it', '')}",
            f"  Decision Impact     : {row.get('decision_impact', '')}",
            "",
        ]

    c6 = [_sep("="), "EVIDENCE STATE BY LAYER", _sep("="), ""]
    if not evidence_state_by_layer_register:
        c6 += ["  No layer-evidence rows were produced.", ""]
    for row in evidence_state_by_layer_register:
        c6 += [
            f"  Layer               : {row.get('layer', '')}",
            f"  Evidence State      : {row.get('evidence_state', '')}",
            f"  Observed Support    : {_join(row.get('observed_support', []))}",
            f"  Open Questions      : {_join(row.get('dominant_open_questions', []))}",
            f"  Structural Risk     : {row.get('structural_risk_if_wrong', '')}",
            f"  Linked Conflicts    : {_join(row.get('linked_conflicts', []))}",
            f"  Linked Frames       : {_join(row.get('linked_problem_frames', []))}",
            "",
        ]

    c7 = [_sep("="), "CROSS-LAYER CONTRADICTIONS", _sep("="), ""]
    if not cross_layer_conflict_register:
        c7 += ["  No cross-layer contradiction rows were produced.", ""]
    for row in cross_layer_conflict_register:
        c7 += [
            f"  Conflict            : {row.get('conflict', '')}",
            f"  Layers Involved     : {_join(row.get('layers_involved', []))}",
            f"  Evidence State      : {row.get('evidence_state', '')}",
            f"  Why It Matters      : {row.get('why_it_matters', '')}",
            f"  What Confirms It    : {row.get('what_confirms_it', '')}",
            f"  What Falsifies It   : {row.get('what_falsifies_it', '')}",
            f"  Potential Redesign  : {row.get('potential_redesign_direction', '')}",
            "",
        ]

    c8 = [_sep("="), "SCENARIO SPACE", _sep("="), ""]
    if not scenario_space:
        c8 += ["  No scenario rows were produced.", ""]
    for row in scenario_space:
        c8 += [
            f"  Scenario            : {row.get('scenario', '')}",
            f"  Plausibility        : {row.get('plausibility_status', '')}",
            f"  Financial Meaning   : {row.get('financial_meaning', '')}",
            f"  What Confirms It    : {row.get('what_would_make_it_true', '')}",
            f"  What Falsifies It   : {row.get('what_would_falsify_it', '')}",
            f"  Evidence Needed     : {row.get('evidence_needed', '')}",
            f"  Evidence Link       : {row.get('linked_evidence_item', '')}",
            f"  Decision Front      : {row.get('linked_decision_front', '')}",
            "",
        ]

    c9 = [_sep("="), "FINANCIAL EXPOSURE UNDER UNCERTAINTY", _sep("="), ""]
    if not structural_financial_exposure_register:
        c9 += ["  No structural financial-exposure rows were produced.", ""]
    for row in structural_financial_exposure_register:
        c9 += [
            f"  Structural Assumption: {row.get('structural_assumption', '')}",
            f"  Evidence State       : {row.get('evidence_state', '')}",
            f"  Exposure If Wrong    : {row.get('financial_exposure_if_wrong', '')}",
            f"  Evidence Needed      : {row.get('evidence_needed', '')}",
            f"  Allowed Output       : {_join(row.get('allowed_financial_output', []))}",
            f"  Prohibited Output    : {_join(row.get('prohibited_financial_output', []))}",
            "",
        ]

    c10 = [_sep("="), "COMPETITIVE / PEER COMPARISON", _sep("="), ""]
    c10_es = [_sep("="), "COMPARACIÓN COMPETITIVA / CON PARES", _sep("="), ""]
    c10 += [_sep("-"), "STRUCTURAL BENCHMARKING", _sep("-"), ""]
    c10_es += [_sep("-"), "BENCHMARKING ESTRUCTURAL", _sep("-"), ""]
    if not structural_benchmark_register:
        c10 += ["  No structural benchmarking rows were produced.", ""]
        c10_es += ["  No se produjeron filas de benchmarking estructural.", ""]
    for row in structural_benchmark_register:
        c10 += [
            f"  Dimension           : {row.get('dimension', '')}",
            f"  Subject Asset       : {row.get('subject_asset', '')}",
            f"  Peer / Benchmark    : {row.get('peer_or_benchmark', '')}",
            f"  Difference          : {row.get('difference', '')}",
            f"  Evidence State      : {row.get('evidence_state', '')}",
            f"  Interpretation      : {row.get('interpretation', '')}",
            "",
        ]
        c10_es += [
            f"  Dimensión           : {row.get('dimension', '')}",
            f"  Activo Analizado    : {row.get('subject_asset', '')}",
            f"  Par / Benchmark     : {row.get('peer_or_benchmark', '')}",
            f"  Diferencia          : {row.get('difference', '')}",
            f"  Estado de Evidencia : {row.get('evidence_state', '')}",
            f"  Interpretación      : {row.get('interpretation', '')}",
            "",
        ]
    c10 += [_sep("-"), "COMPETITIVE COMPARISON", _sep("-"), ""]
    c10_es += [_sep("-"), "COMPARACIÓN COMPETITIVA", _sep("-"), ""]
    if not competitive_comparison_register:
        c10 += ["  No competitive-comparison rows were produced.", ""]
        c10_es += ["  No se produjeron filas de comparación competitiva.", ""]
    for row in competitive_comparison_register:
        c10 += [
            f"  Peer Type           : {row.get('peer_type', row.get('comparison_mode', ''))}",
            f"  Better Performer    : {row.get('better_performer', '')}",
            f"  What They Do Better : {row.get('what_they_do_better', '')}",
            f"  Structural Advantage: {row.get('structural_advantage', '')}",
            f"  Why It Matters      : {row.get('why_it_matters', '')}",
            f"  Transferability     : {row.get('transferability', '')}",
            f"  What It Proves      : {row.get('what_it_proves', '')}",
            f"  What It Does Not Prove: {row.get('what_it_does_not_prove', '')}",
            f"  Evidence Needed     : {_join(row.get('evidence_needed', []))}",
            f"  Evidence State      : {row.get('evidence_state', '')}",
            "",
        ]
        c10_es += [
            f"  Tipo de Par         : {row.get('peer_type', row.get('comparison_mode', ''))}",
            f"  Comparador          : {row.get('better_performer', '')}",
            f"  Qué Hace Mejor      : {row.get('what_they_do_better', '')}",
            f"  Ventaja Estructural : {row.get('structural_advantage', '')}",
            f"  Por Qué Importa     : {row.get('why_it_matters', '')}",
            f"  Transferibilidad    : {row.get('transferability', '')}",
            f"  Qué Demuestra       : {row.get('what_it_proves', '')}",
            f"  Qué No Demuestra    : {row.get('what_it_does_not_prove', '')}",
            f"  Evidencia Necesaria : {_join(row.get('evidence_needed', []))}",
            f"  Estado de Evidencia : {row.get('evidence_state', '')}",
            "",
        ]

    c11 = [_sep("="), "CONDITIONAL REDESIGN PATHWAYS", _sep("="), ""]
    c11_es = [_sep("="), "RUTAS CONDICIONADAS DE REDISEÑO", _sep("="), ""]
    if not conditional_redesign_register:
        c11 += ["  No conditional-redesign rows were produced.", ""]
        c11_es += ["  No se produjeron filas de rediseño condicional.", ""]
    for row in conditional_redesign_register:
        c11 += [
            f"  Trigger Hypothesis  : {row.get('trigger_hypothesis', row.get('hypothesis', ''))}",
            f"  Evidence State      : {row.get('evidence_state', '')}",
            f"  Conflict Resolved   : {row.get('conflict_resolved', '')}",
            f"  Economic Logic      : {row.get('economic_logic', '')}",
            f"  If Confirmed        : {row.get('if_confirmed', '')}",
            f"  Redesign Direction  : {row.get('redesign_direction', '')}",
            f"  If Falsified        : {row.get('if_falsified', '')}",
            f"  Evidence Needed     : {_join(row.get('evidence_needed', row.get('next_evidence', [])))}",
            f"  Kill Condition      : {row.get('kill_condition', row.get('if_falsified', ''))}",
            "",
        ]
        c11_es += [
            f"  Hipótesis Gatillo   : {row.get('trigger_hypothesis', row.get('hypothesis', ''))}",
            f"  Estado de Evidencia : {row.get('evidence_state', '')}",
            f"  Conflicto que Resuelve: {row.get('conflict_resolved', '')}",
            f"  Lógica Económica    : {row.get('economic_logic', '')}",
            f"  Si se Confirma      : {row.get('if_confirmed', '')}",
            f"  Dirección de Rediseño: {row.get('redesign_direction', '')}",
            f"  Si se Falsifica     : {row.get('if_falsified', '')}",
            f"  Evidencia Necesaria : {_join(row.get('evidence_needed', row.get('next_evidence', [])))}",
            f"  Condición de Muerte : {row.get('kill_condition', row.get('if_falsified', ''))}",
            "",
        ]

    c12 = [_sep("="), "MINIMUM EVIDENCE FOR DISCRIMINATION", _sep("="), ""]
    if not minimum_evidence_for_discrimination_register:
        c12 += ["  No discrimination-evidence rows were produced.", ""]
    for row in minimum_evidence_for_discrimination_register:
        c12 += [
            f"  Rival Hypotheses    : {_join(row.get('rival_hypotheses', []))}",
            f"  Minimum Evidence    : {row.get('minimum_evidence', '')}",
            f"  Source              : {row.get('source', '')}",
            f"  What It Confirms    : {row.get('what_it_confirms', '')}",
            f"  What It Falsifies   : {row.get('what_it_falsifies', '')}",
            f"  Unlocks             : {row.get('unlocks', '')}",
            "",
        ]

    client_facing_actions = list((client_facing_tad or {}).get("actions", []) or [])
    tad_rows = client_facing_actions or expanded_structural_tad_action_register
    c13 = [_sep("="), "TAD — ACTION PRIORITY", _sep("="), ""]
    c13_es = [_sep("="), "TAD — PRIORIDAD DE ACCIÓN", _sep("="), ""]
    if not tad_rows:
        c13 += ["  No expanded structural TAD actions were produced.", ""]
        c13_es += ["  No se produjeron acciones TAD estructurales expandidas.", ""]
    for row in tad_rows:
        c13 += [
            f"  Action              : {row.get('action', '')}",
            f"  Status              : {row.get('status', '')}",
            f"  Why                 : {row.get('why', '')}",
            f"  Evidence State      : {row.get('evidence_state', '')}",
            f"  Financial Exposure  : {row.get('financial_exposure', '')}",
            f"  Evidence Needed     : {row.get('evidence_needed', '')}",
            f"  Maps To             : {row.get('maps_to', '')}",
            f"  Prohibited Action   : {row.get('prohibited_action', '')}",
            "",
        ]
        c13_es += [
            f"  Acción              : {row.get('action', '')}",
            f"  Estado              : {row.get('status', '')}",
            f"  Por Qué             : {row.get('why', '')}",
            f"  Estado de Evidencia : {row.get('evidence_state', '')}",
            f"  Exposición Financiera: {row.get('financial_exposure', '')}",
            f"  Evidencia Necesaria : {row.get('evidence_needed', '')}",
            f"  Mapea a             : {row.get('maps_to', '')}",
            f"  Acción Prohibida    : {row.get('prohibited_action', '')}",
            "",
        ]

    c14 = [_sep("="), "WHAT NOT TO DO YET", _sep("="), ""]
    what_not_to_do: list[str] = []
    for row in expanded_structural_tad_action_register:
        prohibited_action = str(row.get("prohibited_action", "")).strip()
        if prohibited_action and prohibited_action not in what_not_to_do:
            what_not_to_do.append(prohibited_action)
    for row in claim_contract_register:
        permission = str(row.get("permission", "")).strip().lower()
        statement = str(row.get("statement", "")).strip()
        if permission in {"prohibited", "screening_only", "hypothesis_only"} and statement:
            what_not_to_do.append(f"{statement} [{permission}]")
        for prohibited in list(row.get("prohibited_use", []) or []):
            prohibited_text = str(prohibited).strip()
            if prohibited_text:
                what_not_to_do.append(prohibited_text)
    deduped_not_to_do: list[str] = []
    for item in what_not_to_do:
        if item not in deduped_not_to_do:
            deduped_not_to_do.append(item)
    if not deduped_not_to_do:
        c14 += ["  No explicit premature-action bans were produced beyond the general claim ceiling.", ""]
    else:
        for item in deduped_not_to_do[:12]:
            c14.append(f"  - {item}")
        c14.append("")

    c15 = [_sep("="), "CLAIM PERMISSION MATRIX", _sep("="), ""]
    if not claim_contract_register:
        c15 += ["  No claim-contract rows were produced.", ""]
    for row in claim_contract_register:
        c15 += [
            f"  Claim ID            : {row.get('claim_id', '')}",
            f"  Claim Family        : {row.get('claim_family', '')}",
            f"  Statement           : {row.get('statement', '')}",
            f"  Permission          : {row.get('permission', '')}",
            f"  Evidence State      : {row.get('evidence_state', '')}",
            f"  Supporting Sources  : {_join(row.get('supporting_sources', []))}",
            f"  Assumptions         : {_join(row.get('assumptions', []))}",
            f"  Falsification       : {row.get('falsification_condition', '')}",
            f"  Minimum Evidence    : {_join(row.get('minimum_evidence_required', []))}",
            f"  Allowed Use         : {_join(row.get('allowed_use', []))}",
            f"  Prohibited Use      : {_join(row.get('prohibited_use', []))}",
            "",
        ]

    c16 = [_sep("="), "SOURCE TRACEABILITY", _sep("="), ""]
    if not source_family_coverage_table:
        c16 += ["  No public source-coverage rows were produced.", ""]
    for row in source_family_coverage_table:
        c16 += [
            f"  Source Family       : {row.get('source_family', '')}",
            f"  Source Name         : {row.get('source_name', '')}",
            f"  Queried             : {'yes' if row.get('queried') else 'no'}",
            f"  Found               : {'yes' if row.get('found') else 'no'}",
            f"  Authority           : {row.get('authority', '')}",
            f"  Scope               : {row.get('scope', '')}",
            f"  Fields Extracted    : {_join(row.get('fields_extracted', []))}",
            f"  Missing             : {_join(row.get('missing', []))}",
            f"  Support Note        : {row.get('support_note', '')}",
            "",
        ]

    c17 = [
        _sep("="),
        "SYSTEM CONSISTENCY CHECK",
        _sep("="),
        "",
        "  Final consistency status is filled at render time from motor_036.",
        "  PDF generation is blocked if any critical consistency check fails.",
        "",
        "  Expected critical checks:",
        "    - asset context vs public data",
        "    - claim permissions vs visible claims",
        "    - scenario vs evidence/falsification contract",
        "    - TAD posture vs visible action language",
        "    - structural section presence vs selected output mode",
        "    - source scope vs source support note",
        "",
    ]

    return [
        _section("c1_structural_exec", "C1", 1, "Executive Structural Brief", "executive", "body", "STRUCTURAL_LANE | DECISION_GRADE", llm_lookup.get("s01_exec_narrative", ""), "b_structural_exec_brief", c1, c1, c1_es, llm_lookup_en.get("s01_exec_narrative", ""), llm_lookup_es.get("s01_exec_narrative", "")),
        _section("c2_client_problem", "C2", 2, "What the Client Thinks the Problem Is", "executive", "body", "STRUCTURAL_LANE | STATED_PROBLEM", "", "b_structural_client_problem", c2, c2, c2_es),
        _section("c3_system_problem", "C3", 3, "What the System Thinks the Problem Might Actually Be", "executive", "body", "STRUCTURAL_LANE | REFRAMING", "", "b_structural_problem_reframe", c3, c3, c3_es),
        _section("c4_system_abstraction", "C4", 4, "System Abstraction Map", "technical", "body", "STRUCTURAL_LANE | MIXED_EVIDENCE", "", "b_structural_system_abstraction_body", c4),
        _section("c5_dominant_variables", "C5", 5, "Dominant Variables", "technical", "body", "STRUCTURAL_LANE | DOMINANT_VARIABLES", "", "b_structural_dominant_variables_body", c5),
        _section("c6_evidence_state_by_layer", "C6", 6, "Evidence State by Layer", "technical", "body", "STRUCTURAL_LANE | LAYER_EVIDENCE", "", "b_structural_evidence_state_by_layer_body", c6),
        _section("c7_cross_layer_contradictions", "C7", 7, "Cross-Layer Contradictions", "technical", "body", "STRUCTURAL_LANE | CONDITIONAL", llm_lookup.get("s06_tensions_narrative", ""), "b_structural_cross_layer_conflicts_body", c7, llm_lookup_en.get("s06_tensions_narrative", ""), llm_lookup_es.get("s06_tensions_narrative", "")),
        _section("c8_scenario_space", "C8", 8, "Scenario Space", "executive", "body", "CONDITIONAL", "", "b_structural_scenario_space", c8),
        _section("c9_financial_exposure", "C9", 9, "Financial Exposure Under Uncertainty", "technical", "body", "STRUCTURAL_LANE | CONDITIONAL", "", "b_structural_financial_exposure_body", c9),
        _section("c10_competitive_peer", "C10", 10, "Competitive / Peer Comparison", "technical", "body", "STRUCTURAL_LANE | COMPARISON", "", "b_structural_competitive_peer", c10, c10, c10_es),
        _section("c11_conditional_redesign", "C11", 11, "Conditional Redesign Pathways", "technical", "body", "STRUCTURAL_LANE | CONDITIONAL", "", "b_structural_conditional_redesign", c11, c11, c11_es),
        _section("c12_minimum_evidence", "C12", 12, "Minimum Evidence for Discrimination", "technical", "body", "STRUCTURAL_LANE | DISCRIMINATION", "", "b_structural_minimum_evidence_body", c12),
        _section("c13_tad_action_priority", "C13", 13, "TAD — Action Priority", "executive", "body", "STRUCTURAL_LANE | ACTION_PRIORITY", "", "b_structural_tad_action_priority", c13, c13, c13_es),
        _section("c14_what_not_to_do_yet", "C14", 14, "What Not To Do Yet", "executive", "body", "STRUCTURAL_LANE | CLAIM_CEILING", "", "b_structural_what_not_to_do", c14),
        _section("c15_claim_permission_matrix", "C15", 15, "Claim Permission Matrix", "technical", "body", "STRUCTURAL_LANE | CLAIM_PERMISSIONS", "", "b_structural_claim_permission_matrix", c15),
        _section("c16_source_traceability", "C16", 16, "Source Traceability", "technical", "body", "DIRECT_EVIDENCE", "", "b_structural_source_traceability", c16),
        _section("c17_system_consistency_check", "C17", 17, "System Consistency Check", "technical", "body", "GOVERNANCE", "", "b_structural_system_consistency_check", c17),
    ]


def _build_report_traceability(
    report_package_id: str,
    traceability_register: dict[str, Any],
    decision_core_lineage: dict[str, Any],
    source_lineage: dict[str, Any],
    sections: list[dict[str, Any]],
    produced_at: str,
) -> dict[str, Any]:
    block_traces = {
        entry.get("block_id", ""): entry
        for entry in traceability_register.get("block_traces", [])
        if entry.get("block_id")
    }
    section_traces: list[dict[str, Any]] = []
    for section in sections:
        section_block_ids = [
            block.get("block_id", "")
            for block in section.get("blocks", [])
            if isinstance(block, dict) and block.get("block_id")
        ]
        section_upstream_traces: list[str] = []
        for block_id in section_block_ids:
            section_upstream_traces.extend(
                block_traces.get(block_id, {}).get("upstream_traces", [])
            )
        section_traces.append(
            {
                "section_id": section.get("section_id", ""),
                "chapter_id": section.get("chapter_id", ""),
                "block_ids": section_block_ids,
                "upstream_traces": sorted(set(section_upstream_traces)),
                "epistemic_marker": section.get("epistemic_marker", ""),
            }
        )
    return {
        "report_traceability_id": f"rt:{report_package_id}",
        "produced_at": produced_at,
        "source_lineage_id": source_lineage.get("lineage_id", ""),
        "decision_core_lineage_id": decision_core_lineage.get("lineage_id", ""),
        "block_traceability_id": traceability_register.get("traceability_id", ""),
        "coverage_gap_types": source_lineage.get("coverage_gap_types", []),
        "admitted_source_types": source_lineage.get("admitted_source_types", []),
        "section_traces": section_traces,
        "trace_chain": [
            "motor_012.evidence_lineage",
            "motor_014.decision_core_lineage",
            "motor_015.traceability_register",
            "motor_016.report_package",
        ],
    }


def _build_provisional_governance_summary(
    runtime: dict[str, Any],
    source_lineage: dict[str, Any],
    decision_core_lineage: dict[str, Any],
    traceability_register: dict[str, Any],
    conflict_register: list[dict[str, Any]],
    llm_available: bool,
    chart_assets: list[dict[str, Any]],
    chart_errors: list[dict[str, Any]],
    produced_at: str,
) -> dict[str, Any]:
    runtime_truth = runtime.get("truth_summary", {}) if isinstance(runtime.get("truth_summary", {}), dict) else {}
    stubs_active = (
        runtime_truth.get("stub", 0)
        + runtime_truth.get("cached_stub", 0)
        + runtime_truth.get("completed_stub", 0)
    )
    traceability_chain_complete = bool(source_lineage and decision_core_lineage and traceability_register)
    blocking_conflicts = len(conflict_register)
    publication_ceiling = "publish_bounded"
    downgrade_triggers: list[str] = []
    if blocking_conflicts > 0:
        downgrade_triggers.append(
            f"{blocking_conflicts} blocking conflict(s) remain active; report is bounded, not decision-closing."
        )
    if stubs_active > 0:
        publication_ceiling = "publish_with_degradation"
        downgrade_triggers.append(
            f"{stubs_active} stub or cached-stub motor(s) active in upstream runtime state."
        )
    if not traceability_chain_complete:
        publication_ceiling = "hold_for_validation"
        downgrade_triggers.append(
            "Traceability chain incomplete between sources, inference objects, and report sections."
        )
    if not llm_available:
        downgrade_triggers.append(
            "LLM narrative layer unavailable; report relies on structured analytical blocks only."
        )
    if chart_errors:
        downgrade_triggers.append(
            f"{len(chart_errors)} chart generation error(s); visual layer may be incomplete."
        )
    framework_constraint = " ".join([
        "This report is a governed materialization of Decision Core outputs.",
        "It remains Decision-grade unless and until independent evidence upgrades the underlying objects.",
        f"Publication ceiling: {publication_ceiling.replace('_', ' ')}.",
        "No statement constitutes a verified diagnosis, compliance determination, or investment recommendation.",
        "All claims remain conditional on validation requirements and domain-of-validity boundaries stated in the report.",
    ] + downgrade_triggers)
    return {
        "governance_summary_id": f"gov:{produced_at[:19]}",
        "produced_at": produced_at,
        "epistemic_grade": "Decision-grade (unresolved conflicts)" if blocking_conflicts else "Decision-grade",
        "publication_ceiling": publication_ceiling,
        "traceability_chain_complete": traceability_chain_complete,
        "blocking_conflicts": blocking_conflicts,
        "stubs_active": stubs_active,
        "llm_available": llm_available,
        "chart_assets_available": len(chart_assets),
        "chart_errors_count": len(chart_errors),
        "downgrade_triggers": downgrade_triggers,
        "framework_constraint": framework_constraint,
    }


def _content_integrity_scan(
    sections: list[dict[str, Any]],
    target_definition: dict[str, Any],
    company_name: str,
    ticker: str,
) -> dict[str, Any]:
    address = str(target_definition.get("target_identifier") or target_definition.get("target_name") or "").strip()
    target_type = str(target_definition.get("target_type", "") or "").strip().lower()
    jurisdiction_items = [str(item).upper() for item in (target_definition.get("jurisdiction_scope") or [])]
    is_nyc_case = any("US-NY" in item or "NYC" in item or "NEW YORK" in item for item in jurisdiction_items)
    allowed_ticker = (ticker or "").upper().strip()
    allowed_company = (company_name or "").upper().strip()
    target_family = "building"
    if target_type == "warehouse_distribution":
        target_family = "logistics"
    elif target_type in {"industrial_plant", "manufacturing_facility", "food_processing_facility", "cold_chain_facility"}:
        target_family = "manufacturing"
    elif target_type == "infrastructure_node":
        target_family = "infrastructure"
    elif target_type in {"oil_gas_upstream_site", "oil_gas_midstream_facility", "oil_gas_downstream_facility"}:
        target_family = "oil_gas"

    issues: list[dict[str, str]] = []
    text_fragments: list[tuple[str, str]] = []
    for sec in sections:
        text_fragments.append((sec.get("section_id", ""), sec.get("title", "")))
        llm_text = " ".join(
            str(sec.get(key, "") or "")
            for key in ("llm_text", "llm_text_en", "llm_text_es")
        )
        block_text = " ".join(
            str(block.get("content", "") or "")
            for block in sec.get("blocks", [])
            if isinstance(block, dict)
        )
        text_fragments.append((sec.get("section_id", ""), f"{llm_text} {block_text}".strip()))

    watched_strings = [
        ("legacy_ll97_reference", "LL97", not is_nyc_case),
        ("legacy_local_law_97_reference", "LOCAL LAW 97", not is_nyc_case),
        ("legacy_operational_intelligence_report", "OPERATIONAL INTELLIGENCE REPORT", True),
        ("legacy_operational_decision_intelligence_report", "OPERATIONAL DECISION INTELLIGENCE REPORT", True),
        ("legacy_technical_decision_intelligence_report", "TECHNICAL DECISION INTELLIGENCE REPORT", True),
        ("legacy_empire_state_reference", "EMPIRE STATE", "EMPIRE STATE" not in address.upper()),
        ("legacy_350_fifth_reference", "350 FIFTH", "350 FIFTH" not in address.upper()),
        ("legacy_800_boylston_reference", "800 BOYLSTON", "800 BOYLSTON" not in address.upper()),
        ("legacy_pier_1_reference", "PIER 1 BAY 1", "PIER 1 BAY 1" not in address.upper()),
        ("legacy_universe_blvd_reference", "700 UNIVERSE", "700 UNIVERSE" not in address.upper()),
        ("legacy_main_avenue_reference", "901 MAIN AVENUE", "901 MAIN AVENUE" not in address.upper()),
        ("legacy_boston_properties_reference", "BOSTON PROPERTIES", bool(allowed_company and "BOSTON PROPERTIES" != allowed_company)),
        ("legacy_prologis_reference", "PROLOGIS", bool(allowed_company and "PROLOGIS" not in allowed_company)),
        ("legacy_nextera_reference", "NEXTERA", bool(allowed_company and "NEXTERA" not in allowed_company)),
        ("legacy_general_electric_reference", "GENERAL ELECTRIC", bool(allowed_company and "GENERAL ELECTRIC" not in allowed_company)),
    ]
    watched_regex_patterns = [
        ("legacy_esrt_reference", r"\bESRT\b", bool(allowed_ticker and allowed_ticker != "ESRT")),
        ("legacy_bxp_reference", r"\bBXP\b", bool(allowed_ticker and allowed_ticker != "BXP")),
        ("legacy_pld_reference", r"\bPLD\b", bool(allowed_ticker and allowed_ticker != "PLD")),
        ("legacy_nee_reference", r"\bNEE\b", bool(allowed_ticker and allowed_ticker != "NEE")),
        ("legacy_tdir_reference", r"\bTDIR\b", True),
    ]
    invalid_empty_patterns = [
        ("invalid_blank_eui", "EUI: N/A"),
        ("invalid_blank_eui_unspecified", "EUI: UNSPECIFIED"),
        ("invalid_zero_eui", "EUI: 0"),
        ("invalid_unspecified_fuel", "PRIMARY FUEL: UNSPECIFIED"),
        ("invalid_unspecified_systems", "SYSTEMS: UNSPECIFIED"),
        ("invalid_not_confirmed", ": NOT CONFIRMED"),
    ]
    invalid_empty_regex_patterns = [
        ("invalid_zero_gfa", r"(?<![\d,])0 SQFT\b"),
    ]
    instruction_leakage_patterns = [
        ("instruction_leakage_chart", "THE CHART SHOULD"),
        ("instruction_leakage_text", "USE IN TEXT"),
        ("instruction_leakage_prose", "THE PROSE SHOULD"),
        ("instruction_leakage_reader_takeaway", "READER TAKEAWAY"),
        ("instruction_leakage_technical_reference_data", "TECHNICAL REFERENCE DATA"),
        ("instruction_leakage_epistemic_marker", "EPISTEMIC MARKER"),
    ]
    instruction_leakage_regex_patterns = [
        ("instruction_leakage_chapter_marker", r"\[(C|A)\d+[A-Z]?\]"),
    ]
    family_specific_patterns: list[tuple[str, str]] = []
    if target_family in {"manufacturing", "infrastructure", "oil_gas"}:
        family_specific_patterns.extend([
            ("legacy_building_leasing_semantics", "LEASE EXTENSION"),
            ("legacy_building_reletting_semantics", "RE-LETTING"),
            ("legacy_building_subletting_semantics", "SUBLETTING"),
            ("legacy_building_anchor_tenant_semantics", "ANCHOR TENANT"),
            ("legacy_building_common_area_semantics", "COMMON-AREA LOADS"),
            ("legacy_building_rentable_area_semantics", "RENTABLE AREA"),
            ("legacy_building_tenant_driven_semantics", "TENANT-DRIVEN"),
        ])

    for section_id, text in text_fragments:
        upper = str(text or "").upper()
        for code, token, should_flag in watched_strings:
            if should_flag and token in upper:
                issues.append({
                    "issue_code": code,
                    "severity": "error",
                    "section_id": section_id,
                    "matched_text": token,
                    "message": f"Unexpected legacy context token detected: {token}",
                })
        for code, pattern, should_flag in watched_regex_patterns:
            if should_flag and re.search(pattern, upper):
                issues.append({
                    "issue_code": code,
                    "severity": "error",
                    "section_id": section_id,
                    "matched_text": pattern,
                    "message": f"Unexpected legacy context token detected: {pattern}",
                })
        for code, pattern in invalid_empty_regex_patterns:
            if re.search(pattern, upper):
                issues.append({
                    "issue_code": code,
                    "severity": "error",
                    "section_id": section_id,
                    "matched_text": pattern,
                    "message": f"Invalid empty-field presentation detected: {pattern}",
                })
        for code, token in invalid_empty_patterns:
            if token in upper:
                issues.append({
                    "issue_code": code,
                    "severity": "error",
                    "section_id": section_id,
                    "matched_text": token,
                    "message": f"Invalid empty-field presentation detected: {token}",
                })
        for code, token in instruction_leakage_patterns:
            if token in upper:
                issues.append({
                    "issue_code": code,
                    "severity": "error",
                    "section_id": section_id,
                    "matched_text": token,
                    "message": f"Internal prompt instruction leaked into visible report: {token}",
                })
        for code, pattern in instruction_leakage_regex_patterns:
            if re.search(pattern, upper):
                issues.append({
                    "issue_code": code,
                    "severity": "error",
                    "section_id": section_id,
                    "matched_text": pattern,
                    "message": f"Internal report scaffolding leaked into visible report: {pattern}",
                })
        for code, token in family_specific_patterns:
            if token in upper:
                issues.append({
                    "issue_code": code,
                    "severity": "error",
                    "section_id": section_id,
                    "matched_text": token,
                    "message": f"Unexpected building/company-first token detected for {target_family} target: {token}",
                })

    return {
        "scan_status": "blocked" if issues else "passed",
        "issue_count": len(issues),
        "issues": issues,
        "render_eligible": not issues,
    }


def _is_blocked_report_class(report_identity_state: str) -> bool:
    return report_identity_state in {
        "Issuer Context Memo",
        "Address Candidate Brief",
        "Site Candidate Brief",
        "Asset Context Seed Brief",
        "Asset Context Insufficiency Brief",
        "Decision-Blocked Asset Brief",
        "Pre-Verification Asset Brief",
    }


def _visible_document_label(
    report_identity_state: str,
    recommended_report_type: str = "",
) -> str:
    recommended_label = canonicalize_output_mode(recommended_report_type)
    report_identity_label = canonicalize_output_mode(report_identity_state)
    if recommended_label in {
        "Target Classification Brief",
        "Decision-Blocked Asset Brief",
        "Exploratory Prior Brief",
        "Compliance / Investment Screening Brief",
        "Structural Contradiction Brief",
        "System Redesign Hypothesis Brief",
        "Competitive Positioning Brief",
        "TAD Action Priority Brief",
        "Full Technical Decision Intelligence Report",
    }:
        return recommended_label
    if report_identity_label in {
        "Target Classification Brief",
        "Decision-Blocked Asset Brief",
        "Exploratory Prior Brief",
        "Compliance / Investment Screening Brief",
        "Structural Contradiction Brief",
        "System Redesign Hypothesis Brief",
        "Competitive Positioning Brief",
        "TAD Action Priority Brief",
        "Full Technical Decision Intelligence Report",
    }:
        return report_identity_label
    if _is_blocked_report_class(report_identity_state):
        return "Decision-Blocked Asset Brief"
    return "Asset Decision-Admissibility Brief"


def _localized_document_label(
    report_identity_state: str,
    language: str = "en",
    recommended_report_type: str = "",
) -> str:
    if language != "es":
        return _visible_document_label(report_identity_state, recommended_report_type)
    recommended_label = canonicalize_output_mode(recommended_report_type)
    if recommended_label == "Target Classification Brief":
        return "Informe de Clasificación del Objetivo"
    if recommended_label == "Decision-Blocked Asset Brief":
        return "Informe de Activo con Decisión Bloqueada"
    if recommended_label == "Exploratory Prior Brief":
        return "Informe Exploratorio de Prior"
    if recommended_label == "Compliance / Investment Screening Brief":
        return "Informe de Screening de Cumplimiento / Inversión"
    if recommended_label == "Structural Contradiction Brief":
        return "Informe de Contradicción Estructural"
    if recommended_label == "System Redesign Hypothesis Brief":
        return "Informe de Hipótesis de Rediseño del Sistema"
    if recommended_label == "Competitive Positioning Brief":
        return "Informe de Posicionamiento Competitivo"
    if recommended_label == "TAD Action Priority Brief":
        return "Informe TAD de Prioridad de Acción"
    if recommended_label == "Full Technical Decision Intelligence Report":
        return "Informe Técnico Completo de Inteligencia de Decisión"
    report_identity_label = canonicalize_output_mode(report_identity_state)
    if report_identity_label == "Decision-Blocked Asset Brief":
        return "Informe de Activo con Decisión Bloqueada"
    if report_identity_label == "Exploratory Prior Brief":
        return "Informe Exploratorio de Prior"
    if report_identity_label == "Compliance / Investment Screening Brief":
        return "Informe de Screening de Cumplimiento / Inversión"
    if report_identity_label == "Structural Contradiction Brief":
        return "Informe de Contradicción Estructural"
    if report_identity_label == "System Redesign Hypothesis Brief":
        return "Informe de Hipótesis de Rediseño del Sistema"
    if report_identity_label == "Competitive Positioning Brief":
        return "Informe de Posicionamiento Competitivo"
    if report_identity_label == "TAD Action Priority Brief":
        return "Informe TAD de Prioridad de Acción"
    if report_identity_label == "Full Technical Decision Intelligence Report":
        return "Informe Técnico Completo de Inteligencia de Decisión"
    if _is_blocked_report_class(report_identity_state):
        return "Informe de Activo con Decisión Bloqueada"
    return "Informe de Admisibilidad de Decisión del Activo"


def _refine_runtime_report_identity(
    target_admissibility_state: str,
    report_identity_state: str,
    recommended_report_type: str,
    report_readiness_register: dict[str, Any],
) -> tuple[str, str]:
    if target_admissibility_state not in {"bounded_asset", "bounded_asset_with_operable_context"}:
        return report_identity_state, recommended_report_type
    readiness_allowed = [
        str(item).strip()
        for item in list(report_readiness_register.get("report_type_allowed", []) or [])
        if str(item).strip()
    ]
    refined = next(
        (
            item for item in readiness_allowed
            if item in {
                "Decision-Blocked Asset Brief",
                "Exploratory Prior Brief",
                "Compliance / Investment Screening Brief",
                "Full Technical Decision Intelligence Report",
            }
        ),
        "",
    )
    if not refined:
        return report_identity_state, recommended_report_type
    return refined, refined


def _cluster_label(cluster_id: str, language: str = "en") -> str:
    cluster = str(cluster_id or "").strip()
    labels_en = {
        "identity_cluster": "identity",
        "location_cluster": "location",
        "jurisdiction_cluster": "jurisdiction",
        "geometry_size_cluster": "geometry and size",
        "vintage_structure_cluster": "vintage and structure",
        "use_program_cluster": "use and program",
        "operating_regime_cluster": "operating regime",
        "fuel_energy_cluster": "fuel and energy",
        "systems_cluster": "systems",
        "tenant_control_cluster": "occupant control boundary",
        "regulatory_cluster": "regulatory applicability",
        "financial_boundary_cluster": "financial boundary",
        "benchmark_mapping_cluster": "benchmark mapping",
    }
    labels_es = {
        "identity_cluster": "identidad",
        "location_cluster": "ubicación",
        "jurisdiction_cluster": "jurisdicción",
        "geometry_size_cluster": "geometría y tamaño",
        "vintage_structure_cluster": "antigüedad y estructura",
        "use_program_cluster": "uso y programa",
        "operating_regime_cluster": "régimen operativo",
        "fuel_energy_cluster": "energía y combustibles",
        "systems_cluster": "sistemas",
        "tenant_control_cluster": "límite de control de ocupantes",
        "regulatory_cluster": "regulación aplicable",
        "financial_boundary_cluster": "límite financiero",
        "benchmark_mapping_cluster": "benchmark aplicable",
    }
    if language == "es":
        return labels_es.get(cluster, cluster.replace("_", " "))
    return labels_en.get(cluster, cluster.replace("_", " "))


def _decision_state_text(
    target_label: str,
    target_admissibility_state: str,
    asset_context_readiness: str,
    missing_clusters: list[str],
    recommended_report_type: str = "",
    language: str = "en",
) -> str:
    cluster_text = ", ".join(_cluster_label(cluster, language) for cluster in missing_clusters[:5]) or (
        "critical physical observable clusters" if language != "es" else "clusters físicos críticos"
    )
    if target_admissibility_state == "issuer_context_only":
        return (
            f"ESTADO EPISTÉMICO: OBJETIVO FÍSICO NO ACOTADO — {target_label} todavía no es un activo físico admisible. Existe contexto del emisor, pero no soporta una lectura técnica, energética, regulatoria o de capital del activo."
            if language == "es"
            else f"EPISTEMIC STATE: PHYSICAL TARGET NOT YET BOUNDED — {target_label} is not yet an admissible physical asset. Issuer context exists, but it does not support a technical, energy, regulatory, or capital reading of the asset."
        )
    if target_admissibility_state == "address_candidate_only":
        return (
            f"ESTADO EPISTÉMICO: SUSTRATO TÉCNICO DEL ACTIVO INSUFICIENTE — {target_label} todavía no puede tratarse como un caso técnico normal del activo porque siguen faltando clusters observables clave ({cluster_text}). El contexto del emisor o financiero puede servir como contexto, pero no compensa el sustrato faltante del activo."
            if language == "es"
            else f"EPISTEMIC STATE: ASSET TECHNICAL INSUFFICIENCY — {target_label} cannot yet be treated as a normal technical asset case because core observable clusters remain missing ({cluster_text}). Issuer or finance context may still be useful, but it cannot compensate for the missing asset substrate."
        )
    if target_admissibility_state == "site_candidate_only":
        return (
            f"ESTADO EPISTÉMICO: IDENTIDAD DEL ACTIVO TODAVÍA NO ACOTADA — {target_label} solo está resuelto como candidato de sitio. Faltan clusters clave ({cluster_text}) y el límite operativo del activo sigue siendo insuficiente para una decisión más fuerte."
            if language == "es"
            else f"EPISTEMIC STATE: ASSET IDENTITY NOT YET BOUNDED — {target_label} resolves only as a site candidate. Key clusters remain missing ({cluster_text}), and the operating boundary is still insufficient for stronger action."
        )
    if recommended_report_type == "Compliance / Investment Screening Brief":
        return (
            f"ESTADO EPISTÉMICO: SCREENING ADMISIBLE — {target_label} tiene sustrato público suficiente para screening, pero siguen faltando clusters de grado de verificación ({cluster_text}) antes de avanzar a ROI, retrofit o cierre de cumplimiento."
            if language == "es"
            else f"EPISTEMIC STATE: SCREENING ADMISSIBLE — {target_label} has sufficient public substrate for screening, but verification-grade clusters remain unresolved ({cluster_text}) before ROI, retrofit, or compliance-closure claims can advance."
        )
    if asset_context_readiness in {"asset_context_insufficient", "asset_context_minimal", "location_only"}:
        return (
            f"ESTADO EPISTÉMICO: CONTEXTO DEL ACTIVO INSUFICIENTE — {target_label} sigue bloqueado hasta aclarar al menos estos clusters: {cluster_text}."
            if language == "es"
            else f"EPISTEMIC STATE: ASSET CONTEXT INSUFFICIENT — {target_label} remains blocked until at least these clusters are clarified: {cluster_text}."
        )
    return (
        f"ESTADO EPISTÉMICO: LECTURA ACOTADA DEL ACTIVO — {target_label} puede leerse solo dentro de los límites actuales de evidencia y validación."
        if language == "es"
        else f"EPISTEMIC STATE: BOUNDED ASSET READING — {target_label} can only be read within the current evidence and validation limits."
    )


def _visible_case_subtitle(
    report_identity_state: str,
    target_admissibility_state: str,
    asset_context_readiness: str,
    language: str = "en",
) -> str:
    if report_identity_state == "Structural Contradiction Brief":
        return (
            "Contradicciones estructurales entre capas que pueden invalidar la pregunta original"
            if language == "es"
            else "Cross-layer structural contradictions that may invalidate the original question"
        )
    if report_identity_state == "System Redesign Hypothesis Brief":
        return (
            "Hipótesis de rediseño condicionadas por evidencia; no recomendación final"
            if language == "es"
            else "Evidence-bounded redesign hypotheses; not a final recommendation"
        )
    if report_identity_state == "Competitive Positioning Brief":
        return (
            "Comparación estructural y de peers bajo evidencia acotada"
            if language == "es"
            else "Structural peer and competitive comparison under bounded evidence"
        )
    if report_identity_state == "TAD Action Priority Brief":
        return (
            "Prioridad de acción bajo incertidumbre estructural y evidencia acotada"
            if language == "es"
            else "Action priority under structural uncertainty and bounded evidence"
        )
    if _is_blocked_report_class(report_identity_state):
        if target_admissibility_state == "address_candidate_only":
            return (
                "Evidencia mínima requerida antes de decisiones técnicas o de capital"
                if language == "es"
                else "Minimum Evidence Required Before Technical or Capital Decisions"
            )
        if target_admissibility_state == "site_candidate_only":
            return (
                "Evidencia mínima requerida antes de decisiones a nivel de activo"
                if language == "es"
                else "Minimum Evidence Required Before Asset-Level Decisions"
            )
        return (
            "Decisión bloqueada hasta aclarar sujeto, evidencia mínima y contexto acotado del activo"
            if language == "es"
            else "Decision blocked pending minimum evidence, subject clarification, and bounded asset context"
        )
    if asset_context_readiness in {"asset_context_operable", "asset_context_hardened"}:
        return (
            "Reporte de admisibilidad de decisión / evidencia mínima para incertidumbre de inversión en activos"
            if language == "es"
            else "Decision-Admissibility / Minimum Evidence Report for Asset Investment Uncertainty"
        )
    return (
        "Reporte de admisibilidad de decisión / evidencia mínima bajo incertidumbre acotada del activo"
        if language == "es"
        else "Decision-Admissibility / Minimum Evidence Report under bounded asset uncertainty"
    )


def _main_warning_text(
    target_admissibility_state: str,
    asset_context_readiness: str,
    missing_clusters: list[str],
    language: str = "en",
) -> str:
    if target_admissibility_state == "issuer_context_only":
        return (
            "Existe contexto del emisor, pero el objetivo físico todavía no está acotado como activo admisible."
            if language == "es"
            else "Issuer context is present, but the physical target is not yet bounded as an admissible asset."
        )
    if target_admissibility_state == "address_candidate_only":
        return (
            "El sujeto actual sigue siendo solo un candidato por dirección. El contexto público a nivel de dirección no soporta una decisión técnica o de capital defendible."
            if language == "es"
            else "The current subject is still an address candidate. Address-level public context cannot support a defendable technical or capital decision."
        )
    if target_admissibility_state == "site_candidate_only":
        return (
            "El sujeto actual sigue siendo solo un candidato de sitio. La identidad del activo y su límite operativo siguen siendo insuficientes para una acción más fuerte."
            if language == "es"
            else "The current subject is only a site candidate. Asset identity and operating boundary remain insufficient for stronger action."
        )
    if asset_context_readiness in {"location_only", "asset_context_insufficient"}:
        cluster_text = ", ".join(missing_clusters[:4]) if missing_clusters else "critical physical observable clusters"
        return (
            (
                "Falta contexto crítico del activo. "
                f"El caso queda bloqueado hasta aclarar al menos estos clusters: {cluster_text}."
            )
            if language == "es"
            else (
                "Critical asset context remains missing. "
                f"The case is blocked until at least these clusters are clarified: {cluster_text}."
            )
        )
    return (
        "Este brief sigue acotado por el estado actual de la evidencia y no debe leerse como verificación-grade."
        if language == "es"
        else "This brief remains bounded by the current evidence state and should not be read as verification-grade."
    )


def _build_decision_admissibility_sections(  # noqa: PLR0913
    output_blocks: list[dict[str, Any]],
    governance_summary: dict[str, Any],
    llm_lookup: dict[str, str],
    llm_lookup_en: dict[str, str],
    llm_lookup_es: dict[str, str],
    conflict_register: list[dict[str, Any]],
    validation_queue: list[dict[str, Any]],
    tad_prelim: dict[str, Any],
    financial_exposure_case: dict[str, Any],
    compliance_applicability_case: dict[str, Any],
    document_label: str,
    main_warning: str,
    allowed_use: list[str],
    prohibited_use: list[str],
    structural_executive_summary: dict[str, Any] | None = None,
) -> list[dict[str, Any]]:
    decision_block = _find_block(output_blocks, "decision_admissibility_block")
    readiness_block = _find_block(output_blocks, "asset_context_readiness_block")
    uncertainty_block = _find_block(output_blocks, "investment_uncertainty_map_block")
    evidence_block = _find_block(output_blocks, "minimum_evidence_pack_block")
    scenario_block = _find_block(output_blocks, "scenario_space_block")
    financial_exposure_block = _find_block(output_blocks, "financial_exposure_block")
    decision_fronts_block = _find_block(output_blocks, "decision_fronts_block")
    inference_case_block = _find_block(output_blocks, "inference_case_register_block")
    next_questions_block = _find_block(output_blocks, "next_best_questions_block")
    rule_family_records = compliance_applicability_case.get("rule_family_record", [])
    primary_rule_name = ""
    if isinstance(rule_family_records, list) and rule_family_records:
        primary_rule_name = rule_family_records[0].get("rule_family_name", "")
    elif isinstance(rule_family_records, dict):
        primary_rule_name = rule_family_records.get("rule_family_name", "")

    c1 = [
        _sep("="),
        document_label.upper(),
        _sep("="),
        "",
        f"  Decision State        : {decision_block.get('decision_state', '')}",
        f"  Primary Block Reason  : {decision_block.get('primary_block_reason', '')}",
        f"  Decision Evaluated    : {decision_block.get('decision_evaluated', '')}",
        f"  Recommended Action    : {decision_block.get('recommended_action', '')}",
        f"  Epistemic Grade       : {governance_summary.get('epistemic_grade', 'Decision-grade')}",
        f"  Publication Ceiling   : {governance_summary.get('publication_ceiling', 'publish_bounded').replace('_', ' ')}",
        f"  Main Warning          : {main_warning}",
        "",
        "  This brief does not conclude that the asset is good or bad.",
        "  It concludes whether the current evidence is sufficient for a defendable decision.",
        "  If not, it identifies the minimum evidence required before capital-facing logic can be trusted.",
        "",
        f"  Use                   : {'; '.join(allowed_use)}",
        f"  Not Use               : {'; '.join(prohibited_use)}",
        "",
    ]
    structural_executive_summary = dict(structural_executive_summary or {})
    structural_modes = list(structural_executive_summary.get("structural_mode_candidates", []) or [])
    promotable_structural_modes = list(structural_executive_summary.get("promotable_primary_structural_modes", []) or [])
    if any(
        [
            structural_modes,
            promotable_structural_modes,
            structural_executive_summary.get("primary_reframed_problem"),
            structural_executive_summary.get("dominant_structural_conflict"),
            structural_executive_summary.get("primary_structural_action"),
        ]
    ):
        c1 += [
            _sep("="),
            "STRUCTURAL READ",
            _sep("="),
            "",
            f"  Reasoning Path    : {structural_executive_summary.get('default_reasoning_path', 'legacy_decision_gating_only')}",
            f"  Problem Frame     : {'ACTIVE' if structural_executive_summary.get('problem_frame_active', False) else 'INACTIVE'}",
            f"  Mode Candidates   : {', '.join(structural_modes) or 'NONE'}",
            f"  Primary-Eligible  : {', '.join(promotable_structural_modes) or 'NONE'}",
            f"  Reframed Problem  : {structural_executive_summary.get('primary_reframed_problem', '')}",
            f"  Dominant Conflict : {structural_executive_summary.get('dominant_structural_conflict', '')}",
            f"  Structural Action : {structural_executive_summary.get('primary_structural_action', '')} [{structural_executive_summary.get('primary_structural_action_status', '')}]",
            f"  Constraint        : {structural_executive_summary.get('bounded_note', '')}",
            "",
        ]

    c2 = [
        _sep("="),
        "ASSET CONTEXT READINESS",
        _sep("="),
        "",
        f"  Current State: {readiness_block.get('asset_context_readiness', 'unknown')}",
        "",
    ]
    for row in readiness_block.get("rows", []):
        c2 += [
            f"  [{row.get('status','')}]  {row.get('cluster','')}",
            f"    Current Evidence : {row.get('current_evidence','')}",
            f"    Consequence      : {row.get('consequence','')}",
            "",
        ]

    c3 = [
        _sep("="),
        "BLOCKING CONFLICTS",
        _sep("="),
        "",
    ]
    if not conflict_register:
        c3.append("  No blocking conflicts registered.")
    for conflict in conflict_register:
        c3 += [
            f"  [{conflict.get('conflict_id','')}]  {conflict.get('conflict_name','')}",
            f"    Why it blocks    : {conflict.get('blocking_status','')}",
            f"    Evidence needed  : {conflict.get('validation_requirement','')}",
            "    No-go implication: no stronger claim or action is admissible until this is resolved.",
            "",
        ]

    c4 = [
        _sep("="),
        "INVESTMENT UNCERTAINTY MAP",
        _sep("="),
        "",
    ]
    for row in uncertainty_block.get("rows", []):
        c4 += [
            f"  Uncertainty       : {row.get('uncertainty','')}",
            f"  Why it matters    : {row.get('why_it_matters_financially','')}",
            f"  Decision blocked  : {row.get('decision_it_blocks','')}",
            f"  Evidence needed   : {row.get('evidence_needed','')}",
            f"  Priority          : {row.get('priority','')}",
            "",
        ]

    c5 = [
        _sep("="),
        "REGULATORY / NORMATIVE SCREENING",
        _sep("="),
        "",
        f"  Rule Family              : {primary_rule_name}",
        f"  Trigger Status           : {compliance_applicability_case.get('applicability_state', '')}",
        f"  Current Posture          : {compliance_applicability_case.get('compliance_posture_state', '')}",
        f"  Determination Status     : {compliance_applicability_case.get('determination_status', '')}",
        "",
        "  This remains bounded screening only. It is not compliance closure.",
        "",
    ]

    c6 = [
        _sep("="),
        "SCENARIO SPACE UNDER CURRENT UNCERTAINTY",
        _sep("="),
        "",
    ]
    for row in scenario_block.get("rows", []):
        c6 += [
            f"  {row.get('scenario','')}",
            f"    Plausibility   : {row.get('plausibility_status','')}",
            f"    Financial Mean.: {row.get('financial_meaning','')}",
            f"    Makes it true  : {row.get('what_would_make_it_true','')}",
            f"    Falsifies it   : {row.get('what_would_falsify_it','')}",
            f"    Decision front : {row.get('linked_decision_front','')}",
            f"    Evidence link  : {row.get('linked_evidence_item','')}",
            f"    Evidence needed: {row.get('evidence_needed','')}",
            "",
        ]

    c7 = [
        _sep("="),
        "MINIMUM EVIDENCE PACK",
        _sep("="),
        "",
    ]
    for row in evidence_block.get("rows", []):
        c7 += [
            f"  Evidence Item    : {row.get('evidence_item','')}",
            f"  Source           : {row.get('source','')}",
            f"  Why needed       : {row.get('why_needed','')}",
            f"  Cases resolved   : {', '.join(row.get('cases_resolved', []))}",
            f"  Priority         : {row.get('priority', row.get('effort',''))}",
            f"  Effort           : {row.get('effort','')}",
            f"  Decision unlock  : {row.get('decision_unlock','')}",
            "",
        ]
    if validation_queue:
        c7 += [
            _sep("-"),
            "VALIDATION PRIORITY RANKING",
            _sep("-"),
            "",
        ]
        for item in validation_queue[:5]:
            c7 += [
                f"  P{item.get('queue_position','?')}  {item.get('case_name','')}",
                f"    Validation requirement: {item.get('validation_requirement','')}",
                f"    Decision relevance    : {item.get('decision_relevance_score',0):.2f}",
                f"    Validation urgency    : {item.get('validation_urgency_score',0):.2f}",
                "",
            ]

    c8 = [
        _sep("="),
        "TAD — DECISION-ADMISSIBILITY LAYER",
        _sep("="),
        "",
    ]
    for row in decision_fronts_block.get("rows", []):
        c8 += [
            f"  Decision Front   : {row.get('decision_front','')}",
            f"  Current Status   : {row.get('current_status','')}",
            f"  Why              : {row.get('why','')}",
            f"  Required Evidence: {row.get('required_evidence','')}",
            f"  Admissible Action: {row.get('admissible_action','')}",
            "",
        ]

    c9 = [
        _sep("="),
        "INFERENCE CASE REGISTER",
        _sep("="),
        "",
    ]
    for row in inference_case_block.get("rows", []):
        c9 += [
            f"  Case            : {row.get('case_id','')} — {row.get('case_name','')}",
            f"  Type            : {str(row.get('case_type','')).replace('_',' ').title()}",
            f"  P/R/V           : {row.get('prv','')}",
            f"  Evidence State  : {row.get('evidence_state','')}",
            f"  Decision Weight : {row.get('decision_relevance','')}",
            f"  Validation Req. : {row.get('validation_required','')}",
            "",
        ]

    c10 = [
        _sep("="),
        "NEXT BEST QUESTIONS",
        _sep("="),
        "",
    ]
    for row in next_questions_block.get("rows", []):
        c10 += [
            f"  [{row.get('question_id','')}] {row.get('question','')}",
            f"    Urgency       : {row.get('urgency','')}",
            f"    Linked Case   : {row.get('linked_case','')}",
            f"    Why it matters: {row.get('why_it_matters','')}",
            f"    How to answer : {row.get('how_to_answer','')}",
            "",
        ]

    c11 = [
        _sep("="),
        "FINANCIAL EXPOSURE UNDER UNCERTAINTY",
        _sep("="),
        "",
        f"  Finance Readiness State : {financial_exposure_case.get('finance_readiness_state','')}",
        f"  Scope Boundary          : {financial_exposure_case.get('scope_boundary','')}",
        f"  Baseline Dependency     : {financial_exposure_case.get('baseline_dependency_state','')}",
        f"  Tariff Basis State      : {financial_exposure_case.get('tariff_basis_state','')}",
        f"  Cost Basis State        : {financial_exposure_case.get('cost_basis_state','')}",
        f"  Bankability Posture     : {financial_exposure_case.get('bankability_posture','')}",
        "",
        "  This section maps exposure and readiness only.",
        "  It does not authorize ROI, payback, IRR, NPV, or bankability claims.",
        "",
    ]
    for row in financial_exposure_block.get("rows", []):
        c11 += [
            f"  Assumption       : {row.get('assumption','')}",
            f"  Current Support  : {row.get('current_support','')}",
            f"  Downside If Wrong: {row.get('downside_if_wrong','')}",
            f"  Evidence Needed  : {row.get('evidence_needed','')}",
            f"  Consequence      : {row.get('financial_consequence','')}",
            f"  Decision Front   : {row.get('linked_decision_front','')}",
            "",
        ]

    return [
        _section(
            sid="c1_framework_brief",
            chapter_id="C1",
            chapter_number=1,
            title="Executive Decision-Admissibility Brief",
            audience="executive",
            section_type="body",
            epistemic_marker="DECISION_GRADE",
            llm_text=llm_lookup.get("s01_exec_narrative", ""),
            llm_text_en=llm_lookup_en.get("s01_exec_narrative", ""),
            llm_text_es=llm_lookup_es.get("s01_exec_narrative", ""),
            block_id="BLK-DA-001",
            content=c1,
        ),
        _section(
            sid="c2_operational_identity",
            chapter_id="C2",
            chapter_number=2,
            title="Asset Context Readiness",
            audience="technical",
            section_type="body",
            epistemic_marker="DIRECT_EVIDENCE | BLOCKING_FIELDS",
            llm_text="",
            block_id="BLK-AR-001",
            content=c2,
        ),
        _section(
            sid="c4_inference_case_map",
            chapter_id="C3",
            chapter_number=3,
            title="Investment Uncertainty Map",
            audience="executive",
            section_type="body",
            epistemic_marker="REQUIRES_VALIDATION",
            llm_text="",
            block_id="BLK-IU-001",
            content=c4,
        ),
        _section(
            sid="c3_blocking_conflicts",
            chapter_id="C4",
            chapter_number=4,
            title="Blocking Conflicts",
            audience="technical",
            section_type="body",
            epistemic_marker="BLOCKING_CONFLICT",
            llm_text=llm_lookup.get("s02_blocking_conflict", ""),
            llm_text_en=llm_lookup_en.get("s02_blocking_conflict", ""),
            llm_text_es=llm_lookup_es.get("s02_blocking_conflict", ""),
            block_id="BLK-CF-001",
            content=c3,
        ),
        _section(
            sid="c7_validation_architecture",
            chapter_id="C5",
            chapter_number=5,
            title="Minimum Evidence Pack",
            audience="technical",
            section_type="body",
            epistemic_marker="REQUIRES_VALIDATION",
            llm_text=llm_lookup.get("s04_validation_narrative", ""),
            llm_text_en=llm_lookup_en.get("s04_validation_narrative", ""),
            llm_text_es=llm_lookup_es.get("s04_validation_narrative", ""),
            block_id="BLK-ME-001",
            content=c7,
        ),
        _section(
            sid="c6_tension_map",
            chapter_id="C6",
            chapter_number=6,
            title="Scenario Space Under Current Uncertainty",
            audience="executive",
            section_type="body",
            epistemic_marker="CONDITIONAL",
            llm_text=llm_lookup.get("s06_tensions_narrative", ""),
            llm_text_en=llm_lookup_en.get("s06_tensions_narrative", ""),
            llm_text_es=llm_lookup_es.get("s06_tensions_narrative", ""),
            block_id="BLK-SS-001",
            content=c6,
        ),
        _section(
            sid="c8_conditional_opportunities",
            chapter_id="C7",
            chapter_number=7,
            title="TAD — Decision-Admissibility Layer",
            audience="executive",
            section_type="body",
            epistemic_marker="DECISION_GRADE",
            llm_text=llm_lookup.get("s08_opportunities_narrative", ""),
            llm_text_en=llm_lookup_en.get("s08_opportunities_narrative", ""),
            llm_text_es=llm_lookup_es.get("s08_opportunities_narrative", ""),
            block_id="BLK-DF-001",
            content=c8,
        ),
        _section(
            sid="c5_energy_normative",
            chapter_id="C8",
            chapter_number=8,
            title="Regulatory / Normative Screening",
            audience="technical",
            section_type="body",
            epistemic_marker="SCREENING_GRADE",
            llm_text=llm_lookup.get("s09_systems_energy_narrative", ""),
            llm_text_en=llm_lookup_en.get("s09_systems_energy_narrative", ""),
            llm_text_es=llm_lookup_es.get("s09_systems_energy_narrative", ""),
            block_id="BLK-AR-001",
            content=c5,
        ),
        _section(
            sid="c9_inference_register",
            chapter_id="C9",
            chapter_number=9,
            title="Inference Case Register",
            audience="technical",
            section_type="body",
            epistemic_marker="INFERRED",
            llm_text="",
            block_id="BLK-IC-001",
            content=c9,
        ),
        _section(
            sid="c10_next_best_questions",
            chapter_id="C10",
            chapter_number=10,
            title="Next Best Questions",
            audience="executive",
            section_type="body",
            epistemic_marker="REQUIRES_VALIDATION",
            llm_text="",
            block_id="BLK-NQ-001",
            content=c10,
        ),
        _section(
            sid="c9_financial_context",
            chapter_id="A4",
            chapter_number=4,
            title="Financial Exposure Under Uncertainty",
            audience="technical",
            section_type="appendix",
            epistemic_marker="DIRECT_EVIDENCE | CONSOLIDATED_ONLY",
            llm_text=llm_lookup.get("s03_financial_narrative", ""),
            llm_text_en=llm_lookup_en.get("s03_financial_narrative", ""),
            llm_text_es=llm_lookup_es.get("s03_financial_narrative", ""),
            block_id="BLK-IU-001",
            content=c11,
        ),
    ]


def _build_report_section_packet(
    section: dict[str, Any],
    governance_summary: dict[str, Any],
    report_traceability: dict[str, Any],
) -> dict[str, Any]:
    trace_lookup = {
        entry.get("section_id", ""): entry
        for entry in report_traceability.get("section_traces", [])
        if entry.get("section_id")
    }
    llm_packet = section.get("llm_section_packet", {}) if isinstance(section.get("llm_section_packet", {}), dict) else {}
    chart_assets = section.get("chart_assets", []) if isinstance(section.get("chart_assets", []), list) else []
    return {
        "packet_id": f"rpk:{section.get('section_id', '')}",
        "section_id": section.get("section_id", ""),
        "chapter_id": section.get("chapter_id", ""),
        "title": section.get("title", ""),
        "section_type": section.get("section_type", ""),
        "epistemic_marker": section.get("epistemic_marker", ""),
        "publication_ceiling": governance_summary.get("publication_ceiling", "publish_bounded"),
        "narrative_mode": section.get("llm_render_mode", "structured_only"),
        "narrative_lint_status": section.get("llm_lint_status", "not_applicable"),
        "chart_required": bool(chart_assets),
        "chart_assets": [
            {
                "asset_id": asset.get("asset_id", ""),
                "title": asset.get("title", ""),
                "reader_takeaway": asset.get("reader_takeaway", ""),
                "chart_role": asset.get("chart_role", ""),
            }
            for asset in chart_assets
        ],
        "llm_section_packet": llm_packet,
        "traceability": trace_lookup.get(section.get("section_id", ""), {}),
        "block_excerpt": [
            {
                "block_id": block.get("block_id", ""),
                "content_excerpt": block.get("content", "")[:400],
            }
            for block in section.get("blocks", [])
            if isinstance(block, dict)
        ],
    }


def _parse_money_signal(text: str | int | float | None) -> float | None:
    if isinstance(text, (int, float)):
        return float(text)
    if not text:
        return None
    s = str(text)
    money_match = re.search(r"\$([\d,]+(?:\.\d+)?)\s*(million|billion|m|b)?", s, re.IGNORECASE)
    if not money_match:
        money_match = re.search(r"\b([\d,]+(?:\.\d+)?)\s*(million|billion)\b", s, re.IGNORECASE)
    if not money_match:
        return None
    value = float(money_match.group(1).replace(",", ""))
    suffix = (money_match.group(2) or "").lower()
    if suffix in {"billion", "b"}:
        value *= 1_000_000_000
    elif suffix in {"million", "m"}:
        value *= 1_000_000
    return value


def _extract_public_debt_signal(ext_sources: dict[str, Any], reported_debt: float | None) -> tuple[float | None, str]:
    ws_debt = ext_sources.get("ws_debt_leverage", {}) if isinstance(ext_sources.get("ws_debt_leverage", {}), dict) else {}
    candidates: list[float] = []
    for raw in ws_debt.get("numeric_extracts", []) or []:
        parsed = _parse_money_signal(raw)
        if parsed:
            candidates.append(parsed)
    for result in ws_debt.get("results", []) or []:
        parsed = _parse_money_signal(result.get("snippet", ""))
        if parsed:
            candidates.append(parsed)
    unique_candidates: list[float] = []
    for value in candidates:
        if value not in unique_candidates:
            unique_candidates.append(value)
    for value in unique_candidates:
        if not reported_debt:
            return value, "public leverage signal"
        if abs(value - reported_debt) / max(reported_debt, 1.0) >= 0.10:
            return value, "public leverage signal"
    return None, ""


def _build_financial_exposure_case(
    financials: dict[str, Any],
    enriched: dict[str, Any],
    source_lineage: dict[str, Any],
    conflict_register: list[dict[str, Any]],
    quality_gate: bool,
    produced_at: str,
) -> dict[str, Any]:
    ext_sources = enriched.get("extended_sources", {}) if isinstance(enriched.get("extended_sources", {}), dict) else {}
    ws_capex = ext_sources.get("ws_capex_sustainability", {}) if isinstance(ext_sources.get("ws_capex_sustainability", {}), dict) else {}
    reported_debt = financials.get("total_debt")
    public_debt_signal, public_debt_label = _extract_public_debt_signal(ext_sources, reported_debt)
    debt_conflict_active = any(
        "debt" in " ".join([
            str(conflict.get("conflict_name", "")),
            str(conflict.get("conflict_statement", "")),
            str(conflict.get("blocking_status", "")),
        ]).lower()
        for conflict in conflict_register
    )
    financial_lineage = source_lineage.get("financial_lineage", {}) if isinstance(source_lineage.get("financial_lineage", {}), dict) else {}
    financials_present = bool(financial_lineage.get("financials_present")) and bool(financials)
    if not financials_present or not quality_gate:
        finance_readiness_state = "screening_only"
    elif debt_conflict_active or public_debt_signal is not None:
        finance_readiness_state = "hold_for_overstatement_risk"
    else:
        finance_readiness_state = "bounded_decision_grade"
    cost_basis_state = "public_search_only" if ws_capex.get("numeric_extracts") or ws_capex.get("results") else "unavailable"
    publication_ceiling = (
        "publish_with_degradation" if finance_readiness_state == "hold_for_overstatement_risk"
        else "publish_bounded"
    )
    hardening_requirements = [
        "Asset-level revenue / NOI boundary confirmation.",
        "Confirmed debt schedule and scope reconciliation.",
        "Utility tariff data for the actual asset.",
        "Local CapEx quotes or engineering reserve evidence.",
        "Asset-specific operating baseline and verification path.",
    ]
    return {
        "financial_exposure_case_id": f"fec:{produced_at[:19]}",
        "produced_at": produced_at,
        "finance_readiness_state": finance_readiness_state,
        "scope_boundary": "consolidated_entity_level_only",
        "baseline_dependency_state": "asset_specific_baseline_unavailable",
        "tariff_basis_state": "unavailable",
        "cost_basis_state": cost_basis_state,
        "time_horizon": financials.get("filing_date", "") or "latest_annual_filing_period",
        "discount_basis": "not_permitted_in_current_state",
        "bankability_posture": "not_bankable_in_current_state",
        "publication_ceiling": publication_ceiling,
        "financial_assumption_register": [
            {
                "assumption_id": "FA-01",
                "assumption": "Reported financial metrics are consolidated at issuer/entity scope, not asset scope.",
            },
            {
                "assumption_id": "FA-02",
                "assumption": "No asset-level tariff, OPEX, NOI, or validated baseline is currently available.",
            },
            {
                "assumption_id": "FA-03",
                "assumption": "Public CapEx / leverage signals are contextual only unless reconciled locally.",
            },
        ],
        "metric_permission_register": {
            "allowed_context_metrics": [
                "revenues_annual",
                "operating_income",
                "net_income_annual",
                "total_assets",
                "total_debt",
            ],
            "inadmissible_metrics": [
                "asset_level_NOI",
                "asset_level_payback",
                "asset_level_IRR",
                "asset_level_NPV",
                "DSCR",
                "bankability_claim",
            ],
        },
        "range_provenance_record": [
            {
                "metric_id": "consolidated_revenue",
                "basis": "sec_edgar_xbrl_annual",
                "value": financials.get("revenues_annual"),
            },
            {
                "metric_id": "reported_total_debt",
                "basis": "sec_edgar_xbrl_annual",
                "value": reported_debt,
            },
            {
                "metric_id": "public_debt_signal",
                "basis": public_debt_label or "not_available",
                "value": public_debt_signal,
            },
            {
                "metric_id": "capex_public_signals",
                "basis": "web_search_capex_sustainability",
                "value": (ws_capex.get("numeric_extracts", []) or [])[:5],
            },
        ],
        "preliminary_financial_implication": (
            "Current financial use is limited to scale, leverage ambiguity, and value-of-information framing. "
            "No asset-level economics can be closed from the present evidence state."
        ),
        "hardening_requirements": hardening_requirements,
        "public_debt_signal": public_debt_signal,
        "public_debt_signal_label": public_debt_label,
    }


class Motor016Adapter(BaseMotorAdapter):
    @property
    def motor_id(self) -> str:
        return "motor_016"

    @property
    def input_motor_ids(self) -> list[str]:
        return [
            "motor_015", "motor_014", "motor_012", "motor_034",
            "motor_018", "motor_019", "motor_028", "motor_001",
            "motor_033", "motor_035",
            "motor_037", "motor_038", "motor_039", "motor_040",
            "motor_041", "motor_042", "motor_043", "motor_044",
            "motor_045", "motor_046", "motor_047", "motor_048",
        ]

    def _run_impl(self, inputs: dict[str, Any]) -> dict[str, Any]:
        pipeline     = inputs.get("__pipeline__", {})
        produced_at  = datetime.now(timezone.utc).isoformat()

        m15 = inputs.get("motor_015", {})
        m14 = inputs.get("motor_014", {})
        m12 = inputs.get("motor_012", {})
        m34 = inputs.get("motor_034", {}) if isinstance(inputs.get("motor_034", {}), dict) else {}
        m28 = inputs.get("motor_028", {})
        m47 = inputs.get("motor_047", {}) if isinstance(inputs.get("motor_047", {}), dict) else {}
        m48 = inputs.get("motor_048", {}) if isinstance(inputs.get("motor_048", {}), dict) else {}
        m53 = inputs.get("motor_053", {}) if isinstance(inputs.get("motor_053", {}), dict) else {}
        m54 = inputs.get("motor_054", {}) if isinstance(inputs.get("motor_054", {}), dict) else {}

        skill_support_context = build_skill_first_package_support_context(
            target_definition=(inputs.get("__runtime__", {}) if isinstance(inputs.get("__runtime__", {}), dict) else {}).get(
                "target_definition",
                {},
            ),
            executive_thesis=dict(m47.get("executive_thesis", {}) or {}),
            motor_053_output=m53,
            motor_054_output=m54,
        )
        skill_analysis_context = build_skill_first_runtime_analysis_registers(
            target_definition=(inputs.get("__runtime__", {}) if isinstance(inputs.get("__runtime__", {}), dict) else {}).get(
                "target_definition",
                {},
            ),
            executive_thesis=dict(m47.get("executive_thesis", {}) or {}),
            motor_053_output=m53,
            motor_054_output=m54,
        )

        output_blocks      = m15.get("output_blocks", [])
        composite_reading  = m15.get("composite_reading", {})
        facility_prior_id  = m15.get("facility_prior_id", "")
        traceability_register = m15.get("traceability_register", {})
        decision_core_lineage = m14.get("decision_core_lineage", {})
        source_lineage = m12.get("evidence_lineage", {})
        if not output_blocks:
            output_blocks = list(skill_support_context.get("output_blocks", []) or [])
        if not composite_reading:
            composite_reading = dict(skill_support_context.get("composite_reading", {}) or {})

        m49 = inputs.get("motor_049", {}) if isinstance(inputs.get("motor_049", {}), dict) else {}
        m51 = inputs.get("motor_051", {}) if isinstance(inputs.get("motor_051", {}), dict) else {}
        inference_records      = m14.get("inference_records", [])
        tension_records        = m14.get("tension_records", [])
        conflict_register      = m14.get("conflict_register", [])
        opportunity_candidates = m14.get("opportunity_candidates", [])
        uncertainty_register   = m14.get("uncertainty_register", [])
        evidence_gap_register  = m14.get("evidence_gap_register", [])
        validation_queue       = m14.get("validation_queue", [])
        next_best_questions    = m14.get("next_best_questions", [])
        if not inference_records:
            inference_records = list(skill_analysis_context.get("inference_records", []) or [])
        if not conflict_register:
            conflict_register = list(skill_analysis_context.get("conflict_register", []) or [])
        if not opportunity_candidates:
            opportunity_candidates = list(skill_analysis_context.get("opportunity_candidates", []) or [])
        if not uncertainty_register:
            uncertainty_register = list(skill_analysis_context.get("uncertainty_register", []) or [])
        if not evidence_gap_register:
            evidence_gap_register = list(skill_analysis_context.get("evidence_gap_register", []) or [])
        if not validation_queue:
            validation_queue = list(skill_analysis_context.get("validation_queue", []) or [])
        if not next_best_questions:
            next_best_questions = list(skill_analysis_context.get("next_best_questions", []) or [])
        scenario_space         = list(m14.get("scenario_space", []) or [])
        claim_permission_summary = m14.get("claim_permission_summary", {}) if isinstance(m14.get("claim_permission_summary", {}), dict) else {}
        variable_bottleneck_register = list(m14.get("variable_bottleneck_register", []) or [])
        report_readiness_register = dict(
            m14.get("report_readiness_register", m34.get("report_readiness_register", {})) or {}
        )
        if not scenario_space:
            scenario_space = list(skill_support_context.get("scenario_space", []) or [])
        if not claim_permission_summary:
            claim_permission_summary = dict(skill_support_context.get("claim_permission_summary", {}) or {})
        if not variable_bottleneck_register:
            variable_bottleneck_register = list(skill_support_context.get("variable_bottleneck_register", []) or [])
        if not report_readiness_register:
            report_readiness_register = dict(skill_support_context.get("report_readiness_register", {}) or {})
        motor_014_enrichment_state = (
            "legacy_present"
            if m14
            else "optional_legacy_absent_skill_backfilled"
            if inference_records or validation_queue or next_best_questions
            else "optional_legacy_absent_unbackfilled"
        )
        motor_015_enrichment_state = (
            "legacy_present"
            if m15
            else "optional_legacy_absent_skill_backfilled"
            if output_blocks or report_readiness_register or claim_permission_summary
            else "optional_legacy_absent_unbackfilled"
        )
        legacy_enrichment_dependency_state = (
            "optional_legacy_enrichment_only"
            if motor_014_enrichment_state != "optional_legacy_absent_unbackfilled"
            and motor_015_enrichment_state != "optional_legacy_absent_unbackfilled"
            else "legacy_enrichment_gap"
        )
        report_type_classifier_table = list(m34.get("report_type_classifier_table", []) or [])
        claim_contract_register = list(m34.get("claim_contract_register", []) or [])
        structural_claim_permission_register = list(m34.get("structural_claim_permission_register", []) or [])
        structural_output_mode_classifier_table = list(m34.get("structural_output_mode_classifier_table", []) or [])
        structural_output_mode_summary = dict(m34.get("structural_output_mode_summary", {}) or {})
        structural_primary_promotion_gate = dict(m34.get("structural_primary_promotion_gate", {}) or {})
        system_abstraction = dict(inputs.get("motor_037", {}).get("system_abstraction", {}) or {})
        dominant_variable_register = list(inputs.get("motor_038", {}).get("dominant_variable_register", []) or [])
        cross_layer_conflict_register = list(inputs.get("motor_040", {}).get("cross_layer_conflict_register", []) or [])
        problem_framing_register = list(inputs.get("motor_041", {}).get("problem_framing_register", []) or [])
        structural_benchmark_register = list(inputs.get("motor_042", {}).get("structural_benchmark_register", []) or [])
        competitive_comparison_register = list(inputs.get("motor_043", {}).get("competitive_comparison_register", []) or [])
        conditional_redesign_register = list(inputs.get("motor_044", {}).get("conditional_redesign_register", []) or [])
        structural_financial_exposure_register = list(inputs.get("motor_045", {}).get("structural_financial_exposure_register", []) or [])
        evidence_state_by_layer_register = list(inputs.get("motor_045", {}).get("evidence_state_by_layer_register", []) or [])
        minimum_evidence_for_discrimination_register = list(inputs.get("motor_046", {}).get("minimum_evidence_for_discrimination_register", []) or [])
        expanded_structural_tad_action_register: list[dict[str, Any]] = []

        facility_prior  = m12.get("facility_prior", {})
        fp_entities     = facility_prior.get("entities", {})
        fp_assumptions  = facility_prior.get("prior_assumptions_pack", [])
        fp_uncertainty  = facility_prior.get("uncertainty_markers", [])
        fp_tensions     = facility_prior.get("operational_tension_hypotheses", [])
        sys_hyps        = facility_prior.get("system_asset_hypotheses", [])

        m19_out              = inputs.get("motor_019", {})
        llm_written_sections = m19_out.get("written_sections", [])
        llm_available        = m19_out.get("codex_available", m19_out.get("ollama_available", False))
        llm_model            = m19_out.get("model_used", "")
        llm_governance_summary = m19_out.get("llm_governance_summary", {})
        runtime              = inputs.get("__runtime__", {}) if isinstance(inputs.get("__runtime__", {}), dict) else {}
        runtime_target_definition = runtime.get("target_definition", {}) if isinstance(runtime.get("target_definition", {}), dict) else {}
        runtime_target_admissibility_state = runtime.get("target_admissibility_state", "")
        canonical_asset_context_summary = dict(
            m14.get("canonical_asset_context_summary", m34.get("canonical_asset_context_summary", {})) or {}
        )
        runtime_asset_context_readiness = (
            str(canonical_asset_context_summary.get("canonical_asset_context_state", "")).strip()
            or runtime.get("asset_context_readiness", "")
        )
        runtime_report_identity_state = runtime.get("report_identity_state", "")
        runtime_recommended_report_type = runtime.get("recommended_report_type", "")
        runtime_report_identity_state, runtime_recommended_report_type = _refine_runtime_report_identity(
            runtime_target_admissibility_state,
            runtime_report_identity_state,
            runtime_recommended_report_type,
            report_readiness_register,
        )
        if bool(structural_primary_promotion_gate.get("override_allowed", False)):
            elected_mode = str(structural_primary_promotion_gate.get("elected_primary_report_type", "") or "").strip()
            if elected_mode:
                runtime_report_identity_state = elected_mode
                runtime_recommended_report_type = elected_mode
        runtime_dominant_evidence_scope = runtime.get("dominant_evidence_scope", "")
        runtime_missing_observable_clusters = list(
            canonical_asset_context_summary.get("missing_clusters", runtime.get("missing_observable_clusters", [])) or []
        )

        m33_out      = inputs.get("motor_033", {})
        tad_prelim   = m33_out.get("tad_preliminary", {})
        tad_actions  = tad_prelim.get("tad_action_plan", [])
        tad_frontier = tad_prelim.get("decision_frontier", "")
        tad_deficit  = tad_prelim.get("information_deficit_score", None)
        tad_posture_summary = tad_prelim.get("posture_summary", {})
        expanded_structural_tad_action_register = list(m33_out.get("expanded_structural_tad_action_register", []) or [])

        chart_assets = inputs.get("motor_018", {}).get("chart_assets", [])
        chart_errors = inputs.get("motor_018", {}).get("chart_errors", [])
        provisional_case_id = derive_effective_case_id(pipeline, runtime_target_definition)
        chart_case_namespace_register = build_case_namespace_register(
            target_definition=runtime_target_definition,
            case_id=provisional_case_id,
            case_title=str(pipeline.get("case_title", "Governed Asset Brief")).strip(),
            document_visible_type=runtime_report_identity_state or runtime_recommended_report_type,
        )
        chart_assets = stamp_chart_asset_case_context(
            chart_assets=chart_assets,
            case_namespace_register=chart_case_namespace_register,
        )
        _section_chart_map: dict[str, str] = {}
        _chart_b64_map: dict[str, str] = {}
        _chart_b64_list_map: dict[str, list[str]] = {}
        _chart_asset_list_map: dict[str, list[dict[str, Any]]] = {}
        for ca in chart_assets:
            hint = ca.get("section_hint", "")
            if not hint:
                continue
            if hint not in _section_chart_map:
                _section_chart_map[hint] = ca["asset_id"]
            if hint not in _chart_b64_map:
                _chart_b64_map[hint] = ca.get("image_b64", "")
            _chart_b64_list_map.setdefault(hint, []).append(ca.get("image_b64", ""))
            _chart_asset_list_map.setdefault(hint, []).append(ca)

        m28_out         = inputs.get("motor_028", {})
        enriched        = m28_out.get("enriched_data", {})
        financials      = enriched.get("financials", {})
        quality_gate    = m28_out.get("quality_gate_passed", False)
        requestable_evidence_items = m28_out.get("requestable_evidence_items", [])
        source_register = list(m28_out.get("source_register", []) or [])
        source_family_coverage_base = list(m28_out.get("source_family_coverage_table", []) or [])
        search_attempt_ledger = list(m28_out.get("search_attempt_ledger", []) or [])
        discovery_need_register = list(m28_out.get("discovery_need_register", []) or [])
        next_best_search_register = list(m28_out.get("next_best_search_register", []) or [])
        benchmark_routing_register = enriched.get("benchmark_routing_register", {})
        source_scope_register = enriched.get("source_scope_register", {})
        m35 = inputs.get("motor_035", {}) if isinstance(inputs.get("motor_035", {}), dict) else {}
        maturity_summary = dict(m34.get("maturity_summary", {}) or {})
        cluster_maturity_register = list(m34.get("cluster_maturity_register", []) or [])
        asset_field_register = list(m12.get("asset_field_register", []) or [])
        variable_maturity_register = list(
            m14.get("variable_maturity_register", m34.get("variable_maturity_register", [])) or []
        )
        claim_permission_register = list(m14.get("claim_permission_register", m34.get("claim_permission_register", [])) or [])
        peer_requirement_register = list(m51.get("peer_requirement_register", []) or [])
        comparison_blocker_register = list(m51.get("comparison_blocker_register", []) or [])
        comparison_not_yet_valid_register = list(m51.get("comparison_not_yet_valid_register", []) or [])
        decision_permission_register = list(
            m14.get("decision_permission_register", m34.get("decision_permission_register", [])) or []
        )
        if not claim_permission_register:
            claim_permission_register = list(skill_support_context.get("claim_permission_register", []) or [])
        if not decision_permission_register:
            decision_permission_register = list(skill_support_context.get("decision_permission_register", []) or [])
        blocked_claim_count = len(
            [row for row in claim_permission_register if str(row.get("current_permission", "")).strip() == "prohibited"]
        )

        fi           = pipeline.get("facility_inputs", {})
        case_id      = derive_effective_case_id(pipeline, runtime_target_definition)
        case_title   = pipeline.get("case_title", "Governed Asset Brief")
        case_subtitle = pipeline.get("case_subtitle", "Asset Decision-Admissibility Brief")
        organization = pipeline.get("organization", "ZLab")
        analyst      = pipeline.get("analyst", "Autonomous Decision System")

        revenues         = financials.get("revenues_annual")
        total_debt       = financials.get("total_debt")
        total_assets     = financials.get("total_assets")
        net_income       = financials.get("net_income_annual")
        operating_income = financials.get("operating_income")
        filing_date      = financials.get("filing_date", "")
        revenues_series  = financials.get("revenues_series", [])

        exec_block       = _find_block(output_blocks, "executive_summary_block")
        tech_block       = _find_block(output_blocks, "technical_summary_block")
        evidence_block   = _find_block(output_blocks, "evidence_table_block")
        minimum_evidence_pack_block = _find_block(output_blocks, "minimum_evidence_pack_block")
        scenario_space_block = _find_block(output_blocks, "scenario_space_block")
        financial_exposure_block = _find_block(output_blocks, "financial_exposure_block")
        uncertainty_block = _find_block(output_blocks, "uncertainty_block")
        conflict_block   = _find_block(output_blocks, "conflict_block")
        opportunity_block = _find_block(output_blocks, "opportunity_block")
        validation_block = _find_block(output_blocks, "validation_agenda_block")
        next_steps_block = _find_block(output_blocks, "next_steps_block")
        caption_block    = _find_block(output_blocks, "artifact_caption_block")

        # LLM narrative lookup (section_id → text)
        llm_section_lookup: dict[str, dict[str, Any]] = {
            s["section_id"]: s
            for s in llm_written_sections
            if s.get("section_id")
        }
        llm_lookup: dict[str, str] = {
            sid: sec.get("text", "")
            for sid, sec in llm_section_lookup.items()
        }
        llm_lookup_en: dict[str, str] = {
            sid: sec.get("text_en", sec.get("text", ""))
            for sid, sec in llm_section_lookup.items()
        }
        llm_lookup_es: dict[str, str] = {
            sid: sec.get("text_es", sec.get("text", ""))
            for sid, sec in llm_section_lookup.items()
        }

        fac     = fi.get("input_02_facility_type", {})
        size    = fi.get("input_05_size", {})
        vintage = fi.get("input_06_vintage", {})
        tenants = fi.get("input_04_primary_use", {})
        schedule = fi.get("input_07_operating_schedule", {})
        energy  = fi.get("input_08_energy_fuel", {})
        systems = fi.get("input_09_known_systems", {})
        concern = fi.get("input_10_main_concern", {})
        loc     = fi.get("input_01_location", {})
        sector  = fi.get("input_03_sector", {})
        canonical_address = _asset_field_text(asset_field_register, "address", default=loc.get("address", "NOT OBSERVED"))
        canonical_asset_class = _asset_field_text(
            asset_field_register,
            "asset_class",
            "primary_classification",
            default=fac.get("primary_classification", "NOT OBSERVED"),
        )
        canonical_parcel_id = _asset_field_text(
            asset_field_register,
            "parcel_id",
            "property_id",
            "bbl",
            default="NOT OBSERVED",
        )
        canonical_gfa = _asset_field_int(asset_field_register, "GFA", "GFA_sqft", "gross_floor_area")
        canonical_floor_count = _asset_field_int(asset_field_register, "floor_count", "floors_total", "total_floors")
        canonical_year_built = _asset_field_text(asset_field_register, "year_built", default=str(vintage.get("year_built", "")).strip() or "NOT OBSERVED")
        canonical_occupancy = _asset_field_text(
            asset_field_register,
            "occupancy",
            "use_mix",
            default=tenants.get("use_1", "NOT OBSERVED"),
        )
        canonical_current_eui = _asset_field_text(asset_field_register, "current_EUI", "EUI", default="")
        company_name = enriched.get("company_name", sector.get("owner_name", "Unknown Company"))
        ticker = enriched.get("ticker", sector.get("owner_ticker", "")) or "NOT OBSERVED"
        owner_row = _best_asset_field_row(asset_field_register, "owner", "owner_name")
        owner_scope = str(owner_row.get("scope", "")).strip()
        owner_name_from_fields = str(owner_row.get("value", "")).strip()
        owner_name_fallback = str(runtime_target_definition.get("owner_entity", "")).strip()
        owner_display_name = owner_name_from_fields or owner_name_fallback or company_name or "NOT OBSERVED"
        if owner_scope == "ENTITY_LEVEL" and owner_display_name != "NOT OBSERVED":
            owner_display_name = f"{owner_display_name} [entity-level support only]"
        weak_asset_identity = _is_blocked_report_class(runtime_report_identity_state)
        internal_document_type = runtime_report_identity_state or "Asset Decision-Admissibility Brief"
        document_label = _visible_document_label(
            runtime_report_identity_state,
            runtime_recommended_report_type,
        )
        target_label = canonical_address or runtime_target_definition.get("target_name") or case_title or company_name
        case_title = target_label
        case_subtitle = _visible_case_subtitle(
            runtime_report_identity_state,
            runtime_target_admissibility_state,
            runtime_asset_context_readiness,
            "en",
        )
        case_subtitle_es = _visible_case_subtitle(
            runtime_report_identity_state,
            runtime_target_admissibility_state,
            runtime_asset_context_readiness,
            "es",
        )
        main_warning = _main_warning_text(
            runtime_target_admissibility_state,
            runtime_asset_context_readiness,
            runtime_missing_observable_clusters,
            "en",
        )
        main_warning_es = _main_warning_text(
            runtime_target_admissibility_state,
            runtime_asset_context_readiness,
            runtime_missing_observable_clusters,
            "es",
        )
        allowed_use = [
            "Evidence request",
            "Diligence scoping",
            "Validation sequencing",
        ]
        allowed_use_es = [
            "Solicitud de evidencia",
            "Alcance de diligencia",
            "Secuenciación de validación",
        ]
        prohibited_use = [
            "Investment recommendation",
            "Compliance conclusion",
            "Savings estimate",
            "Bankability claim",
        ]
        prohibited_use_es = [
            "Recomendación de inversión",
            "Conclusión de cumplimiento",
            "Estimación de ahorros",
            "Afirmación de bancabilidad",
        ]
        subject_label = target_label or company_name
        industry_adaptation_table = _build_industry_adaptation_table(
            target_type=str(runtime_target_definition.get("target_type", "")),
            requestable_evidence_items=list(minimum_evidence_pack_block.get("rows", []) or []),
            scenario_space=list(scenario_space_block.get("rows", scenario_space) or []),
            financial_exposure_rows=list(financial_exposure_block.get("rows", []) or []),
        )
        canonical_problem_frame = dict(
            m33_out.get("canonical_problem_frame", m14.get("canonical_problem_frame", m34.get("canonical_problem_frame", {}))) or {}
        )
        structural_reasoning_path = dict(
            m33_out.get("structural_reasoning_path", m14.get("structural_reasoning_path", {})) or {}
        )
        executive_thesis = dict(m47.get("executive_thesis", {}) or {})
        main_report_outline = dict(m48.get("main_report_outline", {}) or {})
        appendix_map = list(m48.get("appendix_map", []) or [])
        section_authority_map = dict(m48.get("section_authority_map", {}) or {})
        deduplicated_claim_map = dict(m48.get("deduplicated_claim_map", {}) or {})
        client_facing_tad = dict(m48.get("client_facing_tad", {}) or {})
        congruence_visibility_register = list(m48.get("congruence_visibility_register", []) or [])
        section_demotions_register = list(m48.get("section_demotions_register", []) or [])
        body_to_appendix_justification_map = dict(m48.get("body_to_appendix_justification_map", {}) or {})
        compression_decision_log = list(m48.get("compression_decision_log", []) or [])
        skill_package_context = build_skill_first_report_package_context(
            target_definition=runtime_target_definition,
            executive_thesis=executive_thesis,
            main_report_outline=main_report_outline,
            motor_053_output=m53,
            motor_054_output=m54,
        )
        if not canonical_problem_frame:
            canonical_problem_frame = dict(skill_package_context.get("canonical_problem_frame", {}) or {})
        if not claim_contract_register:
            claim_contract_register = list(skill_package_context.get("claim_contract_register", []) or [])
        if not structural_claim_permission_register:
            structural_claim_permission_register = list(
                skill_package_context.get("structural_claim_permission_register", []) or []
            )
        if not report_type_classifier_table:
            report_type_classifier_table = list(skill_package_context.get("report_type_classifier_table", []) or [])
        if not structural_output_mode_classifier_table:
            structural_output_mode_classifier_table = list(
                skill_package_context.get("structural_output_mode_classifier_table", []) or []
            )
        if not structural_output_mode_summary:
            structural_output_mode_summary = dict(skill_package_context.get("structural_output_mode_summary", {}) or {})
        if not structural_primary_promotion_gate:
            structural_primary_promotion_gate = dict(
                skill_package_context.get("structural_primary_promotion_gate", {}) or {}
            )
        if not system_abstraction:
            system_abstraction = dict(skill_package_context.get("system_abstraction", {}) or {})
        if not dominant_variable_register:
            dominant_variable_register = list(skill_package_context.get("dominant_variable_register", []) or [])
        if not cross_layer_conflict_register:
            cross_layer_conflict_register = list(skill_package_context.get("cross_layer_conflict_register", []) or [])
        if not problem_framing_register:
            problem_framing_register = list(skill_package_context.get("problem_framing_register", []) or [])
        if not structural_benchmark_register:
            structural_benchmark_register = list(skill_package_context.get("structural_benchmark_register", []) or [])
        if not competitive_comparison_register:
            competitive_comparison_register = list(
                skill_package_context.get("competitive_comparison_register", []) or []
            )
        if not conditional_redesign_register:
            conditional_redesign_register = list(skill_package_context.get("conditional_redesign_register", []) or [])
        if not structural_financial_exposure_register:
            structural_financial_exposure_register = list(
                skill_package_context.get("structural_financial_exposure_register", []) or []
            )
        if not evidence_state_by_layer_register:
            evidence_state_by_layer_register = list(
                skill_package_context.get("evidence_state_by_layer_register", []) or []
            )
        if not minimum_evidence_for_discrimination_register:
            minimum_evidence_for_discrimination_register = list(
                skill_package_context.get("minimum_evidence_for_discrimination_register", []) or []
            )
        if not expanded_structural_tad_action_register:
            expanded_structural_tad_action_register = list(
                skill_package_context.get("expanded_structural_tad_action_register", []) or []
            )
        if not cross_layer_conflict_register:
            dominant_conflict = str(canonical_problem_frame.get("dominant_conflict", "")).strip()
            if dominant_conflict:
                minimum_evidence_text = str(canonical_problem_frame.get("minimum_evidence_to_discriminate", "")).strip()
                evidence_items = [item.strip() for item in minimum_evidence_text.split("+") if item.strip()]
                cross_layer_conflict_register = [
                    {
                        "conflict": dominant_conflict,
                        "layers_involved": ["finance", "control/responsibility", "regulation"],
                        "evidence_state": "CONDITIONAL_HYPOTHESIS",
                        "why_it_matters": str(canonical_problem_frame.get("reframed_problem", "")).strip()
                        or "The dominant structural contradiction still changes capital logic and admissible action sequencing.",
                        "what_confirms_it": evidence_items or ["bounded discriminating evidence"],
                        "what_falsifies_it": [
                            "Observed owner-controlled dominant loads and validated compliance boundary."
                        ],
                        "potential_redesign_direction": "Close the discriminating evidence gap before owner-side CAPEX or closure language.",
                    }
                ]
        structural_intelligence_registers = {
            "system_abstraction": system_abstraction,
            "dominant_variable_register": dominant_variable_register,
            "evidence_state_by_layer_register": evidence_state_by_layer_register,
            "cross_layer_conflict_register": cross_layer_conflict_register,
            "problem_framing_register": problem_framing_register,
            "canonical_problem_frame": canonical_problem_frame,
            "structural_reasoning_path": structural_reasoning_path,
            "structural_benchmark_register": structural_benchmark_register,
            "competitive_comparison_register": competitive_comparison_register,
            "conditional_redesign_register": conditional_redesign_register,
            "structural_financial_exposure_register": structural_financial_exposure_register,
            "minimum_evidence_for_discrimination_register": minimum_evidence_for_discrimination_register,
            "structural_claim_permission_register": structural_claim_permission_register,
            "claim_contract_register": claim_contract_register,
            "structural_output_mode_classifier_table": structural_output_mode_classifier_table,
            "structural_output_mode_summary": structural_output_mode_summary,
            "structural_primary_promotion_gate": structural_primary_promotion_gate,
            "expanded_structural_tad_action_register": expanded_structural_tad_action_register,
            "executive_thesis": executive_thesis,
            "main_report_outline": main_report_outline,
            "appendix_map": appendix_map,
            "section_authority_map": section_authority_map,
            "deduplicated_claim_map": deduplicated_claim_map,
            "client_facing_tad": client_facing_tad,
            "congruence_visibility_register": congruence_visibility_register,
            "section_demotions_register": section_demotions_register,
            "body_to_appendix_justification_map": body_to_appendix_justification_map,
            "compression_decision_log": compression_decision_log,
        }
        structural_intelligence_summary = _build_structural_intelligence_summary(structural_intelligence_registers)
        structural_executive_summary = _build_structural_executive_summary(structural_intelligence_registers)
        owner_exchange = sector.get("exchange") or sector.get("owner_exchange") or "NYSE"
        owner_cik = sector.get("owner_cik", "")
        financial_context_note = (
            f"Financial figures below are consolidated {ticker} data, not necessarily asset-specific."
            if ticker and ticker != "NOT OBSERVED"
            else "Financial figures below are consolidated company-level context, not necessarily asset-specific."
        )

        acq_status    = composite_reading.get("decision_state", "") or _decision_state_text(
            target_label,
            runtime_target_admissibility_state,
            runtime_asset_context_readiness,
            runtime_missing_observable_clusters,
            runtime_recommended_report_type,
            "en",
        )
        blocking_count = len(conflict_register)
        tension_count  = len(tension_records)
        opp_count      = len(opportunity_candidates)
        active_count   = len(inference_records)
        governance_summary = _build_provisional_governance_summary(
            runtime,
            source_lineage,
            decision_core_lineage,
            traceability_register,
            conflict_register,
            llm_available,
            chart_assets,
            chart_errors,
            produced_at,
        )
        governance_summary["scraping_admissibility_summary"] = {
            "target_type_classification": runtime.get("target_type_classification", ""),
            "recommended_report_type": runtime.get("recommended_report_type", ""),
            "source_register_count": len(m28.get("source_register", []) or []),
            "asset_field_register_count": len(m12.get("asset_field_register", []) or []),
            "missing_evidence_count": len(m12.get("missing_evidence_register", []) or []),
            "contamination_log_count": len(m28.get("contamination_log", []) or []),
        }
        routing_plan_compliance = dict(m12.get("routing_plan_compliance", {}) or m28.get("routing_plan_compliance", {}) or {})
        mandatory_source_gaps = list(routing_plan_compliance.get("mandatory_sources_missing_from_executor", []) or [])
        governance_summary["routing_plan_summary"] = {
            "routing_plan_total": int(routing_plan_compliance.get("total_routed_sources", 0) or 0),
            "mandatory_source_gap_count": len(mandatory_source_gaps),
            "mandatory_sources_missing_from_executor": mandatory_source_gaps,
            "routing_plan_gate_passed": len(mandatory_source_gaps) == 0,
        }
        governance_summary["routing_bundle_summary"] = {
            "jurisdiction_resolution": dict(m35.get("jurisdiction_resolution", {}) or {}),
            "asset_type_route": dict(m35.get("asset_type_route", {}) or {}),
            "report_type_switch_recommendation": dict(m35.get("report_type_switch_recommendation", {}) or {}),
            "critical_field_contract": list(m35.get("critical_field_contract", []) or []),
            "source_routing_plan": dict(m35.get("source_routing_plan", {}) or {}),
        }
        source_family_coverage_table = _build_source_family_coverage_table(
            source_family_coverage_base,
            asset_field_register,
        )
        governance_summary["evidence_maturity_summary"] = {
            "counts_by_level": maturity_summary.get("counts_by_level", {}),
            "blocked_claim_count": blocked_claim_count,
            "claim_permission_summary": claim_permission_summary,
            "key_variable_bottlenecks": list(maturity_summary.get("key_bottlenecks", []) or []),
            "variable_bottleneck_register": variable_bottleneck_register[:6],
            "report_type_allowed": report_readiness_register.get("report_type_allowed", []),
            "report_type_prohibited": report_readiness_register.get("report_type_prohibited", []),
            "report_readiness_reason": report_readiness_register.get("reason", ""),
        }
        case_adaptation_memo = _build_case_adaptation_memo(
            target_definition=runtime_target_definition,
            jurisdiction_resolution=dict(m35.get("jurisdiction_resolution", {}) or {}),
            source_register=source_register,
            cluster_maturity_register=cluster_maturity_register,
            decision_front_register=list(m14.get("decision_front_register", []) or []),
            scenario_space=scenario_space,
            report_readiness_register=report_readiness_register,
            variable_bottleneck_register=variable_bottleneck_register,
        )
        governance_summary["case_adaptation_summary"] = {
            "substantive_dimension_count": case_adaptation_memo.get("substantive_dimension_count", 0),
            "required_dimension_count": case_adaptation_memo.get("required_dimension_count", 0),
            "template_contamination_failure": case_adaptation_memo.get("template_contamination_failure", False),
            "failure_reasons": case_adaptation_memo.get("failure_reasons", []),
            "reference_count": (case_adaptation_memo.get("comparison_summary", {}) or {}).get("reference_count", 0),
            "closest_reference_key": (case_adaptation_memo.get("comparison_summary", {}) or {}).get("closest_reference_key", ""),
            "closest_reference_difference_count": (case_adaptation_memo.get("comparison_summary", {}) or {}).get("closest_reference_difference_count", 0),
        }
        if case_adaptation_memo.get("template_contamination_failure"):
            governance_summary.setdefault("downgrade_triggers", []).append(
                "Template contamination failure: case-adaptation memo does not demonstrate sufficient case-specific differentiation."
            )
        if llm_governance_summary.get("fallback_sections", 0) > 0:
            governance_summary["publication_ceiling"] = (
                "publish_with_degradation"
                if governance_summary.get("publication_ceiling") == "publish_bounded"
                else governance_summary.get("publication_ceiling")
            )
            governance_summary.setdefault("downgrade_triggers", []).append(
                f"{llm_governance_summary.get('fallback_sections', 0)} section(s) rendered through deterministic fallback."
            )
        if llm_governance_summary.get("lint_failures", 0) > 0:
            governance_summary.setdefault("downgrade_triggers", []).append(
                f"{llm_governance_summary.get('lint_failures', 0)} LLM section(s) failed policy lint and were downgraded."
            )
        if llm_governance_summary.get("budget_exhausted"):
            governance_summary.setdefault("downgrade_triggers", []).append(
                "LLM writing budget exhausted before all requested sections could be freely rendered."
            )
        if governance_summary.get("downgrade_triggers"):
            governance_summary["framework_constraint"] = " ".join([
                f"This {document_label} is a governed materialization of Decision Core outputs.",
                "It remains Decision-grade unless and until independent evidence upgrades the underlying objects.",
                f"Publication ceiling: {governance_summary.get('publication_ceiling', 'publish_bounded').replace('_', ' ')}.",
                "No statement constitutes a verified diagnosis, compliance determination, or investment recommendation.",
                "All claims remain conditional on validation requirements and domain-of-validity boundaries stated in the report.",
            ] + governance_summary.get("downgrade_triggers", []))
        financial_exposure_case = _build_financial_exposure_case(
            financials,
            enriched,
            source_lineage,
            conflict_register,
            quality_gate,
            produced_at,
        )

        top3 = sorted(
            inference_records,
            key=lambda c: c.get("validation_urgency_score", 0),
            reverse=True,
        )[:3]

        sections: list[dict] = []

        # ── C1: Framework Context & Executive Brief ────────────────────────────
        c1: list[str] = [
            _sep("="),
            document_label.upper(),
            _sep("="),
            "",
            f"  Framework    : ZLab Operational Truth Framework",
            f"  Document Type: {document_label} | Epistemic Grade: {governance_summary.get('epistemic_grade', 'Decision-grade')}",
            f"  Case ID      : {case_id}",
            f"  Date         : {produced_at[:10]}",
            f"  Analyst      : {analyst}",
            "",
            _sep("="),
            "CASE IDENTIFICATION",
            _sep("="),
            "",
            f"  Subject      : {subject_label}",
            f"  Owner        : {owner_display_name} ({ticker} -- {owner_exchange} | CIK {owner_cik})",
            f"  Asset Class  : {canonical_asset_class}",
            f"  Landmark     : {fac.get('landmark_status', '')}",
            "",
            _sep("="),
            "DECISION STATE",
            _sep("="),
            "",
            f"  {acq_status}",
            "",
            f"  Blocking Conflicts : {blocking_count}  [advancement blocked until resolved]",
            f"  Open Tensions      : {tension_count}",
            f"  Inference Cases    : {active_count} active",
            f"  Opportunities      : {opp_count} conditional",
            "",
        ]
        structural_modes = list(structural_executive_summary.get("structural_mode_candidates", []) or [])
        promotable_structural_modes = list(structural_executive_summary.get("promotable_primary_structural_modes", []) or [])
        if any(
            [
                structural_modes,
                promotable_structural_modes,
                structural_executive_summary.get("primary_reframed_problem"),
                structural_executive_summary.get("dominant_structural_conflict"),
                structural_executive_summary.get("primary_structural_action"),
            ]
        ):
            c1 += [
                _sep("="),
                "STRUCTURAL READ",
                _sep("="),
                "",
                f"  Reasoning Path    : {structural_executive_summary.get('default_reasoning_path', 'legacy_decision_gating_only')}",
                f"  Problem Frame     : {'ACTIVE' if structural_executive_summary.get('problem_frame_active', False) else 'INACTIVE'}",
                f"  Mode Candidates   : {', '.join(structural_modes) or 'NONE'}",
                f"  Primary-Eligible  : {', '.join(promotable_structural_modes) or 'NONE'}",
                f"  Reframed Problem  : {structural_executive_summary.get('primary_reframed_problem', '')}",
                f"  Dominant Conflict : {structural_executive_summary.get('dominant_structural_conflict', '')}",
                f"  Structural Action : {structural_executive_summary.get('primary_structural_action', '')} [{structural_executive_summary.get('primary_structural_action_status', '')}]",
                f"  Constraint        : {structural_executive_summary.get('bounded_note', '')}",
                "",
            ]
        c1 += [
            _sep("-"),
            "ACTIVE INFERENCE CASES -- URGENCY RANKING",
            _sep("-"),
            "",
            "  Scores: P = Plausibility | R = Decision Relevance | V = Validation Urgency",
            "",
        ]
        for r in sorted(
            inference_records,
            key=lambda x: x.get("validation_urgency_score", 0),
            reverse=True,
        ):
            c1.append(
                f"  [{r['case_id']}]  {r['case_name']}"
            )
            c1.append(
                f"    P={r.get('plausibility_score',0):.2f}  "
                f"R={r.get('decision_relevance_score',0):.2f}  "
                f"V={r.get('validation_urgency_score',0):.2f}  "
                f"| {_urgency_label(r.get('validation_urgency_score',0))} "
                f"| {_family_label(r.get('claim_family',''))}"
            )
            c1.append("")

        c1 += [
            _sep("="),
            "EPISTEMIC LIMITS OF THIS REPORT",
            _sep("="),
            "",
            "  - No field-verified data. All claims conditional on validation requirements in C7.",
            f"  - {financial_context_note}",
            "  - Energy and systems data are publicly-declared retrofits and benchmark estimates.",
            "  - No investment recommendation is implicit or explicit in this document.",
            f"  - LLM narratives ({llm_model}) are bounded by analytical objects. No new facts.",
            "",
        ]
        if runtime_asset_context_readiness in ("issuer_context_only", "location_only", "asset_context_insufficient"):
            c1 += [
                "  - Asset context is not yet technically mature enough for a normal full-report technical surface.",
                f"  - Current asset context readiness: {runtime_asset_context_readiness}.",
                f"  - Missing observable clusters: {', '.join(runtime_missing_observable_clusters) or 'not recorded'}.",
                "",
            ]

        sections.append(_section(
            sid="c1_framework_brief",
            chapter_id="C1",
            chapter_number=1,
            title="Framework Context & Executive Brief",
            audience="executive",
            section_type="body",
            epistemic_marker="DECISION_GRADE",
            llm_text=llm_lookup.get("s01_exec_narrative", ""),
            llm_text_en=llm_lookup_en.get("s01_exec_narrative", ""),
            llm_text_es=llm_lookup_es.get("s01_exec_narrative", ""),
            block_id="b_exec",
            content=c1,
        ))

        # ── C2: Operational Identity ───────────────────────────────────────────
        # Physical facts + declared systems. Source: facility_inputs + submissions.
        c2: list[str] = [
            _sep("="),
            "PHYSICAL IDENTITY",
            _sep("="),
            "",
            f"  Name               : {case_title or company_name}",
            f"  Address            : {canonical_address}",
            f"  Parcel / Property ID: {canonical_parcel_id}",
            f"  Borough / County   : {loc.get('borough','')} / {loc.get('county','')}",
            f"  Primary Class      : {canonical_asset_class}",
            f"  Secondary Class    : {fac.get('secondary_classification','')}",
            f"  Asset Category     : {fac.get('asset_category','')}",
            f"  Building Class     : {fac.get('building_class','')}",
            f"  Construction Type  : {fac.get('construction_type','')}",
            f"  Landmark Status    : {fac.get('landmark_status','')}",
            f"  Climate Zone       : ASHRAE {loc.get('climate_zone_ASHRAE','')} (Mixed-Humid)",
            "",
            _sep("-"),
            "SIZE AND CONFIGURATION",
            _sep("-"),
            "",
            f"  Total Floors       : {_fmt_optional_number(canonical_floor_count)}",
            f"  Office Floors      : {size.get('floors_office','')}",
            f"  Observatory Floors : {size.get('floors_observatory','')}",
            f"  Building Height    : {size.get('height_ft','')} ft",
            f"  Gross Floor Area   : {_fmt_optional_number(canonical_gfa, ' sqft')}",
            f"  Rentable Office    : {size.get('rentable_office_sqft_approx',0):,} sqft (approx)",
            "",
            _sep("-"),
            "VINTAGE AND CAPITAL HISTORY",
            _sep("-"),
            "",
            f"  Year Built         : {canonical_year_built}  ({vintage.get('years_old','')} years old as of 2026)",
            f"  Vintage Category   : {vintage.get('vintage_category','')}",
            f"  Structural Note    : {vintage.get('structural_note','')}",
            "",
            "  Major Renovations:",
        ]
        for ren in vintage.get("major_renovations_known", []):
            cert = f"  Certification: {ren['certification']}" if ren.get("certification") else ""
            sqft_str = (
                f"  Amenity Added: {ren.get('sqft_amenity_added',0):,} sqft"
                if ren.get("sqft_amenity_added")
                else ""
            )
            c2.append(f"    {ren.get('period','?')}: {ren.get('scope','?')}{cert}{sqft_str}")

        c2 += [
            "",
            _sep("-"),
            "OPERATING SCHEDULE",
            _sep("-"),
            "",
            f"  Office:            {schedule.get('office_schedule','')}",
            f"  Observatory:       {schedule.get('observatory_schedule','')}",
            f"  24/7 Components:   {', '.join(schedule.get('24_7_components',[]))}",
            f"  Peak Note:         {schedule.get('peak_occupancy_note','')}",
            f"  HVAC Note:         {schedule.get('hvac_schedule_note','')}",
            f"  Public Occupancy Basis: {canonical_occupancy}",
            "",
            _sep("-"),
            "TENANT PROFILE",
            _sep("-"),
            "",
            f"  Use 1 -- {tenants.get('use_1','')}  (~{tenants.get('use_1_approx_pct','')}% revenue)",
            f"  Use 2 -- {tenants.get('use_2','')}  (~{tenants.get('use_2_approx_pct','')}% revenue)",
            f"  Use 3 -- {tenants.get('use_3','')}  (~{tenants.get('use_3_approx_pct','')}% revenue)",
            f"  Anchor Tenant      : {tenants.get('anchor_tenant','')}",
            f"  Anchor Sqft        : {tenants.get('anchor_tenant_approx_sqft',0):,} sqft",
            f"  Known Major Tenants: {', '.join(tenants.get('major_tenants_known',[]))}",
            "",
            _sep("-"),
            "DECLARED ENERGY AND SYSTEMS",
            _sep("-"),
            "",
            f"  Primary Fuel       : {energy.get('primary_fuel','')}",
            f"  Primary Uses       : {energy.get('primary_fuel_use','')}",
            f"  Secondary Fuel     : {energy.get('secondary_fuel','')}",
            f"  Secondary Uses     : {energy.get('secondary_fuel_use','')}",
            f"  Utility Electric   : {energy.get('utility_electricity','')}",
            f"  Utility Gas        : {energy.get('utility_gas','')}",
            f"  LEED Gold          : {'Certified -- achieved 2011 through 2019 retrofit' if energy.get('LEED_Gold_certified') else 'Not confirmed'}",
            f"  Declared EUI Note  : {canonical_current_eui or energy.get('recent_EUI_note','')}",
            "",
            "  Known Systems (declared -- not site-verified):",
            f"    HVAC     : {systems.get('HVAC',{}).get('type','')} | {systems.get('HVAC',{}).get('retrofit_status','')}",
            f"    Elevators: {systems.get('elevators',{}).get('count','')} units | {systems.get('elevators',{}).get('status','')}",
            f"    Lighting : {systems.get('lighting',{}).get('type','')} | Controls: {systems.get('lighting',{}).get('controls','')}",
            f"    BMS      : Present={systems.get('BMS',{}).get('present','')} | Integration: {systems.get('BMS',{}).get('integration_level','')}",
            f"    Data Ctr : Tenant-operated ({systems.get('data_center',{}).get('known_occupant','')}) | Density: {systems.get('data_center',{}).get('power_density_class','')}",
            "",
            _sep("-"),
            "SYSTEM ASSET HYPOTHESES",
            _sep("-"),
            "",
            "  These are plausible hypotheses derived from public retrofit disclosures.",
            "  NOT site-verified. Each carries an explicit epistemic qualifier.",
            "",
        ]
        for sh in sys_hyps:
            c2 += [
                f"  System    : {sh.get('system','')}",
                f"  Type      : {sh.get('type', sh.get('type_mix', sh.get('count', '')))}",
                f"  Status    : {sh.get('retrofit_status', sh.get('controls', sh.get('integration_level', '')))}",
                f"  Hypothesis: {sh.get('hypothesis','')}",
                f"  Confidence: {sh.get('confidence','')}",
                f"  Epistemic : {sh.get('epistemic_status','')}",
                "",
            ]

        c2 += [
            _sep("-"),
            "CORPORATE OWNER",
            _sep("-"),
            "",
            f"  Company            : {company_name}",
            f"  Ticker / Exchange  : {ticker} -- {sector.get('owner_exchange','NYSE')}",
            f"  SEC CIK            : {sector.get('owner_cik','')}",
            f"  NAIC Code          : {sector.get('naic_code','')}",
            f"  Ownership Struct   : {sector.get('ownership_structure','')}",
            f"  SIC Description    : {enriched.get('sic_description','Real Estate Investment Trust')}",
            f"  State of Incorp    : {enriched.get('state_of_incorporation','')}",
            "",
            _sep("-"),
            "PRIMARY CONCERN AT INTAKE",
            _sep("-"),
            "",
            f"  {concern.get('primary_concern','')}",
            "",
            "  Sub-Concerns:",
        ]
        for sc in concern.get("sub_concerns", []):
            c2.append(f"    - {sc}")
        c2.append("")

        sections.append(_section(
            sid="c2_operational_identity",
            chapter_id="C2",
            chapter_number=2,
            title="Operational Identity",
            audience="technical",
            section_type="body",
            epistemic_marker="DIRECT_EVIDENCE",
            llm_text=llm_lookup.get("s00_operational_identity", ""),
            llm_text_en=llm_lookup_en.get("s00_operational_identity", ""),
            llm_text_es=llm_lookup_es.get("s00_operational_identity", ""),
            block_id="b_profile",
            content=c2,
        ))

        # ── C3: Blocking Conflicts ─────────────────────────────────────────────
        c3: list[str] = [
            _sep("="),
            "CONFLICT REGISTER -- HARD INCOMPATIBILITIES",
            _sep("="),
            "",
            "A CONFLICT is a hard incompatibility between data points that CANNOT",
            "coexist without resolution. Unlike tensions (which require trade-offs),",
            "conflicts BLOCK analytical advancement until resolved.",
            "",
        ]

        if not conflict_register:
            c3.append("  No hard conflicts activated in this analysis run.")
        else:
            for c in conflict_register:
                rec = next(
                    (r for r in inference_records if r["case_id"] == c.get("inference_case_id", "")),
                    {},
                )
                c3 += [
                    _sep("*"),
                    f"  *** BLOCKING CONFLICT [{c['conflict_id']}] ***",
                    _sep("*"),
                    "",
                    f"  Case Reference    : {c.get('inference_case_id','')}",
                    f"  Name              : {c['conflict_name']}",
                    f"  Conflict Type     : {c.get('conflict_type','').replace('_',' ').title()}",
                    f"  Blocking Status   : {c.get('blocking_status','')}",
                    "",
                    f"  P={c.get('plausibility_score',0):.2f}  R={c.get('decision_relevance_score',0):.2f}  V={c.get('validation_urgency_score',0):.2f}  [{_urgency_label(c.get('validation_urgency_score',0))}]",
                    "",
                    "  CONFLICT STATEMENT:",
                ]
                c3 += _wrap_text(c.get("conflict_statement", ""))

                if rec:
                    c3 += ["", "  INFERENCE LOGIC:"]
                    c3 += _wrap_text(rec.get("inference_logic", ""))
                    c3 += ["", "  DEPENDENCY ASSUMPTIONS:"]
                    for i, dep in enumerate(rec.get("dependency_assumptions", []), 1):
                        c3.append(f"    {i}. {dep}")

                c3 += [
                    "",
                    "  RESOLUTION PATH:",
                    f"    {c.get('validation_requirement','')}",
                    "",
                    "  DECISION IMPLICATION:",
                    "    No credible claim upgrade is possible until this conflict is resolved.",
                    "    Downstream analytical weight depends on obtaining the stated evidence.",
                    "",
                ]

        sections.append(_section(
            sid="c3_blocking_conflicts",
            chapter_id="C3",
            chapter_number=3,
            title="Blocking Conflicts",
            audience="technical",
            section_type="body",
            epistemic_marker="BLOCKING_CONFLICT",
            llm_text=llm_lookup.get("s02_blocking_conflict", ""),
            llm_text_en=llm_lookup_en.get("s02_blocking_conflict", ""),
            llm_text_es=llm_lookup_es.get("s02_blocking_conflict", ""),
            block_id="b_conflicts",
            content=c3,
        ))

        # ── C4: Inference Case Map ─────────────────────────────────────────────
        c4: list[str] = [
            _sep("="),
            "INFERENCE CASE REGISTER -- DECISION CORE OUTPUT",
            _sep("="),
            "",
            "Activation means: the current asset-context prior contains sufficient triggers to",
            "justify structured investigation. Activation is NOT confirmation.",
            "",
            _sep("-"),
            "SUMMARY TABLE",
            _sep("-"),
            "",
            "  Case ID    | Family                  | P    | R    | V    | Urgency",
            "  -----------|-------------------------|------|------|------|--------",
        ]
        for r in sorted(
            inference_records,
            key=lambda x: x.get("validation_urgency_score", 0),
            reverse=True,
        ):
            fam_short = _family_label(r.get("claim_family", ""))[:24]
            c4.append(
                f"  {r['case_id']:<10} | {fam_short:<23} | "
                f"{r.get('plausibility_score',0):.2f} | "
                f"{r.get('decision_relevance_score',0):.2f} | "
                f"{r.get('validation_urgency_score',0):.2f} | "
                f"{_urgency_label(r.get('validation_urgency_score',0))}"
            )
        c4 += ["", _sep("-"), "DETAILED CASE RECORDS", _sep("-")]

        for rec in sorted(
            inference_records,
            key=lambda x: x.get("validation_urgency_score", 0),
            reverse=True,
        ):
            c4 += [
                "",
                f"  [{rec['case_id']}]  {rec['case_name']}",
                f"  {_sep('=', 68)}",
                f"  Claim Family   : {_family_label(rec.get('claim_family',''))}",
                f"  P={rec.get('plausibility_score',0):.2f}  R={rec.get('decision_relevance_score',0):.2f}  V={rec.get('validation_urgency_score',0):.2f}  [{_urgency_label(rec.get('validation_urgency_score',0))}]",
                "",
                "  CONDITIONAL STATEMENT:",
            ]
            c4 += _wrap_text(rec.get("conditional_statement", ""))
            c4 += ["", "  INFERENCE LOGIC:"]
            c4 += _wrap_text(rec.get("inference_logic", ""))
            c4 += ["", "  DEPENDENCY ASSUMPTIONS:"]
            for i, dep in enumerate(rec.get("dependency_assumptions", []), 1):
                c4.append(f"    {i}. {dep}")
            c4 += ["", "  BASE SUPPORT TRACES:"]
            for trace in rec.get("base_support_traces", []):
                c4.append(f"    - {trace}")
            rationale = rec.get("score_rationale", {})
            if any(rationale.values()):
                c4 += ["", "  SCORE RATIONALE:"]
                if rationale.get("plausibility"):
                    c4.append(f"    Plausibility       : {rationale['plausibility']}")
                if rationale.get("decision_relevance"):
                    c4.append(f"    Decision Relevance : {rationale['decision_relevance']}")
                if rationale.get("validation_urgency"):
                    c4.append(f"    Validation Urgency : {rationale['validation_urgency']}")
            c4 += [
                "",
                "  VALIDATION REQUIREMENT:",
                f"    {rec.get('validation_requirement','')}",
                "",
                _sep("-"),
            ]

        case_narrative_keys = sorted(k for k in llm_lookup if k.startswith("s03_case_"))
        llm_c4 = "\n\n".join(llm_lookup[k] for k in case_narrative_keys)
        llm_c4_en = "\n\n".join(llm_lookup_en[k] for k in case_narrative_keys)
        llm_c4_es = "\n\n".join(llm_lookup_es[k] for k in case_narrative_keys)

        sections.append(_section(
            sid="c4_inference_case_map",
            chapter_id="C4",
            chapter_number=4,
            title="Inference Case Map",
            audience="technical",
            section_type="body",
            epistemic_marker="INFERRED",
            llm_text=llm_c4,
            llm_text_en=llm_c4_en,
            llm_text_es=llm_c4_es,
            block_id="b_inference",
            content=c4,
        ))

        # ── C5: Energy Profile & Normative Constraints ─────────────────────────
        reg_ctx = fp_entities.get("RegulatoryContext", {})
        imp_con = fp_entities.get("ImprovementConstraint", {})
        bench   = facility_prior.get("benchmark_bundle", {})
        reg_flags = facility_prior.get("regulatory_flag_bundle", {})
        comp_case = facility_prior.get("compliance_applicability_case", m12.get("compliance_applicability_case", {}))
        comp_trace = comp_case.get("jurisdiction_trace_record", {})
        comp_triggers = comp_case.get("trigger_field_register", [])
        comp_thresholds = comp_case.get("threshold_register", [])

        is_nyc_case = any(
            "US-NY" in str(item).upper() or "NYC" in str(item).upper() or "NEW YORK" in str(item).upper()
            for item in (runtime_target_definition.get("jurisdiction_scope") or [])
        )
        adjusted_benchmark_label = "NYC-Adjusted EUI" if is_nyc_case else "Adjusted Benchmark EUI"

        c5: list[str] = [
            _sep("="),
            "ENERGY PROFILE AND NORMATIVE CONSTRAINTS",
            _sep("="),
            "",
            "This section covers the analytical layer on energy risk:",
            "system hypotheses, regulatory applicability posture, benchmark context,",
            "and improvement constraints. Data is hypothesis-level unless noted.",
            "",
            _sep("-"),
            "BENCHMARK CONTEXT",
            _sep("-"),
            "",
            f"  Benchmark Source   : {bench.get('benchmark_source', reg_ctx.get('benchmark_source','EIA CBECS 2018'))}",
            f"  Office Median EUI  : {bench.get('office_sector_median_EUI_kBtu_sqft', reg_ctx.get('office_sector_median_EUI_kBtu_sqft',''))} kBtu/sqft",
            f"  {adjusted_benchmark_label:<18}: {bench.get('NYC_adjusted_EUI_estimate_kBtu_sqft', reg_ctx.get('NYC_adjusted_EUI_estimate_kBtu_sqft',''))} kBtu/sqft",
            f"  Benchmark Limit    : {bench.get('benchmark_limitation', reg_ctx.get('benchmark_limitation','Sectoral benchmark only -- not site measurement'))}",
            "",
            _sep("-"),
            "REGULATORY APPLICABILITY POSTURE",
            _sep("-"),
            "",
            f"  Primary Regulation   : {comp_trace.get('primary_regulation', reg_ctx.get('primary_regulation', reg_flags.get('primary_regulation','Not assigned')))}",
            f"  Jurisdiction Codes   : {', '.join(comp_trace.get('jurisdiction_codes', reg_ctx.get('jurisdiction_codes', []))) or 'Not assigned'}",
            f"  Applicability State  : {comp_case.get('applicability_state', 'rule_family_relevant')}",
            f"  Posture State        : {comp_case.get('compliance_posture_state', 'trigger_plausible')}",
            f"  Determination Status : {comp_case.get('determination_status', reg_ctx.get('compliance_determination_status','Requires validation'))}",
            f"  Publication Ceiling  : {comp_case.get('publication_ceiling', 'publish_bounded')}",
            "",
        ]
        if comp_triggers:
            c5 += ["  Trigger Field Register:"]
            for trigger in comp_triggers[:4]:
                c5.append(
                    f"    - {trigger.get('field_name','')}: {trigger.get('field_state','')} "
                    f"({trigger.get('value','')})"
                )
            c5.append("")
        if comp_thresholds:
            c5 += ["  Threshold Register:"]
            for threshold in comp_thresholds[:3]:
                c5.append(
                    f"    - {threshold.get('threshold_name','')}: {threshold.get('threshold_state','')} "
                    f"(value={threshold.get('measured_value','')}, threshold={threshold.get('threshold_value','')})"
                )
            c5.append("")
        if comp_case.get("hardening_requirements"):
            c5 += ["  Hardening Requirements:"]
            for req in comp_case.get("hardening_requirements", [])[:4]:
                c5.append(f"    - {req}")
            c5.append("")

        ll97_limit_2030 = reg_ctx.get("LL97_2030_2034_limit_tCO2e_sqft", reg_flags.get("LL97_2030_2034_limit_tCO2e_sqft"))
        ll97_penalty_rate = reg_ctx.get("LL97_penalty_per_tCO2e_usd", reg_flags.get("LL97_penalty_per_tCO2e_usd"))
        ll97_gfa = reg_ctx.get("LL97_GFA_sqft", reg_flags.get("LL97_GFA_sqft"))
        if is_nyc_case and ll97_limit_2030 and ll97_penalty_rate and ll97_gfa:
            c5 += [
                _sep("-"),
                "PRIMARY REGULATION DETAIL",
                _sep("-"),
                "",
                f"  Covered GFA         : {ll97_gfa:,} sqft",
                f"  2024-2029 Limit     : {reg_ctx.get('LL97_2024_2029_limit_tCO2e_sqft', reg_flags.get('LL97_2024_2029_limit_tCO2e_sqft',''))} tCO2e/sqft",
                f"  2030-2034 Limit     : {ll97_limit_2030} tCO2e/sqft",
                f"  Penalty Rate        : ${ll97_penalty_rate} per tCO2e above limit",
                f"  Certification Note  : {reg_ctx.get('LEED_Gold_ll97_equivalence', reg_flags.get('LEED_Gold_ll97_equivalence',''))}",
                "",
                "  Illustrative penalty (screening-grade only — not a compliance determination):",
                f"    If actual = 0.010 tCO2e/sqft and 2030 limit = 0.00453 tCO2e/sqft:",
                f"    Overage: 0.00547 x {ll97_gfa:,} sqft = {0.00547 * ll97_gfa:,.0f} tCO2e",
                f"    Annual penalty = ~${0.00547 * ll97_gfa * float(ll97_penalty_rate):,.0f} USD",
                "    ILLUSTRATIVE ONLY. Actual emissions and regulated scope require official disclosure.",
                "",
            ]
        c5 += [
            _sep("-"),
            "IMPROVEMENT CONSTRAINTS",
            _sep("-"),
            "",
            "  Landmark Constraints:",
            f"    Status      : {imp_con.get('landmark_constraints',{}).get('status','')}",
            f"    Implication : {imp_con.get('landmark_constraints',{}).get('implication','')}",
            "",
            "  Structural Constraints:",
            f"    Frame       : {imp_con.get('structural_constraints',{}).get('frame','')}",
            f"    Implication : {imp_con.get('structural_constraints',{}).get('implication','')}",
            "",
            "  Operational Constraints:",
        ]
        for k, v in imp_con.get("operational_constraints", {}).items():
            c5.append(f"    {k}: {v}")
        c5 += ["", "  Regulatory Constraints:"]
        for rc_item in imp_con.get("regulatory_constraints", []):
            c5.append(f"    - {rc_item}")
        c5.append("")

        llm_c5_parts = [
            llm_lookup.get("s09_systems_energy_narrative", ""),
            llm_lookup.get("s09_capex_narrative", ""),
        ]
        llm_c5 = "\n\n".join(p for p in llm_c5_parts if p)
        llm_c5_en = "\n\n".join(
            p for p in [
                llm_lookup_en.get("s09_systems_energy_narrative", ""),
                llm_lookup_en.get("s09_capex_narrative", ""),
            ] if p
        )
        llm_c5_es = "\n\n".join(
            p for p in [
                llm_lookup_es.get("s09_systems_energy_narrative", ""),
                llm_lookup_es.get("s09_capex_narrative", ""),
            ] if p
        )
        if not is_nyc_case:
            c5 = [_sanitize_non_local_regulatory_text(line, is_nyc_case=False) for line in c5]
            llm_c5 = _sanitize_non_local_regulatory_text(llm_c5, is_nyc_case=False)
            llm_c5_en = _sanitize_non_local_regulatory_text(llm_c5_en, is_nyc_case=False)
            llm_c5_es = _sanitize_non_local_regulatory_text(llm_c5_es, is_nyc_case=False)

        sections.append(_section(
            sid="c5_energy_normative",
            chapter_id="C5",
            chapter_number=5,
            title="Energy Profile & Normative Constraints",
            audience="technical",
            section_type="body",
            epistemic_marker="HYPOTHESIS | REQUIRES_VALIDATION",
            llm_text=llm_c5,
            llm_text_en=llm_c5_en,
            llm_text_es=llm_c5_es,
            block_id="b_energy",
            content=c5,
        ))

        # ── C6: Tension Map ────────────────────────────────────────────────────
        c6: list[str] = [
            _sep("="),
            "TENSION MAP -- MATERIAL FRICTIONS REQUIRING TRADE-OFFS",
            _sep("="),
            "",
            "A TENSION is a probable friction between elements of the case.",
            "Unlike conflicts, tensions do not constitute hard contradictions.",
            "They complicate advancement and generate structured validation requirements.",
            "",
        ]
        tensions_from_records = [
            r for r in inference_records if r.get("claim_family") == "tension"
        ]
        if not tensions_from_records:
            c6.append("  No material tensions activated in this analysis run.")
        else:
            for i, t in enumerate(
                sorted(
                    tensions_from_records,
                    key=lambda x: x.get("validation_urgency_score", 0),
                    reverse=True,
                ),
                1,
            ):
                c6 += [
                    _sep("-"),
                    f"  TENSION {i} -- [{t['case_id']}]  {t['case_name']}",
                    _sep("-"),
                    "",
                    f"  P={t.get('plausibility_score',0):.2f}  R={t.get('decision_relevance_score',0):.2f}  V={t.get('validation_urgency_score',0):.2f}  [{_urgency_label(t.get('validation_urgency_score',0))}]",
                    "",
                    "  TENSION STATEMENT:",
                ]
                c6 += _wrap_text(t.get("conditional_statement", ""))
                c6 += ["", "  INFERENCE LOGIC:"]
                c6 += _wrap_text(t.get("inference_logic", ""))
                c6 += ["", "  DEPENDENCY ASSUMPTIONS:"]
                for j, dep in enumerate(t.get("dependency_assumptions", []), 1):
                    c6.append(f"    {j}. {dep}")
                c6 += [
                    "",
                    "  VALIDATION REQUIREMENT:",
                    f"    {t.get('validation_requirement','')}",
                    "",
                ]

        sections.append(_section(
            sid="c6_tension_map",
            chapter_id="C6",
            chapter_number=6,
            title="Tension Map",
            audience="technical",
            section_type="body",
            epistemic_marker="INFERRED",
            llm_text=llm_lookup.get("s06_tensions_narrative", ""),
            llm_text_en=llm_lookup_en.get("s06_tensions_narrative", ""),
            llm_text_es=llm_lookup_es.get("s06_tensions_narrative", ""),
            block_id="b_tensions",
            content=c6,
        ))

        # ── C7: Validation Architecture ────────────────────────────────────────
        c7: list[str] = [
            _sep("="),
            "VALIDATION ARCHITECTURE -- PRIORITIZED EVIDENCE REQUIREMENTS",
            _sep("="),
            "",
            "Items ordered by Validation Urgency Score (highest first).",
            "Each item identifies what data is needed and which cases it resolves.",
            "",
            _sep("-"),
        ]
        for item in validation_queue:
            rec = next(
                (r for r in inference_records if r["case_id"] == item.get("case_id", "")),
                {},
            )
            c7 += [
                "",
                f"  PRIORITY {item['queue_position']}  [{item['case_id']}]  {item['case_name']}",
                f"  {_sep('=', 60)}",
                f"  Claim Family       : {_family_label(item.get('claim_family',''))}",
                f"  Validation Urgency : {item.get('validation_urgency_score',0):.2f}  [{_urgency_label(item.get('validation_urgency_score',0))}]",
                f"  Decision Relevance : {item.get('decision_relevance_score',0):.2f}",
                "",
                "  EVIDENCE REQUIRED:",
                f"    {item.get('validation_requirement','')}",
                "",
            ]
            if rec:
                c7 += [
                    "  IF CONFIRMED   : Case hypothesis eligible for upgrade to Verification-grade.",
                    "  IF DENIED      : Inference case retired or reclassified. Downstream weight adjusted.",
                    "",
                ]
            c7.append(_sep("-"))

        if evidence_gap_register:
            c7 += [
                "",
                _sep("-"),
                "EVIDENCE GAP REGISTER",
                _sep("-"),
                "",
            ]
            for g in evidence_gap_register:
                c7 += [
                    f"  [{g['gap_id']}]  {g['description']}",
                    f"  Epistemic Impact: {g.get('epistemic_impact', g.get('acquisition_impact',''))}",
                    f"  Blocking Cases : {', '.join(g.get('blocking_inference_cases',[]))}",
                    f"  Urgency        : {g.get('validation_urgency_score',0):.2f}",
                    "",
                ]

        # TAD Preliminary injection (from motor_033)
        if tad_actions:
            c7 += [
                "",
                _sep("="),
                "TECHNICAL ASSESSMENT DOCUMENT (TAD) — PRELIMINARY",
                _sep("="),
                "",
                "Information-value ordering: actions ranked by decision impact per validation effort.",
                "Each action identifies the epistemic state that becomes accessible upon completion.",
                "",
            ]
            if tad_deficit is not None:
                c7 += [
                    f"  Information Deficit Score : {tad_deficit:.2f}",
                    f"  (0.0 = fully resolved  |  1.0 = maximal epistemic gap)",
                    "",
                ]
            if tad_posture_summary:
                c7 += [
                    "  POSTURE SUMMARY:",
                    f"    validation_first        : {tad_posture_summary.get('validation_first', 0)}",
                    f"    investigate_then_decide : {tad_posture_summary.get('investigate_then_decide', 0)}",
                    f"    bounded_candidate_action: {tad_posture_summary.get('bounded_candidate_action', 0)}",
                    f"    defer                   : {tad_posture_summary.get('defer', 0)}",
                    "",
                ]
            if tad_frontier:
                c7 += [
                    "  DECISION FRONTIER (current):",
                    f"  {tad_frontier}",
                    "",
                ]
            c7 += [_sep("-"), "ORDERED ACTION PLAN", _sep("-"), ""]
            for act in tad_actions:
                c7 += [
                    f"  TAD-{act.get('rank', '?')}  [{act.get('case_id','')}]  {act.get('action_title','')}",
                    f"  VoI Score      : {act.get('voi_score', 0):.3f}",
                    f"  Action Family  : {act.get('action_family','')}",
                    f"  Posture        : {act.get('recommended_posture','')}",
                    f"  Burden Level   : {act.get('burden_level','')}",
                    f"  Downside       : {act.get('downside_profile','')}",
                    f"  Irreversibility: {act.get('irreversibility_profile','')}",
                    f"  Decision unlock: {act.get('decision_unlock','')}",
                    f"  Evidence needed: {act.get('evidence_needed','')}",
                    f"  Effort tier    : {act.get('effort_tier','')}",
                    f"  No-Go Condition: {act.get('no_go_condition','')}",
                    "",
                ]

        sections.append(_section(
            sid="c7_validation_architecture",
            chapter_id="C7",
            chapter_number=7,
            title="Validation Architecture",
            audience="technical",
            section_type="body",
            epistemic_marker="REQUIRES_VALIDATION",
            llm_text=llm_lookup.get("s04_validation_narrative", ""),
            llm_text_en=llm_lookup_en.get("s04_validation_narrative", ""),
            llm_text_es=llm_lookup_es.get("s04_validation_narrative", ""),
            block_id="b_validation",
            content=c7,
        ))

        # ── C8: Conditional Opportunities ──────────────────────────────────────
        c8: list[str] = [
            _sep("="),
            "CONDITIONAL OPPORTUNITY PATHWAYS",
            _sep("="),
            "",
            "These are value-creation or risk-mitigation pathways plausible given",
            "the current asset-context prior and active inference cases. NOT recommendations.",
            "Each pathway is conditional on specific field validation requirements.",
            "",
        ]
        display_opportunity_candidates = list(opportunity_candidates or []) or list(
            structural_executive_summary.get("conditional_opportunity_pathways", []) or []
        )
        for o in display_opportunity_candidates:
            c8 += [
                _sep("-"),
                f"  [{o['opportunity_id']}]  {o['opportunity_name']}",
                _sep("-"),
                "",
                f"  Type: {o.get('opportunity_type','').replace('_',' ').title()}",
                f"  P={o.get('plausibility_score',0):.2f}  R={o.get('decision_relevance_score',0):.2f}  V={o.get('validation_urgency_score',0):.2f}",
                "",
                "  CONDITIONAL STATEMENT:",
            ]
            c8 += _wrap_text(o.get("conditional_statement", ""))
            c8 += ["", "  KEY DEPENDENCIES:"]
            for j, dep in enumerate(o.get("dependency_assumptions", []), 1):
                c8.append(f"    {j}. {dep}")
            c8 += [
                "",
                "  VALIDATION REQUIRED:",
                f"    {o.get('validation_requirement','')}",
                "",
            ]

        sections.append(_section(
            sid="c8_conditional_opportunities",
            chapter_id="C8",
            chapter_number=8,
            title="Conditional Opportunities",
            audience="executive",
            section_type="body",
            epistemic_marker="CONDITIONAL",
            llm_text=llm_lookup.get("s08_opportunities_narrative", ""),
            llm_text_en=llm_lookup_en.get("s08_opportunities_narrative", ""),
            llm_text_es=llm_lookup_es.get("s08_opportunities_narrative", ""),
            block_id="b_opps",
            content=c8,
        ))

        # ── C9: Financial Context (subordinated) ───────────────────────────────
        finance_as_appendix = weak_asset_identity or runtime_asset_context_readiness in {
            "issuer_context_only",
            "location_only",
            "asset_context_insufficient",
            "asset_context_minimal",
        }
        c9: list[str] = [
            _sep("="),
            "ISSUER-LEVEL FINANCIAL CONTEXT -- SUBORDINATED",
            _sep("="),
            "",
            f"NOTE: All figures below are consolidated {company_name} ({ticker})",
            "data from SEC EDGAR XBRL. They represent company-level context, not necessarily asset-specific",
            "segment data. Asset-specific financials require local scope confirmation or footnote analysis.",
            f"This section is subordinated context -- the analytical axis of this {document_label}",
            "is asset understanding, not financial underwriting.",
            "",
            f"  Data Source        : SEC EDGAR XBRL -- {company_name} (CIK {owner_cik})",
            f"  Filing Reference   : {filing_date}",
            f"  Data Quality Gate  : {'PASSED' if quality_gate else 'NOT PASSED'}",
            "",
            _sep("-"),
            "FINANCIAL READINESS",
            _sep("-"),
            "",
            f"  Finance Readiness State : {financial_exposure_case.get('finance_readiness_state','screening_only')}",
            f"  Scope Boundary          : {financial_exposure_case.get('scope_boundary','consolidated_entity_level_only')}",
            f"  Baseline Dependency     : {financial_exposure_case.get('baseline_dependency_state','asset_specific_baseline_unavailable')}",
            f"  Tariff Basis State      : {financial_exposure_case.get('tariff_basis_state','unavailable')}",
            f"  Cost Basis State        : {financial_exposure_case.get('cost_basis_state','unavailable')}",
            f"  Bankability Posture     : {financial_exposure_case.get('bankability_posture','not_bankable_in_current_state')}",
            "",
            "  Allowed Use:",
            "    Consolidated scale context, leverage ambiguity mapping, and value-of-information framing only.",
            "  Not Admissible Yet:",
            "    Asset NOI, payback, IRR, NPV, DSCR, or bankability claims.",
            "",
            _sep("-"),
            "INCOME STATEMENT",
            _sep("-"),
            "",
            f"  Total Revenue (Annual)  : {_fmt_usd(revenues)}",
            f"  Operating Income        : {_fmt_usd(operating_income)}",
            f"  Net Income              : {_fmt_usd(net_income)}",
            "",
            _sep("-"),
            "BALANCE SHEET",
            _sep("-"),
            "",
            f"  Total Assets            : {_fmt_usd(total_assets)}",
            f"  Total Debt (XBRL)       : {_fmt_usd(total_debt)}",
            f"  Shares Outstanding      : {(lambda s: f'{s:,}' if s else 'NOT OBSERVED')(financials.get('shares_outstanding'))}",
            "",
            "  LEVERAGE AMBIGUITY NOTE:",
            "  Any leverage-dependent reading remains bounded until debt scope is reconciled.",
            f"  Public Debt Signal      : {_fmt_usd(financial_exposure_case.get('public_debt_signal'))}",
            f"  Public Signal Basis     : {financial_exposure_case.get('public_debt_signal_label') or 'not available'}",
            "  See C3 (Blocking Conflicts) for the active debt-scope conflict when present.",
            "",
            _sep("-"),
            "HISTORICAL REVENUE TREND",
            _sep("-"),
            "",
        ]
        if revenues_series:
            max_rev = max(e["val"] for e in revenues_series) if revenues_series else 1
            for entry in revenues_series:
                bar_width = int(round(entry["val"] / max_rev * 30))
                bar = "[" + "#" * bar_width + "-" * (30 - bar_width) + "]"
                c9.append(f"  {entry['end'][:4]}:  {_fmt_usd(entry['val']):>10}  {bar}")
        else:
            c9.append("  Revenue trend series not available.")
        c9 += [
            "",
            "  Interpretation context: These figures describe owner-level scale and balance-sheet context.",
            "  They do not resolve asset identity, system behavior, or building-level economics.",
            "",
            _sep("-"),
            "HARDENING REQUIREMENTS",
            _sep("-"),
            "",
        ]
        for req in financial_exposure_case.get("hardening_requirements", []):
            c9.append(f"  - {req}")

        sections.append(_section(
            sid="c9_financial_context",
            chapter_id="A4" if finance_as_appendix else "C9",
            chapter_number=4 if finance_as_appendix else 9,
            title="Issuer Financial Context (Subordinated)" if finance_as_appendix else "Financial Context",
            audience="technical",
            section_type="appendix" if finance_as_appendix else "body",
            epistemic_marker="DIRECT_EVIDENCE | CONSOLIDATED_ONLY",
            llm_text=llm_lookup.get("s03_financial_narrative", ""),
            llm_text_en=llm_lookup_en.get("s03_financial_narrative", ""),
            llm_text_es=llm_lookup_es.get("s03_financial_narrative", ""),
            block_id="b_fin",
            content=c9,
            chart_ref=_section_chart_map.get("c9_financial_context", ""),
        ))

        a0: list[str] = [
            _sep("="),
            "GOVERNANCE STATUS — PROVISIONAL OUTPUT CEILING",
            _sep("="),
            "",
            f"  Epistemic Grade        : {governance_summary.get('epistemic_grade','Decision-grade')}",
            f"  Publication Ceiling    : {governance_summary.get('publication_ceiling','publish_bounded').replace('_',' ')}",
            f"  Traceability Complete  : {'yes' if governance_summary.get('traceability_chain_complete') else 'no'}",
            f"  Blocking Conflicts     : {governance_summary.get('blocking_conflicts', 0)}",
            f"  Stubs Active           : {governance_summary.get('stubs_active', 0)}",
            f"  LLM Layer Available    : {'yes' if governance_summary.get('llm_available') else 'no'}",
            f"  Charts Available       : {governance_summary.get('chart_assets_available', 0)}",
            f"  Chart Errors           : {governance_summary.get('chart_errors_count', 0)}",
            f"  Maturity Counts        : {' | '.join(f'{level}={count}' for level, count in (governance_summary.get('evidence_maturity_summary', {}).get('counts_by_level', {}) or {}).items()) or 'not available'}",
            f"  Blocked Claim Classes  : {governance_summary.get('evidence_maturity_summary', {}).get('blocked_claim_count', 0)}",
            "",
            _sep("-"),
            "FRAMEWORK CONSTRAINT",
            _sep("-"),
            "",
        ]
        a0 += _wrap_text(governance_summary.get("framework_constraint", ""))
        maturity_summary_block = governance_summary.get("evidence_maturity_summary", {}) if isinstance(governance_summary.get("evidence_maturity_summary", {}), dict) else {}
        if maturity_summary_block:
            a0 += ["", _sep("-"), "EVIDENCE MATURITY CEILING", _sep("-"), ""]
            readiness_reason = str(maturity_summary_block.get("report_readiness_reason", "") or "").strip()
            if readiness_reason:
                a0 += _wrap_text(readiness_reason)
                a0.append("")
            allowed_report_types = maturity_summary_block.get("report_type_allowed", []) or []
            prohibited_report_types = maturity_summary_block.get("report_type_prohibited", []) or []
            a0.append(
                "  Allowed Report Types  : "
                + (", ".join(str(item) for item in allowed_report_types) if allowed_report_types else "not declared")
            )
            a0.append(
                "  Prohibited Types      : "
                + (", ".join(str(item) for item in prohibited_report_types) if prohibited_report_types else "none declared")
            )
            bottlenecks = list(maturity_summary_block.get("key_variable_bottlenecks", []) or [])
            if bottlenecks:
                a0.append("  Key Bottlenecks       : " + ", ".join(str(item) for item in bottlenecks[:6]))
            claim_summary = maturity_summary_block.get("claim_permission_summary", {}) or {}
            if claim_summary:
                a0.append(
                    "  Claim Permissions     : "
                    f"{claim_summary.get('allowed_count', 0)} allowed / "
                    f"{claim_summary.get('conditional_count', 0)} conditional / "
                    f"{claim_summary.get('prohibited_count', 0)} prohibited"
                )
            a0.append("")
        a0 += ["", _sep("-"), "DOWNGRADE TRIGGERS", _sep("-"), ""]
        if governance_summary.get("downgrade_triggers"):
            for trigger in governance_summary.get("downgrade_triggers", []):
                a0.append(f"  - {trigger}")
        else:
            a0.append("  - No active downgrade triggers in provisional report packaging state.")
        a0.append("")

        sections.append(_section(
            sid="a0_governance_status",
            chapter_id="A0",
            chapter_number=0,
            title="Governance Status",
            audience="technical",
            section_type="appendix",
            epistemic_marker="DECISION_GRADE",
            llm_text="",
            block_id="b_governance",
            content=a0,
        ))

        adaptation_lines: list[str] = [
            _sep("="),
            "CASE ADAPTATION MEMO",
            _sep("="),
            "",
        ]
        for row in case_adaptation_memo.get("rows", []):
            adaptation_lines += [
                f"  Dimension        : {row.get('dimension','')}",
                f"  Case Finding     : {row.get('case_specific_finding','')}",
                f"  Report Change    : {row.get('how_it_changes_the_report','')}",
                "",
            ]
        comparison_summary = dict(case_adaptation_memo.get("comparison_summary", {}) or {})
        if comparison_summary:
            adaptation_lines += [
                f"  Comparable References : {comparison_summary.get('reference_count', 0)}",
                f"  Closest Reference     : {comparison_summary.get('closest_reference_key', 'NONE') or 'NONE'}",
                f"  Difference Count      : {comparison_summary.get('closest_reference_difference_count', 0)}",
                f"  Divergence Dimensions : {', '.join(comparison_summary.get('closest_reference_differences', []) or []) or 'NONE'}",
                "",
            ]
        if case_adaptation_memo.get("template_contamination_failure"):
            adaptation_lines += [
                "  TEMPLATE CONTAMINATION FAILURE: YES",
                "  Failure Reasons:",
            ]
            for reason in case_adaptation_memo.get("failure_reasons", []):
                adaptation_lines.append(f"    - {reason}")
            adaptation_lines.append("")
        else:
            adaptation_lines += [
                "  TEMPLATE CONTAMINATION FAILURE: NO",
                "",
            ]

        sections.append(_section(
            sid="a0_case_adaptation_memo",
            chapter_id="A0A",
            chapter_number=0,
            title="Case Adaptation Memo",
            audience="technical",
            section_type="appendix",
            epistemic_marker="DECISION_GRADE",
            llm_text="",
            block_id="b_case_adaptation",
            content=adaptation_lines,
        ))

        # ── A1: Evidence & Source Traceability ─────────────────────────────────
        evidence_rows = evidence_block.get("evidence_rows", [])
        sources_used  = caption_block.get("sources_used", [])
        bench_limits  = caption_block.get("benchmark_limitations", [])

        a1: list[str] = [
            _sep("="),
            "EVIDENCE AND SOURCE TRACEABILITY",
            _sep("="),
            "",
            "Full evidence map for each activated inference case.",
            "",
            _sep("-"),
            "EVIDENCE QUALITY LEGEND",
            _sep("-"),
            "",
            "  confirmed_public   : Directly supported by SEC filing, regulatory text, or public record.",
            "  plausible_inferred : Supported by public signals and domain logic. Not verified.",
            "  benchmark_only     : Sectoral benchmark alone. Requires site data.",
            "",
            _sep("-"),
            "CASE EVIDENCE MAP",
            _sep("-"),
            "",
        ]
        for row in evidence_rows:
            a1 += [
                f"  [{row.get('case_id','')}]  {row.get('case_name','')}",
                f"  Evidence Quality   : {row.get('evidence_quality','').replace('_',' ').title()}",
                f"  Source Types       : {', '.join(row.get('evidence_source_types',[]))}",
                f"  Base Support       : {', '.join(row.get('base_support_traces',[]))}",
                "  Key Assumptions:",
            ]
            for dep in row.get("dependency_assumptions", [])[:3]:
                a1.append(f"    - {dep}")
            a1.append("")

        a1 += [_sep("-"), "SOURCES USED", _sep("-"), ""]
        for src in sources_used:
            a1 += [
                f"  [{src.get('source_id','')}]",
                f"  Description  : {src.get('description','')}",
                f"  Authority    : {src.get('authority_class','').replace('_',' ').title()}",
                f"  Used For     : {src.get('used_for','')}",
                "",
            ]

        a1 += [_sep("-"), "BENCHMARK LIMITATIONS", _sep("-"), ""]
        for lim in bench_limits:
            a1.append(f"  - {lim}")
        a1.append("")

        sections.append(_section(
            sid="a1_evidence_traceability",
            chapter_id="A1",
            chapter_number=1,
            title="Evidence & Source Traceability",
            audience="technical",
            section_type="appendix",
            epistemic_marker="DIRECT_EVIDENCE",
            llm_text="",
            block_id="b_evidence",
            content=a1,
        ))

        # ── A2: Asset Context Prior and Raw Source Map ────────────────────────
        a2: list[str] = [
            _sep("="),
            "ASSET CONTEXT PRIOR AND RAW SOURCE MAP",
            _sep("="),
            "",
            "This appendix shows the structured prior and the source-routing state that",
            "support the governed asset brief. Every assumption is explicit. Every unknown",
            "is stated, not filled with plausible-sounding narrative.",
            "",
            _sep("-"),
            "SOURCE ROUTING STATUS",
            _sep("-"),
            "",
            f"  Route Class            : {benchmark_routing_register.get('route_class', 'NOT OBSERVED')}",
            f"  Selected Source Type   : {benchmark_routing_register.get('selected_source_type', 'NOT OBSERVED')}",
            f"  Selected Source Family : {benchmark_routing_register.get('source_family_selected', 'NOT OBSERVED')}",
            f"  Scope Boundary         : {benchmark_routing_register.get('scope_boundary', 'NOT OBSERVED')}",
            f"  Jurisdiction           : {', '.join(benchmark_routing_register.get('jurisdiction', [])) or 'NOT OBSERVED'}",
            f"  Dominant Asset Scopes  : {', '.join(source_scope_register.get('dominant_asset_scopes', [])) or 'NOT OBSERVED'}",
            f"  Issuer Context Found   : {'yes' if source_scope_register.get('issuer_context_found') else 'no'}",
            "",
            _sep("-"),
            "PRIOR ASSUMPTIONS PACK",
            _sep("-"),
            "",
        ]
        for pa in fp_assumptions:
            a2 += [
                f"  [{pa.get('assumption_id','')}]",
                f"  Assumption   : {pa.get('assumption','')}",
                f"  Basis        : {pa.get('basis','')}",
                f"  Risk if Wrong: {pa.get('risk_if_wrong','')}",
                "",
            ]

        a2 += [
            _sep("-"),
            "UNCERTAINTY MARKERS",
            _sep("-"),
            "",
            "Dimensions that cannot be resolved from available public sources.",
            "These are analytical boundaries, not analytical failures.",
            "",
        ]
        for um in fp_uncertainty:
            a2 += [
                f"  [{um.get('marker_id','')}]  {um.get('dimension','').replace('_',' ').title()}",
                f"  Description    : {um.get('description','')}",
                f"  Impact         : {um.get('impact','')}",
                f"  Resolution Path: {um.get('resolution_path','')}",
                "",
            ]

        a2 += [
            _sep("-"),
            "OPERATIONAL TENSION HYPOTHESES",
            _sep("-"),
            "",
        ]
        for t in fp_tensions:
            a2 += [
                f"  [{t.get('tension_id','')}]  {t.get('tension_type','').replace('_',' ').title()}",
                f"  {t.get('description','')}",
                f"  Elements   : {', '.join(t.get('elements_in_tension',[]))}",
                f"  Validation : {t.get('validation_requirement','')}",
                "",
            ]

        a2 += [
            _sep("-"),
            "REQUESTABLE EVIDENCE ITEMS ALREADY DERIVED",
            _sep("-"),
            "",
        ]
        for item in requestable_evidence_items[:8]:
            a2 += [
                f"  Evidence Item : {item.get('evidence_item', '')}",
                f"  Source        : {item.get('source', '')}",
                f"  Why Needed    : {item.get('why_needed', '')}",
                f"  Unlocks       : {item.get('decision_unlock', '')}",
                "",
            ]

        sections.append(_section(
            sid="a2_asset_context_prior",
            chapter_id="A2",
            chapter_number=2,
            title="Asset Context Prior and Raw Source Map",
            audience="technical",
            section_type="appendix",
            epistemic_marker="HYPOTHESIS",
            llm_text="",
            block_id="b_prior",
            content=a2,
        ))

        # ── A3: Detailed Validation Questions ─────────────────────────────────
        a3: list[str] = [
            _sep("="),
            "DETAILED VALIDATION QUESTIONS",
            _sep("="),
            "",
            "These questions represent the highest-value information requests for",
            "resolving current analytical blockers. Ordered by urgency and decision impact.",
            "Each question targets a specific inference case and identifies the data source,",
            "decision implication, and path to claim upgrade.",
            "",
        ]
        for q in next_best_questions:
            urgency = q.get("urgency", "").upper()
            a3 += [
                _sep("-"),
                f"  [{q['question_id']}]  URGENCY: {urgency}",
                _sep("-"),
                "",
                "  QUESTION:",
                f"    {q['question']}",
                "",
                f"  Linked Case            : {q.get('linked_case','')}",
                "",
                "  WHY IT MATTERS:",
                f"    {q.get('why_it_matters','')}",
                "",
                "  HOW TO ANSWER:",
                f"    {q.get('how_to_answer','')}",
                "",
            ]

        sections.append(_section(
            sid="a3_priority_questions",
            chapter_id="A3",
            chapter_number=3,
            title="Detailed Validation Questions",
            audience="executive",
            section_type="appendix",
            epistemic_marker="REQUIRES_VALIDATION",
            llm_text=llm_lookup.get("s11_questions_narrative", ""),
            llm_text_en=llm_lookup_en.get("s11_questions_narrative", ""),
            llm_text_es=llm_lookup_es.get("s11_questions_narrative", ""),
            block_id="b_questions",
            content=a3,
        ))

        # ── A5: Evidence Maturity Matrix ─────────────────────────────────────
        a5: list[str] = [
            _sep("="),
            "EVIDENCE MATURITY & CLAIM PERMISSION MATRIX",
            _sep("="),
            "",
            "REPORT READINESS",
            _sep("-"),
            f"  Allowed Report Types   : {', '.join(report_readiness_register.get('report_type_allowed', [])) or 'NOT OBSERVED'}",
            f"  Prohibited Report Types: {', '.join(report_readiness_register.get('report_type_prohibited', [])) or 'NOT OBSERVED'}",
            f"  Readiness Reason       : {report_readiness_register.get('reason', 'NOT OBSERVED')}",
            "",
            "VARIABLE MATURITY REGISTER",
            _sep("-"),
            "",
        ]
        if not variable_maturity_register:
            a5 += ["  No variable maturity records were produced.", ""]
        for row in variable_maturity_register[:20]:
            allowed_outputs = ", ".join(row.get("allowed_outputs", []) or []) or "NONE"
            prohibited_outputs = ", ".join(row.get("prohibited_outputs", []) or []) or "NONE"
            unlocked = ", ".join(row.get("decisions_unlocked", []) or []) or "NONE"
            a5 += [
                f"  Variable           : {row.get('variable_name', '')}",
                f"  Family             : {row.get('variable_family', '')}",
                f"  Level              : {row.get('maturity_level', '')}",
                f"  Source Scope       : {row.get('source_scope', '')}",
                f"  Evidence Source    : {row.get('evidence_source', '')}",
                f"  Authority          : {row.get('authority_score', '')}",
                f"  Uncertainty Reason : {row.get('uncertainty_reason', '')}",
                f"  Allowed Outputs    : {allowed_outputs}",
                f"  Forbidden Outputs  : {prohibited_outputs}",
                f"  Decisions Unlocked : {unlocked}",
                "",
            ]

        a5 += [
            "CLAIM PERMISSION REGISTER",
            _sep("-"),
            "",
        ]
        if not claim_permission_register:
            a5 += ["  No claim permission records were produced.", ""]
        for row in claim_permission_register[:20]:
            upgrade_path = "; ".join(row.get("upgrade_path", []) or []) or "NONE"
            a5 += [
                f"  Claim              : {row.get('claim_name', '')}",
                f"  Permission         : {row.get('current_permission', '')}",
                f"  Reason If Blocked  : {row.get('reason_if_blocked', '') or 'NOT BLOCKED'}",
                f"  Upgrade Path       : {upgrade_path}",
                "",
            ]

        a5 += [
            "DECISION PERMISSION REGISTER",
            _sep("-"),
            "",
        ]
        if not decision_permission_register:
            a5 += ["  No decision permission records were produced.", ""]
        for row in decision_permission_register[:20]:
            evidence_needed = "; ".join(row.get("evidence_needed", []) or []) or "NONE"
            a5 += [
                f"  Decision           : {row.get('decision_name', '')}",
                f"  Admissibility      : {row.get('admissibility_state', '')}",
                f"  Variable Bottleneck: {row.get('current_variable_bottleneck', '')}",
                f"  Allowed Action     : {row.get('allowed_action', '')}",
                f"  Evidence Needed    : {evidence_needed}",
                "",
            ]

        sections.append(_section(
            sid="a5_evidence_maturity_matrix",
            chapter_id="A5",
            chapter_number=5,
            title="Evidence Maturity & Claim Permission Matrix",
            audience="technical",
            section_type="appendix",
            epistemic_marker="GOVERNED_REGISTER",
            llm_text="",
            block_id="b_evidence_maturity_matrix",
            content=a5,
        ))

        a6: list[str] = [
            _sep("="),
            "PUBLIC SOURCE COVERAGE TABLE",
            _sep("="),
            "",
            "This appendix shows exactly which routed public source families were queried,",
            "what they actually supported, and what remains missing at the asset level.",
            "",
        ]
        if not source_family_coverage_table:
            a6 += ["  No routed public-source coverage rows were produced.", ""]
        for row in source_family_coverage_table:
            a6 += [
                f"  Source Family    : {row.get('source_family', '')}",
                f"  Source Name      : {row.get('source_name', '')}",
                f"  Queried          : {'yes' if row.get('queried') else 'no'}",
                f"  Found            : {'yes' if row.get('found') else 'no'}",
                f"  Authority        : {row.get('authority', '')}",
                f"  Scope            : {row.get('scope', '')}",
                f"  Fields Extracted : {', '.join(row.get('fields_extracted', []) or []) or 'NONE'}",
                f"  Missing          : {', '.join(row.get('missing', []) or []) or 'NONE'}",
                f"  Support Note     : {row.get('support_note', '')}",
                "",
            ]

        sections.append(_section(
            sid="a6_public_source_coverage",
            chapter_id="A6",
            chapter_number=6,
            title="Public Source Coverage Table",
            audience="technical",
            section_type="appendix",
            epistemic_marker="GOVERNED_REGISTER",
            llm_text="",
            block_id="b_public_source_coverage",
            content=a6,
        ))

        a7: list[str] = [
            _sep("="),
            "REPORT TYPE CLASSIFIER TABLE",
            _sep("="),
            "",
        ]
        if not report_type_classifier_table:
            a7 += ["  No report-type classifier rows were produced.", ""]
        for row in report_type_classifier_table:
            a7 += [
                f"  Asset                : {row.get('asset', '')}",
                f"  Recommended Report   : {row.get('recommended_report_type', '')}",
                f"  Why                  : {row.get('why', '')}",
                f"  Allowed Claims       : {', '.join(row.get('allowed_claims', []) or []) or 'NONE'}",
                f"  Blocked Claims       : {', '.join(row.get('blocked_claims', []) or []) or 'NONE'}",
                "",
            ]

        sections.append(_section(
            sid="a7_report_type_classifier",
            chapter_id="A7",
            chapter_number=7,
            title="Report Type Classifier Table",
            audience="technical",
            section_type="appendix",
            epistemic_marker="GOVERNED_REGISTER",
            llm_text="",
            block_id="b_report_type_classifier",
            content=a7,
        ))

        a8: list[str] = [
            _sep("="),
            "INDUSTRY ADAPTATION TABLE",
            _sep("="),
            "",
        ]
        if not industry_adaptation_table:
            a8 += ["  No industry adaptation rows were produced.", ""]
        for row in industry_adaptation_table:
            a8 += [
                f"  Asset Type           : {row.get('asset_type', '')}",
                f"  Activated Logic      : {row.get('activated_industry_logic', '')}",
                f"  Specific Data Needs  : {', '.join(row.get('specific_data_needs', []) or []) or 'NONE'}",
                f"  Specific Risks       : {', '.join(row.get('specific_risks', []) or []) or 'NONE'}",
                "",
            ]

        sections.append(_section(
            sid="a8_industry_adaptation",
            chapter_id="A8",
            chapter_number=8,
            title="Industry Adaptation Table",
            audience="technical",
            section_type="appendix",
            epistemic_marker="GOVERNED_REGISTER",
            llm_text="",
            block_id="b_industry_adaptation",
            content=a8,
        ))
        sections.extend(_build_structural_intelligence_appendices(structural_intelligence_registers))

        canonical_output_mode = canonicalize_output_mode(document_label or runtime_report_identity_state)
        structural_first_default_active = (
            str(structural_executive_summary.get("default_reasoning_path", "")).strip() == "structural_first"
            and bool(structural_executive_summary.get("problem_frame_active", False))
            and canonical_output_mode != "Target Classification Brief"
        )
        structural_body_sections = _build_structural_primary_body_sections(
            document_label=document_label,
            main_warning=main_warning,
            allowed_use=allowed_use,
            prohibited_use=prohibited_use,
            structural_executive_summary=structural_executive_summary,
            client_concern=concern,
            system_abstraction=system_abstraction,
            dominant_variable_register=dominant_variable_register,
            evidence_state_by_layer_register=evidence_state_by_layer_register,
            cross_layer_conflict_register=cross_layer_conflict_register,
            scenario_space=scenario_space,
            structural_financial_exposure_register=structural_financial_exposure_register,
            structural_benchmark_register=structural_benchmark_register,
            competitive_comparison_register=competitive_comparison_register,
            conditional_redesign_register=conditional_redesign_register,
            minimum_evidence_for_discrimination_register=minimum_evidence_for_discrimination_register,
            expanded_structural_tad_action_register=expanded_structural_tad_action_register,
            client_facing_tad=client_facing_tad,
            claim_contract_register=claim_contract_register,
            source_family_coverage_table=source_family_coverage_table,
            problem_framing_register=problem_framing_register,
            llm_lookup=llm_lookup,
            llm_lookup_en=llm_lookup_en,
            llm_lookup_es=llm_lookup_es,
        )

        if _is_blocked_report_class(runtime_report_identity_state):
            legacy_body_sections = _build_decision_admissibility_sections(
                output_blocks,
                governance_summary,
                llm_lookup,
                llm_lookup_en,
                llm_lookup_es,
                conflict_register,
                validation_queue,
                tad_prelim,
                financial_exposure_case,
                comp_case,
                document_label,
                main_warning,
                allowed_use,
                prohibited_use,
                structural_executive_summary,
            )
            appendix_sections = [
                s
                for s in sections
                if s.get("section_type") == "appendix"
                and s.get("section_id") != "c9_financial_context"
            ]
            body_sections = (
                _merge_structural_first_body_sections(legacy_body_sections, structural_body_sections)
                if structural_first_default_active
                else legacy_body_sections
            )
        elif _is_structural_primary_output_type(runtime_report_identity_state):
            appendix_sections = [s for s in sections if s.get("section_type") == "appendix"]
            body_sections = structural_body_sections
        elif structural_first_default_active:
            legacy_body_sections = [s for s in sections if s.get("section_type") == "body"]
            appendix_sections = [s for s in sections if s.get("section_type") == "appendix"]
            body_sections = _merge_structural_first_body_sections(legacy_body_sections, structural_body_sections)
        else:
            body_sections = [s for s in sections if s.get("section_type") == "body"]
            appendix_sections = [s for s in sections if s.get("section_type") == "appendix"]

        if main_report_outline and canonical_output_mode not in {"Target Classification Brief", "Decision-Blocked Asset Brief"}:
            body_sections = _compose_client_facing_body_sections(
                main_report_outline=main_report_outline,
                executive_thesis=executive_thesis,
                client_facing_tad=client_facing_tad,
                problem_framing_register=problem_framing_register,
                system_abstraction=system_abstraction,
                cross_layer_conflict_register=cross_layer_conflict_register,
                claim_contract_register=claim_contract_register,
            )

        if main_report_outline and canonical_output_mode != "Decision-Blocked Asset Brief":
            body_sections = _prioritize_body_sections_by_outline(body_sections, main_report_outline)
        body_sections, appendix_sections = _demote_legacy_duplicate_sections(
            body_sections,
            appendix_sections,
            structural_first_default_active=structural_first_default_active,
            main_report_outline=main_report_outline,
        )
        appendix_sections = _disambiguate_appendix_titles_against_body(
            body_sections,
            appendix_sections,
        )

        selected_asset_family = str(
            m49.get(
                "selected_asset_family",
                runtime_target_definition.get("target_type", ""),
            )
            or ""
        ).strip()
        support_chart_visibility_policy = get_support_chart_visibility_policy(
            canonical_output_mode,
            selected_asset_family,
        )
        support_chart_lane_visibility_policy = get_support_chart_lane_visibility_policy(
            canonical_output_mode,
        )
        support_chart_lane_curation_policy = get_support_chart_lane_curation_policy(
            canonical_output_mode,
        )
        visible_section_ids = {
            str(sec.get("section_id", "")).strip()
            for sec in body_sections + appendix_sections
            if str(sec.get("section_id", "")).strip()
        }
        body_section_ids = {
            str(sec.get("section_id", "")).strip()
            for sec in body_sections
            if str(sec.get("section_id", "")).strip()
        }
        section_surface_map = {
            str(sec.get("section_id", "")).strip(): str(sec.get("section_type", "")).strip()
            for sec in body_sections + appendix_sections
            if str(sec.get("section_id", "")).strip()
        }
        lane_visibility_counts: dict[tuple[str, str, str], int] = {}
        resolved_section_chart_map: dict[str, str] = {}
        resolved_chart_b64_map: dict[str, str] = {}
        resolved_chart_b64_list_map: dict[str, list[str]] = {}
        resolved_chart_asset_list_map: dict[str, list[dict[str, Any]]] = {}
        chart_visibility_policy_register: list[dict[str, Any]] = []
        chart_resolution_records: list[dict[str, Any]] = []
        for original_index, ca in enumerate(chart_assets):
            original_hint = str(ca.get("section_hint", "")).strip()
            policy_entry = _resolve_chart_visibility_policy_entry(
                original_hint,
                visible_section_ids,
                support_chart_visibility_policy=support_chart_visibility_policy,
                chart_asset=ca,
            )
            resolved_hint = str(policy_entry.get("resolved_section_hint", "")).strip()
            policy_state = str(policy_entry.get("visibility_policy_state", "")).strip()
            target_hint = resolved_hint or original_hint
            if policy_state == "promoted_to_visible_support_section":
                curation_entry = _resolve_support_chart_lane_curation_entry(
                    resolved_section_hint=target_hint,
                    chart_asset=ca,
                    support_chart_lane_curation_policy=support_chart_lane_curation_policy,
                )
            else:
                curation_entry = {
                    "lane_curation_state": "not_applicable",
                    "lane_curation_rank": None,
                    "lane_curation_rule_scope": "",
                    "lane_curation_priority_source": str(
                        (support_chart_lane_curation_policy or {}).get("policy_source", "") or ""
                    ),
                }
            chart_resolution_records.append({
                "chart_asset": ca,
                "original_index": original_index,
                "original_hint": original_hint,
                "resolved_hint": resolved_hint,
                "policy_state": policy_state,
                "policy_entry": policy_entry,
                "target_hint": target_hint,
                "chart_lane": str(ca.get("chart_lane", "")).strip(),
                "lane_curation_state": str(curation_entry.get("lane_curation_state", "")).strip(),
                "lane_curation_rank": curation_entry.get("lane_curation_rank"),
                "lane_curation_rule_scope": str(curation_entry.get("lane_curation_rule_scope", "")).strip(),
                "lane_curation_priority_source": str(curation_entry.get("lane_curation_priority_source", "")).strip(),
            })
        chart_resolution_records_by_section: dict[str, list[dict[str, Any]]] = {}
        records_without_target: list[dict[str, Any]] = []
        for record in chart_resolution_records:
            target_hint = str(record.get("target_hint", "")).strip()
            if not target_hint:
                records_without_target.append(record)
                continue
            chart_resolution_records_by_section.setdefault(target_hint, []).append(record)
        ordered_chart_resolution_records: list[dict[str, Any]] = list(records_without_target)
        ordered_section_ids = [
            str(sec.get("section_id", "")).strip()
            for sec in body_sections + appendix_sections
            if str(sec.get("section_id", "")).strip()
        ]
        for section_id in ordered_section_ids:
            ordered_chart_resolution_records.extend(
                _order_section_chart_records(chart_resolution_records_by_section.get(section_id, []))
            )
        for record in ordered_chart_resolution_records:
            ca = dict(record.get("chart_asset", {}) or {})
            original_hint = str(record.get("original_hint", "")).strip()
            resolved_hint = str(record.get("resolved_hint", "")).strip()
            policy_state = str(record.get("policy_state", "")).strip()
            policy_entry = dict(record.get("policy_entry", {}) or {})
            lane_curation_state = str(record.get("lane_curation_state", "")).strip()
            lane_curation_rank = record.get("lane_curation_rank")
            lane_curation_rule_scope = str(record.get("lane_curation_rule_scope", "")).strip()
            lane_curation_priority_source = str(record.get("lane_curation_priority_source", "")).strip()
            lane_visibility_entry = _apply_support_chart_lane_visibility_cap(
                policy_state=policy_state,
                resolved_section_hint=resolved_hint or original_hint,
                chart_asset=ca,
                section_surface_map=section_surface_map,
                support_chart_lane_visibility_policy=support_chart_lane_visibility_policy,
                lane_visibility_counts=lane_visibility_counts,
            )
            chart_lane = str(ca.get("chart_lane", "")).strip()
            lane_surface_type = str(lane_visibility_entry.get("lane_visibility_surface_type", "")).strip()
            lane_limit = lane_visibility_entry.get("lane_visibility_limit")
            lane_visibility_state = str(lane_visibility_entry.get("lane_visibility_state", "")).strip()
            target_hint = str(lane_visibility_entry.get("effective_visible_section_hint", "")).strip()
            resolved_ca = dict(ca)
            resolved_ca["original_section_hint"] = original_hint
            resolved_ca["resolved_section_hint"] = target_hint
            resolved_ca["visibility_policy_state"] = policy_state
            resolved_ca["visibility_policy_rule_id"] = str(policy_entry.get("policy_rule_id", "")).strip()
            resolved_ca["visibility_policy_source"] = str(policy_entry.get("policy_source", "")).strip()
            resolved_ca["visibility_policy_note"] = str(policy_entry.get("policy_note", "")).strip()
            resolved_ca["lane_visibility_state"] = lane_visibility_state
            resolved_ca["lane_visibility_surface_type"] = lane_surface_type
            resolved_ca["lane_visibility_limit"] = lane_limit
            resolved_ca["lane_curation_state"] = lane_curation_state
            resolved_ca["lane_curation_rank"] = lane_curation_rank
            resolved_ca["lane_curation_rule_scope"] = lane_curation_rule_scope
            resolved_ca["lane_curation_priority_source"] = lane_curation_priority_source
            chart_visibility_policy_register.append({
                "asset_id": resolved_ca.get("asset_id", ""),
                "original_section_hint": original_hint,
                "resolved_section_hint": resolved_hint or original_hint,
                "effective_visible_section_hint": target_hint,
                "visibility_policy_state": policy_state,
                "policy_rule_id": str(policy_entry.get("policy_rule_id", "")).strip(),
                "policy_source": str(policy_entry.get("policy_source", "")).strip(),
                "policy_note": str(policy_entry.get("policy_note", "")).strip(),
                "chart_lane": chart_lane,
                "lane_visibility_state": lane_visibility_state,
                "lane_visibility_surface_type": lane_surface_type,
                "lane_visibility_limit": lane_limit,
                "lane_curation_state": lane_curation_state,
                "lane_curation_rank": lane_curation_rank,
                "lane_curation_rule_scope": lane_curation_rule_scope,
                "lane_curation_priority_source": lane_curation_priority_source,
            })
            if target_hint and target_hint not in resolved_section_chart_map:
                resolved_section_chart_map[target_hint] = str(resolved_ca.get("asset_id", "")).strip()
            if target_hint and target_hint not in resolved_chart_b64_map:
                resolved_chart_b64_map[target_hint] = resolved_ca.get("image_b64", "")
            if target_hint:
                resolved_chart_b64_list_map.setdefault(target_hint, []).append(resolved_ca.get("image_b64", ""))
                resolved_chart_asset_list_map.setdefault(target_hint, []).append(resolved_ca)

        (
            resolved_chart_asset_list_map,
            chart_strategic_surface_policy_register,
            chart_strategic_surface_summary,
        ) = _apply_chart_strategic_surface_gate(
            resolved_chart_asset_list_map=resolved_chart_asset_list_map,
            body_section_ids=body_section_ids,
            appendix_section_ids=[
                str(sec.get("section_id", "")).strip()
                for sec in appendix_sections
                if str(sec.get("section_id", "")).strip()
            ],
            appendix_demote_section_id=(
                str((appendix_sections[0] or {}).get("section_id", "")).strip()
                if appendix_sections
                else ""
            ),
        )
        resolved_chart_surface_section_ids = set(resolved_chart_asset_list_map.keys())
        (
            resolved_section_chart_map,
            resolved_chart_b64_map,
            resolved_chart_b64_list_map,
        ) = _rebuild_chart_surface_maps(resolved_chart_asset_list_map)

        # ── Assign chart_refs and chart_b64 from maps ─────────────────────────
        for sec in body_sections + appendix_sections:
            sid = sec.get("section_id", "")
            if sid in resolved_chart_surface_section_ids:
                sec["chart_ref"] = resolved_section_chart_map.get(sid, "")
                sec["chart_b64"] = resolved_chart_b64_map.get(sid, "")
                sec["chart_b64_list"] = resolved_chart_b64_list_map.get(sid, [])
                sec["chart_assets"] = resolved_chart_asset_list_map.get(sid, [])
            else:
                if not sec.get("chart_ref"):
                    sec["chart_ref"] = resolved_section_chart_map.get(sid, _section_chart_map.get(sid, ""))
                if not sec.get("chart_b64"):
                    sec["chart_b64"] = resolved_chart_b64_map.get(sid, _chart_b64_map.get(sid, ""))
                if not sec.get("chart_b64_list"):
                    sec["chart_b64_list"] = resolved_chart_b64_list_map.get(sid, _chart_b64_list_map.get(sid, (
                        [sec["chart_b64"]] if sec.get("chart_b64") else []
                    )))
                sec["chart_assets"] = resolved_chart_asset_list_map.get(sid, _chart_asset_list_map.get(sid, []))
            llm_section = llm_section_lookup.get(sid, {})
            sec["llm_render_mode"] = llm_section.get("render_mode", "structured_only")
            sec["llm_lint_status"] = llm_section.get("lint_status", "not_applicable")
            sec["llm_lint_violations"] = llm_section.get("lint_violations", [])
            sec["llm_section_packet"] = llm_section.get("section_packet", {})

        sections_body_ordered, sections_appendix, render_section_contract = resolve_render_section_contract(
            canonical_output_mode,
            body_sections,
            appendix_sections,
        )
        section_explanation_fallback_register = build_section_explanation_fallback_register(
            competitive_comparison_register=competitive_comparison_register,
            comparison_not_yet_valid_register=comparison_not_yet_valid_register,
            comparison_blocker_register=comparison_blocker_register,
            peer_requirement_register=peer_requirement_register,
            source_family_coverage_table=source_family_coverage_table,
            search_attempt_ledger=search_attempt_ledger,
            discovery_need_register=discovery_need_register,
            next_best_search_register=next_best_search_register,
        )
        (
            sections_body_ordered,
            sections_appendix,
            _applied_empty_policy_rows,
            _section_population_rows,
        ) = apply_empty_section_policy(
            body_sections=sections_body_ordered,
            appendix_sections=sections_appendix,
            section_explanation_fallback_register=section_explanation_fallback_register,
        )
        empty_section_policy_register = build_empty_section_policy_register(
            applied_policy_rows=_applied_empty_policy_rows,
        )
        section_population_status_register = build_section_population_status_register(
            section_population_rows=_section_population_rows,
        )
        sections_body_ordered = _sanitize_sections(sections_body_ordered)
        sections_appendix = _sanitize_sections(sections_appendix)
        if main_report_outline and canonical_output_mode not in {"Target Classification Brief", "Decision-Blocked Asset Brief"}:
            sections_body_ordered = _prioritize_body_sections_by_outline(
                sections_body_ordered,
                main_report_outline,
            )
        hard_required_body_titles = {
            str(title).strip()
            for title in list(render_section_contract.get("required_body_sections", []) or [])
            if str(title).strip()
        }
        original_required_body_sections = [
            str(title).strip()
            for title in list(render_section_contract.get("required_body_sections", []) or [])
            if str(title).strip()
        ]

        (
            sections_body_ordered,
            sections_appendix,
            section_density_surface_policy_register,
            section_density_surface_summary,
        ) = _apply_section_surface_density_gate(
            body_sections=sections_body_ordered,
            appendix_sections=sections_appendix,
            required_body_titles=hard_required_body_titles,
        )
        (
            sections_body_ordered,
            sections_appendix,
            section_strategic_surface_policy_register,
            section_strategic_surface_summary,
        ) = _apply_section_strategic_surface_gate(
            body_sections=sections_body_ordered,
            appendix_sections=sections_appendix,
            required_body_titles=hard_required_body_titles,
        )
        (
            sections_body_ordered,
            sections_appendix,
            section_redundancy_surface_policy_register,
            section_redundancy_surface_summary,
        ) = _apply_section_strategic_redundancy_gate(
            body_sections=sections_body_ordered,
            appendix_sections=sections_appendix,
            required_body_titles=hard_required_body_titles,
        )
        (
            sections_body_ordered,
            sections_appendix,
            section_inventory_surface_policy_register,
            section_inventory_surface_summary,
        ) = _apply_section_inventory_surface_gate(
            body_sections=sections_body_ordered,
            appendix_sections=sections_appendix,
            required_body_titles=hard_required_body_titles,
        )
        sections_body_ordered = _renumber_body_sections(sections_body_ordered)
        sections_appendix = _normalize_appendix_chapter_ids(sections_appendix)
        compression_state = str(main_report_outline.get("compression_state", "") or "").strip()
        client_facing_body_titles = [
            str(title).strip()
            for title in list(main_report_outline.get("body_section_titles", []) or [])
            if str(title).strip()
        ]
        planned_body_titles = (
            list(client_facing_body_titles)
            or [
                str(title).strip()
                for title in list(render_section_contract.get("body_section_titles", []) or [])
                if str(title).strip()
            ]
        )
        if compression_state == "inadmissible_bypass":
            actual_body_titles = [
                str(section.get("title", "")).strip()
                for section in sections_body_ordered
                if str(section.get("title", "")).strip()
            ]
            actual_appendix_titles = [
                str(section.get("title", "")).strip()
                for section in sections_appendix
                if str(section.get("title", "")).strip()
            ]
            render_section_contract["body_priority_titles"] = list(actual_body_titles)
            render_section_contract["body_section_titles"] = list(actual_body_titles)
            render_section_contract["required_body_sections"] = []
            render_section_contract["resolved_body_sections"] = list(actual_body_titles)
            render_section_contract["appendix_priority_titles"] = list(actual_appendix_titles)
            render_section_contract["appendix_section_titles"] = list(actual_appendix_titles)
            render_section_contract["required_appendix_sections"] = []
            render_section_contract["resolved_appendix_sections"] = list(actual_appendix_titles)
            render_section_contract["policy_note"] = (
                "Inadmissible thesis bypass: render only the sections actually packaged and "
                "do not inherit structural or legacy minimum-body requirements."
            )
        elif planned_body_titles and canonical_output_mode != "Target Classification Brief":
            actual_body_titles = [
                str(section.get("title", "")).strip()
                for section in sections_body_ordered
                if str(section.get("title", "")).strip()
            ]
            actual_appendix_titles = [
                str(section.get("title", "")).strip()
                for section in sections_appendix
                if str(section.get("title", "")).strip()
            ]
            required_body_after_surface = [
                title for title in original_required_body_sections if title in actual_body_titles
            ]
            demoted_preferred_titles = [
                title for title in planned_body_titles if title not in actual_body_titles
            ]
            render_section_contract["preferred_body_sections"] = list(planned_body_titles)
            render_section_contract["body_priority_titles"] = list(actual_body_titles)
            render_section_contract["body_section_titles"] = list(actual_body_titles)
            render_section_contract["required_body_sections"] = list(required_body_after_surface)
            render_section_contract["resolved_body_sections"] = list(actual_body_titles)
            render_section_contract["preferred_appendix_sections"] = list(
                render_section_contract.get("appendix_section_titles", []) or []
            )
            render_section_contract["resolved_appendix_sections"] = list(actual_appendix_titles)
            render_section_contract["demoted_preferred_body_sections"] = list(demoted_preferred_titles)
            if demoted_preferred_titles:
                render_section_contract["policy_note"] = (
                    "Surface governance may demote preferred body sections to appendix when they are "
                    "optional, low-novelty, or inventory-like; only hard required sections remain protected."
                )
            else:
                render_section_contract["policy_note"] = str(render_section_contract.get("policy_note", "") or "")
        sections_body_ordered, sections_appendix, section_claim_trace_register = _attach_claim_contract_traces(
            sections_body_ordered,
            sections_appendix,
            claim_contract_register,
        )
        context_integrity_scan = _content_integrity_scan(
            sections_body_ordered + sections_appendix,
            runtime_target_definition,
            company_name,
            ticker,
        )

        # ── Chart assets ───────────────────────────────────────────────────────
        case_namespace_register = build_case_namespace_register(
            target_definition=runtime_target_definition,
            case_id=case_id,
            case_title=case_title,
            document_visible_type=document_label,
        )
        chart_assets = stamp_chart_asset_case_context(
            chart_assets=chart_assets,
            case_namespace_register=case_namespace_register,
        )
        chart_case_match_register = build_chart_case_match_register(
            case_namespace_register=case_namespace_register,
            chart_assets=chart_assets,
        )
        cross_case_contamination_scan = build_cross_case_contamination_scan(
            chart_case_match_register=chart_case_match_register,
        )
        assets = [
            {**asset, "asset_id": asset.get("asset_id", asset.get("chart_id", ""))}
            for asset in chart_assets
        ]

        # ── Report package ─────────────────────────────────────────────────────
        pkg_id = "rp:" + hashlib.sha256(
            f"{case_id}:{produced_at}".encode()
        ).hexdigest()[:8]

        report_traceability = _build_report_traceability(
            pkg_id,
            traceability_register,
            decision_core_lineage,
            source_lineage,
            sections_body_ordered + sections_appendix,
            produced_at,
        )
        decision_state_en = _decision_state_text(
            target_label,
            runtime_target_admissibility_state,
            runtime_asset_context_readiness,
            runtime_missing_observable_clusters,
            runtime_recommended_report_type,
            "en",
        )
        decision_state_es = _decision_state_text(
            target_label,
            runtime_target_admissibility_state,
            runtime_asset_context_readiness,
            runtime_missing_observable_clusters,
            runtime_recommended_report_type,
            "es",
        )
        report_package = {
            "package_id":    pkg_id,
            "document_type": document_label,
            "canonical_output_mode": canonical_output_mode,
            "report_product_state": (
                "decision_admissibility"
                if _is_blocked_report_class(runtime_report_identity_state)
                else "structural_intelligence_report"
                if bool(render_section_contract.get("structural_primary", False))
                else "technical_report"
            ),
            "case_metadata": {
                "case_id":      case_id,
                "case_title":   case_title,
                "case_subtitle": case_subtitle,
                "case_subtitle_en": case_subtitle,
                "case_subtitle_es": case_subtitle_es,
                "document_internal_type": internal_document_type,
                "document_visible_type": document_label,
                "document_type_en": document_label,
                "document_type_es": _localized_document_label(
                    runtime_report_identity_state,
                    "es",
                    runtime_recommended_report_type,
                ),
                "main_warning": main_warning,
                "main_warning_en": main_warning,
                "main_warning_es": main_warning_es,
                "decision_state": decision_state_en,
                "decision_state_en": decision_state_en,
                "decision_state_es": decision_state_es,
                "allowed_use": allowed_use,
                "allowed_use_en": allowed_use,
                "allowed_use_es": allowed_use_es,
                "prohibited_use": prohibited_use,
                "prohibited_use_en": prohibited_use,
                "prohibited_use_es": prohibited_use_es,
                "organization": organization,
                "analyst":      analyst,
                "llm_model":    llm_model,
                "produced_at":  produced_at,
                "publication_ceiling": governance_summary.get("publication_ceiling", "publish_bounded"),
                "available_languages": ["en", "es"],
                "default_language": "en",
                "evidence_maturity_summary": governance_summary.get("evidence_maturity_summary", {}),
                "case_fingerprint": case_namespace_register[0].get("case_fingerprint", "") if case_namespace_register else "",
            },
            "epistemic_grade": governance_summary.get("epistemic_grade", "Decision-grade"),
            "publication_ceiling": governance_summary.get("publication_ceiling", "publish_bounded"),
            "framework_constraint": governance_summary.get("framework_constraint", ""),
            "facility_prior_id":         facility_prior_id,
            "decision_state": decision_state_en,
            "governance_summary": governance_summary,
            "case_adaptation_memo": case_adaptation_memo,
            "evidence_maturity_summary": governance_summary.get("evidence_maturity_summary", {}),
            "source_family_coverage_table": source_family_coverage_table,
            "report_type_classifier_table": report_type_classifier_table,
            "industry_adaptation_table": industry_adaptation_table,
            "structural_output_mode_classifier_table": structural_output_mode_classifier_table,
            "structural_output_mode_summary": structural_output_mode_summary,
            "structural_primary_promotion_gate": structural_primary_promotion_gate,
            "render_section_contract": render_section_contract,
            "support_chart_visibility_policy": support_chart_visibility_policy,
            "support_chart_lane_visibility_policy": support_chart_lane_visibility_policy,
            "support_chart_lane_curation_policy": support_chart_lane_curation_policy,
            "chart_visibility_policy_register": chart_visibility_policy_register,
            "chart_strategic_surface_policy_register": chart_strategic_surface_policy_register,
            "chart_strategic_surface_summary": chart_strategic_surface_summary,
            "case_namespace_register": case_namespace_register,
            "chart_case_match_register": chart_case_match_register,
            "cross_case_contamination_scan": cross_case_contamination_scan,
            "empty_section_policy_register": empty_section_policy_register,
            "section_population_status_register": section_population_status_register,
            "section_explanation_fallback_register": section_explanation_fallback_register,
            "section_density_surface_policy_register": section_density_surface_policy_register,
            "section_density_surface_summary": section_density_surface_summary,
            "section_strategic_surface_policy_register": section_strategic_surface_policy_register,
            "section_strategic_surface_summary": section_strategic_surface_summary,
            "section_redundancy_surface_policy_register": section_redundancy_surface_policy_register,
            "section_redundancy_surface_summary": section_redundancy_surface_summary,
            "section_inventory_surface_policy_register": section_inventory_surface_policy_register,
            "section_inventory_surface_summary": section_inventory_surface_summary,
            "required_body_sections": list(render_section_contract.get("required_body_sections", []) or []),
            "required_appendix_sections": list(render_section_contract.get("required_appendix_sections", []) or []),
            "written_body_policy_basis": str(render_section_contract.get("policy_note", "") or ""),
            "claim_contract_register": claim_contract_register,
            "section_claim_trace_register": section_claim_trace_register,
            "structural_executive_summary": structural_executive_summary,
            "structural_intelligence_summary": structural_intelligence_summary,
            "structural_intelligence_registers": structural_intelligence_registers,
            "executive_thesis": executive_thesis,
            "main_report_outline": main_report_outline,
            "appendix_map": appendix_map,
            "section_authority_map": section_authority_map,
            "deduplicated_claim_map": deduplicated_claim_map,
            "client_facing_tad": client_facing_tad,
            "congruence_visibility_register": congruence_visibility_register,
            "section_demotions_register": section_demotions_register,
            "body_to_appendix_justification_map": body_to_appendix_justification_map,
            "compression_decision_log": compression_decision_log,
            "client_facing_body_titles": client_facing_body_titles,
            "planned_chapter_inventory": _planned_chapter_inventory(
                sections_body_ordered,
                sections_appendix,
                render_section_contract,
            ),
            "evidence_maturity_registers": {
                "variable_maturity_register": variable_maturity_register,
                "claim_permission_register": claim_permission_register,
                "decision_permission_register": decision_permission_register,
                "report_readiness_register": report_readiness_register,
            },
            "llm_governance_summary": llm_governance_summary,
            "financial_exposure_case": financial_exposure_case,
            "compliance_applicability_case": comp_case,
            "legacy_enrichment_boundary": {
                "motor_014_enrichment_state": motor_014_enrichment_state,
                "motor_015_enrichment_state": motor_015_enrichment_state,
                "legacy_enrichment_dependency_state": legacy_enrichment_dependency_state,
            },
            "primary_view_key": "report_view",
            "approved_views": {
                "report_view": {
                    "sections": sections_body_ordered + sections_appendix,
                    "body_sections": sections_body_ordered,
                    "appendix_sections": sections_appendix,
                    "llm_available": llm_available,
                    "llm_model": llm_model,
                    "available_languages": ["en", "es"],
                    "default_language": "en",
                    "document_type": document_label,
                    "document_internal_type": internal_document_type,
                    "canonical_output_mode": canonical_output_mode,
                },
            },
            "assets":             assets,
            "context_integrity_scan": context_integrity_scan,
            "mandatory_body_sections": [
                sec.get("title", "")
                for sec in sections_body_ordered
            ],
            "section_packets": [
                _build_report_section_packet(sec, governance_summary, report_traceability)
                for sec in (sections_body_ordered + sections_appendix)
            ],
            "output_block_count": len(output_blocks),
            "total_sections":     len(sections),
        }
        report_package["report_traceability"] = report_traceability

        return {
            "report_package":          report_package,
            "total_sections":          len(sections),
            "chart_assets_available":  len(chart_assets),
            "facility_prior_id":       facility_prior_id,
            "produced_at":             produced_at,
            "motor_014_enrichment_state": motor_014_enrichment_state,
            "motor_015_enrichment_state": motor_015_enrichment_state,
            "legacy_enrichment_dependency_state": legacy_enrichment_dependency_state,
        }
