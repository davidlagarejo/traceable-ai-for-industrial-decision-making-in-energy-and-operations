from runtime_orchestrator.public_data_routing import (
    AssetType,
    DecisionType,
    JurisdictionClass,
    build_source_routing_plan,
    resolve_us_jurisdiction,
    route_for_asset_type,
    routing_keys_for_resolution,
    source_matrix_rows,
)


def _source_keys(entries):
    return [entry.source_key for entry in entries]


def test_resolve_us_jurisdiction_for_nyc_building_maps_coned_and_ll84_stack():
    resolution = resolve_us_jurisdiction(
        state="NY",
        city="NYC",
        asset_type=AssetType.COMMERCIAL_BUILDING,
    )
    assert resolution.utility_territory == "ConEdison"
    assert resolution.climate_zone_ashrae == "4A"
    assert resolution.jurisdiction_class == JurisdictionClass.HIGH_DATA_AVAILABILITY_BUILDING
    assert "NYC LL84 benchmarking" in resolution.regulatory_stack
    assert routing_keys_for_resolution(resolution, AssetType.COMMERCIAL_BUILDING) == ["US", "US-NY-NYC"]


def test_nyc_commercial_building_route_has_mandatory_local_datasets_and_disallows_cbecs_substitution():
    resolution = resolve_us_jurisdiction(
        state="NY",
        city="New York",
        asset_type=AssetType.COMMERCIAL_BUILDING,
    )
    plan = build_source_routing_plan(
        resolution,
        AssetType.COMMERCIAL_BUILDING,
        DecisionType.ACQUISITION_UNDERWRITING,
    )
    mandatory_keys = set(_source_keys(plan.mandatory_sources))
    assert {
        "nyc_dof_property_record",
        "nyc_pluto_property",
        "nyc_ll84_energy_benchmarking",
        "nyc_ll97_covered_buildings_list",
        "nyc_dob_permits",
    }.issubset(mandatory_keys)
    assert any("CBECS_EUI" in item for item in plan.disallowed_substitutions)


def test_target_identification_route_for_san_francisco_excludes_entity_finance_and_keeps_local_benchmarking():
    resolution = resolve_us_jurisdiction(
        state="CA",
        city="San Francisco",
        asset_type=AssetType.COMMERCIAL_BUILDING,
    )
    plan = build_source_routing_plan(
        resolution,
        AssetType.COMMERCIAL_BUILDING,
        DecisionType.TARGET_IDENTIFICATION,
    )
    mandatory_keys = set(_source_keys(plan.mandatory_sources))
    optional_keys = set(_source_keys(plan.optional_sources))
    high_priority_keys = set(_source_keys(plan.high_priority_sources))
    assert "city_benchmarking_san_francisco" in mandatory_keys
    assert "sf_assessor_property_record" in mandatory_keys
    assert "sec_edgar_company_filings" not in optional_keys | high_priority_keys | mandatory_keys


def test_los_angeles_route_keeps_real_local_permits_and_official_assessor_portal_context():
    resolution = resolve_us_jurisdiction(
        state="CA",
        city="Los Angeles",
        asset_type=AssetType.COMMERCIAL_BUILDING,
    )
    plan = build_source_routing_plan(
        resolution,
        AssetType.COMMERCIAL_BUILDING,
        DecisionType.TARGET_IDENTIFICATION,
    )
    mandatory_keys = set(_source_keys(plan.mandatory_sources))
    high_priority_keys = set(_source_keys(plan.high_priority_sources))
    assert "city_benchmarking_los_angeles" in mandatory_keys
    assert "la_building_permits" in high_priority_keys
    assert "la_county_assessor_portal_context" in high_priority_keys


def test_oakland_route_uses_property_portal_permit_context_and_pge_territory():
    resolution = resolve_us_jurisdiction(
        state="CA",
        city="Oakland",
        asset_type=AssetType.COMMERCIAL_BUILDING,
    )
    plan = build_source_routing_plan(
        resolution,
        AssetType.COMMERCIAL_BUILDING,
        DecisionType.TARGET_IDENTIFICATION,
    )
    mandatory_keys = set(_source_keys(plan.mandatory_sources))
    high_priority_keys = set(_source_keys(plan.high_priority_sources))
    assert resolution.utility_territory == "PG&E"
    assert resolution.jurisdiction_class == JurisdictionClass.UTILITY_AND_PERMIT_BUILDING
    assert routing_keys_for_resolution(resolution, AssetType.COMMERCIAL_BUILDING) == ["US", "US-CA", "US-CA-OAKLAND"]
    assert "alameda_county_property_search_portal" in mandatory_keys
    assert "oakland_building_permit_portal" in high_priority_keys
    assert "utility_pge_service_territory" in high_priority_keys


def test_houston_industrial_process_change_route_promotes_process_case_libraries_but_keeps_tceq_mandatory():
    resolution = resolve_us_jurisdiction(
        state="TX",
        city="Houston",
        asset_type=AssetType.INDUSTRIAL_FACILITY,
    )
    plan = build_source_routing_plan(
        resolution,
        AssetType.INDUSTRIAL_FACILITY,
        DecisionType.PROCESS_CHANGE,
    )
    mandatory_keys = set(_source_keys(plan.mandatory_sources))
    high_priority_keys = set(_source_keys(plan.high_priority_sources))
    assert "tceq_permits_and_emissions" in mandatory_keys
    assert "harris_county_appraisal_district_property_record" in mandatory_keys
    assert "state_environmental_agency_permits" in mandatory_keys
    assert "doe_iac_database" in high_priority_keys
    assert "openei_industrial_combustion" in high_priority_keys
    assert "harris_cad_property_search_portal" in high_priority_keys
    assert "houston_permit_portal_context" in high_priority_keys


def test_dallas_data_center_route_uses_dallas_portal_and_oncor_context():
    resolution = resolve_us_jurisdiction(
        state="TX",
        city="Dallas",
        asset_type=AssetType.DATA_CENTER,
    )
    plan = build_source_routing_plan(
        resolution,
        AssetType.DATA_CENTER,
        DecisionType.RETROFIT_CAPEX,
    )
    mandatory_keys = set(_source_keys(plan.mandatory_sources))
    high_priority_keys = set(_source_keys(plan.high_priority_sources))
    assert resolution.utility_territory == "Oncor_or_ERCOT"
    assert routing_keys_for_resolution(resolution, AssetType.DATA_CENTER) == ["US", "US-TX", "US-TX-DALLAS"]
    assert "dallas_cad_property_search_portal" in mandatory_keys
    assert "dallas_building_permit_portal" in high_priority_keys
    assert "utility_oncor_service_territory" in high_priority_keys


def test_temple_industrial_route_adds_bell_cad_and_temple_records_context():
    resolution = resolve_us_jurisdiction(
        state="TX",
        city="Temple",
        asset_type=AssetType.INDUSTRIAL_FACILITY,
    )
    plan = build_source_routing_plan(
        resolution,
        AssetType.INDUSTRIAL_FACILITY,
        DecisionType.PROCESS_CHANGE,
    )
    mandatory_keys = set(_source_keys(plan.mandatory_sources))
    high_priority_keys = set(_source_keys(plan.high_priority_sources))
    assert resolution.county == "Bell County"
    assert routing_keys_for_resolution(resolution, AssetType.INDUSTRIAL_FACILITY) == ["US", "US-TX", "US-TX-TEMPLE", "US-INDUSTRIAL"]
    assert "bell_cad_property_search_portal" in mandatory_keys
    assert "temple_permit_records_context" in high_priority_keys
    assert "tceq_permits_and_emissions" in mandatory_keys


def test_san_diego_industrial_route_adds_regional_air_district_context():
    resolution = resolve_us_jurisdiction(
        state="CA",
        city="San Diego",
        asset_type=AssetType.INDUSTRIAL_FACILITY,
    )
    plan = build_source_routing_plan(
        resolution,
        AssetType.INDUSTRIAL_FACILITY,
        DecisionType.PROCESS_CHANGE,
    )
    high_priority_keys = set(_source_keys(plan.high_priority_sources))
    mandatory_keys = set(_source_keys(plan.mandatory_sources))
    assert resolution.utility_territory == "SDG&E"
    assert "ca_carb_facility_emissions" in mandatory_keys
    assert "ca_state_environmental_permits" in mandatory_keys
    assert "sdapcd_permit_portal_context" in high_priority_keys


def test_asset_type_router_for_data_center_emphasizes_power_and_cooling():
    route = route_for_asset_type(AssetType.DATA_CENTER)
    assert route is not None
    assert route.route_name == "power_cooling_and_uptime_context_first"
    assert "critical_load_anchor" in route.critical_field_family
    assert "cooling_or_redundancy_clue" in route.critical_field_family


def test_source_matrix_rows_include_nyc_california_and_texas_layers():
    rows = source_matrix_rows()
    keys = {(row["jurisdiction"], row["source_key"]) for row in rows}
    assert ("US-NY-NYC", "nyc_ll84_energy_benchmarking") in keys
    assert ("US-CA-SF", "city_benchmarking_san_francisco") in keys
    assert ("US-CA-LA", "la_county_assessor_portal_context") in keys
    assert ("US-CA-OAKLAND", "alameda_county_property_search_portal") in keys
    assert ("US-TX", "tceq_permits_and_emissions") in keys
    assert ("US-TX-HOUSTON", "harris_cad_property_search_portal") in keys
    assert ("US-TX-TEMPLE", "bell_cad_property_search_portal") in keys
    assert ("US-TX-DALLAS", "utility_oncor_service_territory") in keys
