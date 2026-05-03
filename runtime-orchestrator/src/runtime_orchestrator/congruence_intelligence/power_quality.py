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


def _pack_state(operational_intake_pack: dict[str, Any], pack_name: str) -> str:
    return text((operational_intake_pack.get(pack_name, {}) or {}).get("current_state"))


def build_power_quality_hypothesis_register(
    *,
    asset_family_research_profile: dict[str, Any],
    operational_intake_pack: dict[str, Any],
    subsystem_register: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    asset_family = text(asset_family_research_profile.get("asset_family"))
    if _route_state(asset_family_research_profile) != "operational_asset_candidate":
        return []

    if asset_family not in {
        "industrial_manufacturing",
        "thermal_process_site",
        "utility_heavy_site",
        "infrastructure_node",
    }:
        return []

    subsystems = _subsystem_names(subsystem_register)
    if not ({"motors / drives / fans / pumps", "large motors and drives", "compressors"} & subsystems):
        return []

    utility_state = _pack_state(operational_intake_pack, "utility_and_tariff_pack")
    evidence_state = (
        "CONDITIONAL_HYPOTHESIS"
        if utility_state in {"public_context_only", "partially_evidenced"}
        else "ARCHETYPAL_PRIOR"
    )
    return [
        {
            "hypothesis_name": "power_quality_and_reactive_exposure_plausible",
            "evidence_state": evidence_state,
            "why_plausible": "Inductive and support-system-heavy sites can hide demand, PF or reactive-cost exposure that is invisible in aggregate kWh alone.",
            "minimum_evidence": [
                "utility bill with demand or PF charges",
                "tariff structure",
                "major motor or compressor inventory",
                "interval demand evidence if bills are insufficient",
            ],
            "if_confirmed": "Prioritize tariff-aware control, sequencing or correction logic before generic consumption-reduction CAPEX.",
            "if_falsified": "De-prioritize PF or reactive logic and re-rank support-system hypotheses.",
            "measurement_priority": "bills_first_then_targeted_analyzer_if_material",
            "allowed_language": "Strategic hypothesis justified by system family and potential tariff exposure.",
            "prohibited_language": "Do not state that PF, harmonics or reactive losses are present without tariff or analyzer evidence.",
        }
    ]
