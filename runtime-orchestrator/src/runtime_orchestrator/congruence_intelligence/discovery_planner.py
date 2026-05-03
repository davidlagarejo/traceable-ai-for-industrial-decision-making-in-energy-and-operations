from __future__ import annotations

from typing import Any

from .research_library import ASSET_FAMILY_RESEARCH_LIBRARY
from .schemas import dedupe, text

_FAMILY_BY_TARGET_TYPE = {
    "commercial_building": "commercial_building",
    "multifamily_building": "commercial_building",
    "data_center": "commercial_building",
    "warehouse_distribution": "logistics_warehouse",
    "cold_chain_facility": "cold_chain",
    "manufacturing_facility": "industrial_manufacturing",
    "food_processing_facility": "industrial_manufacturing",
    "industrial_plant": "industrial_manufacturing",
    "thermal_process_site": "thermal_process_site",
    "infrastructure_node": "infrastructure_node",
    "utility_heavy_site": "utility_heavy_site",
    "oil_gas_upstream_site": "utility_heavy_site",
    "oil_gas_midstream_facility": "utility_heavy_site",
    "oil_gas_downstream_facility": "utility_heavy_site",
}

_PRIORITY_BASE = {
    "critical": 100,
    "high": 70,
    "medium": 40,
    "low": 20,
}

_SEVERITY_BONUS = {
    "critical": 35,
    "high": 20,
    "medium": 10,
    "low": 4,
}

_STATE_FIELD_BY_NEED_ID = {
    "asset_identity_anchor": "identity_state",
    "utility_territory_and_tariff_context": "utility_context_state",
    "warehouse_subtype_classification": "identity_state",
    "dock_and_service_intensity": "schedule_state",
    "refrigeration_presence": "identity_state",
    "operator_boundary_and_control": "operator_boundary_state",
    "mhe_charging_and_mechanical_clues": "utility_context_state",
    "cold_chain_confirmation": "identity_state",
    "process_and_permit_profile": "identity_state",
    "thermal_system_and_utility_mix": "utility_context_state",
    "throughput_proxy_and_schedule": "schedule_state",
}

_UNRESOLVED_STATE_VALUES = {
    "routing_blocked",
    "public_anchor_missing",
    "asset_localized",
    "address_only",
    "unknown",
    "not_yet_evidenced",
    "partially_evidenced",
}

_PRESSURE_HINTS_BY_NEED_ID: dict[str, dict[str, set[str]]] = {
    "asset_identity_anchor": {
        "contradiction_targets": {"subtype_vs_generic_benchmark"},
    },
    "utility_territory_and_tariff_context": {
        "hypothesis_ids": {"warehouse_tariff_orchestration"},
        "loss_pattern_tags": {"tariff_exposure_hidden", "mhe_charging_peak_demand", "power_factor_penalty"},
        "financial_exposure_tags": {"demand_charge_exposure_hidden"},
        "contradiction_targets": {"tariff_vs_efficiency"},
    },
    "warehouse_subtype_classification": {
        "hypothesis_ids": {"warehouse_subtype_temperature_regime"},
        "loss_pattern_tags": {"asset_family_misclassification", "refrigeration_load"},
        "financial_exposure_tags": {"wrong_peer_valuation"},
        "contradiction_targets": {"subtype_vs_generic_benchmark"},
    },
    "dock_and_service_intensity": {
        "hypothesis_ids": {"warehouse_service_intensity_denominator"},
        "loss_pattern_tags": {"dock_infiltration", "schedule_waste"},
        "financial_exposure_tags": {"wrong_underwriting_premium"},
        "contradiction_targets": {"service_intensity_vs_building_waste"},
    },
    "refrigeration_presence": {
        "hypothesis_ids": {"warehouse_subtype_temperature_regime"},
        "loss_pattern_tags": {"refrigeration_load"},
        "financial_exposure_tags": {"wrong_peer_valuation"},
        "contradiction_targets": {"subtype_vs_generic_benchmark"},
    },
    "operator_boundary_and_control": {
        "hypothesis_ids": {"warehouse_control_boundary_value_leakage"},
        "loss_pattern_tags": {"control_boundary_value_leakage"},
        "financial_exposure_tags": {"tenant_operator_value_leakage"},
        "contradiction_targets": {"control_boundary_vs_owner_capture"},
    },
    "mhe_charging_and_mechanical_clues": {
        "hypothesis_ids": {"warehouse_tariff_orchestration", "warehouse_mechanical_topology"},
        "loss_pattern_tags": {"mhe_charging_peak_demand", "rooftop_hvac_degradation", "dock_infiltration"},
        "financial_exposure_tags": {"demand_charge_exposure_hidden", "wrong_retrofit_sequencing"},
        "contradiction_targets": {"tariff_vs_efficiency", "mechanical_vs_logistics_interface"},
    },
    "cold_chain_confirmation": {
        "hypothesis_ids": {"warehouse_subtype_temperature_regime"},
        "loss_pattern_tags": {"refrigeration_load"},
        "financial_exposure_tags": {"wrong_peer_valuation"},
        "contradiction_targets": {"subtype_vs_generic_benchmark"},
    },
    "process_and_permit_profile": {
        "hypothesis_ids": {"manufacturing_process_thermal_lane", "manufacturing_maintenance_downtime"},
        "loss_pattern_tags": {"process_heat_waste", "maintenance_downtime_exposure"},
        "financial_exposure_tags": {"wrong_retrofit_sequencing", "maintenance_downtime_exposure"},
        "contradiction_targets": {"process_load_vs_support_waste", "maintenance_reality_vs_efficiency_story"},
    },
    "thermal_system_and_utility_mix": {
        "hypothesis_ids": {"manufacturing_process_thermal_lane", "manufacturing_compressed_air_support_waste"},
        "loss_pattern_tags": {"thermal_system_loss", "compressed_air_waste", "power_factor_penalty"},
        "financial_exposure_tags": {"wrong_retrofit_sequencing", "operational_savings_not_capturable"},
        "contradiction_targets": {"process_load_vs_support_waste", "support_system_vs_process_load"},
    },
    "throughput_proxy_and_schedule": {
        "hypothesis_ids": {"manufacturing_throughput_normalization"},
        "loss_pattern_tags": {"throughput_normalization_block", "idle_equipment"},
        "financial_exposure_tags": {"wrong_underwriting_premium"},
        "contradiction_targets": {"throughput_vs_support_system_intensity"},
    },
}

_TX_FAMILY_HINTS = [
    "utility_service_territory",
    "permit_record",
    "county_assessor",
    "business_registry",
]
_NYC_FAMILY_HINTS = [
    "benchmark_record",
    "permit_record",
    "county_assessor",
    "property_record",
]
_CA_FAMILY_HINTS = [
    "county_assessor",
    "permit_record",
    "utility_service_territory",
    "benchmark_record",
]

_GENERIC_DISCOVERY_NEEDS: list[dict[str, Any]] = [
    {
        "need_id": "asset_identity_anchor",
        "discovery_need": "Confirm bounded asset identity and parcel boundary.",
        "priority": "critical",
        "why_it_exists": "No dynamic search or peer logic is trustworthy until the framework knows the case refers to a real bounded asset.",
        "search_families_to_explore": [
            "county_assessor",
            "parcel_gis",
            "property_record",
            "owner_asset_page",
            "benchmark_record",
        ],
        "accepted_evidence_types": [
            "assessor_record",
            "parcel_record",
            "owner_asset_record",
            "benchmarking_record",
        ],
        "support_terms": ["parcel", "property", "assessor", "benchmark", "address"],
        "relevant_gap_types": ["asset_context_readiness", "asset_geocode_match", "asset_primary_anchor_missing"],
        "minimum_sufficient_evidence": "One bounded-asset public record that ties address to parcel/building identity plus one corroborating asset-level anchor.",
        "stop_condition": "asset identity classified with evidence_state >= L2 and no critical foreign-asset conflict",
        "downgrade_condition": "no parcel or owner-level anchor found after identity families exhausted",
        "escalation_condition": "ask operator or owner for asset identifier, parcel, or direct asset record",
    },
    {
        "need_id": "utility_territory_and_tariff_context",
        "discovery_need": "Confirm utility territory and tariff context.",
        "priority": "high",
        "why_it_exists": "Tariff exposure, demand logic, and public utility context often explain cost structure before equipment-level judgment.",
        "search_families_to_explore": [
            "utility_service_territory",
            "utility_tariff_schedule",
            "utility_rate_context",
        ],
        "accepted_evidence_types": [
            "utility_territory_record",
            "utility_tariff_record",
            "public_rate_schedule",
        ],
        "support_terms": ["utility", "tariff", "demand", "service territory", "power"],
        "relevant_gap_types": ["asset_energy_behavior_reference", "extended_source_time_budget_exhausted"],
        "minimum_sufficient_evidence": "Utility territory plus one tariff or rate-family anchor.",
        "stop_condition": "utility territory and tariff family are bounded or explicitly escalated to local bills",
        "downgrade_condition": "no utility-family record found within public route and budget",
        "escalation_condition": "ask operator or owner for utility bills and tariff sheets",
    },
]

_FAMILY_DISCOVERY_NEEDS: dict[str, list[dict[str, Any]]] = {
    "logistics_warehouse": [
        {
            "need_id": "warehouse_subtype_classification",
            "discovery_need": "Confirm warehouse subtype.",
            "priority": "critical",
            "why_it_exists": "Dry warehouse, cold-chain, fulfillment, cross-dock and 3PL assets have different operational and energy drivers.",
            "search_families_to_explore": [
                "property_listing",
                "leasing_brochure",
                "owner_asset_page",
                "tenant_operator_page",
                "zoning_record",
                "county_assessor",
                "satellite_photo_clues",
            ],
            "accepted_evidence_types": [
                "asset_brochure",
                "assessor_record",
                "operator_page",
                "zoning_or_permit_record",
            ],
            "support_terms": ["warehouse", "distribution", "fulfillment", "cross-dock", "3pl", "cold", "refrigerat"],
            "relevant_gap_types": ["asset_primary_anchor_missing", "asset_energy_behavior_reference"],
            "minimum_sufficient_evidence": "Subtype clue from listing, brochure, zoning, operator, or permit context.",
            "stop_condition": "asset subtype classified with evidence_state >= L2",
            "downgrade_condition": "no subtype clue across listing / brochure / assessor / operator families",
            "escalation_condition": "ask operator whether facility is dry, cold-chain, fulfillment, cross-dock, or mixed",
        },
        {
            "need_id": "dock_and_service_intensity",
            "discovery_need": "Bound dock density and service-level intensity.",
            "priority": "critical",
            "why_it_exists": "Dock count, service regime, and logistics intensity determine whether area-based benchmarking is meaningful.",
            "search_families_to_explore": [
                "property_listing",
                "leasing_brochure",
                "satellite_photo_clues",
                "site_plan_or_photo_clues",
                "tenant_operator_page",
                "logistics_market_report",
            ],
            "accepted_evidence_types": [
                "dock_count_clue",
                "service_level_description",
                "site_plan",
                "operator_page",
            ],
            "support_terms": ["dock", "loading", "bay", "throughput", "dispatch", "staging"],
            "relevant_gap_types": ["asset_energy_behavior_reference"],
            "minimum_sufficient_evidence": "Observed dock or service-intensity clue plus schedule or operator context.",
            "stop_condition": "dock/service-level intensity bounded enough to prohibit generic area-only comparison",
            "downgrade_condition": "no dock or service clue after listing/photo/operator search",
            "escalation_condition": "ask operator for dock count, shifts, and throughput window",
        },
        {
            "need_id": "refrigeration_presence",
            "discovery_need": "Determine whether any refrigerated or temperature-controlled footprint exists.",
            "priority": "critical",
            "why_it_exists": "Cold-chain status changes the asset family and invalidates generic dry-warehouse comparisons.",
            "search_families_to_explore": [
                "property_listing",
                "leasing_brochure",
                "permit_record",
                "operator_page",
                "satellite_photo_clues",
                "refrigeration_clues",
            ],
            "accepted_evidence_types": [
                "refrigeration_system_clue",
                "cold_storage_listing",
                "permit_or_equipment_record",
            ],
            "support_terms": ["refrigerat", "cold", "freezer", "temperature-controlled", "cooler"],
            "relevant_gap_types": ["asset_energy_behavior_reference"],
            "minimum_sufficient_evidence": "Any credible refrigeration or temperature-control clue from public or operator evidence.",
            "stop_condition": "cold-chain presence either evidenced or explicitly downgraded pending operator confirmation",
            "downgrade_condition": "no refrigeration clue found in listing, permits, operator, or photo context",
            "escalation_condition": "ask operator whether any portion is refrigerated or temperature-controlled",
        },
        {
            "need_id": "operator_boundary_and_control",
            "discovery_need": "Confirm tenant / operator boundary and who controls docks, charging, and schedules.",
            "priority": "critical",
            "why_it_exists": "If the operator controls logistics behavior while the owner pays utility or CAPEX, value capture can leak across the boundary.",
            "search_families_to_explore": [
                "tenant_operator_page",
                "lease_summary",
                "property_listing",
                "business_registry",
            ],
            "accepted_evidence_types": [
                "operator_page",
                "lease_matrix",
                "owner_operator_assignment",
            ],
            "support_terms": ["tenant", "operator", "lease", "responsibility", "control boundary"],
            "relevant_gap_types": ["asset_context_readiness"],
            "minimum_sufficient_evidence": "At least one operator / tenant clue plus one ownership or lease-boundary clue.",
            "stop_condition": "owner and operator boundary discussed as observed or explicitly unbound",
            "downgrade_condition": "public boundary evidence remains absent after operator and listing search",
            "escalation_condition": "ask owner/operator for lease responsibility and metering boundary",
        },
        {
            "need_id": "mhe_charging_and_mechanical_clues",
            "discovery_need": "Look for motive-power charging and roof/HVAC/mechanical clues.",
            "priority": "high",
            "why_it_exists": "Charging windows, rooftop units, and conditioning duty can dominate demand and false efficiency narratives.",
            "search_families_to_explore": [
                "property_photo_clues",
                "operator_page",
                "equipment_listing",
                "permit_record",
                "satellite_photo_clues",
            ],
            "accepted_evidence_types": [
                "forklift_or_mhe_clue",
                "charging_infrastructure_clue",
                "roof_hvac_clue",
                "mechanical_permit_clue",
            ],
            "support_terms": ["forklift", "charging", "battery", "hvac", "roof", "rtu", "mechanical"],
            "relevant_gap_types": ["asset_energy_behavior_reference"],
            "minimum_sufficient_evidence": "Public clues showing charging or mechanical systems relevant to demand and conditioning.",
            "stop_condition": "charging/mechanical clue either observed or escalated to operator intake",
            "downgrade_condition": "no public clue from photo, permit, or operator search",
            "escalation_condition": "ask operator for forklift fleet, charging windows, and HVAC / rooftop system type",
        },
    ],
    "cold_chain": [
        {
            "need_id": "cold_chain_confirmation",
            "discovery_need": "Confirm cold-chain regime and temperature bands.",
            "priority": "critical",
            "why_it_exists": "Temperature regime, refrigeration duty, and door traffic redefine comparability and loss logic.",
            "search_families_to_explore": [
                "property_listing",
                "leasing_brochure",
                "operator_page",
                "permit_record",
                "refrigeration_clues",
            ],
            "accepted_evidence_types": [
                "cold_storage_description",
                "refrigeration_equipment_clue",
                "permit_record",
            ],
            "support_terms": ["cold", "freezer", "refrigerat", "temperature-controlled"],
            "relevant_gap_types": ["asset_energy_behavior_reference"],
            "minimum_sufficient_evidence": "One refrigeration / temperature-control clue plus one operating-context clue.",
            "stop_condition": "cold-chain regime bounded to temperature-controlled or explicitly unresolved",
            "downgrade_condition": "no refrigeration clue in listing / permit / operator families",
            "escalation_condition": "ask operator for temperature bands and refrigerated footprint",
        },
    ],
    "industrial_manufacturing": [
        {
            "need_id": "process_and_permit_profile",
            "discovery_need": "Confirm process family and permit-bearing systems.",
            "priority": "critical",
            "why_it_exists": "Permits, process type, and emissions-bearing systems often reveal the dominant physical lane before detailed site data exists.",
            "search_families_to_explore": [
                "permit_record",
                "environmental_registry",
                "operator_page",
                "industry_guidance",
                "property_record",
            ],
            "accepted_evidence_types": [
                "permit_record",
                "process_description",
                "regulated_equipment_clue",
            ],
            "support_terms": ["permit", "emission", "boiler", "reactor", "line", "process", "production"],
            "relevant_gap_types": ["asset_primary_anchor_missing", "asset_energy_behavior_reference"],
            "minimum_sufficient_evidence": "Permit or process clue that identifies the dominant process lane.",
            "stop_condition": "process family and major regulated system are bounded enough to route hypotheses",
            "downgrade_condition": "public permit/process families produce no usable clue",
            "escalation_condition": "ask operator for process map and regulated equipment inventory",
        },
        {
            "need_id": "thermal_system_and_utility_mix",
            "discovery_need": "Identify thermal systems and utility mix.",
            "priority": "critical",
            "why_it_exists": "Combustion, steam, chilled water, and electric duty can make a benchmark frame totally wrong if not bounded early.",
            "search_families_to_explore": [
                "permit_record",
                "environmental_registry",
                "utility_service_territory",
                "technical_sourcebook",
                "operator_page",
            ],
            "accepted_evidence_types": [
                "boiler_or_furnace_clue",
                "utility_mix_clue",
                "thermal_system_record",
            ],
            "support_terms": ["steam", "boiler", "furnace", "kiln", "combustion", "gas", "thermal"],
            "relevant_gap_types": ["asset_energy_behavior_reference"],
            "minimum_sufficient_evidence": "Any permit or technical clue confirming fuel/thermal lane plus utility context.",
            "stop_condition": "thermal lane bounded enough to activate or falsify thermal-loss hypotheses",
            "downgrade_condition": "no thermal/utility clue across permit and process search",
            "escalation_condition": "ask operator for boiler, furnace, steam, chilled-water and primary fuel inventory",
        },
        {
            "need_id": "throughput_proxy_and_schedule",
            "discovery_need": "Find throughput proxies and operating schedule clues.",
            "priority": "critical",
            "why_it_exists": "Manufacturing comparability fails without throughput or duty normalization.",
            "search_families_to_explore": [
                "operator_page",
                "industry_guidance",
                "market_or_product_description",
                "business_registry",
            ],
            "accepted_evidence_types": [
                "throughput_proxy",
                "shift_or_schedule_clue",
                "product_mix_description",
            ],
            "support_terms": ["throughput", "shift", "24/7", "capacity", "tons", "line rate", "product mix"],
            "relevant_gap_types": ["asset_energy_behavior_reference"],
            "minimum_sufficient_evidence": "Throughput or capacity proxy plus duty/schedule clue.",
            "stop_condition": "comparison can be routed to throughput-aware normalization or explicitly blocked",
            "downgrade_condition": "no throughput clue from operator or market context",
            "escalation_condition": "ask operator for throughput by shift, duty cycle, and product mix",
        },
    ],
}


def _asset_family(target_definition: dict[str, Any]) -> str:
    target_type = text(target_definition.get("target_type"))
    return _FAMILY_BY_TARGET_TYPE.get(target_type, "commercial_building")


def _gap_map(coverage_gaps: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    return {
        text(row.get("gap_type")): row
        for row in list(coverage_gaps or [])
        if text(row.get("gap_type"))
    }


def _requestable_text(items: list[dict[str, Any]]) -> str:
    tokens: list[str] = []
    for row in list(items or []):
        tokens.extend(
            [
                text(row.get("evidence_item")),
                text(row.get("why_needed")),
                text(row.get("source")),
                " ".join(text(item) for item in list(row.get("related_clusters", []) or [])),
            ]
        )
    return " ".join(token.lower() for token in tokens if token)


def _attempt_text(attempts: list[dict[str, Any]]) -> str:
    parts: list[str] = []
    for row in list(attempts or []):
        parts.extend(
            [
                text(row.get("source_type")),
                text(row.get("source_family")),
                text(row.get("detail")),
                text(row.get("discovery_reason")),
            ]
        )
    return " ".join(part.lower() for part in parts if part)


def _need_is_active(template: dict[str, Any], gap_rows: dict[str, dict[str, Any]], requestable_text: str, attempt_text: str) -> bool:
    relevant_gap_types = set(template.get("relevant_gap_types", []) or [])
    if relevant_gap_types.intersection(gap_rows):
        return True
    support_terms = [str(token).lower() for token in list(template.get("support_terms", []) or []) if str(token).strip()]
    if support_terms and any(token in requestable_text for token in support_terms):
        return True
    if support_terms and any(token in attempt_text for token in support_terms):
        return True
    return not relevant_gap_types


def _state_value(dynamic_case_state: dict[str, Any], field_name: str) -> str:
    return text(dynamic_case_state.get(field_name))


def _pressure_context(template: dict[str, Any], dynamic_case_state: dict[str, Any]) -> tuple[list[str], list[str], dict[str, int]]:
    need_id = text(template.get("need_id"))
    hints = _PRESSURE_HINTS_BY_NEED_ID.get(need_id, {})
    active_hypotheses = {
        text(item)
        for item in list(dynamic_case_state.get("active_rival_hypotheses", []) or [])
        + list(dynamic_case_state.get("dominant_hypothesis_ids", []) or [])
        if text(item)
    }
    comparison_blockers = {
        text(item)
        for item in list(dynamic_case_state.get("active_comparison_blockers", []) or [])
        if text(item)
    }
    loss_candidates = {
        text(item)
        for item in list(dynamic_case_state.get("active_loss_pattern_candidates", []) or [])
        if text(item)
    }
    financial_candidates = {
        text(item)
        for item in list(dynamic_case_state.get("active_financial_exposure_candidates", []) or [])
        if text(item)
    }
    contradiction_targets = {
        text(item)
        for item in list(dynamic_case_state.get("active_contradiction_targets", []) or [])
        if text(item)
    }

    hypothesis_hits = sorted(active_hypotheses.intersection(hints.get("hypothesis_ids", set())))
    loss_hits = sorted(loss_candidates.intersection(hints.get("loss_pattern_tags", set())))
    financial_hits = sorted(financial_candidates.intersection(hints.get("financial_exposure_tags", set())))
    contradiction_hits = sorted(contradiction_targets.intersection(hints.get("contradiction_targets", set())))
    comparison_hits = [need_id] if need_id in comparison_blockers else []

    basis_register: list[str] = []
    basis_register.extend(f"hypothesis_pressure:{value}" for value in hypothesis_hits)
    basis_register.extend(f"comparison_pressure:{value}" for value in comparison_hits)
    basis_register.extend(f"loss_pattern_pressure:{value}" for value in loss_hits)
    basis_register.extend(f"financial_pressure:{value}" for value in financial_hits)
    basis_register.extend(f"contradiction_pressure:{value}" for value in contradiction_hits)

    signals: list[str] = []
    if hypothesis_hits:
        signals.append("active_rival_hypotheses")
    if comparison_hits:
        signals.append("active_comparison_blockers")
    if loss_hits:
        signals.append("active_loss_pattern_candidates")
    if financial_hits:
        signals.append("active_financial_exposure_candidates")
    if contradiction_hits:
        signals.append("active_contradiction_targets")

    scores = {
        "hypothesis_pressure_score": min(len(hypothesis_hits) * 18, 36),
        "comparison_pressure_score": min(len(comparison_hits) * 16, 32),
        "loss_pattern_pressure_score": min(len(loss_hits) * 10, 20),
        "financial_pressure_score": min(len(financial_hits) * 10, 20),
        "contradiction_pressure_score": min(len(contradiction_hits) * 12, 24),
    }
    return basis_register, signals, scores


def _jurisdiction_family_hints(dynamic_case_state: dict[str, Any], target_definition: dict[str, Any]) -> list[str]:
    tokens = " ".join(
        text(item).lower()
        for item in list(dynamic_case_state.get("jurisdiction_scope", []) or [])
        + list(dynamic_case_state.get("active_regulatory_triggers", []) or [])
        + list(target_definition.get("jurisdiction_scope", []) or [])
    )
    if any(token in tokens for token in ("us-ny-nyc", "ll84", "ll97", "new york city", "nyc")):
        return list(_NYC_FAMILY_HINTS)
    if any(token in tokens for token in ("us-tx", "ercot", "tceq", "houston", "dallas", "austin")):
        return list(_TX_FAMILY_HINTS)
    if any(token in tokens for token in ("us-ca", "title24", "calgreen", "los angeles", "oakland", "san francisco")):
        return list(_CA_FAMILY_HINTS)
    return []


def _mandatory_gap_family_hints(dynamic_case_state: dict[str, Any]) -> list[str]:
    hints: list[str] = []
    for gap in list(dynamic_case_state.get("mandatory_source_gaps", []) or []):
        lowered = text(gap).lower()
        if any(token in lowered for token in ("utility_", "tariff", "oncor", "austin_energy", "pge", "sdge", "ladwp", "sce")):
            hints.append("utility_service_territory")
        if any(token in lowered for token in ("permit", "dob", "acris", "tceq")):
            hints.append("permit_record")
        if any(token in lowered for token in ("assessor", "cad", "property_record", "pluto")):
            hints.append("county_assessor")
        if any(token in lowered for token in ("benchmark", "ll84", "ll97")):
            hints.append("benchmark_record")
        if any(token in lowered for token in ("operator", "tenant", "lease")):
            hints.append("tenant_operator_page")
    return dedupe(hints)


def _source_family_preference_hints(
    *,
    template: dict[str, Any],
    target_definition: dict[str, Any],
    dynamic_case_state: dict[str, Any],
) -> list[str]:
    if not dynamic_case_state:
        return []
    families = [text(item) for item in list(template.get("search_families_to_explore", []) or []) if text(item)]
    if not families:
        return []
    hinted = dedupe(
        family
        for family in _jurisdiction_family_hints(dynamic_case_state, target_definition)
        + _mandatory_gap_family_hints(dynamic_case_state)
        if family in families
    )
    return hinted


def _jurisdiction_fit(
    *,
    template: dict[str, Any],
    target_definition: dict[str, Any],
    dynamic_case_state: dict[str, Any],
) -> str:
    if not dynamic_case_state:
        return "generic"
    preferred = _source_family_preference_hints(
        template=template,
        target_definition=target_definition,
        dynamic_case_state=dynamic_case_state,
    )
    family_count = len(list(template.get("search_families_to_explore", []) or []))
    if preferred and len(preferred) >= min(2, max(family_count, 1)):
        return "high"
    if preferred:
        return "medium"
    return "generic"


def _activation_context(
    *,
    template: dict[str, Any],
    target_definition: dict[str, Any],
    gap_rows: dict[str, dict[str, Any]],
    requestable_text: str,
    attempt_text: str,
    dynamic_case_state: dict[str, Any],
) -> tuple[bool, list[str], list[str], list[str], dict[str, int]]:
    reasons: list[str] = []
    signals: list[str] = []
    activation_basis_register: list[str] = []
    pressure_scores = {
        "hypothesis_pressure_score": 0,
        "comparison_pressure_score": 0,
        "loss_pattern_pressure_score": 0,
        "financial_pressure_score": 0,
        "contradiction_pressure_score": 0,
    }
    relevant_gap_types = set(template.get("relevant_gap_types", []) or [])
    matched_gap_types = sorted(relevant_gap_types.intersection(gap_rows))
    if matched_gap_types:
        reasons.extend(f"matched_gap:{gap_type}" for gap_type in matched_gap_types)
        signals.append("coverage_gaps")

    support_terms = [str(token).lower() for token in list(template.get("support_terms", []) or []) if str(token).strip()]
    if support_terms and any(token in requestable_text for token in support_terms):
        reasons.append("requestable_evidence_signal")
        signals.append("requestable_evidence_items")
    if support_terms and any(token in attempt_text for token in support_terms):
        reasons.append("attempt_signal")
        signals.append("attempt_history")

    if dynamic_case_state:
        if not bool(dynamic_case_state.get("technical_scraping_allowed", True)) and text(template.get("need_id")) != "asset_identity_anchor":
            return False, [], ["technical_scraping_gate"], [], pressure_scores
        state_field = _STATE_FIELD_BY_NEED_ID.get(text(template.get("need_id")))
        state_value = _state_value(dynamic_case_state, state_field) if state_field else ""
        if state_value in _UNRESOLVED_STATE_VALUES:
            reasons.append(f"dynamic_state:{state_field}={state_value}")
            signals.append(state_field)
        hinted_families = _source_family_preference_hints(
            template=template,
            target_definition=target_definition,
            dynamic_case_state=dynamic_case_state,
        )
        if hinted_families:
            reasons.append("jurisdiction_signal")
            signals.append("jurisdiction_scope")
            if dynamic_case_state.get("mandatory_source_gaps"):
                reasons.append("mandatory_source_gap_signal")
                signals.append("mandatory_source_gaps")
        pressure_basis, pressure_signals, pressure_scores = _pressure_context(template, dynamic_case_state)
        if pressure_basis:
            reasons.extend(pressure_basis)
            activation_basis_register.extend(pressure_basis)
            signals.extend(pressure_signals)

    if not reasons and not relevant_gap_types:
        reasons.append("family_default_need")
        signals.append("family_library_default")

    return bool(reasons), dedupe(reasons), dedupe(signals), dedupe(activation_basis_register), pressure_scores


def _activation_score(
    *,
    template: dict[str, Any],
    matched_gap_types: list[str],
    gap_rows: dict[str, dict[str, Any]],
    jurisdiction_fit: str,
    state_signals_used: list[str],
    pressure_scores: dict[str, int],
) -> int:
    score = _PRIORITY_BASE.get(text(template.get("priority")).lower(), 20)
    score += sum(
        _SEVERITY_BONUS.get(text(gap_rows[gap_type].get("severity")).lower(), 0)
        for gap_type in matched_gap_types
        if gap_type in gap_rows
    )
    if jurisdiction_fit == "high":
        score += 12
    elif jurisdiction_fit == "medium":
        score += 6
    if "mandatory_source_gaps" in state_signals_used:
        score += 8
    if "jurisdiction_scope" in state_signals_used:
        score += 4
    score += int(pressure_scores.get("hypothesis_pressure_score", 0) or 0)
    score += int(pressure_scores.get("comparison_pressure_score", 0) or 0)
    score += int(pressure_scores.get("loss_pattern_pressure_score", 0) or 0)
    score += int(pressure_scores.get("financial_pressure_score", 0) or 0)
    score += int(pressure_scores.get("contradiction_pressure_score", 0) or 0)
    return score


def build_discovery_need_register(
    *,
    target_definition: dict[str, Any],
    coverage_gaps: list[dict[str, Any]],
    requestable_evidence_items: list[dict[str, Any]],
    attempts: list[dict[str, Any]],
    search_budget_register: list[dict[str, Any]] | None = None,
    dynamic_case_state: dict[str, Any] | None = None,
) -> list[dict[str, Any]]:
    family = _asset_family(target_definition)
    library = ASSET_FAMILY_RESEARCH_LIBRARY.get(family, {})
    gap_rows = _gap_map(coverage_gaps)
    requestable_blob = _requestable_text(requestable_evidence_items)
    attempt_blob = _attempt_text(attempts)
    dynamic_case_state = dict(dynamic_case_state) if isinstance(dynamic_case_state, dict) else {}
    budget_state = text((list(search_budget_register or [{}]) or [{}])[0].get("budget_state")) or "bounded"
    budget_class = text((list(search_budget_register or [{}]) or [{}])[0].get("budget_class")) or "identity_only_screening"
    templates = _GENERIC_DISCOVERY_NEEDS + list(_FAMILY_DISCOVERY_NEEDS.get(family, []) or [])

    rows: list[dict[str, Any]] = []
    for template in templates:
        if dynamic_case_state and not bool(dynamic_case_state.get("technical_scraping_allowed", True)):
            if text(template.get("need_id")) != "asset_identity_anchor":
                continue
        active, activation_reasons, state_signals_used, activation_basis_register, pressure_scores = _activation_context(
            template=template,
            target_definition=target_definition,
            gap_rows=gap_rows,
            requestable_text=requestable_blob,
            attempt_text=attempt_blob,
            dynamic_case_state=dynamic_case_state,
        )
        legacy_active = _need_is_active(template, gap_rows, requestable_blob, attempt_blob)
        if not active and not legacy_active:
            continue
        matched_gap_types = [gap_type for gap_type in template.get("relevant_gap_types", []) or [] if gap_type in gap_rows]
        jurisdiction_fit = _jurisdiction_fit(
            template=template,
            target_definition=target_definition,
            dynamic_case_state=dynamic_case_state,
        )
        source_family_preference_hints = _source_family_preference_hints(
            template=template,
            target_definition=target_definition,
            dynamic_case_state=dynamic_case_state,
        )
        if legacy_active and not activation_reasons:
            activation_reasons = ["legacy_gap_or_support_activation"]
            state_signals_used = ["coverage_gaps_or_support_terms"]
        rows.append(
            {
                "need_id": text(template.get("need_id")),
                "asset_family": family,
                "discovery_need": text(template.get("discovery_need")),
                "priority": text(template.get("priority")) or "medium",
                "why_it_exists": text(template.get("why_it_exists")),
                "search_families_to_explore": list(template.get("search_families_to_explore", []) or []),
                "accepted_evidence_types": list(template.get("accepted_evidence_types", []) or []),
                "stop_condition": text(template.get("stop_condition")),
                "minimum_sufficient_evidence": text(template.get("minimum_sufficient_evidence")),
                "downgrade_condition": text(template.get("downgrade_condition")),
                "escalation_condition": text(template.get("escalation_condition")),
                "matched_gap_types": matched_gap_types,
                "matched_gap_severities": dedupe(
                    text(gap_rows[gap_type].get("severity"))
                    for gap_type in matched_gap_types
                    if gap_type in gap_rows
                ),
                "research_anchor_count": len(list(library.get("authoritative_source_families", []) or [])),
                "budget_state": budget_state,
                "budget_class": budget_class,
                "activation_reasons": activation_reasons,
                "activation_basis_register": activation_basis_register,
                "state_signals_used": state_signals_used,
                "jurisdiction_fit": jurisdiction_fit,
                "source_family_preference_hints": source_family_preference_hints,
                "hypothesis_pressure_score": int(pressure_scores.get("hypothesis_pressure_score", 0) or 0),
                "comparison_pressure_score": int(pressure_scores.get("comparison_pressure_score", 0) or 0),
                "loss_pattern_pressure_score": int(pressure_scores.get("loss_pattern_pressure_score", 0) or 0),
                "financial_pressure_score": int(pressure_scores.get("financial_pressure_score", 0) or 0),
                "contradiction_pressure_score": int(pressure_scores.get("contradiction_pressure_score", 0) or 0),
            }
        )
    rows.sort(
        key=lambda row: (
            -_activation_score(
                template={**row, "priority": row.get("priority", "")},
                matched_gap_types=list(row.get("matched_gap_types", []) or []),
                gap_rows=gap_rows,
                jurisdiction_fit=text(row.get("jurisdiction_fit")),
                state_signals_used=list(row.get("state_signals_used", []) or []),
                pressure_scores={
                    "hypothesis_pressure_score": int(row.get("hypothesis_pressure_score", 0) or 0),
                    "comparison_pressure_score": int(row.get("comparison_pressure_score", 0) or 0),
                    "loss_pattern_pressure_score": int(row.get("loss_pattern_pressure_score", 0) or 0),
                    "financial_pressure_score": int(row.get("financial_pressure_score", 0) or 0),
                    "contradiction_pressure_score": int(row.get("contradiction_pressure_score", 0) or 0),
                },
            ),
            text(row.get("discovery_need")),
        )
    )
    return rows


def build_search_family_execution_plan(
    *,
    discovery_need_register: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for need in list(discovery_need_register or []):
        families = list(need.get("search_families_to_explore", []) or [])
        accepted_types = list(need.get("accepted_evidence_types", []) or [])
        for order, family in enumerate(families, start=1):
            rows.append(
                {
                    "need_id": text(need.get("need_id")),
                    "discovery_need": text(need.get("discovery_need")),
                    "execution_priority": text(need.get("priority")),
                    "search_family": text(family),
                    "family_order": order,
                    "expected_evidence_types": accepted_types,
                    "stop_condition": text(need.get("stop_condition")),
                    "execution_state": (
                        "deferred_budget_exhausted"
                        if text(need.get("budget_state")) == "exhausted"
                        else "planned"
                    ),
                }
            )
    return rows


def build_accepted_evidence_type_register(
    *,
    discovery_need_register: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for need in list(discovery_need_register or []):
        for evidence_type in list(need.get("accepted_evidence_types", []) or []):
            rows.append(
                {
                    "need_id": text(need.get("need_id")),
                    "discovery_need": text(need.get("discovery_need")),
                    "accepted_evidence_type": text(evidence_type),
                }
            )
    return rows


def build_discovery_stop_condition_register(
    *,
    discovery_need_register: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for need in list(discovery_need_register or []):
        rows.append(
            {
                "need_id": text(need.get("need_id")),
                "purpose": text(need.get("discovery_need")),
                "minimum_sufficient_evidence": text(need.get("minimum_sufficient_evidence")),
                "stop_condition": text(need.get("stop_condition")),
                "downgrade_condition": text(need.get("downgrade_condition")),
                "escalation_condition": text(need.get("escalation_condition")),
                "budget_class": text(need.get("budget_class")),
            }
        )
    return rows
