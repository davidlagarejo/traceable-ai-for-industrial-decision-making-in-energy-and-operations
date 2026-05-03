from __future__ import annotations

from collections import defaultdict
from typing import Any

from .schemas import text
from .source_hierarchy import source_precedence_policy


def _haystack(row: dict[str, Any]) -> str:
    return " ".join(
        text(row.get(key)).lower()
        for key in (
            "source_id",
            "title",
            "url",
            "notes",
            "text_excerpt",
            "detail",
            "asset_name",
            "operator_name",
            "owner_name",
        )
    )


def _extract_claims(row: dict[str, Any]) -> list[dict[str, Any]]:
    haystack = _haystack(row)
    claims: list[dict[str, Any]] = []

    subtype_tokens = [
        ("cold_chain", ("cold", "freezer", "refrigerat", "temperature-controlled")),
        ("cross_dock", ("cross-dock", "cross dock")),
        ("fulfillment", ("fulfillment", "e-commerce", "pick and pack")),
        ("dry_warehouse", ("dry warehouse", "ambient storage", "warehouse", "distribution center")),
    ]
    for value, tokens in subtype_tokens:
        if any(token in haystack for token in tokens):
            claims.append({"domain": "asset_subtype", "value": value})
            break

    system_tokens = [
        ("refrigeration", ("refrigerat", "freezer", "cooler")),
        ("thermal_process", ("boiler", "steam", "furnace", "kiln", "combustion")),
        ("compressed_air", ("compressed air", "air compressor")),
        ("rooftop_hvac", ("rtu", "rooftop", "hvac", "mechanical")),
    ]
    for value, tokens in system_tokens:
        if any(token in haystack for token in tokens):
            claims.append({"domain": "system_topology", "value": value})
            break

    tariff_tokens = [
        ("demand_charge_exposure", ("demand charge", "peak demand", "kw demand")),
        ("power_factor_exposure", ("power factor", "reactive", "kvar")),
        ("time_of_use_exposure", ("time-of-use", "tou", "on-peak", "off-peak")),
        ("flat_energy_only", ("flat rate", "energy-only", "per kwh only")),
    ]
    for value, tokens in tariff_tokens:
        if any(token in haystack for token in tokens):
            claims.append({"domain": "tariff_driver", "value": value})
            break

    return claims


def build_authority_precedence_register(
    *,
    source_register: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for row in list(source_register or []):
        precedence = source_precedence_policy(row)
        rows.append(
            {
                "source_id": text(row.get("source_id")) or text(row.get("title")),
                "source_family": precedence["source_family"],
                "source_tier": precedence["source_tier"],
                "authority_score": precedence["authority_score"],
                "precedence_score": precedence["precedence_score"],
                "precedence_basis": precedence["precedence_basis"],
            }
        )
    return rows


def build_source_conflict_register(
    *,
    source_register: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    precedence_rows = build_authority_precedence_register(source_register=source_register)
    precedence_by_source = {
        text(row.get("source_id")): row
        for row in precedence_rows
        if text(row.get("source_id"))
    }
    claims_by_domain: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for source in list(source_register or []):
        source_id = text(source.get("source_id")) or text(source.get("title"))
        precedence = precedence_by_source.get(source_id, {})
        for claim in _extract_claims(source):
            claims_by_domain[text(claim.get("domain"))].append(
                {
                    "source_id": source_id,
                    "source_family": text(source.get("source_family")),
                    "value": text(claim.get("value")),
                    "precedence_score": int(precedence.get("precedence_score", 0) or 0),
                    "source_tier": text(precedence.get("source_tier")),
                    "authority_score": text(precedence.get("authority_score")),
                }
            )

    rows: list[dict[str, Any]] = []
    for domain, claims in claims_by_domain.items():
        unique_values = {text(claim.get("value")) for claim in claims if text(claim.get("value"))}
        if len(unique_values) <= 1:
            continue
        ranked = sorted(claims, key=lambda row: (-int(row.get("precedence_score", 0) or 0), text(row.get("source_id"))))
        lead = ranked[0]
        challengers = [row for row in ranked[1:] if text(row.get("value")) != text(lead.get("value"))]
        if not challengers:
            continue
        top_delta = int(lead.get("precedence_score", 0) or 0) - int(challengers[0].get("precedence_score", 0) or 0)
        unresolved = top_delta < 15 and int(lead.get("precedence_score", 0) or 0) >= 90
        severity = "critical" if unresolved else "warning"
        rows.append(
            {
                "conflict_domain": domain,
                "lead_value": text(lead.get("value")),
                "lead_source_id": text(lead.get("source_id")),
                "lead_source_family": text(lead.get("source_family")),
                "lead_precedence_score": int(lead.get("precedence_score", 0) or 0),
                "conflicting_values": sorted({text(row.get("value")) for row in challengers if text(row.get("value"))}),
                "conflicting_source_ids": [text(row.get("source_id")) for row in challengers if text(row.get("source_id"))],
                "conflicting_source_families": sorted({text(row.get("source_family")) for row in challengers if text(row.get("source_family"))}),
                "precedence_delta": top_delta,
                "severity": severity,
                "resolution_state": "unresolved_high_authority_conflict" if unresolved else "resolved_to_higher_precedence_source",
                "why": (
                    f"Conflicting `{domain}` signals were observed. Higher-precedence source supports `{text(lead.get('value'))}`."
                    if not unresolved
                    else f"High-precedence sources disagree on `{domain}` and should block certainty upgrades."
                ),
            }
        )
    return rows


def build_conflict_resolution_outcome_register(
    *,
    source_conflict_register: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    return [
        {
            "conflict_domain": text(row.get("conflict_domain")),
            "resolution_state": text(row.get("resolution_state")),
            "severity": text(row.get("severity")),
            "leading_interpretation": text(row.get("lead_value")),
            "claim_upgrade_allowed": text(row.get("resolution_state")) != "unresolved_high_authority_conflict",
        }
        for row in list(source_conflict_register or [])
    ]
