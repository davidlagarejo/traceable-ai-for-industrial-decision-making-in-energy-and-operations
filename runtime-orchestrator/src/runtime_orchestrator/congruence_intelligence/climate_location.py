from __future__ import annotations

from typing import Any

from .schemas import text


def _jurisdictions(target_definition: dict[str, Any]) -> list[str]:
    return [text(code) for code in list(target_definition.get("jurisdiction_scope", []) or []) if text(code)]


def _source_family_set(source_register: list[dict[str, Any]]) -> set[str]:
    return {
        text(row.get("source_family"))
        for row in source_register
        if text(row.get("source_family"))
    }


def build_climate_location_context_register(
    *,
    target_definition: dict[str, Any],
    asset_family_research_profile: dict[str, Any],
    source_register: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    if text(asset_family_research_profile.get("route_state")) != "operational_asset_candidate":
        return []

    source_families = _source_family_set(source_register)
    asset_family = text(asset_family_research_profile.get("asset_family"))
    jurisdictions = _jurisdictions(target_definition)
    return [
        {
            "context_name": "climate_and_location_structural_context",
            "context_logic": f"Climate and jurisdiction shape the plausible load story for `{asset_family}` and can invalidate naive peer logic if they are ignored.",
            "evidence_state": "OBSERVED_FACT" if "climate_normals_record" in source_families else "CONDITIONAL_HYPOTHESIS",
            "jurisdiction_scope": jurisdictions,
            "allowed_use": "Use as normalization and demand-context support.",
            "prohibited_use": "Do not treat climate alone as proof of local operational schedule or fault behavior.",
        }
    ]


def build_utility_tariff_context_register(
    *,
    asset_family_research_profile: dict[str, Any],
    operational_intake_pack: dict[str, Any],
    source_register: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    if text(asset_family_research_profile.get("route_state")) != "operational_asset_candidate":
        return []

    source_families = _source_family_set(source_register)
    utility_state = text((operational_intake_pack.get("utility_and_tariff_pack", {}) or {}).get("current_state"))
    return [
        {
            "tariff_context": "utility tariff and rate structure context",
            "context_state": utility_state or "not_yet_evidenced",
            "evidence_state": "OBSERVED_FACT" if "utility_tariff_record" in source_families else "CONDITIONAL_HYPOTHESIS",
            "plausible_cost_logic": "Tariff structure can make demand, schedule, PF or duty timing more important than aggregate consumption alone.",
            "non_substitutable_for": ["site-specific bill truth", "observed charge realization without bills"],
        }
    ]
