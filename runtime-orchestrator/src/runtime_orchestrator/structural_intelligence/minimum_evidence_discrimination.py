"""
AI-SCAFFOLDING — see AI_SCAFFOLDING_REGISTRY.md entry S9.
This module contains per-asset-family `if family == "..."` branches with
hardcoded language strings written by Claude during V1 RECOVERY. The
framework should derive this language from asset_archetypes.yaml +
process_logic.yaml + active pattern specs. DO NOT add new families here;
add them to asset_archetypes.yaml. Will be reduced to lookups in V4.
"""
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

    if target_type == "cold_chain_facility":
        rows.append(
            MinimumEvidenceDiscriminationRecord(
                rival_hypotheses=[
                    "Refrigeration duty dominates economics.",
                    "Infiltration through docks and door cycles dominates losses.",
                    "Defrost discipline and equipment maintenance dominate operating cost.",
                ],
                minimum_evidence="Temperature zone log + door cycle profile + refrigeration inventory + defrost schedule + dock seal audit",
                source="operator BMS, refrigeration controls, dock-cycle records, and maintenance log",
                what_it_confirms="Whether the dominant cost driver sits in equipment duty, envelope infiltration, or maintenance discipline.",
                what_it_falsifies="The assumption that area-normalized energy intensity alone is enough to compare cold-chain peers.",
                unlocks=[
                    "thermal-boundary redesign hypothesis",
                    "refrigeration vs infiltration prioritization",
                    "fair cold-chain peer set construction",
                ],
            ).to_dict()
        )

    if target_type == "warehouse_distribution":
        rows.append(
            MinimumEvidenceDiscriminationRecord(
                rival_hypotheses=[
                    "Charging-window peak demand dominates economics.",
                    "Dock cycles and infiltration dominate operating cost.",
                    "Service-level intensity drives the loss story (movement, throughput).",
                ],
                minimum_evidence="Utility bill intervals + tariff schedule + charging schedule + MHE inventory + dock activity profile + service-level proxy",
                source="operator dispatch records, utility bills, MHE telemetry, dock controls",
                what_it_confirms="Whether the dominant cost driver is tariff exposure, thermal exchange via docks, or operational intensity.",
                what_it_falsifies="The assumption that area-normalized EUI alone is a valid warehouse comparison basis.",
                unlocks=[
                    "tariff orchestration hypothesis",
                    "thermal-boundary redesign hypothesis",
                    "fair warehouse peer set construction",
                ],
            ).to_dict()
        )

    if target_type in {"datacenter", "data_center"}:
        rows.append(
            MinimumEvidenceDiscriminationRecord(
                rival_hypotheses=[
                    "PUE composition driven by IT-load split (not facility losses).",
                    "Cooling topology and free-cooling capture dominate operating cost.",
                    "Redundancy posture (Tier-N) drives over-provisioning loss.",
                ],
                minimum_evidence="IT-load metering + facility metering + one-line diagram + cooling inventory + containment audit",
                source="operator DCIM, facility metering, redundancy audit",
                what_it_confirms="Whether the dominant cost driver is IT-load split, cooling topology, or redundancy over-provisioning.",
                what_it_falsifies="The assumption that PUE alone is a valid comparison basis without IT-load and redundancy bounds.",
                unlocks=[
                    "PUE composition reframe",
                    "cooling redesign hypothesis",
                    "redundancy posture audit",
                ],
            ).to_dict()
        )

    if target_type in {"infrastructure_node", "rail_terminal", "rail_logistics_node", "port_terminal"}:
        rows.append(
            MinimumEvidenceDiscriminationRecord(
                rival_hypotheses=[
                    "Continuity duty (always-on signaling, switching, refrigeration) dominates base load.",
                    "Dispatch posture and traffic intensity drive movement-related cost.",
                    "Maintenance reality of long-lived assets dominates lifecycle economics more than energy intensity.",
                ],
                minimum_evidence="Dispatch records + signaling and substation inventory + continuity-load metering + preventive maintenance log + traffic intensity profile",
                source="operator dispatch, signal-engineering, traction-power and maintenance records",
                what_it_confirms="Whether the dominant cost driver is continuity duty, dispatch traffic, or maintenance reality.",
                what_it_falsifies="The assumption that area-EUI or generic energy intensity is a valid comparison basis for an infrastructure node.",
                unlocks=[
                    "continuity duty reframe",
                    "dispatch posture audit",
                    "lifecycle vs energy capital sequencing",
                ],
            ).to_dict()
        )

    if target_type == "logistics_terminal":
        rows.append(
            MinimumEvidenceDiscriminationRecord(
                rival_hypotheses=[
                    "Continuity duty (reefer / shore power) dominates base load.",
                    "Dispatch posture and yard-tractor fleet drive movement intensity.",
                    "Refrigeration and cold-ironing capture drive operating envelope.",
                ],
                minimum_evidence="Reefer runtime log + dispatch log + shore-power records + intermodal throughput + fleet inventory",
                source="terminal operations, dispatch and reefer telemetry, intermodal records",
                what_it_confirms="Whether the dominant cost driver is continuity duty, dispatch posture, or thermal continuity.",
                what_it_falsifies="The assumption that area-EUI is a valid comparison basis for a logistics terminal.",
                unlocks=[
                    "continuity duty reframe",
                    "dispatch posture audit",
                    "intermodal throughput peer construction",
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

