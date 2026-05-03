from __future__ import annotations

from typing import Any

CONFIRMATION_STATES = (
    "DECLARED_BY_USER",
    "PUBLICLY_CONFIRMED",
    "AUTHORITY_CONFIRMED",
    "OPERATOR_CONFIRMED",
    "FIELD_VERIFIED",
)

_NOT_OBSERVED_STATUSES = {
    "NOT_OBSERVED",
    "NOT_PUBLICLY_AVAILABLE",
    "REQUIRES_CLIENT_INPUT",
    "BLOCKING_FIELD",
}

_OPERATOR_CONFIRMED_FAMILIES = {
    "operator_input_record",
    "utility_bill_record",
    "utility_tariff_record",
    "lease_matrix_record",
    "submetering_record",
    "meter_interval_record",
    "equipment_inventory_record",
    "maintenance_contract_record",
    "maintenance_log_record",
    "cmms_record",
    "schedule_record",
    "bms_trend_record",
}

_AUTHORITY_CONFIRMED_FAMILIES = {
    "geospatial_public_record",
    "benchmarking_disclosure_record",
    "permit_record",
    "industrial_emissions_record",
    "regulatory_record",
}

_AUTHORITY_TOKENS = (
    "assessor",
    "parcel",
    "property_record",
    "pluto",
    "dof",
    "benchmarking",
    "ll84",
    "ll97",
    "permit",
    "ghgrp",
    "emissions",
    "county appraisal",
    "covered buildings list",
)

_OPERATOR_TOKENS = (
    "operator",
    "lease",
    "submeter",
    "meter interval",
    "maintenance",
    "cmms",
    "workorder",
    "schedule",
    "bms",
    "utility bill",
    "tariff sheet",
)

_CRITICAL_FIELDS = {
    "asset_name",
    "address",
    "parcel_id",
    "asset_class",
    "GFA",
    "year_built",
    "occupancy_use",
    "tenant_control_boundary",
    "primary_fuel",
    "HVAC_type",
    "operating_schedule",
    "current_EUI",
    "compliance_filings",
}


def _row_text(row: dict[str, Any]) -> str:
    return " ".join(
        str(row.get(key, "") or "").strip().lower()
        for key in ("source_id", "source_family", "source_title", "notes")
    )


def derive_confirmation_state(row: dict[str, Any]) -> str:
    status = str(row.get("status", "") or "").strip().upper()
    if status in _NOT_OBSERVED_STATUSES:
        return ""

    source_id = str(row.get("source_id", "") or "").strip().lower()
    source_family = str(row.get("source_family", "") or "").strip().lower()
    authority_score = str(row.get("authority_score", "") or "").strip().lower()
    scope = str(row.get("scope", "") or "").strip().upper()
    haystack = _row_text(row)

    if "field_verified" in haystack or authority_score == "field_verified":
        return "FIELD_VERIFIED"
    if source_id.startswith("declared_input::") or authority_score == "declared_input":
        return "DECLARED_BY_USER"
    if source_family in _OPERATOR_CONFIRMED_FAMILIES or any(token in haystack for token in _OPERATOR_TOKENS):
        return "OPERATOR_CONFIRMED"
    if (
        source_family in _AUTHORITY_CONFIRMED_FAMILIES
        or any(token in haystack for token in _AUTHORITY_TOKENS)
        or (authority_score == "high" and scope == "ASSET_LEVEL")
    ):
        return "AUTHORITY_CONFIRMED"
    if source_id:
        return "PUBLICLY_CONFIRMED"
    return "DECLARED_BY_USER"


def annotate_asset_field_register(asset_field_register: list[dict[str, Any]]) -> list[dict[str, Any]]:
    annotated_rows: list[dict[str, Any]] = []
    for row in asset_field_register:
        annotated = dict(row)
        confirmation_state = derive_confirmation_state(annotated)
        annotated["confirmation_state"] = confirmation_state
        annotated["verified_evidence"] = confirmation_state in {
            "AUTHORITY_CONFIRMED",
            "OPERATOR_CONFIRMED",
            "FIELD_VERIFIED",
        }
        if confirmation_state == "DECLARED_BY_USER":
            annotated["admissibility"] = "DECLARED_INPUT_ONLY"
            notes = str(annotated.get("notes", "") or "").strip()
            downgrade_note = "Declared input is retained as a lead but downgraded below verified evidence."
            if downgrade_note not in notes:
                annotated["notes"] = f"{notes} {downgrade_note}".strip()
        annotated_rows.append(annotated)
    return annotated_rows


def build_declared_input_downgrade_register(asset_field_register: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for row in asset_field_register:
        if str(row.get("confirmation_state", "") or "").strip() != "DECLARED_BY_USER":
            continue
        if str(row.get("status", "") or "").strip().upper() in _NOT_OBSERVED_STATUSES:
            continue
        field = str(row.get("field", "") or "").strip()
        rows.append(
            {
                "field": field,
                "source_id": str(row.get("source_id", "") or "").strip() or f"declared_input::{field}",
                "confirmation_state": "DECLARED_BY_USER",
                "downgraded_admissibility": "DECLARED_INPUT_ONLY",
                "max_maturity_level": 1,
                "severity": "critical" if field in _CRITICAL_FIELDS else "warning",
                "why_not_verified": "Declared input is not verified evidence and cannot unlock strong asset-level claims by itself.",
                "upgrade_needed": (
                    f"Add public authority, operator, or field-verified evidence for {field}."
                    if field
                    else "Add stronger evidence."
                ),
                "claim_impact": (
                    f"{field} remains usable only for bounded screening context until confirmed."
                    if field
                    else "Field remains screening-only until confirmed."
                ),
            }
        )
    return rows
