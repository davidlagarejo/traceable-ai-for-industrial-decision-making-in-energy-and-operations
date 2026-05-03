from __future__ import annotations

from typing import Any

from .schemas import EvidenceStateByLayerRecord, StructuralEvidenceState

CANONICAL_EVIDENCE_LAYERS: list[str] = [
    "physics",
    "operation",
    "energy",
    "finance",
    "regulation",
    "maintenance",
    "logistics",
    "procurement",
    "commercial",
    "culture",
    "control/responsibility",
    "market/competitiveness",
]

_STATE_RANK = {
    StructuralEvidenceState.NOT_OBSERVED.value: 0,
    StructuralEvidenceState.ARCHETYPAL_PRIOR.value: 1,
    StructuralEvidenceState.CONDITIONAL_HYPOTHESIS.value: 2,
    StructuralEvidenceState.OBSERVED_FACT.value: 3,
    StructuralEvidenceState.INADMISSIBLE_CLAIM.value: 0,
}

_LAYER_ALIASES = {
    "physical": "physics",
    "physics": "physics",
    "operation": "operation",
    "operations": "operation",
    "energy": "energy",
    "finance": "finance",
    "financial": "finance",
    "regulation": "regulation",
    "regulatory": "regulation",
    "maintenance": "maintenance",
    "logistics": "logistics",
    "procurement": "procurement",
    "purchasing": "procurement",
    "commercial": "commercial",
    "sales": "commercial",
    "culture": "culture",
    "control": "control/responsibility",
    "responsibility": "control/responsibility",
    "control/responsibility": "control/responsibility",
    "benchmarking": "market/competitiveness",
    "market": "market/competitiveness",
    "competitiveness": "market/competitiveness",
    "market/competitiveness": "market/competitiveness",
    "support_system": "energy",
}

_GENERIC_OPEN_QUESTIONS = {
    "physics": "What physical driver actually dominates system behavior?",
    "operation": "Which operating pattern materially changes interpretation of the case?",
    "energy": "Is energy behavior structural load, controllable waste, or a mixed signal?",
    "finance": "Which financial assumption becomes false first if the structural reading is wrong?",
    "regulation": "Which regulatory pathway actually constrains the case today?",
    "maintenance": "Does reliability or maintenance discipline dominate value before energy does?",
    "logistics": "Do flow, access, scheduling, or movement constraints shape the system materially?",
    "procurement": "Do tariffs, fuel contracts, materials, or vendor constraints change the solution path?",
    "commercial": "Does the business model or customer/tenant allocation change what the asset should optimize?",
    "culture": "Is execution discipline or organizational behavior hiding the real bottleneck?",
    "control/responsibility": "Who actually controls the variables that matter economically and operationally?",
    "market/competitiveness": "What peer context is strong enough to change strategic interpretation?",
}

_GENERIC_RISKS = {
    "physics": "The system can be redesigned around a false physical bottleneck.",
    "operation": "The system can be optimized against the wrong operating pattern.",
    "energy": "Energy conclusions can confuse structural load with correctable waste.",
    "finance": "Capital logic can be built on a false structural assumption.",
    "regulation": "The wrong compliance pathway can drive the wrong action.",
    "maintenance": "Reliability and downtime can stay hidden behind visible utility symptoms.",
    "logistics": "Movement, access, or schedule constraints can invalidate an otherwise plausible redesign path.",
    "procurement": "Commercial terms or supply-side constraints can block the intended intervention.",
    "commercial": "The asset can optimize technically while missing the real value mechanism.",
    "culture": "The organization may fail to capture value even if the technical diagnosis is right.",
    "control/responsibility": "The party paying may not control the driver that matters.",
    "market/competitiveness": "Generic peer claims can be mistaken for local strategic truth.",
}


def _normalize_layer(layer: str) -> str:
    return _LAYER_ALIASES.get(str(layer or "").strip().lower(), "")


def _as_state(value: str) -> str:
    candidate = str(value or "").strip()
    if candidate in StructuralEvidenceState._value2member_map_:
        return candidate
    return StructuralEvidenceState.NOT_OBSERVED.value


def _listify(value: Any) -> list[str]:
    if isinstance(value, list):
        return [str(item).strip() for item in value if str(item).strip()]
    text = str(value or "").strip()
    return [text] if text else []


def _append_unique(target: list[str], values: list[str]) -> None:
    for value in values:
        item = str(value).strip()
        if item and item not in target:
            target.append(item)


def _promote_state(current: str, candidate: str) -> str:
    current_state = _as_state(current)
    candidate_state = _as_state(candidate)
    if _STATE_RANK[candidate_state] > _STATE_RANK[current_state]:
        return candidate_state
    return current_state


def _base_rows() -> dict[str, dict[str, Any]]:
    rows: dict[str, dict[str, Any]] = {}
    for layer in CANONICAL_EVIDENCE_LAYERS:
        rows[layer] = EvidenceStateByLayerRecord(
            layer=layer,
            evidence_state=StructuralEvidenceState.NOT_OBSERVED,
            dominant_open_questions=[_GENERIC_OPEN_QUESTIONS[layer]],
            observed_support=[],
            structural_risk_if_wrong=_GENERIC_RISKS[layer],
            linked_conflicts=[],
            linked_problem_frames=[],
        ).to_dict()
    return rows


def _merge_system_abstraction(rows: dict[str, dict[str, Any]], system_abstraction: dict[str, Any]) -> None:
    for field_name, layer in (
        ("dominant_process_type", "physics"),
        ("dominant_physical_drivers", "physics"),
        ("dominant_operational_drivers", "operation"),
        ("control_structure", "control/responsibility"),
        ("constraint_structure", "logistics"),
        ("economic_driver", "finance"),
        ("regulatory_exposure", "regulation"),
        ("business_function", "commercial"),
        ("value_creation_mechanism", "market/competitiveness"),
    ):
        field = dict(system_abstraction.get(field_name, {}) or {})
        if not field:
            continue
        row = rows[layer]
        row["evidence_state"] = _promote_state(row.get("evidence_state", ""), str(field.get("evidence_state", "")))
        if str(field.get("evidence_state", "")).strip() == StructuralEvidenceState.OBSERVED_FACT.value:
            _append_unique(row["observed_support"], [str(field.get("statement", "")).strip()])
        _append_unique(row["dominant_open_questions"], _listify(field.get("minimum_evidence_required", [])))
        if str(field.get("falsification_condition", "")).strip():
            row["structural_risk_if_wrong"] = str(field.get("falsification_condition", "")).strip()


def _merge_dominant_variables(rows: dict[str, dict[str, Any]], dominant_variable_register: list[dict[str, Any]]) -> None:
    for variable_row in dominant_variable_register:
        layer = _normalize_layer(variable_row.get("layer", ""))
        if not layer:
            continue
        row = rows[layer]
        evidence_state = str(variable_row.get("evidence_state", "")).strip()
        row["evidence_state"] = _promote_state(row.get("evidence_state", ""), evidence_state)
        summary = (
            f"{str(variable_row.get('variable', '')).strip()}: "
            f"{str(variable_row.get('why_it_could_matter', '')).strip()}"
        ).strip(": ")
        if evidence_state == StructuralEvidenceState.OBSERVED_FACT.value:
            _append_unique(row["observed_support"], [summary])
        _append_unique(row["dominant_open_questions"], _listify(variable_row.get("what_confirms_it", [])))
        risk_fragments = _listify(variable_row.get("decision_impact", []))
        if risk_fragments:
            row["structural_risk_if_wrong"] = "; ".join(risk_fragments[:3])


def _merge_conflicts(rows: dict[str, dict[str, Any]], cross_layer_conflict_register: list[dict[str, Any]]) -> None:
    for conflict_row in cross_layer_conflict_register:
        conflict_name = str(conflict_row.get("conflict", "")).strip()
        evidence_state = str(conflict_row.get("evidence_state", "")).strip()
        for raw_layer in list(conflict_row.get("layers_involved", []) or []):
            layer = _normalize_layer(raw_layer)
            if not layer:
                continue
            row = rows[layer]
            row["evidence_state"] = _promote_state(row.get("evidence_state", ""), evidence_state)
            _append_unique(row["linked_conflicts"], [conflict_name])
            _append_unique(row["dominant_open_questions"], _listify(conflict_row.get("what_confirms_it", [])))
            if str(conflict_row.get("why_it_matters", "")).strip():
                row["structural_risk_if_wrong"] = str(conflict_row.get("why_it_matters", "")).strip()


def _merge_problem_framing(rows: dict[str, dict[str, Any]], problem_framing_register: list[dict[str, Any]]) -> None:
    for framing_row in problem_framing_register:
        linked_layers = list(framing_row.get("linked_layers", []) or [])
        for raw_layer in linked_layers:
            layer = _normalize_layer(raw_layer)
            if not layer:
                continue
            row = rows[layer]
            row["evidence_state"] = _promote_state(row.get("evidence_state", ""), str(framing_row.get("evidence_state", "")))
            _append_unique(row["linked_problem_frames"], [str(framing_row.get("reframed_problem", "")).strip()])
            _append_unique(row["dominant_open_questions"], _listify(framing_row.get("evidence_needed", [])))
            if str(framing_row.get("strategic_risk", "")).strip():
                row["structural_risk_if_wrong"] = str(framing_row.get("strategic_risk", "")).strip()


def _merge_competitive_comparison(rows: dict[str, dict[str, Any]], competitive_comparison_register: list[dict[str, Any]]) -> None:
    row = rows["market/competitiveness"]
    for comparison_row in competitive_comparison_register:
        evidence_state = str(comparison_row.get("evidence_state", "")).strip()
        row["evidence_state"] = _promote_state(row.get("evidence_state", ""), evidence_state)
        if evidence_state == StructuralEvidenceState.OBSERVED_FACT.value:
            _append_unique(
                row["observed_support"],
                [
                    str(comparison_row.get("what_they_do_better", "")).strip(),
                    str(comparison_row.get("structural_advantage", "")).strip(),
                ],
            )
        _append_unique(row["dominant_open_questions"], _listify(comparison_row.get("evidence_needed", [])))
        if str(comparison_row.get("why_it_matters", "")).strip():
            row["structural_risk_if_wrong"] = str(comparison_row.get("why_it_matters", "")).strip()


def _merge_financial_exposure(rows: dict[str, dict[str, Any]], structural_financial_exposure_register: list[dict[str, Any]]) -> None:
    row = rows["finance"]
    for financial_row in structural_financial_exposure_register:
        row["evidence_state"] = _promote_state(row.get("evidence_state", ""), str(financial_row.get("evidence_state", "")))
        _append_unique(row["dominant_open_questions"], _listify(financial_row.get("evidence_needed", [])))
        if str(financial_row.get("financial_exposure_if_wrong", "")).strip():
            row["structural_risk_if_wrong"] = str(financial_row.get("financial_exposure_if_wrong", "")).strip()


def _apply_target_specific_defaults(rows: dict[str, dict[str, Any]], target_type: str) -> None:
    if target_type == "commercial_building":
        _append_unique(
            rows["control/responsibility"]["dominant_open_questions"],
            ["tenant metering map", "lease responsibility matrix", "central plant / BMS topology"],
        )
        _append_unique(
            rows["commercial"]["dominant_open_questions"],
            ["tenant profile", "after-hours occupancy", "green-lease exposure"],
        )
        _append_unique(
            rows["procurement"]["dominant_open_questions"],
            ["fuel / utility procurement basis", "electrification procurement strategy"],
        )
        _append_unique(
            rows["culture"]["dominant_open_questions"],
            ["continuous commissioning discipline", "tenant engagement discipline"],
        )
    elif target_type == "manufacturing_facility":
        _append_unique(
            rows["logistics"]["dominant_open_questions"],
            ["material-handling map", "production scheduling constraint", "shipping / storage bottlenecks"],
        )
        _append_unique(
            rows["procurement"]["dominant_open_questions"],
            ["fuel supply basis", "resin / materials procurement exposure", "spare-parts lead-time profile"],
        )
        _append_unique(
            rows["commercial"]["dominant_open_questions"],
            ["product-mix economics", "customer service-level constraints", "quality / scrap cost linkage"],
        )
        _append_unique(
            rows["culture"]["dominant_open_questions"],
            ["maintenance discipline", "operator scheduling discipline", "process-control discipline"],
        )


def build_evidence_state_by_layer_register(
    *,
    target_definition: dict[str, Any],
    system_abstraction: dict[str, Any],
    dominant_variable_register: list[dict[str, Any]],
    cross_layer_conflict_register: list[dict[str, Any]],
    problem_framing_register: list[dict[str, Any]],
    competitive_comparison_register: list[dict[str, Any]],
    structural_financial_exposure_register: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    target_type = str(target_definition.get("target_type", "")).strip().lower()
    rows = _base_rows()
    _merge_system_abstraction(rows, system_abstraction)
    _merge_dominant_variables(rows, dominant_variable_register)
    _merge_conflicts(rows, cross_layer_conflict_register)
    _merge_problem_framing(rows, problem_framing_register)
    _merge_competitive_comparison(rows, competitive_comparison_register)
    _merge_financial_exposure(rows, structural_financial_exposure_register)
    _apply_target_specific_defaults(rows, target_type)
    return [rows[layer] for layer in CANONICAL_EVIDENCE_LAYERS]
