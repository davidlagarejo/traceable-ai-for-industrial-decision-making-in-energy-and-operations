from __future__ import annotations

from typing import Any

from .schemas import text


def _source_family_set(source_register: list[dict[str, Any]]) -> set[str]:
    return {
        text(row.get("source_family"))
        for row in source_register
        if text(row.get("source_family"))
    }


def _jurisdictions(target_definition: dict[str, Any]) -> list[str]:
    return [text(code) for code in list(target_definition.get("jurisdiction_scope", []) or []) if text(code)]


def build_regulatory_physics_register(
    *,
    target_definition: dict[str, Any],
    asset_family_research_profile: dict[str, Any],
    subsystem_register: list[dict[str, Any]],
    source_register: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    if text(asset_family_research_profile.get("route_state")) != "operational_asset_candidate":
        return []

    asset_family = text(asset_family_research_profile.get("asset_family"))
    source_families = _source_family_set(source_register)
    jurisdictions = _jurisdictions(target_definition)
    subsystem_names = {text(row.get("subsystem_name")) for row in subsystem_register if text(row.get("subsystem_name"))}
    rows: list[dict[str, Any]] = []

    if asset_family == "commercial_building":
        if any(code.startswith("US-NY-NYC") for code in jurisdictions):
            rows.append(
                {
                    "regulatory_signal": "NYC benchmarking and building performance obligations",
                    "physical_implication": "Owner-facing compliance logic attaches to whole-building performance and can collide with unresolved tenant or control boundaries.",
                    "evidence_state": "OBSERVED_FACT" if "benchmarking_disclosure_record" in source_families else "CONDITIONAL_HYPOTHESIS",
                    "what_it_supports": ["screening-grade compliance context", "covered-building risk framing"],
                    "what_it_does_not_support": ["compliance closure", "owner-capturable retrofit ROI"],
                }
            )
        if "HVAC / central plant" in subsystem_names:
            rows.append(
                {
                    "regulatory_signal": "Building-performance rules intersect central plant and control topology",
                    "physical_implication": "Compliance pressure may push capital toward base-building systems before the owner knows whether those systems dominate the economics.",
                    "evidence_state": "CONDITIONAL_HYPOTHESIS",
                    "what_it_supports": ["request for central plant topology", "control-boundary verification"],
                    "what_it_does_not_support": ["technical closure of retrofit package"],
                }
            )

    if asset_family == "infrastructure_node":
        rows.append(
            {
                "regulatory_signal": "Service, safety or node-level operating constraints",
                "physical_implication": "Reliability, dispatch or switching obligations can define which optimization moves are admissible before any tariff-only framing closes.",
                "evidence_state": "CONDITIONAL_HYPOTHESIS",
                "what_it_supports": ["request for continuity and dispatch evidence", "bounded reliability-aware redesign framing"],
                "what_it_does_not_support": ["assumption that visible demand cost is avoidable waste"],
            }
        )

    if asset_family in {"industrial_manufacturing", "thermal_process_site", "utility_heavy_site"}:
        if "permit_record" in source_families or "regulatory_coverage_record" in source_families:
            rows.append(
                {
                    "regulatory_signal": "Industrial environmental or process permit context",
                    "physical_implication": "Permits can imply combustion, thermal, emissions, wastewater or material-handling relevance without proving current operating condition.",
                    "evidence_state": "OBSERVED_FACT" if "permit_record" in source_families else "CONDITIONAL_HYPOTHESIS",
                    "what_it_supports": ["bounded process-duty hypothesis", "permit-constrained redesign framing"],
                    "what_it_does_not_support": ["proof of current equipment condition", "proof of current loss mechanism"],
                }
            )
        if {"process heating / thermal systems", "steam / boiler systems", "furnaces / kilns / ovens", "boilers / burners"} & subsystem_names:
            rows.append(
                {
                    "regulatory_signal": "Thermal-process and combustion systems are likely decision-relevant under permit logic",
                    "physical_implication": "Combustion quality, emissions controls or thermal-duty boundaries can dominate feasible redesign and cost logic.",
                    "evidence_state": "CONDITIONAL_HYPOTHESIS",
                    "what_it_supports": ["request for fuel bills", "combustion tests", "thermal-duty evidence"],
                    "what_it_does_not_support": ["assumption that thermal losses are observed locally"],
                }
            )

    if asset_family in {"cold_chain", "logistics_warehouse"}:
        rows.append(
            {
                "regulatory_signal": "Storage, safety and refrigeration context may define operational boundaries",
                "physical_implication": "Food safety, refrigeration or storage rules can shape temperature duty, traffic behavior and service-level cost logic.",
                "evidence_state": "CONDITIONAL_HYPOTHESIS",
                "what_it_supports": ["request for temperature-duty and door-traffic evidence"],
                "what_it_does_not_support": ["claim that compliance is the dominant cost without local evidence"],
            }
        )

    return rows


def build_permit_signal_register(
    *,
    target_definition: dict[str, Any],
    asset_family_research_profile: dict[str, Any],
    source_register: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    if text(asset_family_research_profile.get("route_state")) != "operational_asset_candidate":
        return []

    jurisdictions = _jurisdictions(target_definition)
    source_families = _source_family_set(source_register)
    asset_family = text(asset_family_research_profile.get("asset_family"))
    rows: list[dict[str, Any]] = []

    if asset_family == "commercial_building" and any(code.startswith("US-NY-NYC") for code in jurisdictions):
        rows.append(
            {
                "permit_or_rule_signal": "LL84 / LL97 / local building-performance context",
                "signal_state": "OBSERVED_FACT" if "benchmarking_disclosure_record" in source_families else "CONDITIONAL_HYPOTHESIS",
                "implied_physical_domain": "whole-building energy and covered-load logic",
                "non_substitutable_for": ["utility bills", "tenant metering map", "full control-boundary proof"],
            }
        )

    if asset_family == "infrastructure_node":
        rows.append(
            {
                "permit_or_rule_signal": "service continuity or infrastructure operating rule context",
                "signal_state": "CONDITIONAL_HYPOTHESIS",
                "implied_physical_domain": "dispatch, switching, redundancy or continuity-relevant systems",
                "non_substitutable_for": ["service continuity logs", "equipment condition evidence", "tariff and demand profile"],
            }
        )

    if asset_family in {"industrial_manufacturing", "thermal_process_site", "utility_heavy_site"} and (
        "permit_record" in source_families or "regulatory_coverage_record" in source_families
    ):
        rows.append(
            {
                "permit_or_rule_signal": "industrial permit or emissions coverage",
                "signal_state": "OBSERVED_FACT" if "permit_record" in source_families else "CONDITIONAL_HYPOTHESIS",
                "implied_physical_domain": "thermal process, combustion, emissions or wastewater-relevant systems",
                "non_substitutable_for": ["full process map", "equipment condition evidence", "throughput normalization"],
            }
        )

    return rows


def build_regulatory_constraint_register(
    *,
    asset_family_research_profile: dict[str, Any],
    regulatory_physics_register: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    if text(asset_family_research_profile.get("route_state")) != "operational_asset_candidate":
        return []

    rows: list[dict[str, Any]] = []
    for row in regulatory_physics_register:
        rows.append(
            {
                "constraint_name": text(row.get("regulatory_signal")),
                "constraint_logic": text(row.get("physical_implication")),
                "evidence_state": text(row.get("evidence_state")),
                "decision_effect": "Constrains redesign framing and admissible claims until the relevant physical boundary is locally evidenced.",
            }
        )
    return rows
