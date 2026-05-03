from __future__ import annotations

import json
import re
from hashlib import sha256
from typing import Any

from .schemas import dedupe, text

_ASSET_NAME_KEYS = (
    "asset_name",
    "site_name",
    "property_name",
    "facility_name",
    "document_asset_name",
    "target_name",
)
_OWNER_NAME_KEYS = ("owner_name", "owner_entity", "landlord_name", "landlord_entity")
_OPERATOR_NAME_KEYS = ("operator_name", "operator_entity", "occupier_name", "facility_operator")
_TENANT_NAME_KEYS = ("tenant_name", "tenant_entity")

_DIRECT_ASSET_SOURCE_FAMILIES = {
    "geospatial_public_record",
    "benchmarking_disclosure_record",
    "permit_record",
    "utility_bill_record",
    "utility_tariff_record",
    "equipment_inventory_record",
    "submetering_record",
    "meter_interval_record",
    "lease_matrix_record",
    "maintenance_contract_record",
    "maintenance_log_record",
    "cmms_record",
    "bms_trend_record",
    "schedule_record",
    "operator_input_record",
    "climate_normals_record",
}
_BOUNDARY_RELEVANT_SOURCE_FAMILIES = {
    "lease_matrix_record",
    "submetering_record",
    "meter_interval_record",
    "operator_input_record",
    "schedule_record",
    "utility_bill_record",
    "utility_tariff_record",
    "bms_trend_record",
    "equipment_inventory_record",
}
_ECONOMIC_BOUNDARY_SOURCE_FAMILIES = {
    "lease_matrix_record",
    "submetering_record",
    "meter_interval_record",
    "utility_bill_record",
    "utility_tariff_record",
    "operator_input_record",
}
_OPERATOR_CONTEXT_SOURCE_FAMILIES = {
    "operator_input_record",
    "schedule_record",
    "equipment_inventory_record",
    "maintenance_contract_record",
    "maintenance_log_record",
    "cmms_record",
    "bms_trend_record",
}
_OWNER_OR_ISSUER_CONTEXT_SOURCE_FAMILIES = {
    "issuer_financial_record",
}
_TENANT_SHARED_LOAD_SOURCE_FAMILIES = {
    "lease_matrix_record",
    "submetering_record",
    "meter_interval_record",
}
_NOISE_TOKENS = {
    "the",
    "and",
    "for",
    "from",
    "with",
    "tower",
    "building",
    "facility",
    "site",
    "property",
    "page",
    "record",
    "summary",
    "utility",
    "bill",
    "tariff",
    "permit",
    "operator",
}


def _normalize(value: Any) -> str:
    normalized = re.sub(r"[^a-z0-9]+", " ", text(value).lower()).strip()
    return re.sub(r"\s+", " ", normalized)


def _tokens(value: Any) -> set[str]:
    return {
        token
        for token in _normalize(value).split()
        if len(token) >= 3 and token not in _NOISE_TOKENS
    }


def _semantic_match(candidate: Any, aliases: list[str]) -> bool:
    normalized_candidate = _normalize(candidate)
    if not normalized_candidate:
        return False
    candidate_tokens = _tokens(normalized_candidate)
    for alias in aliases:
        normalized_alias = _normalize(alias)
        if not normalized_alias:
            continue
        if normalized_candidate == normalized_alias:
            return True
        if normalized_candidate in normalized_alias or normalized_alias in normalized_candidate:
            return True
        alias_tokens = _tokens(normalized_alias)
        shared_tokens = candidate_tokens.intersection(alias_tokens)
        if candidate_tokens and alias_tokens and (
            candidate_tokens.issubset(alias_tokens) or alias_tokens.issubset(candidate_tokens)
        ) and len(shared_tokens) >= min(2, len(candidate_tokens), len(alias_tokens)):
            return True
    return False


def _aliases(target_definition: dict[str, Any], *keys: str) -> list[str]:
    values: list[str] = []
    for key in keys:
        raw = text(target_definition.get(key))
        if raw:
            values.append(raw)
            if "," in raw:
                values.append(raw.split(",", 1)[0].strip())
    return dedupe(values)


def build_case_fingerprint(*, target_definition: dict[str, Any]) -> str:
    payload = {
        "target_name": text(target_definition.get("target_name")),
        "target_identifier": text(target_definition.get("target_identifier")),
        "address_raw": text(target_definition.get("address_raw")),
        "target_type": text(target_definition.get("target_type")),
        "jurisdiction_scope": [text(value) for value in list(target_definition.get("jurisdiction_scope", []) or []) if text(value)],
    }
    return sha256(json.dumps(payload, sort_keys=True).encode()).hexdigest()[:16]


def _payload(row: dict[str, Any]) -> dict[str, Any]:
    payload = row.get("payload")
    return dict(payload) if isinstance(payload, dict) else {}


def _candidate_value(row: dict[str, Any], payload: dict[str, Any], keys: tuple[str, ...]) -> str:
    for key in keys:
        value = text(row.get(key))
        if value:
            return value
        value = text(payload.get(key))
        if value:
            return value
    return ""


def _relation_class(source_family: str) -> str:
    if source_family in _OWNER_OR_ISSUER_CONTEXT_SOURCE_FAMILIES:
        return "owner_or_issuer_context"
    if source_family in _OPERATOR_CONTEXT_SOURCE_FAMILIES:
        return "operator_or_site_record"
    if source_family in _BOUNDARY_RELEVANT_SOURCE_FAMILIES:
        return "boundary_or_shared_load_record"
    return "asset_or_public_record"


def _resolution_row(
    *,
    row: dict[str, Any],
    case_fingerprint: str,
    asset_aliases: list[str],
    owner_aliases: list[str],
    operator_aliases: list[str],
    tenant_aliases: list[str],
) -> dict[str, Any]:
    payload = _payload(row)
    source_family = text(row.get("source_family"))
    source_id = text(row.get("source_id"))
    title = text(row.get("title"))
    url = text(row.get("url"))
    asset_name = _candidate_value(row, payload, _ASSET_NAME_KEYS)
    owner_name = _candidate_value(row, payload, _OWNER_NAME_KEYS)
    operator_name = _candidate_value(row, payload, _OPERATOR_NAME_KEYS)
    tenant_name = _candidate_value(row, payload, _TENANT_NAME_KEYS)

    resolution_role = "asset"
    resolution_state = "unresolved_case_alignment"
    coherence_state = "unresolved_case_alignment"
    evidence_state = "CONDITIONAL_HYPOTHESIS"
    supporting_basis = "No explicit entity binding was observed in the source row."

    if asset_name:
        if _semantic_match(asset_name, asset_aliases):
            resolution_state = "resolved_asset_match_l4"
            coherence_state = "coherent_with_case"
            evidence_state = "OBSERVED_FACT"
            supporting_basis = "Source explicitly names the target asset and matches the bounded case identity."
        else:
            resolution_state = "foreign_asset_conflict"
            coherence_state = "conflicting_foreign_entity"
            evidence_state = "OBSERVED_FACT"
            supporting_basis = "Source explicitly names a different asset than the bounded target."
    elif operator_name:
        resolution_role = "operator"
        if operator_aliases and _semantic_match(operator_name, operator_aliases):
            resolution_state = "resolved_operator_match_l3"
            coherence_state = "coherent_with_case"
            evidence_state = "OBSERVED_FACT"
            supporting_basis = "Source explicitly names the operator and matches the bounded operator context."
        elif operator_aliases:
            resolution_state = "foreign_operator_conflict"
            coherence_state = "conflicting_foreign_entity"
            evidence_state = "OBSERVED_FACT"
            supporting_basis = "Source explicitly names an operator that conflicts with the bounded operator context."
        else:
            resolution_state = "operator_context_unresolved"
            coherence_state = "unresolved_case_alignment"
            evidence_state = "CONDITIONAL_HYPOTHESIS"
            supporting_basis = "Source names an operator but the case has no bounded operator alias to match against."
    elif owner_name:
        resolution_role = "owner"
        if owner_aliases and _semantic_match(owner_name, owner_aliases):
            resolution_state = "resolved_owner_match_l3"
            coherence_state = "context_only_non_asset"
            evidence_state = "OBSERVED_FACT"
            supporting_basis = "Source explicitly names the owner and matches the bounded owner context."
        elif owner_aliases:
            resolution_state = "foreign_owner_conflict"
            coherence_state = "conflicting_foreign_entity"
            evidence_state = "OBSERVED_FACT"
            supporting_basis = "Source explicitly names an owner that conflicts with the bounded owner context."
        else:
            resolution_state = "owner_context_unresolved"
            coherence_state = "context_only_non_asset"
            evidence_state = "CONDITIONAL_HYPOTHESIS"
            supporting_basis = "Source names an owner but the case has no bounded owner alias to match against."
    elif tenant_name:
        resolution_role = "tenant"
        if tenant_aliases and _semantic_match(tenant_name, tenant_aliases):
            resolution_state = "resolved_tenant_match_l3"
            coherence_state = "coherent_with_case"
            evidence_state = "OBSERVED_FACT"
            supporting_basis = "Source explicitly names the tenant and matches the bounded tenant context."
        elif tenant_aliases:
            resolution_state = "foreign_tenant_conflict"
            coherence_state = "conflicting_foreign_entity"
            evidence_state = "OBSERVED_FACT"
            supporting_basis = "Source explicitly names a tenant that conflicts with the bounded tenant context."
        else:
            resolution_state = "tenant_context_unresolved"
            coherence_state = "unresolved_case_alignment"
            evidence_state = "CONDITIONAL_HYPOTHESIS"
            supporting_basis = "Source names a tenant but the case has no bounded tenant alias to match against."
    elif title and _semantic_match(title, asset_aliases):
        resolution_state = "resolved_asset_match_l3"
        coherence_state = "coherent_with_case"
        evidence_state = "OBSERVED_FACT"
        supporting_basis = "Source title contains the target asset identity."
    elif source_family in _OWNER_OR_ISSUER_CONTEXT_SOURCE_FAMILIES:
        resolution_role = "owner_context"
        resolution_state = "context_only_unbound"
        coherence_state = "context_only_non_asset"
        supporting_basis = "Source is issuer or owner context and cannot stand in for asset truth by itself."
    elif source_family in _DIRECT_ASSET_SOURCE_FAMILIES:
        if source_family in _OPERATOR_CONTEXT_SOURCE_FAMILIES:
            resolution_role = "operator_context"
            resolution_state = "family_aligned_operator_context_l2"
            supporting_basis = "Source family is operationally local to the site but lacks explicit named-entity confirmation."
        else:
            resolution_state = "family_aligned_asset_context_l2"
            supporting_basis = "Source family is asset-local and aligned with the case, but without explicit named-entity confirmation."
        coherence_state = "coherent_with_case"
    elif url and _semantic_match(url, asset_aliases):
        resolution_state = "resolved_asset_match_l2"
        coherence_state = "coherent_with_case"
        supporting_basis = "Source URL contains target asset identity."

    eligible_for_asset_truth = resolution_state in {
        "resolved_asset_match_l4",
        "resolved_asset_match_l3",
        "resolved_asset_match_l2",
        "family_aligned_asset_context_l2",
        "resolved_operator_match_l3",
        "family_aligned_operator_context_l2",
        "resolved_tenant_match_l3",
    }
    return {
        "case_fingerprint": case_fingerprint,
        "source_id": source_id,
        "source_family": source_family,
        "title": title,
        "url": url,
        "relation_class": _relation_class(source_family),
        "resolution_role": resolution_role,
        "resolution_state": resolution_state,
        "coherence_state": coherence_state,
        "evidence_state": evidence_state,
        "eligible_for_asset_truth": eligible_for_asset_truth,
        "asset_name_candidate": asset_name,
        "owner_name_candidate": owner_name,
        "operator_name_candidate": operator_name,
        "tenant_name_candidate": tenant_name,
        "supporting_basis": supporting_basis,
    }


def build_entity_resolution_register(
    *,
    target_definition: dict[str, Any],
    source_register: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    case_fingerprint = build_case_fingerprint(target_definition=target_definition)
    asset_aliases = _aliases(target_definition, "target_name", "target_identifier", "address_raw")
    owner_aliases = _aliases(target_definition, "owner_entity")
    operator_aliases = _aliases(target_definition, "operator_entity")
    tenant_aliases = _aliases(target_definition, "tenant_entity")
    return [
        _resolution_row(
            row=dict(row),
            case_fingerprint=case_fingerprint,
            asset_aliases=asset_aliases,
            owner_aliases=owner_aliases,
            operator_aliases=operator_aliases,
            tenant_aliases=tenant_aliases,
        )
        for row in list(source_register or [])
        if text(row.get("source_id")) or text(row.get("source_family"))
    ]


def build_entity_conflict_register(
    *,
    entity_resolution_register: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    conflicts: list[dict[str, Any]] = []
    for row in list(entity_resolution_register or []):
        resolution_state = text(row.get("resolution_state"))
        if resolution_state not in {
            "foreign_asset_conflict",
            "foreign_owner_conflict",
            "foreign_operator_conflict",
            "foreign_tenant_conflict",
        }:
            continue
        source_family = text(row.get("source_family"))
        severity = "critical" if resolution_state == "foreign_asset_conflict" or source_family in _BOUNDARY_RELEVANT_SOURCE_FAMILIES else "high"
        conflicts.append(
            {
                "case_fingerprint": text(row.get("case_fingerprint")),
                "source_id": text(row.get("source_id")),
                "source_family": source_family,
                "conflict_type": resolution_state,
                "severity": severity,
                "resolution_state": "unresolved_conflict",
                "blocking_scope": (
                    "asset_identity_and_peer_construction"
                    if severity == "critical"
                    else "control_or_economic_boundary_interpretation"
                ),
                "why_it_blocks": text(row.get("supporting_basis")),
            }
        )
    return conflicts


def _boundary_state(
    *,
    supporting_rows: list[dict[str, Any]],
    critical_conflicts: list[dict[str, Any]],
    bounded_threshold: int,
) -> str:
    if critical_conflicts:
        return "conflicted"
    if len(supporting_rows) >= bounded_threshold:
        return "bounded"
    if supporting_rows:
        return "partially_bounded"
    return "unresolved"


def build_asset_boundary_resolution_register(
    *,
    target_definition: dict[str, Any],
    entity_resolution_register: list[dict[str, Any]],
    entity_conflict_register: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    case_fingerprint = build_case_fingerprint(target_definition=target_definition)
    critical_conflicts = [
        dict(row)
        for row in list(entity_conflict_register or [])
        if text(row.get("severity")) == "critical"
    ]
    asset_rows = [
        dict(row)
        for row in list(entity_resolution_register or [])
        if bool(row.get("eligible_for_asset_truth"))
    ]
    control_rows = [
        dict(row)
        for row in asset_rows
        if text(row.get("source_family")) in _BOUNDARY_RELEVANT_SOURCE_FAMILIES
    ]
    economic_rows = [
        dict(row)
        for row in asset_rows
        if text(row.get("source_family")) in _ECONOMIC_BOUNDARY_SOURCE_FAMILIES
    ]
    return [
        {
            "case_fingerprint": case_fingerprint,
            "boundary_dimension": "physical_asset_boundary",
            "boundary_state": _boundary_state(supporting_rows=asset_rows, critical_conflicts=critical_conflicts, bounded_threshold=2),
            "supporting_source_ids": dedupe([text(row.get("source_id")) for row in asset_rows]),
            "blocking_conflict_count": len(critical_conflicts),
            "allowed_use": ["asset-level routing", "bounded operational logic"] if asset_rows else [],
        },
        {
            "case_fingerprint": case_fingerprint,
            "boundary_dimension": "operational_control_boundary",
            "boundary_state": _boundary_state(supporting_rows=control_rows, critical_conflicts=critical_conflicts, bounded_threshold=2),
            "supporting_source_ids": dedupe([text(row.get("source_id")) for row in control_rows]),
            "blocking_conflict_count": len(critical_conflicts),
            "allowed_use": ["control-boundary interpretation", "peer-construction readiness"] if control_rows else [],
        },
        {
            "case_fingerprint": case_fingerprint,
            "boundary_dimension": "economic_value_boundary",
            "boundary_state": _boundary_state(supporting_rows=economic_rows, critical_conflicts=critical_conflicts, bounded_threshold=2),
            "supporting_source_ids": dedupe([text(row.get("source_id")) for row in economic_rows]),
            "blocking_conflict_count": len(critical_conflicts),
            "allowed_use": ["value-capture interpretation", "tariff and bill framing"] if economic_rows else [],
        },
    ]


def build_owner_operator_tenant_resolution_register(
    *,
    target_definition: dict[str, Any],
    entity_resolution_register: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    case_fingerprint = build_case_fingerprint(target_definition=target_definition)
    rows = list(entity_resolution_register or [])

    def _supporting_count(states: set[str]) -> int:
        return sum(1 for row in rows if text(row.get("resolution_state")) in states)

    owner_entity = text(target_definition.get("owner_entity"))
    operator_entity = text(target_definition.get("operator_entity"))
    tenant_entity = text(target_definition.get("tenant_entity"))

    out: list[dict[str, Any]] = []
    if owner_entity:
        out.append(
            {
                "case_fingerprint": case_fingerprint,
                "party": owner_entity,
                "role_type": "owner",
                "resolution_state": "resolved_owner_context" if _supporting_count({"resolved_owner_match_l3"}) else "declared_only_unconfirmed",
                "supporting_source_count": _supporting_count({"resolved_owner_match_l3"}),
            }
        )
    if operator_entity:
        out.append(
            {
                "case_fingerprint": case_fingerprint,
                "party": operator_entity,
                "role_type": "operator",
                "resolution_state": "resolved_operator_context" if _supporting_count({"resolved_operator_match_l3", "family_aligned_operator_context_l2"}) else "declared_only_unconfirmed",
                "supporting_source_count": _supporting_count({"resolved_operator_match_l3", "family_aligned_operator_context_l2"}),
            }
        )
    tenant_support = _supporting_count({"resolved_tenant_match_l3"}) + sum(
        1
        for row in rows
        if text(row.get("source_family")) in _TENANT_SHARED_LOAD_SOURCE_FAMILIES and bool(row.get("eligible_for_asset_truth"))
    )
    if tenant_entity or tenant_support:
        out.append(
            {
                "case_fingerprint": case_fingerprint,
                "party": tenant_entity or "tenant_or_shared_load_context",
                "role_type": "tenant_or_shared_load_context",
                "resolution_state": "resolved_tenant_or_shared_load_context" if tenant_support else "declared_only_unconfirmed",
                "supporting_source_count": tenant_support,
            }
        )
    return out


def derive_entity_resolution_state(
    *,
    entity_resolution_register: list[dict[str, Any]],
    entity_conflict_register: list[dict[str, Any]],
    asset_boundary_resolution_register: list[dict[str, Any]],
) -> str:
    if any(text(row.get("severity")) == "critical" for row in list(entity_conflict_register or [])):
        return "critical_conflict"
    if any(text(row.get("boundary_state")) == "bounded" for row in list(asset_boundary_resolution_register or [])):
        return "bounded"
    if any(bool(row.get("eligible_for_asset_truth")) for row in list(entity_resolution_register or [])):
        return "partially_bounded"
    return "unresolved"
