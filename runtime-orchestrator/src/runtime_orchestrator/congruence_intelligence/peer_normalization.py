from __future__ import annotations

from typing import Any

from .schemas import dedupe, text


def _binding_state(local_evidence_binding_register: list[dict[str, Any]]) -> str:
    return text((local_evidence_binding_register or [{}])[0].get("current_local_binding_state"))


def _allows_conditional_archetypal_screening(route_state: str, asset_family: str) -> bool:
    return (
        route_state == "target_not_yet_operationally_bounded"
        and bool(asset_family)
        and asset_family != "generic_operational_asset"
    )


def build_fair_comparison_profile(
    *,
    asset_family_research_profile: dict[str, Any],
    operational_intake_pack: dict[str, Any],
    process_map: dict[str, Any],
    control_boundary_map: list[dict[str, Any]],
    local_evidence_binding_register: list[dict[str, Any]],
) -> dict[str, Any]:
    asset_family = text(asset_family_research_profile.get("asset_family"))
    route_state = text(asset_family_research_profile.get("route_state"))
    binding_state = _binding_state(local_evidence_binding_register)
    schedule_state = text((operational_intake_pack.get("schedule_and_utilization_pack", {}) or {}).get("current_state"))
    control_boundary_state = text((operational_intake_pack.get("control_boundary_pack", {}) or {}).get("current_state"))
    maintenance_state = text((operational_intake_pack.get("maintenance_maturity_pack", {}) or {}).get("current_state"))
    climate_state = text((operational_intake_pack.get("climate_location_pack", {}) or {}).get("current_state"))
    process_state = text(process_map.get("process_map_state"))

    throughput_required = asset_family in {
        "industrial_manufacturing",
        "logistics_warehouse",
        "cold_chain",
        "thermal_process_site",
        "utility_heavy_site",
        "infrastructure_node",
    }
    throughput_proxy = (
        "throughput_or_product_mix_proxy"
        if asset_family in {"industrial_manufacturing", "thermal_process_site", "utility_heavy_site"}
        else "service_continuity_or_dispatch_burden_proxy"
        if asset_family == "infrastructure_node"
        else "service_level_or_movement_intensity_proxy"
        if asset_family in {"logistics_warehouse", "cold_chain"}
        else "occupancy_and_control_boundary_proxy"
    )
    comparison_state = (
        "inadmissible_until_asset_identity_bounded"
        if (
            route_state == "target_unresolved"
            or (
                route_state != "operational_asset_candidate"
                and not _allows_conditional_archetypal_screening(route_state, asset_family)
            )
        )
        else "archetypal_screening_only"
        if _allows_conditional_archetypal_screening(route_state, asset_family)
        else "bounded_screening_only"
        if binding_state not in {"partially_bound", "sufficiently_bound"}
        else "partially_normalized"
    )

    return {
        "asset_family": asset_family,
        "comparison_state": comparison_state,
        "process_type": text(process_map.get("asset_family")) or asset_family,
        "process_map_state": process_state,
        "climate_context_state": climate_state or "public_context_seeded",
        "operating_schedule_state": schedule_state or "not_yet_evidenced",
        "throughput_proxy_required": throughput_required,
        "throughput_proxy": throughput_proxy,
        "throughput_proxy_state": "not_yet_evidenced" if throughput_required else "not_primary",
        "control_boundary_state": control_boundary_state or "not_yet_evidenced",
        "control_boundary_count": len(control_boundary_map or []),
        "maintenance_maturity_state": maintenance_state or "not_yet_evidenced",
        "regulatory_context": list(asset_family_research_profile.get("typical_regulatory_signals", []) or []),
        "technology_stack_hint": dedupe(
            [text(row.get("subsystem_name")) for row in (control_boundary_map or [])]
            + list(asset_family_research_profile.get("typical_subsystems", []) or [])[:4]
        )[:6],
        "valid_peer_basis": [
            "same asset family",
            "matching dominant process or service logic",
            "matching climate and schedule context",
        ]
        + (["matching control boundary"] if asset_family == "commercial_building" else [])
        + (["matching throughput or service-level normalization"] if throughput_required else []),
        "prohibited_peer_shortcuts": list(asset_family_research_profile.get("typical_invalid_comparisons", []) or []),
    }


def build_normalization_requirements_register(
    *,
    fair_comparison_profile: dict[str, Any],
) -> list[dict[str, Any]]:
    asset_family = text(fair_comparison_profile.get("asset_family"))
    throughput_required = bool(fair_comparison_profile.get("throughput_proxy_required"))
    rows = [
        {
            "normalization_dimension": "asset_family_and_process_type",
            "current_state": text(fair_comparison_profile.get("process_map_state")),
            "required_for": "all_peer_logic",
            "why": "Comparisons are invalid if the compared systems do not transform value in a structurally similar way.",
        },
        {
            "normalization_dimension": "climate_and_operating_schedule",
            "current_state": text(fair_comparison_profile.get("climate_context_state")) or "public_context_seeded",
            "required_for": "benchmark_and_peer_framing",
            "why": "Schedule and climate can dominate load shape even when the asset family matches.",
        },
    ]
    if asset_family == "commercial_building":
        rows.append(
            {
                "normalization_dimension": "owner_tenant_control_boundary",
                "current_state": text(fair_comparison_profile.get("control_boundary_state")),
                "required_for": "owner_capturable_building_comparisons",
                "why": "A whole-building comparison is structurally invalid if owner burden and controllable load do not align.",
            }
        )
    if throughput_required:
        rows.append(
            {
                "normalization_dimension": text(fair_comparison_profile.get("throughput_proxy")),
                "current_state": text(fair_comparison_profile.get("throughput_proxy_state")),
                "required_for": "manufacturing_or_logistics_peer_logic",
                "why": "Area or gross consumption comparisons are weak if throughput, service level, or process duty are not normalized.",
            }
        )
    return rows
