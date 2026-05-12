"""
AI-SCAFFOLDING — see AI_SCAFFOLDING_REGISTRY.md entry S9.
Per-asset-family branches with handwritten language. Reduce to lookups in
V4 by sourcing per-family text from asset_archetypes.yaml.
"""
from __future__ import annotations

from .schemas import ConditionalRedesignRecord, StructuralEvidenceState


def _var_map(dominant_variable_register: list[dict]) -> dict[str, dict]:
    return {
        str(row.get("variable", "")).strip(): row
        for row in dominant_variable_register
        if str(row.get("variable", "")).strip()
    }


def build_conditional_redesign_register(
    *,
    target_definition: dict,
    dominant_variable_register: list[dict],
    cross_layer_conflict_register: list[dict],
    problem_framing_register: list[dict],
    competitive_comparison_register: list[dict],
) -> list[dict]:
    target_type = str(target_definition.get("target_type", "")).strip().lower()
    variables = _var_map(dominant_variable_register)
    conflicts = {str(row.get("conflict", "")).strip().lower(): row for row in cross_layer_conflict_register}
    rows: list[dict] = []

    if target_type == "commercial_building":
        owner_control_state = str(variables.get("owner_control_boundary", {}).get("evidence_state", "ARCHETYPAL_PRIOR"))
        ll97_state = str(variables.get("LL97_pathway", {}).get("evidence_state", "ARCHETYPAL_PRIOR"))
        rows.append(
            ConditionalRedesignRecord(
                hypothesis="Tenant-driven loads and unresolved control boundary weaken owner-only retrofit economics.",
                trigger_hypothesis="Tenant-driven loads and unresolved control boundary weaken owner-only retrofit economics.",
                evidence_state=StructuralEvidenceState.CONDITIONAL_HYPOTHESIS if owner_control_state != "OBSERVED_FACT" else StructuralEvidenceState.OBSERVED_FACT,
                if_confirmed="Do not treat owner-only retrofit as the primary answer; redesign the control and contract architecture first.",
                redesign_direction="Submetering, green leases, tenant after-hours policy, BMS schedule discipline, and clearer owner/tenant responsibility mapping.",
                if_falsified="Owner-managed central plant and BMS optimization may become investable before contractual redesign.",
                conflict_resolved="Regulation sits with the owner while load control and savings capture may sit with tenants or unresolved contractual boundaries.",
                economic_logic="Owner CAPEX alone may not capture value until metering, lease, and control boundaries are redesigned.",
                evidence_needed=[
                    "tenant metering map",
                    "lease responsibility matrix",
                    "BMS / central plant topology",
                    "after-hours occupancy profile",
                ],
                kill_condition="Owner-managed central plant and common-area systems dominate load and savings capture.",
                next_evidence=[
                    "tenant metering map",
                    "lease responsibility matrix",
                    "BMS / central plant topology",
                    "after-hours occupancy profile",
                ],
            ).to_dict()
        )
        if ll97_state in {"OBSERVED_FACT", "CONDITIONAL_HYPOTHESIS"}:
            rows.append(
                ConditionalRedesignRecord(
                    hypothesis="The dominant capital logic is LL97 penalty avoidance and compliance design, not pure energy-savings capture.",
                    trigger_hypothesis="The dominant capital logic is LL97 penalty avoidance and compliance design, not pure energy-savings capture.",
                    evidence_state=StructuralEvidenceState.CONDITIONAL_HYPOTHESIS,
                    if_confirmed="Frame the pathway around compliance strategy, procurement, electrification sequencing, and owner-control boundary rather than generic retrofit marketing.",
                    redesign_direction="LL97 pathway design, electrification sequencing, procurement strategy, and contract redesign around controllable loads.",
                    if_falsified="Conventional owner-controlled energy optimization may matter more than compliance-driven capital logic.",
                    conflict_resolved="Compliance exposure may dominate the economics while the intuitive retrofit-savings frame points to the wrong capital logic.",
                    economic_logic="If penalties or fuel-transition posture dominate, capital should be sequenced around compliance design rather than generic savings capture.",
                    evidence_needed=[
                        "LL97 filing basis",
                        "fuel / utility basis",
                        "covered-load boundary",
                    ],
                    kill_condition="Observed filing logic and load boundary show that owner-controlled operating savings dominate penalty avoidance economics.",
                    next_evidence=[
                        "LL97 filing basis",
                        "fuel / utility basis",
                        "covered-load boundary",
                    ],
                ).to_dict()
            )

    if target_type == "manufacturing_facility":
        throughput_state = str(variables.get("throughput", {}).get("evidence_state", "ARCHETYPAL_PRIOR"))
        downtime_state = str(variables.get("downtime", {}).get("evidence_state", "ARCHETYPAL_PRIOR"))
        rows.append(
            ConditionalRedesignRecord(
                hypothesis="Energy intensity is structurally tied to throughput, thermal duty, or curing profile rather than generic utility waste.",
                trigger_hypothesis="Energy intensity is structurally tied to throughput, thermal duty, or curing profile rather than generic utility waste.",
                evidence_state=StructuralEvidenceState.CONDITIONAL_HYPOTHESIS if throughput_state != "OBSERVED_FACT" else StructuralEvidenceState.OBSERVED_FACT,
                if_confirmed="Do not prioritize generic energy retrofit first; redesign scheduling, thermal integration, process control, or production planning.",
                redesign_direction="Thermal integration, scheduling redesign, process-control refinement, and throughput-aware operating strategy.",
                if_falsified="Target support-system waste such as compressed air, controls, idle load, and maintenance discipline before process redesign.",
                conflict_resolved="Finance may seek energy CAPEX while the real driver is structural process duty and throughput behavior.",
                economic_logic="CAPEX aimed at generic utility reduction can miss the economics if process duty, scheduling, or thermal integration actually dominate value.",
                evidence_needed=[
                    "throughput by shift",
                    "process map",
                    "utility baseline",
                    "equipment inventory",
                ],
                kill_condition="Observed evidence shows that support-system waste, not process duty, dominates the economic upside.",
                next_evidence=[
                    "throughput by shift",
                    "process map",
                    "utility baseline",
                    "equipment inventory",
                ],
            ).to_dict()
        )
        rows.append(
            ConditionalRedesignRecord(
                hypothesis="Maintenance discipline and uptime economics dominate value more than visible utility intensity.",
                trigger_hypothesis="Maintenance discipline and uptime economics dominate value more than visible utility intensity.",
                evidence_state=StructuralEvidenceState.CONDITIONAL_HYPOTHESIS if downtime_state != "OBSERVED_FACT" else StructuralEvidenceState.OBSERVED_FACT,
                if_confirmed="Prioritize reliability, downtime, scrap reduction, and spare-parts readiness before pitching efficiency CAPEX as the main answer.",
                redesign_direction="Maintenance redesign, uptime management, outage-cost reduction, and operational discipline.",
                if_falsified="Energy and support-system optimization may deserve priority over maintenance redesign.",
                conflict_resolved="Visible energy symptoms may distract from the larger economics of uptime, scrap, and reliability.",
                economic_logic="If downtime and reliability dominate value, maintenance redesign can matter more than energy retrofit to real cash flow.",
                evidence_needed=[
                    "downtime logs",
                    "failure history",
                    "scrap profile",
                    "maintenance work-order history",
                ],
                kill_condition="Observed uptime evidence shows maintenance is secondary and utility-side waste dominates the economic upside.",
                next_evidence=[
                    "downtime logs",
                    "failure history",
                    "scrap profile",
                    "maintenance work-order history",
                ],
            ).to_dict()
        )

    if target_type == "cold_chain_facility":
        rows.append(
            ConditionalRedesignRecord(
                hypothesis="Refrigeration economics may be dominated by infiltration and thermal-boundary discipline rather than equipment efficiency.",
                trigger_hypothesis="Refrigeration economics may be dominated by infiltration and thermal-boundary discipline rather than equipment efficiency.",
                evidence_state=StructuralEvidenceState.CONDITIONAL_HYPOTHESIS,
                if_confirmed="Prioritize thermal-boundary, dock-seal, and door-cycle redesign before equipment replacement.",
                redesign_direction="Thermal envelope, dock seal discipline, defrost orchestration, and refrigerant integrity.",
                if_falsified="Refrigeration equipment refresh and compressor strategy may deserve priority over envelope redesign.",
                conflict_resolved="Equipment-first retrofit may target a secondary cost driver while the real loss is structural / operational.",
                economic_logic="If infiltration and dock cycles dominate refrigeration duty, equipment-only retrofit captures less value than envelope discipline.",
                evidence_needed=[
                    "temperature zone log",
                    "door cycle profile",
                    "dock seal audit",
                    "refrigeration inventory",
                    "defrost schedule",
                ],
                kill_condition="Observed thermal-boundary evidence shows envelope is bounded and equipment replacement dominates economics.",
                next_evidence=[
                    "temperature zone log",
                    "door cycle profile",
                    "dock seal audit",
                    "refrigeration inventory",
                    "defrost schedule",
                ],
            ).to_dict()
        )

    if target_type == "warehouse_distribution":
        rows.append(
            ConditionalRedesignRecord(
                hypothesis="Warehouse economics may be dominated by tariff exposure and dock-cycle thermal exchange rather than area-normalized inefficiency.",
                trigger_hypothesis="Warehouse economics may be dominated by tariff exposure and dock-cycle thermal exchange rather than area-normalized inefficiency.",
                evidence_state=StructuralEvidenceState.CONDITIONAL_HYPOTHESIS,
                if_confirmed="Prioritize charging-window orchestration, dock-seal discipline, and control-boundary realignment before HVAC/lighting CAPEX.",
                redesign_direction="Tariff orchestration, dock thermal discipline, control-boundary alignment.",
                if_falsified="Generic efficiency retrofit may still deserve priority over operational redesign.",
                conflict_resolved="Area-normalized retrofit logic may target a secondary driver while real cost is tariff- and boundary-driven.",
                economic_logic="If charging windows and dock exchange dominate cost, area-EUI retrofit captures less value than operational discipline.",
                evidence_needed=[
                    "utility bill intervals",
                    "tariff schedule",
                    "charging schedule",
                    "MHE inventory",
                    "dock activity profile",
                ],
                kill_condition="Observed tariff and dock evidence shows charging is bounded and equipment efficiency dominates upside.",
                next_evidence=[
                    "utility bill intervals",
                    "tariff schedule",
                    "charging schedule",
                    "MHE inventory",
                    "dock activity profile",
                ],
            ).to_dict()
        )

    if not rows:
        next_evidence = []
        if problem_framing_register:
            next_evidence = list(problem_framing_register[0].get("evidence_needed", []) or [])
        rows.append(
            ConditionalRedesignRecord(
                hypothesis="Any redesign path remains premature until the dominant structural bottleneck is bounded.",
                trigger_hypothesis="Any redesign path remains premature until the dominant structural bottleneck is bounded.",
                evidence_state=StructuralEvidenceState.CONDITIONAL_HYPOTHESIS,
                if_confirmed="Reframe the redesign question around the variable that actually dominates value and risk.",
                redesign_direction="Do not redesign broadly yet; narrow the system boundary first.",
                if_falsified="A bounded redesign hypothesis may become admissible.",
                conflict_resolved="Broad redesign ambition is competing with unresolved system understanding.",
                economic_logic="Premature redesign can spend capital against the wrong bottleneck before the governing variable is discriminated.",
                evidence_needed=next_evidence,
                kill_condition="A bounded dominant variable and contradiction are observed strongly enough to support a narrower redesign path.",
                next_evidence=next_evidence,
            ).to_dict()
        )

    _ = conflicts
    _ = competitive_comparison_register
    return rows
