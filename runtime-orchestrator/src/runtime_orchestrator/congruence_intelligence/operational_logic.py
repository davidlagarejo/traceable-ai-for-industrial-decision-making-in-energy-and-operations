from __future__ import annotations

from typing import Any

from .process_mapping import build_process_map
from .schemas import text


def _binding_state(local_evidence_binding_register: list[dict[str, Any]]) -> str:
    return text((local_evidence_binding_register or [{}])[0].get("current_local_binding_state"))


def _base_evidence_state(route_state: str, binding_state: str) -> str:
    if route_state != "operational_asset_candidate":
        return "INADMISSIBLE_CLAIM"
    if binding_state in {"partially_bound", "sufficiently_bound"}:
        return "CONDITIONAL_HYPOTHESIS"
    return "ARCHETYPAL_PRIOR"


def build_subsystem_register(
    *,
    asset_family_research_profile: dict[str, Any],
    local_evidence_binding_register: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    asset_family = text(asset_family_research_profile.get("asset_family"))
    route_state = text(asset_family_research_profile.get("route_state"))
    binding_state = _binding_state(local_evidence_binding_register)
    evidence_state = _base_evidence_state(route_state, binding_state)
    if evidence_state == "INADMISSIBLE_CLAIM":
        return []

    subsystem_roles = {
        "commercial_building": {
            "HVAC / central plant": ("service conditioning", ["electricity", "thermal"], "mixed automatic / operator"),
            "lighting": ("service support", ["electricity"], "scheduled automatic / operator"),
            "vertical transportation": ("service support", ["electricity"], "automatic"),
            "plug and tenant loads": ("tenant-side service demand", ["electricity"], "tenant / occupant"),
            "BMS / controls": ("control orchestration", ["control signals"], "automatic / operator"),
            "water and domestic systems": ("service support", ["electricity", "water"], "mixed"),
            "building envelope": ("load boundary", ["passive thermal"], "passive"),
        },
        "industrial_manufacturing": {
            "process heating / thermal systems": ("dominant process duty", ["fuel", "thermal", "electricity"], "automatic / operator"),
            "motors / drives / fans / pumps": ("mechanical support and movement", ["electricity"], "automatic / operator"),
            "compressed air": ("utility support", ["electricity"], "automatic / operator"),
            "chilled water / cooling": ("process or support cooling", ["electricity", "thermal"], "automatic"),
            "steam / boiler systems": ("thermal utility support", ["fuel", "water"], "automatic / operator"),
            "waste handling": ("byproduct handling", ["electricity", "logistics"], "operator"),
            "material handling / logistics": ("flow support", ["electricity", "fuel"], "operator"),
        },
        "logistics_warehouse": {
            "lighting": ("visibility and shift support", ["electricity"], "scheduled automatic / operator"),
            "HVAC / ventilation": ("facility conditioning", ["electricity", "thermal"], "automatic / operator"),
            "dock and door systems": ("flow boundary and ingress control", ["electricity"], "operator"),
            "forklift charging / motive power": ("movement support", ["electricity"], "operator"),
            "sorting and handling systems": ("goods movement", ["electricity"], "operator / automatic"),
            "cold-room or conditioned storage if present": ("conditioned storage", ["electricity", "thermal"], "automatic / operator"),
        },
        "cold_chain": {
            "refrigeration plant": ("temperature control", ["electricity", "refrigerant"], "automatic / operator"),
            "defrost systems": ("refrigeration support", ["electricity", "thermal"], "automatic"),
            "door and dock systems": ("infiltration boundary", ["electricity"], "operator"),
            "lighting": ("visibility and support", ["electricity"], "scheduled automatic / operator"),
            "forklift charging": ("movement support", ["electricity"], "operator"),
        },
        "thermal_process_site": {
            "furnaces / kilns / ovens": ("thermal transformation", ["fuel", "thermal"], "automatic / operator"),
            "boilers / burners": ("thermal support", ["fuel", "water"], "automatic / operator"),
            "air and combustion systems": ("combustion support", ["electricity", "air"], "automatic"),
            "heat recovery": ("efficiency support", ["thermal"], "automatic / operator"),
        },
        "utility_heavy_site": {
            "large motors and drives": ("utility-heavy motion", ["electricity"], "automatic / operator"),
            "compressors": ("support utility generation", ["electricity"], "automatic / operator"),
            "pumps and fans": ("fluid and air movement", ["electricity"], "automatic / operator"),
            "distribution equipment": ("utility distribution", ["electricity"], "automatic"),
        },
        "infrastructure_node": {
            "power conversion or motive-power systems": ("service conversion or flow handling", ["electricity"], "automatic / operator"),
            "controls and dispatch logic": ("dispatch and continuity orchestration", ["control signals"], "automatic / operator"),
            "redundancy / backup systems": ("continuity support", ["electricity", "backup fuel"], "automatic / operator"),
            "network or node-level support systems": ("node support and constrained delivery", ["electricity"], "mixed"),
        },
    }
    rows: list[dict[str, Any]] = []
    for subsystem in list(asset_family_research_profile.get("typical_subsystems", []) or []):
        role, energy_forms, control_mode = subsystem_roles.get(asset_family, {}).get(
            subsystem,
            ("asset-family support role", ["mixed"], "mixed"),
        )
        rows.append(
            {
                "subsystem_name": subsystem,
                "subsystem_role": role,
                "primary_equipment_classes": [subsystem],
                "dominant_energy_forms": energy_forms,
                "control_mode": control_mode,
                "maintenance_dependency": "Maintenance maturity can materially alter realized performance or downtime behavior.",
                "evidence_state": evidence_state,
                "why_it_may_matter": f"This subsystem is a recurrent structural domain for `{asset_family}` and may dominate the realized operating boundary or loss logic.",
            }
        )
    return rows


def build_equipment_dominance_register(
    *,
    subsystem_register: list[dict[str, Any]],
    route_state: str,
    binding_state: str,
) -> list[dict[str, Any]]:
    evidence_state = _base_evidence_state(route_state, binding_state)
    if evidence_state == "INADMISSIBLE_CLAIM":
        return []
    rows: list[dict[str, Any]] = []
    for subsystem in subsystem_register[:5]:
        name = text(subsystem.get("subsystem_name"))
        rows.append(
            {
                "equipment_class": name,
                "dominance_hypothesis": f"`{name}` may be operationally dominant or decision-relevant if it shapes the main service, process or cost boundary.",
                "evidence_state": evidence_state if name not in {"BMS / controls", "plug and tenant loads"} else "CONDITIONAL_HYPOTHESIS",
                "why_it_could_dominate": text(subsystem.get("why_it_may_matter")),
            }
        )
    return rows


def build_maintenance_dependency_map(
    *,
    subsystem_register: list[dict[str, Any]],
    route_state: str,
    binding_state: str,
) -> list[dict[str, Any]]:
    evidence_state = _base_evidence_state(route_state, binding_state)
    if evidence_state == "INADMISSIBLE_CLAIM":
        return []
    return [
        {
            "subsystem_name": text(subsystem.get("subsystem_name")),
            "maintenance_dependency": text(subsystem.get("maintenance_dependency")),
            "evidence_state": evidence_state if text(subsystem.get("subsystem_name")) not in {"compressed air", "steam / boiler systems", "refrigeration plant"} else "CONDITIONAL_HYPOTHESIS",
            "maintenance_proof_needed": [
                "preventive maintenance program evidence",
                "inspection or test logs",
                "downtime or recurring failure proof",
            ],
        }
        for subsystem in subsystem_register[:6]
    ]


def build_control_boundary_map(
    *,
    asset_family_research_profile: dict[str, Any],
    route_state: str,
    binding_state: str,
) -> list[dict[str, Any]]:
    if route_state != "operational_asset_candidate":
        return []
    asset_family = text(asset_family_research_profile.get("asset_family"))
    if asset_family == "commercial_building":
        return [
            {
                "boundary_name": "owner_vs_tenant_load_boundary",
                "boundary_logic": "The owner may face regulatory or utility burden while tenant-side loads or schedules drive realized economics.",
                "evidence_state": "CONDITIONAL_HYPOTHESIS",
                "binding_state": binding_state,
            },
            {
                "boundary_name": "base_building_vs_occupant_behavior",
                "boundary_logic": "Base-building systems may be owner-managed while after-hours usage and tenant behavior shape realized load.",
                "evidence_state": "CONDITIONAL_HYPOTHESIS",
                "binding_state": binding_state,
            },
        ]
    if asset_family in {"industrial_manufacturing", "thermal_process_site", "utility_heavy_site"}:
        return [
            {
                "boundary_name": "process_load_vs_support_system_load",
                "boundary_logic": "The decision boundary may depend on whether process duty or support systems dominate the observed cost and energy pattern.",
                "evidence_state": "CONDITIONAL_HYPOTHESIS",
                "binding_state": binding_state,
            },
            {
                "boundary_name": "operations_vs_maintenance_control",
                "boundary_logic": "Operational discipline and maintenance maturity can jointly determine whether visible consumption is structural or avoidable.",
                "evidence_state": "CONDITIONAL_HYPOTHESIS",
                "binding_state": binding_state,
            },
        ]
    if asset_family == "infrastructure_node":
        return [
            {
                "boundary_name": "continuity_duty_vs_avoidable_loss_boundary",
                "boundary_logic": "The decision boundary depends on whether visible demand or energy burden is the price of service continuity and redundancy, or truly avoidable operating waste.",
                "evidence_state": "CONDITIONAL_HYPOTHESIS",
                "binding_state": binding_state,
            },
            {
                "boundary_name": "dispatch_obligation_vs_tariff_optimization_boundary",
                "boundary_logic": "Tariff and PF exposure may be real, but optimization is bounded by dispatch logic, switching practice and reliability obligations.",
                "evidence_state": "CONDITIONAL_HYPOTHESIS",
                "binding_state": binding_state,
            },
        ]
    return [
        {
            "boundary_name": "throughput_vs_service_level_boundary",
            "boundary_logic": "The true operating boundary may be defined by service level, storage conditions and movement intensity rather than area alone.",
            "evidence_state": "CONDITIONAL_HYPOTHESIS",
            "binding_state": binding_state,
        }
    ]


def build_operational_value_flow_register(process_map: dict[str, Any]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for stage in list(process_map.get("market_value_link", []) or []):
        rows.append(
            {
                "value_stage": text(stage.get("stage")),
                "value_logic": text(stage.get("description")),
                "evidence_state": text(stage.get("evidence_state")),
            }
        )
    return rows


def build_asset_operational_logic(
    *,
    asset_family_research_profile: dict[str, Any],
    local_evidence_binding_register: list[dict[str, Any]],
) -> dict[str, Any]:
    route_state = text(asset_family_research_profile.get("route_state"))
    binding_state = _binding_state(local_evidence_binding_register)
    process_map = build_process_map(
        asset_family_research_profile=asset_family_research_profile,
        local_evidence_binding_register=local_evidence_binding_register,
    )
    subsystem_register = build_subsystem_register(
        asset_family_research_profile=asset_family_research_profile,
        local_evidence_binding_register=local_evidence_binding_register,
    )
    equipment_dominance_register = build_equipment_dominance_register(
        subsystem_register=subsystem_register,
        route_state=route_state,
        binding_state=binding_state,
    )
    maintenance_dependency_map = build_maintenance_dependency_map(
        subsystem_register=subsystem_register,
        route_state=route_state,
        binding_state=binding_state,
    )
    control_boundary_map = build_control_boundary_map(
        asset_family_research_profile=asset_family_research_profile,
        route_state=route_state,
        binding_state=binding_state,
    )
    return {
        "operational_logic_state": (
            "inadmissible_until_asset_identity_bounded"
            if route_state != "operational_asset_candidate"
            else "research_seeded_operational_logic"
        ),
        "process_map": process_map,
        "subsystem_register": subsystem_register,
        "equipment_dominance_register": equipment_dominance_register,
        "maintenance_dependency_map": maintenance_dependency_map,
        "control_boundary_map": control_boundary_map,
        "operational_value_flow_register": build_operational_value_flow_register(process_map),
    }
