from __future__ import annotations

from typing import Any

from .schemas import dedupe, text


def _route_active(asset_family_research_profile: dict[str, Any]) -> bool:
    return text(asset_family_research_profile.get("route_state")) == "operational_asset_candidate"


def _source_rows(source_register: list[dict[str, Any]], families: set[str]) -> list[dict[str, Any]]:
    return [
        dict(row)
        for row in list(source_register or [])
        if text(row.get("source_family")) in families
    ]


def _extended_sources(enriched_data: dict[str, Any]) -> dict[str, Any]:
    return dict((enriched_data or {}).get("extended_sources", {}) or {})


def _payload_candidates(
    *,
    source_rows: list[dict[str, Any]],
    enriched_data: dict[str, Any],
    key_tokens: list[str],
) -> list[tuple[str, dict[str, Any]]]:
    candidates: list[tuple[str, dict[str, Any]]] = []
    for row in source_rows:
        payload = row.get("payload")
        if isinstance(payload, dict):
            candidates.append((text(row.get("source_family")), payload))

    extended = _extended_sources(enriched_data)
    if not extended:
        return candidates
    source_markers = set()
    for row in source_rows:
        source_markers.add(text(row.get("title")).lower())
        source_markers.add(text(row.get("source_id")).split("::")[0].lower())
        source_markers.add(text(row.get("source_family")).lower())
    for key, payload in extended.items():
        key_l = text(key).lower()
        if any(token in key_l for token in key_tokens) or any(marker and marker in key_l for marker in source_markers):
            if isinstance(payload, dict):
                guessed_family = ""
                for row in source_rows:
                    family = text(row.get("source_family"))
                    if family and family.lower() in key_l:
                        guessed_family = family
                        break
                candidates.append((guessed_family, payload))
    return candidates


def _records(payload: dict[str, Any]) -> list[dict[str, Any]]:
    records = payload.get("records")
    if isinstance(records, list):
        return [dict(row) for row in records if isinstance(row, dict)]
    if any(isinstance(value, (str, int, float, bool)) for value in payload.values()):
        return [payload]
    return []


def _coalesce(record: dict[str, Any], *keys: str) -> str:
    for key in keys:
        value = record.get(key)
        candidate = text(value)
        if candidate:
            return candidate
    return ""


def build_control_boundary_evidence_register(
    *,
    asset_family_research_profile: dict[str, Any],
    target_definition: dict[str, Any],
    source_register: list[dict[str, Any]],
    enriched_data: dict[str, Any] | None = None,
) -> list[dict[str, Any]]:
    if not _route_active(asset_family_research_profile):
        return []

    asset_family = text(asset_family_research_profile.get("asset_family"))
    if asset_family not in {"commercial_building", "industrial_manufacturing", "logistics_warehouse", "cold_chain"}:
        return []

    relevant = {"lease_matrix_record", "submetering_record", "meter_interval_record", "operator_input_record", "bms_trend_record"}
    rows = _source_rows(source_register, relevant)
    if not rows:
        return []

    out: list[dict[str, Any]] = []
    owner_entity = text(target_definition.get("owner_entity"))
    operator_entity = text(target_definition.get("operator_entity"))
    for row in rows:
        family = text(row.get("source_family"))
        signal = text(row.get("title")) or family or "local boundary evidence"
        out.append(
            {
                "source_id": text(row.get("source_id")),
                "source_family": family,
                "boundary_signal": signal,
                "boundary_dimension": "control_or_metering_boundary",
                "observed_boundary_fact": "Local evidence exists for how burden or metering is partitioned.",
                "owner_entity": owner_entity,
                "operator_entity": operator_entity,
                "evidence_state": "OBSERVED_FACT",
                "what_it_supports": ["bounded control boundary", "responsibility mapping", "claim-ceiling adjustment"],
                "what_it_does_not_support": ["tenant behavior truth without operational evidence", "ROI closure by itself"],
            }
        )

    payloads = _payload_candidates(
        source_rows=rows,
        enriched_data=dict(enriched_data or {}),
        key_tokens=["lease", "meter", "submeter", "boundary", "tenant", "owner", "operator"],
    )
    for family, payload in payloads:
        for record in _records(payload):
            observed_fact = (
                _coalesce(record, "metering_scope", "shared_loads", "responsibility_split", "control_boundary", "boundary_note")
                or "Parsed boundary evidence exists."
            )
            out.append(
                {
                    "source_id": _coalesce(record, "source_id", "meter_id", "lease_id", "boundary_id"),
                    "source_family": family or _coalesce(record, "source_family"),
                    "boundary_signal": _coalesce(record, "title", "record_name", "metering_scope", "responsibility_split") or "parsed boundary evidence",
                    "boundary_dimension": "control_or_metering_boundary",
                    "observed_boundary_fact": observed_fact,
                    "owner_entity": _coalesce(record, "owner_entity") or owner_entity,
                    "operator_entity": _coalesce(record, "operator_entity") or operator_entity,
                    "evidence_state": "OBSERVED_FACT",
                    "what_it_supports": ["bounded control boundary", "responsibility mapping", "load partition interpretation"],
                    "what_it_does_not_support": ["behavioral causality without operating evidence", "economics closure without bills and duty logic"],
                }
            )
    return out


def build_owner_operator_tenant_responsibility_register(
    *,
    asset_family_research_profile: dict[str, Any],
    target_definition: dict[str, Any],
    control_boundary_evidence_register: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    if not _route_active(asset_family_research_profile):
        return []

    out: list[dict[str, Any]] = []
    owner = text(target_definition.get("owner_entity"))
    operator = text(target_definition.get("operator_entity"))
    if owner:
        out.append(
            {
                "party": owner,
                "role_type": "owner",
                "responsibility_signal": "Declared owner context for the bounded asset.",
                "evidence_state": "OBSERVED_FACT",
            }
        )
    if operator:
        out.append(
            {
                "party": operator,
                "role_type": "operator",
                "responsibility_signal": "Declared operator context for the bounded asset.",
                "evidence_state": "OBSERVED_FACT",
            }
        )
    if control_boundary_evidence_register:
        out.append(
            {
                "party": "tenant_or_load_partition_context",
                "role_type": "tenant_or_shared_boundary",
                "responsibility_signal": "Local boundary evidence indicates shared or partitioned operating burden needs bounded interpretation.",
                "evidence_state": "OBSERVED_FACT",
            }
        )
    return out


def build_maintenance_proof_evidence_register(
    *,
    asset_family_research_profile: dict[str, Any],
    source_register: list[dict[str, Any]],
    enriched_data: dict[str, Any] | None = None,
) -> list[dict[str, Any]]:
    if not _route_active(asset_family_research_profile):
        return []

    relevant = {"maintenance_contract_record", "maintenance_log_record", "cmms_record"}
    rows = _source_rows(source_register, relevant)
    if not rows:
        return []

    out: list[dict[str, Any]] = []
    for row in rows:
        family = text(row.get("source_family"))
        out.append(
            {
                "source_id": text(row.get("source_id")),
                "source_family": family,
                "proof_type": family or "maintenance_evidence",
                "program_signal": text(row.get("title")) or "maintenance evidence present",
                "critical_system": "",
                "program_or_recurrence_signal": "Local maintenance evidence exists.",
                "evidence_state": "OBSERVED_FACT",
                "what_it_supports": ["maintenance maturity bounded above weak-signal level", "downtime and reliability interpretation"],
                "what_it_does_not_support": ["asset condition closure without deeper technical proof"],
            }
        )

    payloads = _payload_candidates(
        source_rows=rows,
        enriched_data=dict(enriched_data or {}),
        key_tokens=["maintenance", "cmms", "workorder", "downtime", "pm", "spares"],
    )
    for family, payload in payloads:
        for record in _records(payload):
            out.append(
                {
                    "source_id": _coalesce(record, "source_id", "workorder_id", "contract_id"),
                    "source_family": family or _coalesce(record, "source_family"),
                    "proof_type": family or "maintenance_evidence",
                    "program_signal": _coalesce(record, "pm_program", "program_signal", "maintenance_program", "contract_scope") or "parsed maintenance evidence",
                    "critical_system": _coalesce(record, "critical_system", "critical_spares", "system_scope"),
                    "program_or_recurrence_signal": _coalesce(record, "recurrence_signal", "charger_ir_scan", "repeat_failure_signal", "notes") or "parsed maintenance support",
                    "evidence_state": "OBSERVED_FACT",
                    "what_it_supports": ["maintenance maturity bounded above weak-signal level", "reliability interpretation", "downtime economics framing"],
                    "what_it_does_not_support": ["performance closure without operating context", "savings claim by itself"],
                }
            )
    return out
