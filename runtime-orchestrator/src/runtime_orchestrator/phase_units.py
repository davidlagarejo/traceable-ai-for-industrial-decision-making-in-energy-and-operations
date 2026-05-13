"""Phase canonical units — projection functions.

Each function projects an upstream motor's native output into the
canonical EPISTEMOLOGICAL UNIT of its phase, as defined in the
constitutional master documents (`Phases/phase-{N}/docs/es/`).

This is a thin layer. The motors already compute the fields; this module
only renames / shapes them into the canonical schema so downstream
consumers (dashboard, narrator, validators) see the same names the
constitution uses.

Phase 2 — Inference Case (Master Doc §15):
  base_support, inference_logic, claim_type, conditional_statement,
  dependency_assumptions, validation_requirement (+ three scores)

Phase 4 — claim_upgrade_candidate (Master Doc §5):
  claim_id, evidence_local_required, baseline_hardening_state,
  contrast_route, observation_route, measurement_route,
  instrument_dependency, validity_domain, upgrade_condition,
  hold_degrade_block_reason

Phase 5 — financial_exposure_case (Master Doc §4 + §7.1):
  decision_front, asset_boundary, baseline_dependency_state,
  tariff_basis_state, cost_basis_state, benefit_driver_family,
  horizon_basis, discount_basis_rule, regulatory_dependency_state,
  publication_ceiling, decision_finance_posture

Phase 6 — compliance_applicability_case (Master Doc §4 + §7.1):
  jurisdiction, authority_source, rule_family, rule_version,
  asset_boundary, subsystem_boundary, missing_trigger_fields,
  threshold_dependency, exception_path, publication_ceiling,
  applicability_state

Phase 7 — belief_revision_event (Master Doc §4 + §7.1):
  target_object, prior_state, trigger_event, dependency_type,
  causal_statement, scope_impact, propagation_scope,
  publication_consequence, lifecycle_action

Phase 8 — decision_admissibility_case (Master Doc §4 + §7.1):
  target_action_family, action_scope, current_support_posture,
  downside_class, irreversibility_class, regulatory_dependency,
  unresolved_blockers, required_evidence_burden, publication_ceiling
"""
from __future__ import annotations

from typing import Any


# ── Phase 2 — Inference Case ────────────────────────────────────────────


def to_inference_case_register(
    inference_records: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """Project motor_014.inference_records into the canonical Phase 2 unit.

    The 6 mandatory attributes from Phase 2 Master Doc §15 are exposed
    explicitly under their canonical names. The three Decision Core
    scores (plausibility / decision_relevance / validation_urgency)
    travel along as Phase 2's quantitative surface.
    """
    out: list[dict[str, Any]] = []
    for record in inference_records or []:
        out.append({
            "case_id": str(record.get("case_id", "")),
            "case_name": str(record.get("case_name", "")),
            # ── 6 canonical Phase 2 attributes ──
            "base_support": list(record.get("base_support_traces", []) or []),
            "inference_logic": str(record.get("inference_logic", "")),
            "claim_type": str(record.get("claim_family", "")),
            "conditional_statement": str(record.get("conditional_statement", "")),
            "dependency_assumptions": list(record.get("dependency_assumptions", []) or []),
            "validation_requirement": str(record.get("validation_requirement", "")),
            # ── Phase 2 three scores ──
            "plausibility_score": record.get("plausibility_score"),
            "decision_relevance_score": record.get("decision_relevance_score"),
            "validation_urgency_score": record.get("validation_urgency_score"),
            # ── Provenance marker ──
            "__phase__": 2,
            "__canonical_unit__": "inference_case",
        })
    return out


# ── Phase 4 — claim_upgrade_candidate ───────────────────────────────────


_HARDENING_HINT_FROM_PERMISSION = {
    "permitted": "evidence_present_supports_upgrade",
    "conditional": "additional_evidence_required",
    "restricted": "blocking_evidence_gap",
    "blocked": "do_not_upgrade",
}


def to_claim_upgrade_candidate_register(
    claim_permission_register: list[dict[str, Any]] | dict[str, Any],
    evidence_gap_register: list[dict[str, Any]] | None = None,
    validation_queue: list[dict[str, Any]] | None = None,
) -> list[dict[str, Any]]:
    """Project motor_014/motor_034 claim permission rows into the
    canonical Phase 4 unit (claim_upgrade_candidate).

    Each candidate carries the explicit hardening-route fields from
    Phase 4 Master Doc §5: evidence_local_required, baseline_hardening
    state, contrast/observation/measurement routes, instrument dependency,
    validity domain, upgrade condition, hold/degrade/block reason.

    Inputs:
      claim_permission_register — motor_014/motor_034 permission rows
      evidence_gap_register — motor_014 evidence gaps to derive evidence_local_required
      validation_queue — motor_014 validation entries for hardening routes
    """
    rows = (
        claim_permission_register
        if isinstance(claim_permission_register, list)
        else list((claim_permission_register or {}).get("permissions", []) or [])
    )
    gaps_by_claim: dict[str, list[dict[str, Any]]] = {}
    for gap in evidence_gap_register or []:
        if isinstance(gap, dict):
            cid = str(gap.get("linked_claim_id") or gap.get("linked_case_id") or "")
            if cid:
                gaps_by_claim.setdefault(cid, []).append(gap)

    queue_by_claim: dict[str, list[dict[str, Any]]] = {}
    for item in validation_queue or []:
        if isinstance(item, dict):
            cid = str(item.get("case_id") or item.get("linked_claim_id") or "")
            if cid:
                queue_by_claim.setdefault(cid, []).append(item)

    out: list[dict[str, Any]] = []
    for row in rows:
        if not isinstance(row, dict):
            continue
        claim_id = str(row.get("claim_id") or row.get("case_id") or "")
        permission = str(row.get("permission") or row.get("permission_state") or "").lower()
        hardening_hint = _HARDENING_HINT_FROM_PERMISSION.get(permission, "")
        gaps = gaps_by_claim.get(claim_id, [])
        queue = queue_by_claim.get(claim_id, [])
        evidence_local_required = [
            str(g.get("missing_evidence") or g.get("description") or "").strip()
            for g in gaps
            if str(g.get("missing_evidence") or g.get("description") or "").strip()
        ]
        # Route hints from queue items: measurement / observation / contrast
        measurement_route = [
            str(q.get("validation_requirement", "")).strip()
            for q in queue
            if "measur" in str(q.get("validation_requirement", "")).lower()
        ]
        observation_route = [
            str(q.get("validation_requirement", "")).strip()
            for q in queue
            if "observ" in str(q.get("validation_requirement", "")).lower()
        ]
        contrast_route = [
            str(q.get("validation_requirement", "")).strip()
            for q in queue
            if "contrast" in str(q.get("validation_requirement", "")).lower()
            or "compare" in str(q.get("validation_requirement", "")).lower()
        ]
        upgrade_condition = ""
        hold_reason = ""
        if hardening_hint == "do_not_upgrade":
            hold_reason = (
                f"permission={permission}: claim cannot upgrade until "
                f"blocking evidence resolved"
            )
        elif hardening_hint == "blocking_evidence_gap":
            hold_reason = (
                f"permission={permission}: blocked on {len(gaps)} evidence gap(s)"
            )
        elif hardening_hint == "additional_evidence_required":
            upgrade_condition = (
                f"resolve {len(gaps)} evidence gap(s) + hardening route(s)"
            )
        else:
            upgrade_condition = "evidence already present supports upgrade attempt"

        out.append({
            "claim_id": claim_id,
            "evidence_local_required": evidence_local_required,
            "baseline_hardening_state": str(row.get("baseline_hardening_state", "")),
            "contrast_route": contrast_route,
            "observation_route": observation_route,
            "measurement_route": measurement_route,
            "instrument_dependency": list(row.get("instrument_dependency", []) or []),
            "validity_domain": str(row.get("validity_domain", "")),
            "upgrade_condition": upgrade_condition,
            "hold_degrade_block_reason": hold_reason,
            "permission_state": permission,
            "__phase__": 4,
            "__canonical_unit__": "claim_upgrade_candidate",
        })
    return out


# ── Phase 5 — financial_exposure_case ───────────────────────────────────


_FINANCE_READINESS_LADDER = (
    "screening_only",
    "range_bound_preliminary",
    "decision_grade_range",
    "partially_hardened_finance",
    "verification_ready_finance",
    "verification_supported_finance",
    "verified_finance",
)


def to_financial_exposure_case_register(
    financial_exposure_register: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """Project motor_045 financial exposure register into Phase 5 unit.

    The decision_finance_posture is derived from the row's existing
    `support_state` if present, defaulting to `screening_only` for
    sparse data.
    """
    out: list[dict[str, Any]] = []
    for row in financial_exposure_register or []:
        if not isinstance(row, dict):
            continue
        support = str(row.get("support_state", "")).lower()
        # Map support_state to finance ladder
        if "verified" in support:
            posture = "verified_finance"
        elif "verification_supported" in support:
            posture = "verification_supported_finance"
        elif "verification_ready" in support:
            posture = "verification_ready_finance"
        elif "partially_hardened" in support:
            posture = "partially_hardened_finance"
        elif "decision" in support:
            posture = "decision_grade_range"
        elif "range" in support or "screening" not in support and support:
            posture = "range_bound_preliminary"
        else:
            posture = "screening_only"

        out.append({
            "exposure_case_id": str(row.get("case_id") or row.get("exposure_id") or ""),
            "decision_front": str(row.get("decision_front", "")),
            "asset_boundary": str(row.get("asset_boundary", "")),
            "baseline_dependency_state": str(row.get("baseline_dependency_state", "unknown")),
            "tariff_basis_state": str(row.get("tariff_basis_state", "unknown")),
            "cost_basis_state": str(row.get("cost_basis_state", "unknown")),
            "benefit_driver_family": list(row.get("benefit_driver_family", []) or []),
            "horizon_basis": str(row.get("horizon_basis", "")),
            "discount_basis_rule": str(row.get("discount_basis_rule", "")),
            "regulatory_dependency_state": str(row.get("regulatory_dependency_state", "")),
            "publication_ceiling": str(row.get("publication_ceiling", "")),
            "decision_finance_posture": posture,
            "raw_row": row,  # preserve full source row for narrator/audit
            "__phase__": 5,
            "__canonical_unit__": "financial_exposure_case",
        })
    return out


# ── Phase 6 — compliance_applicability_case ─────────────────────────────


_COMPLIANCE_LADDER = (
    "rule_family_relevant",
    "trigger_plausible",
    "trigger_partially_supported",
    "trigger_confirmed",
    "applicability_likely",
    "applicability_confirmed",
    "compliance_open",
)


def to_compliance_applicability_case_register(
    regulatory_flag_bundle: list[dict[str, Any]] | dict[str, Any] | None,
) -> list[dict[str, Any]]:
    """Project motor_053 / motor_012 regulatory bundle into Phase 6 unit.

    Sparse data → `rule_family_relevant` as default posture.
    """
    if not regulatory_flag_bundle:
        return []
    flags = (
        regulatory_flag_bundle
        if isinstance(regulatory_flag_bundle, list)
        else list(regulatory_flag_bundle.get("flags", []) or [])
    )
    out: list[dict[str, Any]] = []
    for flag in flags:
        if not isinstance(flag, dict):
            continue
        trigger_fields_missing = list(flag.get("missing_trigger_fields", []) or [])
        confirmed = bool(flag.get("trigger_confirmed", False))
        if confirmed:
            state = "trigger_confirmed"
        elif trigger_fields_missing and len(trigger_fields_missing) < 3:
            state = "trigger_partially_supported"
        elif flag.get("trigger_plausible", False):
            state = "trigger_plausible"
        else:
            state = "rule_family_relevant"

        out.append({
            "compliance_case_id": str(flag.get("flag_id") or flag.get("rule_id") or ""),
            "jurisdiction": str(flag.get("jurisdiction", "")),
            "authority_source": str(flag.get("authority_source", "")),
            "rule_family": str(flag.get("rule_family") or flag.get("rule_name") or ""),
            "rule_version": str(flag.get("rule_version", "")),
            "asset_boundary": str(flag.get("asset_boundary", "")),
            "subsystem_boundary": str(flag.get("subsystem_boundary", "")),
            "missing_trigger_fields": trigger_fields_missing,
            "threshold_dependency": str(flag.get("threshold_dependency", "")),
            "exception_path": str(flag.get("exception_path", "")),
            "publication_ceiling": str(flag.get("publication_ceiling", "screening_only")),
            "applicability_state": state,
            "raw_flag": flag,
            "__phase__": 6,
            "__canonical_unit__": "compliance_applicability_case",
        })
    return out


# ── Phase 7 — belief_revision_event ─────────────────────────────────────


def to_belief_revision_event_register(
    belief_revision_log: list[dict[str, Any]] | None,
    contradiction_register: list[dict[str, Any]] | None = None,
) -> list[dict[str, Any]]:
    """Project motor_020 / motor_054 belief-update rows into Phase 7 unit.

    Each event must record: target_object, prior_state, trigger_event,
    dependency_type, causal_statement, scope_impact, propagation_scope,
    publication_consequence, lifecycle_action.
    """
    out: list[dict[str, Any]] = []
    for entry in belief_revision_log or []:
        if not isinstance(entry, dict):
            continue
        out.append({
            "event_id": str(entry.get("event_id") or entry.get("revision_id") or ""),
            "target_object": str(entry.get("target_object") or entry.get("target_id") or ""),
            "prior_state": str(entry.get("prior_state", "")),
            "trigger_event": str(entry.get("trigger_event") or entry.get("trigger", "")),
            "dependency_type": str(entry.get("dependency_type", "")),
            "causal_statement": str(entry.get("causal_statement") or entry.get("reason", "")),
            "scope_impact": str(entry.get("scope_impact", "")),
            "propagation_scope": list(entry.get("propagation_scope", []) or []),
            "publication_consequence": str(entry.get("publication_consequence", "")),
            "lifecycle_action": str(entry.get("lifecycle_action") or entry.get("action", "")),
            "__phase__": 7,
            "__canonical_unit__": "belief_revision_event",
        })
    # Also fold contradictions as belief-revision events of type 'contradiction_preserved'
    for cr in contradiction_register or []:
        if not isinstance(cr, dict):
            continue
        out.append({
            "event_id": str(cr.get("contradiction_id") or ""),
            "target_object": str(cr.get("subject", "")),
            "prior_state": "uncontradicted",
            "trigger_event": "contradiction_detected",
            "dependency_type": "evidence_conflict",
            "causal_statement": str(cr.get("description", "")),
            "scope_impact": "claim_visibility_only",
            "propagation_scope": list(cr.get("affected_claims", []) or []),
            "publication_consequence": "preserve_contradiction_in_report",
            "lifecycle_action": "hold",
            "__phase__": 7,
            "__canonical_unit__": "belief_revision_event",
        })
    return out


# ── Phase 8 — decision_admissibility_case ───────────────────────────────


# Canonical action families per Phase 8 Master Doc §7.2.
PHASE_8_ACTION_FAMILIES: tuple[str, ...] = (
    "inspect",
    "measure",
    "classify",
    "pilot",
    "design",
    "procure",
    "implement",
    "defer",
)


def _normalize_action_family(raw_action: str) -> str:
    """Map free-form TAD action strings to the 8 canonical action families."""
    s = (raw_action or "").lower()
    if any(t in s for t in ("inspect", "field_visit", "site_visit", "verify_in_field")):
        return "inspect"
    if any(t in s for t in ("measure", "meter", "instrument", "monitor", "datalog")):
        return "measure"
    if any(t in s for t in ("classify", "categorize", "screen", "triage")):
        return "classify"
    if any(t in s for t in ("pilot", "trial", "prove_out", "demonstration")):
        return "pilot"
    if any(t in s for t in ("design", "engineer", "specify")):
        return "design"
    if any(t in s for t in ("procure", "tender", "rfp", "buy")):
        return "procure"
    if any(t in s for t in ("implement", "deploy", "execute", "install", "act_now")):
        return "implement"
    if any(t in s for t in ("defer", "do_not", "hold", "block", "wait")):
        return "defer"
    return "classify"  # safe default — needs more triage


def to_decision_admissibility_case_register(
    tad_action_plan: list[dict[str, Any]] | None,
    no_go_signals: list[dict[str, Any]] | None = None,
) -> list[dict[str, Any]]:
    """Project motor_033 / motor_054 TAD action plan into Phase 8 unit.

    Each row carries: target_action_family (mapped to the 8 canonical
    families), action_scope, current_support_posture, downside_class,
    irreversibility_class, regulatory_dependency, unresolved_blockers,
    required_evidence_burden, publication_ceiling.

    Also produces a derived `defer_investigate_act_map` and `no_go_register`
    via the action_family taxonomy.
    """
    out: list[dict[str, Any]] = []
    for row in tad_action_plan or []:
        if not isinstance(row, dict):
            continue
        action_family = _normalize_action_family(
            str(row.get("action_family") or row.get("action") or "")
        )
        out.append({
            "decision_case_id": str(row.get("action_id") or row.get("tad_id") or ""),
            "target_action_family": action_family,
            "action_scope": str(row.get("action_scope") or row.get("scope", "")),
            "current_support_posture": str(row.get("current_support") or row.get("evidence_state", "")),
            "downside_class": str(row.get("downside_class", "")),
            "irreversibility_class": str(row.get("irreversibility_class", "")),
            "regulatory_dependency": str(row.get("regulatory_dependency", "")),
            "unresolved_blockers": list(row.get("unresolved_blockers") or row.get("blockers", []) or []),
            "required_evidence_burden": list(row.get("required_evidence_burden") or row.get("evidence_needed", []) or []),
            "publication_ceiling": str(row.get("publication_ceiling", "")),
            "linked_claim_id": str(row.get("linked_claim") or row.get("linked_claim_id", "")),
            "__phase__": 8,
            "__canonical_unit__": "decision_admissibility_case",
        })
    # Add no_go entries
    for signal in no_go_signals or []:
        if not isinstance(signal, dict):
            continue
        out.append({
            "decision_case_id": str(signal.get("signal_id") or ""),
            "target_action_family": "defer",
            "action_scope": str(signal.get("scope", "")),
            "current_support_posture": "insufficient_for_action",
            "downside_class": str(signal.get("downside_class", "high")),
            "irreversibility_class": str(signal.get("irreversibility_class", "")),
            "regulatory_dependency": "",
            "unresolved_blockers": list(signal.get("blockers", []) or []),
            "required_evidence_burden": [],
            "publication_ceiling": "no_go",
            "linked_claim_id": str(signal.get("linked_claim", "")),
            "__phase__": 8,
            "__canonical_unit__": "decision_admissibility_case",
            "__no_go__": True,
        })
    return out


def derive_defer_investigate_act_map(
    decision_admissibility_register: list[dict[str, Any]],
) -> dict[str, list[str]]:
    """Bucket Phase 8 cases into the canonical defer/investigate/act map."""
    out: dict[str, list[str]] = {"defer": [], "investigate": [], "act": []}
    for row in decision_admissibility_register or []:
        fam = row.get("target_action_family", "")
        cid = row.get("decision_case_id", "")
        if fam in ("defer",):
            out["defer"].append(cid)
        elif fam in ("inspect", "measure", "classify", "pilot"):
            out["investigate"].append(cid)
        elif fam in ("design", "procure", "implement"):
            out["act"].append(cid)
    return out
