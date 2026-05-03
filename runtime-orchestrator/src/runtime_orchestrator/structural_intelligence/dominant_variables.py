from __future__ import annotations

from typing import Any

from .schemas import DominantVariableHypothesis, StructuralEvidenceState


def _field_values(asset_field_register: list[dict[str, Any]]) -> dict[str, list[str]]:
    values: dict[str, list[str]] = {}
    for row in asset_field_register:
        key = str(row.get("field", "")).strip().lower()
        value = str(row.get("value", "")).strip()
        if key and value:
            values.setdefault(key, []).append(value.lower())
    return values


def _dataset_keys(dataset_coverage_register: list[dict[str, Any]]) -> set[str]:
    keys: set[str] = set()
    for row in dataset_coverage_register:
        key = str(row.get("dataset_key", "")).strip().lower()
        if key:
            keys.add(key)
    return keys


def _promote_variable_state(
    variable: str,
    *,
    target_type: str,
    field_values: dict[str, list[str]],
    dataset_keys: set[str],
) -> StructuralEvidenceState:
    if variable == "utility_baseline":
        if "utility_bills" in field_values:
            return StructuralEvidenceState.OBSERVED_FACT
        if "current_eui" in field_values:
            return StructuralEvidenceState.CONDITIONAL_HYPOTHESIS
    if variable == "LL97_pathway":
        if target_type == "commercial_building" and (
            "nyc_ll97_covered_buildings_list" in dataset_keys
            or "nyc_ll97_public_filing_candidate" in dataset_keys
            or "nyc_ll84_energy_benchmarking" in dataset_keys
        ):
            return StructuralEvidenceState.OBSERVED_FACT
    if variable in {"tenant_metering", "owner_control_boundary"}:
        if variable in field_values or "lease_responsibility" in field_values:
            return StructuralEvidenceState.OBSERVED_FACT
        return StructuralEvidenceState.CONDITIONAL_HYPOTHESIS
    if variable == "central_plant":
        if "hvac_type" in field_values or "central_plant_topology" in field_values:
            return StructuralEvidenceState.OBSERVED_FACT
        return StructuralEvidenceState.CONDITIONAL_HYPOTHESIS
    if variable in {"throughput", "thermal_duty", "downtime"}:
        if variable in field_values:
            return StructuralEvidenceState.OBSERVED_FACT
        if "process_flow" in field_values or "load_driver" in field_values or "operating_schedule" in field_values:
            return StructuralEvidenceState.CONDITIONAL_HYPOTHESIS
    if variable == "compressed_air":
        if "compressed_air" in field_values:
            return StructuralEvidenceState.OBSERVED_FACT
        if target_type == "manufacturing_facility":
            return StructuralEvidenceState.CONDITIONAL_HYPOTHESIS
    if variable == "resin_curing_profile":
        process_text = " ".join(field_values.get("process_flow", []) + field_values.get("load_driver", []))
        if any(token in process_text for token in ("resin", "curing", "laminate", "press")):
            return StructuralEvidenceState.CONDITIONAL_HYPOTHESIS
    return StructuralEvidenceState.ARCHETYPAL_PRIOR


def _dominance_label(evidence_state: StructuralEvidenceState) -> str:
    mapping = {
        StructuralEvidenceState.OBSERVED_FACT: "observed_candidate_dominant",
        StructuralEvidenceState.CONDITIONAL_HYPOTHESIS: "conditional_candidate_dominant",
        StructuralEvidenceState.ARCHETYPAL_PRIOR: "archetypal_candidate",
        StructuralEvidenceState.NOT_OBSERVED: "not_observed",
        StructuralEvidenceState.INADMISSIBLE_CLAIM: "inadmissible",
    }
    return mapping[evidence_state]


def build_dominant_variable_register(
    *,
    target_definition: dict[str, Any],
    system_abstraction: dict[str, Any],
    dominant_variable_hypotheses: list[dict[str, Any]],
    asset_field_register: list[dict[str, Any]],
    dataset_coverage_register: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    target_type = str(target_definition.get("target_type", "")).strip().lower()
    field_values = _field_values(asset_field_register)
    dataset_keys = _dataset_keys(dataset_coverage_register)
    rows: list[dict[str, Any]] = []

    for row in dominant_variable_hypotheses:
        variable = str(row.get("variable", "")).strip()
        if not variable:
            continue
        evidence_state = _promote_variable_state(
            variable,
            target_type=target_type,
            field_values=field_values,
            dataset_keys=dataset_keys,
        )
        hypothesis = DominantVariableHypothesis(
            variable=variable,
            layer=str(row.get("layer", "")).strip(),
            dominance=_dominance_label(evidence_state),
            evidence_state=evidence_state,
            why_it_could_matter=str(row.get("why_it_could_matter", "")).strip(),
            what_confirms_it=list(row.get("what_confirms_it", []) or []),
            what_falsifies_it=list(row.get("what_falsifies_it", []) or []),
            decision_impact=list(row.get("decision_impact", []) or []),
        )
        rows.append(hypothesis.to_dict())

    seen = {row["variable"] for row in rows}
    for variable, layer, why_it_could_matter, confirms, falsifies, impact in [
        (
            "owner_control_boundary",
            "control",
            "Control boundary determines whether economics and compliance can be translated into owner action.",
            ["lease responsibility matrix", "metering topology", "operator responsibility map"],
            ["full third-party or tenant control over dominant loads"],
            ["retrofit admissibility", "compliance strategy", "TAD action priority"],
        ),
    ]:
        if variable in seen:
            continue
        evidence_state = _promote_variable_state(
            variable,
            target_type=target_type,
            field_values=field_values,
            dataset_keys=dataset_keys,
        )
        rows.append(
            DominantVariableHypothesis(
                variable=variable,
                layer=layer,
                dominance=_dominance_label(evidence_state),
                evidence_state=evidence_state,
                why_it_could_matter=why_it_could_matter,
                what_confirms_it=confirms,
                what_falsifies_it=falsifies,
                decision_impact=impact,
            ).to_dict()
        )

    _ = system_abstraction  # explicit placeholder so this lane can later use richer abstraction logic
    return rows

