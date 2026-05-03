from __future__ import annotations

from typing import Any

from .schemas import ProblemFramingRecord, StructuralEvidenceState


def _var_map(dominant_variable_register: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    return {
        str(row.get("variable", "")).strip(): row
        for row in dominant_variable_register
        if str(row.get("variable", "")).strip()
    }


def build_problem_framing_register(
    *,
    target_definition: dict[str, Any],
    system_abstraction: dict[str, Any],
    dominant_variable_register: list[dict[str, Any]],
    cross_layer_conflict_register: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    target_type = str(target_definition.get("target_type", "")).strip().lower()
    decision_intent = str(target_definition.get("decision_intent", "")).strip() or "improve asset performance"
    variables = _var_map(dominant_variable_register)
    conflicts = {str(row.get("conflict", "")).strip().lower(): row for row in cross_layer_conflict_register}
    rows: list[dict[str, Any]] = []

    if target_type == "commercial_building":
        rows.append(
            ProblemFramingRecord(
                stated_problem=decision_intent if decision_intent != "improve asset performance" else "Need retrofit / compliance action",
                reframed_problem="Need to determine whether owner-managed base-building systems, tenant-driven loads, or LL97 exposure actually dominate value and capital logic.",
                why_original_framing_may_be_wrong="The visible building question may collapse three different issues: owner control, tenant load allocation, and compliance-driven capital exposure.",
                evidence_needed=[
                    "utility bills",
                    "tenant metering map",
                    "lease responsibility matrix",
                    "central plant / BMS topology",
                    "LL97 filing basis",
                ],
                strategic_risk="Owner capital can be aimed at the wrong load boundary or the wrong compliance pathway.",
                evidence_state=StructuralEvidenceState.CONDITIONAL_HYPOTHESIS,
                linked_layers=["operation", "control/responsibility", "regulation", "finance", "commercial"],
            ).to_dict()
        )
        if "regulation vs control boundary" in conflicts:
            rows.append(
                ProblemFramingRecord(
                    stated_problem="Need to reduce energy or close compliance gap",
                    reframed_problem="Need to distinguish whether the problem is efficiency, control-boundary design, tenant allocation, or penalty-avoidance strategy.",
                    why_original_framing_may_be_wrong="The current question is premature because regulation and control do not yet align cleanly.",
                    evidence_needed=["tenant metering", "lease responsibility", "LL97 filing basis"],
                    strategic_risk="The company may solve the wrong problem and still fail to improve owner economics.",
                    evidence_state=StructuralEvidenceState.CONDITIONAL_HYPOTHESIS,
                    linked_layers=["regulation", "control/responsibility", "commercial", "finance"],
                ).to_dict()
            )

    if target_type == "manufacturing_facility":
        throughput_state = str(variables.get("throughput", {}).get("evidence_state", "ARCHETYPAL_PRIOR"))
        thermal_state = str(variables.get("thermal_duty", {}).get("evidence_state", "ARCHETYPAL_PRIOR"))
        rows.append(
            ProblemFramingRecord(
                stated_problem=decision_intent if decision_intent != "improve asset performance" else "Need energy savings or process-efficiency CAPEX",
                reframed_problem="Need to determine whether visible energy intensity is structural process load, support-system waste, or an uptime / maintenance problem.",
                why_original_framing_may_be_wrong="The company may be solving for energy before it has bounded throughput, thermal duty, and downtime as the dominant variables.",
                evidence_needed=[
                    "throughput by shift",
                    "process map",
                    "utility baseline",
                    "equipment inventory",
                    "downtime logs",
                ],
                strategic_risk="Capital can be misallocated between process redesign, utility optimization, and maintenance.",
                evidence_state=StructuralEvidenceState.CONDITIONAL_HYPOTHESIS if throughput_state != "OBSERVED_FACT" or thermal_state != "OBSERVED_FACT" else StructuralEvidenceState.OBSERVED_FACT,
                linked_layers=["physics", "operation", "energy", "finance", "maintenance"],
            ).to_dict()
        )
        if "maintenance and uptime economics may dominate visible energy symptoms" in conflicts:
            rows.append(
                ProblemFramingRecord(
                    stated_problem="Need efficiency CAPEX",
                    reframed_problem="Need to test whether reliability, downtime, and maintenance discipline dominate economics before framing an energy project.",
                    why_original_framing_may_be_wrong="Energy is visible, but it may not be the true bottleneck.",
                    evidence_needed=["downtime logs", "failure history", "scrap profile"],
                    strategic_risk="The company may optimize utility costs while the real value leak sits in uptime and quality loss.",
                    evidence_state=StructuralEvidenceState.CONDITIONAL_HYPOTHESIS,
                    linked_layers=["maintenance", "operation", "finance", "commercial"],
                ).to_dict()
            )

    if not rows:
        abstraction_state = str(system_abstraction.get("evidence_maturity", {}).get("evidence_state", "NOT_OBSERVED"))
        rows.append(
            ProblemFramingRecord(
                stated_problem=decision_intent,
                reframed_problem="The current question may be premature until dominant variables and structural contradictions are bounded.",
                why_original_framing_may_be_wrong="Current evidence does not yet show that the framed decision is the right one.",
                evidence_needed=["dominant variable evidence", "control boundary evidence", "scenario discrimination evidence"],
                strategic_risk="The system may be optimizing a secondary variable.",
                evidence_state=StructuralEvidenceState(abstraction_state) if abstraction_state in StructuralEvidenceState._value2member_map_ else StructuralEvidenceState.CONDITIONAL_HYPOTHESIS,
                linked_layers=["physics", "operation", "finance", "control/responsibility"],
            ).to_dict()
        )

    return rows
