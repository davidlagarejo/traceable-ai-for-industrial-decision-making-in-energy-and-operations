from __future__ import annotations

from typing import Any

from .schemas import text


def _subsystem_names(subsystem_register: list[dict[str, Any]]) -> set[str]:
    return {
        text(row.get("subsystem_name"))
        for row in subsystem_register
        if text(row.get("subsystem_name"))
    }


def _route_state(asset_family_research_profile: dict[str, Any]) -> str:
    return text(asset_family_research_profile.get("route_state"))


def _pack_state(operational_intake_pack: dict[str, Any], pack_name: str) -> str:
    return text((operational_intake_pack.get(pack_name, {}) or {}).get("current_state"))


def _question_ids(dynamic_intake_question_register: list[dict[str, Any]]) -> set[str]:
    return {
        text(row.get("question_id"))
        for row in list(dynamic_intake_question_register or [])
        if text(row.get("question_id"))
    }


def _peer_requirement_keys(peer_requirement_register: list[dict[str, Any]]) -> set[str]:
    return {
        text(row.get("requirement_key"))
        for row in list(peer_requirement_register or [])
        if text(row.get("requirement_key"))
    }


def _pattern(
    *,
    pattern_name: str,
    system_domain: str,
    applicability: str,
    evidence_state: str,
    hypothesis: str,
    why_plausible: str,
    minimum_local_evidence: list[str],
    what_confirms: list[str],
    what_falsifies: list[str],
    economic_materiality_gate: str,
    tad_action: str,
) -> dict[str, Any]:
    return {
        "pattern_name": text(pattern_name),
        "system_domain": text(system_domain),
        "pattern_class": "structural_pattern",
        "applicability": text(applicability),
        "evidence_state": text(evidence_state),
        "hypothesis": text(hypothesis),
        "why_plausible": text(why_plausible),
        "minimum_local_evidence": list(minimum_local_evidence or []),
        "what_confirms": list(what_confirms or []),
        "what_falsifies": list(what_falsifies or []),
        "economic_materiality_gate": text(economic_materiality_gate),
        "tad_action": text(tad_action),
        "allowed_language": "Plausible recurring pattern for this system family; must be locally falsified before diagnosis.",
        "prohibited_language": "Do not state that the site has this loss as observed fact without local evidence.",
    }


def build_loss_pattern_hypothesis_register(
    *,
    asset_family_research_profile: dict[str, Any],
    operational_intake_pack: dict[str, Any],
    subsystem_register: list[dict[str, Any]],
    dynamic_intake_question_register: list[dict[str, Any]] | None = None,
    peer_requirement_register: list[dict[str, Any]] | None = None,
) -> list[dict[str, Any]]:
    asset_family = text(asset_family_research_profile.get("asset_family"))
    if _route_state(asset_family_research_profile) != "operational_asset_candidate":
        return []

    subsystems = _subsystem_names(subsystem_register)
    question_ids = _question_ids(dynamic_intake_question_register or [])
    peer_requirement_keys = _peer_requirement_keys(peer_requirement_register or [])
    utility_state = _pack_state(operational_intake_pack, "utility_and_tariff_pack")
    control_state = _pack_state(operational_intake_pack, "control_boundary_pack")
    rows: list[dict[str, Any]] = []

    if asset_family == "commercial_building":
        rows.append(
            _pattern(
                pattern_name="schedule_and_after_hours_waste_plausible",
                system_domain="controls_and_schedule",
                applicability="high",
                evidence_state="CONDITIONAL_HYPOTHESIS",
                hypothesis="After-hours occupancy and schedule drift may create avoidable load if the owner controls the affected systems.",
                why_plausible="Commercial buildings with central plant and BMS layers recurrently lose value through schedule mismatch before deeper retrofit logic is bounded.",
                minimum_local_evidence=["BMS trend logs", "after-hours occupancy profile", "tenant schedule evidence"],
                what_confirms=["BMS trends showing HVAC/lighting runtime after occupied hours", "after-hours occupancy materially below runtime pattern"],
                what_falsifies=["occupied schedule aligns with HVAC/lighting runtime", "major loads are tenant-controlled and not owner-capturable"],
                economic_materiality_gate="Material only if the owner controls the affected systems and the schedule mismatch drives enough hours or demand.",
                tad_action="VALIDATE_LOSS_PATTERN",
            )
        )
        rows.append(
            _pattern(
                pattern_name="simultaneous_heating_cooling_plausible",
                system_domain="HVAC_and_central_plant",
                applicability="high",
                evidence_state="ARCHETYPAL_PRIOR" if "HVAC / central plant" in subsystems else "CONDITIONAL_HYPOTHESIS",
                hypothesis="Simultaneous heating and cooling can be a recurrent hidden loss pattern where central plant logic and zone control are poorly aligned.",
                why_plausible="Mixed-mode commercial buildings recurrently suffer from control and sequencing mismatch.",
                minimum_local_evidence=["BMS trend logs", "airside and waterside sequence review", "zone complaint patterns"],
                what_confirms=["simultaneous valve / damper / heating-cooling calls in trend data", "zone complaints consistent with control conflict"],
                what_falsifies=["sequencing review shows no overlapping heating/cooling duty", "building topology uses packaged zones without overlap risk"],
                economic_materiality_gate="Material only if sequencing mismatch persists at meaningful operating hours and is owner-capturable.",
                tad_action="VALIDATE_LOSS_PATTERN",
            )
        )
        rows.append(
            _pattern(
                pattern_name="missing_control_boundary_visibility",
                system_domain="metering_and_governance",
                applicability="high",
                evidence_state="CONDITIONAL_HYPOTHESIS" if control_state != "partially_evidenced" else "ARCHETYPAL_PRIOR",
                hypothesis="The dominant hidden loss may be governance and metering opacity rather than pure technical inefficiency.",
                why_plausible="Without tenant metering and lease-boundary clarity, the owner may be optimizing the wrong part of the system.",
                minimum_local_evidence=["tenant metering map", "lease responsibility matrix", "utility billing responsibility map"],
                what_confirms=["tenant/owner control boundary remains unresolved", "billing boundary does not align with operational control"],
                what_falsifies=["metering and lease matrix show clean owner control over dominant loads", "tenant loads are isolated and non-dominant"],
                economic_materiality_gate="Material if the unresolved boundary prevents valid owner-side capital logic.",
                tad_action="VALIDATE_CONTROL_BOUNDARY",
            )
        )
        rows.append(
            _pattern(
                pattern_name="lighting_controls_failure_plausible",
                system_domain="lighting_and_controls",
                applicability="medium",
                evidence_state="CONDITIONAL_HYPOTHESIS",
                hypothesis="Lighting control failure or schedule mismatch may be creating avoidable load and false retrofit narratives.",
                why_plausible="Commercial buildings recurrently lose value through basic controls drift before larger capital interventions are warranted.",
                minimum_local_evidence=["lighting control schedules", "after-hours lighting runtime", "occupancy schedule"],
                what_confirms=["lighting runtime materially exceeds occupied hours", "manual override patterns persist without operational reason"],
                what_falsifies=["lighting schedules align with occupancy", "lights are already zoned and controlled to actual use"],
                economic_materiality_gate="Material if large common areas or after-hours schedules make lighting runtime non-trivial.",
                tad_action="VALIDATE_LOSS_PATTERN",
            )
        )

    if asset_family in {"industrial_manufacturing", "thermal_process_site", "utility_heavy_site", "infrastructure_node"}:
        if "compressed air" in subsystems or "compressors" in subsystems:
            rows.append(
                _pattern(
                    pattern_name="compressed_air_leakage_or_pressure_overuse_plausible",
                    system_domain="compressed_air",
                    applicability="high",
                    evidence_state="CONDITIONAL_HYPOTHESIS",
                    hypothesis="Compressed-air leakage, pressure overuse or poor sequencing may be materially affecting cost.",
                    why_plausible="Compressed-air systems recurrently hide economically meaningful losses even when the plant's main issue is not generic kWh reduction.",
                    minimum_local_evidence=["leak survey evidence", "compressor sequencing logic", "pressure setpoints", "utility bills or demand profile"],
                    what_confirms=["leak survey finds significant loss", "pressure setpoints materially exceed process need", "compressors short-cycle or run unloaded"],
                    what_falsifies=["survey shows low leakage and right-sized pressure", "compressed air use is structurally process-critical and well sequenced"],
                    economic_materiality_gate="Material if compressed air is a major support utility and the cost structure penalizes excess runtime or pressure.",
                    tad_action="VALIDATE_LOSS_PATTERN",
                )
            )
        if {"process heating / thermal systems", "steam / boiler systems", "furnaces / kilns / ovens", "boilers / burners"} & subsystems:
            rows.append(
                _pattern(
                    pattern_name="thermal_combustion_and_recovery_losses_plausible",
                    system_domain="thermal_process",
                    applicability="high",
                    evidence_state="CONDITIONAL_HYPOTHESIS",
                    hypothesis="Combustion quality, excess air, stack losses, poor insulation or unrecovered condensate may dominate the avoidable-loss story.",
                    why_plausible="Thermal-process and boiler-heavy sites recurrently hide losses in combustion tuning and heat recovery, not just aggregate fuel use.",
                    minimum_local_evidence=["combustion test records", "fuel bills", "steam trap or condensate evidence", "throughput-normalized duty context"],
                    what_confirms=["combustion tests show excess air or poor tuning", "steam/condensate evidence shows unrecovered heat or trap failure", "throughput-normalized duty exceeds expected lane"],
                    what_falsifies=["combustion tests are tight and recovery systems perform as designed", "thermal duty is fully explained by throughput and product mix"],
                    economic_materiality_gate="Material if thermal duty is large enough that marginal efficiency changes move fuel cost or constraint risk.",
                    tad_action="VALIDATE_LOSS_PATTERN",
                )
            )
        if {"motors / drives / fans / pumps", "large motors and drives", "compressors"} & subsystems:
            rows.append(
                _pattern(
                    pattern_name="demand_pf_or_reactive_exposure_plausible",
                    system_domain="electrical_quality_and_tariff",
                    applicability="high",
                    evidence_state="CONDITIONAL_HYPOTHESIS" if utility_state in {"public_context_only", "partially_evidenced"} else "ARCHETYPAL_PRIOR",
                    hypothesis="Demand spikes, poor PF or reactive exposure may matter more economically than total consumption reduction.",
                    why_plausible="Inductive support systems recurrently create a cost story that is invisible if the analyst only watches aggregate kWh.",
                    minimum_local_evidence=["utility bill with tariff structure", "PF or demand charges", "interval demand profile", "motor inventory"],
                    what_confirms=["utility bills show demand or PF charges", "interval profile shows concentrated peaks", "motor inventory indicates inductive penalty risk"],
                    what_falsifies=["tariff does not penalize demand or PF", "interval profile is flat and motors do not drive peaks materially"],
                    economic_materiality_gate="Material only if tariff structure actually penalizes demand or PF behavior.",
                    tad_action="VALIDATE_TARIFF_EXPOSURE",
                )
            )
        if asset_family in {"industrial_manufacturing", "thermal_process_site"}:
            rows.append(
                _pattern(
                    pattern_name="idle_equipment_and_schedule_waste_plausible",
                    system_domain="process_schedule_and_utilities",
                    applicability="medium",
                    evidence_state="CONDITIONAL_HYPOTHESIS",
                    hypothesis="Utilities or major equipment may be running outside productive duty windows.",
                    why_plausible="Industrial sites recurrently carry idle runtime when schedule, maintenance and production ownership are weakly coordinated.",
                    minimum_local_evidence=["throughput by shift", "equipment runtime logs", "operator schedule evidence"],
                    what_confirms=["runtime persists during low or zero throughput windows", "utilities remain active outside justified duty periods"],
                    what_falsifies=["runtime aligns with actual throughput and startup constraints", "idle periods are operationally necessary"],
                    economic_materiality_gate="Material if runtime extends meaningfully beyond productive duty and affects energy or maintenance cost.",
                    tad_action="VALIDATE_LOSS_PATTERN",
                )
            )
            rows.append(
                _pattern(
                    pattern_name="poor_lubrication_or_reactive_maintenance_plausible",
                    system_domain="maintenance_and_reliability",
                    applicability="medium",
                    evidence_state="CONDITIONAL_HYPOTHESIS",
                    hypothesis="The visible utility symptom may be secondary to weak maintenance execution, lubrication, or reactive reliability practices.",
                    why_plausible="Plants recurrently mistake reliability and maintenance debt for pure efficiency problems.",
                    minimum_local_evidence=["PM logs", "lubrication records", "downtime history", "work orders"],
                    what_confirms=["PM proof is thin and downtime clusters around critical utilities", "maintenance records show reactive rather than planned interventions"],
                    what_falsifies=["maintenance maturity is evidenced and downtime does not align with the visible symptom", "reliability program is mature and preventive"],
                    economic_materiality_gate="Material if downtime, scrap, or asset stress dominate the economics more than direct energy savings.",
                    tad_action="VALIDATE_MAINTENANCE_REALITY",
                )
            )
        rows.append(
            _pattern(
                pattern_name="nobody_owns_the_data_or_support_system_boundary",
                system_domain="culture_and_governance",
                applicability="high",
                evidence_state="ARCHETYPAL_PRIOR",
                hypothesis="The hidden loss may be weak operational ownership of utility data, support systems or basic maintenance evidence.",
                why_plausible="Industrial sites recurrently struggle when process, utility and maintenance ownership are split and no one owns the discriminatory evidence.",
                minimum_local_evidence=["utility bill ownership", "equipment inventory owner", "maintenance proof", "throughput records"],
                what_confirms=["no clear owner for bills, equipment inventory, or maintenance records", "cross-functional evidence remains fragmented"],
                what_falsifies=["clear ownership exists and discriminatory evidence is already governed", "responsibility matrix aligns with decision authority"],
                economic_materiality_gate="Material if missing ownership delays decisions or misdirects CAPEX toward the wrong subsystem.",
                tad_action="REQUEST_MINIMUM_EVIDENCE",
            )
        )

    if asset_family in {"logistics_warehouse", "cold_chain"}:
        rows.append(
            _pattern(
                pattern_name="schedule_and_idle_conditioning_waste_plausible",
                system_domain="logistics_flow_and_schedule",
                applicability="high",
                evidence_state="CONDITIONAL_HYPOTHESIS",
                hypothesis="Operating schedule and idle conditioning may dominate the loss story more than area-based energy intensity.",
                why_plausible="Warehouse and logistics sites recurrently hide losses in schedule mismatch and conditioned runtime rather than in isolated equipment efficiency.",
                minimum_local_evidence=["dock activity profile", "service-level proxy", "operating schedule", "movement or charging pattern evidence"],
                what_confirms=["conditioning runtime materially exceeds active service windows", "dock/service schedule shows large idle conditioned periods"],
                what_falsifies=["conditioning follows service windows closely", "runtime is justified by actual throughput or temperature duty"],
                economic_materiality_gate="Material if service complexity or charging behavior shapes peak cost or conditioned-load behavior.",
                tad_action="VALIDATE_LOSS_PATTERN",
            )
        )
        rows.append(
            _pattern(
                pattern_name="dock_infiltration_and_door_discipline_plausible",
                system_domain="docks_and_envelope",
                applicability="high",
                evidence_state="CONDITIONAL_HYPOTHESIS",
                hypothesis="Dock traffic, infiltration, poor seals, or weak door discipline may dominate the thermal and conditioning loss story.",
                why_plausible="Warehouse interfaces recurrently leak conditioned air through loading behavior rather than through generic equipment inefficiency.",
                minimum_local_evidence=["dock count", "door cycle profile", "seal condition", "temperature duty"],
                what_confirms=["high dock cycles with weak sealing/discipline", "conditioning load spikes align with loading periods", "door condition or seal evidence is poor"],
                what_falsifies=["limited door activity or strong dock-seal controls", "no conditioned thermal duty near dock operations"],
                economic_materiality_gate="Material if dock activity intersects with conditioned or refrigerated zones.",
                tad_action="VALIDATE_LOSS_PATTERN",
            )
        )
        rows.append(
            _pattern(
                pattern_name="high_bay_lighting_waste_plausible",
                system_domain="lighting",
                applicability="medium",
                evidence_state="CONDITIONAL_HYPOTHESIS",
                hypothesis="High-bay lighting runtime or controls drift may create avoidable load in logistics assets with long schedules and intermittent occupancy.",
                why_plausible="Warehouse lighting often follows crude schedules even when service windows and occupancy are variable.",
                minimum_local_evidence=["lighting type", "controls strategy", "occupied vs lit schedule", "bay zoning"],
                what_confirms=["lighting runtime materially exceeds active occupancy/service windows", "controls are absent or bypassed in large high-bay zones"],
                what_falsifies=["lighting is LED/controlled and aligned to actual occupancy", "service window requires continuous lighting by design"],
                economic_materiality_gate="Material if large high-bay floor area or long runtime makes lighting a meaningful share of load.",
                tad_action="VALIDATE_LOSS_PATTERN",
            )
        )
        rows.append(
            _pattern(
                pattern_name="rooftop_hvac_degradation_plausible",
                system_domain="hvac_and_conditioning",
                applicability="medium",
                evidence_state="CONDITIONAL_HYPOTHESIS",
                hypothesis="Rooftop HVAC degradation, sequencing issues, or poor conditioning zoning may be inflating cost.",
                why_plausible="Warehouse rooftop systems recurrently drift or degrade, especially where schedules and dock behavior create unstable load conditions.",
                minimum_local_evidence=["HVAC / rooftop inventory", "maintenance history", "runtime or condition evidence", "conditioned-zone map"],
                what_confirms=["aged or poorly maintained RTUs", "runtime/maintenance evidence shows degraded performance", "conditioned zones are poorly matched to operations"],
                what_falsifies=["rooftop systems are limited, well-maintained, or non-dominant", "conditioning load is dominated by dock/refrigeration interface instead"],
                economic_materiality_gate="Material if conditioning systems serve large areas or peak windows relevant to cost.",
                tad_action="VALIDATE_LOSS_PATTERN",
            )
        )
        rows.append(
            _pattern(
                pattern_name="poor_submetering_and_boundary_visibility_plausible",
                system_domain="metering_and_governance",
                applicability="high" if "control_boundary_and_tariff" in peer_requirement_keys or "warehouse_control_boundary" in question_ids else "medium",
                evidence_state="CONDITIONAL_HYPOTHESIS" if control_state != "evidenced" else "ARCHETYPAL_PRIOR",
                hypothesis="Poor submetering or boundary visibility may be the reason the cost story looks like generic inefficiency.",
                why_plausible="Warehouse portfolios recurrently lack the boundary visibility needed to separate owner burden, operator behavior, and charging loads.",
                minimum_local_evidence=["meter map", "lease responsibility matrix", "billing boundary", "submeter list"],
                what_confirms=["metering does not align with operational zones or control boundary", "bills aggregate unrelated loads or tenant spaces"],
                what_falsifies=["metering cleanly aligns with zones and decision boundaries", "billing and operational control match cleanly"],
                economic_materiality_gate="Material if missing visibility blocks valid attribution of cost drivers or savings.",
                tad_action="VALIDATE_CONTROL_BOUNDARY",
            )
        )
        if asset_family == "cold_chain":
            rows.append(
                _pattern(
                    pattern_name="refrigeration_infiltration_and_defrost_logic_plausible",
                    system_domain="refrigeration",
                    applicability="high",
                    evidence_state="CONDITIONAL_HYPOTHESIS",
                    hypothesis="Door traffic, infiltration and defrost logic may dominate cold-chain loss patterns.",
                    why_plausible="Temperature-controlled assets recurrently lose value through operational boundary issues, not just refrigeration nameplate efficiency.",
                    minimum_local_evidence=["door traffic profile", "defrost schedule", "temperature bands", "refrigeration inventory"],
                    what_confirms=["door traffic and infiltration align with refrigeration runtime spikes", "defrost schedule is poorly aligned with operating regime", "temperature bands imply high latent/sensible loss risk"],
                    what_falsifies=["stable low-infiltration operation with disciplined door behavior", "defrost logic already optimized to duty and bands"],
                    economic_materiality_gate="Material if temperature duty and infiltration behavior dominate the site's operating envelope.",
                    tad_action="VALIDATE_LOSS_PATTERN",
                )
            )
        else:
            rows.append(
                _pattern(
                    pattern_name="forklift_charging_and_demand_spike_plausible",
                    system_domain="motive_power_and_tariff",
                    applicability="high",
                    evidence_state="CONDITIONAL_HYPOTHESIS",
                    hypothesis="Charging windows and dock activity may create demand spikes that distort the cost story.",
                    why_plausible="Warehouse energy economics recurrently depend on when charging and movement happen, not just how much area is conditioned.",
                    minimum_local_evidence=["forklift fleet and charging schedule", "interval demand profile", "service-level profile"],
                    what_confirms=["charging windows cluster into bill peak periods", "fleet size and charger mix imply concentrated demand spikes", "service-level peaks align with demand peaks"],
                    what_falsifies=["charging is distributed or off-peak", "utility bills do not show material demand structure", "fleet is fuel-based or non-dominant"],
                    economic_materiality_gate="Material only if peak charges or charging concentration matter economically.",
                    tad_action="VALIDATE_TARIFF_EXPOSURE",
                )
            )
        if asset_family == "logistics_warehouse":
            rows.append(
                _pattern(
                    pattern_name="door_discipline_breakdown_plausible",
                    system_domain="operations_and_docks",
                    applicability="medium",
                    evidence_state="CONDITIONAL_HYPOTHESIS",
                    hypothesis="Weak dock-door discipline or trailer dwell behavior may be creating recurring conditioned-air loss and false HVAC blame.",
                    why_plausible="Operational discipline around doors and dwell time often matters more than equipment nameplate efficiency at logistics interfaces.",
                    minimum_local_evidence=["door open-time profile", "yard/trailer dwell behavior", "dock operating practices", "conditioned-zone adjacency"],
                    what_confirms=["long door-open durations or dwell times during conditioned operation", "operational practice keeps conditioned doors open without offset controls"],
                    what_falsifies=["strict door discipline and short dwell time", "dock operations are isolated from conditioned zones"],
                    economic_materiality_gate="Material if conditioned or semi-conditioned loading areas dominate the thermal interface.",
                    tad_action="VALIDATE_LOSS_PATTERN",
                )
            )

    return rows


def build_activated_pattern_register(
    *,
    loss_pattern_hypothesis_register: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    return [
        {
            "pattern_name": text(row.get("pattern_name")),
            "system_domain": text(row.get("system_domain")),
            "applicability": text(row.get("applicability")),
            "evidence_state": text(row.get("evidence_state")),
            "why_plausible": text(row.get("why_plausible")),
            "tad_action": text(row.get("tad_action")),
        }
        for row in list(loss_pattern_hypothesis_register or [])
        if text(row.get("pattern_name"))
    ]


def build_pattern_discrimination_register(
    *,
    loss_pattern_hypothesis_register: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    return [
        {
            "pattern_name": text(row.get("pattern_name")),
            "hypothesis": text(row.get("hypothesis")),
            "what_confirms": list(row.get("what_confirms", []) or []),
            "what_falsifies": list(row.get("what_falsifies", []) or []),
            "evidence_needed": list(row.get("minimum_local_evidence", []) or []),
            "tad_action": text(row.get("tad_action")),
            "evidence_state": text(row.get("evidence_state")),
        }
        for row in list(loss_pattern_hypothesis_register or [])
        if text(row.get("pattern_name"))
    ]


def build_industrial_common_sense_register(
    *,
    asset_family_research_profile: dict[str, Any],
    operational_intake_pack: dict[str, Any],
) -> list[dict[str, Any]]:
    asset_family = text(asset_family_research_profile.get("asset_family"))
    if _route_state(asset_family_research_profile) != "operational_asset_candidate":
        return []

    maintenance_state = _pack_state(operational_intake_pack, "maintenance_maturity_pack")
    if asset_family == "commercial_building":
        return [
            {
                "heuristic": "Do not call the problem an efficiency problem before you know whether the owner controls the dominant load.",
                "evidence_state": "ARCHETYPAL_PRIOR",
                "why_it_matters": "Control-boundary mistakes can make a technically plausible retrofit economically irrelevant to the owner.",
                "what_to_request": ["tenant metering map", "lease responsibility matrix", "utility bills"],
                "prohibited_language": "Do not say the building has owner-capturable waste just because benchmark data is visible.",
            },
            {
                "heuristic": "Absence of BMS trends or tenant schedule evidence does not prove bad control; it blocks dismissal of schedule waste as a driver.",
                "evidence_state": "ARCHETYPAL_PRIOR",
                "why_it_matters": "Public-only screening cannot falsify after-hours control waste by itself.",
                "what_to_request": ["BMS trend logs", "after-hours occupancy profile"],
                "prohibited_language": "Do not diagnose control failure as observed fact without local evidence.",
            },
        ]
    if asset_family in {"industrial_manufacturing", "thermal_process_site", "utility_heavy_site", "infrastructure_node"}:
        return [
            {
                "heuristic": "Do not call high intensity waste before throughput, product mix or thermal duty are normalized.",
                "evidence_state": "ARCHETYPAL_PRIOR",
                "why_it_matters": "Process duty may be structural and economically rational even when headline consumption looks high.",
                "what_to_request": ["throughput by shift", "process map", "utility bills"],
                "prohibited_language": "Do not call a plant inefficient from kWh totals alone.",
            },
            {
                "heuristic": "If maintenance maturity is not evidenced, downtime economics may be more important than direct energy savings.",
                "evidence_state": "ARCHETYPAL_PRIOR" if maintenance_state != "partially_evidenced" else "CONDITIONAL_HYPOTHESIS",
                "why_it_matters": "Reactive maintenance can turn a utility problem into a margin, scrap or uptime problem.",
                "what_to_request": ["maintenance logs", "downtime records", "critical-spares evidence"],
                "prohibited_language": "Do not dismiss maintenance as secondary just because energy is visible in bills.",
            },
        ]
    return [
        {
            "heuristic": "Do not compare warehouses or service assets by area before service intensity and schedule complexity are normalized.",
            "evidence_state": "ARCHETYPAL_PRIOR",
            "why_it_matters": "Operational intensity can dominate the cost story more than area or nominal asset type.",
            "what_to_request": ["service-level proxy", "dock activity profile", "charging schedule"],
            "prohibited_language": "Do not call a warehouse inefficient from area-normalized energy alone.",
        }
    ]
