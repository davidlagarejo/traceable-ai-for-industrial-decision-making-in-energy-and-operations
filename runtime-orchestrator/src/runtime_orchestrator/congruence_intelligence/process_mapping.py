from __future__ import annotations

from typing import Any

from .schemas import text


def _flow_row(
    stage: str,
    description: str,
    *,
    evidence_state: str,
    local_binding_state: str,
) -> dict[str, Any]:
    return {
        "stage": text(stage),
        "description": text(description),
        "evidence_state": text(evidence_state),
        "local_binding_state": text(local_binding_state),
    }


def build_process_map(
    *,
    asset_family_research_profile: dict[str, Any],
    local_evidence_binding_register: list[dict[str, Any]],
) -> dict[str, Any]:
    asset_family = text(asset_family_research_profile.get("asset_family"))
    route_state = text(asset_family_research_profile.get("route_state"))
    binding_state = text((local_evidence_binding_register or [{}])[0].get("current_local_binding_state"))
    if route_state != "operational_asset_candidate":
        return {
            "asset_family": asset_family,
            "process_map_state": "inadmissible_until_asset_identity_bounded",
            "inputs": [],
            "transformations": [],
            "support_systems": [],
            "loss_points": [],
            "outputs": [],
            "market_value_link": [],
            "human_control_points": [],
            "automatic_control_points": [],
            "regulatory_friction_points": [],
        }

    if binding_state in {"partially_bound", "sufficiently_bound"}:
        evidence_state = "CONDITIONAL_HYPOTHESIS"
    else:
        evidence_state = "ARCHETYPAL_PRIOR"

    if asset_family == "commercial_building":
        return {
            "asset_family": asset_family,
            "process_map_state": "research_seeded_operational_logic",
            "inputs": [
                _flow_row("occupants_and_tenants", "Occupancy and tenant demand create the service load that the building must support.", evidence_state=evidence_state, local_binding_state=binding_state),
            ],
            "transformations": [
                _flow_row("building_services_delivery", "The asset converts purchased utilities and controls into comfort, usable space, compliance and asset quality.", evidence_state=evidence_state, local_binding_state=binding_state),
            ],
            "support_systems": [
                _flow_row("central_plant_hvac", "HVAC / central plant conditions the space and often dominates owner-managed base-building systems.", evidence_state=evidence_state, local_binding_state=binding_state),
                _flow_row("lighting_vertical_transport_water", "Lighting, elevators and water systems support service delivery and tenant experience.", evidence_state=evidence_state, local_binding_state=binding_state),
            ],
            "loss_points": [
                _flow_row("control_boundary_mismatch", "Owner burden can diverge from the loads and behaviors that actually drive economics.", evidence_state="CONDITIONAL_HYPOTHESIS", local_binding_state=binding_state),
                _flow_row("schedule_and_after_hours_waste", "After-hours occupancy and control discipline can create avoidable load if the boundary is owner-capturable.", evidence_state="CONDITIONAL_HYPOTHESIS", local_binding_state=binding_state),
            ],
            "outputs": [
                _flow_row("premium_space_and_compliance", "The output is rentable compliant space and preserved building value.", evidence_state=evidence_state, local_binding_state=binding_state),
            ],
            "market_value_link": [
                _flow_row("noi_and_penalty_exposure", "Value is linked to occupancy quality, compliance posture, cost control and the owner's ability to capture system economics.", evidence_state="CONDITIONAL_HYPOTHESIS", local_binding_state=binding_state),
            ],
            "human_control_points": [
                _flow_row("schedule_and_operations", "Operations teams, property management and tenant policies shape schedule discipline and boundary conditions.", evidence_state="CONDITIONAL_HYPOTHESIS", local_binding_state=binding_state),
            ],
            "automatic_control_points": [
                _flow_row("bms_and_central_plant_logic", "BMS and plant sequencing control how the asset converts conditions into load and cost.", evidence_state="CONDITIONAL_HYPOTHESIS", local_binding_state=binding_state),
            ],
            "regulatory_friction_points": [
                _flow_row("benchmarking_and_performance_rules", "Benchmarking and performance standards create owner-facing compliance burdens that may not align with owner-controllable load.", evidence_state="OBSERVED_FACT", local_binding_state="public_context_seeded"),
            ],
        }
    if asset_family in {"industrial_manufacturing", "thermal_process_site", "utility_heavy_site"}:
        return {
            "asset_family": asset_family,
            "process_map_state": "research_seeded_operational_logic",
            "inputs": [
                _flow_row("raw_materials_and_energy", "Raw materials, utilities and labor enter the asset as process inputs.", evidence_state=evidence_state, local_binding_state=binding_state),
            ],
            "transformations": [
                _flow_row("process_transformation", "The asset transforms inputs into product through thermal, mechanical, electrical or hybrid process duty.", evidence_state=evidence_state, local_binding_state=binding_state),
            ],
            "support_systems": [
                _flow_row("utilities_and_support_systems", "Compressed air, motors, pumps, boilers, chillers and other support systems enable the dominant process.", evidence_state=evidence_state, local_binding_state=binding_state),
            ],
            "loss_points": [
                _flow_row("process_vs_waste_ambiguity", "Visible energy intensity may reflect structural process load rather than avoidable waste.", evidence_state="CONDITIONAL_HYPOTHESIS", local_binding_state=binding_state),
                _flow_row("maintenance_and_downtime_losses", "Maintenance immaturity can convert equipment condition into downtime, scrap or unstable energy behavior.", evidence_state="CONDITIONAL_HYPOTHESIS", local_binding_state=binding_state),
            ],
            "outputs": [
                _flow_row("finished_product", "The output is finished product or process service with throughput, quality and uptime implications.", evidence_state=evidence_state, local_binding_state=binding_state),
            ],
            "market_value_link": [
                _flow_row("throughput_margin_and_reliability", "Value is linked to throughput, yield, uptime, energy cost structure and process reliability.", evidence_state="CONDITIONAL_HYPOTHESIS", local_binding_state=binding_state),
            ],
            "human_control_points": [
                _flow_row("operators_maintenance_schedule", "Operators, schedulers and maintenance teams affect uptime, sequencing and hidden loss persistence.", evidence_state="CONDITIONAL_HYPOTHESIS", local_binding_state=binding_state),
            ],
            "automatic_control_points": [
                _flow_row("drives_controls_combustion_logic", "Drives, compressors, controls and combustion tuning shape process-support behavior.", evidence_state="CONDITIONAL_HYPOTHESIS", local_binding_state=binding_state),
            ],
            "regulatory_friction_points": [
                _flow_row("permit_and_emissions_constraints", "Permits and environmental obligations can signal dominant thermal or chemical system relevance.", evidence_state="OBSERVED_FACT", local_binding_state="public_context_seeded"),
            ],
        }
    if asset_family == "infrastructure_node":
        return {
            "asset_family": asset_family,
            "process_map_state": "research_seeded_operational_logic",
            "inputs": [
                _flow_row("grid_or_network_feed", "Power, network flow or utility-service burden enters the node as a continuity-sensitive input.", evidence_state=evidence_state, local_binding_state=binding_state),
            ],
            "transformations": [
                _flow_row("conversion_and_dispatch", "The node converts, conditions, routes or dispatches service under continuity and redundancy obligations.", evidence_state=evidence_state, local_binding_state=binding_state),
            ],
            "support_systems": [
                _flow_row("controls_redundancy_and_major_equipment", "Controls, backup logic, transformers, breakers, pumps or compressors support service continuity more than pure energy minimization.", evidence_state=evidence_state, local_binding_state=binding_state),
            ],
            "loss_points": [
                _flow_row("continuity_burden_vs_waste_ambiguity", "Visible energy or demand burden may reflect continuity duty, redundancy class or dispatch obligation rather than simple avoidable waste.", evidence_state="CONDITIONAL_HYPOTHESIS", local_binding_state=binding_state),
                _flow_row("sequencing_and_peak_logic", "Peak behavior, switching logic or redundancy posture may dominate tariff or uptime economics.", evidence_state="CONDITIONAL_HYPOTHESIS", local_binding_state=binding_state),
            ],
            "outputs": [
                _flow_row("service_continuity_and_dispatch", "The output is reliable service continuity, dispatch capability and constrained network performance.", evidence_state=evidence_state, local_binding_state=binding_state),
            ],
            "market_value_link": [
                _flow_row("uptime_tariff_and_constraint_logic", "Value depends on uptime, service continuity, dispatch burden, demand structure and avoidance of reliability events.", evidence_state="CONDITIONAL_HYPOTHESIS", local_binding_state=binding_state),
            ],
            "human_control_points": [
                _flow_row("dispatch_and_switching_practice", "Operator dispatch, switching and maintenance practice can materially alter demand, continuity and event risk.", evidence_state="CONDITIONAL_HYPOTHESIS", local_binding_state=binding_state),
            ],
            "automatic_control_points": [
                _flow_row("protection_controls_and_redundancy_logic", "Protection schemes, controls and backup logic shape whether the node behaves like continuity infrastructure or simple load.", evidence_state="CONDITIONAL_HYPOTHESIS", local_binding_state=binding_state),
            ],
            "regulatory_friction_points": [
                _flow_row("service_and_safety_constraints", "Service obligations, safety rules or network constraints can limit what counts as admissible optimization.", evidence_state="CONDITIONAL_HYPOTHESIS", local_binding_state=binding_state),
            ],
        }
    if asset_family in {"logistics_warehouse", "cold_chain"}:
        return {
            "asset_family": asset_family,
            "process_map_state": "research_seeded_operational_logic",
            "inputs": [
                _flow_row("goods_receipt", "Goods arrive for storage, staging or onward movement.", evidence_state=evidence_state, local_binding_state=binding_state),
            ],
            "transformations": [
                _flow_row("storage_and_handling", "The asset transforms inbound goods into outbound service through storage, movement, handling and dispatch discipline.", evidence_state=evidence_state, local_binding_state=binding_state),
            ],
            "support_systems": [
                _flow_row("lighting_hvac_docks_motive_power", "Lighting, ventilation, charging, dock systems and any conditioned storage support service-level delivery.", evidence_state=evidence_state, local_binding_state=binding_state),
            ],
            "loss_points": [
                _flow_row("layout_and_schedule_friction", "Movement inefficiency, charging peaks, idle conditioning and dock-door losses may dominate.", evidence_state="CONDITIONAL_HYPOTHESIS", local_binding_state=binding_state),
            ],
            "outputs": [
                _flow_row("service_level_and_dispatch", "The output is service-level performance, storage integrity and reliable dispatch.", evidence_state=evidence_state, local_binding_state=binding_state),
            ],
            "market_value_link": [
                _flow_row("service_level_cost_tradeoff", "Value depends on service level, throughput, storage conditions, movement efficiency and demand structure.", evidence_state="CONDITIONAL_HYPOTHESIS", local_binding_state=binding_state),
            ],
            "human_control_points": [
                _flow_row("dock_and_handling_practice", "Scheduling, picking, charging and loading practices materially affect realized demand and losses.", evidence_state="CONDITIONAL_HYPOTHESIS", local_binding_state=binding_state),
            ],
            "automatic_control_points": [
                _flow_row("temperature_and_facility_controls", "Temperature or ventilation controls shape conditioned-load behavior where relevant.", evidence_state="CONDITIONAL_HYPOTHESIS", local_binding_state=binding_state),
            ],
            "regulatory_friction_points": [
                _flow_row("storage_and_safety_requirements", "Storage, safety and refrigeration requirements can shape operational boundaries and cost logic.", evidence_state="CONDITIONAL_HYPOTHESIS", local_binding_state=binding_state),
            ],
        }
    return {
        "asset_family": asset_family,
        "process_map_state": "generic_operational_logic_only",
        "inputs": [],
        "transformations": [],
        "support_systems": [],
        "loss_points": [],
        "outputs": [],
        "market_value_link": [],
        "human_control_points": [],
        "automatic_control_points": [],
        "regulatory_friction_points": [],
    }
