from __future__ import annotations

from typing import Any

from .schemas import text

_PACK_ESCALATION_OWNER = {
    "utility_bill_pack": "owner / accounting / operator",
    "utility_tariff_pack": "owner / accounting / operator",
    "throughput_schedule_pack": "operator / facility manager",
    "equipment_inventory_pack": "maintenance / facility engineer",
    "metering_boundary_pack": "owner / operator / energy manager",
    "lease_responsibility_pack": "owner / asset manager / operator",
    "maintenance_proof_pack": "maintenance manager",
    "bms_or_controls_pack": "controls / facility manager",
    "cmms_or_workorder_pack": "maintenance manager",
    "permit_detail_pack": "owner / operator / EHS lead",
}


def _budget_state(search_budget_register: list[dict[str, Any]]) -> str:
    for row in list(search_budget_register or []):
        if text(row.get("budget_scope")) == "total_public_discovery":
            return text(row.get("budget_state")) or "bounded"
    return "bounded"


def _next_search_by_need(next_best_search_register: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    return {
        text(row.get("need_id")): row
        for row in list(next_best_search_register or [])
        if text(row.get("need_id"))
    }


def _build_search_stop_rows(
    *,
    discovery_need_register: list[dict[str, Any]],
    next_best_search_register: list[dict[str, Any]],
    search_budget_register: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    budget_state = _budget_state(search_budget_register)
    next_by_need = _next_search_by_need(next_best_search_register)
    rows: list[dict[str, Any]] = []

    for need in list(discovery_need_register or []):
        need_id = text(need.get("need_id"))
        next_row = next_by_need.get(need_id, {})
        continuation_allowed = budget_state != "exhausted"
        rows.append(
            {
                "path_type": "public_search",
                "path_id": need_id,
                "purpose": text(need.get("discovery_need")),
                "minimum_sufficient_evidence": text(need.get("minimum_sufficient_evidence")),
                "stop_condition": text(need.get("stop_condition")),
                "downgrade_condition": text(need.get("downgrade_condition")),
                "escalation_condition": text(need.get("escalation_condition")),
                "current_state": (
                    "stop_and_escalate"
                    if not continuation_allowed
                    else "continue_public_search"
                ),
                "continuation_allowed": continuation_allowed,
                "next_search_family": text(next_row.get("search_family")),
                "expected_evidence": text(next_row.get("expected_evidence")),
                "matched_gap_types": list(need.get("matched_gap_types", []) or []),
            }
        )
    return rows


def _pack_minimum_sufficient_evidence(pack: dict[str, Any]) -> str:
    present = [text(item) for item in list(pack.get("present_source_families", []) or []) if text(item)]
    expected = [text(item) for item in list(pack.get("expected_local_sources", []) or []) if text(item)]
    binding = [text(item) for item in list(pack.get("binding_needed", []) or []) if text(item)]
    if expected:
        return ", ".join(expected[:3])
    if present:
        return ", ".join(present[:3])
    if binding:
        return ", ".join(binding[:3])
    return "operator-confirmed local evidence for this diligence pack"


def _build_intake_stop_rows(
    *,
    operational_intake_pack: dict[str, Any] | None,
) -> list[dict[str, Any]]:
    operational_intake_pack = operational_intake_pack or {}
    rows: list[dict[str, Any]] = []
    for pack in list(operational_intake_pack.get("diligence_pack_register", []) or []):
        pack_name = text(pack.get("pack_name"))
        if not pack_name:
            continue
        current_state = text(pack.get("current_state"))
        if current_state == "not_primary":
            continue
        required_from = _PACK_ESCALATION_OWNER.get(pack_name, "operator / owner")
        minimum_sufficient_evidence = _pack_minimum_sufficient_evidence(pack)
        continuation_allowed = current_state not in {"evidenced", "not_primary"}
        if current_state == "evidenced":
            state = "stop_intake_satisfied"
        elif current_state in {"requested_but_absent", "public_context_only"}:
            state = "escalate_to_operator"
        else:
            state = "continue_local_binding"
        rows.append(
            {
                "path_type": "intake_escalation",
                "path_id": pack_name,
                "purpose": text(pack.get("decision_relevance")) or pack_name.replace("_", " "),
                "minimum_sufficient_evidence": minimum_sufficient_evidence,
                "stop_condition": f"{pack_name} reaches evidenced state with usable local binding.",
                "downgrade_condition": (
                    f"{pack_name} remains {current_state or 'unbounded'} and related claims stay screening-only."
                ),
                "escalation_condition": (
                    f"Ask {required_from} for {minimum_sufficient_evidence}."
                ),
                "current_state": state,
                "continuation_allowed": continuation_allowed,
                "binding_needed": list(pack.get("binding_needed", []) or []),
                "required_from": required_from,
            }
        )
    return rows


def build_stop_condition_register(
    *,
    discovery_need_register: list[dict[str, Any]],
    next_best_search_register: list[dict[str, Any]],
    search_budget_register: list[dict[str, Any]],
    operational_intake_pack: dict[str, Any] | None = None,
) -> list[dict[str, Any]]:
    return _build_search_stop_rows(
        discovery_need_register=discovery_need_register,
        next_best_search_register=next_best_search_register,
        search_budget_register=search_budget_register,
    ) + _build_intake_stop_rows(
        operational_intake_pack=operational_intake_pack,
    )


def build_downgrade_condition_register(
    *,
    stop_condition_register: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    return [
        {
            "path_type": text(row.get("path_type")),
            "path_id": text(row.get("path_id")),
            "downgrade_condition": text(row.get("downgrade_condition")),
            "current_state": text(row.get("current_state")),
        }
        for row in list(stop_condition_register or [])
    ]


def build_escalation_condition_register(
    *,
    stop_condition_register: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    return [
        {
            "path_type": text(row.get("path_type")),
            "path_id": text(row.get("path_id")),
            "escalation_condition": text(row.get("escalation_condition")),
            "current_state": text(row.get("current_state")),
        }
        for row in list(stop_condition_register or [])
    ]


def build_minimum_sufficient_evidence_register(
    *,
    stop_condition_register: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    return [
        {
            "path_type": text(row.get("path_type")),
            "path_id": text(row.get("path_id")),
            "purpose": text(row.get("purpose")),
            "minimum_sufficient_evidence": text(row.get("minimum_sufficient_evidence")),
            "stop_condition": text(row.get("stop_condition")),
        }
        for row in list(stop_condition_register or [])
    ]
