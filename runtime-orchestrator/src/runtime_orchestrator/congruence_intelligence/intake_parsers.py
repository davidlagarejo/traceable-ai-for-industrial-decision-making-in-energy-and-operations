from __future__ import annotations

from typing import Any

from .schemas import dedupe, list_text, text


def _route_active(asset_family_research_profile: dict[str, Any]) -> bool:
    return text(asset_family_research_profile.get("route_state")) == "operational_asset_candidate"


def _source_rows(source_register: list[dict[str, Any]], family: str) -> list[dict[str, Any]]:
    return [
        dict(row)
        for row in list(source_register or [])
        if text(row.get("source_family")) == family
    ]


def _extended_sources(enriched_data: dict[str, Any]) -> dict[str, Any]:
    return dict((enriched_data or {}).get("extended_sources", {}) or {})


def _payload_candidates(
    *,
    source_rows: list[dict[str, Any]],
    enriched_data: dict[str, Any],
    key_tokens: list[str],
) -> list[dict[str, Any]]:
    candidates: list[dict[str, Any]] = []
    for row in source_rows:
        payload = row.get("payload")
        if isinstance(payload, dict):
            candidates.append(payload)

    extended = _extended_sources(enriched_data)
    if not extended:
        return candidates
    source_markers = set()
    for row in source_rows:
        source_markers.add(text(row.get("title")).lower())
        source_markers.add(text(row.get("source_id")).split("::")[0].lower())
    for key, payload in extended.items():
        key_l = text(key).lower()
        if any(token in key_l for token in key_tokens) or any(marker and marker in key_l for marker in source_markers):
            if isinstance(payload, dict):
                candidates.append(payload)
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
        if value is None:
            continue
        candidate = text(value)
        if candidate:
            return candidate
    return ""


def build_utility_charge_breakdown_register(
    *,
    asset_family_research_profile: dict[str, Any],
    source_register: list[dict[str, Any]],
    enriched_data: dict[str, Any] | None = None,
) -> list[dict[str, Any]]:
    if not _route_active(asset_family_research_profile):
        return []

    bill_rows = _source_rows(source_register, "utility_bill_record")
    if not bill_rows:
        return []

    payloads = _payload_candidates(
        source_rows=bill_rows,
        enriched_data=dict(enriched_data or {}),
        key_tokens=["bill", "utility", "electric", "gas", "tariff"],
    )
    out: list[dict[str, Any]] = []
    for row in bill_rows:
        out.append(
            {
                "source_id": text(row.get("source_id")),
                "billing_signal": text(row.get("title")) or "utility bill record",
                "charge_basis": "bill_presence_only",
                "billing_period": "",
                "service_type": "",
                "charge_type": "unknown",
                "charge_amount": "",
                "demand_kw": "",
                "pf_or_reactive_signal": "",
                "evidence_state": "OBSERVED_FACT",
                "what_it_supports": ["bounded utility-cost existence", "request charge detail if economically material"],
                "what_it_does_not_support": ["local savings estimate", "root-cause diagnosis from bill presence alone"],
            }
        )
    for payload in payloads:
        for record in _records(payload):
            charge_type = _coalesce(record, "charge_type", "Charge Type", "charge_name", "Charge Name")
            out.append(
                {
                    "source_id": _coalesce(record, "source_id", "bill_source", "utility_source"),
                    "billing_signal": _coalesce(record, "statement_name", "statement_type", "service_name") or "parsed utility billing record",
                    "charge_basis": _coalesce(record, "rate_basis", "rate_class", "tariff_name") or "parsed bill detail",
                    "billing_period": _coalesce(record, "billing_period", "period", "billing_month"),
                    "service_type": _coalesce(record, "service_type", "commodity", "utility_type"),
                    "charge_type": charge_type or "unknown",
                    "charge_amount": _coalesce(record, "charge_amount", "amount", "billed_amount"),
                    "demand_kw": _coalesce(record, "demand_kw", "peak_kw", "billing_demand_kw"),
                    "pf_or_reactive_signal": _coalesce(record, "pf_charge", "reactive_charge", "power_factor"),
                    "evidence_state": "OBSERVED_FACT",
                    "what_it_supports": ["bounded charge-structure interpretation", "tariff-aware measurement prioritization"],
                    "what_it_does_not_support": ["subsystem attribution without metering or process evidence"],
                }
            )
    return out


def build_tariff_exposure_register(
    *,
    asset_family_research_profile: dict[str, Any],
    source_register: list[dict[str, Any]],
    enriched_data: dict[str, Any] | None = None,
) -> list[dict[str, Any]]:
    if not _route_active(asset_family_research_profile):
        return []

    tariff_rows = _source_rows(source_register, "utility_tariff_record")
    if not tariff_rows and not _source_rows(source_register, "utility_bill_record"):
        return []

    payloads = _payload_candidates(
        source_rows=tariff_rows or _source_rows(source_register, "utility_bill_record"),
        enriched_data=dict(enriched_data or {}),
        key_tokens=["tariff", "rate", "bill", "utility"],
    )
    out: list[dict[str, Any]] = []
    for row in tariff_rows:
        out.append(
            {
                "source_id": text(row.get("source_id")),
                "tariff_signal": text(row.get("title")) or "utility tariff record",
                "exposure_type": "tariff_context_present",
                "evidence_state": "OBSERVED_FACT",
                "why_it_matters": "Tariff structure may make demand, PF, reactive or schedule timing more material than aggregate consumption alone.",
                "next_best_binding": ["utility bills", "interval demand profile"],
            }
        )
    for payload in payloads:
        for record in _records(payload):
            exposure_type = "tariff_context_present"
            record_text = " ".join(f"{k}={v}" for k, v in record.items()).lower()
            if any(token in record_text for token in ("pf", "power factor", "reactive")):
                exposure_type = "pf_or_reactive_exposure"
            elif any(token in record_text for token in ("demand", "kw")):
                exposure_type = "demand_charge_exposure"
            elif any(token in record_text for token in ("time of use", "tou", "on-peak", "off-peak")):
                exposure_type = "time_of_use_exposure"
            out.append(
                {
                    "source_id": _coalesce(record, "source_id", "tariff_id", "rate_id"),
                    "tariff_signal": _coalesce(record, "rate_class", "tariff_name", "service_class") or "parsed tariff detail",
                    "exposure_type": exposure_type,
                    "evidence_state": "OBSERVED_FACT",
                    "why_it_matters": "Tariff structure can reprioritize what should be measured or fixed first.",
                    "next_best_binding": dedupe(
                        list_text(
                            [
                                _coalesce(record, "next_best_binding"),
                                "interval demand profile",
                                "utility bills",
                            ]
                        )
                    ),
                }
            )
    return out


def build_permit_to_system_register(
    *,
    asset_family_research_profile: dict[str, Any],
    source_register: list[dict[str, Any]],
    enriched_data: dict[str, Any] | None = None,
) -> list[dict[str, Any]]:
    if not _route_active(asset_family_research_profile):
        return []

    permit_rows = _source_rows(source_register, "permit_record") + _source_rows(source_register, "regulatory_coverage_record")
    if not permit_rows:
        return []

    asset_family = text(asset_family_research_profile.get("asset_family"))
    payloads = _payload_candidates(
        source_rows=permit_rows,
        enriched_data=dict(enriched_data or {}),
        key_tokens=["permit", "ll97", "ll84", "dob", "tceq", "emissions", "wastewater"],
    )
    out: list[dict[str, Any]] = []

    def _domain_from_text(value: str) -> str:
        text_l = value.lower()
        if any(token in text_l for token in ("ll97", "ll84", "benchmark", "dob")):
            return "whole-building energy and covered-load logic"
        if any(token in text_l for token in ("air permit", "emissions", "combust", "boiler", "thermal")):
            return "thermal process / combustion / emissions-relevant systems"
        if any(token in text_l for token in ("wastewater", "water", "wet process")):
            return "water or wet-process systems"
        if any(token in text_l for token in ("refrigerant", "refrigeration", "cold")):
            return "refrigeration and conditioned-storage systems"
        if asset_family == "commercial_building":
            return "whole-building energy and covered-load logic"
        if asset_family in {"industrial_manufacturing", "thermal_process_site", "utility_heavy_site"}:
            return "process or support systems constrained by permit context"
        return "bounded system domain implied by permit context"

    for row in permit_rows:
        basis = " ".join([text(row.get("title")), text(row.get("source_id"))])
        out.append(
            {
                "source_id": text(row.get("source_id")),
                "permit_signal": text(row.get("title")) or "permit or regulatory context",
                "physical_domain": _domain_from_text(basis),
                "evidence_state": "OBSERVED_FACT" if text(row.get("source_family")) == "permit_record" else "CONDITIONAL_HYPOTHESIS",
                "supports": ["bounded permit-to-physics translation", "request for local operating evidence"],
                "does_not_support": ["proof of current operation", "compliance closure"],
            }
        )
    for payload in payloads:
        for record in _records(payload):
            basis = " ".join(f"{k}={v}" for k, v in record.items())
            out.append(
                {
                    "source_id": _coalesce(record, "permit_id", "RN", "source_id"),
                    "permit_signal": _coalesce(record, "permit_type", "permit_name", "rule_signal", "permit_summary") or "parsed permit detail",
                    "physical_domain": _domain_from_text(basis),
                    "evidence_state": "OBSERVED_FACT",
                    "supports": ["bounded permit-to-physics translation", "regulated process framing"],
                    "does_not_support": ["proof of current equipment condition", "proof of local loss mechanism"],
                }
            )
    return out


def build_regulated_process_scope_register(
    *,
    asset_family_research_profile: dict[str, Any],
    permit_to_system_register: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    if not _route_active(asset_family_research_profile):
        return []
    rows: list[dict[str, Any]] = []
    for row in permit_to_system_register:
        rows.append(
            {
                "scope_signal": text(row.get("permit_signal")),
                "process_or_system_scope": text(row.get("physical_domain")),
                "evidence_state": text(row.get("evidence_state")) or "CONDITIONAL_HYPOTHESIS",
                "binding_needed": ["local operating evidence", "equipment or boundary proof"],
            }
        )
    return rows
