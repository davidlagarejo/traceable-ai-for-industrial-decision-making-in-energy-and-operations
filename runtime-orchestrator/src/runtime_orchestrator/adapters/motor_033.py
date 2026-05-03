"""Adapter for motor_033 — TAD Preliminary (Technical Assessment Document).

Produces a TAD Preliminary: a ranked action plan ordered by the Value of
Information (VoI) each validation action provides relative to decision state
advancement.

Algorithm:
  VoI(i) = validation_urgency_score(i)
            × decision_relevance_score(i)
            × (1 − plausibility_score(i))   ← epistemic gap size

  The third term captures that a case we are UNCERTAIN about yields more
  information per validation unit than one that is already highly plausible.
  A case that is certain (plausibility ≈ 1.0) has VoI ≈ 0 — validating it
  confirms what we already believe.

Output:
  tad_action_plan          — ordered list of TAD actions with effort tiers
  decision_frontier        — narrative of current epistemic ceiling
  information_deficit_score — aggregate gap (0 = resolved, 1 = maximal)
  blocking_resolution_paths — minimal evidence set per blocking conflict
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from .base import BaseMotorAdapter
from runtime_orchestrator.evidence_maturity.decision_templates import get_decision_template


_EFFORT_THRESHOLDS = {
    "immediate":  0.80,   # VoI ≥ 0.80 → same-day request
    "high":       0.55,   # VoI ≥ 0.55 → this-week priority
    "medium":     0.30,   # VoI ≥ 0.30 → scheduled investigation
    "low":        0.0,    # VoI < 0.30 → background / opportunistic
}

_SOURCE_EFFORT = {
    "confirmed_public":   "low",
    "plausible_inferred": "medium",
    "benchmark_only":     "high",
    None:                 "high",
}


def _voi(rec: dict) -> float:
    """Value of Information score for one inference case."""
    if rec.get("case_id") == "LC-ASSET-01":
        return 0.995
    v = rec.get("validation_urgency_score", 0.0)
    r = rec.get("decision_relevance_score", 0.0)
    p = rec.get("plausibility_score", 0.0)
    gap = 1.0 - p
    return round(v * r * gap, 4)


def _effort_tier(voi_score: float) -> str:
    for tier, threshold in _EFFORT_THRESHOLDS.items():
        if voi_score >= threshold:
            return tier
    return "low"


def _decision_unlock(rec: dict) -> str:
    family = rec.get("claim_family", "")
    case_id = rec.get("case_id", "")
    case_name = rec.get("case_name", "")
    if case_id == "LC-ASSET-01":
        return (
            "Resolves the foundational asset-context insufficiency. "
            "Unlocks admissible technical reading of the asset before finance-heavy interpretation."
        )
    if family == "conflict":
        return (f"Resolves BLOCKING conflict {case_id}. "
                f"Unlocks leverage-dependent analysis and downstream financial modelling.")
    if family == "tension":
        return (f"Clarifies material tension in {case_name[:50]}. "
                f"Enables confidence upgrade from HYPOTHESIS to INFERRED.")
    if family == "plausible_hypothesis":
        return (f"Confirms or retires hypothesis {case_id}. "
                f"Recalibrates inference case weight in decision composite.")
    if family == "opportunity":
        return (f"Validates opportunity pathway {case_id}. "
                f"Moves from CONDITIONAL to actionable decision space.")
    return f"Advances epistemic state for {case_id}."


def _action_family(rec: dict) -> str:
    family = rec.get("claim_family", "")
    if rec.get("case_id") == "LC-ASSET-01":
        return "classify"
    reg_text = " ".join(
        [
            rec.get("case_id", ""),
            rec.get("case_name", ""),
            rec.get("conditional_statement", ""),
            rec.get("validation_requirement", ""),
        ]
    ).lower()
    if "regulat" in reg_text or "compliance" in reg_text or rec.get("case_id", "").startswith("LC-REG"):
        return "seek_regulatory_review"
    if family == "conflict":
        return "measure"
    if family == "tension":
        return "investigate"
    if family == "plausible_hypothesis":
        return "inspect"
    if family == "opportunity":
        return "pilot"
    return "investigate"


def _downside_profile(rec: dict) -> str:
    family = rec.get("claim_family", "")
    relevance = rec.get("decision_relevance_score", 0.0)
    if family == "conflict":
        return "high"
    if family == "opportunity" and relevance >= 0.75:
        return "medium_high"
    if family == "tension":
        return "medium"
    return "low_medium"


def _irreversibility_profile(action_family: str) -> str:
    if action_family in {"measure", "inspect", "classify", "investigate", "seek_regulatory_review"}:
        return "low"
    if action_family == "pilot":
        return "medium"
    return "high"


def _recommended_posture(rec: dict, action_family: str) -> str:
    family = rec.get("claim_family", "")
    if rec.get("case_id") == "LC-ASSET-01":
        return "validation_first"
    plausibility = rec.get("plausibility_score", 0.0)
    relevance = rec.get("decision_relevance_score", 0.0)
    if action_family == "seek_regulatory_review":
        return "validation_first"
    if family == "conflict":
        return "validation_first"
    if family in {"tension", "plausible_hypothesis"}:
        return "investigate_then_decide"
    if family == "opportunity" and plausibility >= 0.65 and relevance >= 0.70:
        return "bounded_candidate_action"
    if family == "opportunity":
        return "defer"
    return "investigate_then_decide"


def _burden_level(action_family: str, posture: str, downside: str) -> str:
    if posture == "validation_first":
        return "evidence_before_action"
    if posture == "defer":
        return "insufficient_support"
    if action_family == "pilot":
        return "bounded_reversible_only"
    if downside in {"high", "medium_high"}:
        return "heightened_validation"
    return "standard_validation"


def _no_go_condition(rec: dict, posture: str) -> str:
    family = rec.get("claim_family", "")
    if rec.get("case_id") == "LC-ASSET-01":
        return "No finance-led, compliance-closing, or implementation-oriented reading is admissible until the asset is better identified physically and operationally."
    reg_text = " ".join(
        [rec.get("case_id", ""), rec.get("case_name", ""), rec.get("validation_requirement", "")]
    ).lower()
    if "regulat" in reg_text or "compliance" in reg_text:
        return "No compliance-closing, permit-dependent, or irreversible action is admissible until regulatory applicability and current posture are confirmed."
    if family == "conflict":
        return "No leverage-dependent, compliance-closing, or irreversible capital action is admissible until this conflict is resolved."
    if posture == "defer":
        return "Do not advance beyond bounded investigation until evidence materially strengthens the case."
    if posture == "bounded_candidate_action":
        return "Only reversible or low-regret pilot action is admissible; full implementation remains blocked."
    return "No irreversible action without satisfying the stated validation requirement."


def _information_deficit(records: list[dict]) -> float:
    """Aggregate information deficit: weighted average of epistemic gaps."""
    if not records:
        return 0.0
    total_weight = sum(r.get("decision_relevance_score", 0) for r in records)
    if not total_weight:
        return 0.0
    weighted_gap = sum(
        r.get("decision_relevance_score", 0) * (1 - r.get("plausibility_score", 0))
        for r in records
    )
    return round(weighted_gap / total_weight, 3)


def _frontier_narrative(
    records: list[dict],
    conflicts: list[dict],
    deficit_score: float,
) -> str:
    blocking = [r for r in records if r.get("claim_family") == "conflict"]
    n_blocking = len(blocking) + len(conflicts)
    top = sorted(records, key=lambda r: _voi(r), reverse=True)[:2]
    top_names = " and ".join(f"[{r['case_id']}] {r['case_name'][:35]}" for r in top)

    if deficit_score >= 0.70:
        grade = "CRITICAL — decision advancement not possible without primary validation"
    elif deficit_score >= 0.45:
        grade = "HIGH — significant epistemic gaps constrain analytical confidence"
    elif deficit_score >= 0.25:
        grade = "MODERATE — key uncertainties remain but partial advancement is possible"
    else:
        grade = "LOW — validation is refinement, not foundational repair"

    parts = [f"Deficit grade: {grade}."]
    if any(r.get("case_id") == "LC-ASSET-01" for r in records):
        parts.append(
            "The primary frontier is asset clarification: the case remains physically underpopulated, so technical reading must stay bounded."
        )
    if n_blocking:
        parts.append(
            f"{n_blocking} blocking conflict(s) prevent leverage-dependent analysis."
        )
    if top_names:
        parts.append(f"Highest-value validation targets: {top_names}.")
    parts.append(
        "No section of this governed brief advances beyond INFERRED grade until "
        "blocking conflicts are resolved and top-priority cases are validated."
    )
    return " ".join(parts)


def _decision_front_actions(
    decision_front_register: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    def _canonical_status(raw_status: str) -> str:
        status = str(raw_status or "").strip().upper()
        if status in {"ACT NOW", "VALIDATE FIRST", "DEFER", "NO-GO"}:
            return status
        if status in {"INVESTIGATE", "INVESTIGATE THEN DECIDE"}:
            return "INVESTIGATE"
        return "INVESTIGATE"

    def _posture_from_status(status: str) -> str:
        return {
            "ACT NOW": "act_now",
            "VALIDATE FIRST": "validation_first",
            "INVESTIGATE": "investigate",
            "DEFER": "defer",
            "NO-GO": "no_go",
        }.get(status, "investigate")

    def _action_family_from_status(status: str) -> str:
        return {
            "ACT NOW": "request_evidence",
            "VALIDATE FIRST": "validate_first",
            "INVESTIGATE": "investigate",
            "DEFER": "defer",
            "NO-GO": "no_go",
        }.get(status, "investigate")

    def _prohibited_action(front: dict[str, Any], status: str) -> str:
        explicit = str(front.get("prohibited_action", "")).strip()
        if explicit:
            return explicit
        decision_name = str(front.get("maturity_decision_name", "")).strip()
        if decision_name:
            template = get_decision_template(decision_name)
            if template and template.blocked_actions:
                return "; ".join(str(item).strip() for item in template.blocked_actions if str(item).strip())
        if status == "ACT NOW":
            return "Do not advance beyond evidence request until the required evidence is received."
        if status == "VALIDATE FIRST":
            return "Do not close this decision front until the required evidence is validated."
        if status == "DEFER":
            return "Do not advance this decision front until higher-priority evidence gaps are resolved."
        if status == "NO-GO":
            return "Do not advance this decision front under current evidence."
        return "Do not commit capital or close technical claims before investigation resolves the current bottleneck."

    actions: list[dict[str, Any]] = []
    for rank, front in enumerate(decision_front_register, 1):
        raw_status = str(front.get("current_status", "")).upper()
        status = _canonical_status(raw_status)
        action_family = _action_family_from_status(status)
        posture = _posture_from_status(status)
        actions.append(
            {
                "rank": rank,
                "decision_front": front.get("decision_front", ""),
                "decision_name": front.get("maturity_decision_name", ""),
                "raw_current_status": raw_status,
                "current_status": status,
                "why": front.get("why", ""),
                "required_evidence": front.get("required_evidence", ""),
                "admissible_action": front.get("allowed_action_by_maturity", "") or front.get("admissible_action", ""),
                "prohibited_action": _prohibited_action(front, status),
                "variable_bottleneck": front.get("variable_bottleneck", ""),
                "maturity_admissibility_state": front.get("maturity_admissibility_state", ""),
                "allowed_action_by_maturity": front.get("allowed_action_by_maturity", ""),
                "action_family": action_family,
                "recommended_posture": posture,
            }
        )
    return actions


def _expanded_structural_tad_actions(
    *,
    target_definition: dict[str, Any],
    structural_claim_permission_register: list[dict[str, Any]],
    competitive_comparison_register: list[dict[str, Any]],
    conditional_redesign_register: list[dict[str, Any]],
    structural_financial_exposure_register: list[dict[str, Any]],
    minimum_evidence_for_discrimination_register: list[dict[str, Any]],
    dominant_variable_register: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    claim_map = {
        str(row.get("claim", "")).strip(): str(row.get("permission", "")).strip()
        for row in structural_claim_permission_register
        if str(row.get("claim", "")).strip()
    }
    target_type = str(target_definition.get("target_type", "")).strip().lower()
    var_map = {
        str(row.get("variable", "")).strip(): row
        for row in dominant_variable_register
        if str(row.get("variable", "")).strip()
    }
    evidence_needed = minimum_evidence_for_discrimination_register[0]["minimum_evidence"] if minimum_evidence_for_discrimination_register else ""
    financial_exposure = structural_financial_exposure_register[0]["financial_exposure_if_wrong"] if structural_financial_exposure_register else ""
    observed_or_conditional = len([row for row in dominant_variable_register if str(row.get("evidence_state", "")).strip() in {"OBSERVED_FACT", "CONDITIONAL_HYPOTHESIS"}])
    compare_permission = claim_map.get("peer_comparison_claim", "prohibited")
    redesign_permission = claim_map.get("redesign_hypothesis_claim", "prohibited")

    actions: list[dict[str, Any]] = []
    if minimum_evidence_for_discrimination_register:
        actions.append(
            {
                "action": "Request discriminating evidence pack",
                "status": "ACT NOW",
                "why": "This evidence set discriminates the rival structural hypotheses with the highest value of information.",
                "evidence_state": "CONDITIONAL_HYPOTHESIS",
                "financial_exposure": financial_exposure,
                "evidence_needed": evidence_needed,
                "prohibited_action": "Do not close savings, ROI, or redesign claims before this evidence arrives.",
                "linked_claim": "TAD_action_claim",
            }
        )
    if competitive_comparison_register:
        actions.append(
            {
                "action": "Compare against structural peers",
                "status": "COMPARE TO PEERS" if compare_permission != "prohibited" else "INVESTIGATE",
                "why": "Peer comparison can clarify whether the bottleneck is technology, control boundary, maintenance discipline, or process design.",
                "evidence_state": competitive_comparison_register[0].get("evidence_state", "CONDITIONAL_HYPOTHESIS"),
                "financial_exposure": financial_exposure,
                "evidence_needed": ", ".join(competitive_comparison_register[0].get("evidence_needed", []) or []),
                "prohibited_action": "Do not state peer superiority as fact without evidence state and transferability bounds.",
                "linked_claim": "peer_comparison_claim",
            }
        )
    if conditional_redesign_register:
        actions.append(
            {
                "action": "Advance bounded redesign hypothesis",
                "status": "REDESIGN HYPOTHESIS" if redesign_permission != "prohibited" else "INVESTIGATE",
                "why": "A redesign path is useful only as a falsifiable hypothesis under current evidence.",
                "evidence_state": conditional_redesign_register[0].get("evidence_state", "CONDITIONAL_HYPOTHESIS"),
                "financial_exposure": financial_exposure,
                "evidence_needed": ", ".join(conditional_redesign_register[0].get("next_evidence", []) or []),
                "prohibited_action": "Do not present redesign as a final recommendation.",
                "linked_claim": "redesign_hypothesis_claim",
            }
        )
    do_not_model_yet = (
        observed_or_conditional < 3
        or (target_type == "commercial_building" and str(var_map.get("owner_control_boundary", {}).get("evidence_state", "")).strip() != "OBSERVED_FACT")
        or (target_type == "manufacturing_facility" and str(var_map.get("throughput", {}).get("evidence_state", "")).strip() != "OBSERVED_FACT")
    )
    actions.append(
        {
            "action": "Build detailed system model / digital twin",
            "status": "DO NOT MODEL YET" if do_not_model_yet else "INVESTIGATE",
            "why": "The framework should not model complexity before the dominant variables and control boundaries are sufficiently bounded.",
            "evidence_state": "CONDITIONAL_HYPOTHESIS",
            "financial_exposure": financial_exposure,
            "evidence_needed": evidence_needed,
            "prohibited_action": "Do not commit modeling effort to irrelevant complexity before the dominant variables are discriminated.",
            "linked_claim": "TAD_action_claim",
        }
    )
    return actions


class Motor033Adapter(BaseMotorAdapter):
    @property
    def motor_id(self) -> str:
        return "motor_033"

    @property
    def input_motor_ids(self) -> list[str]:
        return ["motor_014", "motor_015", "motor_034", "motor_012", "motor_038", "motor_040", "motor_041", "motor_042", "motor_043", "motor_044", "motor_045", "motor_046"]

    def _run_impl(self, inputs: dict[str, Any]) -> dict[str, Any]:
        m14 = inputs.get("motor_014", {})
        m15 = inputs.get("motor_015", {})
        m34 = inputs.get("motor_034", {}) if isinstance(inputs.get("motor_034", {}), dict) else {}

        inference_records  = m14.get("inference_records", [])
        conflict_register  = m14.get("conflict_register", [])
        evidence_gap_register = m14.get("evidence_gap_register", [])
        validation_queue   = m14.get("validation_queue", [])
        next_best_questions = m14.get("next_best_questions", [])
        decision_front_register = m14.get("decision_front_register", [])
        variable_bottleneck_register = m14.get("variable_bottleneck_register", m34.get("decision_permission_register", []))
        canonical_problem_frame = dict(m14.get("canonical_problem_frame", m34.get("canonical_problem_frame", {})) or {})
        structural_reasoning_path = dict(m14.get("structural_reasoning_path", {}) or {})
        produced_at        = datetime.now(timezone.utc).isoformat()

        # ── Step 1: Compute VoI for each inference record ──────────────────────
        scored = []
        for rec in inference_records:
            voi_score = _voi(rec)
            scored.append({
                "case_id":        rec["case_id"],
                "case_name":      rec["case_name"],
                "claim_family":   rec.get("claim_family", ""),
                "voi_score":      voi_score,
                "plausibility":   rec.get("plausibility_score", 0),
                "relevance":      rec.get("decision_relevance_score", 0),
                "urgency":        rec.get("validation_urgency_score", 0),
                "gap_size":       round(1 - rec.get("plausibility_score", 0), 3),
                "effort_tier":    _effort_tier(voi_score),
                "validation_requirement": rec.get("validation_requirement", ""),
                "decision_unlock": _decision_unlock(rec),
            })

        scored.sort(key=lambda x: x["voi_score"], reverse=True)

        # ── Step 2: Build TAD action plan ──────────────────────────────────────
        tad_action_plan = []
        for rank, item in enumerate(scored, 1):
            # Find matching validation queue entry for evidence details
            vq_entry = next(
                (q for q in validation_queue if q.get("case_id") == item["case_id"]),
                {},
            )
            rec = next((r for r in inference_records if r.get("case_id") == item["case_id"]), {})
            action_family = _action_family(rec)
            posture = _recommended_posture(rec, action_family)
            downside = _downside_profile(rec)
            irreversibility = _irreversibility_profile(action_family)
            tad_action_plan.append({
                "rank":             rank,
                "case_id":          item["case_id"],
                "case_name":        item["case_name"],
                "action_title":     f"Validate: {item['case_name'][:60]}",
                "action_family":    action_family,
                "recommended_posture": posture,
                "voi_score":        item["voi_score"],
                "effort_tier":      item["effort_tier"],
                "downside_profile": downside,
                "irreversibility_profile": irreversibility,
                "burden_level":     _burden_level(action_family, posture, downside),
                "decision_unlock":  item["decision_unlock"],
                "evidence_needed":  item["validation_requirement"][:160],
                "claim_family":     item["claim_family"],
                "plausibility":     item["plausibility"],
                "epistemic_gap":    item["gap_size"],
                "no_go_condition":  _no_go_condition(rec, posture),
                "sequencing_note":  vq_entry.get("data_source_needed", "") or item["validation_requirement"][:100],
            })

        # ── Step 3: Blocking conflict resolution paths ─────────────────────────
        blocking_paths = []
        for conflict in conflict_register:
            rec = next(
                (r for r in inference_records if r["case_id"] == conflict.get("inference_case_id", "")),
                {},
            )
            blocking_paths.append({
                "conflict_id":     conflict.get("conflict_id", ""),
                "conflict_name":   conflict.get("conflict_name", ""),
                "blocking_status": conflict.get("blocking_status", ""),
                "minimum_evidence": conflict.get("validation_requirement", rec.get("validation_requirement", "")),
                "unblock_voi":     next(
                    (s["voi_score"] for s in scored if s["case_id"] == conflict.get("inference_case_id")),
                    0.0,
                ),
                "unblocked_analyses": [
                    "leverage_structure_analysis",
                    "debt_service_coverage_modelling",
                    "cap_rate_application",
                ],
            })

        # ── Step 4: Decision frontier and deficit score ────────────────────────
        deficit_score  = m14.get("information_deficit_score", _information_deficit(inference_records))
        frontier       = _frontier_narrative(inference_records, conflict_register, deficit_score)
        report_readiness = m34.get("report_readiness_register", {}) if isinstance(m34.get("report_readiness_register", {}), dict) else {}
        if report_readiness.get("reason"):
            frontier = " ".join([frontier, str(report_readiness.get("reason", "")).strip()])
        decision_front_actions = _decision_front_actions(decision_front_register)
        expanded_structural_tad_action_register = _expanded_structural_tad_actions(
            target_definition=inputs.get("motor_007", {}).get("target_definition_contract", {}) or {},
            structural_claim_permission_register=list(m34.get("structural_claim_permission_register", []) or []),
            competitive_comparison_register=list(inputs.get("motor_043", {}).get("competitive_comparison_register", []) or []),
            conditional_redesign_register=list(inputs.get("motor_044", {}).get("conditional_redesign_register", []) or []),
            structural_financial_exposure_register=list(inputs.get("motor_045", {}).get("structural_financial_exposure_register", []) or []),
            minimum_evidence_for_discrimination_register=list(inputs.get("motor_046", {}).get("minimum_evidence_for_discrimination_register", []) or []),
            dominant_variable_register=list(inputs.get("motor_038", {}).get("dominant_variable_register", []) or []),
        )
        front_posture_summary = {
            "act_now": len([a for a in decision_front_actions if a["recommended_posture"] == "act_now"]),
            "validation_first": len([a for a in decision_front_actions if a["recommended_posture"] == "validation_first"]),
            "investigate": len([a for a in decision_front_actions if a["recommended_posture"] == "investigate"]),
            "defer": len([a for a in decision_front_actions if a["recommended_posture"] == "defer"]),
            "no_go": len([a for a in decision_front_actions if a["recommended_posture"] == "no_go"]),
        }
        structural_posture_summary = {
            "act_now": len([a for a in expanded_structural_tad_action_register if a["status"] == "ACT NOW"]),
            "validate_first": len([a for a in expanded_structural_tad_action_register if a["status"] == "VALIDATE FIRST"]),
            "investigate": len([a for a in expanded_structural_tad_action_register if a["status"] == "INVESTIGATE"]),
            "defer": len([a for a in expanded_structural_tad_action_register if a["status"] == "DEFER"]),
            "no_go": len([a for a in expanded_structural_tad_action_register if a["status"] == "NO-GO"]),
            "redesign_hypothesis": len([a for a in expanded_structural_tad_action_register if a["status"] == "REDESIGN HYPOTHESIS"]),
            "compare_to_peers": len([a for a in expanded_structural_tad_action_register if a["status"] == "COMPARE TO PEERS"]),
            "do_not_model_yet": len([a for a in expanded_structural_tad_action_register if a["status"] == "DO NOT MODEL YET"]),
        }

        # ── Step 5: Epistemic completeness by section ──────────────────────────
        section_epistemic = {}
        family_map = {
            "conflict":             "c3_blocking_conflicts",
            "tension":              "c6_tension_map",
            "plausible_hypothesis": "c4_inference_case_map",
            "opportunity":          "c8_conditional_opportunities",
        }
        for rec in inference_records:
            section = family_map.get(rec.get("claim_family", ""), "c4_inference_case_map")
            if section not in section_epistemic:
                section_epistemic[section] = {"cases": 0, "avg_plausibility": 0.0, "avg_voi": 0.0}
            section_epistemic[section]["cases"] += 1
            section_epistemic[section]["avg_plausibility"] += rec.get("plausibility_score", 0)
            section_epistemic[section]["avg_voi"] += _voi(rec)
        for sec_data in section_epistemic.values():
            n = max(sec_data["cases"], 1)
            sec_data["avg_plausibility"] = round(sec_data["avg_plausibility"] / n, 3)
            sec_data["avg_voi"] = round(sec_data["avg_voi"] / n, 3)

        tad_preliminary = {
            "tad_action_plan":           tad_action_plan,
            "blocking_resolution_paths": blocking_paths,
            "decision_frontier":         frontier,
            "information_deficit_score": deficit_score,
            "section_epistemic_map":     section_epistemic,
            "posture_summary": {
                **front_posture_summary,
                "investigate_then_decide": front_posture_summary["investigate"],
                "bounded_candidate_action": 0,
            },
            "expanded_structural_posture_summary": structural_posture_summary,
            "decision_front_actions": decision_front_actions,
            "expanded_structural_tad_action_register": expanded_structural_tad_action_register,
            "decision_front_register": decision_front_register,
            "variable_bottleneck_register": variable_bottleneck_register,
            "canonical_problem_frame": canonical_problem_frame,
            "structural_reasoning_path": structural_reasoning_path,
            "primary_reasoning_path": str(
                structural_reasoning_path.get("reasoning_path")
                or canonical_problem_frame.get("reasoning_path")
                or "legacy_decision_gating_only"
            ),
            "structural_problem_frame_active": bool(
                structural_reasoning_path.get("problem_frame_active", canonical_problem_frame.get("problem_frame_active", False))
            ),
            "report_readiness_register": report_readiness,
            "recommended_posture": (
                decision_front_actions[0]["recommended_posture"]
                if decision_front_actions
                else "investigate"
            ),
            "total_cases_scored":        len(scored),
            "critical_actions":          [a for a in tad_action_plan if a["effort_tier"] == "immediate"],
            "high_actions":              [a for a in tad_action_plan if a["effort_tier"] == "high"],
        }

        return {
            "tad_preliminary":           tad_preliminary,
            "tad_action_count":          len(tad_action_plan),
            "blocking_conflict_count":   len(conflict_register),
            "information_deficit_score": deficit_score,
            "expanded_structural_tad_action_register": expanded_structural_tad_action_register,
            "produced_at":               produced_at,
        }
