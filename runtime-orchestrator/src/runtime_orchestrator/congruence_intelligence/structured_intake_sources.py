from __future__ import annotations

from typing import Any

from .schemas import dedupe, list_text, text

_PACK_DEFAULT_SOURCE_FAMILIES = {
    "utility_bill_pack": ["utility_bill_record"],
    "utility_tariff_pack": ["utility_tariff_record"],
    "throughput_schedule_pack": ["schedule_record", "operator_input_record"],
    "equipment_inventory_pack": ["equipment_inventory_record"],
    "metering_boundary_pack": ["submetering_record", "operator_input_record"],
    "lease_responsibility_pack": ["lease_matrix_record", "operator_input_record"],
    "maintenance_proof_pack": ["maintenance_log_record", "maintenance_contract_record"],
    "bms_or_controls_pack": ["bms_trend_record", "operator_input_record"],
    "cmms_or_workorder_pack": ["cmms_record", "operator_input_record"],
    "permit_detail_pack": ["permit_record"],
}

_PACK_DEFAULT_TITLES = {
    "utility_bill_pack": "Structured utility bill intake",
    "utility_tariff_pack": "Structured utility tariff intake",
    "throughput_schedule_pack": "Structured throughput and schedule intake",
    "equipment_inventory_pack": "Structured equipment inventory intake",
    "metering_boundary_pack": "Structured metering boundary intake",
    "lease_responsibility_pack": "Structured lease responsibility intake",
    "maintenance_proof_pack": "Structured maintenance proof intake",
    "bms_or_controls_pack": "Structured controls / BMS intake",
    "cmms_or_workorder_pack": "Structured CMMS / workorder intake",
    "permit_detail_pack": "Structured permit detail intake",
}


def _pack_container(pipeline: dict[str, Any]) -> dict[str, Any]:
    facility_inputs = dict((pipeline or {}).get("facility_inputs", {}) or {})
    raw = (
        facility_inputs.get("input_11_congruence_diligence")
        or facility_inputs.get("input_11_operator_diligence")
        or (pipeline or {}).get("congruence_diligence")
        or {}
    )
    if not isinstance(raw, dict):
        return {}
    packs = raw.get("packs")
    if isinstance(packs, dict):
        return dict(packs)
    return dict(raw)


def _meaningful_pack_payload(payload: Any) -> bool:
    if isinstance(payload, list):
        return len(payload) > 0
    if not isinstance(payload, dict):
        return bool(text(payload))
    state = text(payload.get("current_state") or payload.get("state")).lower()
    if state in {"requested_but_absent", "not_primary", "not_yet_evidenced", "not_yet_locally_bounded"}:
        return False
    for key, value in payload.items():
        if key in {"current_state", "state", "notes"}:
            continue
        if isinstance(value, list) and value:
            return True
        if isinstance(value, dict) and value:
            return True
        if text(value):
            return True
    return False


def _source_rows_for_pack(
    *,
    pack_name: str,
    payload: dict[str, Any],
    target_definition: dict[str, Any],
) -> list[dict[str, Any]]:
    source_families = dedupe(
        list_text(payload.get("source_families"))
        or list(_PACK_DEFAULT_SOURCE_FAMILIES.get(pack_name, []) or [])
    )
    if not source_families:
        return []

    title = text(payload.get("title")) or _PACK_DEFAULT_TITLES.get(pack_name, pack_name.replace("_", " "))
    target_label = (
        text(target_definition.get("target_identifier"))
        or text(target_definition.get("target_name"))
        or text(target_definition.get("address_raw"))
        or "local-asset"
    )
    rows: list[dict[str, Any]] = []
    for source_family in source_families:
        rows.append(
            {
                "source_id": f"structured_intake::{target_label}::{pack_name}::{source_family}",
                "url": "",
                "title": title,
                "authority_score": "medium",
                "scope": "ASSET_LEVEL",
                "scope_raw": "asset_level",
                "round_id": "structured_intake",
                "recency": "current",
                "accepted": True,
                "rejection_reason": "",
                "source_family": source_family,
                "payload": dict(payload),
                "used_for": [pack_name, "structured_local_diligence"],
            }
        )
    return rows


def merge_source_registers(*registers: list[dict[str, Any]]) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    seen: set[tuple[str, str]] = set()
    for register in registers:
        for row in list(register or []):
            source_id = text(row.get("source_id"))
            source_family = text(row.get("source_family"))
            key = (source_id, source_family)
            if not source_id or not source_family or key in seen:
                continue
            seen.add(key)
            out.append(dict(row))
    return out


def build_structured_local_source_register(
    *,
    pipeline: dict[str, Any],
    target_definition: dict[str, Any],
) -> list[dict[str, Any]]:
    packs = _pack_container(pipeline)
    rows: list[dict[str, Any]] = []
    for pack_name, raw_payload in packs.items():
        payload = dict(raw_payload) if isinstance(raw_payload, dict) else {"value": raw_payload}
        if not _meaningful_pack_payload(payload):
            continue
        rows.extend(
            _source_rows_for_pack(
                pack_name=text(pack_name),
                payload=payload,
                target_definition=target_definition,
            )
        )
    return merge_source_registers(rows)
