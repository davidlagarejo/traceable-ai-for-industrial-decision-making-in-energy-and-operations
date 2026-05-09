from __future__ import annotations

from typing import Any

from .schemas import text


def _contract(
    *,
    claim_id: str,
    statement: str,
    evidence_state: str,
    supporting_sources: list[str],
    assumptions: list[str],
    minimum_evidence_required: list[str],
    allowed_use: list[str],
    prohibited_use: list[str],
    current_evidence_summary: str,
) -> dict[str, Any]:
    return {
        "claim_id": claim_id,
        "claim_family": "congruence_intelligence_lane",
        "statement": statement,
        "permission": "allowed" if evidence_state in {"OBSERVED_FACT", "CONDITIONAL_HYPOTHESIS", "WEAK_SIGNAL", "ARCHETYPAL_PRIOR"} else "prohibited",
        "evidence_state": evidence_state,
        "supporting_sources": supporting_sources or ["motor_054.congruence_claim_governor"],
        "assumptions": assumptions,
        "falsification_condition": "Asset-specific evidence proves the current congruence framing is wrong, incomplete, or too weak for the intended use.",
        "minimum_evidence_required": minimum_evidence_required,
        "allowed_use": allowed_use,
        "prohibited_use": prohibited_use,
        "current_evidence_summary": current_evidence_summary,
    }


def build_congruence_claim_contract_register(
    *,
    strategic_gold_nugget_register: list[dict[str, Any]],
    strategic_gold_nugget_source: str = "motor_054.strategic_gold_nugget_register",
    congruence_action_priority_register: list[dict[str, Any]],
    invalid_comparison_risk_register: list[dict[str, Any]],
    measurement_strategy_register: list[dict[str, Any]],
    regulatory_physics_register: list[dict[str, Any]],
    finance_physics_dependency_register: list[dict[str, Any]],
    loss_pattern_hypothesis_register: list[dict[str, Any]],
    culture_execution_proxy_register: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []

    if invalid_comparison_risk_register:
        first = invalid_comparison_risk_register[0]
        rows.append(
            _contract(
                claim_id="congruence_invalid_comparison_claim",
                statement="Peer or benchmark logic must remain bounded when the comparison basis is structurally invalid.",
                evidence_state="CONDITIONAL_HYPOTHESIS",
                supporting_sources=["motor_051.invalid_comparison_risk_register"],
                assumptions=["Comparison validity depends on normalization, not just asset label similarity."],
                minimum_evidence_required=list(first.get("required_normalization", []) or []),
                allowed_use=["Bounded peer warning", "Fair-comparison gating", "Do-not-compare-yet posture"],
                prohibited_use=["Peer superiority", "Transferable ROI", "Local waste diagnosis from invalid comparison"],
                current_evidence_summary=text(first.get("trigger")),
            )
        )

    if measurement_strategy_register:
        first = measurement_strategy_register[0]
        rows.append(
            _contract(
                claim_id="congruence_measurement_minimality_claim",
                statement="The next valid measurement step should be the cheapest evidence path that discriminates the dominant hypothesis.",
                evidence_state="ARCHETYPAL_PRIOR",
                supporting_sources=["motor_052.measurement_strategy_register"],
                assumptions=["Measurement strategy should follow hypothesis discrimination, not hardware reflex."],
                minimum_evidence_required=[text(first.get("minimum_measurement"))],
                allowed_use=["Measurement minimality guidance", "Bills-first or logs-first framing"],
                prohibited_use=["Broad sensor rollout recommendation without hypothesis"],
                current_evidence_summary=text(first.get("why")),
            )
        )

    if loss_pattern_hypothesis_register:
        first = loss_pattern_hypothesis_register[0]
        rows.append(
            _contract(
                claim_id="congruence_loss_pattern_claim",
                statement="Recurring loss patterns can justify bounded hypotheses without becoming local diagnosis.",
                evidence_state=text(first.get("evidence_state")) or "ARCHETYPAL_PRIOR",
                supporting_sources=["motor_052.loss_pattern_hypothesis_register"],
                assumptions=["Structural patterns recur by asset family but must still be locally falsified."],
                minimum_evidence_required=list(first.get("minimum_local_evidence", []) or []),
                allowed_use=["Structural pattern framing", "Targeted evidence request"],
                prohibited_use=["Observed local leak or waste diagnosis without proof"],
                current_evidence_summary=text(first.get("hypothesis")),
            )
        )

    if regulatory_physics_register:
        first = regulatory_physics_register[0]
        rows.append(
            _contract(
                claim_id="congruence_regulatory_physics_claim",
                statement="Regulatory and permit signals can support bounded physical or redesign hypotheses without proving current operating truth.",
                evidence_state=text(first.get("evidence_state")) or "CONDITIONAL_HYPOTHESIS",
                supporting_sources=["motor_053.regulatory_physics_register"],
                assumptions=["Public rules and permits imply bounded physical domains, not closed operating condition."],
                minimum_evidence_required=list(first.get("what_it_supports", []) or []),
                allowed_use=["Permit-to-physics framing", "Constraint-aware redesign gating"],
                prohibited_use=["Compliance closure", "Proof of current operation from permit context alone"],
                current_evidence_summary=text(first.get("physical_implication")),
            )
        )

    if finance_physics_dependency_register:
        first = finance_physics_dependency_register[0]
        rows.append(
            _contract(
                claim_id="congruence_finance_physics_claim",
                statement="Financial logic is admissible only to the degree that its physical dependency is explicitly bounded.",
                evidence_state=text(first.get("evidence_state")) or "CONDITIONAL_HYPOTHESIS",
                supporting_sources=["motor_053.finance_physics_dependency_register"],
                assumptions=["Cost or capital logic can fail if the physical dependency is misidentified."],
                minimum_evidence_required=list(first.get("evidence_needed", []) or []),
                allowed_use=["Cost-driver dependency framing", "Capital-at-risk under uncertainty"],
                prohibited_use=["Closed ROI", "Bankability", "Savings closure without physical dependency evidence"],
                current_evidence_summary=text(first.get("risk_if_wrong")),
            )
        )

    if culture_execution_proxy_register:
        first = culture_execution_proxy_register[0]
        rows.append(
            _contract(
                claim_id="congruence_culture_proxy_claim",
                statement="Execution discipline should be treated only as a weak or conditional proxy unless direct organizational evidence exists.",
                evidence_state=text(first.get("evidence_state")) or "WEAK_SIGNAL",
                supporting_sources=["motor_053.culture_execution_proxy_register"],
                assumptions=["Operational ownership signals can matter without proving culture as fact."],
                minimum_evidence_required=["direct organizational evidence", "maintenance and schedule ownership evidence"],
                allowed_use=["Weak-signal governance framing", "Ownership bottleneck hypothesis"],
                prohibited_use=["Strong culture diagnosis without direct evidence"],
                current_evidence_summary=text(first.get("proxy_signal")),
            )
        )

    if strategic_gold_nugget_register:
        first = strategic_gold_nugget_register[0]
        rows.append(
            _contract(
                claim_id="congruence_gold_nugget_claim",
                statement="Strategic gold nuggets must stay evidence-bounded and tied to a concrete dependency or invalid frame.",
                evidence_state=text(first.get("evidence_state")) or "CONDITIONAL_HYPOTHESIS",
                supporting_sources=[text(strategic_gold_nugget_source) or "motor_054.strategic_gold_nugget_register"],
                assumptions=["A surprising interpretation is only useful if it is traceable to the governing evidence and constraint structure."],
                minimum_evidence_required=[text(first.get("linked_dependency"))],
                allowed_use=["Executive reframe", "Decision-shock insight"],
                prohibited_use=["Clever but ungrounded narrative leap"],
                current_evidence_summary=text(first.get("gold_nugget")),
            )
        )

    if congruence_action_priority_register:
        first = congruence_action_priority_register[0]
        rows.append(
            _contract(
                claim_id="congruence_action_priority_claim",
                statement="Congruence-side actions are admissible only when they stay linked to evidence gaps, invalid frames or blocked economic logic.",
                evidence_state="CONDITIONAL_HYPOTHESIS",
                supporting_sources=["motor_054.congruence_action_priority_register"],
                assumptions=["Strategic action should remain evidence-linked and bounded by cheapest valid evidence first."],
                minimum_evidence_required=list(first.get("evidence_needed", []) or []),
                allowed_use=["Bounded action priority", "Validate-first strategic posture"],
                prohibited_use=["Action posture disconnected from evidence or claim governance"],
                current_evidence_summary=text(first.get("why")),
            )
        )

    return rows
