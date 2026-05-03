from __future__ import annotations

from .schemas import AssetType, AssetTypeRoute
from .target_taxonomy import normalize_asset_type


ASSET_TYPE_ROUTES: dict[AssetType, AssetTypeRoute] = {
    AssetType.COMMERCIAL_BUILDING: AssetTypeRoute(
        asset_type=AssetType.COMMERCIAL_BUILDING,
        route_name="building_benchmarking_and_property_records_first",
        primary_decision_anchors=[
            "property record or assessor anchor",
            "benchmarking disclosure if jurisdiction supports it",
            "permit-driven systems clues",
            "regulatory family screening",
        ],
        critical_field_family=[
            "address_confirmed",
            "size_or_gfa",
            "use_or_occupancy",
            "year_built",
            "energy_baseline_or_proxy",
            "system_presence",
            "regulatory_applicability",
        ],
        prohibited_shortcuts=[
            "Do not use CBECS or sector averages as local EUI when city benchmarking exists.",
            "Do not use SEC or ESG reports to fill asset-level building systems or energy fields.",
        ],
        routing_notes=[
            "Prioritize assessor / parcel / property datasets before marketing or generic owner pages.",
            "If local benchmarking exists, it outranks ENERGY STAR or generic web-search summaries.",
            "For large office towers, route early to tenant metering, lease-responsibility, and central-plant clues when available.",
            "Fuel-transition context should distinguish steam, gas, district energy, and electrification exposure before retrofit claims are allowed.",
        ],
    ),
    AssetType.MULTIFAMILY: AssetTypeRoute(
        asset_type=AssetType.MULTIFAMILY,
        route_name="multifamily_property_and_local_disclosure_first",
        primary_decision_anchors=[
            "property record",
            "use or unit mix",
            "local benchmarking disclosure if covered",
            "permit-driven systems clues",
        ],
        critical_field_family=[
            "address_confirmed",
            "size_or_gfa",
            "unit_or_use_mix",
            "energy_baseline_or_proxy",
            "regulatory_applicability",
        ],
        prohibited_shortcuts=[
            "Do not use multifamily portfolio averages as local building truth.",
            "Do not infer unit mix from owner narrative if property record is absent.",
        ],
        routing_notes=[
            "Covered multifamily assets may still route through the same benchmarking and permit layers as commercial buildings.",
        ],
    ),
    AssetType.INDUSTRIAL_FACILITY: AssetTypeRoute(
        asset_type=AssetType.INDUSTRIAL_FACILITY,
        route_name="permit_emissions_and_process_anchor_first",
        primary_decision_anchors=[
            "property or site anchor",
            "environmental permit or emissions registry",
            "process or throughput clue",
            "utility or fuel basis",
        ],
        critical_field_family=[
            "address_confirmed",
            "size_or_gfa",
            "process_anchor",
            "environmental_or_permit_anchor",
            "throughput_or_load_driver",
            "fuel_type",
            "regulatory_applicability",
        ],
        prohibited_shortcuts=[
            "Do not substitute corporate ESG intensity for site-level emissions or process data.",
            "Do not treat MECS or OpenEI sector benchmarks as local energy truth.",
        ],
        routing_notes=[
            "Industrial routing is permit-first and emissions-first, not brochure-first.",
            "EPA GHGRP and state environmental agencies outrank generic web pages.",
            "Manufacturing subtypes should route to process-family clues such as NAICS/SIC, curing or thermal duty, compressed-air topology, and emissions-control systems.",
            "Do not collapse wastewater, VOC, dust, or thermal-generation exposure into a generic industrial support-load narrative.",
        ],
    ),
    AssetType.WAREHOUSE_LOGISTICS: AssetTypeRoute(
        asset_type=AssetType.WAREHOUSE_LOGISTICS,
        route_name="property_logistics_and_cold_chain_split",
        primary_decision_anchors=[
            "property or assessor anchor",
            "dock or throughput clue",
            "refrigeration yes or no",
            "benchmarking disclosure if covered",
        ],
        critical_field_family=[
            "address_confirmed",
            "size_or_gfa",
            "dock_or_throughput_anchor",
            "refrigeration_yes_no",
            "energy_baseline_or_proxy",
            "regulatory_applicability",
        ],
        prohibited_shortcuts=[
            "Do not assume cold-chain from owner branding alone.",
            "Do not use retail or office benchmarks as warehouse local truth.",
        ],
        routing_notes=[
            "Cold-chain split is mandatory because refrigeration changes both system expectations and energy routing.",
        ],
    ),
    AssetType.DATA_CENTER: AssetTypeRoute(
        asset_type=AssetType.DATA_CENTER,
        route_name="power_cooling_and_uptime_context_first",
        primary_decision_anchors=[
            "property or site anchor",
            "critical load clue",
            "cooling or redundancy clue",
            "utility and tariff context",
        ],
        critical_field_family=[
            "address_confirmed",
            "critical_load_anchor",
            "cooling_or_redundancy_clue",
            "utility_tariff_or_power_context",
            "energy_baseline_or_proxy",
            "regulatory_applicability",
        ],
        prohibited_shortcuts=[
            "Do not use generic commercial-building HVAC assumptions as data-center cooling truth.",
            "Do not use office tariff assumptions for data-center power economics.",
        ],
        routing_notes=[
            "Utility territory and power-service context matter earlier here than in generic buildings.",
        ],
    ),
}


def route_for_asset_type(asset_type: AssetType | str | None) -> AssetTypeRoute | None:
    normalized = normalize_asset_type(asset_type)
    if normalized is None:
        return None
    return ASSET_TYPE_ROUTES.get(normalized)
