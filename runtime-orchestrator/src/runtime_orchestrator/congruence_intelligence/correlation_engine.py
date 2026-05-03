from __future__ import annotations

from typing import Any

from .schemas import text


def _subsystem_names(subsystem_register: list[dict[str, Any]]) -> set[str]:
    return {
        text(row.get("subsystem_name"))
        for row in subsystem_register
        if text(row.get("subsystem_name"))
    }


def build_structural_correlation_register(
    *,
    asset_family_research_profile: dict[str, Any],
    operational_intake_pack: dict[str, Any],
    subsystem_register: list[dict[str, Any]],
    control_boundary_map: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    asset_family = text(asset_family_research_profile.get("asset_family"))
    route_state = text(asset_family_research_profile.get("route_state"))
    subsystems = _subsystem_names(subsystem_register)
    tariff_public = text((operational_intake_pack.get("utility_and_tariff_pack", {}) or {}).get("current_state")) == "public_context_only"
    rows: list[dict[str, Any]] = []

    if route_state != "operational_asset_candidate":
        return rows

    if asset_family == "commercial_building":
        rows.append(
            {
                "correlation": "Benchmarking / performance burden + unresolved owner-tenant boundary",
                "layers_connected": ["regulation", "control", "finance"],
                "evidence_state": "CONDITIONAL_HYPOTHESIS",
                "why_it_matters": "Regulatory and whole-building performance pressure can exist even when the owner may not control the dominant load economics.",
                "strategic_meaning": "Compliance pressure may be real while owner-capturable retrofit logic is still structurally unbounded.",
                "what_confirms": ["tenant metering map", "lease responsibility matrix", "LL97 filing basis"],
                "what_falsifies": ["observed owner control over the dominant covered loads"],
                "evidence_needed": ["tenant metering map", "lease responsibility matrix", "LL97 filing basis"],
                "possible_gold_nugget": "The compliance burden may be real even when the owner does not yet control the dominant efficiency lever.",
                "strategic_action": "Request control-boundary evidence before underwriting owner-side retrofit economics.",
            }
        )
        if "BMS / controls" in subsystems or "HVAC / central plant" in subsystems:
            rows.append(
                {
                    "correlation": "Central plant / BMS presence + after-hours schedule ambiguity",
                    "layers_connected": ["physics", "operation", "controls"],
                    "evidence_state": "CONDITIONAL_HYPOTHESIS",
                    "why_it_matters": "Schedule waste can be economically material only if the owner controls the affected systems and hours.",
                    "strategic_meaning": "The issue may be runtime orchestration, not equipment inefficiency.",
                    "what_confirms": ["BMS trend logs", "after-hours occupancy profile", "central plant topology"],
                    "what_falsifies": ["minimal after-hours load or tenant-dominant uncontrolled schedule"],
                    "evidence_needed": ["BMS trend logs", "after-hours occupancy profile", "central plant topology"],
                    "possible_gold_nugget": "Before retrofitting plant equipment, determine whether the plant is simply running when the building is not.",
                    "strategic_action": "Use schedule evidence to discriminate between control problem and generic efficiency story.",
                }
            )

    if asset_family in {"industrial_manufacturing", "thermal_process_site", "utility_heavy_site"}:
        if {"motors / drives / fans / pumps", "compressed air"} & subsystems or {"large motors and drives", "compressors"} & subsystems:
            rows.append(
                {
                    "correlation": "Inductive support systems + tariff context",
                    "layers_connected": ["physics", "tariff", "finance"],
                    "evidence_state": "CONDITIONAL_HYPOTHESIS" if tariff_public else "ARCHETYPAL_PRIOR",
                    "why_it_matters": "Demand, PF or reactive exposure can dominate savings logic more than aggregate kWh alone.",
                    "strategic_meaning": "The economic problem may be electrical-quality and tariff structure, not generic energy intensity.",
                    "what_confirms": ["utility bill with demand or PF charges", "major motor inventory", "interval demand profile"],
                    "what_falsifies": ["flat tariff structure with no demand or PF exposure"],
                    "evidence_needed": ["utility bill with demand or PF charges", "major motor inventory", "interval demand profile"],
                    "possible_gold_nugget": "If the tariff penalizes PF or peaks, the highest-value fix may have little to do with annual consumption.",
                    "strategic_action": "Request bill and tariff evidence before assuming consumption-only economics.",
                }
            )
        if {"process heating / thermal systems", "steam / boiler systems", "furnaces / kilns / ovens", "boilers / burners"} & subsystems:
            rows.append(
                {
                    "correlation": "Thermal process subsystems + regulatory or permit context",
                    "layers_connected": ["physics", "permits", "regulation", "operation"],
                    "evidence_state": "CONDITIONAL_HYPOTHESIS",
                    "why_it_matters": "Permitting and thermal-duty signals may indicate that structural process load, combustion quality or emissions constraints dominate the decision.",
                    "strategic_meaning": "Permit-bearing thermal systems can reveal that the real problem is duty discrimination, not simplistic waste hunting.",
                    "what_confirms": ["fuel bills", "air permit coverage", "combustion test records", "throughput by shift"],
                    "what_falsifies": ["observed non-thermal dominant process with low combustion relevance"],
                    "evidence_needed": ["fuel bills", "air permit coverage", "combustion test records", "throughput by shift"],
                    "possible_gold_nugget": "The permit file may tell you more about the energy story than the benchmark table does.",
                    "strategic_action": "Separate process-duty logic from generic energy-waste framing.",
                }
            )
        rows.append(
            {
                "correlation": "Support-system complexity + maintenance dependency",
                "layers_connected": ["maintenance", "operation", "physics"],
                "evidence_state": "CONDITIONAL_HYPOTHESIS",
                "why_it_matters": "Maintenance discipline may determine whether visible energy symptoms are structural process duty or avoidable operational loss.",
                "strategic_meaning": "Downtime and maintenance reality may be the real economic lane behind the utility symptom.",
                "what_confirms": ["maintenance logs", "downtime records", "critical spare evidence"],
                "what_falsifies": ["observed strong PM discipline with stable uptime"],
                "evidence_needed": ["maintenance logs", "downtime records", "critical spare evidence"],
                "possible_gold_nugget": "An energy problem can be a reliability problem in disguise.",
                "strategic_action": "Request maintenance proof before assuming energy-first CAPEX is the priority.",
            }
        )

    if asset_family in {"logistics_warehouse", "cold_chain"}:
        rows.append(
            {
                "correlation": "Movement / dock systems + schedule complexity",
                "layers_connected": ["logistics", "operation", "physics"],
                "evidence_state": "CONDITIONAL_HYPOTHESIS",
                "why_it_matters": "Dock traffic, charging windows and service-level pressure can dominate energy shape more than area alone.",
                "strategic_meaning": "The denominator may be wrong because the cost driver is movement intensity, not square footage.",
                "what_confirms": ["dock activity profile", "charging schedule", "throughput or service-level proxy"],
                "what_falsifies": ["low-variability operation with simple service profile"],
                "evidence_needed": ["dock activity profile", "charging schedule", "throughput or service-level proxy"],
                "possible_gold_nugget": "A high-service logistics node can look inefficient only because it is being measured with the wrong denominator.",
                "strategic_action": "Normalize service intensity before comparing to peer warehouses.",
            }
        )
        rows.append(
            {
                "correlation": "MHE charging + demand tariff + operating schedule",
                "layers_connected": ["logistics", "tariff", "finance", "operation"],
                "evidence_state": "CONDITIONAL_HYPOTHESIS",
                "why_it_matters": "Charging concentration can make the cost problem a tariff and scheduling problem rather than an efficiency problem.",
                "strategic_meaning": "The issue may be demand orchestration, not annual energy efficiency.",
                "what_confirms": ["utility bills with demand charges", "charging schedule", "MHE inventory"],
                "what_falsifies": ["no demand-charge structure", "distributed/off-peak charging", "no meaningful electric MHE load"],
                "evidence_needed": ["utility bills with demand charges", "charging schedule", "MHE inventory"],
                "possible_gold_nugget": "If charging drives peak demand, the asset may have a tariff design problem disguised as energy inefficiency.",
                "strategic_action": "Validate tariff exposure before underwriting generic efficiency retrofit logic.",
            }
        )
        rows.append(
            {
                "correlation": "Dock activity + climate + HVAC/refrigeration duty",
                "layers_connected": ["logistics", "climate", "physics", "operation"],
                "evidence_state": "CONDITIONAL_HYPOTHESIS",
                "why_it_matters": "Air exchange through the logistics interface can dominate conditioning duty more than equipment efficiency does.",
                "strategic_meaning": "Loss may be dominated by air exchange and logistics-envelope interaction, not generic HVAC inefficiency.",
                "what_confirms": ["dock cycles", "weather/climate context", "refrigerated or conditioned footprint", "door discipline evidence"],
                "what_falsifies": ["minimal dock traffic near conditioned zones", "little or no conditioned/refrigerated duty"],
                "evidence_needed": ["dock cycles", "weather/climate context", "refrigerated or conditioned footprint", "door discipline evidence"],
                "possible_gold_nugget": "Before buying equipment, determine whether the building is leaking conditioned air through its logistics interface.",
                "strategic_action": "Validate loss pattern before HVAC or refrigeration capital framing.",
            }
        )
        rows.append(
            {
                "correlation": "Operator control + utility payer + CAPEX boundary",
                "layers_connected": ["control", "finance", "logistics"],
                "evidence_state": "CONDITIONAL_HYPOTHESIS",
                "why_it_matters": "If the operator controls docks, charging and schedules while the owner pays utility or CAPEX, value capture can leak.",
                "strategic_meaning": "The economics may be broken by boundary, not by physics.",
                "what_confirms": ["lease responsibility matrix", "metering boundary", "utility payer evidence", "operator control over charging/docks"],
                "what_falsifies": ["clean alignment between operator control and cost responsibility", "owner directly controls dominant drivers"],
                "evidence_needed": ["lease responsibility matrix", "metering boundary", "utility payer evidence", "operator control over charging/docks"],
                "possible_gold_nugget": "If the operator controls docks and charging but the owner pays utility or CAPEX, retrofit value may leak across the boundary.",
                "strategic_action": "Validate control boundary before owner-side ROI logic.",
            }
        )
        if "refrigeration plant" in subsystems:
            rows.append(
                {
                    "correlation": "Refrigeration plant + door / infiltration exposure",
                    "layers_connected": ["refrigeration", "logistics", "physics"],
                    "evidence_state": "CONDITIONAL_HYPOTHESIS",
                    "why_it_matters": "Temperature duty and door traffic may dominate total-site energy and invalidate general warehouse benchmarks.",
                    "strategic_meaning": "Cold-chain duty changes the asset family and the valid peer frame.",
                    "what_confirms": ["door traffic profile", "temperature bands", "defrost schedule"],
                    "what_falsifies": ["minimal temperature-control duty"],
                    "evidence_needed": ["door traffic profile", "temperature bands", "defrost schedule"],
                    "possible_gold_nugget": "Cold-chain status is not a detail. It changes the asset family.",
                    "strategic_action": "Treat cold-chain logic separately from general storage logic.",
                }
            )

    _ = control_boundary_map
    return rows


def build_structural_correlation_graph(
    *,
    structural_correlation_register: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for index, row in enumerate(list(structural_correlation_register or []), start=1):
        rows.append(
            {
                "correlation_id": f"corr_{index:02d}",
                "correlation": text(row.get("correlation")),
                "layers_connected": list(row.get("layers_connected", []) or []),
                "strategic_meaning": text(row.get("strategic_meaning")) or text(row.get("why_it_matters")),
                "evidence_needed": list(row.get("evidence_needed", []) or row.get("what_confirms", []) or []),
                "possible_gold_nugget": text(row.get("possible_gold_nugget")),
                "evidence_state": text(row.get("evidence_state")),
            }
        )
    return rows


def build_correlation_priority_register(
    *,
    structural_correlation_graph: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for row in list(structural_correlation_graph or []):
        layers = list(row.get("layers_connected", []) or [])
        evidence_state = text(row.get("evidence_state"))
        priority_score = len(layers) * 10 + (5 if evidence_state == "CONDITIONAL_HYPOTHESIS" else 3)
        rows.append(
            {
                "correlation_id": text(row.get("correlation_id")),
                "correlation": text(row.get("correlation")),
                "priority_score": priority_score,
                "priority_reason": f"{len(layers)} layers connected",
                "strategic_meaning": text(row.get("strategic_meaning")),
            }
        )
    rows.sort(key=lambda item: (-int(item.get("priority_score", 0) or 0), text(item.get("correlation_id"))))
    return rows


def build_gold_nugget_candidate_register(
    *,
    structural_correlation_graph: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    return [
        {
            "correlation_id": text(row.get("correlation_id")),
            "gold_nugget_candidate": text(row.get("possible_gold_nugget")),
            "why_it_matters": text(row.get("strategic_meaning")),
            "evidence_needed": list(row.get("evidence_needed", []) or []),
            "evidence_state": text(row.get("evidence_state")),
        }
        for row in list(structural_correlation_graph or [])
        if text(row.get("possible_gold_nugget"))
    ]
