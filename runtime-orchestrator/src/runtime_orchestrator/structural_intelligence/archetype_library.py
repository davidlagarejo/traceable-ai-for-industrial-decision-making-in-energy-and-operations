from __future__ import annotations

from typing import Any

from .schemas import (
    ArchetypeDefinition,
    ArchetypeResolution,
    ArchetypeSelectionBasis,
    DominantVariableHypothesis,
    EvidenceBoundField,
    StructuralEvidenceState,
)


def _driver(
    variable: str,
    layer: str,
    why_it_could_matter: str,
    *,
    what_confirms_it: list[str],
    what_falsifies_it: list[str],
    decision_impact: list[str],
    dominance: str = "candidate_dominant",
) -> DominantVariableHypothesis:
    return DominantVariableHypothesis(
        variable=variable,
        layer=layer,
        dominance=dominance,
        evidence_state=StructuralEvidenceState.ARCHETYPAL_PRIOR,
        why_it_could_matter=why_it_could_matter,
        what_confirms_it=what_confirms_it,
        what_falsifies_it=what_falsifies_it,
        decision_impact=decision_impact,
    )


def _field(field_name: str, value: Any, falsification_condition: str, minimum_evidence_required: list[str]) -> EvidenceBoundField:
    return EvidenceBoundField(
        field_name=field_name,
        value=value,
        evidence_state=StructuralEvidenceState.ARCHETYPAL_PRIOR,
        falsification_condition=falsification_condition,
        minimum_evidence_required=minimum_evidence_required,
    )


ARCHETYPE_LIBRARY: dict[str, ArchetypeDefinition] = {
    "target_not_yet_structurally_modelable": ArchetypeDefinition(
        archetype_id="target_not_yet_structurally_modelable",
        label="Target Not Yet Structurally Modelable",
        asset_type="unresolved_target",
        business_function="Structural modeling is premature until the target is confirmed as a physical operating asset.",
        value_creation_mechanism="Unknown until the system confirms asset identity and operating substrate.",
        dominant_process_type="unknown",
        dominant_physical_drivers=[],
        dominant_operational_drivers=[],
        control_structure="Unresolved.",
        constraint_structure="Target identity and asset boundary remain unresolved.",
        economic_driver="Do not assign one yet.",
        regulatory_exposure="Unknown until physical target resolution.",
        minimum_evidence_required=[
            "physical asset confirmation",
            "asset-level address and boundary evidence",
            "operating substrate confirmation",
        ],
        dominant_variable_hypotheses=[],
    ),
    "commercial_building_generic": ArchetypeDefinition(
        archetype_id="commercial_building_generic",
        label="Commercial Building Generic",
        asset_type="commercial_building",
        business_function="Provide usable conditioned space and capture value through occupancy, rent, and base-building operations.",
        value_creation_mechanism="Owner economics depend on controllable base-building systems, operating schedule, and contractual allocation of energy and compliance burdens.",
        dominant_process_type="base-building conditioning and occupied-space operations",
        dominant_physical_drivers=["hvac_duty", "operating_schedule", "tenant_loads", "fuel_mix"],
        dominant_operational_drivers=["control_boundary", "metering_topology", "schedule_discipline", "maintenance_tuning"],
        control_structure="Owner control must be separated from tenant-driven loads and third-party operators.",
        constraint_structure="Utility metering, lease terms, occupancy pattern, and jurisdiction-specific compliance rules constrain action.",
        economic_driver="Operating cost position and rent resilience depend on whether major loads are owner-controllable.",
        regulatory_exposure="Building performance regulation may matter, but applicability must be observed, not assumed.",
        critical_systems=["hvac", "lighting_controls", "metering", "bms_or_ems"],
        operational_risks=["after_hours_load_blind_spot", "metering_gap", "owner_control_mismatch"],
        regulatory_risks=["mis-scoped_compliance_strategy"],
        relevant_metrics=["utility_baseline", "EUI", "fuel_mix", "operating_schedule"],
        comparable_lenses=["owner-control boundary", "base-building vs tenant load split", "peer building operating profile"],
        minimum_evidence_required=["utility bills", "meter map", "HVAC/BMS topology", "lease responsibility matrix"],
        dominant_variable_hypotheses=[
            _driver(
                "utility_baseline",
                "energy",
                "Load shape determines whether building-level screening reflects real controllable economics.",
                what_confirms_it=["12-month utility bills", "interval data"],
                what_falsifies_it=["metering gap showing incomplete building coverage"],
                decision_impact=["screening admissibility", "retrofit gating"],
            ),
            _driver(
                "control_boundary",
                "control",
                "Owner economics weaken if major loads sit outside owner control.",
                what_confirms_it=["lease responsibility matrix", "metering map"],
                what_falsifies_it=["full owner-controlled base-building load boundary"],
                decision_impact=["retrofit economics", "compliance burden allocation"],
            ),
        ],
    ),
    "commercial_office_tower_nyc": ArchetypeDefinition(
        archetype_id="commercial_office_tower_nyc",
        label="Commercial Office Tower NYC",
        asset_type="commercial_building",
        business_function="Operate a premium urban office tower under NYC disclosure and emissions rules.",
        value_creation_mechanism="Value depends on occupancy, rent durability, owner-managed base-building performance, and the ability to navigate LL84/LL97 exposure.",
        dominant_process_type="high-rise office tower base-building and tenant-serving operations",
        dominant_physical_drivers=["central_plant_duty", "tenant_load_profile", "after_hours_occupancy", "fuel_mix"],
        dominant_operational_drivers=["BMS_tuning", "tenant_metering", "lease_responsibility", "LL97_pathway"],
        control_structure="Owner likely controls base-building systems, but tenant loads and lease design can dominate realized value.",
        constraint_structure="LL84/LL97, utility metering topology, tenant schedule, and central-plant configuration jointly constrain action.",
        economic_driver="Capital logic may be driven by penalty avoidance, owner-controllable savings, or both.",
        regulatory_exposure="NYC LL84 and LL97 covered-building exposure is a first-order structural constraint.",
        critical_systems=["central_plant", "airside_HVAC", "tenant_metering", "BMS_or_EMS", "vertical_transport"],
        operational_risks=["tenant-driven_after-hours_load", "base-building vs tenant split ambiguity", "central-plant baseload"],
        regulatory_risks=["mis-framed_LL97_capital_logic", "filing-pathway mismatch"],
        relevant_metrics=["LL84 EUI", "LL97 exposure", "utility baseline", "after-hours occupancy"],
        comparable_lenses=["Class A NYC covered towers", "central-plant control boundary", "green lease strategy"],
        minimum_evidence_required=["LL84 and LL97 records", "utility bills", "tenant metering map", "lease responsibility matrix", "BMS / central plant topology"],
        dominant_variable_hypotheses=[
            _driver(
                "central_plant",
                "physical",
                "If a central plant dominates the base-building load, owner-managed optimization may be investable.",
                what_confirms_it=["central plant topology", "BMS trend logs", "plant equipment inventory"],
                what_falsifies_it=["distributed or tenant-dominant load structure"],
                decision_impact=["retrofit admissibility", "screening posture", "owner-controllable upside"],
            ),
            _driver(
                "tenant_metering",
                "control",
                "Metering determines whether apparent building energy intensity can be translated into owner economics.",
                what_confirms_it=["tenant submetering map", "billing allocation logic"],
                what_falsifies_it=["single owner meter with fully owner-controlled systems"],
                decision_impact=["compliance strategy", "retrofit economics", "green lease redesign"],
            ),
            _driver(
                "after_hours_occupancy",
                "operation",
                "After-hours tenant usage can turn a nominal base-building issue into a tenant behavior issue.",
                what_confirms_it=["after-hours badge or occupancy profile", "BMS schedules", "tenant operating schedule"],
                what_falsifies_it=["strict schedule adherence with low after-hours load"],
                decision_impact=["BMS tuning", "tenant engagement", "load interpretation"],
            ),
            _driver(
                "LL97_pathway",
                "regulation",
                "Capital logic may be driven by penalty avoidance rather than pure savings.",
                what_confirms_it=["LL97 filing basis", "emissions baseline", "covered-building pathway"],
                what_falsifies_it=["no material penalty exposure under official filing"],
                decision_impact=["compliance investment", "electrification framing", "procurement strategy"],
            ),
        ],
    ),
    "manufacturing_generic": ArchetypeDefinition(
        archetype_id="manufacturing_generic",
        label="Manufacturing Generic",
        asset_type="manufacturing_facility",
        business_function="Convert material inputs into sellable output through repeatable process operations.",
        value_creation_mechanism="Economics depend on throughput, yield, uptime, process discipline, and support-system efficiency.",
        dominant_process_type="production process with support utilities",
        dominant_physical_drivers=["throughput", "thermal_duty", "motors_and_drives", "compressed_air"],
        dominant_operational_drivers=["downtime", "product_mix", "maintenance_discipline", "shift_pattern"],
        control_structure="Operator control boundary must distinguish process load from support-system waste and outsourced services.",
        constraint_structure="Production schedule, maintenance windows, permits, and utility/tariff structure constrain intervention.",
        economic_driver="Bad process framing can misallocate capital between process redesign, maintenance, and support-system efficiency.",
        regulatory_exposure="Permits and emissions context can shape feasible redesign paths.",
        critical_systems=["process equipment", "compressed_air", "motors_and_drives", "thermal utilities"],
        operational_risks=["structural_process_load_misread_as_waste", "downtime-hidden cost", "throughput variability"],
        regulatory_risks=["permit-constrained redesign"],
        relevant_metrics=["throughput", "downtime", "utility baseline", "product mix"],
        comparable_lenses=["yield and scrap profile", "maintenance discipline", "support-system intensity"],
        minimum_evidence_required=["process map", "utility bills", "throughput by shift", "equipment inventory", "downtime logs", "permit records"],
        dominant_variable_hypotheses=[
            _driver(
                "throughput",
                "operation",
                "Throughput can dominate energy intensity and invalidate waste assumptions.",
                what_confirms_it=["throughput by shift", "production log"],
                what_falsifies_it=["flat output with highly variable energy use"],
                decision_impact=["energy framing", "process redesign vs support-system focus"],
            ),
            _driver(
                "downtime",
                "maintenance",
                "Downtime can dominate economics even when energy is visible first.",
                what_confirms_it=["downtime log", "failure history", "maintenance work orders"],
                what_falsifies_it=["stable high availability with low outage cost"],
                decision_impact=["maintenance priority", "capital sequencing"],
            ),
        ],
    ),
    "manufacturing_laminate": ArchetypeDefinition(
        archetype_id="manufacturing_laminate",
        label="Manufacturing Laminate",
        asset_type="manufacturing_facility",
        business_function="Produce laminate output through thermal-mechanical conversion, resin handling, pressing, curing, and finishing operations.",
        value_creation_mechanism="Economics depend on throughput, thermal duty, resin/curing discipline, uptime, scrap, and emissions-constrained operation.",
        dominant_process_type="thermal-mechanical laminate production",
        dominant_physical_drivers=["throughput", "thermal_duty", "resin_curing_profile", "pressing_duty", "compressed_air"],
        dominant_operational_drivers=["downtime", "scrap_rate", "shift_pattern", "maintenance_windows"],
        control_structure="Operator must distinguish structural process load from support-system waste and compliance-driven operating limits.",
        constraint_structure="Air permits, VOC controls, production schedule, and maintenance access jointly constrain redesign.",
        economic_driver="Energy CAPEX may fail if thermal duty is structural or if downtime/scrap dominates economics.",
        regulatory_exposure="Air permit, VOC, and emissions-control obligations can dominate feasible process changes.",
        critical_systems=["presses", "curing_or_process_heat", "resin_handling", "compressed_air", "dust_or_voc_control", "material_handling"],
        operational_risks=["structural_thermal_load_misread_as_waste", "resin_cure instability", "downtime and scrap hidden in energy framing"],
        regulatory_risks=["VOC-control constraint", "permit-limited process change"],
        relevant_metrics=["throughput", "shift profile", "scrap rate", "downtime", "utility baseline", "permit obligations"],
        comparable_lenses=["thermal integration", "compressed-air discipline", "yield and scrap", "maintenance uptime"],
        minimum_evidence_required=["process map", "utility bills", "throughput by shift", "equipment inventory", "TCEQ/EPA permits", "downtime logs"],
        dominant_variable_hypotheses=[
            _driver(
                "throughput",
                "operation",
                "Laminate energy intensity may track output more than waste.",
                what_confirms_it=["throughput by shift", "production mix log"],
                what_falsifies_it=["flat throughput with large energy swings"],
                decision_impact=["process redesign", "savings admissibility", "screening interpretation"],
            ),
            _driver(
                "thermal_duty",
                "physical",
                "Process heat and curing can dominate both energy and emissions behavior.",
                what_confirms_it=["process map", "thermal equipment inventory", "fuel and utility profile"],
                what_falsifies_it=["support-system loads dominate over process heat"],
                decision_impact=["thermal integration hypothesis", "permit-driven capital logic"],
            ),
            _driver(
                "resin_curing_profile",
                "physical",
                "Resin formulation and cure window can make the process structurally energy-intensive.",
                what_confirms_it=["process recipe or resin profile", "quality/yield linkage"],
                what_falsifies_it=["product line without cure-sensitive energy dependence"],
                decision_impact=["process redesign", "quality-risk framing"],
            ),
            _driver(
                "compressed_air",
                "support_system",
                "Support-system waste may matter, but only after process load is bounded.",
                what_confirms_it=["compressor map", "air leak survey", "load profile"],
                what_falsifies_it=["minor compressed-air share relative to process heat"],
                decision_impact=["targeted utility optimization", "maintenance actions"],
            ),
            _driver(
                "downtime",
                "maintenance",
                "Maintenance and uptime may dominate value even when energy is visible first.",
                what_confirms_it=["downtime log", "failure history", "spare-parts lead time"],
                what_falsifies_it=["stable uptime with low outage cost"],
                decision_impact=["maintenance redesign", "capital sequencing", "peer comparison"],
            ),
        ],
    ),
    "logistics_warehouse_generic": ArchetypeDefinition(
        archetype_id="logistics_warehouse_generic",
        label="Logistics Warehouse Generic",
        asset_type="warehouse_distribution",
        business_function="Move, store, stage, and dispatch goods against service-level commitments.",
        value_creation_mechanism="Economics depend on movement intensity, dock utilization, charging profile, labor-service rhythm, and schedule discipline more than area alone.",
        dominant_process_type="warehouse movement, handling, staging, and dispatch operations",
        dominant_physical_drivers=["movement_intensity", "forklift_or_mhe_duty", "charging_profile", "temperature_duty_if_present"],
        dominant_operational_drivers=["service_level_complexity", "dock_activity_profile", "schedule_congestion", "control_boundary"],
        control_structure="Operator control must be separated from landlord/common-area assumptions and from outsourced fleet or service duties.",
        constraint_structure="Service windows, dock logic, charging schedule, tenant/operator boundary, and tariff exposure jointly constrain action.",
        economic_driver="Bad comparison logic can misdiagnose a service-intensity system as simple area-based inefficiency.",
        regulatory_exposure="Safety, refrigeration, or fleet-related obligations may matter depending on local operating context, but should not be assumed closed.",
        critical_systems=["material_handling_equipment", "charging_or_fuel_systems", "dock_operations", "lighting_controls", "metering_boundary"],
        operational_risks=["area_benchmark_false_positive", "charging_schedule_blind_spot", "dock_intensity_hidden_cost"],
        regulatory_risks=["mis-scoped_operational_boundary"],
        relevant_metrics=["service_level_proxy", "dock turns", "charging profile", "utility baseline", "operating schedule"],
        comparable_lenses=["service intensity", "dock and dispatch rhythm", "charging-duty normalization", "control boundary"],
        minimum_evidence_required=["service-level proxy", "operating schedule", "equipment inventory", "metering boundary", "dock activity profile"],
        dominant_variable_hypotheses=[
            _driver(
                "service_level_complexity",
                "operation",
                "Area-based benchmarking can fail if service intensity rather than area drives the economics.",
                what_confirms_it=["service-level proxy", "dock activity profile", "throughput or dispatch records"],
                what_falsifies_it=["flat service rhythm with low movement intensity"],
                decision_impact=["fair comparison", "measurement minimality", "CAPEX timing"],
            ),
            _driver(
                "charging_profile",
                "physical",
                "Material-handling charging windows can dominate visible electricity patterns without implying generic waste.",
                what_confirms_it=["forklift or MHE inventory", "charging schedule", "meter interval context"],
                what_falsifies_it=["negligible electric handling fleet or fuel-based handling only"],
                decision_impact=["tariff logic", "peak-demand framing", "measurement strategy"],
            ),
            _driver(
                "control_boundary",
                "control",
                "Warehouse economics weaken if the actor facing the cost does not control the duty boundary that matters.",
                what_confirms_it=["operator responsibility map", "metering boundary", "lease or service allocation"],
                what_falsifies_it=["single operator-controlled duty boundary"],
                decision_impact=["owner-vs-operator logic", "peer validity", "investment gating"],
            ),
        ],
    ),
    "cold_chain_generic": ArchetypeDefinition(
        archetype_id="cold_chain_generic",
        label="Cold Chain Generic",
        asset_type="cold_chain_facility",
        business_function="Preserve temperature-sensitive goods through storage, handling, and dispatch under controlled thermal conditions.",
        value_creation_mechanism="Economics depend on refrigeration duty, infiltration control, service rhythm, product temperature requirements, and uptime discipline.",
        dominant_process_type="temperature-controlled storage and dispatch operations",
        dominant_physical_drivers=["refrigeration_duty", "temperature_band_requirement", "infiltration_load", "defrost_profile"],
        dominant_operational_drivers=["door_traffic", "service_level_complexity", "maintenance_discipline", "control_boundary"],
        control_structure="The operator must distinguish unavoidable refrigeration duty from avoidable schedule, infiltration, or maintenance-driven losses.",
        constraint_structure="Temperature commitments, food or pharma operating discipline, service windows, and maintenance access constrain intervention.",
        economic_driver="Visible energy intensity can reflect thermal duty and service complexity rather than generic inefficiency.",
        regulatory_exposure="Food safety, cold-chain integrity, or sector-specific compliance can constrain scheduling and redesign options.",
        critical_systems=["refrigeration_plant", "evaporators_and_defrost", "door_and_loading_interfaces", "controls", "metering_boundary"],
        operational_risks=["refrigeration_duty_misread_as_waste", "infiltration_hidden_cost", "maintenance-driven_temperature_drift"],
        regulatory_risks=["cold-chain_integrity_constraint"],
        relevant_metrics=["temperature-duty map", "door traffic profile", "refrigeration inventory", "defrost schedule", "utility baseline"],
        comparable_lenses=["temperature band", "door traffic intensity", "refrigeration architecture", "control boundary"],
        minimum_evidence_required=["temperature bands", "door traffic profile", "refrigeration inventory", "defrost schedule", "operating schedule"],
        dominant_variable_hypotheses=[
            _driver(
                "refrigeration_duty",
                "physical",
                "Total site energy can be structurally dominated by refrigeration duty rather than generic building or warehouse inefficiency.",
                what_confirms_it=["refrigeration inventory", "temperature-duty map", "controls or defrost schedule"],
                what_falsifies_it=["minor refrigeration share relative to non-thermal loads"],
                decision_impact=["fair comparison", "capital targeting", "measurement minimality"],
            ),
            _driver(
                "door_traffic_profile",
                "operation",
                "Door activity and service rhythm can dominate infiltration losses and distort simplistic benchmarks.",
                what_confirms_it=["door traffic log", "dispatch schedule", "loading activity profile"],
                what_falsifies_it=["low door-cycle intensity with stable thermal envelope duty"],
                decision_impact=["infiltration logic", "maintenance and controls priority", "peer validity"],
            ),
            _driver(
                "control_boundary",
                "control",
                "The burdened actor may still not control the thermal and service boundary that drives the visible cost.",
                what_confirms_it=["operator responsibility map", "metering boundary", "service allocation evidence"],
                what_falsifies_it=["single operator-controlled refrigeration and service boundary"],
                decision_impact=["investment gating", "comparison validity", "owner-vs-operator logic"],
            ),
        ],
    ),
    "utility_heavy_site_generic": ArchetypeDefinition(
        archetype_id="utility_heavy_site_generic",
        label="Utility-Heavy Site Generic",
        asset_type="utility_heavy_site",
        business_function="Generate, condition, or route utility-intensive support services that can dominate site economics without being the main product themselves.",
        value_creation_mechanism="Economics depend on demand structure, PF or reactive exposure, major-motor duty, compressor or pumping sequencing, and maintenance discipline more than aggregate kWh alone.",
        dominant_process_type="support-utility generation, motive-power duty and distribution support",
        dominant_physical_drivers=["demand_structure", "pf_or_reactive_exposure", "major_motor_duty", "support_system_sequencing"],
        dominant_operational_drivers=["support_system_dispatch", "maintenance_discipline", "control_logic", "metering_boundary"],
        control_structure="The operator must separate structural support-duty from avoidable sequencing, PF, or support-system loss before funding broad consumption CAPEX.",
        constraint_structure="Tariff structure, demand windows, support-duty obligations, maintenance access and local control logic jointly constrain action.",
        economic_driver="Visible utility burden can be dominated by demand, PF, reactive structure or support-duty rhythm rather than total consumption alone.",
        regulatory_exposure="Electrical-service conditions, support-utility oversight, and reliability obligations may constrain which correction paths are admissible.",
        critical_systems=["large_motors_and_drives", "compressors_or_pumps", "distribution_and_mcc", "metering_and_controls"],
        operational_risks=["consumption_false_front", "demand_pf_false_priority", "maintenance_driven_peak_or_drift"],
        regulatory_risks=["mis-scoped_service_or_metering_constraint"],
        relevant_metrics=["demand profile", "PF or reactive exposure", "major motor inventory", "support-duty schedule", "maintenance history"],
        comparable_lenses=["demand structure", "PF / reactive exposure", "support-system duty", "major motor intensity"],
        minimum_evidence_required=["utility bills", "tariff structure", "major motor or compressor inventory", "support-duty schedule", "maintenance evidence"],
        dominant_variable_hypotheses=[
            _driver(
                "demand_structure",
                "finance",
                "Demand, PF or reactive structure can dominate the economics even when aggregate consumption looks like the obvious problem.",
                what_confirms_it=["utility bills", "tariff structure", "interval demand evidence"],
                what_falsifies_it=["flat tariff structure with immaterial demand or PF exposure"],
                decision_impact=["tariff-aware control", "sequencing logic", "measurement strategy"],
            ),
            _driver(
                "support_system_duty",
                "operation",
                "Support-system duty can be structural and economically rational, so visible utility burden is not automatically waste.",
                what_confirms_it=["major motor inventory", "support-duty schedule", "metering boundary"],
                what_falsifies_it=["minor support-duty share relative to a different dominant process or service driver"],
                decision_impact=["fair comparison", "capital sequencing", "loss discrimination"],
            ),
            _driver(
                "maintenance_discipline",
                "maintenance",
                "Maintenance discipline can drive peaks, instability and downtime economics that are easily misread as pure utility inefficiency.",
                what_confirms_it=["maintenance logs", "CMMS history", "repeat failure evidence"],
                what_falsifies_it=["stable PM-backed operation with no recurring utility-support failures"],
                decision_impact=["maintenance redesign", "targeted correction", "CAPEX gating"],
            ),
        ],
    ),
    "infrastructure_node_generic": ArchetypeDefinition(
        archetype_id="infrastructure_node_generic",
        label="Infrastructure Node Generic",
        asset_type="infrastructure_node",
        business_function="Convert, route, dispatch or support network service under continuity and reliability obligations.",
        value_creation_mechanism="Economics depend on service continuity, dispatch burden, redundancy posture, tariff structure and major-equipment reliability more than simple average energy intensity.",
        dominant_process_type="node-level conversion, routing and continuity support",
        dominant_physical_drivers=["service_continuity_burden", "demand_structure", "major_equipment_duty", "redundancy_class"],
        dominant_operational_drivers=["dispatch_logic", "switching_practice", "maintenance_discipline", "control_boundary"],
        control_structure="The operator must separate unavoidable continuity duty from avoidable operating or sequencing loss.",
        constraint_structure="Service obligations, dispatch logic, redundancy requirements, tariff structure and maintenance access jointly constrain action.",
        economic_driver="Bad comparison logic can mistake continuity burden or redundancy posture for generic inefficiency.",
        regulatory_exposure="Safety, service-continuity or node-level operating rules may constrain what optimization is admissible.",
        critical_systems=["power_conversion", "dispatch_controls", "redundancy_backup", "metering_and_protection"],
        operational_risks=["continuity_duty_misread_as_waste", "demand_structure_false_positive", "reliability_vs_tariff_conflict"],
        regulatory_risks=["mis-scoped_service_constraint"],
        relevant_metrics=["service_continuity_profile", "dispatch burden", "demand profile", "utility baseline", "outage or maintenance history"],
        comparable_lenses=["service continuity burden", "dispatch intensity", "redundancy class", "tariff structure"],
        minimum_evidence_required=["utility bills", "tariff structure", "service continuity or dispatch logs", "equipment inventory", "maintenance evidence"],
        dominant_variable_hypotheses=[
            _driver(
                "service_continuity_burden",
                "operation",
                "Average energy can mislead if continuity duty rather than avoidable waste dominates the node economics.",
                what_confirms_it=["service continuity profile", "dispatch or uptime logs", "operating obligation evidence"],
                what_falsifies_it=["low continuity burden with flexible dispatch and low uptime sensitivity"],
                decision_impact=["fair comparison", "capital sequencing", "measurement minimality"],
            ),
            _driver(
                "demand_structure",
                "finance",
                "Demand, PF and tariff structure may dominate the visible cost logic more than aggregate consumption.",
                what_confirms_it=["utility bills", "tariff structure", "interval demand evidence"],
                what_falsifies_it=["flat tariff structure with immaterial demand or PF exposure"],
                decision_impact=["tariff-aware control", "PF or sequencing logic", "measurement strategy"],
            ),
            _driver(
                "redundancy_class",
                "control",
                "Redundancy and reliability obligations can make some energy or demand burdens structurally rational.",
                what_confirms_it=["backup configuration", "switching or dispatch rules", "reliability or outage evidence"],
                what_falsifies_it=["minimal redundancy requirement with flexible service posture"],
                decision_impact=["reliability-aware redesign", "peer validity", "CAPEX gating"],
            ),
        ],
    ),
}


_TARGET_TYPE_FALLBACKS: dict[str, str] = {
    "commercial_building": "commercial_building_generic",
    "manufacturing_facility": "manufacturing_generic",
    "warehouse_distribution": "logistics_warehouse_generic",
    "cold_chain_facility": "cold_chain_generic",
    "utility_heavy_site": "utility_heavy_site_generic",
    "infrastructure_node": "infrastructure_node_generic",
}


def _has_nyc_tower_signal(asset_name: str, asset_fields: list[dict[str, Any]]) -> bool:
    name = asset_name.lower()
    if "tower" in name or "vanderbilt" in name:
        return True
    for row in asset_fields:
        field_name = str(row.get("field", "")).strip().lower()
        value = str(row.get("value", "")).strip()
        if field_name == "floor_count":
            try:
                if float(value) >= 20:
                    return True
            except ValueError:
                continue
        if field_name in {"gfa", "gross_floor_area"}:
            digits = "".join(ch for ch in value if ch.isdigit())
            if digits and int(digits) >= 250000:
                return True
    return False


def _source_type_set(source_register: list[dict[str, Any]], dataset_coverage_register: list[dict[str, Any]]) -> set[str]:
    values: set[str] = set()
    for row in source_register:
        for key in ("source_type", "source_family", "source_id", "title"):
            value = str(row.get(key, "")).strip().lower()
            if value:
                values.add(value)
    for row in dataset_coverage_register:
        value = str(row.get("dataset_key", "")).strip().lower()
        if value:
            values.add(value)
    return values


def _hint_text(asset_name: str, asset_fields: list[dict[str, Any]]) -> str:
    parts = [asset_name]
    for row in asset_fields:
        field_name = str(row.get("field", "")).strip().lower()
        if field_name in {"process_flow", "load_driver", "asset_name", "asset_class", "operating_schedule"}:
            parts.append(str(row.get("value", "")))
    return " ".join(parts).lower()


def _basis(dimension: str, value: str, source: str) -> ArchetypeSelectionBasis:
    return ArchetypeSelectionBasis(
        dimension=dimension,
        value=value,
        evidence_state=StructuralEvidenceState.OBSERVED_FACT,
        source=source,
    )


def resolve_archetype(
    *,
    target_definition: dict[str, Any],
    target_classification_object: dict[str, Any],
    facility_prior: dict[str, Any],
    asset_field_register: list[dict[str, Any]],
    dataset_coverage_register: list[dict[str, Any]],
    source_register: list[dict[str, Any]],
) -> dict[str, Any]:
    target_type = str(target_definition.get("target_type", "")).strip().lower()
    target_classification = str(target_classification_object.get("target_type", "")).strip().upper()
    jurisdictions = [str(code).strip().upper() for code in target_definition.get("jurisdiction_scope", []) if str(code).strip()]
    asset_name = str(
        facility_prior.get("asset_name")
        or target_definition.get("target_name")
        or target_definition.get("target_label")
        or ""
    ).strip()
    hints = _hint_text(asset_name, asset_field_register)
    seen_sources = _source_type_set(source_register, dataset_coverage_register)

    basis_register: list[ArchetypeSelectionBasis] = []
    if target_type:
        basis_register.append(_basis("target_type", target_type, "target_definition.target_type"))
    if target_classification:
        basis_register.append(_basis("target_classification", target_classification, "motor_007.target_classification_object"))
    if jurisdictions:
        basis_register.append(_basis("jurisdiction_scope", ", ".join(jurisdictions), "target_definition.jurisdiction_scope"))

    if target_classification in {"CORPORATE_HEADQUARTERS", "REGISTERED_AGENT_OR_MAILING_ADDRESS", "AMBIGUOUS_TARGET"}:
        selected_id = "target_not_yet_structurally_modelable"
        confidence = "high" if target_classification != "AMBIGUOUS_TARGET" else "medium"
        why_selected = "Target classification does not yet support structural modeling of a physical operating asset."
        resolver_state = "non_operating_or_unresolved_target"
    elif (
        target_type == "commercial_building"
        and any(code.startswith("US-NY-NYC") for code in jurisdictions)
        and _has_nyc_tower_signal(asset_name, asset_field_register)
    ):
        selected_id = "commercial_office_tower_nyc"
        confidence = "high"
        why_selected = "Observed NYC jurisdiction plus tower-scale signals activate the bounded NYC office tower archetype."
        resolver_state = "selected"
        basis_register.append(_basis("tower_scale_signal", "nyc high-rise signal observed", "asset_field_register / asset_name"))
    elif target_type == "manufacturing_facility" and any(token in hints for token in ("laminate", "resin", "curing", "press", "pressing")):
        selected_id = "manufacturing_laminate"
        confidence = "high"
        why_selected = "Observed public process clues align with laminate manufacturing without claiming process truth."
        resolver_state = "selected"
        basis_register.append(_basis("process_clues", "laminate / resin / curing public clues observed", "asset_field_register"))
    elif target_type in {"industrial_plant", "utility_heavy_site"} and any(
        token in hints
        for token in (
            "utility heavy",
            "utility_heavy",
            "central utility",
            "utility island",
            "power factor",
            "reactive",
            "compressor house",
            "large motor",
            "cooling water pump",
            "motor control center",
        )
    ):
        selected_id = "utility_heavy_site_generic"
        confidence = "high"
        why_selected = "Observed utility-heavy operating clues support a bounded utility-heavy archetype without claiming local performance closure."
        resolver_state = "selected"
        basis_register.append(_basis("utility_heavy_clues", "utility-heavy duty and support-system signals observed", "asset_field_register"))
    elif target_type == "commercial_building" and any(code.startswith("US-NY-NYC") for code in jurisdictions) and (
        "nyc_ll84_energy_benchmarking" in seen_sources
        or "nyc_pluto_property" in seen_sources
        or "nyc_dof_property_record" in seen_sources
    ):
        selected_id = "commercial_building_generic"
        confidence = "medium"
        why_selected = "Observed NYC commercial-building routing supports a building archetype, but not a stronger tower-specific selection yet."
        resolver_state = "selected"
    else:
        selected_id = _TARGET_TYPE_FALLBACKS.get(target_type, "target_not_yet_structurally_modelable")
        confidence = "medium" if selected_id != "target_not_yet_structurally_modelable" else "low"
        if selected_id == "target_not_yet_structurally_modelable":
            why_selected = "No bounded operating archetype can be chosen without stronger target and process evidence."
            resolver_state = "fallback_unresolved"
        else:
            why_selected = "Target type supports only a generic archetype at the current evidence state."
            resolver_state = "fallback_generic"

    definition = ARCHETYPE_LIBRARY[selected_id]
    resolution = ArchetypeResolution(
        selected_archetype_id=definition.archetype_id,
        label=definition.label,
        match_confidence=confidence,
        resolver_state=resolver_state,
        archetype_evidence_state=StructuralEvidenceState.ARCHETYPAL_PRIOR if selected_id != "target_not_yet_structurally_modelable" else StructuralEvidenceState.INADMISSIBLE_CLAIM,
        why_selected=why_selected,
        selection_basis_register=basis_register,
    )

    system_abstraction_seed = {
        "asset_type": _field(
            "asset_type",
            target_type or "unknown",
            "Target classification or asset-type evidence changes materially.",
            ["target classification evidence", "asset-level operating substrate confirmation"],
        ).to_dict(),
        "business_function": _field(
            "business_function",
            definition.business_function,
            "Observed operating documents contradict the selected business function.",
            definition.minimum_evidence_required,
        ).to_dict(),
        "value_creation_mechanism": _field(
            "value_creation_mechanism",
            definition.value_creation_mechanism,
            "Observed financial and operating evidence shows a different value logic.",
            definition.minimum_evidence_required,
        ).to_dict(),
        "dominant_process_type": _field(
            "dominant_process_type",
            definition.dominant_process_type,
            "Observed process inventory or system topology shows a materially different operating structure.",
            definition.minimum_evidence_required,
        ).to_dict(),
        "dominant_physical_drivers": _field(
            "dominant_physical_drivers",
            definition.dominant_physical_drivers,
            "Observed load-driver evidence shows different physical dominance.",
            definition.minimum_evidence_required,
        ).to_dict(),
        "dominant_operational_drivers": _field(
            "dominant_operational_drivers",
            definition.dominant_operational_drivers,
            "Observed schedule, control, or maintenance evidence shifts the operating bottleneck.",
            definition.minimum_evidence_required,
        ).to_dict(),
        "control_structure": _field(
            "control_structure",
            definition.control_structure,
            "Observed meter maps, contracts, or operator roles show a different control boundary.",
            definition.minimum_evidence_required,
        ).to_dict(),
        "constraint_structure": _field(
            "constraint_structure",
            definition.constraint_structure,
            "Observed regulations, contracts, or process limits show different constraints.",
            definition.minimum_evidence_required,
        ).to_dict(),
        "economic_driver": _field(
            "economic_driver",
            definition.economic_driver,
            "Observed economics show that a different variable dominates value or downside.",
            definition.minimum_evidence_required,
        ).to_dict(),
        "regulatory_exposure": _field(
            "regulatory_exposure",
            definition.regulatory_exposure,
            "Observed filings or permits show different jurisdictional exposure.",
            definition.minimum_evidence_required,
        ).to_dict(),
        "evidence_maturity": _field(
            "evidence_maturity",
            "archetypal_only" if selected_id != "target_not_yet_structurally_modelable" else "not_modelable_yet",
            "Observed asset-specific evidence upgrades or invalidates the archetype.",
            definition.minimum_evidence_required,
        ).to_dict(),
    }

    return {
        "archetype_resolution": resolution.to_dict(),
        "archetype_library_register": [definition.to_dict()],
        "archetype_selection_basis_register": [row.to_dict() for row in basis_register],
        "dominant_variable_hypotheses": [row.to_dict() for row in definition.dominant_variable_hypotheses],
        "archetype_minimum_evidence_register": list(definition.minimum_evidence_required),
        "system_abstraction_seed": system_abstraction_seed,
        "anti_hallucination_contract": {
            "selected_archetype_evidence_state": resolution.archetype_evidence_state.value,
            "rule": "No archetypal prior may be presented as observed fact.",
            "allowed_use": ["hypothesis_structuring", "evidence_request_design", "future structural-intelligence motors"],
            "prohibited_use": ["decision_closure", "ROI claim", "savings claim", "final redesign recommendation"],
        },
    }
