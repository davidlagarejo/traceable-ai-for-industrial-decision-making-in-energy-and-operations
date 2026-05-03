from __future__ import annotations

from typing import Any

from .schemas import text

_QUESTION_ID_TO_GAP_CLASS = {
    "warehouse_subtype_and_cold_chain_status": "missing_comparability",
    "warehouse_dock_cycles_and_operating_hours": "missing_comparability",
    "warehouse_mhe_charging_profile": "missing_tariff_evidence",
    "warehouse_control_boundary": "missing_control_evidence",
    "warehouse_hvac_mechanical_context": "missing_operational_context",
    "cold_chain_temperature_regime": "missing_comparability",
    "manufacturing_process_and_thermal_lane": "missing_operational_context",
    "manufacturing_compressed_air_use": "missing_operational_context",
    "manufacturing_throughput_and_product_mix": "missing_comparability",
    "manufacturing_maintenance_ownership": "missing_maintenance_proof",
    "utility_bill_history": "missing_tariff_evidence",
    "utility_tariff_or_rate_class": "missing_tariff_evidence",
    "metering_and_boundary_map": "missing_control_evidence",
}


def _claim_impact_map(claim_impact_register: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    return {
        text(row.get("question_id")): row
        for row in list(claim_impact_register or [])
        if text(row.get("question_id"))
    }


def _question_gap_class(question: dict[str, Any]) -> str:
    question_id = text(question.get("question_id"))
    if question_id in _QUESTION_ID_TO_GAP_CLASS:
        return _QUESTION_ID_TO_GAP_CLASS[question_id]

    lower = " ".join(
        [
            question_id.lower(),
            text(question.get("hypothesis_it_discriminates")).lower(),
            text(question.get("claim_impact_if_missing")).lower(),
        ]
    )
    if any(token in lower for token in {"identity", "parcel", "foreign asset"}):
        return "missing_identity_resolution"
    if any(token in lower for token in {"control boundary", "lease", "meter"}):
        return "missing_control_evidence"
    if any(token in lower for token in {"tariff", "rate class", "demand"}):
        return "missing_tariff_evidence"
    if any(token in lower for token in {"maintenance", "downtime", "cmms"}):
        return "missing_maintenance_proof"
    if any(token in lower for token in {"peer", "eui", "comparison", "denominator"}):
        return "missing_comparability"
    if any(token in lower for token in {"schedule", "throughput", "process", "subtype", "operating"}):
        return "missing_operational_context"
    return "missing_data"


def _question_next_action(question: dict[str, Any], gap_class: str) -> str:
    if gap_class == "missing_comparability":
        return "comparison_building"
    if gap_class in {"missing_identity_resolution"} and not list(question.get("public_search_context", []) or []):
        return "search"
    if list(question.get("public_search_context", []) or []):
        return "intake"
    return "search"


def _blocker_gap_class(blocker: dict[str, Any]) -> str:
    blocker_code = text(blocker.get("blocker_code")).lower()
    domain = text(blocker.get("conflict_domain")).lower()
    why = text(blocker.get("why")).lower()
    combined = " ".join([blocker_code, domain, why])
    if "identity" in combined or "foreign_asset" in combined:
        return "missing_identity_resolution"
    if "control" in combined or "boundary" in combined or "lease" in combined:
        return "missing_control_evidence"
    if "tariff" in combined or "demand" in combined:
        return "missing_tariff_evidence"
    if "maintenance" in combined or "downtime" in combined:
        return "missing_maintenance_proof"
    if "comparison" in combined or "peer" in combined:
        return "missing_comparability"
    if "schedule" in combined or "throughput" in combined or "process" in combined:
        return "missing_operational_context"
    return "missing_data"


def build_gap_taxonomy_register(
    *,
    dynamic_intake_question_register: list[dict[str, Any]],
    promotion_blocker_register: list[dict[str, Any]],
    claim_impact_register: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    claim_impact_by_question = _claim_impact_map(claim_impact_register)
    rows: list[dict[str, Any]] = []

    for question in list(dynamic_intake_question_register or []):
        question_id = text(question.get("question_id"))
        if not question_id:
            continue
        gap_class = _question_gap_class(question)
        claim_row = claim_impact_by_question.get(question_id, {})
        rows.append(
            {
                "gap_id": question_id,
                "gap_class": gap_class,
                "source_type": "dynamic_intake_question",
                "source_id": question_id,
                "why_blocked": text(question.get("claim_impact_if_missing")),
                "evidence_needed": list(claim_row.get("evidence_needed", []) or []),
                "next_action_type": _question_next_action(question, gap_class),
                "blocked_claims": list(claim_row.get("blocked_claims", []) or []),
                "linked_need_ids": list(question.get("linked_need_ids", []) or []),
                "linked_pack_names": list(question.get("linked_pack_names", []) or []),
            }
        )

    for blocker in list(promotion_blocker_register or []):
        blocker_code = text(blocker.get("blocker_code"))
        if not blocker_code:
            continue
        rows.append(
            {
                "gap_id": blocker_code,
                "gap_class": _blocker_gap_class(blocker),
                "source_type": "promotion_blocker",
                "source_id": blocker_code,
                "why_blocked": text(blocker.get("why")),
                "evidence_needed": [],
                "next_action_type": "claim_prohibition",
                "blocked_claims": [blocker_code],
                "linked_need_ids": [],
                "linked_pack_names": [],
            }
        )

    return rows


def extend_gap_taxonomy_with_comparison_risks(
    *,
    gap_taxonomy_register: list[dict[str, Any]],
    invalid_comparison_risk_register: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    rows = list(gap_taxonomy_register or [])
    for risk in list(invalid_comparison_risk_register or []):
        risk_name = text(risk.get("risk_name"))
        if not risk_name:
            continue
        rows.append(
            {
                "gap_id": risk_name,
                "gap_class": "missing_comparability",
                "source_type": "invalid_comparison_risk",
                "source_id": risk_name,
                "why_blocked": text(risk.get("trigger")),
                "evidence_needed": list(risk.get("required_normalization", []) or []),
                "next_action_type": "comparison_building",
                "blocked_claims": list(risk.get("blocked_claims", []) or []),
                "linked_need_ids": [],
                "linked_pack_names": [],
            }
        )
    return rows


def build_evidence_need_class_register(
    *,
    gap_taxonomy_register: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    return [
        {
            "gap_id": text(row.get("gap_id")),
            "evidence_need_class": text(row.get("gap_class")),
            "next_action_type": text(row.get("next_action_type")),
            "blocked_claims": list(row.get("blocked_claims", []) or []),
            "evidence_needed": list(row.get("evidence_needed", []) or []),
        }
        for row in list(gap_taxonomy_register or [])
        if text(row.get("gap_id"))
    ]
