from __future__ import annotations

from .schemas import MinimumEvidenceDiscriminationRecord


def build_minimum_evidence_for_discrimination_register(
    *,
    target_definition: dict,
    dominant_variable_register: list[dict],
    cross_layer_conflict_register: list[dict],
    problem_framing_register: list[dict],
    conditional_redesign_register: list[dict],
) -> list[dict]:
    target_type = str(target_definition.get("target_type", "")).strip().lower()
    rows: list[dict] = []

    if target_type == "commercial_building":
        rows.append(
            MinimumEvidenceDiscriminationRecord(
                rival_hypotheses=[
                    "Owner-controllable base-building upside dominates.",
                    "Tenant-driven loads dominate realized economics.",
                    "Compliance-driven capital logic dominates the near-term decision.",
                ],
                minimum_evidence="Utility bills + tenant metering map + BMS / central plant topology + LL97 filing basis",
                source="owner / operator records + public LL84/LL97 records",
                what_it_confirms="Whether public benchmarking can be translated into owner economics, compliance strategy, or tenant-boundary redesign.",
                what_it_falsifies="The assumption that public energy intensity alone is enough to justify owner-side retrofit logic.",
                unlocks=[
                    "bounded retrofit admissibility",
                    "compliance screening posture",
                    "lease / submetering redesign hypothesis",
                ],
            ).to_dict()
        )

    if target_type == "manufacturing_facility":
        rows.append(
            MinimumEvidenceDiscriminationRecord(
                rival_hypotheses=[
                    "Structural process load dominates.",
                    "Support-system waste dominates.",
                    "Maintenance / reliability dominates economics.",
                ],
                minimum_evidence="Throughput by shift + utility bills + equipment inventory + downtime logs",
                source="operator production, utility, engineering, and maintenance records",
                what_it_confirms="Whether the economic bottleneck sits in process duty, support systems, or uptime discipline.",
                what_it_falsifies="The assumption that visible utility intensity alone is enough to prioritize efficiency CAPEX.",
                unlocks=[
                    "process redesign vs utility optimization",
                    "maintenance-priority hypothesis",
                    "capital sequencing",
                ],
            ).to_dict()
        )

    if not rows:
        evidence_needed = []
        if problem_framing_register:
            evidence_needed = list(problem_framing_register[0].get("evidence_needed", []) or [])
        rows.append(
            MinimumEvidenceDiscriminationRecord(
                rival_hypotheses=["Current dominant hypothesis", "Alternative structural explanation"],
                minimum_evidence=" + ".join(evidence_needed) if evidence_needed else "Targeted discriminating evidence still needs to be defined.",
                source="case-specific evidence request",
                what_it_confirms="Which structural hypothesis deserves further modeling.",
                what_it_falsifies="Generic, non-discriminating data collection.",
                unlocks=["better-bounded next question"],
            ).to_dict()
        )

    _ = dominant_variable_register
    _ = cross_layer_conflict_register
    _ = conditional_redesign_register
    return rows

