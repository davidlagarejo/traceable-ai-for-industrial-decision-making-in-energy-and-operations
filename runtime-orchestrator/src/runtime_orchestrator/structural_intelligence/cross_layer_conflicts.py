from __future__ import annotations

from typing import Any

from .schemas import CrossLayerConflictRecord, StructuralEvidenceState


def _var_map(dominant_variable_register: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    return {
        str(row.get("variable", "")).strip(): row
        for row in dominant_variable_register
        if str(row.get("variable", "")).strip()
    }


def _decision_map(decision_front_actions: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    return {
        str(row.get("decision_front", "")).strip().lower(): row
        for row in decision_front_actions
        if str(row.get("decision_front", "")).strip()
    }


def _financial_text(financial_exposure_register: list[dict[str, Any]]) -> str:
    parts: list[str] = []
    for row in financial_exposure_register:
        for key in ("assumption", "current_support", "downside_if_wrong", "financial_consequence"):
            value = str(row.get(key, "")).strip()
            if value:
                parts.append(value.lower())
    return " ".join(parts)


def _claim_permissions(claim_permission_register: list[dict[str, Any]]) -> dict[str, str]:
    return {
        str(row.get("claim_name", "")).strip(): str(row.get("current_permission", "")).strip()
        for row in claim_permission_register
        if str(row.get("claim_name", "")).strip()
    }


def build_cross_layer_conflict_register(
    *,
    target_definition: dict[str, Any],
    system_abstraction: dict[str, Any],
    dominant_variable_register: list[dict[str, Any]],
    financial_exposure_register: list[dict[str, Any]],
    claim_permission_register: list[dict[str, Any]],
    decision_front_actions: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    target_type = str(target_definition.get("target_type", "")).strip().lower()
    variables = _var_map(dominant_variable_register)
    decisions = _decision_map(decision_front_actions)
    financial_text = _financial_text(financial_exposure_register)
    claim_permissions = _claim_permissions(claim_permission_register)
    economic_driver_text = str(
        (system_abstraction.get("economic_driver", {}) or {}).get("statement", "")
    ).strip().lower()
    rows: list[dict[str, Any]] = []

    if target_type == "commercial_building":
        owner_control_state = str(variables.get("owner_control_boundary", {}).get("evidence_state", "ARCHETYPAL_PRIOR"))
        tenant_metering_state = str(variables.get("tenant_metering", {}).get("evidence_state", "ARCHETYPAL_PRIOR"))
        ll97_state = str(variables.get("LL97_pathway", {}).get("evidence_state", "ARCHETYPAL_PRIOR"))
        utility_baseline_state = str(variables.get("utility_baseline", {}).get("evidence_state", "ARCHETYPAL_PRIOR"))
        control_boundary_unresolved = owner_control_state != "OBSERVED_FACT" or tenant_metering_state != "OBSERVED_FACT"
        ll97_signal_present = "LL97_pathway" in variables or ll97_state != "NOT_OBSERVED" or "ll97" in economic_driver_text
        central_plant_signal_present = "central_plant" in variables
        owner_capturable_logic_is_structurally_plausible = (
            "owner" in economic_driver_text
            and (
                "controllable" in economic_driver_text
                or "penalty avoidance" in economic_driver_text
                or "economics" in economic_driver_text
            )
        )
        if ll97_signal_present and control_boundary_unresolved:
            rows.append(
                CrossLayerConflictRecord(
                    conflict="Regulation vs control boundary",
                    layers_involved=["regulation", "control", "finance"],
                    evidence_state=StructuralEvidenceState.CONDITIONAL_HYPOTHESIS if owner_control_state != "OBSERVED_FACT" else StructuralEvidenceState.OBSERVED_FACT,
                    why_it_matters="Compliance burden may sit with the owner while dominant loads and economic capture remain partly tenant-driven or contractually unresolved.",
                    what_confirms_it=["tenant metering map", "lease responsibility matrix", "LL97 filing basis"],
                    what_falsifies_it=["observed full owner control over the dominant covered loads"],
                    potential_redesign_direction="Reframe toward lease redesign, submetering, or owner/tenant responsibility architecture before owner-only CAPEX logic.",
                ).to_dict()
            )
        if control_boundary_unresolved and (
            ("owner-controllable energy upside" in financial_text)
            or owner_capturable_logic_is_structurally_plausible
            or central_plant_signal_present
            or "tenant_metering" in variables
        ):
            rows.append(
                CrossLayerConflictRecord(
                    conflict="Finance assumes owner-capturable savings before control is proven",
                    layers_involved=["finance", "operation", "control"],
                    evidence_state=StructuralEvidenceState.CONDITIONAL_HYPOTHESIS,
                    why_it_matters="Retrofit economics can be overstated if owner economics do not track the dominant load.",
                    what_confirms_it=["utility bills", "metering map", "owner control boundary", "tenant schedule"],
                    what_falsifies_it=["fully owner-controlled central plant and covered loads"],
                    potential_redesign_direction="Prioritize metering and control-boundary validation before underwriting owner-side savings.",
                ).to_dict()
            )
        if (
            claim_permissions.get("numeric_eui_claim") in {"allowed", "conditional"}
            or ll97_signal_present
            or utility_baseline_state in {"CONDITIONAL_HYPOTHESIS", "ARCHETYPAL_PRIOR"}
            or "tenant_metering" in variables
        ) and utility_baseline_state != "OBSERVED_FACT":
            rows.append(
                CrossLayerConflictRecord(
                    conflict="Benchmark disclosure vs physical load truth",
                    layers_involved=["energy", "benchmarking", "physics"],
                    evidence_state=StructuralEvidenceState.CONDITIONAL_HYPOTHESIS,
                    why_it_matters="A high public benchmark can support screening, but it does not yet prove owner-correctable waste.",
                    what_confirms_it=["utility bills", "interval data", "central plant topology", "tenant metering"],
                    what_falsifies_it=["full utility baseline showing non-owner-dominant load drivers"],
                    potential_redesign_direction="Treat benchmarking as screening input only; separate compliance logic from savings logic.",
                ).to_dict()
            )

    if target_type == "manufacturing_facility":
        throughput_state = str(variables.get("throughput", {}).get("evidence_state", "ARCHETYPAL_PRIOR"))
        thermal_state = str(variables.get("thermal_duty", {}).get("evidence_state", "ARCHETYPAL_PRIOR"))
        downtime_state = str(variables.get("downtime", {}).get("evidence_state", "ARCHETYPAL_PRIOR"))
        process_capex_front = decisions.get("process efficiency capex") or decisions.get("process efficiency or utility-support capex")
        if throughput_state != "OBSERVED_FACT" or thermal_state != "OBSERVED_FACT":
            rows.append(
                CrossLayerConflictRecord(
                    conflict="Energy-savings framing vs unresolved process load",
                    layers_involved=["physics", "operation", "finance"],
                    evidence_state=StructuralEvidenceState.CONDITIONAL_HYPOTHESIS,
                    why_it_matters="Capital can be justified on energy waste even when the dominant driver is structural throughput, thermal duty, or process chemistry.",
                    what_confirms_it=["throughput by shift", "process map", "utility baseline", "equipment inventory"],
                    what_falsifies_it=["observed support-system waste dominating total load"],
                    potential_redesign_direction="Differentiate process redesign, support-system optimization, and maintenance action before energy CAPEX framing.",
                ).to_dict()
            )
        if downtime_state != "OBSERVED_FACT":
            rows.append(
                CrossLayerConflictRecord(
                    conflict="Maintenance and uptime economics may dominate visible energy symptoms",
                    layers_involved=["maintenance", "operation", "finance"],
                    evidence_state=StructuralEvidenceState.CONDITIONAL_HYPOTHESIS,
                    why_it_matters="The economic bottleneck may sit in downtime, scrap, or reliability rather than direct energy waste.",
                    what_confirms_it=["downtime logs", "failure history", "scrap profile", "spare parts lead time"],
                    what_falsifies_it=["observed stable uptime with low outage cost"],
                    potential_redesign_direction="Reframe toward maintenance discipline, uptime, and scheduling before generic efficiency CAPEX.",
                ).to_dict()
            )
        if process_capex_front and str(process_capex_front.get("current_status", "")).strip().upper() in {"DEFER", "NO-GO"}:
            rows.append(
                CrossLayerConflictRecord(
                    conflict="Action pressure vs process evidence maturity",
                    layers_involved=["decision", "operation", "finance"],
                    evidence_state=StructuralEvidenceState.CONDITIONAL_HYPOTHESIS,
                    why_it_matters="Process CAPEX interest is premature while the system still cannot discriminate structural load from operational waste.",
                    what_confirms_it=["throughput", "equipment inventory", "utility bills", "maintenance records"],
                    what_falsifies_it=["observed dominant waste mechanism with controllable boundary"],
                    potential_redesign_direction="Use evidence collection to decide whether redesign, maintenance, or utility optimization deserves priority.",
                ).to_dict()
            )

    return rows
