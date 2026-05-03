from __future__ import annotations

from typing import Any

from .schemas import text


def _route_state(asset_family_research_profile: dict[str, Any]) -> str:
    return text(asset_family_research_profile.get("route_state"))


def _asset_family(asset_family_research_profile: dict[str, Any]) -> str:
    return text(asset_family_research_profile.get("asset_family"))


def build_measurement_strategy_register(
    *,
    asset_family_research_profile: dict[str, Any],
    power_quality_hypothesis_register: list[dict[str, Any]],
    leakage_hypothesis_register: list[dict[str, Any]],
    loss_pattern_hypothesis_register: list[dict[str, Any]],
    maintenance_reality_register: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    if _route_state(asset_family_research_profile) != "operational_asset_candidate":
        return []

    asset_family = _asset_family(asset_family_research_profile)
    rows: list[dict[str, Any]] = []

    if asset_family == "commercial_building":
        rows.append(
            {
                "hypothesis": "owner_vs_tenant_control_boundary_drives_the_case",
                "minimum_measurement": "utility bills + tenant metering map + lease responsibility matrix",
                "why": "The first discriminating question is boundary and economic capture, not extra sensing.",
                "if_confirmed": "Reframe the case around control boundary and owner-capturable logic.",
                "if_falsified": "De-prioritize control-boundary ambiguity and focus on directly owner-controlled systems.",
                "hardware_trigger": "No new hardware until document and metering-boundary evidence fail to discriminate the question.",
            }
        )
        rows.append(
            {
                "hypothesis": "after_hours_schedule_waste_is_material",
                "minimum_measurement": "BMS trend logs + after-hours occupancy profile",
                "why": "Existing trend data should discriminate schedule drift before any new sensor rollout.",
                "if_confirmed": "Prioritize schedule and control correction before broader capital action.",
                "if_falsified": "De-prioritize schedule waste and refocus on boundary or central-plant questions.",
                "hardware_trigger": "Temporary sensors only if BMS data are absent and the issue remains material.",
            }
        )

    if asset_family == "infrastructure_node":
        rows.append(
            {
                "hypothesis": "continuity_burden_not_average_energy_drives_cost",
                "minimum_measurement": "utility bills + tariff structure + service continuity or dispatch logs + equipment inventory",
                "why": "The first job is to separate continuity duty and redundancy burden from avoidable electrical or operational waste.",
                "if_confirmed": "Route the case toward continuity-aware optimization and bounded tariff logic, not generic consumption reduction.",
                "if_falsified": "De-prioritize continuity-duty framing and look for more targeted demand, maintenance or subsystem losses.",
                "hardware_trigger": "No broad sensors until bills, tariff and continuity records fail to discriminate the question.",
            }
        )
        if power_quality_hypothesis_register:
            rows.append(
                {
                    "hypothesis": "power_quality_or_pf_exposure_is_material",
                    "minimum_measurement": "utility bill with demand/PF charges + tariff structure + major equipment inventory + temporary analyzer only if needed",
                    "why": "Bills, tariff logic and continuity duty must justify any analyzer deployment.",
                    "if_confirmed": "Prioritize tariff-aware sequencing, PF correction or targeted controls without violating continuity obligations.",
                    "if_falsified": "De-prioritize electrical-quality logic and refocus on continuity, maintenance or dispatch hypotheses.",
                    "hardware_trigger": "Use a temporary analyzer only after the bill and tariff show a material electrical-quality question.",
                }
            )

    if asset_family in {"industrial_manufacturing", "thermal_process_site", "utility_heavy_site"}:
        rows.append(
            {
                "hypothesis": "process_or_support_system_load_dominates_cost",
                "minimum_measurement": "utility bills + throughput by shift + process map + equipment inventory",
                "why": "The first job is to separate structural process duty from controllable support-system waste.",
                "if_confirmed": "Route the case toward process redesign, support-system optimization or maintenance evidence as appropriate.",
                "if_falsified": "De-prioritize process-duty framing and look for dominant support-system losses.",
                "hardware_trigger": "No broad sensors until bills and process normalization fail to discriminate the question.",
            }
        )
        if power_quality_hypothesis_register:
            rows.append(
                {
                    "hypothesis": "power_quality_or_pf_exposure_is_material",
                    "minimum_measurement": "utility bill with demand/PF charges + tariff structure + motor inventory + temporary analyzer only if needed",
                    "why": "Bills and tariff logic must justify any analyzer deployment.",
                    "if_confirmed": "Prioritize tariff-aware sequencing, PF correction or targeted controls before generic efficiency CAPEX.",
                    "if_falsified": "De-prioritize electrical-quality logic and refocus on thermal, maintenance or process hypotheses.",
                    "hardware_trigger": "Use a temporary analyzer only after the bill and tariff show a material electrical-quality question.",
                }
            )
        if leakage_hypothesis_register:
            rows.append(
                {
                    "hypothesis": "leakage_or_hidden_thermal_loss_is_material",
                    "minimum_measurement": "operator walkdown or leak survey + maintenance records + bills/fuel data",
                    "why": "A targeted survey discriminates leakage logic faster and cheaper than permanent instrumentation.",
                    "if_confirmed": "Prioritize maintenance or control correction before new hardware rollout.",
                    "if_falsified": "De-prioritize leakage and re-rank other support-system hypotheses.",
                    "hardware_trigger": "Permanent sensors only if repeated surveys cannot resolve a material recurring loss.",
                }
            )

    if asset_family in {"logistics_warehouse", "cold_chain"}:
        rows.append(
            {
                "hypothesis": "service_intensity_not_area_drives_cost",
                "minimum_measurement": "utility bills + operating schedule + service-level proxy + dock activity or charging profile",
                "why": "Operational intensity must be bounded before any hardware-first logic.",
                "if_confirmed": "Normalize service intensity before diagnosing inefficiency or comparing peers.",
                "if_falsified": "De-prioritize movement-intensity framing and look for subsystem-specific issues.",
                "hardware_trigger": "Temporary data logging only if schedule and activity records cannot discriminate the question.",
            }
        )

    if any("maintenance maturity" in text(row.get("reality_claim")).lower() for row in maintenance_reality_register):
        rows.append(
            {
                "hypothesis": "maintenance_reality_changes_the_economic_story",
                "minimum_measurement": "maintenance logs + downtime records + PM evidence",
                "why": "The next discriminating evidence may be organizational and operational, not sensor-based.",
                "if_confirmed": "Re-rank the case toward uptime, reliability or governance action.",
                "if_falsified": "Treat maintenance as less likely to dominate the visible symptom set.",
                "hardware_trigger": "No hardware upgrade justified by maintenance ambiguity alone.",
            }
        )

    _ = loss_pattern_hypothesis_register
    return rows
