from __future__ import annotations

from typing import Any

from .schemas import dedupe, list_text, text

RESEARCH_LIBRARY_VERSION = "2026-05-01.cgi-c01-c02"

ASSET_FAMILY_RESEARCH_LIBRARY: dict[str, dict[str, Any]] = {
    "commercial_building": {
        "productization_state": "versioned_seeded_dossier",
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
        "valid_normalization_bases": [
            "owner-burdened load boundary",
            "occupied hours or service regime",
            "whole-building benchmarking only as bounded public context",
        ],
        "minimum_local_evidence_classes": [
            "utility_bill_pack",
            "metering_boundary_pack",
            "lease_responsibility_pack",
            "bms_or_controls_pack",
        ],
        "maintainer": "congruence_intelligence_seed_library",
    },
    "industrial_manufacturing": {
        "productization_state": "versioned_seeded_dossier",
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
        "valid_normalization_bases": [
            "throughput or unit output",
            "production hour or duty cycle",
            "process family and thermal-duty class",
            "maintenance maturity and operating schedule",
        ],
        "minimum_local_evidence_classes": [
            "utility_bill_pack",
            "utility_tariff_pack",
            "throughput_schedule_pack",
            "equipment_inventory_pack",
            "maintenance_proof_pack",
        ],
        "maintainer": "congruence_intelligence_seed_library",
    },
    "logistics_warehouse": {
        "productization_state": "versioned_seeded_dossier",
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
        "valid_normalization_bases": [
            "service-level intensity",
            "movement or dock activity",
            "charging profile and conditioned-space share",
        ],
        "minimum_local_evidence_classes": [
            "utility_bill_pack",
            "throughput_schedule_pack",
            "equipment_inventory_pack",
            "metering_boundary_pack",
        ],
        "maintainer": "congruence_intelligence_seed_library",
    },
    "cold_chain": {
        "productization_state": "versioned_seeded_dossier",
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
        "valid_normalization_bases": [
            "temperature regime",
            "dwell or throughput logic",
            "refrigeration boundary and defrost profile",
        ],
        "minimum_local_evidence_classes": [
            "utility_bill_pack",
            "throughput_schedule_pack",
            "equipment_inventory_pack",
            "bms_or_controls_pack",
        ],
        "maintainer": "congruence_intelligence_seed_library",
    },
    "thermal_process_site": {
        "productization_state": "versioned_seeded_dossier",
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
        "valid_normalization_bases": [
            "thermal duty",
            "fuel-normalized output",
            "combustion regime and process family",
        ],
        "minimum_local_evidence_classes": [
            "utility_bill_pack",
            "utility_tariff_pack",
            "throughput_schedule_pack",
            "permit_detail_pack",
        ],
        "maintainer": "congruence_intelligence_seed_library",
    },
    "utility_heavy_site": {
        "productization_state": "versioned_seeded_dossier",
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
        "valid_normalization_bases": [
            "demand structure",
            "reactive or PF exposure",
            "service continuity burden",
        ],
        "minimum_local_evidence_classes": [
            "utility_bill_pack",
            "utility_tariff_pack",
            "equipment_inventory_pack",
            "maintenance_proof_pack",
        ],
        "maintainer": "congruence_intelligence_seed_library",
    },
    "infrastructure_node": {
        "productization_state": "versioned_seeded_dossier",
        "authoritative_source_families": [
            "geospatial_public_record",
            "regulatory_coverage_record",
            "utility_tariff_record",
            "industry_guidance_record",
        ],
        "typical_processes": [
            "flow or network service intake",
            "conversion / routing / dispatch",
            "service continuity and constrained-output delivery",
        ],
        "typical_subsystems": [
            "power conversion or motive-power systems",
            "controls and dispatch logic",
            "redundancy / backup systems",
            "network or node-level support systems",
        ],
        "typical_loss_patterns": [
            "service-continuity burden hidden by energy averages",
            "demand or peak constraint misread as pure consumption issue",
            "redundancy cost treated as waste without duty logic",
        ],
        "typical_regulatory_signals": [
            "service obligation or network constraint",
            "safety / dispatch / uptime compliance",
        ],
        "typical_measurement_paths": [
            "service profile",
            "demand profile",
            "dispatch or uptime logs",
            "major equipment inventory",
        ],
        "typical_invalid_comparisons": [
            "comparing node energy use without matching continuity or duty burden",
        ],
        "valid_normalization_bases": [
            "service continuity",
            "throughput or dispatch burden",
            "redundancy class",
        ],
        "minimum_local_evidence_classes": [
            "utility_bill_pack",
            "throughput_schedule_pack",
            "equipment_inventory_pack",
            "maintenance_proof_pack",
        ],
        "maintainer": "congruence_intelligence_seed_library",
    },
    "generic_operational_asset": {
        "productization_state": "versioned_seeded_dossier",
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
        "valid_normalization_bases": [
            "none until family and operating boundary are clarified",
        ],
        "minimum_local_evidence_classes": [
            "utility_bill_pack",
            "throughput_schedule_pack",
            "equipment_inventory_pack",
        ],
        "maintainer": "congruence_intelligence_seed_library",
    },
}

_COVERAGE_FIELDS = (
    ("authoritative_source_families", "authoritative_source_families"),
    ("typical_processes", "process_logic"),
    ("typical_subsystems", "subsystem_archetypes"),
    ("typical_loss_patterns", "recurrent_loss_patterns"),
    ("valid_normalization_bases", "valid_normalization_bases"),
    ("typical_regulatory_signals", "permit_tariff_concerns"),
    ("typical_measurement_paths", "measurement_paths"),
    ("typical_invalid_comparisons", "invalid_comparison_risks"),
    ("minimum_local_evidence_classes", "minimum_local_evidence_classes"),
)


def asset_family_dossier(asset_family: str) -> dict[str, Any]:
    family = text(asset_family) or "generic_operational_asset"
    base = dict(ASSET_FAMILY_RESEARCH_LIBRARY.get(family, ASSET_FAMILY_RESEARCH_LIBRARY["generic_operational_asset"]))
    base["asset_family"] = family
    base["research_library_version"] = RESEARCH_LIBRARY_VERSION
    return base


def build_asset_family_research_dossier(
    *,
    asset_family_research_profile: dict[str, Any],
) -> dict[str, Any]:
    family = text(asset_family_research_profile.get("asset_family")) or "generic_operational_asset"
    dossier = asset_family_dossier(family)
    dossier["route_state"] = text(asset_family_research_profile.get("route_state"))
    dossier["research_mode"] = text(asset_family_research_profile.get("research_mode"))
    dossier["jurisdiction_scope"] = dedupe(list_text(asset_family_research_profile.get("jurisdiction_scope")))
    return dossier


def build_family_research_coverage_register(
    *,
    asset_family_research_dossier: dict[str, Any],
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for field_name, coverage_domain in _COVERAGE_FIELDS:
        values = dedupe(list_text(asset_family_research_dossier.get(field_name)))
        rows.append(
            {
                "asset_family": text(asset_family_research_dossier.get("asset_family")),
                "coverage_domain": coverage_domain,
                "coverage_state": "covered" if values else "gap",
                "item_count": len(values),
                "items": values,
                "research_library_version": text(asset_family_research_dossier.get("research_library_version")),
            }
        )
    return rows


def build_family_research_gap_register(
    *,
    asset_family_research_dossier: dict[str, Any],
    family_research_coverage_register: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    if text(asset_family_research_dossier.get("productization_state")) != "versioned_seeded_dossier":
        rows.append(
            {
                "asset_family": text(asset_family_research_dossier.get("asset_family")),
                "gap_code": "dossier_not_versioned_seeded",
                "gap_domain": "dossier_productization",
                "why": "The family dossier exists but is not yet in versioned seeded state.",
                "research_library_version": text(asset_family_research_dossier.get("research_library_version")),
            }
        )
    for row in list(family_research_coverage_register or []):
        if text(row.get("coverage_state")) == "covered":
            continue
        rows.append(
            {
                "asset_family": text(asset_family_research_dossier.get("asset_family")),
                "gap_code": "family_research_coverage_gap",
                "gap_domain": text(row.get("coverage_domain")),
                "why": f"`{text(row.get('coverage_domain'))}` is not yet covered in the family research dossier.",
                "research_library_version": text(asset_family_research_dossier.get("research_library_version")),
            }
        )
    return rows
