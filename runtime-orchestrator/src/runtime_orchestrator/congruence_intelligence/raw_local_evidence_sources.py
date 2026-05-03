from __future__ import annotations

import re
from typing import Any

from .schemas import dedupe, list_text, text

_EXPLICIT_SOURCE_FAMILY_ALIASES = {
    "bill": "utility_bill_record",
    "bms": "bms_trend_record",
    "bms_trend": "bms_trend_record",
    "cmms": "cmms_record",
    "equipment_inventory": "equipment_inventory_record",
    "interval_meter": "meter_interval_record",
    "lease": "lease_matrix_record",
    "maintenance_contract": "maintenance_contract_record",
    "maintenance_log": "maintenance_log_record",
    "meter_interval": "meter_interval_record",
    "operator_input": "operator_input_record",
    "permit": "permit_record",
    "schedule": "schedule_record",
    "submetering": "submetering_record",
    "tariff": "utility_tariff_record",
    "utility_bill": "utility_bill_record",
    "utility_tariff": "utility_tariff_record",
    "workorder": "cmms_record",
}

_INFERRED_SOURCE_FAMILY_PATTERNS = [
    ("utility_bill_record", ("utility bill", "electric bill", "gas bill", "invoice", "statement", "billing demand")),
    ("utility_tariff_record", ("tariff", "rate rider", "rate class", "service class", "svc cls", "svc class", "rate sch", "billing determinant", "time of use", "tou", "power factor charge")),
    ("lease_matrix_record", ("lease matrix", "lease responsibility", "tenant responsibility", "owner responsibility", "responsibility matrix", "landlord responsibility", "lessor responsibility", "lessee responsibility", "cam charges")),
    ("submetering_record", ("submeter", "metering boundary", "meter map", "single-line metering", "metering scope")),
    ("meter_interval_record", ("interval data", "15-minute", "15 minute", "demand profile", "ami export", "interval profile")),
    ("equipment_inventory_record", ("equipment inventory", "asset inventory", "nameplate", "major equipment", "equipment list")),
    ("maintenance_contract_record", ("maintenance contract", "service agreement", "preventive maintenance contract")),
    ("maintenance_log_record", ("maintenance log", "service log", "inspection log", "maintenance report", "pm log", "recurring fault", "nuisance trip", "downtime log")),
    ("cmms_record", ("cmms", "work order", "workorder", "maintenance backlog", "wo open", "wo aging", "backlog summary")),
    ("permit_record", ("permit", "filing", "regulatory packet", "permit summary", "license record")),
    ("schedule_record", ("schedule", "shift", "throughput", "dock turns", "traffic profile", "operating pattern")),
    ("bms_trend_record", ("bms", "bas trend", "controls trend", "trend log", "defrost schedule")),
    ("operator_input_record", ("operator note", "site note", "operator interview", "operations note")),
]

_MONTH_TO_NUM = {
    "jan": "01",
    "january": "01",
    "feb": "02",
    "february": "02",
    "mar": "03",
    "march": "03",
    "apr": "04",
    "april": "04",
    "may": "05",
    "jun": "06",
    "june": "06",
    "jul": "07",
    "july": "07",
    "aug": "08",
    "august": "08",
    "sep": "09",
    "sept": "09",
    "september": "09",
    "oct": "10",
    "october": "10",
    "nov": "11",
    "november": "11",
    "dec": "12",
    "december": "12",
}


def _raw_text(document: dict[str, Any]) -> str:
    parts: list[str] = [
        text(document.get("document_type")),
        text(document.get("source_family")),
        text(document.get("title")),
        text(document.get("scope")),
        text(document.get("summary")),
        text(document.get("text_excerpt")),
    ]
    extracted_fields = document.get("extracted_fields")
    if isinstance(extracted_fields, dict):
        parts.extend(f"{key}={value}" for key, value in extracted_fields.items())
    extracted_records = document.get("extracted_records") or document.get("records")
    if isinstance(extracted_records, list):
        for record in extracted_records:
            if isinstance(record, dict):
                parts.extend(f"{key}={value}" for key, value in record.items())
    return " ".join(part for part in parts if part)


def _document_container(pipeline: dict[str, Any]) -> list[dict[str, Any]]:
    facility_inputs = dict((pipeline or {}).get("facility_inputs", {}) or {})
    raw = (
        facility_inputs.get("input_12_raw_local_evidence")
        or facility_inputs.get("input_12_local_evidence")
        or (pipeline or {}).get("raw_local_evidence")
        or (pipeline or {}).get("local_evidence")
        or {}
    )
    if isinstance(raw, list):
        return [dict(doc) for doc in raw if isinstance(doc, dict)]
    if isinstance(raw, dict):
        documents = raw.get("documents") or raw.get("items") or raw.get("records")
        if isinstance(documents, list):
            return [dict(doc) for doc in documents if isinstance(doc, dict)]
    fallback = (pipeline or {}).get("raw_local_evidence_documents")
    if isinstance(fallback, list):
        return [dict(doc) for doc in fallback if isinstance(doc, dict)]
    return []


def _slug(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", text(value).lower()).strip("-") or "document"


def _canonical_source_family(value: str) -> str:
    normalized = _slug(value).replace("-", "_")
    if not normalized:
        return ""
    if normalized in _EXPLICIT_SOURCE_FAMILY_ALIASES:
        return _EXPLICIT_SOURCE_FAMILY_ALIASES[normalized]
    if normalized.endswith("_record"):
        return normalized
    return ""


def _raw_text_for_inference(document: dict[str, Any]) -> str:
    return _raw_text(document).lower()


def _infer_source_families(document: dict[str, Any]) -> list[str]:
    explicit = dedupe(
        [
            _canonical_source_family(value)
            for value in (
                list_text(document.get("source_families"))
                + list_text(document.get("source_family"))
                + list_text(document.get("document_type"))
            )
        ]
    )
    explicit = [value for value in explicit if value]
    if explicit:
        return explicit

    raw_text = _raw_text_for_inference(document)
    inferred: list[str] = []
    for source_family, tokens in _INFERRED_SOURCE_FAMILY_PATTERNS:
        if any(token in raw_text for token in tokens):
            inferred.append(source_family)
    return dedupe(inferred)


def _search(pattern: str, text_blob: str) -> str:
    match = re.search(pattern, text_blob, flags=re.IGNORECASE)
    if not match:
        return ""
    for group in match.groups():
        if text(group):
            return text(group)
    return text(match.group(0))


def _contains_any(text_blob: str, tokens: tuple[str, ...] | list[str]) -> bool:
    lowered = text_blob.lower()
    return any(token in lowered for token in tokens)


def _extract_party_scope(text_blob: str, party: str) -> str:
    aliases = {
        "owner": ("owner", "landlord", "lessor", "ll"),
        "tenant": ("tenant", "lessee", "occupant", "tnt"),
        "operator": ("operator", "operations", "3pl", "service operator"),
    }.get(party, (party,))
    alias_pattern = r"\b(?:" + "|".join(re.escape(alias) for alias in aliases) + r")\b"
    patterns = [
        rf"{alias_pattern}\s*(?:resp\.?|responsibility)\s*[:\-]\s*([^.;\n]+)",
        rf"{alias_pattern}\s*(?:shall be\s*)?(?:is\s*)?(?:responsible for|retains?|maintains?|controls?|covers?|pays for|bears?|handles?)\s*([^.;\n]+)",
        rf"{alias_pattern}\s*[:\-]\s*([^.;\n]+)",
    ]
    for pattern in patterns:
        match = _search(pattern, text_blob)
        if match:
            return match
    return ""


def _extract_billing_period(text_blob: str) -> str:
    direct = _search(r"(20\d{2}[-/](?:0[1-9]|1[0-2]))", text_blob)
    if direct:
        return direct.replace("/", "-")
    month_match = re.search(
        r"\b(jan(?:uary)?|feb(?:ruary)?|mar(?:ch)?|apr(?:il)?|may|jun(?:e)?|jul(?:y)?|aug(?:ust)?|sep(?:t(?:ember)?)?|oct(?:ober)?|nov(?:ember)?|dec(?:ember)?)\s+(20\d{2})\b",
        text_blob,
        flags=re.IGNORECASE,
    )
    if month_match:
        month_num = _MONTH_TO_NUM.get(text(month_match.group(1)).lower(), "")
        year = text(month_match.group(2))
        if month_num and year:
            return f"{year}-{month_num}"
    return ""


def _normalize_frequency(value: str) -> str:
    normalized = text(value).lower().replace(".", "").strip()
    mapping = {
        "qtrly": "quarterly",
        "qtr": "quarterly",
        "quarterly": "quarterly",
        "wkly": "weekly",
        "weekly": "weekly",
        "mo": "monthly",
        "monthly": "monthly",
        "annually": "annual",
        "annual": "annual",
        "semiannual": "semiannual",
        "semi-annual": "semiannual",
        "daily": "daily",
    }
    return mapping.get(normalized, normalized)


def _extract_frequency(text_blob: str) -> str:
    value = _search(r"\b(monthly|quarterly|weekly|annual|annually|semiannual|semi-annual|daily|qtrly|qtr|wkly|mo)\b", text_blob)
    if value:
        return _normalize_frequency(value)
    return ""


def _detect_critical_systems(text_blob: str) -> str:
    lowered = text_blob.lower()
    labels: list[str] = []
    for token, label in (
        ("refrigeration", "refrigeration"),
        ("cold room", "refrigeration"),
        ("freezer", "refrigeration"),
        ("dock", "dock equipment"),
        ("charging", "charging systems"),
        ("forklift", "forklift charging"),
        ("central plant", "central plant"),
        ("controls", "controls"),
        ("bms", "controls"),
        ("boiler", "boilers"),
        ("chiller", "chillers"),
        ("compressor", "compressors"),
        ("conveyor", "conveyors"),
    ):
        if token in lowered:
            labels.append(label)
    return ", ".join(dedupe(labels))


def _extract_open_workorders(text_blob: str) -> str:
    return (
        _search(r"(?:open workorders?|backlog)\s*[:=]?\s*(\d+)", text_blob)
        or _search(r"(\d+)\s*(?:open workorders?|backlog)", text_blob)
        or _search(r"(?:wo|w\/o)\s*(?:open|backlog|aging)?\s*[:=]?\s*(\d+)", text_blob)
        or _search(r"(\d+)\s*(?:wo|w\/o)\b", text_blob)
    )


def _heuristic_payload_from_text(document: dict[str, Any], source_family: str) -> dict[str, Any]:
    raw_text = _raw_text(document)
    raw_text_l = raw_text.lower()
    if not raw_text_l:
        return {}

    if source_family == "utility_bill_record":
        charge_type = "demand_charge" if "demand" in raw_text_l else "energy_charge" if "energy charge" in raw_text_l else ""
        service_type = "electricity" if any(token in raw_text_l for token in ("electric", "electricity", "kwh", "kw")) else "natural_gas" if "gas" in raw_text_l else ""
        demand_kw = (
            _search(r"(?:demand|peak|billed demand)\s*(?:kw)?\s*[:=]?\s*(\d+(?:\.\d+)?)\s*kw", raw_text)
            or _search(r"(\d+(?:\.\d+)?)\s*kw\s*(?:demand|peak|billed demand)", raw_text)
        )
        charge_amount = _search(r"(?:charge|amount|billed)\s*[:=]?\s*\$?\s*([\d,]+(?:\.\d+)?)", raw_text)
        billing_period = _extract_billing_period(raw_text)
        return {
            "records": [
                {
                    "statement_name": text(document.get("title")) or "parsed utility statement",
                    "service_type": service_type,
                    "charge_type": charge_type,
                    "charge_amount": charge_amount,
                    "demand_kw": demand_kw,
                    "billing_period": billing_period,
                }
            ]
        }

    if source_family == "utility_tariff_record":
        exposure_terms: list[str] = []
        if any(token in raw_text_l for token in ("power factor", "pf", "reactive", "kvar")):
            exposure_terms.append("power_factor")
        if any(token in raw_text_l for token in ("demand", "kw", "billing demand")):
            exposure_terms.append("demand")
        if any(token in raw_text_l for token in ("time of use", "tou", "on-peak", "off-peak", "on peak", "off peak")):
            exposure_terms.append("time_of_use")
        if "ratchet" in raw_text_l:
            exposure_terms.append("demand_ratchet")
        return {
            "records": [
                {
                    "tariff_name": text(document.get("title")) or "parsed tariff context",
                    "service_class": (
                        _search(r"(?:^|[\n;])\s*(?:service class|svc\s*cls|svc\s*class)\s*[:=]\s*([A-Za-z0-9][A-Za-z0-9 _/-]{0,40})", raw_text)
                        or _search(r"(?:service class|svc\s*cls|svc\s*class)\s*[:=]?\s*([A-Za-z0-9][A-Za-z0-9 _/-]{0,40})", raw_text)
                        or _search(r"(?:service class|svc\s*cls|svc\s*class)\s+([A-Za-z0-9][A-Za-z0-9 _/-]{0,40})", raw_text)
                        or " / ".join(exposure_terms)
                    ),
                    "rate_class": (
                        _search(r"(?:rate class|rate sch)\s*[:=]\s*([A-Za-z0-9][A-Za-z0-9 _/-]{0,20})", raw_text)
                        or _search(r"(?:^|[\n;])\s*(?:rate class|rate sch(?:edule)?)\s*[:=]\s*([A-Za-z0-9][A-Za-z0-9 _/-]{0,20})", raw_text)
                        or _search(r"(?:rate class|rate sch(?:edule)?)\s*[:=]?\s*([A-Za-z0-9][A-Za-z0-9 _/-]{0,20})", raw_text)
                        or _search(r"(?:rate class|rate sch(?:edule)?)\s+([A-Za-z0-9][A-Za-z0-9 _/-]{0,20})", raw_text)
                        or _search(r"(?:service class|svc\s*cls|svc\s*class)\s*[:=]?\s*([A-Za-z0-9][A-Za-z0-9 _/-]{0,20})", raw_text)
                    ),
                    "pf_charge": "present" if _contains_any(raw_text_l, ("power factor charge", "pf charge", "pf penalty", "power factor penalty")) else "",
                    "reactive_charge": "present" if _contains_any(raw_text_l, ("reactive charge", "reactive demand", "kvarh", "kvar")) else "",
                    "power_factor_threshold": (
                        _search(r"(?:power factor|pf)[^.;\n]{0,40}?(?:below|under|less than)\s*[:=]?\s*(0?\.\d+|\d{1,3}\s*%)", raw_text)
                        or _search(r"(?:below|under|less than)\s*[:=]?\s*(0?\.\d+|\d{1,3}\s*%)", raw_text)
                    ),
                    "demand_window": (
                        _search(r"((?:15|30|60)[ -]?minute(?: interval)?(?: billing)? demand)", raw_text)
                        or _search(r"((?:billing determinant|bill det)[^.;\n]*(?:15|30|60)[ -]?(?:minute|min)[^.;\n]*)", raw_text)
                    ),
                    "on_peak_window": (
                        _search(r"(?:on-peak|on peak|on pk)\s*(?:hours?|window)?\s*[:=]?\s*([0-9:apmAPM \-to]+)", raw_text)
                        or _search(r"((?:on-peak|on peak|on pk)[^.;\n]*)", raw_text)
                    ),
                    "demand_ratchet_signal": _search(r"((?:demand ratchet|ratchet|prior summer peak|prior peak)[^.;\n]*)", raw_text),
                    "coincident_peak_signal": _search(r"((?:coincident peak|4CP|5CP|cp tag)[^.;\n]*)", raw_text),
                }
            ]
        }

    if source_family == "lease_matrix_record":
        owner_scope = _extract_party_scope(raw_text, "owner")
        tenant_scope = _extract_party_scope(raw_text, "tenant")
        operator_scope = _extract_party_scope(raw_text, "operator")
        split_parts = []
        if owner_scope:
            split_parts.append(f"owner: {owner_scope}")
        if tenant_scope:
            split_parts.append(f"tenant: {tenant_scope}")
        if operator_scope:
            split_parts.append(f"operator: {operator_scope}")
        split = " | ".join(split_parts) or "owner / tenant responsibility split referenced" if any(token in raw_text_l for token in ("owner", "tenant", "responsibility")) else ""
        metering_scope = (
            _search(r"((?:direct[- ]metered|separately billed|submeter(?:ed|ing)?|split[- ]meter(?:ed)?)[^.;\n]*)", raw_text)
            or _search(r"((?:house meter)[^.;\n]*)", raw_text)
        )
        shared_loads = _search(r"((?:shared|house|base building)[^.;\n]*(?:load|meter)[^.;\n]*)", raw_text)
        control_boundary = ""
        if owner_scope or tenant_scope:
            control_boundary = "Owner and tenant burden split is explicitly described."
        elif metering_scope or shared_loads:
            control_boundary = "Metering or billing boundary is explicitly described."
        return {
            "responsibility_split": split,
            "metering_scope": metering_scope or ("submetered or split-metered load referenced" if "submeter" in raw_text_l or "meter" in raw_text_l else ""),
            "shared_loads": shared_loads,
            "owner_scope": owner_scope,
            "tenant_scope": tenant_scope,
            "operator_scope": operator_scope,
            "control_boundary": control_boundary,
            "boundary_note": _search(r"((?:separately billed|shared loads?|house meter|owner retains|tenant retains)[^.;\n]*)", raw_text),
        }

    if source_family == "submetering_record":
        metering_scope = _search(r"((?:submeter(?:ed|ing)?|metering boundary|house meter|panel split)[^.;\n]*)", raw_text)
        shared_loads = _search(r"((?:shared|house)[^.;\n]*(?:load|lighting|meter)[^.;\n]*)", raw_text)
        return {
            "metering_scope": metering_scope or ("submetering boundary referenced" if any(token in raw_text_l for token in ("submeter", "metering", "house meter")) else ""),
            "shared_loads": shared_loads or ("shared house loads referenced" if "shared" in raw_text_l or "house" in raw_text_l else ""),
            "boundary_note": _search(r"((?:owner meter|tenant meter|shared loads?)[^.;\n]*)", raw_text),
        }

    if source_family in {"maintenance_contract_record", "maintenance_log_record"}:
        frequency = _extract_frequency(raw_text)
        cadence_clause = _search(r"(every\s+\d+\s*(?:days?|weeks?|months?))", raw_text)
        recurrence_signal = _search(r"((?:weekly|monthly|quarterly|annual|qtrly|wkly|mo|every\s+\d+\s*(?:days?|weeks?|months?))[^.;\n]*(?:review|inspection|pm|visit|service)[^.;\n]*)", raw_text)
        repeat_failure_signal = _search(r"((?:no\s+chronic[^.;\n]*|repeat(?:ed)?[^.;\n]*|recurring[^.;\n]*|chronic[^.;\n]*|nuisance[^.;\n]*|recur(?:ring)?[^.;\n]*)\b(?:alarm|fault|failure|trip|issue|problem)?[^.;\n]*)", raw_text)
        open_workorders = _extract_open_workorders(raw_text)
        downtime_signal = (
            _search(r"((?:downtime|outage|unavailable)[^.;\n]*)", raw_text)
            or _search(r"((?:dt|down)\s*[:=]?\s*\d+(?:\.\d+)?\s*(?:h|hr|hrs|hours?)[^.;\n]*)", raw_text)
        )
        scope_clause = _search(r"(?:(?:for|covering|covers|scope)\s*[:=]?\s*)([^.;\n]+)", raw_text)
        critical_system = _detect_critical_systems(raw_text)
        return {
            "pm_program": frequency or cadence_clause or "maintenance program referenced",
            "maintenance_program": recurrence_signal or frequency or cadence_clause,
            "contract_scope": scope_clause,
            "system_scope": scope_clause or ("critical systems referenced" if critical_system else ""),
            "critical_system": critical_system,
            "recurrence_signal": recurrence_signal or cadence_clause or frequency,
            "repeat_failure_signal": repeat_failure_signal,
            "open_workorders": open_workorders,
            "downtime_signal": downtime_signal,
            "notes": _search(r"((?:ir scan|inspection|leak survey|service note|thermography|vibration survey|lube route)[^.;\n]*)", raw_text),
        }

    if source_family == "cmms_record":
        workorders = _extract_open_workorders(raw_text)
        return {
            "open_workorders": workorders,
            "program_signal": "cmms or workorder process referenced",
            "repeat_failure_signal": _search(r"((?:repeat(?:ed)?|recurring|chronic|no chronic|nuisance|recur(?:ring)?)[^.;\n]*(?:alarm|fault|failure|trip|issue|problem)?[^.;\n]*)", raw_text),
            "critical_system": _detect_critical_systems(raw_text),
            "notes": _search(r"((?:weekly|daily|wkly)[^.;\n]*(?:review|triage|meeting)[^.;\n]*)", raw_text),
        }

    if source_family == "schedule_record":
        operating_pattern = _search(r"\b(24\/[567]|24x[567]|24\s*hours?\s*/\s*[567]\s*days?)\b", raw_text)
        dock_turns = _search(r"(?:dock turns?|turns per day|throughput)\s*[:=]?\s*(\d+)", raw_text)
        return {
            "operating_pattern": operating_pattern,
            "dock_turns_per_day": dock_turns,
        }

    if source_family == "equipment_inventory_record":
        fleet = _search(r"(?:fleet count|forklifts?|compressors?)\s*[:=]?\s*(\d+)", raw_text)
        return {
            "records": [
                {
                    "critical_system": "forklift charging" if "forklift" in raw_text_l or "charging" in raw_text_l else _detect_critical_systems(raw_text) or "equipment inventory referenced",
                    "fleet_count": fleet,
                }
            ]
        }

    if source_family == "permit_record":
        permit_type = (
            "air permit" if "air permit" in raw_text else
            "wastewater permit" if "wastewater" in raw_text else
            "refrigeration safety permit" if "refrigeration" in raw_text else
            "permit context referenced"
        )
        return {"records": [{"permit_type": permit_type}]}

    if source_family == "bms_trend_record":
        return {
            "defrost_schedule": "staggered" if "defrost" in raw_text else "",
            "trend_signal": "bms or controls trend referenced",
        }

    return {}


def _payload_for_source_family(document: dict[str, Any], source_family: str) -> dict[str, Any]:
    extracted_fields = document.get("extracted_fields")
    extracted_records = document.get("extracted_records")
    if not isinstance(extracted_records, list):
        extracted_records = document.get("records")

    payload: dict[str, Any]
    if isinstance(extracted_records, list) and extracted_records:
        payload = {
            "records": [dict(record) for record in extracted_records if isinstance(record, dict)],
            "document_fields": dict(extracted_fields) if isinstance(extracted_fields, dict) else {},
        }
    elif isinstance(extracted_fields, dict) and extracted_fields:
        payload = dict(extracted_fields)
    else:
        payload = _heuristic_payload_from_text(document, source_family) or {"records": []}

    payload["document_meta"] = {
        "document_id": text(document.get("document_id")),
        "document_type": text(document.get("document_type")),
        "title": text(document.get("title")),
        "scope": text(document.get("scope")) or "ASSET_LEVEL",
        "summary": text(document.get("summary")),
        "text_excerpt": text(document.get("text_excerpt")),
        "source_family": source_family,
    }
    return payload


def build_raw_local_evidence_source_register(
    *,
    pipeline: dict[str, Any],
    target_definition: dict[str, Any],
) -> list[dict[str, Any]]:
    documents = _document_container(pipeline)
    if not documents:
        return []

    target_label = (
        text(target_definition.get("target_identifier"))
        or text(target_definition.get("target_name"))
        or text(target_definition.get("address_raw"))
        or "local-asset"
    )
    rows: list[dict[str, Any]] = []
    for index, document in enumerate(documents, start=1):
        source_families = _infer_source_families(document)
        if not source_families:
            continue
        document_id = text(document.get("document_id")) or f"doc-{index}"
        title = text(document.get("title")) or text(document.get("document_type")) or "Raw local evidence document"
        scope = text(document.get("scope")) or "ASSET_LEVEL"
        authority_score = text(document.get("authority_score")) or "medium"
        recency = text(document.get("recency")) or "current"
        used_for = dedupe(
            list_text(document.get("used_for"))
            + ["raw_local_evidence"]
        )
        for source_family in source_families:
            rows.append(
                {
                    "source_id": f"raw_local_evidence::{target_label}::{_slug(document_id)}::{source_family}",
                    "url": text(document.get("url")),
                    "title": title,
                    "authority_score": authority_score,
                    "scope": scope,
                    "scope_raw": scope.lower(),
                    "round_id": "raw_local_evidence_ingestion",
                    "recency": recency,
                    "accepted": True,
                    "rejection_reason": "",
                    "source_family": source_family,
                    "payload": _payload_for_source_family(document, source_family),
                    "used_for": used_for + [source_family],
                }
            )
    return rows
