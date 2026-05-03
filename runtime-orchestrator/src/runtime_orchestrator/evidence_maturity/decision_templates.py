from __future__ import annotations

from .levels import EvidenceMaturityLevel
from .schemas import DecisionTemplate


def _decision(
    decision_name: str,
    description: str,
    minimum_maturity_by_variable: dict[str, EvidenceMaturityLevel],
    allowed_actions: list[str],
    blocked_actions: list[str],
    evidence_pack_focus: list[str],
) -> DecisionTemplate:
    return DecisionTemplate(
        decision_name=decision_name,
        description=description,
        required_variables=list(minimum_maturity_by_variable.keys()),
        minimum_maturity_by_variable=minimum_maturity_by_variable,
        allowed_actions=allowed_actions,
        blocked_actions=blocked_actions,
        evidence_pack_focus=evidence_pack_focus,
    )


DECISION_TEMPLATES: dict[str, DecisionTemplate] = {
    "asset_identity_confirmation": _decision(
        "asset_identity_confirmation",
        "Determine whether the target is a bounded operating asset.",
        {
            "asset_vs_entity_classification": EvidenceMaturityLevel.L3,
            "address": EvidenceMaturityLevel.L3,
            "site_boundary": EvidenceMaturityLevel.L2,
        },
        ["ACT NOW", "REQUEST EVIDENCE"],
        ["FULL TECHNICAL REPORT"],
        ["parcel/building record", "official owner property page", "benchmark or permit match"],
    ),
    "retrofit_capex": _decision(
        "retrofit_capex",
        "Advance or block retrofit CAPEX framing.",
        {
            "utility_bills": EvidenceMaturityLevel.L3,
            "HVAC_type": EvidenceMaturityLevel.L2,
            "owner_control_boundary": EvidenceMaturityLevel.L2,
            "candidate_measure": EvidenceMaturityLevel.L2,
            "CAPEX": EvidenceMaturityLevel.L2,
        },
        ["VALIDATE FIRST", "SCENARIO MODELLING"],
        ["INVESTMENT-GRADE COMMITMENT", "GUARANTEED SAVINGS"],
        ["utility bills", "system inventory", "control boundary", "CAPEX range"],
    ),
    "acquisition_underwriting_with_energy_upside": _decision(
        "acquisition_underwriting_with_energy_upside",
        "Use energy upside in underwriting or asset valuation.",
        {
            "utility_bills": EvidenceMaturityLevel.L3,
            "GFA": EvidenceMaturityLevel.L3,
            "owner_control_boundary": EvidenceMaturityLevel.L2,
            "savings": EvidenceMaturityLevel.L2,
        },
        ["SCENARIO SCREENING", "VALIDATE FIRST"],
        ["NO-GO FOR HARD UNDERWRITING WITHOUT STRONGER SUPPORT"],
        ["bill-backed baseline", "scale basis", "control boundary"],
    ),
    "compliance_investment": _decision(
        "compliance_investment",
        "Advance a compliance-motivated investment pathway.",
        {
            "jurisdiction": EvidenceMaturityLevel.L3,
            "applicable_rule_family": EvidenceMaturityLevel.L2,
            "regulated_floor_area": EvidenceMaturityLevel.L2,
            "emissions": EvidenceMaturityLevel.L2,
            "compliance_filing": EvidenceMaturityLevel.L2,
        },
        ["VALIDATE FIRST", "REGULATORY SCREENING"],
        ["LEGAL CLOSURE", "DETERMINISTIC PENALTY COMMITMENT"],
        ["public compliance records", "current rule thresholds", "filing evidence"],
    ),
    "process_redesign": _decision(
        "process_redesign",
        "Advance or defer a process-change decision.",
        {
            "throughput": EvidenceMaturityLevel.L3,
            "process_flow": EvidenceMaturityLevel.L3,
            "stakeholder_control": EvidenceMaturityLevel.L2,
            "downtime_profile": EvidenceMaturityLevel.L2,
        },
        ["INVESTIGATE THEN DECIDE", "VALIDATE FIRST"],
        ["NO PROCESS REDESIGN RECOMMENDATION WITHOUT BOTTLENECK DATA"],
        ["throughput profile", "process map", "control/approval map", "downtime tolerance"],
    ),
    "seller_or_operator_evidence_request": _decision(
        "seller_or_operator_evidence_request",
        "Request the minimum evidence pack from seller, owner, or operator.",
        {
            "asset_vs_entity_classification": EvidenceMaturityLevel.L2,
        },
        ["ACT NOW"],
        [],
        ["identity anchors", "utility bills", "system inventory", "compliance filing"],
    ),
}


def get_decision_template(decision_name: str) -> DecisionTemplate | None:
    return DECISION_TEMPLATES.get(decision_name)
