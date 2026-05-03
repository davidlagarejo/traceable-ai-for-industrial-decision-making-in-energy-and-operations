from __future__ import annotations

from typing import Any

from .schemas import dedupe, text


def _route_state(asset_family_research_profile: dict[str, Any]) -> str:
    return text(asset_family_research_profile.get("route_state"))


def _pack_state(operational_intake_pack: dict[str, Any], pack_name: str) -> str:
    return text((operational_intake_pack.get(pack_name, {}) or {}).get("current_state"))


def build_maintenance_reality_register(
    *,
    asset_family_research_profile: dict[str, Any],
    operational_intake_pack: dict[str, Any],
    maintenance_dependency_map: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    asset_family = text(asset_family_research_profile.get("asset_family"))
    if _route_state(asset_family_research_profile) != "operational_asset_candidate":
        return []

    maintenance_state = _pack_state(operational_intake_pack, "maintenance_maturity_pack")
    summary_claim = (
        "maintenance maturity partially evidenced"
        if maintenance_state == "partially_evidenced"
        else "maintenance maturity not evidenced"
    )
    rows = [
        {
            "reality_claim": summary_claim,
            "maintenance_state": maintenance_state or "not_yet_evidenced",
            "evidence_state": "CONDITIONAL_HYPOTHESIS" if maintenance_state == "partially_evidenced" else "ARCHETYPAL_PRIOR",
            "why_it_matters": "Maintenance evidence affects whether visible cost or energy symptoms should be interpreted as operational drift, reliability risk or structural process duty.",
            "allowed_use": "Use as a bounded maturity statement, not as proof of poor maintenance.",
            "prohibited_use": "Do not state that maintenance is weak as observed fact without local proof.",
        }
    ]

    if asset_family in {"industrial_manufacturing", "thermal_process_site", "utility_heavy_site", "infrastructure_node"}:
        rows.append(
            {
                "reality_claim": "reactive-maintenance risk plausible",
                "maintenance_state": maintenance_state or "not_yet_evidenced",
                "evidence_state": "CONDITIONAL_HYPOTHESIS",
                "why_it_matters": "Support-system instability can move downtime, scrap and throughput economics before any direct energy savings story closes.",
                "allowed_use": "Use to justify requesting maintenance proof and downtime evidence.",
                "prohibited_use": "Do not claim reactive maintenance is observed without logs or recurring failure evidence.",
            }
        )
        rows.append(
            {
                "reality_claim": "downtime economics may dominate visible energy symptoms",
                "maintenance_state": maintenance_state or "not_yet_evidenced",
                "evidence_state": "CONDITIONAL_HYPOTHESIS",
                "why_it_matters": "A site can look like an energy case while the real bottleneck is uptime, scrap or failure cost.",
                "allowed_use": "Use to reframe the next evidence request around uptime and critical-system reliability.",
                "prohibited_use": "Do not collapse uptime economics into a generic energy opportunity.",
            }
        )
    elif maintenance_dependency_map:
        rows.append(
            {
                "reality_claim": "maintenance proof remains a decision-relevant gap",
                "maintenance_state": maintenance_state or "not_yet_evidenced",
                "evidence_state": "CONDITIONAL_HYPOTHESIS",
                "why_it_matters": "Condition, scheduling and controls maintenance can change whether the visible issue is technical waste or governance drift.",
                "allowed_use": "Use to request PM, inspection or service-history evidence.",
                "prohibited_use": "Do not assert degraded maintenance without local records.",
            }
        )
    return rows


def build_maintenance_proof_gap_register(
    *,
    asset_family_research_profile: dict[str, Any],
    maintenance_dependency_map: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    if _route_state(asset_family_research_profile) != "operational_asset_candidate":
        return []

    gaps = dedupe(
        item
        for row in maintenance_dependency_map
        for item in list(row.get("maintenance_proof_needed", []) or [])
    )
    return [
        {
            "proof_gap": gap,
            "why_needed": "Needed to determine whether maintenance maturity changes the dominant cost or loss logic.",
            "affected_subsystems": [
                text(row.get("subsystem_name"))
                for row in maintenance_dependency_map
                if gap in list(row.get("maintenance_proof_needed", []) or [])
            ],
        }
        for gap in gaps
    ]


def build_downtime_dependency_register(
    *,
    asset_family_research_profile: dict[str, Any],
    maintenance_dependency_map: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    asset_family = text(asset_family_research_profile.get("asset_family"))
    if _route_state(asset_family_research_profile) != "operational_asset_candidate":
        return []

    if asset_family in {"industrial_manufacturing", "thermal_process_site", "utility_heavy_site", "infrastructure_node"}:
        economic_logic = "Throughput, yield, uptime and scrap may move margin more than direct utility savings."
    elif asset_family in {"logistics_warehouse", "cold_chain"}:
        economic_logic = "Service-level continuity, dispatch integrity and temperature performance may move cost more than isolated equipment efficiency."
    else:
        economic_logic = "Comfort, compliance and building-service continuity can alter economics even when direct downtime is less visible."

    return [
        {
            "subsystem_name": text(row.get("subsystem_name")),
            "downtime_dependency": "Failure or degraded maintenance in this subsystem may alter the case economics materially.",
            "economic_logic": economic_logic,
            "evidence_state": text(row.get("evidence_state")) or "CONDITIONAL_HYPOTHESIS",
        }
        for row in maintenance_dependency_map[:6]
    ]
