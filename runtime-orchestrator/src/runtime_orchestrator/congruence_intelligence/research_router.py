from __future__ import annotations

from typing import Any

from .research_library import ASSET_FAMILY_RESEARCH_LIBRARY
from .schemas import DILIGENCE_PACK_NAMES, build_diligence_pack, dedupe, list_text, text

_ASSET_FAMILY_LIBRARY = {
    "commercial_building": {
        "authoritative_source_families": [
            "geospatial_public_record",
            "property_record",
            "benchmarking_disclosure_record",
            "regulatory_coverage_record",
            "climate_normals_record",
            "utility_tariff_record",
            "technical_sourcebook_record",
        ],
        "typical_processes": [
            "occupancy and tenant services delivery",
            "central plant / HVAC / lighting / vertical transport support",
            "comfort, compliance, and value preservation",
        ],
        "typical_subsystems": [
            "HVAC / central plant",
            "lighting",
            "vertical transportation",
            "plug and tenant loads",
            "BMS / controls",
            "water and domestic systems",
            "building envelope",
        ],
        "typical_loss_patterns": [
            "owner / tenant control-boundary mismatch",
            "after-hours occupancy / scheduling waste",
            "simultaneous heating and cooling",
            "central plant sequencing inefficiency",
            "missing tenant metering or boundary visibility",
        ],
        "typical_regulatory_signals": [
            "benchmarking and building performance standards",
            "owner filing burden",
            "system-capital and permit history",
        ],
        "typical_measurement_paths": [
            "utility bills",
            "whole-building interval data",
            "tenant metering map",
            "BMS trend logs",
            "central plant topology",
        ],
        "typical_invalid_comparisons": [
            "EUI comparison without matching control boundary",
            "whole-building energy use treated as owner-capturable value without tenant / owner boundary evidence",
        ],
    },
    "industrial_manufacturing": {
        "authoritative_source_families": [
            "geospatial_public_record",
            "regulatory_coverage_record",
            "permit_record",
            "climate_normals_record",
            "utility_tariff_record",
            "technical_sourcebook_record",
            "industry_guidance_record",
        ],
        "typical_processes": [
            "raw material input and storage",
            "process transformation",
            "support systems and utilities",
            "waste streams and finishing",
            "packing and shipping",
        ],
        "typical_subsystems": [
            "process heating / thermal systems",
            "motors / drives / fans / pumps",
            "compressed air",
            "chilled water / cooling",
            "steam / boiler systems",
            "waste handling",
            "material handling / logistics",
        ],
        "typical_loss_patterns": [
            "throughput-normalization error",
            "compressed-air leakage or pressure overuse",
            "thermal and combustion losses",
            "demand / PF / inductive-load exposure",
            "reactive maintenance driving downtime economics",
        ],
        "typical_regulatory_signals": [
            "air / emissions permitting",
            "wastewater or process-water permitting",
            "combustion / boiler oversight",
            "chemical handling or reporting constraints",
        ],
        "typical_measurement_paths": [
            "utility bills",
            "throughput by shift",
            "equipment inventory",
            "process map",
            "demand profile and tariff logic",
            "downtime and maintenance logs",
        ],
        "typical_invalid_comparisons": [
            "kWh per square foot comparison without throughput normalization",
            "benchmarking thermal process loads against non-thermal peers",
            "comparing unlike maintenance maturity or operating schedules",
        ],
    },
    "logistics_warehouse": {
        "authoritative_source_families": [
            "geospatial_public_record",
            "property_record",
            "regulatory_coverage_record",
            "climate_normals_record",
            "utility_tariff_record",
            "industry_guidance_record",
        ],
        "typical_processes": [
            "goods receipt",
            "storage and internal movement",
            "handling / picking / staging",
            "dispatch and service-level delivery",
        ],
        "typical_subsystems": [
            "lighting",
            "HVAC / ventilation",
            "dock and door systems",
            "forklift charging / motive power",
            "sorting and handling systems",
            "cold-room or conditioned storage if present",
        ],
        "typical_loss_patterns": [
            "layout and movement inefficiency",
            "schedule mismatch and idle conditioning",
            "dock-door and infiltration loss",
            "charging schedule and demand spikes",
            "service-level complexity hidden by area-based benchmarks",
        ],
        "typical_regulatory_signals": [
            "building and fire compliance",
            "refrigeration or storage requirements where relevant",
            "vehicle / loading and safety constraints",
        ],
        "typical_measurement_paths": [
            "utility bills",
            "operating schedule",
            "dock activity profile",
            "forklift fleet and charging schedule",
            "storage temperature map if conditioned",
        ],
        "typical_invalid_comparisons": [
            "energy per area without service-level or throughput normalization",
            "cold and non-cold warehouses treated as comparable",
        ],
    },
    "cold_chain": {
        "authoritative_source_families": [
            "geospatial_public_record",
            "property_record",
            "regulatory_coverage_record",
            "climate_normals_record",
            "utility_tariff_record",
            "industry_guidance_record",
            "technical_sourcebook_record",
        ],
        "typical_processes": [
            "temperature-controlled receipt and storage",
            "refrigeration and air-separation support",
            "door / traffic / dispatch management",
        ],
        "typical_subsystems": [
            "refrigeration plant",
            "defrost systems",
            "door and dock systems",
            "lighting",
            "forklift charging",
        ],
        "typical_loss_patterns": [
            "infiltration through doors and traffic patterns",
            "defrost scheduling mismatch",
            "refrigeration setpoint and control mismatch",
            "charging-related demand peaks",
        ],
        "typical_regulatory_signals": [
            "refrigerant management",
            "cold-storage compliance",
            "food-safety or chain-of-custody conditions where relevant",
        ],
        "typical_measurement_paths": [
            "utility bills",
            "refrigeration inventory",
            "temperature bands",
            "door traffic profile",
            "defrost schedule",
        ],
        "typical_invalid_comparisons": [
            "general warehouse benchmark applied to temperature-controlled storage",
        ],
    },
    "thermal_process_site": {
        "authoritative_source_families": [
            "regulatory_coverage_record",
            "permit_record",
            "utility_tariff_record",
            "technical_sourcebook_record",
            "industry_guidance_record",
        ],
        "typical_processes": [
            "fuel input",
            "thermal transformation",
            "heat recovery or heat rejection",
            "process output and finishing",
        ],
        "typical_subsystems": [
            "furnaces / kilns / ovens",
            "boilers / burners",
            "air and combustion systems",
            "heat recovery",
        ],
        "typical_loss_patterns": [
            "combustion and excess-air losses",
            "stack and radiation losses",
            "thermal duty misread as waste",
        ],
        "typical_regulatory_signals": [
            "air permits",
            "combustion equipment oversight",
            "emissions monitoring obligations",
        ],
        "typical_measurement_paths": [
            "fuel bills",
            "combustion test results",
            "duty cycle",
            "process throughput",
        ],
        "typical_invalid_comparisons": [
            "thermal-duty-heavy operations benchmarked against low-thermal peers",
        ],
    },
    "utility_heavy_site": {
        "authoritative_source_families": [
            "utility_tariff_record",
            "technical_sourcebook_record",
            "industry_guidance_record",
        ],
        "typical_processes": [
            "large utility conversion and distribution",
            "support-system heavy operations",
        ],
        "typical_subsystems": [
            "large motors and drives",
            "compressors",
            "pumps and fans",
            "distribution equipment",
        ],
        "typical_loss_patterns": [
            "demand-charge exposure",
            "PF / reactive exposure",
            "sequencing and idle-load waste",
        ],
        "typical_regulatory_signals": [
            "utility service conditions",
            "electrical quality and service constraints",
        ],
        "typical_measurement_paths": [
            "tariff and bill review",
            "demand profile",
            "PF or reactive-charge evidence",
            "major motor inventory",
        ],
        "typical_invalid_comparisons": [
            "energy-consumption-only comparisons that ignore demand and reactive structure",
        ],
    },
    "generic_operational_asset": {
        "authoritative_source_families": [
            "geospatial_public_record",
            "regulatory_coverage_record",
            "climate_normals_record",
            "industry_guidance_record",
        ],
        "typical_processes": [
            "asset-family specific operating logic remains to be bounded",
        ],
        "typical_subsystems": [
            "asset-family specific subsystem logic remains to be bounded",
        ],
        "typical_loss_patterns": [
            "dominant loss logic remains unbounded until asset family and process are clarified",
        ],
        "typical_regulatory_signals": [
            "jurisdictional and permitting context remains screening-grade",
        ],
        "typical_measurement_paths": [
            "start with public records and minimum intake before any deeper instrumentation logic",
        ],
        "typical_invalid_comparisons": [
            "any peer logic before the asset family and operating boundary are bounded",
        ],
    },
}

_ASSET_FAMILY_LIBRARY = ASSET_FAMILY_RESEARCH_LIBRARY

_DILIGENCE_PACK_LIBRARY = {
    "utility_bill_pack": {
        "expected_local_sources": ["utility_bill_record", "meter_interval_record"],
        "binding_tokens": ["bill", "utility", "demand", "pf", "reactive"],
        "public_seed_source_families": [],
        "relevant_families": set(_ASSET_FAMILY_LIBRARY.keys()),
        "family_focus": {
            "commercial_building": "Whole-building charges versus owner-capturable value boundary.",
            "industrial_manufacturing": "Throughput-normalized electric, fuel, and demand structure.",
            "logistics_warehouse": "Base load, charging peaks, and service-level seasonality.",
            "cold_chain": "Refrigeration duty, peak behavior, and seasonal operating profile.",
        },
        "decision_relevance": "First screen for whether economics, tariff burden, or structural load are even decision-relevant.",
        "allowed_without_local_binding": ["screening", "request minimum evidence"],
    },
    "utility_tariff_pack": {
        "expected_local_sources": ["utility_tariff_record", "utility_bill_record"],
        "binding_tokens": ["tariff", "demand", "pf", "reactive"],
        "public_seed_source_families": ["utility_tariff_record"],
        "relevant_families": set(_ASSET_FAMILY_LIBRARY.keys()),
        "family_focus": {
            "industrial_manufacturing": "Tariff logic can dominate CAPEX ranking when inductive or peak-heavy loads exist.",
            "utility_heavy_site": "Demand, PF and service conditions can matter more than aggregate kWh.",
            "cold_chain": "Demand structure may be more material than annualized consumption alone.",
        },
        "decision_relevance": "Prevents consumption-only economics when tariff structure is the real gate.",
        "allowed_without_local_binding": ["tariff-context framing", "bounded demand/PF hypothesis"],
    },
    "throughput_schedule_pack": {
        "expected_local_sources": ["schedule_record", "operator_input_record", "meter_interval_record"],
        "binding_tokens": ["schedule", "shift", "throughput", "occupancy", "traffic", "profile"],
        "public_seed_source_families": [],
        "relevant_families": set(_ASSET_FAMILY_LIBRARY.keys()),
        "family_focus": {
            "commercial_building": "After-hours occupancy and schedule mismatch before deeper retrofit logic.",
            "industrial_manufacturing": "Throughput by shift, product mix and thermal duty before benchmarking.",
            "logistics_warehouse": "Dock activity, movement intensity and service-level rhythm.",
            "cold_chain": "Door traffic, dwell logic and refrigeration duty profile.",
        },
        "decision_relevance": "Separates structural duty from correctable waste.",
        "allowed_without_local_binding": ["bounded schedule hypothesis", "do not compare yet"],
    },
    "equipment_inventory_pack": {
        "expected_local_sources": ["equipment_inventory_record", "operator_input_record"],
        "binding_tokens": ["inventory", "motor", "compressor", "equipment", "refrigeration"],
        "public_seed_source_families": [],
        "relevant_families": {"industrial_manufacturing", "logistics_warehouse", "cold_chain", "thermal_process_site", "utility_heavy_site", "infrastructure_node", "commercial_building"},
        "family_focus": {
            "commercial_building": "Central plant, controls and tenant-load boundary clues.",
            "industrial_manufacturing": "Major process, support-system and motive-power classes.",
            "logistics_warehouse": "Charging, handling, dock, conveyor or conditioned-storage assets.",
            "cold_chain": "Refrigeration plant, defrost logic and conditioned-zone equipment.",
            "infrastructure_node": "Major conversion, dispatch, redundancy and protection assets that define continuity duty.",
        },
        "decision_relevance": "Bounds which systems can plausibly dominate economics or losses.",
        "allowed_without_local_binding": ["research-seeded subsystem hypothesis"],
    },
    "metering_boundary_pack": {
        "expected_local_sources": ["submetering_record", "meter_interval_record", "operator_input_record"],
        "binding_tokens": ["metering", "submeter", "billing responsibility", "boundary"],
        "public_seed_source_families": [],
        "relevant_families": {"commercial_building", "industrial_manufacturing", "logistics_warehouse", "cold_chain"},
        "family_focus": {
            "commercial_building": "Which loads are truly owner-burdened versus tenant-burdened.",
            "industrial_manufacturing": "Which process and support systems share the same economic boundary.",
            "logistics_warehouse": "Whether charging, conditioning or tenant/service loads are blended.",
            "cold_chain": "Whether refrigeration, handling and tenant/service loads are separately visible.",
        },
        "decision_relevance": "Closes the economic and operational boundary before CAPEX logic escalates.",
        "allowed_without_local_binding": ["request control-boundary evidence", "prohibit ROI"],
    },
    "lease_responsibility_pack": {
        "expected_local_sources": ["lease_matrix_record", "operator_input_record"],
        "binding_tokens": ["lease", "tenant", "responsibility", "owner"],
        "public_seed_source_families": [],
        "relevant_families": {"commercial_building", "logistics_warehouse", "cold_chain"},
        "family_focus": {
            "commercial_building": "Maps obligation, control, and savings capture across owner and tenant.",
            "logistics_warehouse": "Separates operator, landlord and tenant responsibility where site use is mixed.",
            "cold_chain": "Clarifies who controls refrigeration, hours and handling constraints.",
        },
        "decision_relevance": "Prevents treating regulated or visible burden as proof of controllable value capture.",
        "allowed_without_local_binding": ["bounded lease-boundary hypothesis", "screening only"],
    },
    "maintenance_proof_pack": {
        "expected_local_sources": ["maintenance_contract_record", "maintenance_log_record", "operator_input_record"],
        "binding_tokens": ["maintenance", "downtime", "pm", "spares"],
        "public_seed_source_families": [],
        "relevant_families": set(_ASSET_FAMILY_LIBRARY.keys()),
        "family_focus": {
            "industrial_manufacturing": "Downtime economics and maintenance maturity may dominate visible energy symptoms.",
            "commercial_building": "Controls and plant maintenance shape whether energy symptoms are drift or duty.",
            "cold_chain": "Refrigeration reliability and maintenance discipline can dominate economics before optimization does.",
        },
        "decision_relevance": "Determines whether the problem is waste, reliability drift, or maintenance under-governance.",
        "allowed_without_local_binding": ["maintenance maturity not evidenced", "request maintenance proof"],
    },
    "bms_or_controls_pack": {
        "expected_local_sources": ["bms_trend_record", "operator_input_record"],
        "binding_tokens": ["bms", "controls", "trend", "topology", "schedule"],
        "public_seed_source_families": [],
        "relevant_families": {"commercial_building", "cold_chain", "industrial_manufacturing"},
        "family_focus": {
            "commercial_building": "Schedule drift, sequencing logic and owner-controlled central-plant behavior.",
            "cold_chain": "Temperature-control, defrost and conditioned-space sequencing.",
            "industrial_manufacturing": "Controls versus structural process duty in support systems.",
        },
        "decision_relevance": "Avoids jumping to sensors or CAPEX before existing control logic is bounded.",
        "allowed_without_local_binding": ["bounded controls hypothesis", "measure only if material"],
    },
    "cmms_or_workorder_pack": {
        "expected_local_sources": ["cmms_record", "maintenance_log_record", "operator_input_record"],
        "binding_tokens": ["cmms", "workorder", "maintenance", "downtime"],
        "public_seed_source_families": [],
        "relevant_families": {"industrial_manufacturing", "cold_chain", "utility_heavy_site", "commercial_building", "logistics_warehouse"},
        "family_focus": {
            "industrial_manufacturing": "Failure recurrence and downtime dependency before energy-only framing.",
            "cold_chain": "Refrigeration workorders as proof of reliability drag or control drift.",
            "logistics_warehouse": "Charging, dock or handling workorders that reveal reliability drag before CAPEX is modeled.",
            "commercial_building": "Controls or plant workorders that shift interpretation of visible load.",
        },
        "decision_relevance": "Turns maintenance from weak signal into bounded local evidence.",
        "allowed_without_local_binding": ["request maintenance proof", "bounded reliability hypothesis"],
    },
    "permit_detail_pack": {
        "expected_local_sources": ["permit_record", "regulatory_coverage_record"],
        "binding_tokens": ["permit", "filing", "ll97", "ll84", "air permit", "wastewater"],
        "public_seed_source_families": ["permit_record", "regulatory_coverage_record"],
        "relevant_families": set(_ASSET_FAMILY_LIBRARY.keys()),
        "family_focus": {
            "commercial_building": "What filing burden exists and what it still cannot prove locally.",
            "industrial_manufacturing": "What process, thermal or emissions domains are likely decision-relevant.",
            "cold_chain": "What refrigerant, safety or storage obligations constrain redesign.",
        },
        "decision_relevance": "Translates formal obligations into bounded physical and capital hypotheses without treating them as operating truth.",
        "allowed_without_local_binding": ["permit-to-physics framing", "bounded regulatory hypothesis"],
    },
}


def _candidate_text(*values: Any) -> str:
    return " ".join(text(value).lower() for value in values if text(value))


def _infer_asset_family(
    *,
    target_definition: dict[str, Any],
    target_classification_object: dict[str, Any],
    facility_prior: dict[str, Any],
    asset_field_register: list[dict[str, Any]],
) -> str:
    target_type = _candidate_text(
        target_definition.get("target_type"),
        target_definition.get("target_name"),
        target_definition.get("decision_intent"),
        target_classification_object.get("target_type"),
    )
    asset_field_text = _candidate_text(
        " ".join(text(row.get("field")) for row in asset_field_register),
        " ".join(text(row.get("value")) for row in asset_field_register),
        facility_prior.get("case_title"),
    )
    merged = f"{target_type} {asset_field_text}"
    if any(token in merged for token in ("cold_chain", "cold chain", "refrigerated", "freezer", "cold storage")):
        return "cold_chain"
    if any(token in merged for token in ("infrastructure_node", "intermodal", "terminal", "port", "rail node", "substation")):
        return "infrastructure_node"
    explicit_utility_heavy = any(
        token in merged
        for token in (
            "utility_heavy_site",
            "utility heavy",
            "central utility",
            "utility island",
            "power factor",
            "pf charge",
            "reactive",
            "motor control center",
            "mcc lineup",
        )
    )
    utility_support_signals = sum(
        1
        for token in (
            "compressor",
            "large motor",
            "large motors",
            "pump house",
            "cooling tower",
            "blower",
            "distribution equipment",
        )
        if token in merged
    )
    if explicit_utility_heavy or (
        utility_support_signals >= 2
        and not any(
            token in merged
            for token in (
                "warehouse",
                "dock",
                "forklift",
                "logistics",
                "cold chain",
                "laminate",
                "resin",
                "food processing",
                "kiln",
                "furnace",
                "chemical reactor",
            )
        )
    ):
        return "utility_heavy_site"
    if any(token in merged for token in ("warehouse", "distribution center", "distribution hub", "logistics", "dock", "forklift", "high-bay storage")):
        return "logistics_warehouse"
    if any(token in merged for token in ("manufacturing", "plant", "factory", "laminate", "process")):
        return "industrial_manufacturing"
    if any(token in merged for token in ("boiler", "furnace", "kiln", "thermal process", "combustion")):
        return "thermal_process_site"
    if any(token in merged for token in ("building", "office", "tower", "tenant", "commercial")):
        return "commercial_building"
    return "generic_operational_asset"


def _infer_research_mode(source_register: list[dict[str, Any]]) -> str:
    observed_source_families = {
        text(source.get("source_family"))
        for source in list(source_register or [])
        if text(source.get("source_family"))
    }
    operator_integrated_families = {
        "cmms_record",
        "bms_trend_record",
        "lease_matrix_record",
        "operator_input_record",
        "maintenance_log_record",
        "meter_interval_record",
    }
    hybrid_families = {
        "utility_bill_record",
        "equipment_inventory_record",
        "schedule_record",
        "maintenance_contract_record",
        "submetering_record",
    }
    if observed_source_families.intersection(operator_integrated_families):
        return "operator_integrated_congruence"
    if observed_source_families.intersection(hybrid_families):
        return "hybrid_diligence"
    return "public_only_screening"


def _route_state(target_classification_object: dict[str, Any]) -> str:
    target_type = text(target_classification_object.get("target_type"))
    if target_type == "OPERATING_ASSET":
        return "operational_asset_candidate"
    if target_type:
        return "target_not_yet_operationally_bounded"
    return "target_unresolved"


def build_asset_family_research_profile(
    *,
    target_definition: dict[str, Any],
    target_classification_object: dict[str, Any],
    facility_prior: dict[str, Any],
    asset_field_register: list[dict[str, Any]],
    source_register: list[dict[str, Any]],
) -> dict[str, Any]:
    asset_family = _infer_asset_family(
        target_definition=target_definition,
        target_classification_object=target_classification_object,
        facility_prior=facility_prior,
        asset_field_register=asset_field_register,
    )
    route = dict(_ASSET_FAMILY_LIBRARY.get(asset_family, _ASSET_FAMILY_LIBRARY["generic_operational_asset"]))
    all_known_source_families = {
        "geospatial_public_record",
        "property_record",
        "benchmarking_disclosure_record",
        "regulatory_coverage_record",
        "permit_record",
        "climate_normals_record",
        "issuer_financial_record",
        "utility_tariff_record",
        "technical_sourcebook_record",
        "industry_guidance_record",
        "vendor_implementation_record",
    }
    selected_families = list(route.get("authoritative_source_families", []) or [])
    return {
        "asset_family": asset_family,
        "route_state": _route_state(target_classification_object),
        "research_mode": _infer_research_mode(source_register),
        "target_type_hint": text(target_definition.get("target_type")),
        "authoritative_source_families": selected_families,
        "rejected_source_families": sorted(all_known_source_families.difference(selected_families)),
        "typical_processes": list(route.get("typical_processes", []) or []),
        "typical_subsystems": list(route.get("typical_subsystems", []) or []),
        "typical_loss_patterns": list(route.get("typical_loss_patterns", []) or []),
        "typical_regulatory_signals": list(route.get("typical_regulatory_signals", []) or []),
        "typical_measurement_paths": list(route.get("typical_measurement_paths", []) or []),
        "typical_invalid_comparisons": list(route.get("typical_invalid_comparisons", []) or []),
        "jurisdiction_scope": list_text(target_definition.get("jurisdiction_scope")),
    }


def build_operational_intake_pack(
    *,
    asset_family_research_profile: dict[str, Any],
    target_definition: dict[str, Any],
    target_classification_object: dict[str, Any],
    facility_prior: dict[str, Any],
    asset_field_register: list[dict[str, Any]],
    source_register: list[dict[str, Any]],
    local_evidence_binding_register: list[dict[str, Any]],
) -> dict[str, Any]:
    jurisdiction_scope = list_text(target_definition.get("jurisdiction_scope"))
    source_families_observed = dedupe([text(source.get("source_family")) for source in list(source_register or [])])
    observed_source_family_set = set(source_families_observed)
    locally_structured_source_families = {
        text(source.get("source_family"))
        for source in list(source_register or [])
        if text(source.get("round_id")) == "structured_intake"
        or "structured_local_diligence" in {text(item) for item in list(source.get("used_for", []) or [])}
        or text(source.get("source_id")).startswith("structured_intake::")
    }
    missing_binding_items = dedupe(
        item
        for row in list(local_evidence_binding_register or [])
        for item in list_text(row.get("local_binding_needed"))
    )
    schedule_state = (
        "partially_evidenced"
        if observed_source_family_set.intersection({"schedule_record", "operator_input_record", "meter_interval_record", "bms_trend_record"})
        else "not_yet_evidenced"
    )
    control_boundary_state = (
        "partially_evidenced"
        if observed_source_family_set.intersection({"lease_matrix_record", "submetering_record", "operator_input_record", "bms_trend_record"})
        else "not_yet_evidenced"
    )
    maintenance_state = (
        "partially_evidenced"
        if observed_source_family_set.intersection({"maintenance_contract_record", "maintenance_log_record", "cmms_record", "operator_input_record"})
        else "not_yet_evidenced"
    )
    utility_state = (
        "partially_evidenced"
        if observed_source_family_set.intersection({"utility_bill_record", "meter_interval_record", "submetering_record"})
        else "public_context_only"
        if "utility_tariff_record" in observed_source_family_set
        else "not_yet_evidenced"
    )
    finance_state = (
        "partially_evidenced"
        if observed_source_family_set.intersection({"utility_bill_record", "issuer_financial_record", "operator_input_record"})
        else "not_yet_locally_bounded"
    )
    asset_family = text(asset_family_research_profile.get("asset_family"))

    def _pack_binding_needed(pack_name: str) -> list[str]:
        tokens = list(_DILIGENCE_PACK_LIBRARY.get(pack_name, {}).get("binding_tokens", []) or [])
        return [
            item
            for item in missing_binding_items
            if any(token.lower() in item.lower() for token in tokens)
        ]

    def _pack_state(pack_name: str) -> str:
        meta = _DILIGENCE_PACK_LIBRARY.get(pack_name, {})
        relevant_families = set(meta.get("relevant_families", set()) or set())
        if asset_family not in relevant_families:
            return "not_primary"
        expected_sources = set(meta.get("expected_local_sources", []) or [])
        public_seed_sources = set(meta.get("public_seed_source_families", []) or [])
        if locally_structured_source_families.intersection(expected_sources):
            return "partially_evidenced"
        if observed_source_family_set.intersection(expected_sources - public_seed_sources):
            return "partially_evidenced"
        if observed_source_family_set.intersection(public_seed_sources):
            return "public_context_only"
        return "requested_but_absent"

    def _build_diligence_pack(pack_name: str) -> dict[str, Any]:
        meta = _DILIGENCE_PACK_LIBRARY.get(pack_name, {})
        expected_sources = list(meta.get("expected_local_sources", []) or [])
        public_seed_sources = set(meta.get("public_seed_source_families", []) or [])
        present_sources = [
            family
            for family in expected_sources
            if family in observed_source_family_set
        ] + [
            family
            for family in public_seed_sources
            if family in observed_source_family_set and family not in expected_sources
        ]
        focus_map = dict(meta.get("family_focus", {}) or {})
        return build_diligence_pack(
            pack_name=pack_name,
            current_state=_pack_state(pack_name),
            decision_relevance=text(meta.get("decision_relevance")),
            expected_local_sources=expected_sources,
            present_source_families=present_sources,
            binding_needed=_pack_binding_needed(pack_name),
            family_specific_focus=focus_map.get(asset_family, ""),
            allowed_without_local_binding=list(meta.get("allowed_without_local_binding", []) or []),
        )

    diligence_pack_register = [_build_diligence_pack(pack_name) for pack_name in DILIGENCE_PACK_NAMES]
    diligence_pack_state_summary = {
        state: sum(1 for row in diligence_pack_register if text(row.get("current_state")) == state)
        for state in {
            "not_primary",
            "public_context_only",
            "requested_but_absent",
            "partially_evidenced",
            "evidenced",
        }
    }

    return {
        "asset_family": asset_family,
        "research_mode": text(asset_family_research_profile.get("research_mode")),
        "asset_identity_pack": {
            "target_name": text(target_definition.get("target_name")),
            "target_identifier": text(target_definition.get("target_identifier")) or text(target_definition.get("address_raw")),
            "target_type": text(target_definition.get("target_type")),
            "jurisdiction_scope": jurisdiction_scope,
            "classification_state": text(target_classification_object.get("target_type")),
            "classification_confidence": text(target_classification_object.get("classification_confidence")),
        },
        "process_overview_pack": {
            "current_state": "research_seed_only",
            "research_hypotheses": list(asset_family_research_profile.get("typical_processes", []) or []),
        },
        "subsystem_inventory_pack": {
            "current_state": "research_seed_only",
            "expected_subsystems": list(asset_family_research_profile.get("typical_subsystems", []) or []),
        },
        "equipment_dominance_pack": {
            "current_state": "not_yet_locally_bounded",
            "dominant_equipment_classes": list(asset_family_research_profile.get("typical_subsystems", []) or [])[:5],
        },
        "schedule_and_utilization_pack": {
            "current_state": schedule_state,
            "binding_needed": [item for item in missing_binding_items if "schedule" in item.lower() or "shift" in item.lower()],
        },
        "control_boundary_pack": {
            "current_state": control_boundary_state,
            "binding_needed": [item for item in missing_binding_items if "boundary" in item.lower() or "lease" in item.lower() or "tenant" in item.lower()],
        },
        "maintenance_maturity_pack": {
            "current_state": maintenance_state,
            "binding_needed": [item for item in missing_binding_items if "maintenance" in item.lower() or "downtime" in item.lower()],
        },
        "measurement_and_metering_pack": {
            "current_state": "research_seed_only",
            "minimum_paths": list(asset_family_research_profile.get("typical_measurement_paths", []) or []),
            "observed_source_families": source_families_observed,
        },
        "utility_and_tariff_pack": {
            "current_state": utility_state,
            "binding_needed": [item for item in missing_binding_items if "bill" in item.lower() or "tariff" in item.lower() or "demand" in item.lower()],
        },
        "utility_bill_pack": _build_diligence_pack("utility_bill_pack"),
        "utility_tariff_pack": _build_diligence_pack("utility_tariff_pack"),
        "throughput_schedule_pack": _build_diligence_pack("throughput_schedule_pack"),
        "equipment_inventory_pack": _build_diligence_pack("equipment_inventory_pack"),
        "metering_boundary_pack": _build_diligence_pack("metering_boundary_pack"),
        "lease_responsibility_pack": _build_diligence_pack("lease_responsibility_pack"),
        "maintenance_proof_pack": _build_diligence_pack("maintenance_proof_pack"),
        "bms_or_controls_pack": _build_diligence_pack("bms_or_controls_pack"),
        "cmms_or_workorder_pack": _build_diligence_pack("cmms_or_workorder_pack"),
        "permit_detail_pack": _build_diligence_pack("permit_detail_pack"),
        "regulatory_and_permit_pack": {
            "current_state": "public_context_seeded",
            "regulatory_signals": list(asset_family_research_profile.get("typical_regulatory_signals", []) or []),
            "dataset_coverage_register": list(facility_prior.get("dataset_coverage_register", []) or []),
        },
        "finance_driver_pack": {
            "current_state": finance_state,
            "binding_needed": [item for item in missing_binding_items if "utility" in item.lower() or "throughput" in item.lower() or "econom" in item.lower()],
        },
        "logistics_pack": {
            "current_state": "research_seed_only" if text(asset_family_research_profile.get("asset_family")) in {"logistics_warehouse", "cold_chain", "industrial_manufacturing"} else "not_primary",
        },
        "procurement_pack": {
            "current_state": "not_yet_evidenced",
        },
        "culture_execution_pack": {
            "current_state": "weak_signal_only",
        },
        "climate_location_pack": {
            "current_state": "public_context_seeded",
            "jurisdiction_scope": jurisdiction_scope,
        },
        "diligence_pack_register": diligence_pack_register,
        "diligence_pack_state_summary": diligence_pack_state_summary,
        "asset_field_register_snapshot": list(asset_field_register or [])[:12],
    }
