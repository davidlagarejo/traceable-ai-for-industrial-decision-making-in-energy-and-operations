"""Adapter for motor_012 — Public Data Engine / Facility Prior Construction.

Takes all Phase 1 artifacts and constructs the facility_prior: the minimum
structured, non-verificatory, traceable representation of the probable context
of the facility. Operates strictly within Decision-grade limits.

The facility_prior contains:
- 12 canonical entity objects (structured public context)
- benchmark_bundle (sector EUI benchmarks by sector)
- jurisdiction_bundle (climate zone, regulatory framework)
- regulatory_flag_bundle (compliance exposure signals)
- system_asset_hypotheses (plausible systems layer)
- operational_tension_hypotheses (preliminary frictions)
- prior_assumptions_pack (all explicit assumptions)
- uncertainty_markers (what cannot be asserted)

Generic version: works for any asset/company globally.
"""
from __future__ import annotations

from copy import deepcopy
import hashlib
from datetime import datetime, timezone
from typing import Any

from ..asset_contracts import derive_effective_case_id, derive_target_definition
from ..congruence_intelligence.declared_input_governor import (
    annotate_asset_field_register,
    build_declared_input_downgrade_register,
)
from .base import BaseMotorAdapter


# ── Climate data lookup by ASHRAE zone and international zones ────────────────

_CLIMATE_DATA: dict[str, dict] = {
    # ASHRAE Standard Climate Zones (US-centric)
    "1A": {"description": "Very Hot-Humid", "HDD_base65": 200,  "CDD_base65": 4000, "heating_dominated": False, "cooling_dominated": True},
    "1B": {"description": "Very Hot-Dry",   "HDD_base65": 200,  "CDD_base65": 4000, "heating_dominated": False, "cooling_dominated": True},
    "2A": {"description": "Hot-Humid",      "HDD_base65": 1200, "CDD_base65": 2700, "heating_dominated": False, "cooling_dominated": True},
    "2B": {"description": "Hot-Dry",        "HDD_base65": 1200, "CDD_base65": 2700, "heating_dominated": False, "cooling_dominated": True},
    "3A": {"description": "Warm-Humid",     "HDD_base65": 2500, "CDD_base65": 1600, "heating_dominated": False, "cooling_dominated": False},
    "3B": {"description": "Warm-Dry",       "HDD_base65": 2500, "CDD_base65": 1600, "heating_dominated": False, "cooling_dominated": False},
    "3C": {"description": "Warm-Marine",    "HDD_base65": 2500, "CDD_base65":  600, "heating_dominated": False, "cooling_dominated": False},
    "4A": {"description": "Mixed-Humid",    "HDD_base65": 4717, "CDD_base65": 1082, "heating_dominated": False, "cooling_dominated": False},
    "4B": {"description": "Mixed-Dry",      "HDD_base65": 4000, "CDD_base65": 1200, "heating_dominated": False, "cooling_dominated": False},
    "4C": {"description": "Mixed-Marine",   "HDD_base65": 4500, "CDD_base65":  300, "heating_dominated": False, "cooling_dominated": False},
    "5A": {"description": "Cool-Humid",     "HDD_base65": 6500, "CDD_base65":  700, "heating_dominated": True,  "cooling_dominated": False},
    "5B": {"description": "Cool-Dry",       "HDD_base65": 6000, "CDD_base65":  500, "heating_dominated": True,  "cooling_dominated": False},
    "5C": {"description": "Cool-Marine",    "HDD_base65": 6000, "CDD_base65":  200, "heating_dominated": True,  "cooling_dominated": False},
    "6A": {"description": "Cold-Humid",     "HDD_base65": 8000, "CDD_base65":  300, "heating_dominated": True,  "cooling_dominated": False},
    "6B": {"description": "Cold-Dry",       "HDD_base65": 8000, "CDD_base65":  200, "heating_dominated": True,  "cooling_dominated": False},
    "7":  {"description": "Very Cold",      "HDD_base65": 10000,"CDD_base65":  100, "heating_dominated": True,  "cooling_dominated": False},
    "8":  {"description": "Subarctic",      "HDD_base65": 14000,"CDD_base65":   50, "heating_dominated": True,  "cooling_dominated": False},
    # Generic international zones
    "TROPICAL":    {"description": "Tropical",    "HDD_base65": 0,    "CDD_base65": 5000, "heating_dominated": False, "cooling_dominated": True},
    "SUBTROPICAL": {"description": "Subtropical", "HDD_base65": 500,  "CDD_base65": 3000, "heating_dominated": False, "cooling_dominated": True},
    "TEMPERATE":   {"description": "Temperate",   "HDD_base65": 4000, "CDD_base65": 1000, "heating_dominated": False, "cooling_dominated": False},
    "HIGHLAND":    {"description": "Highland",    "HDD_base65": 6000, "CDD_base65":  400, "heating_dominated": True,  "cooling_dominated": False},
    "ARID":        {"description": "Arid",        "HDD_base65": 2000, "CDD_base65": 2500, "heating_dominated": False, "cooling_dominated": True},
    "CONTINENTAL": {"description": "Continental", "HDD_base65": 7000, "CDD_base65":  800, "heating_dominated": True,  "cooling_dominated": False},
    "OCEANIC":     {"description": "Oceanic",     "HDD_base65": 5000, "CDD_base65":  400, "heating_dominated": True,  "cooling_dominated": False},
}

_CLIMATE_UNKNOWN = {
    "description": "Unknown", "HDD_base65": None, "CDD_base65": None,
    "heating_dominated": None, "cooling_dominated": None,
}

# EUI benchmark lookup by sector (EIA CBECS 2018 / ENERGY STAR / sector norms)
# Values in kBtu/sqft/yr (median)
_EUI_BENCHMARKS: dict[str, dict] = {
    "commercial_real_estate": {"median_EUI_kBtu_sqft": 74.9,  "source": "EIA_CBECS_2018_office"},
    "industrial":             {"median_EUI_kBtu_sqft": 95.0,  "source": "EIA_CBECS_2018_industrial"},
    "manufacturing":          {"median_EUI_kBtu_sqft": 120.0, "source": "EIA_MECS_2018_manufacturing"},
    "energy":                 {"median_EUI_kBtu_sqft": 200.0, "source": "sector_norm_energy_facilities"},
    "healthcare":             {"median_EUI_kBtu_sqft": 250.0, "source": "EIA_CBECS_2018_healthcare"},
    "education":              {"median_EUI_kBtu_sqft": 62.0,  "source": "EIA_CBECS_2018_education"},
    "hospitality":            {"median_EUI_kBtu_sqft": 130.0, "source": "EIA_CBECS_2018_lodging"},
    "data_center":            {"median_EUI_kBtu_sqft": 400.0, "source": "ENERGY_STAR_DataCenter_2019"},
    "retail":                 {"median_EUI_kBtu_sqft": 60.0,  "source": "EIA_CBECS_2018_retail"},
    "default":                {"median_EUI_kBtu_sqft": 80.0,  "source": "EIA_CBECS_2018_all_buildings_median"},
}

# EUI climate adjustment factors by zone group
_CLIMATE_EUI_ADJUSTMENT: dict[str, float] = {
    "1A": 0.85, "1B": 0.90, "2A": 0.92, "2B": 0.95,
    "3A": 1.00, "3B": 1.00, "3C": 0.95,
    "4A": 1.10, "4B": 1.05, "4C": 1.00,
    "5A": 1.15, "5B": 1.10, "5C": 1.05,
    "6A": 1.20, "6B": 1.18,
    "7": 1.30, "8": 1.40,
    "TROPICAL": 0.85, "SUBTROPICAL": 0.90, "TEMPERATE": 1.05,
    "HIGHLAND": 1.15, "ARID": 0.95, "CONTINENTAL": 1.20, "OCEANIC": 1.05,
}

# Regulatory framework lookup by jurisdiction_code prefix
_REGULATORY_FRAMEWORKS: dict[str, dict] = {
    "US-NY-NYC": {
        "primary":    "NYC_Local_Law_97_2019",
        "secondary":  ["NYSERDA_programs", "NYC_Green_Buildings", "NYC_Energy_Conservation_Code"],
        "notes":      "LL97 applies to buildings >25,000 sqft. Annual reports due May 1.",
    },
    "US-CA":     {
        "primary":    "California_Title_24",
        "secondary":  ["CALGreen", "CPUC_programs", "AB32_GHG"],
        "notes":      "Title 24 is California's Building Energy Efficiency Standards.",
    },
    "US":        {
        "primary":    "ASHRAE_90.1",
        "secondary":  ["DOE_EECBG", "ENERGY_STAR"],
        "notes":      "Federal baseline: ASHRAE 90.1 energy efficiency standard.",
    },
    "CO":        {
        "primary":    "RETIE_CREG",
        "secondary":  ["UPME_programs", "PROURE_efficiency"],
        "notes":      "Colombia: RETIE electrical safety, CREG energy regulatory framework.",
    },
    "MX":        {
        "primary":    "NOM_ENER",
        "secondary":  ["CONUEE_programs"],
        "notes":      "Mexico: NOM-ENER energy efficiency standards.",
    },
    "EU":        {
        "primary":    "EPBD_EU",
        "secondary":  ["EN_15232", "ISO_50001"],
        "notes":      "EU Energy Performance of Buildings Directive.",
    },
    "GB":        {
        "primary":    "UK_Building_Regulations_Part_L",
        "secondary":  ["ESOS", "SECR", "UK_EPC"],
        "notes":      "UK Building Regulations Part L, Energy Savings Opportunity Scheme.",
    },
    "AU":        {
        "primary":    "NCC_Section_J",
        "secondary":  ["NABERS", "CBD_program"],
        "notes":      "Australia: National Construction Code Section J, NABERS rating.",
    },
    "SG":        {
        "primary":    "BCA_Green_Mark",
        "secondary":  ["NEA_programs", "EEO"],
        "notes":      "Singapore: BCA Green Mark scheme.",
    },
    "DEFAULT":   {
        "primary":    "ISO_50001",
        "secondary":  ["ASHRAE_90.1_international", "IEA_best_practice"],
        "notes":      "International baseline: ISO 50001 energy management systems.",
    },
}


def _get_climate_data(zone_code: str) -> dict:
    """Return climate data for the given zone code, with safe fallback."""
    if not zone_code:
        return _CLIMATE_UNKNOWN.copy()
    key = str(zone_code).strip().upper()
    return _CLIMATE_DATA.get(key, _CLIMATE_UNKNOWN.copy())


def _get_eui_benchmark(sector: str) -> dict:
    """Return EUI benchmark for the given sector."""
    return _EUI_BENCHMARKS.get(sector, _EUI_BENCHMARKS["default"]).copy()


def _get_regulatory_framework(jurisdiction_codes: list[str]) -> dict:
    """Return regulatory framework matched by jurisdiction_code prefix (longest match wins)."""
    if not jurisdiction_codes:
        return _REGULATORY_FRAMEWORKS["DEFAULT"]
    for code in jurisdiction_codes:
        c = str(code).upper()
        # Try progressively longer prefixes in order of specificity
        for key in sorted(_REGULATORY_FRAMEWORKS.keys(), key=len, reverse=True):
            if key == "DEFAULT":
                continue
            if c.startswith(key):
                return _REGULATORY_FRAMEWORKS[key]
    return _REGULATORY_FRAMEWORKS["DEFAULT"]


def _target_type_to_sector(target_type: str) -> str:
    t = (target_type or "").strip().lower()
    mapping = {
        "commercial_building": "commercial_real_estate",
        "multifamily_building": "commercial_real_estate",
        "warehouse_distribution": "industrial",
        "industrial_plant": "industrial",
        "manufacturing_facility": "manufacturing",
        "food_processing_facility": "manufacturing",
        "cold_chain_facility": "industrial",
        "infrastructure_node": "energy",
        "oil_gas_upstream_site": "energy",
        "oil_gas_midstream_facility": "energy",
        "oil_gas_downstream_facility": "energy",
        "hospital": "healthcare",
        "hotel": "hospitality",
        "data_center": "data_center",
    }
    return mapping.get(t, "commercial_real_estate")


def _target_family(target_type: str) -> str:
    t = (target_type or "").strip().lower()
    if t == "warehouse_distribution":
        return "logistics"
    if t in {
        "industrial_plant",
        "manufacturing_facility",
        "food_processing_facility",
        "cold_chain_facility",
    }:
        return "manufacturing"
    if t == "infrastructure_node":
        return "infrastructure"
    if t in {
        "oil_gas_upstream_site",
        "oil_gas_midstream_facility",
        "oil_gas_downstream_facility",
    }:
        return "oil_gas"
    return "building"


def _benchmark_measurement_label(target_type: str) -> str:
    family = _target_family(target_type)
    if family == "manufacturing":
        return "metered asset-level process data"
    if family == "infrastructure":
        return "metered asset-level duty and metering data"
    if family == "oil_gas":
        return "metered asset-level process, fuel, and emissions data"
    if family == "logistics":
        return "metered asset-level logistics and refrigeration data"
    return "metered building data"


def _applicability_threshold_reason(target_type: str) -> str:
    family = _target_family(target_type)
    if family == "manufacturing":
        return "Asset size and in-scope process footprint commonly control applicability thresholds."
    if family == "infrastructure":
        return "In-scope node scale and major equipment boundary commonly control applicability thresholds."
    if family == "oil_gas":
        return "In-scope unit scale and emissions-bearing equipment commonly control applicability thresholds."
    if family == "logistics":
        return "Asset size and refrigerated or dock footprint commonly control applicability thresholds."
    return "Asset size commonly controls building-performance-rule applicability."


def _inject_asset_discovery(fi: dict, enriched: dict) -> dict:
    runtime_fi = deepcopy(fi)
    loc = runtime_fi.setdefault("input_01_location", {})
    size = runtime_fi.setdefault("input_05_size", {})
    vintage = runtime_fi.setdefault("input_06_vintage", {})
    primary_use = runtime_fi.setdefault("input_04_primary_use", {})
    geocoder = enriched.get("asset_geocoder", {}) if isinstance(enriched.get("asset_geocoder", {}), dict) else {}
    coords = geocoder.get("coordinates", {}) if isinstance(geocoder.get("coordinates", {}), dict) else {}
    if coords.get("x") and not loc.get("lon"):
        loc["lon"] = coords.get("x")
    if coords.get("y") and not loc.get("lat"):
        loc["lat"] = coords.get("y")
    if not loc.get("county_fips"):
        counties = ((geocoder.get("geographies") or {}).get("Counties") or [])
        if counties and isinstance(counties[0], dict):
            loc["county_fips"] = counties[0].get("GEOID", "")
    climate = enriched.get("asset_climate_zone", {}) if isinstance(enriched.get("asset_climate_zone", {}), dict) else {}
    climate_attrs = climate.get("climate_zone_data", {}) if isinstance(climate.get("climate_zone_data", {}), dict) else {}
    if climate_attrs and not loc.get("climate_zone_ASHRAE"):
        loc["climate_zone_ASHRAE"] = (
            climate_attrs.get("Climate Zone")
            or climate_attrs.get("climate_zone")
            or climate_attrs.get("CZ")
            or ""
        )
    pluto_record = _nyc_pluto_record(enriched)
    if pluto_record:
        if not loc.get("bbl"):
            loc["bbl"] = _safe_text(_first_present(pluto_record, ["bbl", "borough_block_lot"]))
        if not loc.get("bin"):
            loc["bin"] = _safe_text(_first_present(pluto_record, ["bin", "building_id_number"]))
        pluto_gfa = _as_number(_first_present(pluto_record, ["bldgarea", "gross_floor_area", "gross_sqft", "building_area"]))
        if pluto_gfa and not size.get("GFA_sqft"):
            size["GFA_sqft"] = pluto_gfa
        pluto_site_area = _as_number(_first_present(pluto_record, ["lotarea", "site_area", "land_area_sqft"]))
        if pluto_site_area and not size.get("site_area_sqft"):
            size["site_area_sqft"] = pluto_site_area
        pluto_floors = _as_number(_first_present(pluto_record, ["numfloors", "floors", "stories"]))
        if pluto_floors and not (size.get("floor_count") or size.get("floors") or size.get("stories")):
            size["floor_count"] = pluto_floors
        year_built = _as_number(_first_present(pluto_record, ["yearbuilt", "year_built"]))
        if year_built and not vintage.get("year_built"):
            vintage["year_built"] = int(year_built)
        probable_use = _safe_text(_first_present(pluto_record, ["landuse", "building_class", "bldgclass", "primary_use"]))
        existing_uses = primary_use.get("uses", []) if isinstance(primary_use.get("uses", []), list) else []
        if probable_use and not existing_uses:
            primary_use["uses"] = [probable_use]
    benchmark_payload = _local_benchmark_payload(enriched)
    benchmark_data = benchmark_payload.get("data", {}) if isinstance(benchmark_payload.get("data", {}), dict) else {}
    benchmark_record = _local_benchmark_record(enriched)
    if benchmark_data.get("gross_floor_area_sqft") and not size.get("GFA_sqft"):
        size["GFA_sqft"] = benchmark_data.get("gross_floor_area_sqft")
    if benchmark_record:
        local_gfa = _as_number(
            _first_present(
                benchmark_record,
                ["floor_area", "gross_floor_area", "gross_floor_area_sqft", "building_area", "area_sqft"],
            )
        )
        if local_gfa and not size.get("GFA_sqft"):
            size["GFA_sqft"] = local_gfa
        local_year_built = _as_number(_first_present(benchmark_record, ["year_built", "yearbuilt"]))
        if local_year_built and not vintage.get("year_built"):
            vintage["year_built"] = int(local_year_built)
    ll84_record = _nyc_latest_ll84_record(enriched)
    if ll84_record:
        if not loc.get("bbl"):
            loc["bbl"] = _safe_text(_first_present(ll84_record, ["nyc_borough_block_and_lot", "bbl"]))
        if not loc.get("bin"):
            loc["bin"] = _safe_text(_first_present(ll84_record, ["nyc_building_identification", "bin", "building_id"]))
        largest_use = _safe_text(_first_present(ll84_record, ["largest_property_use_type", "primary_property_type_self", "primary_property_type", "primary_property_type_self_selected"]))
        existing_uses = primary_use.get("uses", []) if isinstance(primary_use.get("uses", []), list) else []
        if largest_use and not existing_uses:
            primary_use["uses"] = [largest_use]
    permit_summary = _nyc_dob_permit_summary(enriched)
    if permit_summary and permit_summary.get("permit_summary") and not vintage.get("major_renovations_known"):
        vintage["major_renovations_known"] = [
            {
                "permit_summary": permit_summary.get("permit_summary"),
                "latest_issuance_date": permit_summary.get("latest_issuance_date"),
            }
        ]
    return runtime_fi


def _build_asset_identity_bundle(
    target_definition: dict[str, Any],
    asset_context_readiness: str,
    observable_cluster_register: dict[str, Any],
    missing_clusters: list[str],
    fi: dict[str, Any],
) -> dict[str, Any]:
    loc = fi.get("input_01_location", {})
    return {
        "entity_type": "AssetIdentity",
        "target_scope": target_definition.get("target_scope", "asset"),
        "target_type": target_definition.get("target_type", "commercial_building"),
        "target_identifier": target_definition.get("target_identifier", ""),
        "target_name": target_definition.get("target_name", ""),
        "address_raw": target_definition.get("address_raw", ""),
        "jurisdiction_scope": target_definition.get("jurisdiction_scope", []),
        "asset_context_readiness": asset_context_readiness,
        "observable_cluster_register": observable_cluster_register,
        "missing_observable_clusters": missing_clusters,
        "latitude": loc.get("lat"),
        "longitude": loc.get("lon"),
        "county_fips": loc.get("county_fips", ""),
        "technical_prior_ceiling": (
            "asset_context_insufficient"
            if asset_context_readiness in {"issuer_context_only", "location_only", "asset_context_insufficient"}
            else "preliminary_asset_prior"
        ),
        "epistemic_status": "Decision-grade — asset identity boundary, not site verification",
    }


def _build_operating_archetype_bundle(target_definition: dict[str, Any], fi: dict[str, Any]) -> dict[str, Any]:
    target_type = target_definition.get("target_type", "commercial_building")
    schedule = fi.get("input_07_operating_schedule", {})
    use_values = fi.get("input_04_primary_use", {}).get("uses", [])
    default_mode = {
        "commercial_building": "weekday_peak_office",
        "multifamily_building": "residential_morning_evening",
        "warehouse_distribution": "shift_based_logistics",
        "industrial_plant": "mixed_shift_industrial_operations",
        "manufacturing_facility": "process_shift_production",
        "food_processing_facility": "process_and_refrigeration_continuous",
        "cold_chain_facility": "refrigeration_dominant_24_7",
        "infrastructure_node": "utility_or_network_service_continuous",
        "oil_gas_upstream_site": "field_operations_continuous",
        "oil_gas_midstream_facility": "compression_transport_continuous",
        "oil_gas_downstream_facility": "process_continuous_high_thermal",
        "hospital": "clinical_24_7",
        "hotel": "hospitality_24_7_variable",
        "data_center": "it_cooling_24_7",
    }.get(target_type, "generic_asset_operation")
    return {
        "entity_type": "OperatingArchetype",
        "target_type": target_type,
        "declared_schedule_present": bool(schedule),
        "declared_schedule": schedule,
        "declared_use_mix": use_values,
        "operating_regime_expectation": default_mode,
        "schedule_confidence": "declared" if schedule else "archetypal_only",
        "epistemic_status": "Decision-grade — archetypal operating prior",
    }


def _build_system_typology_prior(target_definition: dict[str, Any], fi: dict[str, Any]) -> dict[str, Any]:
    target_type = target_definition.get("target_type", "commercial_building")
    known_systems = list((fi.get("input_09_known_systems") or {}).keys())
    default_systems = {
        "commercial_building": [
            "hvac_airside",
            "cooling_or_heating_plant",
            "lighting_controls",
            "vertical_transport",
            "tenant_metering_or_submetering",
            "bms_or_ems",
        ],
        "multifamily_building": ["central_heating_or_ptac", "domestic_hot_water", "corridor_ventilation"],
        "warehouse_distribution": ["roof_top_units", "dock_equipment", "lighting_high_bay"],
        "industrial_plant": ["motors_and_drives", "compressed_air", "process_support_utilities", "ventilation_or_exhaust"],
        "manufacturing_facility": [
            "process_motors_and_drives",
            "compressed_air",
            "process_heat_or_curing",
            "dust_or_voc_control",
            "material_handling",
            "process_ventilation",
        ],
        "food_processing_facility": ["refrigeration", "process_heat", "compressed_air", "washdown_water_heating"],
        "cold_chain_facility": ["refrigeration", "insulated_envelope", "defrost_controls", "dock_air_management"],
        "infrastructure_node": ["substation_or_transformer", "power_conversion", "controls", "backup_or_redundancy"],
        "oil_gas_upstream_site": ["pumps", "separators", "flare_or_vent_controls", "field_power"],
        "oil_gas_midstream_facility": ["compression", "pumping", "controls", "fugitive_emissions_monitoring"],
        "oil_gas_downstream_facility": ["fired_heaters", "steam_generation", "process_cooling", "controls"],
        "hospital": ["air_handling", "chilled_water", "steam_or_hot_water", "critical_power"],
        "hotel": ["guestroom_hvac", "hot_water", "laundry", "kitchen_exhaust"],
        "data_center": ["ups", "cooling", "generator_backup", "bms_dcim"],
    }.get(target_type, ["general_mep_systems"])
    return {
        "entity_type": "SystemTypologyPrior",
        "target_type": target_type,
        "declared_known_systems": known_systems,
        "expected_system_families": default_systems,
        "system_prior_mode": "declared_plus_archetypal" if known_systems else "archetypal_only",
        "epistemic_status": "Decision-grade — plausible system topology prior",
    }


def _build_asset_energy_behavior_prior(
    target_definition: dict[str, Any],
    benchmark_context: dict[str, Any],
    climate_entity: dict[str, Any],
    fi: dict[str, Any],
) -> dict[str, Any]:
    target_type = target_definition.get("target_type", "commercial_building")
    primary_use = fi.get("input_04_primary_use", {}).get("uses", [])
    profiles = {
        "commercial_building": {
            "end_use_split_hypothesis": ["hvac", "lighting", "tenant_plug_loads", "central_plant_auxiliaries"],
            "load_shape_hypothesis": "weekday_occupied_peak_with_after_hours_base_load",
            "operating_regime_expectation": "daytime_office_with_after_hours_tenant_and_common_area_load",
            "system_typology_expectation": "airside_hvac_plus_central_plant_plus_tenant_metering_if_large",
            "peak_behavior_expectation": "summer_cooling_winter_heating_and_after_hours_base_load_sensitivity",
            "anomaly_candidates": [
                "tenant_metering_blind_spot",
                "central_plant_baseload",
                "after_hours_tenant_load",
                "steam_or_gas_transition_constraint",
            ],
            "critical_evidence_drivers": [
                "tenant_metering_basis",
                "lease_responsibility_matrix",
                "central_plant_topology",
                "occupancy_use_mix",
                "steam_gas_electrification_basis",
            ],
        },
        "industrial_plant": {
            "end_use_split_hypothesis": ["motors", "compressed_air", "process_support", "ventilation"],
            "load_shape_hypothesis": "shift_and_equipment_duty_driven",
            "operating_regime_expectation": "mixed_shift_industrial_operations",
            "system_typology_expectation": "industrial_support_systems_plus_process_equipment",
            "peak_behavior_expectation": "production_schedule_and_equipment_dispatch_sensitive",
        },
        "manufacturing_facility": {
            "end_use_split_hypothesis": [
                "process_heat_or_curing",
                "press_or_line_motors",
                "compressed_air",
                "dust_or_voc_capture",
                "material_handling",
            ],
            "load_shape_hypothesis": "shift_process_and_thermal_duty_driven",
            "operating_regime_expectation": "multi_shift_or_continuous_process",
            "system_typology_expectation": "process_equipment_plus_thermal_and_environmental_support_systems",
            "peak_behavior_expectation": "production_throughput_and_thermal_cycle_sensitive",
            "anomaly_candidates": [
                "resin_or_press_thermal_drift",
                "compressed_air_leakage",
                "dust_or_voc_capture_penalty",
                "thermal_oil_or_boiler_loss",
                "material_handling_idle_load",
            ],
            "critical_evidence_drivers": [
                "naics_sic_process_family",
                "resin_press_curing_inventory",
                "compressed_air_topology",
                "dust_collection_and_voc_capture",
                "thermal_oil_steam_boiler_basis",
                "material_handling_profile",
                "wastewater_and_air_permits",
                "throughput_and_downtime_profile",
            ],
        },
        "food_processing_facility": {
            "end_use_split_hypothesis": ["refrigeration", "process_heat", "motors", "washdown_hot_water"],
            "load_shape_hypothesis": "refrigeration_base_load_plus_shift_process_peaks",
            "operating_regime_expectation": "continuous_cold_chain_or_batch_processing",
            "system_typology_expectation": "refrigeration_plus_process_heat",
            "peak_behavior_expectation": "strong refrigeration_and_sanitation_cycle_loads",
            "anomaly_candidates": ["sanitation_cycle_spikes", "cold_storage_base_load", "hot_water_cleanup_events"],
            "critical_evidence_drivers": ["production_calendar", "sanitation_schedule", "refrigeration_inventory", "wastewater_or_pretreatment_profile"],
        },
        "cold_chain_facility": {
            "end_use_split_hypothesis": ["refrigeration", "fans", "dock_losses"],
            "load_shape_hypothesis": "continuous_base_load",
            "operating_regime_expectation": "24_7_temperature_control",
            "system_typology_expectation": "refrigeration_dominant",
            "peak_behavior_expectation": "ambient_weather_and_door_cycle_sensitive",
            "anomaly_candidates": ["door_infiltration_losses", "defrost_cycle_peaks", "refrigerant_leak_or_charge_loss"],
            "critical_evidence_drivers": ["temperature_zone_map", "defrost_schedule", "refrigerant_charge_and_leak_history", "dock_cycle_profile"],
        },
        "infrastructure_node": {
            "end_use_split_hypothesis": ["power_conversion", "controls", "redundancy", "network_service_loads"],
            "load_shape_hypothesis": "service_and_reliability_duty_driven",
            "operating_regime_expectation": "continuous_network_or_utility_service",
            "system_typology_expectation": "grid_or_network_support_equipment",
            "peak_behavior_expectation": "throughput_dispatch_and_reliability_sensitive",
            "anomaly_candidates": ["station_service_loss_drift", "redundancy_penalty_load", "dispatch_or_outage_duty_spikes"],
            "critical_evidence_drivers": ["one_line_boundary", "dispatch_profile", "station_service_metering", "backup_or_redundancy_basis"],
        },
        "oil_gas_upstream_site": {
            "end_use_split_hypothesis": ["pumping", "separation", "field_power"],
            "load_shape_hypothesis": "throughput_and_field_conditions_driven",
            "operating_regime_expectation": "continuous_field_operations",
            "system_typology_expectation": "pumps_controls_field_utilities",
            "peak_behavior_expectation": "production_and_compression_sensitive",
            "anomaly_candidates": ["flare_or_vent_events", "artificial_lift_power_swings", "produced_water_handling_load"],
            "critical_evidence_drivers": ["well_or_lift_inventory", "flare_and_vent_basis", "associated_fuel_profile", "produced_water_or_disposal_profile"],
        },
        "oil_gas_midstream_facility": {
            "end_use_split_hypothesis": ["compression", "pumping", "controls"],
            "load_shape_hypothesis": "transport_duty_driven",
            "operating_regime_expectation": "continuous_transport_service",
            "system_typology_expectation": "compression_and_pumping",
            "peak_behavior_expectation": "throughput_and_pressure_sensitive",
            "anomaly_candidates": ["compressor_efficiency_drift", "linepack_variability", "methane_control_or_blowdown_events"],
            "critical_evidence_drivers": ["compression_train_inventory", "linepack_profile", "methane_monitoring_basis", "fuel_and_throughput_by_train"],
        },
        "oil_gas_downstream_facility": {
            "end_use_split_hypothesis": ["process_heat", "steam", "cooling", "motors"],
            "load_shape_hypothesis": "continuous_process_with_turnaround_events",
            "operating_regime_expectation": "continuous_refining_or_processing",
            "system_typology_expectation": "thermal_process_dominant",
            "peak_behavior_expectation": "process_and_thermal_load_sensitive",
            "anomaly_candidates": ["steam_balance_loss", "heater_efficiency_drift", "flare_or_relief_event_load"],
            "critical_evidence_drivers": ["steam_balance", "fired_heater_basis", "flare_history", "turnaround_calendar"],
        },
    }
    profile = profiles.get(target_type, profiles["commercial_building"])
    return {
        "entity_type": "AssetEnergyBehaviorPrior",
        "target_type": target_type,
        "primary_use_declared": primary_use,
        "sector_energy_intensity_band": benchmark_context.get("adjusted_EUI_estimate_kBtu_sqft"),
        "benchmark_source": benchmark_context.get("benchmark_source", ""),
        "climate_zone": climate_entity.get("climate_zone_ASHRAE", ""),
        "climate_sensitivity_expectation": (
            "heating_dominated" if climate_entity.get("heating_dominated")
            else "cooling_dominated" if climate_entity.get("cooling_dominated")
            else "mixed_climate_response"
        ),
        **profile,
        "epistemic_status": "Decision-grade — archetypal energy behavior prior",
    }


def _prior_id(case_id: str) -> str:
    return "fp:" + hashlib.sha256(case_id.encode()).hexdigest()[:12]


def _lineage_id(case_id: str) -> str:
    return "lin:" + hashlib.sha256(f"lineage:{case_id}".encode()).hexdigest()[:12]


def _coverage_gap_types(m28: dict[str, Any], enriched: dict[str, Any]) -> list[str]:
    if enriched.get("coverage_gaps"):
        return [str(g) for g in enriched.get("coverage_gaps", []) if g]
    gap_objects = m28.get("coverage_gaps", [])
    return [
        g.get("gap_type", "")
        for g in gap_objects
        if isinstance(g, dict) and g.get("gap_type")
    ]


def _build_evidence_lineage(case_id: str, produced_at: str, m28: dict[str, Any], enriched: dict[str, Any]) -> dict[str, Any]:
    summary = m28.get("discovery_summary", {}) if isinstance(m28.get("discovery_summary", {}), dict) else {}
    candidates = m28.get("discovery_candidates", [])
    attempts = m28.get("discovery_attempts", [])
    admitted_source_types = sorted({
        c.get("source_type", "")
        for c in candidates
        if isinstance(c, dict) and c.get("source_type")
    })
    financials = enriched.get("financials", {})
    return {
        "lineage_id": _lineage_id(case_id),
        "trace_scope": "source_to_facility_prior",
        "produced_at": produced_at,
        "upstream_motor_id": "motor_028",
        "contract_total": summary.get("contract_total", 0),
        "applicable_contract_total": summary.get("applicable_contract_total", summary.get("contract_total", 0)),
        "attempted": summary.get("attempted", len(attempts)),
        "applicable_attempted": summary.get("applicable_attempted", 0),
        "admitted_candidates": len(candidates),
        "found_sources": summary.get("found", 0),
        "no_data_sources": summary.get("no_data", 0),
        "failed_sources": summary.get("failed", 0),
        "context_missing_sources": summary.get("context_missing", 0),
        "not_applicable_sources": summary.get("not_applicable", 0),
        "tracking_complete": summary.get("tracking_complete", False),
        "applicable_tracking_complete": summary.get("applicable_tracking_complete", False),
        "admitted_source_types": admitted_source_types,
        "coverage_gap_types": _coverage_gap_types(m28, enriched),
        "financial_lineage": {
            "financials_present": bool(financials),
            "filing_date": financials.get("filing_date", ""),
            "financial_source_types": [
                st for st in admitted_source_types
                if st in {"sec_edgar_submissions", "sec_edgar_xbrl_facts", "sec_10k_full_text_extraction", "esrt_10k_html_extraction"}
            ],
        },
        "trace_chain": [
            "motor_028.discovery_attempts",
            "motor_028.discovery_candidates",
            "motor_028.coverage_gaps",
            "motor_028.enriched_data",
            "motor_012.facility_prior",
        ],
    }


def _build_facility_entity(fi: dict) -> dict:
    loc = fi.get("input_01_location", {})
    ftype = fi.get("input_02_facility_type", {})
    size = fi.get("input_05_size", {})
    vintage = fi.get("input_06_vintage", {})
    return {
        "entity_type": "Facility",
        "address": loc.get("address", ""),
        "city": loc.get("city", ""),
        "state": loc.get("state", ""),
        "country": loc.get("country", ""),
        "jurisdiction": loc.get("jurisdiction_codes", []),
        "primary_classification": ftype.get("primary_classification", ""),
        "secondary_classification": ftype.get("secondary_classification", ""),
        "asset_category": ftype.get("asset_category", ""),
        "building_class": ftype.get("building_class", ""),
        "construction_type": ftype.get("construction_type", ""),
        "landmark_status": ftype.get("landmark_status", ""),
        "GFA_sqft": size.get("GFA_sqft"),
        "GFA_m2": size.get("GFA_m2"),
        "floors_total": size.get("floors_total"),
        "height_ft": size.get("height_ft"),
        "height_m": size.get("height_m"),
        "rentable_office_sqft_approx": size.get("rentable_office_sqft_approx"),
        "year_built": vintage.get("year_built"),
        "years_old": vintage.get("years_old"),
        "major_renovations": vintage.get("major_renovations_known", []),
        "certifications": [
            r.get("certification") for r in vintage.get("major_renovations_known", [])
            if r.get("certification")
        ],
        "vintage_category": vintage.get("vintage_category"),
        "data_provenance": "facility_inputs[input_01–input_06]",
        "epistemic_status": "Decision-grade",
    }


def _build_jurisdiction_entity(fi: dict, enriched: dict) -> dict:
    loc = fi.get("input_01_location", {})
    zone = loc.get("climate_zone_ASHRAE") or loc.get("climate_zone", "")
    climate = _get_climate_data(zone)
    jurisdiction_codes = loc.get("jurisdiction_codes", [])
    reg = _get_regulatory_framework(jurisdiction_codes)
    return {
        "entity_type": "Jurisdiction",
        "jurisdiction_codes": jurisdiction_codes,
        "state": loc.get("state", ""),
        "country": loc.get("country", ""),
        "county": loc.get("county", ""),
        "climate_zone_ASHRAE": zone,
        "HDD_base65": climate.get("HDD_base65"),
        "CDD_base65": climate.get("CDD_base65"),
        "micro_climate_note": loc.get("micro_climate_note", ""),
        "primary_regulatory_framework": reg["primary"],
        "secondary_regulatory_frameworks": reg["secondary"],
        "regulatory_notes": reg["notes"],
        "utility_electric": loc.get("utility_electric", ""),
        "utility_gas": loc.get("utility_gas", ""),
        "data_provenance": "facility_inputs[input_01] + public_regulatory_database",
        "epistemic_status": "Decision-grade",
    }


def _build_climate_entity(fi: dict) -> dict:
    loc = fi.get("input_01_location", {})
    zone = loc.get("climate_zone_ASHRAE") or loc.get("climate_zone", "")
    climate = _get_climate_data(zone)
    sector = fi.get("input_03_sector", {}).get("sector", "commercial_real_estate")
    eui_adj = _CLIMATE_EUI_ADJUSTMENT.get(str(zone).strip().upper(), 1.0)
    return {
        "entity_type": "ClimateContext",
        "ASHRAE_zone": zone,
        "zone_description": climate.get("description", "Unknown"),
        "HDD_base65": climate.get("HDD_base65"),
        "CDD_base65": climate.get("CDD_base65"),
        "heating_dominated": climate.get("heating_dominated"),
        "cooling_dominated": climate.get("cooling_dominated"),
        "dual_season_relevance": (
            not climate.get("heating_dominated", False)
            and not climate.get("cooling_dominated", False)
        ),
        "urban_heat_island": loc.get("micro_climate_note", ""),
        "benchmark_EUI_adjustment_factor": eui_adj,
        "data_provenance": "ASHRAE_climate_data_public + facility_inputs[input_01]",
        "epistemic_status": "Decision-grade",
    }


def _build_sector_archetype(fi: dict, enriched: dict) -> dict:
    sector = fi.get("input_03_sector", {})
    primary_use = fi.get("input_04_primary_use", {})
    financials = enriched.get("financials", {})

    # Build use_mix from whatever use keys are present
    use_mix: dict[str, Any] = {}
    for i in range(1, 6):
        use_key = primary_use.get(f"use_{i}")
        pct_key = primary_use.get(f"use_{i}_approx_pct")
        if use_key:
            use_mix[use_key] = pct_key

    return {
        "entity_type": "SectorArchetype",
        "sector": sector.get("sector", ""),
        "subsector": sector.get("subsector", ""),
        "naic_code": sector.get("naic_code", ""),
        "ownership_structure": sector.get("ownership_structure", ""),
        "owner_ticker": sector.get("owner_ticker", ""),
        "owner_exchange": sector.get("owner_exchange", ""),
        "owner_cik": sector.get("owner_cik", ""),
        "company_name_sec": enriched.get("company_name", sector.get("company_name", "")),
        "revenues_annual_usd": financials.get("revenues_annual"),
        "total_debt_usd": financials.get("total_debt"),
        "total_assets_usd": financials.get("total_assets"),
        "use_mix": use_mix,
        "anchor_tenant": primary_use.get("anchor_tenant"),
        "anchor_tenant_sqft": primary_use.get("anchor_tenant_approx_sqft"),
        "major_tenants": primary_use.get("major_tenants_known", []),
        "customer_concentration": primary_use.get("customer_concentration"),
        "secondary_sector": sector.get("secondary_sector"),
        "archetype_note": sector.get("archetype_note", ""),
        "primary_fuel": fi.get("input_08_energy_fuel", {}).get("primary_fuel", ""),
        "secondary_fuel": fi.get("input_08_energy_fuel", {}).get("secondary_fuel", ""),
        "data_provenance": "facility_inputs[input_03–input_04] + financial_enrichment",
        "epistemic_status": "Decision-grade",
    }


def _build_benchmark_context(fi: dict, target_type: str, enriched: dict | None = None) -> dict:
    size = fi.get("input_05_size", {})
    sector = _target_type_to_sector(target_type)
    loc = fi.get("input_01_location", {})
    zone = loc.get("climate_zone_ASHRAE") or loc.get("climate_zone", "")
    routing = (enriched or {}).get("benchmark_routing_register", {}) if isinstance((enriched or {}).get("benchmark_routing_register", {}), dict) else {}
    ll84_record = _nyc_latest_ll84_record(enriched or {})
    local_benchmark_payload = _local_benchmark_payload(enriched or {})
    local_benchmark_record = _local_benchmark_record(enriched or {})
    local_source_type = _safe_text(routing.get("selected_source_type"))

    if ll84_record:
        eui = _first_present(
            ll84_record,
            [
                "weather_normalized_site_eui_kbtu_ft",
                "weather_normalized_site_eui",
                "site_eui_kbtu_ft",
                "site_eui",
            ],
        )
        source_eui = _first_present(ll84_record, ["source_eui_kbtu_ft", "source_eui"])
        emissions = _first_present(
            ll84_record,
            [
                "total_location_based_ghg",
                "net_emissions_metric_tons",
                "total_ghg_emissions_metric_tons_co2e",
                "ghg_emissions_metric_tons_co2e",
                "direct_ghg_emissions_metric",
                "direct_ghg_emissions_metric_tons_co2e",
            ],
        )
        reporting_year = _first_present(ll84_record, ["report_year", "reporting_year", "year"])
        energy_star_score = _first_present(ll84_record, ["energy_star_score", "ENERGY_STAR_score"])
        annual_energy = _first_present(
            ll84_record,
            ["site_energy_use_kbtu", "source_energy_use_kbtu", "site_energy_use"],
        )
        return {
            "entity_type": "BenchmarkContext",
            "benchmark_source": "NYC LL84 public disclosure",
            "benchmark_type": "public asset-level benchmarking disclosure",
            "sector_applied": sector,
            "target_type_applied": target_type,
            "sector_median_EUI_kBtu_sqft": _as_number(source_eui) or _as_number(eui),
            "climate_zone_applied": zone,
            "climate_adjustment_factor": 1.0,
            "adjusted_EUI_estimate_kBtu_sqft": _as_number(eui),
            "adjustment_factors_applied": [f"nyc_ll84_reporting_year_{reporting_year}"] if reporting_year else ["nyc_ll84_public_disclosure"],
            "estimated_annual_energy_kBtu": _as_number(annual_energy),
            "benchmark_limitation": "LL84 is annual public benchmarking disclosure. It improves asset-level maturity but does not substitute for interval data or a hardened baseline.",
            "benchmark_routing_register": routing,
            "benchmark_source_id": "nyc_ll84_energy_benchmarking",
            "benchmark_source_scope": "ASSET_LEVEL",
            "benchmark_authority_score": "high",
            "ll84_reporting_year": reporting_year,
            "ll84_emissions_metric_tons_co2e": _as_number(emissions),
            "ll84_energy_star_score": _as_number(energy_star_score),
            "data_provenance": "NYC LL84 public disclosure + facility_inputs[input_01, input_05]",
            "epistemic_status": "Decision-grade / public asset-level benchmarking",
        }

    if local_benchmark_record and local_source_type in {"city_benchmarking_san_francisco", "city_benchmarking_los_angeles"}:
        eui = _first_present(
            local_benchmark_record,
            [
                "weather_normalized_site_eui_kbtu_ft",
                "weather_normalized_site_eui",
                "weather_normalized_3",
                "site_eui_kbtu_ft",
                "site_eui",
            ],
        )
        emissions = _first_present(
            local_benchmark_record,
            [
                "total_ghg_emissions",
                "total_ghg_emissions_metric_tons_co2e",
                "ghg_emissions_metric_tons_co2e",
                "total_location_based_ghg",
            ],
        )
        reporting_year = _first_present(local_benchmark_record, ["benchmark_year", "program_year", "report_year", "reporting_year", "year"])
        energy_star_score = _first_present(local_benchmark_record, ["energy_star_score", "ENERGY_STAR_score"])
        annual_energy = _first_present(
            local_benchmark_record,
            ["site_energy_use_kbtu", "source_energy_use_kbtu", "site_energy_use", "annual_energy_use_kbtu"],
        )
        local_gfa = _as_number(
            _first_present(
                local_benchmark_record,
                ["floor_area", "gross_floor_area", "gross_floor_area_sqft", "building_area", "area_sqft"],
            )
        )
        local_year_built = _as_number(_first_present(local_benchmark_record, ["year_built", "yearbuilt"]))
        local_property_id = _safe_text(
            _first_present(local_benchmark_record, ["parcel_number", "apn", "building_id", "property_id"])
        )
        local_building_id = _safe_text(_first_present(local_benchmark_record, ["building_id", "bin"]))
        source_label = (
            "San Francisco public benchmarking disclosure"
            if local_source_type == "city_benchmarking_san_francisco"
            else "Los Angeles EBEWE public disclosure"
        )
        return {
            "entity_type": "BenchmarkContext",
            "benchmark_source": source_label,
            "benchmark_type": "public asset-level benchmarking disclosure",
            "sector_applied": sector,
            "target_type_applied": target_type,
            "sector_median_EUI_kBtu_sqft": _as_number(eui),
            "climate_zone_applied": zone,
            "climate_adjustment_factor": 1.0,
            "adjusted_EUI_estimate_kBtu_sqft": _as_number(eui),
            "adjustment_factors_applied": [f"local_benchmark_reporting_year_{reporting_year}"] if reporting_year else ["local_benchmark_disclosure"],
            "estimated_annual_energy_kBtu": _as_number(annual_energy),
            "benchmark_limitation": "Local benchmarking disclosure improves asset-level maturity but does not substitute for interval data, bill history, or a hardened baseline.",
            "benchmark_routing_register": routing,
            "benchmark_source_id": local_source_type,
            "benchmark_source_scope": "ASSET_LEVEL",
            "benchmark_authority_score": "high",
            "ll84_reporting_year": reporting_year,
            "ll84_emissions_metric_tons_co2e": _as_number(emissions),
            "ll84_energy_star_score": _as_number(energy_star_score),
            "local_property_id": local_property_id,
            "local_building_id": local_building_id,
            "local_gfa_sqft": local_gfa,
            "local_year_built": local_year_built,
            "data_provenance": f"{source_label} + facility_inputs[input_01, input_05]",
            "epistemic_status": "Decision-grade / public asset-level benchmarking",
        }

    gfa_sqft = size.get("GFA_sqft") or 0
    rentable_sqft = size.get("rentable_office_sqft_approx") or gfa_sqft

    bench = _get_eui_benchmark(sector)
    eui_base = bench["median_EUI_kBtu_sqft"]
    adj_factor = _CLIMATE_EUI_ADJUSTMENT.get(str(zone).strip().upper(), 1.0)
    adj_eui = round(eui_base * adj_factor, 1)
    annual_est = round(rentable_sqft * adj_eui) if rentable_sqft else None

    return {
        "entity_type": "BenchmarkContext",
        "benchmark_source": bench["source"],
        "benchmark_type": (
            "routed asset-type prior — NOT local site evidence"
            if routing
            else "sectoral — NOT local site evidence"
        ),
        "sector_applied": sector,
        "target_type_applied": target_type,
        "sector_median_EUI_kBtu_sqft": eui_base,
        "climate_zone_applied": zone,
        "climate_adjustment_factor": adj_factor,
        "adjusted_EUI_estimate_kBtu_sqft": adj_eui,
        "adjustment_factors_applied": [
            f"climate_zone_{zone}_adjustment_{adj_factor}" if zone else "no_climate_adjustment"
        ],
        "estimated_annual_energy_kBtu": annual_est,
        "benchmark_limitation": (
            f"Benchmark is {bench['source']} sectoral median. "
            f"It is not a site measurement. It does not substitute for {_benchmark_measurement_label(target_type)}."
        ),
        "benchmark_routing_register": routing,
        "benchmark_source_id": str(routing.get("selected_source_type") or bench["source"]),
        "benchmark_source_scope": "BENCHMARK_LEVEL",
        "benchmark_authority_score": "medium",
        "data_provenance": f"{bench['source']} + facility_inputs[input_01, input_03, input_05] + motor_028.benchmark_routing_register",
        "epistemic_status": "Decision-grade / benchmark only",
    }


def _build_energy_context(fi: dict) -> dict:
    energy = fi.get("input_08_energy_fuel", {})
    schedule = fi.get("input_07_operating_schedule", {})
    certifications = [
        r.get("certification")
        for r in fi.get("input_06_vintage", {}).get("major_renovations_known", [])
        if r.get("certification")
    ]
    return {
        "entity_type": "EnergyContext",
        "primary_fuel": energy.get("primary_fuel", ""),
        "primary_fuel_uses": energy.get("primary_fuel_use", ""),
        "secondary_fuel": energy.get("secondary_fuel", ""),
        "secondary_fuel_uses": energy.get("secondary_fuel_use", ""),
        "certifications_declared": certifications,
        "current_EUI_status": "not_confirmed — declared certifications may not reflect current performance",
        "operating_schedule": schedule.get("office_schedule", ""),
        "extended_hours_components": schedule.get("24_7_components", []),
        "utility_electricity": energy.get("utility_electricity", ""),
        "utility_gas": energy.get("utility_gas", ""),
        "energy_risk_note": energy.get("energy_risk_note", ""),
        "recent_EUI_note": energy.get("recent_EUI_note", ""),
        "data_provenance": "facility_inputs[input_07–input_08]",
        "epistemic_status": "Decision-grade",
    }


def _build_regulatory_context(fi: dict) -> dict:
    size = fi.get("input_05_size", {})
    gfa = size.get("GFA_sqft") or size.get("GFA_m2") or 0
    loc = fi.get("input_01_location", {})
    ftype = fi.get("input_02_facility_type", {})
    jurisdiction_codes = loc.get("jurisdiction_codes", [])
    reg = _get_regulatory_framework(jurisdiction_codes)
    zone = loc.get("climate_zone_ASHRAE") or loc.get("climate_zone", "")

    regulatory_flags: list[str] = []

    # Flag: building above common regulatory size threshold (varies by jurisdiction)
    if gfa:
        threshold = 25000  # sqft (common US threshold), use as indicative
        gfa_sqft = size.get("GFA_sqft", 0)
        if gfa_sqft and gfa_sqft > threshold:
            regulatory_flags.append(f"large_building_size_threshold: GFA {gfa_sqft:,} sqft above typical {threshold:,} sqft regulatory threshold")
        elif size.get("GFA_m2") and size.get("GFA_m2", 0) > 2322:
            regulatory_flags.append("large_building_size_threshold: GFA above indicative 2,322 m2 threshold")

    # Flag: landmark status constraints
    if ftype.get("landmark_status"):
        regulatory_flags.append(f"landmark_retrofit_constraints: {ftype.get('landmark_status')}")

    # Flag: certifications may not cover current compliance period
    vintage = fi.get("input_06_vintage", {})
    certs = [
        r.get("certification")
        for r in vintage.get("major_renovations_known", [])
        if r.get("certification")
    ]
    if certs:
        regulatory_flags.append(
            f"certification_currency_gap: {', '.join(certs)} may not align with current compliance period"
        )

    return {
        "entity_type": "RegulatoryContext",
        "jurisdiction_codes": jurisdiction_codes,
        "primary_regulation": reg["primary"],
        "secondary_regulations": reg["secondary"],
        "regulatory_notes": reg["notes"],
        "landmark_status": ftype.get("landmark_status", ""),
        "landmark_retrofit_constraint": (
            "Landmark designation may restrict facade and mechanical modifications — confirm with local authority"
            if ftype.get("landmark_status") else ""
        ),
        "GFA_sqft": size.get("GFA_sqft"),
        "GFA_m2": size.get("GFA_m2"),
        "regulatory_flags": regulatory_flags,
        "compliance_determination_status": "requires_validation — compliance cannot be confirmed from public data alone",
        "data_provenance": (
            f"{reg['primary']}_text + facility_inputs[input_01, input_02] + jurisdiction_database"
        ),
        "epistemic_status": "Decision-grade — regulatory flags only, not compliance determination",
    }


def _build_compliance_applicability_case(
    fi: dict,
    regulatory_context: dict,
    jurisdiction_bundle: dict,
    improvement_constraint: dict,
    target_definition: dict[str, Any],
    enriched: dict[str, Any],
) -> dict:
    target_type = ""
    if isinstance(target_definition, dict):
        target_type = str(target_definition.get("target_type", "")).strip().lower()
    size = fi.get("input_05_size", {})
    gfa_sqft = regulatory_context.get("GFA_sqft") or size.get("GFA_sqft")
    primary_regulation = regulatory_context.get("primary_regulation", "")
    secondary_regulations = regulatory_context.get("secondary_regulations", [])
    jurisdiction_codes = regulatory_context.get("jurisdiction_codes", [])
    regulatory_flags = regulatory_context.get("regulatory_flags", [])
    landmark_status = regulatory_context.get("landmark_status", "")
    is_nyc_ll97 = primary_regulation == "NYC_Local_Law_97_2019" and "US-NY-NYC" in jurisdiction_codes
    ll97_cbl_row = _nyc_ll97_cbl_record(enriched)
    ll97_cbl_covered = _safe_text(ll97_cbl_row.get("ll97_cbl_covered")).upper()
    ll97_pathway = _safe_text(ll97_cbl_row.get("ll97_compliance_pathway"))
    ll97_pathway_label = _safe_text(ll97_cbl_row.get("ll97_compliance_pathway_label")) or _ll97_pathway_label(ll97_pathway)
    ll97_filing_guidance = enriched.get("ll97_filing_guidance", {})
    ll97_public_filing_candidate = enriched.get("ll97_public_filing_candidate", {})
    ll97_public_filing_best = (
        ll97_public_filing_candidate.get("best_candidate", {})
        if isinstance(ll97_public_filing_candidate.get("best_candidate", {}), dict)
        else {}
    )

    threshold_records: list[dict[str, Any]] = []
    screening_basis_register: list[dict[str, Any]] = []
    trigger_fields: list[dict[str, Any]] = [
        {
            "field_name": "jurisdiction_codes",
            "field_state": "observed" if jurisdiction_codes else "missing",
            "value": jurisdiction_codes,
            "reason": "Jurisdiction assignment anchors rule-family screening.",
        },
        {
            "field_name": "GFA_sqft",
            "field_state": "observed" if gfa_sqft else "missing",
            "value": gfa_sqft,
            "reason": _applicability_threshold_reason(target_type),
        },
        {
            "field_name": "landmark_status",
            "field_state": "observed" if landmark_status else "not_observed",
            "value": landmark_status,
            "reason": "Landmark status may constrain compliance pathway and exception handling.",
        },
    ]
    if ll97_cbl_covered:
        trigger_fields.append(
            {
                "field_name": "ll97_cbl_coverage",
                "field_state": "observed",
                "value": ll97_cbl_covered,
                "reason": "Official NYC Sustainability CBL indicates whether the building is publicly listed as covered for the filing year.",
            }
        )
    if ll97_pathway:
        trigger_fields.append(
            {
                "field_name": "ll97_compliance_pathway",
                "field_state": "observed",
                "value": ll97_pathway_label or ll97_pathway,
                "reason": "Official NYC Sustainability CBL identifies the current public compliance pathway for the filing year.",
            }
        )
    if gfa_sqft:
        threshold_records.append({
            "threshold_name": "nyc_ll97_covered_building_threshold_sqft" if is_nyc_ll97 else "indicative_large_building_threshold_sqft",
            "threshold_value": 25000,
            "measured_value": gfa_sqft,
            "threshold_state": "exceeds" if gfa_sqft > 25000 else "below",
            "threshold_basis": (
                "NYC LL97 covered-building screening threshold from DOB public guidance."
                if is_nyc_ll97
                else "Indicative screening threshold from public regulatory heuristics."
            ),
        })
        screening_basis_register.append({
            "basis_name": "regulated_floor_area_basis",
            "basis_value": gfa_sqft,
            "basis_unit": "sqft",
            "basis_state": "whole_building_screening_basis",
            "source_scope": "ASSET_LEVEL",
            "authority_basis": "Public gross floor area record routed through compliance screening.",
            "notes": (
                "Uses public gross floor area as the current whole-building screening basis for regulated floor area. "
                "Final filing scope may still change with BIN-specific pathway, exception, or dispute outcomes."
            ),
        })

    if is_nyc_ll97:
        screening_basis_register.extend(
            [
                {
                    "basis_name": "ll97_compliance_period",
                    "basis_value": "2024-2029",
                    "basis_unit": "",
                    "basis_state": "article_320_screening_period",
                    "source_scope": "JURISDICTION_LEVEL",
                    "authority_basis": "NYC DOB LL97 public rule guidance.",
                    "notes": "Current public screening period for Article 320 emissions limits; exact pathway should still be confirmed against the Covered Buildings List.",
                },
                {
                    "basis_name": "ll97_penalty_rate",
                    "basis_value": 268,
                    "basis_unit": "USD_per_metric_ton_CO2e",
                    "basis_state": "article_320_penalty_basis",
                    "source_scope": "JURISDICTION_LEVEL",
                    "authority_basis": "NYC DOB LL97 violations guidance.",
                    "notes": "Screening penalty-rate basis for annual emissions above the applicable limit.",
                },
                {
                    "basis_name": "ll97_failure_to_file_penalty",
                    "basis_value": 0.50,
                    "basis_unit": "USD_per_sqft_per_month",
                    "basis_state": "article_320_failure_to_file_basis",
                    "source_scope": "JURISDICTION_LEVEL",
                    "authority_basis": "NYC DOB LL97 violations guidance.",
                    "notes": "Separate filing penalty basis; do not confuse with emissions-over-limit penalty screening.",
                },
            ]
        )
        if ll97_cbl_covered:
            screening_basis_register.append(
                {
                    "basis_name": "ll97_cbl_pathway",
                    "basis_value": ll97_pathway_label or ll97_pathway or ll97_cbl_covered,
                    "basis_unit": "",
                    "basis_state": "official_public_cbl_pathway",
                    "source_scope": "ASSET_LEVEL",
                    "authority_basis": "NYC DOB Sustainability Law CBL 2026.",
                    "notes": "Official covered-building status and public filing-year pathway are observed, but they do not substitute for the actual certified LL97 report.",
                }
            )
        if ll97_filing_guidance:
            screening_basis_register.append(
                {
                    "basis_name": "ll97_filing_process_guidance",
                    "basis_value": "Article 320 / Article 321 public guidance observed",
                    "basis_unit": "",
                    "basis_state": "official_public_filing_process_guidance",
                    "source_scope": "JURISDICTION_LEVEL",
                    "authority_basis": "NYC DOB LL97 public filing FAQs and official submission guides.",
                    "notes": (
                        "Official filing-process guidance is public and admissible as routing context, "
                        "but no public building-level LL97 filing registry was observed in this source path."
                    ),
                }
            )
        if ll97_public_filing_best:
            screening_basis_register.append(
                {
                    "basis_name": "ll97_public_filing_artifact",
                    "basis_value": _safe_text(ll97_public_filing_best.get("title")) or _safe_text(ll97_public_filing_best.get("url")),
                    "basis_unit": "",
                    "basis_state": "public_asset_specific_filing_artifact_observed",
                    "source_scope": "ASSET_LEVEL",
                    "authority_basis": "Public owner or authority artifact located through targeted LL97 filing search.",
                    "notes": (
                        "A public asset-specific filing artifact candidate is observed, but it still requires BIN, period, and scope review before compliance closure can be claimed."
                    ),
                }
            )

    rule_family_records = []
    if primary_regulation:
        rule_family_records.append({
            "rule_family_id": "primary_regulation",
            "rule_family_name": primary_regulation,
            "rule_relevance_state": "relevant",
            "authority_basis": regulatory_context.get("data_provenance", ""),
        })
    for idx, secondary in enumerate(secondary_regulations, 1):
        rule_family_records.append({
            "rule_family_id": f"secondary_regulation_{idx}",
            "rule_family_name": secondary,
            "rule_relevance_state": "secondary_relevant",
            "authority_basis": jurisdiction_bundle.get("data_provenance", ""),
        })

    if primary_regulation:
        applicability_state = "rule_family_relevant"
        compliance_posture_state = "trigger_plausible"
        if jurisdiction_codes or regulatory_flags:
            applicability_state = "trigger_partially_supported"
        if gfa_sqft or landmark_status:
            applicability_state = "applicability_likely"
            compliance_posture_state = "compliance_open"
        if ll97_cbl_covered == "Y":
            applicability_state = "applicability_confirmed_publicly"
            compliance_posture_state = "covered_building_pathway_observed"
    else:
        applicability_state = "rule_family_relevant"
        compliance_posture_state = "trigger_plausible"

    hardening_requirements = [
        f"Obtain current-period official report or filing under {primary_regulation or 'the primary applicable rule family'}.",
        "Confirm regulated scope, thresholds, and exception paths with current authority text or regulated filing.",
        "Obtain measured or reported values for the regulated parameter set before asserting compliance posture.",
    ]
    if is_nyc_ll97 and ll97_filing_guidance:
        hardening_requirements.insert(
            0,
            "No public building-level LL97 filing registry was observed. Obtain the certified LL97 filing PDF, BEAM export, or official Article 321 submission package for the specific BIN.",
        )
    if is_nyc_ll97 and ll97_public_filing_best:
        hardening_requirements.insert(
            0,
            "Review the public LL97 filing artifact against the specific BIN, filing year, pathway, and reported scope before using it as stronger compliance evidence.",
        )
    if ll97_cbl_covered == "Y":
        hardening_requirements.insert(
            0,
            "Use the observed LL97 Covered Buildings List pathway as public routing context, then obtain the current certified LL97 report or Article 321 submission for the specific BIN.",
        )
    if improvement_constraint.get("regulatory_constraints"):
        hardening_requirements.append(
            "Validate whether structural or landmark constraints modify the admissible compliance pathway."
        )

    return {
        "case_id": "compliance_applicability_case",
        "entity_type": "ComplianceApplicabilityCase",
        "jurisdiction_trace_record": {
            "jurisdiction_codes": jurisdiction_codes,
            "primary_regulation": primary_regulation,
            "secondary_regulations": secondary_regulations,
            "authority_source": jurisdiction_bundle.get("data_provenance", ""),
            "climate_zone": jurisdiction_bundle.get("climate_zone_ASHRAE") or jurisdiction_bundle.get("climate_zone", ""),
        },
        "rule_family_record": rule_family_records,
        "trigger_field_register": trigger_fields,
        "threshold_register": threshold_records,
        "exception_register": [],
        "rule_conflict_record": [],
        "applicability_state": applicability_state,
        "compliance_posture_state": compliance_posture_state,
        "determination_status": regulatory_context.get("compliance_determination_status", ""),
        "regulatory_flags": regulatory_flags,
        "screening_basis_register": screening_basis_register,
        "public_filing_registry_state": (
            "public_asset_specific_filing_artifact_observed"
            if is_nyc_ll97 and ll97_public_filing_best
            else
            "not_publicly_observed"
            if is_nyc_ll97 and ll97_filing_guidance
            else "unknown"
        ),
        "domain_of_validity": (
            "Applicability screening and posture framing from public data only. "
            "Not a legal opinion or compliance closure."
        ),
        "publication_ceiling": "publish_bounded",
        "hardening_requirements": hardening_requirements,
        "data_provenance": (
            f"{regulatory_context.get('data_provenance', '')} + {improvement_constraint.get('data_provenance', '')}"
        ).strip(" +"),
        "epistemic_status": "Decision-grade — applicability screening, not compliance closure",
    }


def _build_system_asset_hypotheses(fi: dict) -> list[dict]:
    """Derive system asset hypotheses generically from input_09_known_systems dict keys."""
    systems = fi.get("input_09_known_systems", {})
    if not systems:
        return []

    hypotheses: list[dict] = []
    for system_name, system_data in systems.items():
        if not isinstance(system_data, dict):
            continue

        # Extract all available descriptors from the system data
        sys_type = (
            system_data.get("type")
            or system_data.get("type_mix")
            or system_data.get("technology")
            or "type_not_specified"
        )
        retrofit = (
            system_data.get("retrofit_status")
            or system_data.get("status")
            or system_data.get("modernization_status")
            or ""
        )
        vintage_note = system_data.get("year_installed") or system_data.get("installation_year") or ""
        count = system_data.get("count") or system_data.get("units") or ""
        integration = system_data.get("integration_level") or system_data.get("integration") or ""
        present = system_data.get("present", True)
        known_occupant = system_data.get("known_occupant") or system_data.get("operator") or ""
        controls = system_data.get("controls") or ""

        # Build hypothesis text from available data
        descriptor_parts = []
        if sys_type and sys_type != "type_not_specified":
            descriptor_parts.append(f"type: {sys_type}")
        if retrofit:
            descriptor_parts.append(f"status: {retrofit}")
        if vintage_note:
            descriptor_parts.append(f"installed: {vintage_note}")
        if count:
            descriptor_parts.append(f"count: {count}")
        if integration:
            descriptor_parts.append(f"integration: {integration}")
        if known_occupant:
            descriptor_parts.append(f"operator: {known_occupant}")
        if controls:
            descriptor_parts.append(f"controls: {controls}")

        descriptor_str = "; ".join(descriptor_parts) if descriptor_parts else "details not specified"

        # Determine confidence level from available data richness
        data_richness = len([x for x in [sys_type, retrofit, vintage_note, count] if x and x != "type_not_specified"])
        confidence = (
            "plausible — confirmed from public/operator disclosures"
            if data_richness >= 3
            else "plausible — partial data from operator declaration"
            if data_richness >= 1
            else "tentative — system presence declared but details unspecified"
        )

        hypotheses.append({
            "system": system_name,
            "type": sys_type,
            "retrofit_status": retrofit,
            "vintage_note": vintage_note,
            "count": count,
            "integration_level": integration,
            "present": present,
            "known_occupant": known_occupant,
            "controls": controls,
            "descriptor": descriptor_str,
            "hypothesis": (
                f"{system_name} system declared with the following characteristics: {descriptor_str}. "
                "Integration depth and current performance status not independently verified."
            ),
            "confidence": confidence,
            "epistemic_status": "Decision-grade hypothesis — operator-declared, not site-verified",
        })

    return hypotheses


def _build_operational_tensions(fi: dict, enriched: dict) -> list[dict]:
    """Derive operational tensions generically from available data signals."""
    financials = enriched.get("financials", {})
    primary_use = fi.get("input_04_primary_use", {})
    vintage = fi.get("input_06_vintage", {})
    loc = fi.get("input_01_location", {})
    size = fi.get("input_05_size", {})
    sector = fi.get("input_03_sector", {})
    ftype = fi.get("input_02_facility_type", {})
    jurisdiction_codes = loc.get("jurisdiction_codes", [])
    reg = _get_regulatory_framework(jurisdiction_codes)

    tensions: list[dict] = []
    tension_counter = 1

    # (a) Financial data discrepancies from enriched data
    revenues = financials.get("revenues_annual")
    total_debt_xbrl = financials.get("total_debt")
    total_debt_market = financials.get("total_debt_market_estimate")
    if (
        revenues and total_debt_xbrl and total_debt_market
        and abs(total_debt_xbrl - total_debt_market) / max(total_debt_xbrl, 1) > 0.30
    ):
        tensions.append({
            "tension_id": f"T-{tension_counter:02d}",
            "tension_type": "debt_figure_discrepancy",
            "description": (
                f"Reported debt figure ({total_debt_xbrl:,.0f} USD) differs materially from "
                f"market/analyst estimate ({total_debt_market:,.0f} USD). "
                "Discrepancy may reflect JV-level debt, mezzanine structures, or classification scope. "
                "Unresolved leverage uncertainty materially affects LTV and financing models."
            ),
            "elements_in_tension": ["reported_debt_figure", "market_debt_estimate"],
            "validation_requirement": "Cross-reference 10-K footnotes, mortgage schedule, and JV debt disclosures.",
        })
        tension_counter += 1

    # (b) Concentration signals in facility_inputs
    anchor_tenant = primary_use.get("anchor_tenant")
    anchor_sqft = primary_use.get("anchor_tenant_approx_sqft")
    office_sqft = size.get("rentable_office_sqft_approx") or size.get("GFA_sqft", 0)
    customer_concentration = primary_use.get("customer_concentration")

    if anchor_tenant and anchor_sqft and office_sqft:
        anchor_pct = round(100 * anchor_sqft / office_sqft, 1)
        if anchor_pct > 10:
            tensions.append({
                "tension_id": f"T-{tension_counter:02d}",
                "tension_type": "anchor_tenant_concentration",
                "description": (
                    f"{anchor_tenant} occupies approximately {anchor_pct}% of rentable area "
                    f"(~{anchor_sqft:,} sqft). "
                    "Lease non-renewal would trigger a structural revenue gap. "
                    "Concentration above 10% of GFA creates binary revenue event risk."
                ),
                "elements_in_tension": ["anchor_tenant_concentration", "revenue_stability"],
                "validation_requirement": (
                    f"Confirm {anchor_tenant} lease expiry date, renewal options, and any subleasing activity."
                ),
            })
            tension_counter += 1
    elif customer_concentration and float(customer_concentration or 0) > 0.15:
        tensions.append({
            "tension_id": f"T-{tension_counter:02d}",
            "tension_type": "customer_concentration_risk",
            "description": (
                f"Customer concentration of {float(customer_concentration)*100:.0f}% indicates "
                "significant dependency on a small number of customers or tenants. "
                "Revenue stability is vulnerable to counterparty decisions."
            ),
            "elements_in_tension": ["customer_concentration", "revenue_stability"],
            "validation_requirement": "Confirm counterparty contract terms, renewal status, and backup revenue sources.",
        })
        tension_counter += 1

    # (c) Regulatory flags from jurisdiction lookup
    certs = [
        r.get("certification")
        for r in vintage.get("major_renovations_known", [])
        if r.get("certification")
    ]
    primary_reg = reg["primary"]
    if certs:
        tensions.append({
            "tension_id": f"T-{tension_counter:02d}",
            "tension_type": "certification_vs_current_regulatory_compliance",
            "description": (
                f"Declared certification(s) ({', '.join(certs)}) were achieved in prior periods. "
                f"The applicable regulatory framework ({primary_reg}) operates on current-period "
                "metrics that may differ from the certification methodology. "
                "Certification vintage does not guarantee current compliance."
            ),
            "elements_in_tension": [f"certification_{c.replace(' ', '_')}" for c in certs] + [primary_reg],
            "validation_requirement": (
                f"Obtain current compliance status under {primary_reg}. "
                "Verify whether certification scope covers all regulated uses."
            ),
        })
        tension_counter += 1

    # (d) Vintage vs. system age signals
    year_built = vintage.get("year_built")
    years_old = vintage.get("years_old")
    if year_built and (years_old or 0) >= 40:
        last_major_retrofit = max(
            (r.get("period", "0") for r in vintage.get("major_renovations_known", []) if r.get("period")),
            default="not_confirmed",
        )
        tensions.append({
            "tension_id": f"T-{tension_counter:02d}",
            "tension_type": "vintage_capex_liability",
            "description": (
                f"Facility built in {year_built} ({years_old} years old). "
                f"Last known major retrofit: {last_major_retrofit}. "
                "Pre-modern construction with partially-retained legacy systems carries "
                "structural CapEx obligations beyond disclosed maintenance budgets. "
                "Reserve adequacy cannot be confirmed from public sources."
            ),
            "elements_in_tension": ["building_age_capex_liability", "disclosed_capex_reserve"],
            "validation_requirement": (
                "Obtain CapEx schedule, capital plan, and third-party Property Condition Assessment (PCA)."
            ),
        })
        tension_counter += 1

    # (e) Multi-use complexity tension (>1 use declared)
    uses = [primary_use.get(f"use_{i}") for i in range(1, 6) if primary_use.get(f"use_{i}")]
    if len(uses) > 1:
        tensions.append({
            "tension_id": f"T-{tension_counter:02d}",
            "tension_type": "multi_use_operational_complexity",
            "description": (
                f"Facility declared uses: {', '.join(uses)}. "
                "Multi-use assets face interdependency risks: system schedules, energy loads, "
                "regulatory applicability, and staffing requirements differ across use types. "
                "Optimizing for one use may create adverse conditions for another."
            ),
            "elements_in_tension": ["multi_use_complexity", "operational_optimization"],
            "validation_requirement": (
                "Verify operating schedules, metering segregation, and regulatory applicability per use."
            ),
        })
        tension_counter += 1

    return tensions


def _build_org_capability_profile(fi: dict, enriched: dict) -> dict:
    financials = enriched.get("financials", {})
    sector = fi.get("input_03_sector", {})
    company_name = enriched.get("company_name", sector.get("company_name", ""))
    ticker = sector.get("owner_ticker", "")
    exchange = sector.get("owner_exchange", "")
    ownership = sector.get("ownership_structure", "")

    fin_signals: dict[str, Any] = {
        "revenues_annual_usd": financials.get("revenues_annual"),
        "total_assets_usd": financials.get("total_assets"),
        "total_debt_usd": financials.get("total_debt"),
        "filing_currency": financials.get("filing_currency", ""),
        "data_source": enriched.get("data_source", "financial_enrichment"),
    }

    return {
        "entity_type": "OrganizationCapability",
        "organization": company_name,
        "ticker": ticker,
        "exchange": exchange,
        "ownership_structure": ownership,
        "financial_health_signals": fin_signals,
        "sustainability_capability": enriched.get("sustainability_note", ""),
        "tenant_management_capability": enriched.get("tenant_management_note", ""),
        "capability_uncertainty": (
            "Internal operational efficiency and forward CapEx planning not independently verifiable from public sources"
        ),
        "data_provenance": "financial_enrichment + facility_inputs[input_03–input_04]",
        "epistemic_status": "Decision-grade",
    }


def _build_improvement_constraint_profile(fi: dict) -> dict:
    ftype = fi.get("input_02_facility_type", {})
    vintage = fi.get("input_06_vintage", {})
    loc = fi.get("input_01_location", {})
    schedule = fi.get("input_07_operating_schedule", {})
    systems = fi.get("input_09_known_systems", {})
    jurisdiction_codes = loc.get("jurisdiction_codes", [])
    reg = _get_regulatory_framework(jurisdiction_codes)

    # Build operational constraints from known systems and schedules
    operational_constraints: dict[str, str] = {}
    components_247 = schedule.get("24_7_components", [])
    if components_247:
        operational_constraints["24_7_components"] = (
            f"The following components operate 24/7: {', '.join(components_247)}. "
            "Energy optimization strategies must preserve continuous operations."
        )
    # Flag high-density or critical systems
    for sys_name, sys_data in systems.items():
        if isinstance(sys_data, dict):
            density = sys_data.get("power_density_class", "")
            if density in ("high", "critical"):
                operational_constraints[f"critical_{sys_name}"] = (
                    f"{sys_name} operates at {density} density/criticality. "
                    "Maintenance or modification requires continuity planning."
                )

    # Regulatory constraints from jurisdiction
    regulatory_constraints = [reg["primary"]] + reg["secondary"][:2]

    return {
        "entity_type": "ImprovementConstraint",
        "landmark_constraints": {
            "status": ftype.get("landmark_status", ""),
            "implication": (
                "Landmark designation restricts facade and structural modifications. "
                "Mechanical changes may require regulatory authority approval."
                if ftype.get("landmark_status") else "No landmark constraints declared."
            ),
        },
        "structural_constraints": {
            "frame": vintage.get("structural_note", ""),
            "year_built": vintage.get("year_built"),
            "implication": (
                f"Original structural system from {vintage.get('year_built')} may limit deep retrofit pathways. "
                "Major mechanical changes require structural engineering review."
                if vintage.get("year_built") and (vintage.get("years_old") or 0) >= 30
                else "No structural constraint signals from available data."
            ),
        },
        "operational_constraints": operational_constraints,
        "regulatory_constraints": regulatory_constraints,
        "data_provenance": "facility_inputs[input_02, input_06, input_07, input_09]",
        "epistemic_status": "Decision-grade",
    }


def _build_prior_assumptions_pack(fi: dict, enriched: dict) -> list[dict]:
    financials = enriched.get("financials", {})
    sector = fi.get("input_03_sector", {})
    loc = fi.get("input_01_location", {})
    vintage = fi.get("input_06_vintage", {})
    size = fi.get("input_05_size", {})
    jurisdiction_codes = loc.get("jurisdiction_codes", [])
    reg = _get_regulatory_framework(jurisdiction_codes)
    zone = loc.get("climate_zone_ASHRAE") or loc.get("climate_zone", "")
    bench_sector = sector.get("sector", "commercial_real_estate")
    bench = _get_eui_benchmark(bench_sector)

    # Build certifications list
    certs = [
        r.get("certification")
        for r in vintage.get("major_renovations_known", [])
        if r.get("certification")
    ]

    assumptions: list[dict] = []
    pa_counter = 1

    # PA-01: Certification currency
    if certs:
        cert_str = ", ".join(certs)
        assumptions.append({
            "assumption_id": f"PA-{pa_counter:02d}",
            "assumption": (
                f"Declared certification(s) ({cert_str}) are assumed current for initial benchmarking, "
                f"pending current {reg['primary']} compliance report confirmation."
            ),
            "basis": "Facility operator declaration / public disclosures",
            "risk_if_wrong": (
                "Energy and emissions estimates may be materially off if certification baseline is outdated. "
                f"Actual {reg['primary']} compliance requires current-period data."
            ),
        })
        pa_counter += 1

    # PA-02: Financial figures
    rev = financials.get("revenues_annual")
    debt = financials.get("total_debt")
    data_source = enriched.get("data_source", "financial_enrichment")
    if rev is not None or debt is not None:
        rev_str = f"{rev:,.0f} USD" if rev is not None else "N/A"
        debt_str = f"{debt:,.0f} USD" if debt is not None else "N/A"
        market_debt = financials.get("total_debt_market_estimate")
        market_note = (
            f" Discrepancy with market estimate (~{market_debt:,.0f} USD) is flagged and not resolved."
            if market_debt and debt and abs(market_debt - debt) / max(debt, 1) > 0.30
            else ""
        )
        assumptions.append({
            "assumption_id": f"PA-{pa_counter:02d}",
            "assumption": (
                f"{data_source} figures (revenues ~{rev_str}, debt ~{debt_str}) "
                f"are treated as reported values.{market_note}"
            ),
            "basis": data_source,
            "risk_if_wrong": (
                "Underestimating leverage materially changes LTV and yield models. "
                "Overestimating revenue distorts income quality assessment."
            ),
        })
        pa_counter += 1

    # PA-03: Anchor tenant assumption
    anchor = fi.get("input_04_primary_use", {}).get("anchor_tenant")
    if anchor:
        assumptions.append({
            "assumption_id": f"PA-{pa_counter:02d}",
            "assumption": f"{anchor} lease assumed active as of analysis date. Renewal status not confirmed.",
            "basis": "Facility inputs and public tenant disclosure",
            "risk_if_wrong": (
                f"{anchor} departure would trigger the largest single revenue event. "
                "Concentration risk cannot be bounded without lease term confirmation."
            ),
        })
        pa_counter += 1

    # PA-04: EUI benchmark assumption
    eui_base = bench["median_EUI_kBtu_sqft"]
    eui_adj = _CLIMATE_EUI_ADJUSTMENT.get(str(zone).strip().upper(), 1.0)
    gfa_str = (
        f"{size.get('GFA_sqft', 'N/A'):,} sqft" if size.get("GFA_sqft")
        else f"{size.get('GFA_m2', 'N/A')} m2" if size.get("GFA_m2")
        else "area not specified"
    )
    assumptions.append({
        "assumption_id": f"PA-{pa_counter:02d}",
        "assumption": (
            f"EUI benchmark applies {bench['source']} sectoral median "
            f"({eui_base} kBtu/sqft) with climate zone {zone} adjustment factor ({eui_adj}). "
            "This is a sectoral benchmark, NOT a site measurement."
        ),
        "basis": bench["source"],
        "risk_if_wrong": (
            f"Actual building EUI at {gfa_str} may differ substantially "
            "due to operational profile, tenant mix, and local conditions."
        ),
    })
    pa_counter += 1

    # PA-05: Regulatory framework applicability
    assumptions.append({
        "assumption_id": f"PA-{pa_counter:02d}",
        "assumption": (
            f"Regulatory framework {reg['primary']} applied based on jurisdiction codes "
            f"({', '.join(jurisdiction_codes) if jurisdiction_codes else 'not specified'}). "
            "Actual applicability and compliance status require formal determination."
        ),
        "basis": "jurisdiction_codes + regulatory_database_lookup",
        "risk_if_wrong": (
            "If wrong regulatory framework is applied, compliance assessment may miss "
            "applicable penalties or requirements."
        ),
    })

    return assumptions


def _build_uncertainty_markers(fi: dict, enriched: dict) -> list[dict]:
    financials = enriched.get("financials", {})
    sector = fi.get("input_03_sector", {})
    loc = fi.get("input_01_location", {})
    size = fi.get("input_05_size", {})
    primary_use = fi.get("input_04_primary_use", {})
    vintage = fi.get("input_06_vintage", {})
    jurisdiction_codes = loc.get("jurisdiction_codes", [])
    reg = _get_regulatory_framework(jurisdiction_codes)

    # Pull coverage gaps from enriched data if available
    coverage_gaps: list[str] = enriched.get("coverage_gaps", [])

    markers: list[dict] = []
    um_counter = 1

    # Standard unknowns by sector/data availability

    # UM: Regulatory compliance status
    markers.append({
        "marker_id": f"UM-{um_counter:02d}",
        "dimension": "regulatory_compliance_status",
        "description": (
            f"Current compliance position under {reg['primary']} cannot be determined "
            "from public sources alone. Compliance reports are not always publicly indexed."
        ),
        "impact": "High — non-compliance exposure could reach material amounts depending on asset scale",
        "resolution_path": (
            f"Request current compliance report under {reg['primary']} from the asset owner or regulatory authority."
        ),
    })
    um_counter += 1

    # UM: Actual building EUI
    markers.append({
        "marker_id": f"UM-{um_counter:02d}",
        "dimension": "actual_building_EUI",
        "description": (
            "Actual current building-level EUI is not confirmed available from public sources. "
            "Declared certifications may reflect a prior-period performance baseline."
        ),
        "impact": "Medium — limits precision of energy-driven CapEx and regulatory exposure modeling",
        "resolution_path": (
            "Obtain current metered energy data, ENERGY STAR Portfolio Manager record, "
            "or mandatory benchmarking disclosure (if applicable in jurisdiction)."
        ),
    })
    um_counter += 1

    # UM: Debt scope (if financial data available and discrepancy exists)
    debt_xbrl = financials.get("total_debt")
    debt_market = financials.get("total_debt_market_estimate")
    if debt_xbrl and debt_market and abs(debt_xbrl - debt_market) / max(debt_xbrl, 1) > 0.30:
        markers.append({
            "marker_id": f"UM-{um_counter:02d}",
            "dimension": "total_debt_scope",
            "description": (
                f"Reported debt ({debt_xbrl:,.0f} USD) and market-cited estimate "
                f"({debt_market:,.0f} USD) are inconsistent. "
                "True consolidated leverage scope cannot be confirmed without detailed financial review."
            ),
            "impact": "High — LTV-based financing modeling is unreliable until resolved",
            "resolution_path": "Review full financial statements, mortgage schedule, JV agreements, and analyst reports.",
        })
        um_counter += 1

    # UM: Anchor tenant lease status
    anchor = primary_use.get("anchor_tenant")
    if anchor:
        anchor_sqft = primary_use.get("anchor_tenant_approx_sqft", 0)
        office_sqft = size.get("rentable_office_sqft_approx") or size.get("GFA_sqft", 1)
        anchor_pct = round(100 * anchor_sqft / office_sqft, 1) if (anchor_sqft and office_sqft) else 0
        markers.append({
            "marker_id": f"UM-{um_counter:02d}",
            "dimension": "anchor_tenant_lease_status",
            "description": (
                f"{anchor} lease term, renewal options, and renewal intent "
                "not confirmed from public sources as of analysis date."
            ),
            "impact": (
                f"High — {anchor} represents ~{anchor_pct}% of rentable area. "
                "Concentration risk cannot be bounded without this confirmation."
            ) if anchor_pct > 5 else "Medium — tenant lease status not confirmed",
            "resolution_path": (
                f"Review tenant schedule in financial filings. "
                f"Cross-reference {anchor} real estate announcements."
            ),
        })
        um_counter += 1

    # UM: CapEx reserve adequacy (for older buildings)
    years_old = vintage.get("years_old", 0) or 0
    if years_old >= 30:
        markers.append({
            "marker_id": f"UM-{um_counter:02d}",
            "dimension": "capex_reserve_adequacy",
            "description": (
                f"CapEx reserves for a {years_old}-year-old facility cannot be independently "
                "verified as adequate without third-party engineering review."
            ),
            "impact": "Medium — unplanned CapEx could materially affect early asset economics and decision posture",
            "resolution_path": (
                "Commission an independent Property Condition Assessment (PCA) before stronger CAPEX claims are made."
            ),
        })
        um_counter += 1

    # UM: Additional gaps from enriched data coverage_gaps
    for gap in coverage_gaps:
        markers.append({
            "marker_id": f"UM-{um_counter:02d}",
            "dimension": gap.replace(" ", "_").lower(),
            "description": f"Coverage gap identified in data enrichment: {gap}",
            "impact": "Medium — limits completeness of analytical picture",
            "resolution_path": f"Obtain data to resolve coverage gap: {gap}",
        })
        um_counter += 1

    return markers


def _build_minimum_evidence_pack_seed(
    target_definition: dict[str, Any],
    enriched: dict[str, Any],
    missing_clusters: list[str],
) -> list[dict[str, Any]]:
    seed_rows = list(enriched.get("requestable_evidence_items", []) or [])
    target_type = str(target_definition.get("target_type", "")).strip().lower()
    family = _target_family(target_type)
    present = {
        str(row.get("evidence_item", "")).strip().lower()
        for row in seed_rows
        if row.get("evidence_item")
    }
    present_clusters = {
        str(cluster).strip()
        for row in seed_rows
        for cluster in (row.get("related_clusters", []) or [])
        if cluster
    }

    def add_seed(
        evidence_item: str,
        source: str,
        why_needed: str,
        related_clusters: list[str],
        cases_resolved: list[str],
        decision_unlock: str,
        effort: str,
    ) -> None:
        key = evidence_item.strip().lower()
        if key in present:
            return
        present.add(key)
        present_clusters.update(str(cluster).strip() for cluster in related_clusters if cluster)
        seed_rows.append(
            {
                "evidence_item": evidence_item,
                "source": source,
                "why_needed": why_needed,
                "related_clusters": related_clusters,
                "cases_resolved": cases_resolved,
                "decision_unlock": decision_unlock,
                "effort": effort,
                "target_type": target_definition.get("target_type", ""),
            }
        )

    def cluster_covered(cluster: str) -> bool:
        return cluster in present_clusters

    if "geometry_size_cluster" in missing_clusters and not cluster_covered("geometry_size_cluster"):
        if family == "manufacturing":
            add_seed(
                "Verified site / building area and process footprint",
                "Owner records, site plan, or plant layout",
                "Area is still missing and blocks scale-sensitive technical and compliance reading.",
                ["geometry_size_cluster", "regulatory_cluster"],
                ["LC-ASSET-01", "LC-REG-01"],
                "Unlocks process-scale framing and bounded compliance screening.",
                "CRITICAL",
            )
        elif family == "infrastructure":
            add_seed(
                "One-line or topology boundary, major equipment inventory, and redundancy basis",
                "Operator drawings, site engineering, or asset manager records",
                "Asset boundary is still missing and blocks topology, resilience, and applicability reading.",
                ["geometry_size_cluster", "systems_cluster"],
                ["LC-ASSET-01", "LC-OPS-04"],
                "Unlocks topology-specific technical reading and resilience relevance.",
                "CRITICAL",
            )
        elif family == "oil_gas":
            add_seed(
                "Verified site boundary and major process-unit footprint",
                "Operator records, plot plan, or unit boundary documentation",
                "Asset boundary is still missing and blocks process, emissions, and applicability reading.",
                ["geometry_size_cluster", "regulatory_cluster"],
                ["LC-ASSET-01", "LC-REG-01"],
                "Unlocks bounded process and emissions screening.",
                "CRITICAL",
            )
        elif family == "logistics":
            add_seed(
                "Verified building area, dock count, and refrigerated footprint if applicable",
                "Owner records, site plan, or operator layout",
                "Area is still missing and blocks scale-sensitive logistics and compliance reading.",
                ["geometry_size_cluster", "regulatory_cluster"],
                ["LC-ASSET-01", "LC-REG-01"],
                "Unlocks bounded logistics and compliance screening.",
                "CRITICAL",
            )
        else:
            add_seed(
                "Verified GFA / rentable area",
                "Owner schedule, assessor record, or benchmarking filing",
                "Area is still missing and blocks scale-sensitive technical and compliance reading.",
                ["geometry_size_cluster", "regulatory_cluster"],
                ["LC-ASSET-01", "LC-REG-01"],
                "Unlocks compliance screening and retrofit scale framing.",
                "CRITICAL",
            )
    if "operating_regime_cluster" in missing_clusters and not cluster_covered("operating_regime_cluster"):
        if family == "manufacturing":
            add_seed(
                "Shift schedule, production calendar, and throughput profile",
                "Plant operations or production planning records",
                "Operating regime is required to distinguish structural process load from schedule-driven behavior.",
                ["operating_regime_cluster"],
                ["LC-ASSET-01", "LC-OPS-01"],
                "Unlocks scenario discrimination and process-duty interpretation.",
                "CRITICAL",
            )
        elif family == "infrastructure":
            add_seed(
                "Service-duty or dispatch profile and station-service metering basis",
                "Operations records, SCADA summaries, or operator logs",
                "Operating regime is required to distinguish structural duty from controllable support-load behavior.",
                ["operating_regime_cluster", "fuel_energy_cluster"],
                ["LC-ASSET-01", "LC-OPS-01"],
                "Unlocks scenario discrimination and resilience-side interpretation.",
                "CRITICAL",
            )
        elif family == "oil_gas":
            add_seed(
                "Throughput profile, duty cycle, and turnaround regime",
                "Operations engineering or site operator",
                "Operating regime is required to distinguish structural process duty from operational variability.",
                ["operating_regime_cluster"],
                ["LC-ASSET-01", "LC-OPS-01"],
                "Unlocks scenario discrimination and process-duty interpretation.",
                "CRITICAL",
            )
        elif family == "logistics":
            add_seed(
                "Operating schedule, throughput windows, and dock activity profile",
                "Operator, lease summary, or facility manager",
                "Operating regime is required to distinguish structural throughput from schedule-driven behavior.",
                ["operating_regime_cluster", "tenant_control_cluster"],
                ["LC-ASSET-01", "LC-OPS-01"],
                "Unlocks scenario discrimination and controllability reading.",
                "CRITICAL",
            )
        else:
            add_seed(
                "Operating schedule and use mix by tenant or function",
                "Operator, lease summary, or facility manager",
                "Operating regime is required to distinguish structural load from schedule-driven behavior.",
                ["operating_regime_cluster", "tenant_control_cluster"],
                ["LC-ASSET-01", "LC-OPS-01"],
                "Unlocks scenario discrimination and controllability reading.",
                "CRITICAL",
            )
    if "fuel_energy_cluster" in missing_clusters and not cluster_covered("fuel_energy_cluster"):
        if family == "manufacturing":
            add_seed(
                "12–24 months of utility bills with fuel, steam, refrigeration, and compressed-air context",
                "Utility portal, operator, or plant accounting",
                "Fuel and utility context is still missing, so process-cost and emissions screening remain bounded.",
                ["fuel_energy_cluster", "systems_cluster"],
                ["LC-ASSET-01", "LC-MKT-02", "LC-REG-01"],
                "Unlocks bounded energy, emissions, and process-cost screening.",
                "CRITICAL",
            )
        elif family == "infrastructure":
            add_seed(
                "Station-service, backup-fuel, and metering records",
                "Operations records, SCADA summaries, or operator logs",
                "Fuel and metering context is still missing, so duty and resilience screening remain bounded.",
                ["fuel_energy_cluster", "operating_regime_cluster"],
                ["LC-ASSET-01", "LC-MKT-02", "LC-REG-01"],
                "Unlocks bounded duty, resilience, and compliance reading.",
                "CRITICAL",
            )
        elif family == "oil_gas":
            add_seed(
                "Fuel, flare, steam, and emissions basis by operating unit",
                "Operator data room, environmental reporting, or site engineering",
                "Fuel and emissions context is still missing, so transition and compliance screening remain bounded.",
                ["fuel_energy_cluster", "regulatory_cluster"],
                ["LC-ASSET-01", "LC-MKT-02", "LC-REG-01"],
                "Unlocks bounded carbon, compliance, and process-cost screening.",
                "CRITICAL",
            )
        elif family == "logistics":
            add_seed(
                "12–24 months of utility bills, meter map, and refrigeration profile if present",
                "Utility portal, operator, or owner accounting records",
                "Fuel and utility context is still missing, so refrigeration and carbon screening remain bounded.",
                ["fuel_energy_cluster", "tenant_control_cluster"],
                ["LC-ASSET-01", "LC-MKT-02", "LC-REG-01"],
                "Unlocks bounded energy, carbon, and compliance reading.",
                "CRITICAL",
            )
        else:
            add_seed(
                "12–24 months of utility bills, interval data if available, and meter map",
                "Utility portal, operator, or owner accounting records",
                "Fuel and utility context is still missing, so benchmark-only reading remains bounded.",
                ["fuel_energy_cluster", "tenant_control_cluster"],
                ["LC-ASSET-01", "LC-MKT-02", "LC-REG-01"],
                "Unlocks bounded energy, carbon, and compliance reading.",
                "CRITICAL",
            )
    if "systems_cluster" in missing_clusters and not cluster_covered("systems_cluster"):
        if family == "manufacturing":
            add_seed(
                "Process line inventory and major energy-using equipment list",
                "Plant engineering, maintenance system, or operator records",
                "System inventory is required before any process or reliability claim can be defended.",
                ["systems_cluster", "operating_regime_cluster"],
                ["LC-ASSET-01", "LC-OPS-04"],
                "Unlocks process-level technical reading and retrofit relevance.",
                "CRITICAL",
            )
        elif family == "infrastructure":
            add_seed(
                "One-line or topology boundary, major equipment inventory, and redundancy basis",
                "Operator drawings, site engineering, or asset manager records",
                "System inventory is required before any topology, loss, or resilience claim can be defended.",
                ["systems_cluster", "geometry_size_cluster"],
                ["LC-ASSET-01", "LC-OPS-04"],
                "Unlocks topology-specific technical reading and resilience relevance.",
                "CRITICAL",
            )
        elif family == "oil_gas":
            add_seed(
                "Process-unit inventory, throughput profile, and major duty drivers",
                "Operations engineering, site reports, or operator records",
                "System inventory is required before any process, emissions, or reliability claim can be defended.",
                ["systems_cluster", "operating_regime_cluster"],
                ["LC-ASSET-01", "LC-OPS-04"],
                "Unlocks asset-specific process and reliability reading.",
                "CRITICAL",
            )
        elif family == "logistics":
            add_seed(
                "Dock, HVAC, lighting, refrigeration, and controls inventory",
                "Engineering records, O&M manuals, or site operator",
                "System inventory is required before any logistics or refrigeration claim can be defended.",
                ["systems_cluster"],
                ["LC-ASSET-01", "LC-OPS-04"],
                "Unlocks bounded retrofit and technical diligence logic.",
                "CRITICAL",
            )
        else:
            add_seed(
                "HVAC / BMS / electrical system inventory",
                "Engineering records, O&M manuals, or site operator",
                "System inventory is required before any retrofit or reliability claim can be defended.",
                ["systems_cluster"],
                ["LC-ASSET-01", "LC-OPS-04"],
                "Unlocks bounded retrofit and technical diligence logic.",
                "CRITICAL",
            )
    if "vintage_structure_cluster" in missing_clusters and not cluster_covered("vintage_structure_cluster"):
        if family == "manufacturing":
            add_seed(
                "Commissioning date and major process / utility upgrade history",
                "Owner records, permit history, or plant engineering records",
                "Vintage and process-upgrade history remain underpopulated.",
                ["vintage_structure_cluster", "systems_cluster"],
                ["LC-ASSET-01", "LC-OPS-02"],
                "Improves process-age interpretation and modernization context.",
                "HIGH",
            )
        elif family == "infrastructure":
            add_seed(
                "Commissioning date and major equipment replacement / capacity upgrade history",
                "Owner records, asset manager history, or engineering records",
                "Vintage and equipment-upgrade history remain underpopulated.",
                ["vintage_structure_cluster", "systems_cluster"],
                ["LC-ASSET-01", "LC-OPS-02"],
                "Improves resilience-age interpretation and modernization context.",
                "HIGH",
            )
        elif family == "oil_gas":
            add_seed(
                "Commissioning date and major turnaround / unit replacement history",
                "Owner records, turnaround history, or engineering records",
                "Vintage and unit-upgrade history remain underpopulated.",
                ["vintage_structure_cluster", "systems_cluster"],
                ["LC-ASSET-01", "LC-OPS-02"],
                "Improves process-age interpretation and maintenance-cycle context.",
                "HIGH",
            )
        elif family == "logistics":
            add_seed(
                "Commissioning date and major dock / refrigeration / building upgrade history",
                "Owner records, permit history, or engineering records",
                "Vintage and upgrade history remain underpopulated.",
                ["vintage_structure_cluster", "systems_cluster"],
                ["LC-ASSET-01", "LC-OPS-02"],
                "Improves refrigeration-age interpretation and upgrade context.",
                "HIGH",
            )
        else:
            add_seed(
                "Year built, major renovations, and structural change history",
                "Owner records, permit history, or assessor history",
                "Vintage and structural history remain underpopulated.",
                ["vintage_structure_cluster", "systems_cluster"],
                ["LC-ASSET-01", "LC-OPS-02"],
                "Improves system-age interpretation and CAPEX context.",
                "HIGH",
            )
    return seed_rows[:10]


def _build_investment_uncertainty_map_seed(
    minimum_evidence_pack_seed: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for item in minimum_evidence_pack_seed[:6]:
        related = list(item.get("related_clusters", []) or [])
        rows.append(
            {
                "uncertainty": item.get("why_needed", "") or item.get("evidence_item", ""),
                "why_it_matters_financially": item.get("decision_unlock", ""),
                "decision_it_blocks": ", ".join(item.get("cases_resolved", []) or []),
                "evidence_needed": item.get("evidence_item", ""),
                "priority": item.get("effort", "HIGH"),
                "related_clusters": related,
            }
        )
    return rows


def _build_asset_context_readiness_table_seed(
    asset_context_readiness: str,
    missing_clusters: list[str],
) -> list[dict[str, Any]]:
    cluster_labels = {
        "identity_cluster": "Identity",
        "geometry_size_cluster": "Geometry / Size",
        "vintage_structure_cluster": "Vintage / Structure",
        "operating_regime_cluster": "Operating Regime",
        "fuel_energy_cluster": "Fuel / Energy",
        "systems_cluster": "Systems",
        "tenant_control_cluster": "Tenant Control",
        "regulatory_cluster": "Regulatory Applicability",
        "financial_boundary_cluster": "Financial Boundary",
    }
    rows: list[dict[str, Any]] = []
    for cluster_id, label in cluster_labels.items():
        missing = cluster_id in missing_clusters
        rows.append(
            {
                "cluster_id": cluster_id,
                "cluster": label,
                "status": "BLOCKING" if missing else "PARTIAL",
                "current_evidence": "NOT OBSERVED" if missing else "Public signals or intake declarations available",
                "consequence": (
                    "Blocks stronger technical or financial advancement."
                    if missing
                    else "Supports screening-grade reading only until local evidence arrives."
                ),
            }
        )
    rows.append(
        {
            "cluster_id": "asset_context_readiness",
            "cluster": "Asset Context Readiness",
            "status": asset_context_readiness.upper(),
            "current_evidence": asset_context_readiness,
            "consequence": "Determines which report class is admissible.",
        }
    )
    return rows


def _build_financial_boundary_seed(enriched: dict[str, Any], asset_context_readiness: str) -> dict[str, Any]:
    financials = enriched.get("financials", {}) if isinstance(enriched.get("financials", {}), dict) else {}
    return {
        "scope_boundary": "consolidated_entity_level_only" if financials else "financial_context_not_observed",
        "financial_context_present": bool(financials),
        "asset_context_readiness": asset_context_readiness,
        "boundary_rule": (
            "Issuer-level finance may inform scale or fragility but cannot compensate for missing asset truth."
        ),
    }


def _build_regulatory_screening_seed(compliance_case: dict[str, Any]) -> dict[str, Any]:
    return {
        "applicability_state": compliance_case.get("applicability_state", ""),
        "compliance_posture_state": compliance_case.get("compliance_posture_state", ""),
        "hardening_requirements": compliance_case.get("hardening_requirements", []),
        "trigger_field_register": compliance_case.get("trigger_field_register", []),
        "screening_basis_register": compliance_case.get("screening_basis_register", []),
    }


def _safe_text(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, str):
        return value.strip()
    if isinstance(value, (int, float)) and not value:
        return ""
    if isinstance(value, list):
        parts = [str(item).strip() for item in value if str(item).strip()]
        return ", ".join(parts)
    if isinstance(value, dict):
        return ""
    return str(value).strip()


def _canonical_scope(scope: Any) -> str:
    normalized = str(scope or "").strip()
    upper = normalized.upper()
    if upper in {"ASSET_LEVEL", "ENTITY_LEVEL", "PORTFOLIO_LEVEL", "JURISDICTION_LEVEL", "BENCHMARK_LEVEL"}:
        return upper
    lowered = normalized.lower()
    if lowered == "asset_jurisdiction_specific" or ("asset" in lowered and "jurisdiction" in lowered):
        return "ASSET_LEVEL"
    if "benchmark" in lowered:
        return "BENCHMARK_LEVEL"
    if "portfolio" in lowered:
        return "PORTFOLIO_LEVEL"
    if any(token in lowered for token in ("entity", "issuer", "sec", "owner_context")):
        return "ENTITY_LEVEL"
    if any(token in lowered for token in ("jurisdiction", "regulatory", "climate", "utility_territory")):
        return "JURISDICTION_LEVEL"
    if "asset" in lowered or "property" in lowered or "permit" in lowered or "geospatial" in lowered:
        return "ASSET_LEVEL"
    return upper or "UNKNOWN"


def _first_present(data: dict[str, Any] | None, keys: list[str]) -> Any:
    if not isinstance(data, dict):
        return None
    for key in keys:
        value = data.get(key)
        text = _safe_text(value)
        if text:
            return value
    return None


def _as_number(value: Any) -> float | int | None:
    if isinstance(value, bool):
        return None
    if isinstance(value, (int, float)):
        return value
    text = str(value or "").strip().replace(",", "")
    if not text or text.upper() in {"NONE", "NULL", "N/A", "NA"}:
        return None
    try:
        number = float(text)
    except ValueError:
        return None
    return int(number) if number.is_integer() else number


def _tceq_criteria_emissions_summary(record: dict[str, Any]) -> str:
    if not isinstance(record, dict) or not record:
        return ""
    pollutant_fields = [
        ("NOX TPY", "NOx"),
        ("VOC TPY", "VOC"),
        ("CO TPY", "CO"),
        ("SO2 TPY", "SO2"),
        ("PM10 TPY", "PM10"),
        ("PM2.5 TPY", "PM2.5"),
    ]
    observed: list[str] = []
    for field, label in pollutant_fields:
        value = _as_number(record.get(field))
        if value is None:
            continue
        observed.append(f"{label} {value:g} tpy")
        if len(observed) >= 4:
            break
    if not observed:
        return ""
    year = _safe_text(record.get("REPORTING YEAR"))
    prefix = "TCEQ criteria-air emissions record observed"
    if year:
        prefix += f" ({year})"
    return f"{prefix}: " + "; ".join(observed)


def _tceq_permit_record_summary(record: dict[str, Any]) -> str:
    if not isinstance(record, dict) or not record:
        return ""
    rn = _safe_text(record.get("RN"))
    account = _safe_text(record.get("ACCOUNT"))
    year = _safe_text(record.get("REPORTING YEAR"))
    site = _safe_text(record.get("SITE"))
    parts = []
    if rn:
        parts.append(f"RN {rn}")
    if account:
        parts.append(f"account {account}")
    if year:
        parts.append(f"{year}")
    summary = "TCEQ point-source permit / emissions registry observed"
    if parts:
        summary += f" ({'; '.join(parts)})"
    if site:
        summary += f" for {site}"
    return summary


def _nyc_pluto_record(enriched: dict[str, Any]) -> dict[str, Any]:
    record = enriched.get("pluto_property", {}) if isinstance(enriched.get("pluto_property", {}), dict) else {}
    if record:
        return record
    record = enriched.get("nyc_pluto_property", {}) if isinstance(enriched.get("nyc_pluto_property", {}), dict) else {}
    return record if record else {}


def _nyc_dof_property_record(enriched: dict[str, Any]) -> dict[str, Any]:
    record = enriched.get("dof_property_record", {}) if isinstance(enriched.get("dof_property_record", {}), dict) else {}
    if record:
        return record
    record = enriched.get("nyc_dof_property_record", {}) if isinstance(enriched.get("nyc_dof_property_record", {}), dict) else {}
    return record if record else {}


def _nyc_latest_ll84_record(enriched: dict[str, Any]) -> dict[str, Any]:
    payload = enriched.get("ll84_energy_benchmarking", {}) if isinstance(enriched.get("ll84_energy_benchmarking", {}), dict) else {}
    if not payload:
        payload = enriched.get("nyc_ll84_energy_benchmarking", {}) if isinstance(enriched.get("nyc_ll84_energy_benchmarking", {}), dict) else {}
    records = payload.get("records", []) if isinstance(payload.get("records", []), list) else []
    if not records:
        return {}

    def _year(record: dict[str, Any]) -> int:
        for key in ("report_year", "reporting_year", "year", "calendar_year"):
            value = _as_number(record.get(key))
            if value is not None:
                return int(value)
        return -1

    return max((row for row in records if isinstance(row, dict)), key=_year, default={})


def _nyc_ll97_cbl_record(enriched: dict[str, Any], preferred_bin: Any = "") -> dict[str, Any]:
    payload = enriched.get("ll97_covered_buildings_list", {}) if isinstance(enriched.get("ll97_covered_buildings_list", {}), dict) else {}
    if not payload:
        payload = enriched.get("nyc_ll97_covered_buildings_list", {}) if isinstance(enriched.get("nyc_ll97_covered_buildings_list", {}), dict) else {}
    preferred_bin_text = _safe_text(preferred_bin)
    rows = payload.get("matched_rows", []) if isinstance(payload.get("matched_rows", []), list) else []
    if preferred_bin_text:
        for row in rows:
            if isinstance(row, dict) and _safe_text(row.get("bin")) == preferred_bin_text:
                return row
    selected = payload.get("selected_row", {}) if isinstance(payload.get("selected_row", {}), dict) else {}
    if selected:
        return selected
    return rows[0] if rows and isinstance(rows[0], dict) else {}


def _ll97_pathway_label(pathway_value: Any) -> str:
    text = _safe_text(pathway_value)
    if not text:
        return ""
    try:
        numeric = int(float(text))
    except ValueError:
        return text
    return {
        0: "CP0 — Article 320 beginning 2024",
        1: "CP1 — Article 320 beginning 2026",
        2: "CP2 — Article 320 beginning 2035",
        3: "CP3 — Article 321 one-time compliance",
        4: "CP4 — City Buildings / NYCHA",
    }.get(numeric, f"CP{numeric}")


def _nyc_dob_permit_summary(enriched: dict[str, Any]) -> dict[str, Any]:
    permits = enriched.get("dob_permits_recent")
    if not isinstance(permits, list):
        permits = enriched.get("nyc_dob_permits")
    permits = permits if isinstance(permits, list) else []
    if not permits:
        return {}

    latest = permits[0] if isinstance(permits[0], dict) else {}
    work_text_parts: list[str] = []
    for permit in permits[:5]:
        if not isinstance(permit, dict):
            continue
        for key in ("job_type", "work_type", "job_description", "permit_type", "filing_type", "work_description"):
            text = _safe_text(permit.get(key))
            if text and text not in work_text_parts:
                work_text_parts.append(text)
    work_text = "; ".join(work_text_parts[:4])
    hvac_text = ""
    lowered = work_text.lower()
    if any(token in lowered for token in ("hvac", "mechanical", "boiler", "chiller", "air handling", "duct")):
        hvac_text = work_text
    return {
        "permit_count": len(permits),
        "latest_issuance_date": _safe_text(latest.get("issuance_date") or latest.get("filing_date")),
        "permit_summary": work_text,
        "hvac_summary": hvac_text,
    }


def _local_benchmark_payload(enriched: dict[str, Any]) -> dict[str, Any]:
    payload = enriched.get("asset_energy_behavior_reference", {})
    return payload if isinstance(payload, dict) else {}


def _local_benchmark_record(enriched: dict[str, Any]) -> dict[str, Any]:
    payload = _local_benchmark_payload(enriched)
    records = payload.get("records", []) if isinstance(payload.get("records", []), list) else []
    if not records:
        return {}

    def _year(record: dict[str, Any]) -> int:
        for key in ("report_year", "reporting_year", "benchmark_year", "program_year", "year", "calendar_year"):
            value = _as_number(record.get(key))
            if value is not None:
                return int(value)
        return -1

    return max((row for row in records if isinstance(row, dict)), key=_year, default={})


def _la_assessor_record(enriched: dict[str, Any]) -> dict[str, Any]:
    extended = enriched.get("extended_sources", {}) if isinstance(enriched.get("extended_sources", {}), dict) else {}
    payload = enriched.get("la_county_assessor_property_record", {})
    if not isinstance(payload, dict) or not payload:
        payload = extended.get("la_county_assessor_property_record", {})
    if not isinstance(payload, dict) or not payload:
        return {}
    detail = payload.get("parcel_detail", {})
    if isinstance(detail, dict) and detail:
        return detail
    selected = payload.get("selected_row", {})
    return selected if isinstance(selected, dict) else {}


def _industrial_emissions_payload(enriched: dict[str, Any], *keys: str) -> dict[str, Any]:
    extended = enriched.get("extended_sources", {}) if isinstance(enriched.get("extended_sources", {}), dict) else {}
    for key in keys:
        payload = enriched.get(key, {})
        if isinstance(payload, dict) and payload:
            return payload
        nested_payload = extended.get(key, {})
        if isinstance(nested_payload, dict) and nested_payload:
            return nested_payload
    return {}


def _accepted_source_rows(source_register: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [row for row in source_register if row.get("accepted")]


def _select_source(
    source_rows: list[dict[str, Any]],
    *,
    scope: str | None = None,
    source_family: str | None = None,
    title_tokens: list[str] | None = None,
) -> dict[str, Any]:
    tokens = [token.lower() for token in (title_tokens or [])]
    for row in source_rows:
        if scope and _canonical_scope(row.get("scope")) != scope:
            continue
        if source_family and str(row.get("source_family", "")).strip() != source_family:
            continue
        haystack = " ".join(
            [
                str(row.get("title", "")),
                str(row.get("url", "")),
                str(row.get("source_id", "")),
                str(row.get("source_family", "")),
            ]
        ).lower()
        if tokens and not any(token in haystack for token in tokens):
            continue
        return row
    return {}


def _field_admissibility(scope: str, authority_score: str, status: str) -> str:
    if status in {"NOT_OBSERVED", "NOT_PUBLICLY_AVAILABLE", "REQUIRES_CLIENT_INPUT", "BLOCKING_FIELD"}:
        return "NOT_OBSERVED"
    scope = _canonical_scope(scope)
    authority_score = str(authority_score or "").strip().lower()
    if scope == "ENTITY_LEVEL":
        return "ENTITY_CONTEXT_ONLY"
    if scope == "PORTFOLIO_LEVEL":
        return "PORTFOLIO_CONTEXT_ONLY"
    if scope == "JURISDICTION_LEVEL":
        return "JURISDICTION_CONTEXT_ONLY"
    if scope == "BENCHMARK_LEVEL":
        return "BENCHMARK_ONLY"
    if authority_score == "high":
        return "CONFIRMED_ASSET_LEVEL"
    if authority_score == "declared_input":
        return "DECLARED_INPUT_ONLY"
    return "OBSERVED_PUBLIC_ASSET_LEVEL"


def _field_support_semantics(field: str, admissibility: str, status: str) -> dict[str, bool]:
    field_name = str(field or "").strip()
    if status in {"NOT_OBSERVED", "NOT_PUBLICLY_AVAILABLE", "REQUIRES_CLIENT_INPUT", "BLOCKING_FIELD"}:
        return {
            "identity_supported": False,
            "physical_substrate_supported": False,
            "operating_substrate_supported": False,
            "regulatory_supported": False,
        }

    asset_level_admissibility = {
        "CONFIRMED_ASSET_LEVEL",
        "OBSERVED_PUBLIC_ASSET_LEVEL",
        "INFERRED_ASSET_LEVEL",
    }
    identity_fields = {
        "asset_name",
        "address",
        "parcel_id",
        "property_id",
        "building_id",
        "asset_vs_entity_classification",
    }
    physical_substrate_fields = {
        "GFA",
        "rentable_area",
        "floor_count",
        "year_built",
        "renovations",
        "occupancy_use",
        "site_area",
        "construction_type",
        "structural_constraints",
    }
    operating_substrate_fields = {
        "tenant_control_boundary",
        "owner_control_boundary",
        "primary_fuel",
        "secondary_fuel",
        "HVAC_type",
        "BMS_control_system",
        "operating_schedule",
        "process_flow",
        "throughput",
        "production_volume",
        "load_driver",
        "downtime_profile",
        "maintenance_history",
        "reliability_history",
    }
    regulatory_fields = {
        "energy_benchmarking_record",
        "current_EUI",
        "emissions",
        "compliance_filings",
        "permits",
        "electricity_utility",
        "gas_utility",
        "jurisdiction",
        "applicable_rule_family",
        "penalty_rate",
        "compliance_period",
    }
    asset_supported = admissibility in asset_level_admissibility
    regulatory_supported = field_name in regulatory_fields and admissibility in (
        asset_level_admissibility | {"JURISDICTION_CONTEXT_ONLY"}
    )
    return {
        "identity_supported": field_name in identity_fields and asset_supported,
        "physical_substrate_supported": field_name in physical_substrate_fields and asset_supported,
        "operating_substrate_supported": field_name in operating_substrate_fields and asset_supported,
        "regulatory_supported": regulatory_supported,
    }


_CANONICAL_CONTEXT_CLUSTER_FIELDS: dict[str, set[str]] = {
    "identity_cluster": {
        "asset_name",
        "address",
        "parcel_id",
        "property_id",
        "building_id",
        "asset_class",
    },
    "boundary_cluster": {
        "tenant_control_boundary",
        "owner_control_boundary",
    },
    "geometry_size_cluster": {
        "GFA",
        "rentable_area",
        "floor_count",
        "site_area",
    },
    "vintage_structure_cluster": {
        "year_built",
        "renovations",
        "construction_type",
    },
    "operating_regime_cluster": {
        "occupancy_use",
        "operating_schedule",
        "load_driver",
        "throughput",
        "process_flow",
        "downtime_profile",
    },
    "fuel_energy_cluster": {
        "primary_fuel",
        "secondary_fuel",
        "current_EUI",
        "emissions",
        "energy_benchmarking_record",
        "electricity_utility",
        "gas_utility",
    },
    "systems_cluster": {
        "HVAC_type",
        "BMS_control_system",
    },
    "control_boundary_cluster": {
        "tenant_control_boundary",
        "owner_control_boundary",
    },
    "regulatory_cluster": {
        "compliance_filings",
        "permits",
        "current_EUI",
        "emissions",
        "electricity_utility",
        "gas_utility",
    },
}


def _row_supports_canonical_cluster(row: dict[str, Any], cluster_name: str) -> bool:
    field_name = str(row.get("field", "")).strip()
    if field_name not in _CANONICAL_CONTEXT_CLUSTER_FIELDS.get(cluster_name, set()):
        return False
    if str(row.get("status", "")).strip() in {
        "NOT_OBSERVED",
        "NOT_PUBLICLY_AVAILABLE",
        "REQUIRES_CLIENT_INPUT",
        "BLOCKING_FIELD",
    }:
        return False
    if str(row.get("confirmation_state", "")).strip() == "DECLARED_BY_USER":
        return False
    if cluster_name == "identity_cluster":
        return bool(row.get("identity_supported"))
    if cluster_name in {"geometry_size_cluster", "vintage_structure_cluster"}:
        return bool(row.get("physical_substrate_supported") or row.get("identity_supported"))
    if cluster_name == "boundary_cluster":
        return bool(row.get("operating_substrate_supported"))
    if cluster_name in {"operating_regime_cluster", "systems_cluster", "control_boundary_cluster"}:
        return bool(
            row.get("operating_substrate_supported")
            or row.get("physical_substrate_supported")
        )
    if cluster_name in {"fuel_energy_cluster", "regulatory_cluster"}:
        return bool(
            row.get("regulatory_supported")
            or row.get("operating_substrate_supported")
            or row.get("physical_substrate_supported")
        )
    return False


def _canonical_asset_context_state(
    supported_clusters: set[str],
    missing_clusters: list[str],
) -> str:
    screening_ready = {
        "identity_cluster",
        "geometry_size_cluster",
        "regulatory_cluster",
    }.issubset(supported_clusters)
    operable_clusters = {
        "operating_regime_cluster",
        "fuel_energy_cluster",
        "systems_cluster",
    }
    control_ready = bool(
        {"control_boundary_cluster", "boundary_cluster"} & supported_clusters
    )
    if screening_ready and operable_clusters.issubset(supported_clusters) and control_ready:
        return "asset_context_operable"
    if screening_ready:
        return "asset_context_minimal"
    if "identity_cluster" in supported_clusters:
        return "asset_context_insufficient"
    return "location_only"


def _build_canonical_asset_context_summary(
    asset_field_register: list[dict[str, Any]],
    early_asset_context_readiness: str,
) -> dict[str, Any]:
    cluster_rows: list[dict[str, Any]] = []
    supported_clusters: list[str] = []
    missing_clusters: list[str] = []
    supported_field_register: list[dict[str, Any]] = []

    for cluster_name in _CANONICAL_CONTEXT_CLUSTER_FIELDS:
        supporting_rows = [
            row
            for row in asset_field_register
            if _row_supports_canonical_cluster(row, cluster_name)
        ]
        supporting_fields = [
            str(row.get("field", "")).strip()
            for row in supporting_rows
            if str(row.get("field", "")).strip()
        ]
        if supporting_fields:
            supported_clusters.append(cluster_name)
            for row in supporting_rows:
                if row not in supported_field_register:
                    supported_field_register.append(row)
        else:
            missing_clusters.append(cluster_name)
        cluster_rows.append(
            {
                "cluster_name": cluster_name,
                "supported": bool(supporting_fields),
                "supporting_fields": supporting_fields,
                "supporting_source_ids": [
                    str(row.get("source_id", "")).strip()
                    for row in supporting_rows
                    if str(row.get("source_id", "")).strip()
                ],
            }
        )

    supported_cluster_set = set(supported_clusters)
    canonical_state = _canonical_asset_context_state(
        supported_cluster_set,
        missing_clusters,
    )
    screening_supported = {
        "identity_cluster",
        "geometry_size_cluster",
        "regulatory_cluster",
    }.issubset(supported_cluster_set)
    return {
        "early_asset_context_readiness": str(early_asset_context_readiness or "").strip(),
        "canonical_asset_context_state": canonical_state,
        "screening_supported": screening_supported,
        "supported_clusters": supported_clusters,
        "missing_clusters": missing_clusters,
        "cluster_register": cluster_rows,
        "supported_field_count": len(supported_field_register),
        "supported_field_register": supported_field_register,
    }


def _asset_field_row(
    *,
    field: str,
    value: Any,
    source_row: dict[str, Any] | None = None,
    default_scope: str = "ASSET_LEVEL",
    default_authority: str = "declared_input",
    notes: str = "",
    critical: bool = False,
) -> dict[str, Any]:
    source_row = source_row or {}
    text_value = _safe_text(value)
    status = "OBSERVED"
    if not text_value:
        status = "BLOCKING_FIELD" if critical else "NOT_OBSERVED"
    scope = _canonical_scope(source_row.get("scope", "") or default_scope)
    authority_score = str(source_row.get("authority_score", "") or default_authority).strip().lower()
    admissibility = _field_admissibility(scope, authority_score, status)
    support_semantics = _field_support_semantics(field, admissibility, status)
    if support_semantics["identity_supported"] and not (
        support_semantics["physical_substrate_supported"]
        or support_semantics["operating_substrate_supported"]
    ):
        notes = (
            f"{notes} Source confirms identity only, not physical operating substrate."
            if notes
            else "Source confirms identity only, not physical operating substrate."
        )
    return {
        "field": field,
        "value": text_value or status,
        "status": status,
        "source_id": str(source_row.get("source_id", "")).strip() or f"declared_input::{field}",
        "source_family": str(source_row.get("source_family", "")).strip(),
        "source_title": str(source_row.get("title", "")).strip(),
        "scope": scope,
        "authority_score": authority_score,
        "recency": str(source_row.get("recency", "")).strip() or "unknown",
        "admissibility": admissibility,
        **support_semantics,
        "notes": notes,
    }


def _build_asset_field_register(
    *,
    target_definition: dict[str, Any],
    fi: dict[str, Any],
    source_register: list[dict[str, Any]],
    benchmark_context: dict[str, Any],
    compliance_case: dict[str, Any],
    enriched: dict[str, Any],
) -> list[dict[str, Any]]:
    accepted_sources = _accepted_source_rows(source_register)
    location = fi.get("input_01_location", {})
    facility_type = fi.get("input_02_facility_type", {})
    sector = fi.get("input_03_sector", {})
    primary_use = fi.get("input_04_primary_use", {})
    size = fi.get("input_05_size", {})
    vintage = fi.get("input_06_vintage", {})
    schedule = fi.get("input_07_operating_schedule", {})
    energy = fi.get("input_08_energy_fuel", {})
    systems = fi.get("input_09_known_systems", {})
    dof_record = _nyc_dof_property_record(enriched)
    pluto_record = _nyc_pluto_record(enriched)
    ll84_record = _nyc_latest_ll84_record(enriched)
    local_benchmark_payload = _local_benchmark_payload(enriched)
    local_benchmark_record = _local_benchmark_record(enriched)
    la_assessor_record = _la_assessor_record(enriched)
    ll84_bin = _safe_text(_first_present(ll84_record, ["nyc_building_identification", "bin", "building_id"]))
    ll97_cbl_record = _nyc_ll97_cbl_record(enriched, preferred_bin=ll84_bin or location.get("bin"))
    dob_summary = _nyc_dob_permit_summary(enriched)
    ll97_public_filing_payload = enriched.get("ll97_public_filing_candidate", {}) if isinstance(enriched.get("ll97_public_filing_candidate", {}), dict) else {}
    ll97_public_filing_best = ll97_public_filing_payload.get("best_candidate", {}) if isinstance(ll97_public_filing_payload.get("best_candidate", {}), dict) else {}
    tceq_payload = _industrial_emissions_payload(enriched, "tceq_permits_and_emissions", "state_environmental_agency_permits")
    tceq_records = tceq_payload.get("records", []) if isinstance(tceq_payload.get("records", []), list) else []
    tceq_record = tceq_records[0] if tceq_records and isinstance(tceq_records[0], dict) else {}
    ghgrp_payload = _industrial_emissions_payload(enriched, "epa_ghgrp_facilities")
    ghgrp_records = ghgrp_payload.get("records", []) if isinstance(ghgrp_payload.get("records", []), list) else []
    ghgrp_record = ghgrp_records[0] if ghgrp_records and isinstance(ghgrp_records[0], dict) else {}

    dof_source = _select_source(
        accepted_sources,
        scope="ASSET_LEVEL",
        title_tokens=["nyc_dof_property_record", "nyc_open_data:dof_property", "nyc_dof_acris_legals", "8h5j-fqxa"],
    )
    pluto_source = _select_source(accepted_sources, scope="ASSET_LEVEL", title_tokens=["nyc_open_data:pluto", "nyc_pluto_property", "pluto"])
    sf_assessor_source = _select_source(accepted_sources, scope="ASSET_LEVEL", title_tokens=["sf_assessor_property_record", "sf_parcels_active_retired", "8jwb-2stv"])
    la_assessor_source = _select_source(accepted_sources, scope="ASSET_LEVEL", title_tokens=["la_county_assessor_property_record"])
    ca_assessor_source = _select_source(accepted_sources, scope="ASSET_LEVEL", title_tokens=["ca_county_assessor_property_record"])
    tx_county_source = _select_source(
        accepted_sources,
        scope="ASSET_LEVEL",
        title_tokens=[
            "county_appraisal_district_property_record",
            "harris_county_appraisal_district_property_record",
            "county_assessor_or_appraisal_property_record",
        ],
    )
    cbl_source = _select_source(
        accepted_sources,
        scope="ASSET_LEVEL",
        title_tokens=["nyc_ll97_covered_buildings_list", "cbl26", "sustainability_cbl"],
    )
    ll97_public_filing_source = _select_source(
        accepted_sources,
        scope="ASSET_LEVEL",
        title_tokens=["nyc_ll97_public_filing_candidate", "article 321", "ll97 filing", "greenhouse gas emissions report"],
    )
    ll84_source = _select_source(accepted_sources, scope="ASSET_LEVEL", title_tokens=["nyc_open_data:ll84"]) or _select_source(
        accepted_sources,
        scope="ASSET_LEVEL",
        title_tokens=["nyc_ll84_energy_benchmarking", "ll84", "energy star"],
    )
    local_benchmark_source = _select_source(
        accepted_sources,
        scope="ASSET_LEVEL",
        source_family="benchmarking_disclosure_record",
        title_tokens=["city_benchmarking_san_francisco", "city_benchmarking_los_angeles", "benchmarking"],
    )
    dob_source = _select_source(accepted_sources, scope="ASSET_LEVEL", title_tokens=["nyc_open_data:dob_permits", "nyc_dob_permits", "dob", "permit"])
    tceq_source = _select_source(accepted_sources, scope="ASSET_LEVEL", title_tokens=["tceq_permits_and_emissions", "state_environmental_agency_permits"])
    ghgrp_source = _select_source(accepted_sources, scope="ASSET_LEVEL", title_tokens=["epa_ghgrp_emitters"])
    identity_source = (
        dof_source
        or pluto_source
        or sf_assessor_source
        or la_assessor_source
        or ca_assessor_source
        or tx_county_source
        or ll84_source
        or local_benchmark_source
        or dob_source
        or _select_source(accepted_sources, scope="ASSET_LEVEL")
    )
    jurisdiction_source = _select_source(accepted_sources, scope="JURISDICTION_LEVEL")
    benchmark_source = ll84_source or local_benchmark_source or _select_source(accepted_sources, scope="BENCHMARK_LEVEL")
    entity_source = _select_source(accepted_sources, scope="ENTITY_LEVEL")

    uses = primary_use.get("uses", []) if isinstance(primary_use.get("uses", []), list) else []
    use_mix = uses or [primary_use.get(f"use_{i}") for i in range(1, 6) if primary_use.get(f"use_{i}")]
    pluto_use = _safe_text(_first_present(pluto_record, ["landuse", "building_class", "bldgclass", "primary_use"]))
    ll84_use = _safe_text(_first_present(ll84_record, ["largest_property_use_type", "primary_property_type_self", "primary_property_type", "primary_property_type_self_selected"]))
    if not use_mix and pluto_use:
        use_mix = [pluto_use]
    elif not use_mix and ll84_use:
        use_mix = [ll84_use]
    parcel_id = next(
        (
            str(location.get(key, "")).strip()
            for key in ("parcel_id", "property_id", "bbl", "bin", "lot")
            if str(location.get(key, "")).strip()
        ),
        "",
    )
    if not parcel_id:
        parcel_id = _safe_text(
            dof_record.get("bbl")
            or la_assessor_record.get("AIN")
            or location.get("bbl")
            or benchmark_context.get("local_property_id")
            or _first_present(local_benchmark_record, ["parcel_number", "apn", "property_id"])
        )
    property_id = _safe_text(
        location.get("property_id")
        or dof_record.get("bbl")
        or la_assessor_record.get("AIN")
        or benchmark_context.get("local_property_id")
        or _first_present(local_benchmark_record, ["parcel_number", "apn", "property_id", "building_id"])
        or _first_present(ll84_record, ["property_id"])
        or ll97_cbl_record.get("bin")
        or location.get("bin")
        or location.get("bbl")
    )
    site_area = size.get("site_area_sqft") or _as_number(_first_present(pluto_record, ["lotarea", "site_area", "land_area_sqft"])) or _as_number(_first_present(la_assessor_record, ["SqftLot", "sqft_lot"]))
    gfa_value = (
        size.get("GFA_sqft")
        or size.get("GFA_m2")
        or _as_number(_first_present(pluto_record, ["bldgarea", "gross_floor_area", "gross_sqft", "building_area"]))
        or _as_number(_first_present(la_assessor_record, ["SqftMain", "sqft_main"]))
        or _as_number(ll97_cbl_record.get("gross_square_footage"))
        or _as_number(benchmark_context.get("local_gfa_sqft"))
        or _as_number(_first_present(local_benchmark_record, ["floor_area", "gross_floor_area", "gross_floor_area_sqft", "building_area", "area_sqft"]))
    )
    floor_count = size.get("floor_count") or size.get("floors") or size.get("stories") or _as_number(_first_present(pluto_record, ["numfloors", "floors", "stories"]))
    year_built = (
        vintage.get("year_built")
        or _as_number(_first_present(pluto_record, ["yearbuilt", "year_built"]))
        or _as_number(_first_present(la_assessor_record, ["YearBuilt", "year_built"]))
        or _as_number(benchmark_context.get("local_year_built"))
        or _as_number(_first_present(local_benchmark_record, ["year_built", "yearbuilt"]))
    )
    benchmark_record_value = benchmark_context.get("benchmark_source")
    if ll84_record:
        ll84_year = _safe_text(benchmark_context.get("ll84_reporting_year") or _first_present(ll84_record, ["report_year", "reporting_year", "year"]))
        benchmark_record_value = f"NYC LL84 public disclosure{f' ({ll84_year})' if ll84_year else ''}"
    current_eui_value = benchmark_context.get("adjusted_EUI_estimate_kBtu_sqft")
    emissions_value = (
        benchmark_context.get("ll84_emissions_metric_tons_co2e")
        or _first_present(
            ll84_record,
            [
                "total_location_based_ghg",
                "net_emissions_metric_tons",
                "total_ghg_emissions_metric_tons_co2e",
                "ghg_emissions_metric_tons_co2e",
                "direct_ghg_emissions_metric",
                "direct_ghg_emissions_metric_tons_co2e",
            ],
        )
        or _first_present(
            local_benchmark_record,
            ["total_ghg_emissions", "total_ghg_emissions_metric_tons_co2e", "total_location_based_ghg"],
        )
        or _first_present(ghgrp_record, ["Total reported direct emissions", "Total Reported Direct Emissions"])
        or _tceq_criteria_emissions_summary(tceq_record)
    )
    permit_value = dob_summary.get("permit_summary", "") or _tceq_permit_record_summary(tceq_record)
    compliance_filing_value = ""
    ll84_year = _safe_text(benchmark_context.get("ll84_reporting_year") or _first_present(ll84_record, ["report_year", "reporting_year", "year"]))
    ll97_pathway_label = _safe_text(ll97_cbl_record.get("ll97_compliance_pathway_label")) or _ll97_pathway_label(ll97_cbl_record.get("ll97_compliance_pathway"))
    public_filing_phrase = ""
    if ll97_public_filing_best:
        public_filing_phrase = (
            f"Public LL97 filing artifact observed ({_safe_text(ll97_public_filing_best.get('artifact_class'))}: "
            f"{_safe_text(ll97_public_filing_best.get('title')) or _safe_text(ll97_public_filing_best.get('url'))})"
        )
    if public_filing_phrase:
        if ll97_cbl_record and _safe_text(ll97_cbl_record.get("ll97_cbl_covered")).upper() == "Y":
            cbl_phrase = f"LL97 CBL coverage observed (2026 filing year{f'; {ll97_pathway_label}' if ll97_pathway_label else ''})"
            compliance_filing_value = f"{public_filing_phrase}; {cbl_phrase}"
            if ll84_record:
                compliance_filing_value += f"; LL84 public benchmarking disclosure observed{f' ({ll84_year})' if ll84_year else ''}"
        elif ll84_record:
            compliance_filing_value = f"{public_filing_phrase}; LL84 public benchmarking disclosure observed{f' ({ll84_year})' if ll84_year else ''}"
        else:
            compliance_filing_value = public_filing_phrase
    elif ll97_cbl_record and _safe_text(ll97_cbl_record.get("ll97_cbl_covered")).upper() == "Y":
        cbl_phrase = f"LL97 CBL coverage observed (2026 filing year{f'; {ll97_pathway_label}' if ll97_pathway_label else ''})"
        if ll84_record:
            compliance_filing_value = f"{cbl_phrase}; LL84 public benchmarking disclosure observed{f' ({ll84_year})' if ll84_year else ''}"
        else:
            compliance_filing_value = cbl_phrase
    elif ll84_record:
        compliance_filing_value = f"LL84 public benchmarking disclosure observed{f' ({ll84_year})' if ll84_year else ''}"
    elif compliance_case.get("applicability_state") == "applicability_likely":
        compliance_filing_value = compliance_case.get("applicability_state")
    elif tceq_record:
        compliance_filing_value = _tceq_permit_record_summary(tceq_record)
    hvac_type = ""
    hvac = systems.get("HVAC", {}) if isinstance(systems.get("HVAC", {}), dict) else {}
    if hvac:
        hvac_type = _safe_text(hvac.get("type") or hvac.get("type_mix") or hvac.get("technology"))
    if not hvac_type and dob_summary.get("hvac_summary"):
        hvac_type = f"permit clue: {dob_summary.get('hvac_summary')}"
    bms = systems.get("BMS", {}) if isinstance(systems.get("BMS", {}), dict) else {}
    bms_status = ""
    if bms:
        bms_status = _safe_text(bms.get("integration_level") or bms.get("present") or bms.get("controls"))
    renovation_value = _safe_text(vintage.get("major_renovations_known", [])) or permit_value
    benchmark_default_scope = benchmark_context.get("benchmark_source_scope") or "BENCHMARK_LEVEL"
    benchmark_default_authority = benchmark_context.get("benchmark_authority_score") or "medium"

    field_rows = [
        _asset_field_row(
            field="asset_name",
            value=target_definition.get("target_name") or target_definition.get("target_label"),
            source_row=identity_source,
            notes="Declared target label retained until stronger public asset identity evidence is found.",
            critical=True,
        ),
        _asset_field_row(
            field="address",
            value=target_definition.get("address_raw") or location.get("address"),
            source_row=identity_source,
            notes="Address confirmation is foundational to asset identity admissibility.",
            critical=True,
        ),
        _asset_field_row(
            field="owner",
            value=target_definition.get("owner_entity") or sector.get("owner_name"),
            source_row=entity_source,
            default_scope="ENTITY_LEVEL",
            notes="Owner context may inform issuer context but does not prove asset identity.",
            critical=False,
        ),
        _asset_field_row(
            field="parcel_id",
            value=parcel_id,
            source_row=identity_source,
            notes="Parcel or property record is a preferred public anchor for bounded asset confirmation.",
            critical=True,
        ),
        _asset_field_row(
            field="property_id",
            value=property_id,
            source_row=cbl_source or pluto_source or ll84_source or identity_source,
            notes="Property registry identifiers improve asset-to-address resolution.",
            critical=False,
        ),
        _asset_field_row(
            field="building_id",
            value=location.get("bin") or benchmark_context.get("local_building_id") or _first_present(pluto_record, ["bin", "building_id_number"]) or _first_present(ll84_record, ["nyc_building_identification", "bin", "building_id"]) or _first_present(local_benchmark_record, ["building_id", "bin"]) or ll97_cbl_record.get("bin"),
            source_row=ll84_source or local_benchmark_source or cbl_source or pluto_source or identity_source,
            notes="Jurisdiction-specific building identifiers help route DOB and benchmarking evidence.",
            critical=False,
        ),
        _asset_field_row(
            field="site_area",
            value=site_area,
            source_row=identity_source,
            notes="Site area can help bound density, logistics footprint, and jurisdiction screening.",
            critical=False,
        ),
        _asset_field_row(
            field="asset_class",
            value=target_definition.get("target_type") or facility_type.get("classification"),
            source_row=identity_source,
            notes="Asset class remains provisional until confirmed by asset-level evidence.",
            critical=True,
        ),
        _asset_field_row(
            field="GFA",
            value=gfa_value,
            source_row=pluto_source or identity_source,
            notes="Required for scale, EUI, compliance screening, and capital framing.",
            critical=True,
        ),
        _asset_field_row(
            field="rentable_area",
            value=size.get("rentable_office_sqft_approx") or size.get("rentable_area_sqft"),
            source_row=identity_source,
            notes="Useful for occupiable-area normalization and underwriting context.",
            critical=False,
        ),
        _asset_field_row(
            field="floor_count",
            value=floor_count,
            source_row=pluto_source or identity_source,
            notes="Vertical configuration may affect systems and compliance applicability.",
            critical=False,
        ),
        _asset_field_row(
            field="year_built",
            value=year_built,
            source_row=pluto_source or identity_source,
            notes="Asset vintage informs system age and modernization context.",
            critical=True,
        ),
        _asset_field_row(
            field="renovations",
            value=renovation_value,
            source_row=dob_source or identity_source,
            notes="Renovation history helps bound system age and upgrade relevance.",
            critical=False,
        ),
        _asset_field_row(
            field="occupancy_use",
            value=use_mix,
            source_row=pluto_source or ll84_source or identity_source,
            notes="Use mix is required before any meaningful operating archetype claim.",
            critical=True,
        ),
        _asset_field_row(
            field="tenant_control_boundary",
            value=primary_use.get("tenant_control_boundary") or primary_use.get("control_boundary"),
            source_row=identity_source,
            notes="Control boundary determines whether owner-facing interventions are even admissible.",
            critical=True,
        ),
        _asset_field_row(
            field="primary_fuel",
            value=energy.get("primary_fuel"),
            source_row=identity_source,
            notes="Fuel basis is required for carbon, transition, and utility-risk framing.",
            critical=True,
        ),
        _asset_field_row(
            field="electricity_utility",
            value=energy.get("utility_electricity"),
            source_row=jurisdiction_source,
            default_scope="JURISDICTION_LEVEL",
            notes="Utility territory can contextualize the asset but does not replace local bills or meter records.",
            critical=False,
        ),
        _asset_field_row(
            field="gas_utility",
            value=energy.get("utility_gas"),
            source_row=jurisdiction_source,
            default_scope="JURISDICTION_LEVEL",
            notes="Gas utility context remains secondary until local fuel evidence is received.",
            critical=False,
        ),
        _asset_field_row(
            field="HVAC_type",
            value=hvac_type,
            source_row=dob_source or identity_source,
            notes="System type is required before retrofit or controllability claims are admissible.",
            critical=True,
        ),
        _asset_field_row(
            field="BMS_control_system",
            value=bms_status,
            source_row=identity_source,
            notes="Controls and integration determine whether operational corrections are plausibly owner-controllable.",
            critical=False,
        ),
        _asset_field_row(
            field="operating_schedule",
            value=schedule.get("office_schedule") or schedule.get("shift_schedule") or schedule.get("service_duty_profile"),
            source_row=identity_source,
            notes="Operating regime is required to distinguish structural duty from correctable waste.",
            critical=True,
        ),
        _asset_field_row(
            field="energy_benchmarking_record",
            value=benchmark_record_value,
            source_row=benchmark_source,
            default_scope=benchmark_default_scope,
            default_authority=benchmark_default_authority,
            notes=(
                "Public asset-level benchmarking disclosure observed."
                if ll84_record or local_benchmark_record
                else "Benchmark reference is context only and never substitutes for local measurement."
            ),
            critical=False,
        ),
        _asset_field_row(
            field="current_EUI",
            value=current_eui_value,
            source_row=benchmark_source,
            default_scope=benchmark_default_scope,
            default_authority=benchmark_default_authority,
            notes=(
                "Current EUI comes from NYC LL84 public disclosure."
                if ll84_record
                else "Current EUI comes from local public benchmarking disclosure."
                if local_benchmark_record
                else "Current EUI is not locally observed here; any benchmark-only value remains bounded context."
            ),
            critical=True,
        ),
        _asset_field_row(
            field="emissions",
            value=emissions_value,
            source_row=ll84_source or local_benchmark_source or ghgrp_source or tceq_source or jurisdiction_source,
            default_scope="ASSET_LEVEL" if (ll84_record or local_benchmark_record or ghgrp_record or tceq_record) else "JURISDICTION_LEVEL",
            default_authority="high" if (ll84_record or local_benchmark_record or ghgrp_record or tceq_record) else "medium",
            notes=(
                "Annual public emissions basis observed from NYC benchmarking disclosure."
                if ll84_record
                else "Annual public emissions basis observed from local asset-specific disclosure or industrial emissions registry."
                if (local_benchmark_record or ghgrp_record or tceq_record)
                else "No local emissions filing or measured basis observed."
            ),
            critical=False,
        ),
        _asset_field_row(
            field="compliance_filings",
            value=compliance_filing_value,
            source_row=ll97_public_filing_source or cbl_source or ll84_source or tceq_source or jurisdiction_source,
            default_scope="ASSET_LEVEL" if (ll97_cbl_record or ll84_record or tceq_record) else "JURISDICTION_LEVEL",
            default_authority="high" if (ll97_cbl_record or ll84_record or tceq_record) else "medium",
            notes=(
                "Official CBL pathway and/or LL84 filing presence are observed, but they do not imply a certified LL97 compliance report or compliance closure."
                if ll97_cbl_record or ll84_record
                else "State environmental permit or emissions registry is observed at the asset address, but it does not by itself prove compliance closure."
                if tceq_record
                else "Applicability screening does not prove a local filing exists or is current."
            ),
            critical=True,
        ),
        _asset_field_row(
            field="permits",
            value=permit_value,
            source_row=dob_source or tceq_source or jurisdiction_source,
            default_scope="ASSET_LEVEL" if permit_value else "JURISDICTION_LEVEL",
            default_authority="high" if permit_value else "medium",
            notes=(
                "Permit history observed from NYC DOB public record."
                if dob_summary.get("permit_summary")
                else "Permit or environmental registry observed from TCEQ point-source reporting."
                if tceq_record
                else "Permit history has not yet been confirmed from a local record."
            ),
            critical=False,
        ),
        _asset_field_row(
            field="capex_history",
            value="",
            source_row=entity_source,
            default_scope="ENTITY_LEVEL",
            notes="Issuer-level CapEx context cannot substitute for asset-level capital history.",
            critical=False,
        ),
    ]
    return annotate_asset_field_register(field_rows)


def _build_missing_evidence_register(
    asset_field_register: list[dict[str, Any]],
    minimum_evidence_pack_seed: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    field_rules: dict[str, dict[str, str]] = {
        "asset_name": {
            "cluster": "identity_cluster",
            "why_it_matters": "Asset name and boundary confirmation are required to know whether the target is a real operating asset.",
            "decision_blocked": "target admissibility and any technical report class above classification.",
            "suggested_source": "assessor / parcel / owner asset record",
        },
        "address": {
            "cluster": "identity_cluster",
            "why_it_matters": "Address confirmation anchors every downstream public record and contamination check.",
            "decision_blocked": "target admissibility and all technical advancement.",
            "suggested_source": "assessor / parcel / owner asset record",
        },
        "parcel_id": {
            "cluster": "identity_cluster",
            "why_it_matters": "Parcel or property identifiers are the cleanest public way to distinguish a real asset from HQ or mailing context.",
            "decision_blocked": "asset identity confirmation and bounded diligence scoping.",
            "suggested_source": "municipal assessor / property record",
        },
        "asset_class": {
            "cluster": "identity_cluster",
            "why_it_matters": "Asset class determines which benchmarks, rules, and evidence requests are even relevant.",
            "decision_blocked": "benchmark routing and report-type admissibility.",
            "suggested_source": "owner asset page / brochure / assessor record",
        },
        "GFA": {
            "cluster": "geometry_size_cluster",
            "why_it_matters": "Gross floor area is required for EUI, penalties, scale, and CAPEX framing.",
            "decision_blocked": "compliance and retrofit underwriting.",
            "suggested_source": "municipal assessor / owner disclosure / lease brochure",
        },
        "year_built": {
            "cluster": "vintage_structure_cluster",
            "why_it_matters": "Vintage informs system age, modernization context, and structural constraints.",
            "decision_blocked": "system-age interpretation and bounded CAPEX framing.",
            "suggested_source": "assessor / permit history / owner disclosure",
        },
        "occupancy_use": {
            "cluster": "operating_regime_cluster",
            "why_it_matters": "Use mix determines schedule, control boundary, and whether benchmark classes are even relevant.",
            "decision_blocked": "operating archetype and energy-upside interpretation.",
            "suggested_source": "owner / operator / lease summary",
        },
        "tenant_control_boundary": {
            "cluster": "tenant_control_cluster",
            "why_it_matters": "Control boundary determines whether the owner can actually influence the energy or reliability outcome.",
            "decision_blocked": "retrofit, controllability, and owner-facing savings claims.",
            "suggested_source": "lease summary / operator confirmation / metering boundary",
        },
        "primary_fuel": {
            "cluster": "fuel_energy_cluster",
            "why_it_matters": "Fuel basis determines carbon, transition, and utility-risk exposure.",
            "decision_blocked": "compliance, transition, and energy-cost framing.",
            "suggested_source": "utility bills / operator records",
        },
        "HVAC_type": {
            "cluster": "systems_cluster",
            "why_it_matters": "System type determines whether any retrofit or controllability thesis is physically plausible.",
            "decision_blocked": "energy CAPEX and system-level diligence.",
            "suggested_source": "system inventory / MEP schedule / O&M manual",
        },
        "operating_schedule": {
            "cluster": "operating_regime_cluster",
            "why_it_matters": "Operating regime is required to separate structural load from correctable waste.",
            "decision_blocked": "energy savings claims and process-duty interpretation.",
            "suggested_source": "operator schedule / BMS logs / production calendar",
        },
        "current_EUI": {
            "cluster": "fuel_energy_cluster",
            "why_it_matters": "Current EUI or equivalent measured intensity is required to bound real performance.",
            "decision_blocked": "energy performance claims and underwriting with energy upside.",
            "suggested_source": "benchmark filing / utility bills / interval data",
        },
        "compliance_filings": {
            "cluster": "regulatory_cluster",
            "why_it_matters": "Current local filing is required before any compliance-facing interpretation becomes admissible.",
            "decision_blocked": "compliance posture and penalty exposure framing.",
            "suggested_source": "local filing portal / owner / operator",
        },
    }

    def seed_for_cluster(cluster: str) -> dict[str, Any]:
        for item in minimum_evidence_pack_seed:
            if cluster in (item.get("related_clusters", []) or []):
                return item
        return {}

    rows: list[dict[str, Any]] = []
    for field_row in asset_field_register:
        confirmation_state = str(field_row.get("confirmation_state", "")).strip()
        if (
            field_row.get("status") not in {"NOT_OBSERVED", "BLOCKING_FIELD"}
            and confirmation_state != "DECLARED_BY_USER"
        ):
            continue
        rule = field_rules.get(str(field_row.get("field", "")).strip())
        if not rule:
            continue
        seed = seed_for_cluster(rule["cluster"])
        confirmation_suffix = (
            " Declared input is present but still requires independent confirmation."
            if confirmation_state == "DECLARED_BY_USER"
            else ""
        )
        rows.append(
            {
                "missing_field": field_row.get("field"),
                "why_it_matters": f"{rule['why_it_matters']}{confirmation_suffix}",
                "decision_blocked": rule["decision_blocked"],
                "minimum_evidence_needed": seed.get("evidence_item") or rule["suggested_source"],
                "suggested_source": seed.get("source") or rule["suggested_source"],
                "related_cluster": rule["cluster"],
            }
        )
    return rows


def _build_routing_gap_evidence_register(
    routing_plan_compliance: dict[str, Any],
    source_routing_plan: dict[str, Any],
) -> list[dict[str, Any]]:
    missing_sources = list(routing_plan_compliance.get("mandatory_sources_missing_from_executor", []) or [])
    if not missing_sources:
        return []

    source_meta: dict[str, dict[str, Any]] = {}
    for group_key in ("mandatory_sources", "high_priority_sources", "optional_sources"):
        for row in source_routing_plan.get(group_key, []) or []:
            if isinstance(row, dict):
                source_key = str(row.get("source_key", "")).strip()
                if source_key:
                    source_meta[source_key] = row

    field_rules: dict[str, dict[str, str]] = {
        "nyc_dof_property_record": {
            "cluster": "identity_cluster",
            "why_it_matters": "The NYC DOF parcel record is the primary bounded-asset anchor for address, BBL, and parcel identity in NYC.",
            "decision_blocked": "asset identity confirmation, parcel-level routing, and any technical report class above blocked state.",
        },
        "nyc_pluto_property": {
            "cluster": "geometry_size_cluster",
            "why_it_matters": "PLUTO is the cleanest public route for official size, use, and vintage attributes in NYC.",
            "decision_blocked": "GFA-scale screening, benchmark routing, and regulated-floor-area interpretation.",
        },
        "nyc_ll84_energy_benchmarking": {
            "cluster": "fuel_energy_cluster",
            "why_it_matters": "LL84 is the canonical public energy baseline for covered NYC buildings and should not be substituted with generic benchmarks.",
            "decision_blocked": "asset-level EUI, emissions, and energy-performance screening.",
        },
        "nyc_ll97_covered_buildings_list": {
            "cluster": "regulatory_cluster",
            "why_it_matters": "The covered-buildings list is the public anchor for LL97 applicability and regulated-floor-area screening.",
            "decision_blocked": "covered-building applicability and compliance-pathway interpretation.",
        },
        "nyc_dob_permits": {
            "cluster": "systems_cluster",
            "why_it_matters": "DOB permit history is the primary public route for renovation chronology and systems clues in NYC.",
            "decision_blocked": "renovation chronology and system-clue advancement.",
        },
    }

    rows: list[dict[str, Any]] = []
    for source_key in missing_sources:
        meta = source_meta.get(source_key, {})
        rule = field_rules.get(
            source_key,
            {
                "cluster": "identity_cluster",
                "why_it_matters": "A mandatory public source from the routing plan did not execute, so the evidence map is incomplete.",
                "decision_blocked": "advancement beyond the current blocked or bounded report class.",
            },
        )
        source_name = str(meta.get("source_name", "") or source_key).strip()
        rows.append(
            {
                "missing_field": f"mandatory_source::{source_key}",
                "why_it_matters": rule["why_it_matters"],
                "decision_blocked": rule["decision_blocked"],
                "minimum_evidence_needed": f"Execute and preserve the mandatory routed source: {source_name}",
                "suggested_source": source_name,
                "related_cluster": rule["cluster"],
            }
        )
    return rows


class Motor012Adapter(BaseMotorAdapter):
    @property
    def motor_id(self) -> str:
        return "motor_012"

    @property
    def input_motor_ids(self) -> list[str]:
        return ["motor_008", "motor_004", "motor_005", "motor_007", "motor_011", "motor_028", "motor_001"]

    def _run_impl(self, inputs: dict[str, Any]) -> dict[str, Any]:
        pipeline = inputs.get("__pipeline__", {})
        fi = pipeline.get("facility_inputs", {})
        produced_at = datetime.now(timezone.utc).isoformat()

        m28 = inputs.get("motor_028", {})
        enriched = dict(m28.get("enriched_data", {}))
        quality_gate_passed = m28.get("quality_gate_passed", False)

        # P-DISCOVERY downstream: lee real_discovery_bundle de motor_028 y
        # construye un summary plano que se inyecta en facility_prior para
        # que TODOS los downstream motors lo consuman directamente.
        _rd_bundle = m28.get("real_discovery_bundle", {}) or {}
        _rd_results = _rd_bundle.get("results", {}) or {}

        def _rd_payload(src_key: str) -> dict:
            r = _rd_results.get(src_key) or {}
            return r.get("payload") or {} if r.get("status") == "ok" else {}

        _geo  = _rd_payload("census_geocoder")
        _clim = _rd_payload("noaa_climate")
        _epa  = _rd_payload("epa_envirofacts")
        _eia  = _rd_payload("eia_opendata")
        _osm  = _rd_payload("osm_overpass")
        _comp = _rd_payload("comparable_finder")

        real_discovery_summary: dict[str, Any] = {
            "available":               bool(_rd_bundle),
            "sufficient_for_pipeline": bool(_rd_bundle.get("sufficient_for_pipeline")),
            "ok_sources":              list(_rd_bundle.get("ok_sources", []) or []),
            # Geolocation
            "matched_address":         _geo.get("matched_address", ""),
            "lat":                     _geo.get("lat"),
            "lon":                     _geo.get("lon"),
            "county_name":             _geo.get("county_name", ""),
            "county_geoid":            _geo.get("county_geoid", ""),
            "tract_geoid":             _geo.get("tract_geoid", ""),
            "state_abbreviation":      _geo.get("state_abbreviation", ""),
            # Climate
            "ashrae_climate_zone":     _clim.get("ashrae_climate_zone_heuristic", ""),
            # Energy context
            "residential_price_cents_per_kwh": _eia.get("residential_price_cents_per_kwh"),
            "commercial_price_cents_per_kwh":  _eia.get("commercial_price_cents_per_kwh"),
            "industrial_price_cents_per_kwh":  _eia.get("industrial_price_cents_per_kwh"),
            # Neighbors / context
            "epa_facilities_in_zip_count":     _epa.get("facility_count_city"),
            "epa_estimated_local_industry":    list(_epa.get("estimated_local_industry", []) or [])[:8],
            "epa_naics_peers_in_state_count":  _epa.get("naics_peer_count"),
            "epa_naics_peers_in_state":        list(_epa.get("naics_peers_in_state", []) or [])[:10],
            "osm_industrial_neighbor_count":   _osm.get("industrial_count"),
            "osm_cold_storage_neighbor_count": _osm.get("cold_storage_count"),
            "osm_nearby_substation_count":     _osm.get("nearby_substation_count"),
            # Peers
            "comparable_peer_count":           _comp.get("best_peer_count"),
            "comparable_peer_candidates":      list(_comp.get("peer_candidates", []) or [])[:10],
        }
        routing_plan_compliance = dict(m28.get("routing_plan_compliance", {}) or {})
        source_routing_plan = dict(m28.get("source_routing_plan", {}) or {})
        enriched["coverage_gaps"] = _coverage_gap_types(m28, enriched)
        source_register = list(m28.get("source_register", []) or [])
        library_objects = inputs.get("motor_011", {}).get("library_objects", [])
        target_definition = inputs.get("motor_007", {}).get("target_definition_contract", {}) or derive_target_definition(pipeline)
        case_id = derive_effective_case_id(pipeline, target_definition)
        evidence_lineage = _build_evidence_lineage(case_id, produced_at, m28, enriched)
        asset_context_readiness = inputs.get("motor_007", {}).get("asset_context_readiness", "asset_context_insufficient")
        observable_cluster_register = inputs.get("motor_007", {}).get("observable_cluster_register", {})
        missing_physical_observables = inputs.get("motor_007", {}).get("missing_observable_clusters", [])
        fi_runtime = _inject_asset_discovery(fi, enriched)

        # Build all entity objects
        facility_entity = _build_facility_entity(fi_runtime)
        jurisdiction_entity = _build_jurisdiction_entity(fi_runtime, enriched)
        climate_entity = _build_climate_entity(fi_runtime)
        sector_archetype = _build_sector_archetype(fi_runtime, enriched)
        benchmark_context = _build_benchmark_context(fi_runtime, target_definition.get("target_type", "commercial_building"), enriched)
        energy_context = _build_energy_context(fi_runtime)
        regulatory_context = _build_regulatory_context(fi_runtime)
        org_capability = _build_org_capability_profile(fi_runtime, enriched)
        improvement_constraint = _build_improvement_constraint_profile(fi_runtime)
        compliance_applicability_case = _build_compliance_applicability_case(
            fi_runtime,
            regulatory_context,
            jurisdiction_entity,
            improvement_constraint,
            target_definition,
            enriched,
        )
        asset_identity_bundle = _build_asset_identity_bundle(
            target_definition,
            asset_context_readiness,
            observable_cluster_register,
            missing_physical_observables,
            fi_runtime,
        )
        operating_archetype_bundle = _build_operating_archetype_bundle(target_definition, fi_runtime)
        system_typology_prior = _build_system_typology_prior(target_definition, fi_runtime)
        asset_energy_behavior_prior = _build_asset_energy_behavior_prior(
            target_definition,
            benchmark_context,
            climate_entity,
            fi_runtime,
        )
        minimum_evidence_pack_seed = _build_minimum_evidence_pack_seed(
            target_definition,
            enriched,
            missing_physical_observables,
        )
        investment_uncertainty_map_seed = _build_investment_uncertainty_map_seed(
            minimum_evidence_pack_seed,
        )
        asset_context_readiness_table_seed = _build_asset_context_readiness_table_seed(
            asset_context_readiness,
            missing_physical_observables,
        )
        financial_boundary_seed = _build_financial_boundary_seed(
            enriched,
            asset_context_readiness,
        )
        regulatory_screening_seed = _build_regulatory_screening_seed(
            compliance_applicability_case,
        )
        asset_field_register = _build_asset_field_register(
            target_definition=target_definition,
            fi=fi_runtime,
            source_register=source_register,
            benchmark_context=benchmark_context,
            compliance_case=compliance_applicability_case,
            enriched=enriched,
        )
        declared_input_downgrade_register = build_declared_input_downgrade_register(
            asset_field_register,
        )
        canonical_asset_context_summary = _build_canonical_asset_context_summary(
            asset_field_register,
            asset_context_readiness,
        )
        missing_evidence_register = _build_missing_evidence_register(
            asset_field_register,
            minimum_evidence_pack_seed,
        )
        missing_evidence_register.extend(
            _build_routing_gap_evidence_register(
                routing_plan_compliance,
                source_routing_plan,
            )
        )

        # Derive asset name for labels
        asset_name = (
            target_definition.get("target_name")
            or pipeline.get("case_title")
            or fi_runtime.get("input_01_location", {}).get("address")
            or "the facility"
        )

        # Schedule info
        schedule = fi_runtime.get("input_07_operating_schedule", {})
        uses = [
            fi_runtime.get("input_04_primary_use", {}).get(f"use_{i}")
            for i in range(1, 6)
            if fi_runtime.get("input_04_primary_use", {}).get(f"use_{i}")
        ]
        ops_complexity = (
            "High — multi-use facility with 24/7 operational components drives elevated loads year-round."
            if len(uses) > 1 and schedule.get("24_7_components")
            else "Moderate — single-use facility with standard operational schedule."
            if len(uses) <= 1
            else "Moderate-High — multi-use operational profile."
        )

        # Build the 12 canonical entity objects
        entities = {
            "Facility": facility_entity,
            "Jurisdiction": jurisdiction_entity,
            "ClimateContext": climate_entity,
            "SectorArchetype": sector_archetype,
            "BenchmarkContext": benchmark_context,
            "EnergyContext": energy_context,
            "RegulatoryContext": regulatory_context,
            "AssetIdentity": asset_identity_bundle,
            "OperatingArchetype": operating_archetype_bundle,
            "SourceVersion": {
                "entity_type": "SourceVersion",
                "case_id": case_id,
                "produced_at": produced_at,
                "library_object_count": len(library_objects),
                "quality_gate_passed": quality_gate_passed,
                "source_registry_count": inputs.get("motor_008", {}).get("total_sources", 0),
                "data_provenance": "motor_008 + motor_011",
                "evidence_lineage_id": evidence_lineage["lineage_id"],
                "epistemic_status": "Decision-grade",
            },
            "SystemAsset": {
                "entity_type": "SystemAsset",
                "system_hypotheses": _build_system_asset_hypotheses(fi_runtime),
                "system_typology_prior": system_typology_prior,
                "data_provenance": "facility_inputs[input_09] + target_definition.target_type",
                "epistemic_status": "Decision-grade — plausible hypotheses, not verified site data",
            },
            "OperationalPractice": {
                "entity_type": "OperationalPractice",
                "office_schedule": schedule.get("office_schedule", ""),
                "observatory_schedule": schedule.get("observatory_schedule", ""),
                "peak_occupancy_note": schedule.get("peak_occupancy_note", ""),
                "hvac_schedule_note": schedule.get("hvac_schedule_note", ""),
                "declared_uses": uses,
                "extended_hours_components": schedule.get("24_7_components", []),
                "operations_complexity_signal": ops_complexity,
                "operating_archetype_bundle": operating_archetype_bundle,
                "data_provenance": "facility_inputs[input_07]",
                "epistemic_status": "Decision-grade",
            },
            "AssetEnergyBehaviorPrior": asset_energy_behavior_prior,
            "OrganizationCapability": org_capability,
            "ImprovementConstraint": improvement_constraint,
        }

        facility_prior = {
            "facility_prior_id": _prior_id(case_id),
            "case_id": case_id,
            "case_title": f"Asset Context Prior — {target_definition.get('target_label', asset_name)}",
            "asset_name": asset_name,
            "produced_at": produced_at,
            "produced_by_motor": "motor_012",
            "epistemic_grade": "Decision-grade",
            "target_definition": target_definition,
            "asset_context_readiness": asset_context_readiness,
            "canonical_asset_context_summary": canonical_asset_context_summary,
            "canonical_asset_context_state": canonical_asset_context_summary.get("canonical_asset_context_state", asset_context_readiness),
            "technical_prior_ceiling": asset_identity_bundle.get("technical_prior_ceiling"),
            "framework_constraint": (
                "This facility_prior is non-verificatory. It represents structured public context "
                "and plausible hypotheses. It does not constitute site truth, diagnosis, or verification."
            ),
            "entities": entities,
            "benchmark_bundle": entities["BenchmarkContext"],
            "jurisdiction_bundle": entities["Jurisdiction"],
            "regulatory_flag_bundle": entities["RegulatoryContext"],
            "compliance_applicability_case": compliance_applicability_case,
            "asset_identity_bundle": asset_identity_bundle,
            "asset_energy_behavior_prior": asset_energy_behavior_prior,
            "operating_archetype_bundle": operating_archetype_bundle,
            "system_typology_prior": system_typology_prior,
            "missing_physical_observables_register": missing_physical_observables,
            "minimum_evidence_pack_seed": minimum_evidence_pack_seed,
            "investment_uncertainty_map_seed": investment_uncertainty_map_seed,
            "asset_context_readiness_table_seed": asset_context_readiness_table_seed,
            "financial_boundary_seed": financial_boundary_seed,
            "regulatory_screening_seed": regulatory_screening_seed,
            "asset_field_register": asset_field_register,
            "field_admissibility_matrix": asset_field_register,
            "declared_input_downgrade_register": declared_input_downgrade_register,
            "canonical_supported_field_register": canonical_asset_context_summary.get("supported_field_register", []),
            "missing_evidence_register": missing_evidence_register,
            "dataset_coverage_register": list(m28.get("dataset_coverage_register", []) or enriched.get("dataset_coverage_register", []) or []),
            "routing_plan_compliance": routing_plan_compliance,
            "source_routing_plan": source_routing_plan,
            "system_asset_hypotheses": entities["SystemAsset"]["system_hypotheses"],
            "operational_tension_hypotheses": _build_operational_tensions(fi_runtime, enriched),
            "org_capability_profile": entities["OrganizationCapability"],
            "improvement_constraint_profile": entities["ImprovementConstraint"],
            "prior_assumptions_pack": _build_prior_assumptions_pack(fi_runtime, enriched),
            "uncertainty_markers": _build_uncertainty_markers(fi_runtime, enriched),
            "evidence_lineage": evidence_lineage,
            "input_count": len([k for k in fi_runtime if k.startswith("input_")]),
            "minimum_inputs_satisfied": len([k for k in fi_runtime if k.startswith("input_")]) >= 10,
            # P-DISCOVERY: real US-wide discovery data (Census/NOAA/EPA/EIA/OSM/peers)
            "real_discovery_summary": real_discovery_summary,
        }

        # V10 P3 — auto-attach regulatory applicability bundle for this
        # asset_family. Comes from regulatory_corpus/applicability/<family>.json
        # (built by applicability_mapper). Cero LLM, cero side-effects.
        # Phase 0 inscribed: este bundle es REFERENCIA citable, no decisión.
        try:
            from runtime_orchestrator.industry_corpus.evidence_wire import (
                regulatory_applicability_for as _reg_for,
            )
            _af = (target_definition or {}).get("target_type") or ""
            if _af:
                _regs = _reg_for(_af, max_entries=20)
                facility_prior["regulatory_applicability_bundle"] = {
                    "asset_family":  _af,
                    "regulations": [
                        {
                            "citation":             r.citation,
                            "title":                r.title,
                            "has_text_in_corpus":   r.has_text_in_corpus,
                            "regulation_source_id": r.regulation_source_id,
                            "mention_count":        r.mention_count_in_corpus,
                        }
                        for r in _regs
                    ],
                    "total":         len(_regs),
                    "with_fulltext": sum(1 for r in _regs if r.has_text_in_corpus),
                }
        except Exception:
            facility_prior["regulatory_applicability_bundle"] = {
                "asset_family": "", "regulations": [], "total": 0, "with_fulltext": 0,
            }

        return {
            "facility_prior": facility_prior,
            "facility_prior_id": facility_prior["facility_prior_id"],
            "evidence_lineage": evidence_lineage,
            "compliance_applicability_case": compliance_applicability_case,
            "minimum_evidence_pack_seed": minimum_evidence_pack_seed,
            "investment_uncertainty_map_seed": investment_uncertainty_map_seed,
            "asset_context_readiness_table_seed": asset_context_readiness_table_seed,
            "financial_boundary_seed": financial_boundary_seed,
            "regulatory_screening_seed": regulatory_screening_seed,
            "asset_field_register": asset_field_register,
            "field_admissibility_matrix": asset_field_register,
            "declared_input_downgrade_register": declared_input_downgrade_register,
            "canonical_asset_context_summary": canonical_asset_context_summary,
            "canonical_asset_context_state": canonical_asset_context_summary.get("canonical_asset_context_state", asset_context_readiness),
            "canonical_supported_field_register": canonical_asset_context_summary.get("supported_field_register", []),
            "missing_evidence_register": missing_evidence_register,
            "dataset_coverage_register": list(m28.get("dataset_coverage_register", []) or enriched.get("dataset_coverage_register", []) or []),
            "routing_plan_compliance": routing_plan_compliance,
            "source_routing_plan": source_routing_plan,
            "entity_count": len(entities),
            "tensions_count": len(facility_prior["operational_tension_hypotheses"]),
            "assumptions_count": len(facility_prior["prior_assumptions_pack"]),
            "uncertainty_markers_count": len(facility_prior["uncertainty_markers"]),
            "minimum_inputs_satisfied": facility_prior["minimum_inputs_satisfied"],
        }
