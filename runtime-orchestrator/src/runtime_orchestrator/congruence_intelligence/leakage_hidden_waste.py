from __future__ import annotations

from typing import Any

from .schemas import text


def _route_state(asset_family_research_profile: dict[str, Any]) -> str:
    return text(asset_family_research_profile.get("route_state"))


def _subsystem_names(subsystem_register: list[dict[str, Any]]) -> set[str]:
    return {
        text(row.get("subsystem_name"))
        for row in subsystem_register
        if text(row.get("subsystem_name"))
    }


def build_leakage_hypothesis_register(
    *,
    asset_family_research_profile: dict[str, Any],
    subsystem_register: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    asset_family = text(asset_family_research_profile.get("asset_family"))
    if _route_state(asset_family_research_profile) != "operational_asset_candidate":
        return []

    subsystems = _subsystem_names(subsystem_register)
    rows: list[dict[str, Any]] = []

    if asset_family in {"industrial_manufacturing", "utility_heavy_site"} and (
        "compressed air" in subsystems or "compressors" in subsystems
    ):
        rows.append(
            {
                "hypothesis_name": "compressed_air_hidden_leakage_plausible",
                "evidence_state": "CONDITIONAL_HYPOTHESIS",
                "why_plausible": "Compressed-air systems recurrently hide economically meaningful losses in leaks, pressure drift and idle operation.",
                "minimum_evidence": [
                    "leak survey or operator walkdown",
                    "compressor sequencing logic",
                    "pressure setpoints",
                    "utility bill or demand profile",
                ],
                "materiality_gate": "Only material if compressed air is a meaningful support utility in the operating boundary.",
                "allowed_language": "Leakage is a plausible recurring hypothesis for this system family.",
                "prohibited_language": "Do not diagnose actual compressed-air leaks at this site without local proof.",
            }
        )

    if {"steam / boiler systems", "boilers / burners"} & subsystems:
        rows.append(
            {
                "hypothesis_name": "steam_condensate_or_combustion_hidden_waste_plausible",
                "evidence_state": "CONDITIONAL_HYPOTHESIS",
                "why_plausible": "Steam, condensate and combustion systems recurrently lose value through trap failure, unrecovered condensate or poor combustion tuning.",
                "minimum_evidence": [
                    "steam trap or condensate evidence",
                    "combustion test records",
                    "fuel bills",
                ],
                "materiality_gate": "Only material if thermal duty and boiler service meaningfully affect the site's economics.",
                "allowed_language": "Thermal hidden waste is a plausible recurring hypothesis for boiler-heavy systems.",
                "prohibited_language": "Do not state that steam losses are observed without local evidence.",
            }
        )

    if asset_family == "cold_chain" and "refrigeration plant" in subsystems:
        rows.append(
            {
                "hypothesis_name": "refrigeration_infiltration_or_refrigerant_hidden_waste_plausible",
                "evidence_state": "CONDITIONAL_HYPOTHESIS",
                "why_plausible": "Cold-chain systems recurrently lose value through infiltration, defrost mismatch or refrigerant-related performance loss.",
                "minimum_evidence": [
                    "door traffic profile",
                    "defrost schedule",
                    "temperature bands",
                    "refrigeration service records",
                ],
                "materiality_gate": "Only material if temperature-controlled duty is central to the asset's service logic.",
                "allowed_language": "Cold-chain hidden waste is a plausible recurring hypothesis.",
                "prohibited_language": "Do not state that the site has refrigerant loss or infiltration waste as observed fact without local proof.",
            }
        )

    return rows
