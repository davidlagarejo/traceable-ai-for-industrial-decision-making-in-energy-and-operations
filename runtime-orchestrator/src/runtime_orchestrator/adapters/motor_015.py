"""Adapter for motor_015 — Output Block Composition Engine.

Converts Decision Core outputs (motor_014) into Phase 3 governed output blocks.
Each block is the minimum visible unit traceable to upstream inference records.

Block types produced:
  1. executive_summary_block
  2. technical_summary_block
  3. evidence_table_block
  4. uncertainty_block
  5. conflict_block
  6. opportunity_block
  7. validation_agenda_block
  8. next_steps_block
  9. artifact_caption_block

Phase 3 law (enforced here):
  No visible output block may say more than what is supported by its upstream
  inference records. Composition never inflates certainty.
  Each block carries an explicit epistemic_marker.
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from .base import BaseMotorAdapter


def _trace_ref(inference_records: list[dict], case_ids: list[str]) -> list[str]:
    return [r["case_id"] for r in inference_records if r["case_id"] in case_ids]


def _build_traceability_register(
    output_blocks: list[dict[str, Any]],
    decision_core_lineage: dict[str, Any],
    produced_at: str,
    facility_prior_id: str,
) -> dict[str, Any]:
    source_lineage_id = decision_core_lineage.get("source_lineage_id", "")
    return {
        "traceability_id": f"tr:{facility_prior_id or 'unknown'}",
        "produced_at": produced_at,
        "facility_prior_id": facility_prior_id,
        "decision_core_lineage_id": decision_core_lineage.get("lineage_id", ""),
        "source_lineage_id": source_lineage_id,
        "coverage_gap_types": decision_core_lineage.get("coverage_gap_types", []),
        "admitted_source_types": decision_core_lineage.get("admitted_source_types", []),
        "block_traces": [
            {
                "block_id": block.get("block_id", ""),
                "block_type": block.get("block_type", ""),
                "epistemic_marker": block.get("epistemic_marker", ""),
                "upstream_traces": block.get("upstream_traces", []),
                "source_lineage_id": source_lineage_id,
                "facility_prior_id": facility_prior_id,
            }
            for block in output_blocks
        ],
        "trace_chain": [
            "motor_012.evidence_lineage",
            "motor_014.decision_core_lineage",
            "motor_015.output_blocks",
        ],
    }


def _build_executive_summary_block(
    inference_records: list[dict],
    conflict_register: list[dict],
    tension_records: list[dict],
    opportunity_candidates: list[dict],
    composite_reading: dict,
    facility_prior_id: str,
) -> dict:
    blocking = len(conflict_register)
    tensions = len(tension_records)
    opps = len(opportunity_candidates)
    active = len(inference_records)

    top_cases = sorted(
        inference_records,
        key=lambda c: c.get("validation_urgency_score", 0),
        reverse=True,
    )[:3]

    paragraphs = [
        (
            "This governed asset brief covers the case subject "
            "under a decision-admissibility framework. The analysis is bounded to Decision-grade: "
            "it represents structured, traceable public context and conditional hypotheses. "
            "It does not constitute a verified diagnosis, compliance determination, or "
            "investment recommendation."
        ),
        (
            f"The analytical pipeline activated {active} inference cases. "
            f"Of these, {blocking} blocking conflict(s) and {tensions} open tension(s) "
            f"were identified. The current evidence state is insufficient for a final decision: "
            f"{blocking} critical validation gap(s) must be resolved before credible "
            f"advancement is possible."
        ),
        (
            "The three highest-urgency items for immediate validation are: "
            + "; ".join(
                f"{c['case_name']} (urgency {c.get('validation_urgency_score', 0):.2f})"
                for c in top_cases
            )
            + f". {opps} candidate opportunity pathway(s) are identified, each "
            "conditional on specific validation requirements."
        ),
        (
            "All claims in this brief derive from declared intake fields, public asset-facing "
            "records, bounded issuer context where relevant, and screening-grade benchmarks. "
            "No verified site measurements, confirmed utility files, or executed lease-boundary "
            "documents were available at time of analysis. Confidence boundaries are stated "
            "explicitly throughout."
        ),
    ]

    return {
        "block_id": "BLK-ES-001",
        "block_type": "executive_summary_block",
        "title": "Executive Brief — Case Decision State",
        "audience": "executive",
        "epistemic_grade": "Decision-grade",
        "epistemic_marker": "DECISION_GRADE",
        "content_paragraphs": paragraphs,
        "key_signals": {
            "active_inference_cases": active,
            "blocking_conflicts": blocking,
            "open_tensions": tensions,
            "opportunity_candidates": opps,
            "acquisition_decision_status": composite_reading.get(
                "acquisition_decision_status", ""
            ),
        },
        "upstream_traces": [r["case_id"] for r in inference_records],
        "facility_prior_id": facility_prior_id,
        "produced_by_motor": "motor_015",
    }


def _build_technical_summary_block(
    inference_records: list[dict],
    facility_prior_id: str,
) -> dict:
    scored_table = [
        {
            "case_id": r["case_id"],
            "case_name": r["case_name"],
            "claim_family": r.get("claim_family", ""),
            "plausibility_score": r.get("plausibility_score", 0),
            "decision_relevance_score": r.get("decision_relevance_score", 0),
            "validation_urgency_score": r.get("validation_urgency_score", 0),
            "validation_requirement_summary": r.get("validation_requirement", "")[:120]
            + "...",
        }
        for r in sorted(
            inference_records,
            key=lambda x: x.get("validation_urgency_score", 0),
            reverse=True,
        )
    ]

    return {
        "block_id": "BLK-TS-001",
        "block_type": "technical_summary_block",
        "title": "Inference Case Summary — All Activated Cases",
        "audience": "technical",
        "epistemic_grade": "Decision-grade",
        "epistemic_marker": "INFERRED",
        "scored_inference_table": scored_table,
        "scoring_notes": [
            "Three admissible scores per case: plausibility, decision_relevance, validation_urgency.",
            "Scores range 0.0-1.0. Non-compensatory: a low plausibility does not offset high urgency.",
            "All scores are governed estimates under Decision-grade constraints, not verified measurements.",
        ],
        "upstream_traces": [r["case_id"] for r in inference_records],
        "facility_prior_id": facility_prior_id,
        "produced_by_motor": "motor_015",
    }


def _build_evidence_table_block(
    inference_records: list[dict],
    facility_prior_id: str,
) -> dict:
    rows = []
    for r in inference_records:
        rows.append(
            {
                "case_id": r["case_id"],
                "case_name": r["case_name"],
                "base_support_traces": r.get("base_support_traces", []),
                "dependency_assumptions": r.get("dependency_assumptions", []),
                "activation_basis": r.get("activation_basis", []),
                "evidence_quality": (
                    "confirmed_public"
                    if r.get("plausibility_score", 0) >= 0.80
                    else "plausible_inferred"
                    if r.get("plausibility_score", 0) >= 0.65
                    else "benchmark_only"
                ),
                "evidence_source_types": [
                    "SEC_EDGAR_XBRL",
                    "facility_inputs",
                    "benchmark_database",
                ],
            }
        )

    return {
        "block_id": "BLK-ET-001",
        "block_type": "evidence_table_block",
        "title": "Evidence and Source Traceability Table",
        "audience": "technical",
        "epistemic_grade": "Decision-grade",
        "epistemic_marker": "DIRECT_EVIDENCE",
        "evidence_rows": rows,
        "evidence_quality_legend": {
            "confirmed_public": (
                "Directly supported by SEC EDGAR, regulatory filing, or confirmed public record."
            ),
            "plausible_inferred": (
                "Supported by consistent public signals and domain inference logic — not verified."
            ),
            "benchmark_only": (
                "Supported by sectoral benchmark alone — requires site-specific validation."
            ),
        },
        "upstream_traces": [r["case_id"] for r in inference_records],
        "facility_prior_id": facility_prior_id,
        "produced_by_motor": "motor_015",
    }


def _build_uncertainty_block(
    uncertainty_register: list[dict],
    facility_prior_id: str,
) -> dict:
    return {
        "block_id": "BLK-UN-001",
        "block_type": "uncertainty_block",
        "title": "Uncertainty Register — Material Unknown Dimensions",
        "audience": "technical",
        "epistemic_grade": "Decision-grade",
        "epistemic_marker": "REQUIRES_VALIDATION",
        "preamble": (
            "The following uncertainty markers identify dimensions of the case that cannot be "
            "resolved from available public sources. Each marker is explicitly maintained rather "
            "than filled with assumption. Uncertainty markers do not represent analytical failure; "
            "they represent the system's honest map of what is unknown."
        ),
        "uncertainty_entries": [
            {
                "uncertainty_id": u.get("uncertainty_record_id", u.get("marker_id", "")),
                "dimension": u.get("dimension", ""),
                "description": u.get("description", ""),
                "impact_level": u.get("impact", ""),
                "resolution_path": u.get("resolution_path", ""),
                "linked_inference_case": u.get("linked_inference_case"),
            }
            for u in uncertainty_register
        ],
        "upstream_traces": [
            u.get("marker_id", u.get("uncertainty_record_id", ""))
            for u in uncertainty_register
        ],
        "facility_prior_id": facility_prior_id,
        "produced_by_motor": "motor_015",
    }


def _build_conflict_block(
    conflict_register: list[dict],
    facility_prior_id: str,
) -> dict:
    if not conflict_register:
        return {
            "block_id": "BLK-CF-001",
            "block_type": "conflict_block",
            "title": "Conflict Register — Hard Incompatibilities",
            "audience": "technical",
            "epistemic_grade": "Decision-grade",
            "epistemic_marker": "BLOCKING_CONFLICT",
            "conflicts": [],
            "note": "No hard conflicts activated in this run.",
            "upstream_traces": [],
            "facility_prior_id": facility_prior_id,
            "produced_by_motor": "motor_015",
        }

    return {
        "block_id": "BLK-CF-001",
        "block_type": "conflict_block",
        "title": "Conflict Register — Hard Incompatibilities Requiring Resolution",
        "audience": "technical",
        "epistemic_grade": "Decision-grade",
        "epistemic_marker": "BLOCKING_CONFLICT",
        "preamble": (
            "Conflicts represent hard incompatibilities between observed data points that "
            "cannot coexist without resolution. Unlike tensions (which require trade-offs), "
            "conflicts require data resolution before analytical advancement is possible. "
            "Blocking conflicts prevent any credible claim upgrade."
        ),
        "conflicts": [
            {
                "conflict_id": c["conflict_id"],
                "case_id": c["inference_case_id"],
                "name": c["conflict_name"],
                "statement": c["conflict_statement"],
                "blocking_status": c.get("blocking_status", ""),
                "plausibility_score": c.get("plausibility_score", 0),
                "decision_relevance_score": c.get("decision_relevance_score", 0),
                "validation_urgency_score": c.get("validation_urgency_score", 0),
                "validation_requirement": c.get("validation_requirement", ""),
            }
            for c in conflict_register
        ],
        "upstream_traces": [c["inference_case_id"] for c in conflict_register],
        "facility_prior_id": facility_prior_id,
        "produced_by_motor": "motor_015",
    }


def _build_opportunity_block(
    opportunity_candidates: list[dict],
    facility_prior_id: str,
) -> dict:
    return {
        "block_id": "BLK-OP-001",
        "block_type": "opportunity_block",
        "title": "Conditional Opportunity Pathways",
        "audience": "executive",
        "epistemic_grade": "Decision-grade",
        "epistemic_marker": "CONDITIONAL",
        "preamble": (
            "Candidate opportunities are improvement or value-creation pathways that are "
            "plausible given the facility prior and inference cases. They are NOT recommendations. "
            "Each opportunity is conditional on specific validation requirements. None of these "
            "pathways can be acted upon without field validation."
        ),
        "opportunities": [
            {
                "opportunity_id": o["opportunity_id"],
                "name": o["opportunity_name"],
                "type": o.get("opportunity_type", ""),
                "conditional_statement": o["conditional_statement"],
                "key_dependencies": o.get("dependency_assumptions", []),
                "validation_required": o["validation_requirement"],
                "plausibility_score": o.get("plausibility_score", 0),
                "decision_relevance_score": o.get("decision_relevance_score", 0),
                "validation_urgency_score": o.get("validation_urgency_score", 0),
            }
            for o in opportunity_candidates
        ],
        "upstream_traces": [o["opportunity_id"] for o in opportunity_candidates],
        "facility_prior_id": facility_prior_id,
        "produced_by_motor": "motor_015",
    }


def _build_validation_agenda_block(
    validation_queue: list[dict],
    evidence_gap_register: list[dict],
    facility_prior_id: str,
) -> dict:
    return {
        "block_id": "BLK-VA-001",
        "block_type": "validation_agenda_block",
        "title": "Validation Architecture — Prioritized Evidence Requirements",
        "audience": "technical",
        "epistemic_grade": "Decision-grade",
        "epistemic_marker": "REQUIRES_VALIDATION",
        "preamble": (
            "The validation agenda is the operational output of the Decision Core. "
            "It translates inference case validation requirements into a prioritized evidence "
            "collection plan. Items are ordered by validation_urgency_score (highest first). "
            "Each item identifies what data is needed, why it matters, and which inference "
            "cases it will confirm, downgrade, or retire."
        ),
        "validation_items": [
            {
                "priority": item["queue_position"],
                "case_id": item["case_id"],
                "case_name": item["case_name"],
                "claim_family": item.get("claim_family", ""),
                "validation_urgency_score": item.get("validation_urgency_score", 0),
                "decision_relevance_score": item.get("decision_relevance_score", 0),
                "what_to_obtain": item["validation_requirement"],
            }
            for item in validation_queue
        ],
        "evidence_gaps": [
            {
                "gap_id": g["gap_id"],
                "description": g["description"],
                "acquisition_impact": g.get("acquisition_impact", ""),
                "blocking_cases": g.get("blocking_inference_cases", []),
            }
            for g in evidence_gap_register
        ],
        "upstream_traces": [item["case_id"] for item in validation_queue],
        "facility_prior_id": facility_prior_id,
        "produced_by_motor": "motor_015",
    }


def _build_next_steps_block(
    next_best_questions: list[dict],
    facility_prior_id: str,
) -> dict:
    return {
        "block_id": "BLK-NS-001",
        "block_type": "next_steps_block",
        "title": "Priority Questions for the Deal Team",
        "audience": "executive",
        "epistemic_grade": "Decision-grade",
        "epistemic_marker": "REQUIRES_VALIDATION",
        "preamble": (
            "The following questions represent the highest-value information requests for "
            "resolving the current analytical blockers. They are ordered by urgency and "
            "decision impact."
        ),
        "questions": [
            {
                "question_id": q["question_id"],
                "question": q["question"],
                "urgency": q.get("urgency", ""),
                "linked_inference_case": q.get("linked_case", ""),
                "why_it_matters": q.get("why_it_matters", ""),
                "how_to_answer": q.get("how_to_answer", ""),
            }
            for q in next_best_questions
        ],
        "upstream_traces": [q.get("linked_case", "") for q in next_best_questions],
        "facility_prior_id": facility_prior_id,
        "produced_by_motor": "motor_015",
    }


def _build_decision_admissibility_block(
    composite_reading: dict[str, Any],
    decision_front_register: list[dict[str, Any]],
    facility_prior_id: str,
) -> dict[str, Any]:
    lead_front = next(
        (front for front in decision_front_register if front.get("current_status") in {"ACT NOW", "VALIDATE FIRST", "NO-GO"}),
        decision_front_register[0] if decision_front_register else {},
    )
    return {
        "block_id": "BLK-DA-001",
        "block_type": "decision_admissibility_block",
        "title": "Executive Decision-Admissibility Brief",
        "audience": "executive",
        "epistemic_grade": "Decision-grade",
        "epistemic_marker": "DECISION_GRADE",
        "decision_state": composite_reading.get("decision_state", ""),
        "primary_block_reason": composite_reading.get("primary_block_reason", ""),
        "information_deficit_score": composite_reading.get("information_deficit_score"),
        "decision_evaluated": lead_front.get("decision_front", ""),
        "recommended_action": lead_front.get("admissible_action", ""),
        "key_blockers": [
            composite_reading.get("primary_case_limitation", {}).get("conflict_name", ""),
            composite_reading.get("primary_block_reason", ""),
        ],
        "upstream_traces": [composite_reading.get("primary_case_limitation", {}).get("inference_case_id", "")],
        "facility_prior_id": facility_prior_id,
        "produced_by_motor": "motor_015",
    }


def _build_investment_uncertainty_map_block(
    decision_front_register: list[dict[str, Any]],
    financial_exposure_register: list[dict[str, Any]],
    facility_prior_id: str,
) -> dict[str, Any]:
    if financial_exposure_register:
        rows = [
            {
                "uncertainty": row.get("assumption", ""),
                "why_it_matters_financially": row.get("downside_if_wrong", ""),
                "decision_it_blocks": row.get("linked_decision_front", ""),
                "evidence_needed": row.get("evidence_needed", ""),
                "priority": (
                    "Critical"
                    if "unsupported" in str(row.get("current_support", "")).lower()
                    or "defer" in str(row.get("financial_consequence", "")).lower()
                    else "High"
                ),
            }
            for row in financial_exposure_register
        ]
    else:
        rows = [
            {
                "uncertainty": row.get("decision_front", ""),
                "why_it_matters_financially": row.get("why", ""),
                "decision_it_blocks": row.get("current_status", ""),
                "evidence_needed": row.get("required_evidence", ""),
                "priority": "Critical" if row.get("current_status") in {"NO-GO", "VALIDATE FIRST"} else "High",
            }
            for row in decision_front_register
        ]
    return {
        "block_id": "BLK-IU-001",
        "block_type": "investment_uncertainty_map_block",
        "title": "Investment Uncertainty Map",
        "audience": "executive",
        "epistemic_grade": "Decision-grade",
        "epistemic_marker": "REQUIRES_VALIDATION",
        "rows": rows,
        "upstream_traces": [row.get("decision_front", "") for row in decision_front_register],
        "facility_prior_id": facility_prior_id,
        "produced_by_motor": "motor_015",
    }


def _build_financial_exposure_block(
    financial_exposure_register: list[dict[str, Any]],
    facility_prior_id: str,
) -> dict[str, Any]:
    return {
        "block_id": "BLK-FE-001",
        "block_type": "financial_exposure_block",
        "title": "Financial Exposure Under Uncertainty",
        "audience": "executive",
        "epistemic_grade": "Decision-grade",
        "epistemic_marker": "REQUIRES_VALIDATION",
        "rows": financial_exposure_register,
        "upstream_traces": [row.get("linked_decision_front", "") for row in financial_exposure_register],
        "facility_prior_id": facility_prior_id,
        "produced_by_motor": "motor_015",
    }


def _build_minimum_evidence_pack_block(
    minimum_evidence_unlock_map: list[dict[str, Any]],
    facility_prior_id: str,
) -> dict[str, Any]:
    return {
        "block_id": "BLK-ME-001",
        "block_type": "minimum_evidence_pack_block",
        "title": "Minimum Evidence Pack",
        "audience": "executive",
        "epistemic_grade": "Decision-grade",
        "epistemic_marker": "REQUIRES_VALIDATION",
        "rows": minimum_evidence_unlock_map,
        "upstream_traces": [
            case_id
            for row in minimum_evidence_unlock_map
            for case_id in row.get("cases_resolved", [])
        ],
        "facility_prior_id": facility_prior_id,
        "produced_by_motor": "motor_015",
    }


def _build_scenario_space_block(
    scenario_space: list[dict[str, Any]],
    facility_prior_id: str,
) -> dict[str, Any]:
    return {
        "block_id": "BLK-SS-001",
        "block_type": "scenario_space_block",
        "title": "Scenario Space Under Current Uncertainty",
        "audience": "executive",
        "epistemic_grade": "Decision-grade",
        "epistemic_marker": "CONDITIONAL",
        "rows": scenario_space,
        "upstream_traces": ["scenario_space"],
        "facility_prior_id": facility_prior_id,
        "produced_by_motor": "motor_015",
    }


def _build_asset_context_readiness_block(
    readiness_summary: dict[str, Any],
    facility_prior_id: str,
) -> dict[str, Any]:
    return {
        "block_id": "BLK-AR-001",
        "block_type": "asset_context_readiness_block",
        "title": "Asset Context Readiness",
        "audience": "technical",
        "epistemic_grade": "Decision-grade",
        "epistemic_marker": "DIRECT_EVIDENCE | BLOCKING_FIELDS",
        "asset_context_readiness": readiness_summary.get("asset_context_readiness", ""),
        "critical_missing_clusters": readiness_summary.get("critical_missing_clusters", []),
        "rows": readiness_summary.get("cluster_rows", []),
        "upstream_traces": readiness_summary.get("critical_missing_clusters", []),
        "facility_prior_id": facility_prior_id,
        "produced_by_motor": "motor_015",
    }


def _build_decision_fronts_block(
    decision_front_register: list[dict[str, Any]],
    facility_prior_id: str,
) -> dict[str, Any]:
    return {
        "block_id": "BLK-DF-001",
        "block_type": "decision_fronts_block",
        "title": "Decision Fronts",
        "audience": "executive",
        "epistemic_grade": "Decision-grade",
        "epistemic_marker": "DECISION_GRADE",
        "rows": decision_front_register,
        "upstream_traces": [row.get("decision_front", "") for row in decision_front_register],
        "facility_prior_id": facility_prior_id,
        "produced_by_motor": "motor_015",
    }


def _build_inference_case_register_block(
    inference_records: list[dict[str, Any]],
    facility_prior_id: str,
) -> dict[str, Any]:
    rows = []
    for row in sorted(
        inference_records,
        key=lambda x: (
            -x.get("validation_urgency_score", 0),
            -x.get("decision_relevance_score", 0),
        ),
    ):
        plaus = float(row.get("plausibility_score", 0))
        if plaus >= 0.8:
            evidence_state = "confirmed_public"
        elif plaus >= 0.65:
            evidence_state = "plausible_inferred"
        else:
            evidence_state = "benchmark_only"
        rows.append(
            {
                "case_id": row.get("case_id", ""),
                "case_name": row.get("case_name", ""),
                "case_type": row.get("claim_family", ""),
                "prv": " / ".join(
                    f"{label}:{row.get(key, 0):.2f}"
                    for label, key in (
                        ("P", "plausibility_score"),
                        ("R", "decision_relevance_score"),
                        ("V", "validation_urgency_score"),
                    )
                ),
                "evidence_state": evidence_state,
                "decision_relevance": (
                    "critical"
                    if row.get("decision_relevance_score", 0) >= 0.85
                    else "high"
                    if row.get("decision_relevance_score", 0) >= 0.65
                    else "bounded"
                ),
                "validation_required": row.get("validation_requirement", ""),
            }
        )
    return {
        "block_id": "BLK-IC-001",
        "block_type": "inference_case_register_block",
        "title": "Inference Case Register",
        "audience": "technical",
        "epistemic_grade": "Decision-grade",
        "epistemic_marker": "INFERRED",
        "rows": rows,
        "upstream_traces": [row.get("case_id", "") for row in inference_records],
        "facility_prior_id": facility_prior_id,
        "produced_by_motor": "motor_015",
    }


def _build_next_best_questions_block(
    next_best_questions: list[dict[str, Any]],
    facility_prior_id: str,
) -> dict[str, Any]:
    rows = [
        {
            "question_id": row.get("question_id", ""),
            "question": row.get("question", ""),
            "urgency": row.get("urgency", ""),
            "linked_case": row.get("linked_case", ""),
            "why_it_matters": row.get("why_it_matters", ""),
            "how_to_answer": row.get("how_to_answer", ""),
        }
        for row in next_best_questions[:7]
    ]
    return {
        "block_id": "BLK-NQ-001",
        "block_type": "next_best_questions_block",
        "title": "Next Best Questions",
        "audience": "executive",
        "epistemic_grade": "Decision-grade",
        "epistemic_marker": "REQUIRES_VALIDATION",
        "rows": rows,
        "upstream_traces": [row.get("linked_case", "") for row in rows],
        "facility_prior_id": facility_prior_id,
        "produced_by_motor": "motor_015",
    }


def _build_artifact_caption_block(
    inference_records: list[dict],
    facility_prior: dict[str, Any],
    facility_prior_id: str,
) -> dict:
    sector = (
        facility_prior.get("entities", {})
        .get("SectorArchetype", {})
    )
    owner_name = sector.get("company_name_sec", "") or sector.get("owner_name", "") or "owner context"
    owner_ticker = sector.get("owner_ticker", "") or "NOT OBSERVED"
    source_types = sorted(
        {
            trace
            for rec in inference_records
            for trace in rec.get("base_support_traces", [])
            if isinstance(trace, str)
        }
    )
    return {
        "block_id": "BLK-AC-001",
        "block_type": "artifact_caption_block",
        "title": "Source and Artifact Attribution",
        "audience": "technical",
        "epistemic_grade": "Decision-grade",
        "epistemic_marker": "DIRECT_EVIDENCE",
        "sources_used": [
            {
                "source_id": "src_001_owner_context",
                "description": f"Owner / issuer context — {owner_name} ({owner_ticker})",
                "authority_class": "regulatory_filing",
                "used_for": "Owner identity, issuer context, and public disclosure anchoring",
            },
            {
                "source_id": "src_002_public_benchmarks",
                "description": "Public benchmark and physical-prior references used by the pipeline",
                "authority_class": "public_benchmark",
                "used_for": "Sectoral and contextual screening support only; never local truth substitution",
            },
            {
                "source_id": "src_003_case_trace_types",
                "description": "Trace types activated in this run",
                "authority_class": "runtime_trace",
                "used_for": ", ".join(source_types[:8]) or "No base support traces recorded",
            },
        ],
        "benchmark_limitations": [
            "Public benchmarks are screening-grade context. They are not local measurements.",
            "Issuer-level financial context cannot compensate for missing asset-level physical evidence.",
            "Any jurisdictional rule family must be treated as bounded screening unless local applicability is confirmed.",
        ],
        "upstream_traces": ["all_inference_records"],
        "facility_prior_id": facility_prior_id,
        "produced_by_motor": "motor_015",
    }


class Motor015Adapter(BaseMotorAdapter):
    @property
    def motor_id(self) -> str:
        return "motor_015"

    @property
    def input_motor_ids(self) -> list[str]:
        return ["motor_014", "motor_001", "motor_002"]

    def _run_impl(self, inputs: dict[str, Any]) -> dict[str, Any]:
        m14 = inputs.get("motor_014", {})
        produced_at = datetime.now(timezone.utc).isoformat()

        inference_records     = m14.get("inference_records", [])
        tension_records       = m14.get("tension_records", [])
        conflict_register     = m14.get("conflict_register", [])
        opportunity_candidates = m14.get("opportunity_candidates", [])
        uncertainty_register  = m14.get("uncertainty_register", [])
        evidence_gap_register = m14.get("evidence_gap_register", [])
        validation_queue      = m14.get("validation_queue", [])
        next_best_questions   = m14.get("next_best_questions", [])
        composite_reading     = m14.get("composite_reading", {})
        decision_front_register = m14.get("decision_front_register", [])
        minimum_evidence_unlock_map = m14.get("minimum_evidence_unlock_map", [])
        scenario_space = m14.get("scenario_space", [])
        financial_exposure_register = m14.get("financial_exposure_register", [])
        asset_context_readiness_summary = m14.get("asset_context_readiness_summary", {})
        facility_prior_id     = m14.get("facility_prior_id", "")
        decision_core_lineage = m14.get("decision_core_lineage", {})
        facility_prior = inputs.get("motor_014", {}).get("facility_prior", {}) or inputs.get("motor_012", {}).get("facility_prior", {})

        output_blocks = [
            _build_decision_admissibility_block(
                composite_reading,
                decision_front_register,
                facility_prior_id,
            ),
            _build_executive_summary_block(
                inference_records, conflict_register, tension_records,
                opportunity_candidates, composite_reading, facility_prior_id,
            ),
            _build_investment_uncertainty_map_block(
                decision_front_register,
                financial_exposure_register,
                facility_prior_id,
            ),
            _build_technical_summary_block(inference_records, facility_prior_id),
            _build_evidence_table_block(inference_records, facility_prior_id),
            _build_uncertainty_block(uncertainty_register, facility_prior_id),
            _build_asset_context_readiness_block(
                asset_context_readiness_summary,
                facility_prior_id,
            ),
            _build_conflict_block(conflict_register, facility_prior_id),
            _build_scenario_space_block(
                scenario_space,
                facility_prior_id,
            ),
            _build_financial_exposure_block(
                financial_exposure_register,
                facility_prior_id,
            ),
            _build_opportunity_block(opportunity_candidates, facility_prior_id),
            _build_validation_agenda_block(
                validation_queue, evidence_gap_register, facility_prior_id
            ),
            _build_minimum_evidence_pack_block(
                minimum_evidence_unlock_map,
                facility_prior_id,
            ),
            _build_decision_fronts_block(
                decision_front_register,
                facility_prior_id,
            ),
            _build_inference_case_register_block(
                inference_records,
                facility_prior_id,
            ),
            _build_next_best_questions_block(
                next_best_questions,
                facility_prior_id,
            ),
            _build_next_steps_block(next_best_questions, facility_prior_id),
            _build_artifact_caption_block(inference_records, facility_prior, facility_prior_id),
        ]

        block_register = {b["block_id"]: b["block_type"] for b in output_blocks}
        traceability_register = _build_traceability_register(
            output_blocks,
            decision_core_lineage,
            produced_at,
            facility_prior_id,
        )

        return {
            "output_blocks": output_blocks,
            "block_register": block_register,
            "traceability_register": traceability_register,
            "decision_core_lineage": decision_core_lineage,
            "section_eligibility_register": {
                "decision_admissibility_block": "body_allowed",
                "investment_uncertainty_map_block": "body_allowed",
                "minimum_evidence_pack_block": "body_allowed",
                "scenario_space_block": "body_allowed",
                "financial_exposure_block": "body_allowed",
                "asset_context_readiness_block": "body_allowed",
                "decision_fronts_block": "body_allowed",
                "inference_case_register_block": "body_allowed",
                "next_best_questions_block": "body_allowed",
                "artifact_caption_block": "appendix_only",
            },
            "total_blocks": len(output_blocks),
            "block_types_produced": [b["block_type"] for b in output_blocks],
            "facility_prior_id": facility_prior_id,
            "composite_reading": composite_reading,
            "produced_at": produced_at,
        }
