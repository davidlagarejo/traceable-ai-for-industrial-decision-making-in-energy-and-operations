from __future__ import annotations

from .levels import EvidenceMaturityLevel
from .schemas import ClaimTemplate


def _claim(
    claim_name: str,
    description: str,
    minimum_maturity_by_variable: dict[str, EvidenceMaturityLevel],
    allowed_outputs: list[str],
    prohibited_outputs: list[str],
    required_evidence: list[str],
) -> ClaimTemplate:
    return ClaimTemplate(
        claim_name=claim_name,
        description=description,
        required_variables=list(minimum_maturity_by_variable.keys()),
        minimum_maturity_by_variable=minimum_maturity_by_variable,
        allowed_outputs=allowed_outputs,
        prohibited_outputs=prohibited_outputs,
        required_evidence=list(required_evidence),
        upgrade_path=list(required_evidence),
    )


CLAIM_TEMPLATES: dict[str, ClaimTemplate] = {
    "asset_identity_confirmed_claim": _claim(
        "asset_identity_confirmed_claim",
        "Confirms that the target is a bounded operating asset rather than issuer context.",
        {
            "asset_vs_entity_classification": EvidenceMaturityLevel.L3,
            "address": EvidenceMaturityLevel.L3,
            "site_boundary": EvidenceMaturityLevel.L2,
        },
        ["operating-asset classification", "technical report eligibility"],
        ["entity-only technical report", "asset-level numeric claims without identity"],
        ["assessor or property record", "official owner asset page", "parcel/building identifier match"],
    ),
    "numeric_eui_claim": _claim(
        "numeric_eui_claim",
        "Numeric EUI claim based on asset-specific evidence.",
        {
            "GFA": EvidenceMaturityLevel.L3,
            "EUI": EvidenceMaturityLevel.L3,
        },
        ["numeric EUI display", "asset-intensity comparison with bounded caveats"],
        ["proxy-only intensity claims", "asset penalty math without scale basis"],
        ["PLUTO / assessor GFA", "LL84 or bill-derived baseline"],
    ),
    "energy_savings_claim": _claim(
        "energy_savings_claim",
        "Savings claim for a candidate measure or operational change.",
        {
            "utility_bills": EvidenceMaturityLevel.L3,
            "tariff_class": EvidenceMaturityLevel.L2,
            "owner_control_boundary": EvidenceMaturityLevel.L2,
            "candidate_measure": EvidenceMaturityLevel.L2,
            "HVAC_type": EvidenceMaturityLevel.L2,
        },
        ["bounded savings range", "scenario-based savings narrative"],
        ["guaranteed savings", "verification-grade savings"],
        ["12-24 months utility bills", "system inventory", "control-boundary confirmation"],
    ),
    "roi_directional_claim": _claim(
        "roi_directional_claim",
        "Directional economics or indicative ROI framing.",
        {
            "asset_type": EvidenceMaturityLevel.L1,
            "GFA": EvidenceMaturityLevel.L1,
            "tariff_class": EvidenceMaturityLevel.L1,
            "candidate_measure": EvidenceMaturityLevel.L1,
            "CAPEX": EvidenceMaturityLevel.L1,
        },
        ["directional economics", "value-of-information framing"],
        ["single-point ROI", "financing-grade return claim"],
        ["scale proxy", "tariff proxy", "benchmark CAPEX"],
    ),
    "roi_range_claim": _claim(
        "roi_range_claim",
        "Preliminary ROI range with explicit low-confidence caveats.",
        {
            "GFA": EvidenceMaturityLevel.L2,
            "utility_bills": EvidenceMaturityLevel.L2,
            "tariff_class": EvidenceMaturityLevel.L2,
            "operating_schedule": EvidenceMaturityLevel.L2,
            "HVAC_type": EvidenceMaturityLevel.L2,
            "candidate_measure": EvidenceMaturityLevel.L2,
            "CAPEX": EvidenceMaturityLevel.L1,
            "owner_control_boundary": EvidenceMaturityLevel.L2,
        },
        ["preliminary ROI range", "range-based payback screening"],
        ["investment-grade ROI", "bankability claims"],
        ["asset-specific consumption", "schedule evidence", "preliminary system basis"],
    ),
    "roi_scenario_claim": _claim(
        "roi_scenario_claim",
        "Scenario-based ROI suitable for stronger decision framing.",
        {
            "GFA": EvidenceMaturityLevel.L3,
            "utility_bills": EvidenceMaturityLevel.L3,
            "tariff_class": EvidenceMaturityLevel.L3,
            "operating_schedule": EvidenceMaturityLevel.L2,
            "HVAC_type": EvidenceMaturityLevel.L2,
            "candidate_measure": EvidenceMaturityLevel.L2,
            "CAPEX": EvidenceMaturityLevel.L2,
            "owner_control_boundary": EvidenceMaturityLevel.L2,
        },
        ["scenario-based ROI", "bounded downside/upside bands"],
        ["verified ROI", "finance-grade closure"],
        ["bill-based tariff", "capex range", "control-boundary confirmation"],
    ),
    "ll97_penalty_screening_claim": _claim(
        "ll97_penalty_screening_claim",
        "LL97 screening-level penalty or exposure estimate.",
        {
            "jurisdiction": EvidenceMaturityLevel.L3,
            "applicable_rule_family": EvidenceMaturityLevel.L2,
            "regulated_floor_area": EvidenceMaturityLevel.L2,
            "emissions": EvidenceMaturityLevel.L2,
            "penalty_rate": EvidenceMaturityLevel.L3,
        },
        ["regulatory exposure screening", "bounded penalty scenario"],
        ["compliance closure", "final legal posture"],
        ["LL84/LL97 records", "regulated floor area basis", "current rule-period threshold"],
    ),
    "compliance_screening_claim": _claim(
        "compliance_screening_claim",
        "Rule-family screening and trigger plausibility.",
        {
            "jurisdiction": EvidenceMaturityLevel.L2,
            "applicable_rule_family": EvidenceMaturityLevel.L1,
            "trigger_fields": EvidenceMaturityLevel.L1,
            "asset_vs_entity_classification": EvidenceMaturityLevel.L2,
        },
        ["rule-family screening", "trigger plausibility"],
        ["compliant/non-compliant conclusion", "filing closure"],
        ["jurisdiction confirmation", "asset-level trigger fields", "rule lookup"],
    ),
    "compliance_closure_claim": _claim(
        "compliance_closure_claim",
        "Strong compliance posture or filing-backed conclusion.",
        {
            "jurisdiction": EvidenceMaturityLevel.L3,
            "applicable_rule_family": EvidenceMaturityLevel.L3,
            "trigger_fields": EvidenceMaturityLevel.L3,
            "compliance_filing": EvidenceMaturityLevel.L4,
            "compliance_status": EvidenceMaturityLevel.L4,
        },
        ["strong bounded compliance posture"],
        ["legal opinion beyond verified scope", "unsupported closure"],
        ["official filing", "validated emissions baseline", "independent review"],
    ),
    "process_change_hypothesis_claim": _claim(
        "process_change_hypothesis_claim",
        "Hypothesis that a process or workflow change may be valuable.",
        {
            "operating_schedule": EvidenceMaturityLevel.L1,
            "load_driver": EvidenceMaturityLevel.L1,
            "process_flow": EvidenceMaturityLevel.L1,
        },
        ["process hypothesis", "investigation queue"],
        ["process redesign recommendation", "downtime plan"],
        ["workflow description", "asset-specific operational notes"],
    ),
    "process_redesign_recommendation_claim": _claim(
        "process_redesign_recommendation_claim",
        "Recommendation to redesign or materially change process flow.",
        {
            "throughput": EvidenceMaturityLevel.L3,
            "process_flow": EvidenceMaturityLevel.L3,
            "stakeholder_control": EvidenceMaturityLevel.L2,
            "downtime_profile": EvidenceMaturityLevel.L2,
            "candidate_measure": EvidenceMaturityLevel.L2,
        },
        ["bounded redesign recommendation", "validate-first implementation pathway"],
        ["unsupported process redesign recommendation"],
        ["throughput data", "process map", "operational control confirmation"],
    ),
}


def get_claim_template(claim_name: str) -> ClaimTemplate | None:
    return CLAIM_TEMPLATES.get(claim_name)
