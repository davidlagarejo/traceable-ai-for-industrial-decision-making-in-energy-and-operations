from __future__ import annotations

from runtime_orchestrator.adapters import motor_012 as motor_012_module
from runtime_orchestrator.adapters import motor_028 as motor_028_module


def _sf_ctx() -> dict:
    return {
        "address": "980 HOWARD STREET, SAN FRANCISCO, CA 94103",
        "asset_name": "980 Howard Street",
        "target_label": "980 Howard Street",
        "city": "SAN FRANCISCO",
        "state_code": "CA",
        "zip_code": "94103",
        "parcel_id": "",
        "property_id": "",
    }


def _la_ctx() -> dict:
    return {
        "address": "111 SOUTH GRAND AVENUE, LOS ANGELES, CA 90012",
        "asset_name": "111 South Grand Avenue",
        "target_label": "111 South Grand Avenue",
        "city": "LOS ANGELES",
        "state_code": "CA",
        "zip_code": "90012",
        "parcel_id": "",
        "property_id": "",
    }


def _tx_ctx() -> dict:
    return {
        "address": "5900 HIGHWAY 225, DEER PARK, TX 77536",
        "asset_name": "Deer Park Industrial Site",
        "target_label": "Deer Park Industrial Site",
        "city": "DEER PARK",
        "state_code": "TX",
        "zip_code": "77536",
    }


def _oak_ctx() -> dict:
    return {
        "address": "195 5TH STREET, OAKLAND, CA 94607",
        "asset_name": "195 5th Street",
        "target_label": "195 5th Street",
        "city": "OAKLAND",
        "state_code": "CA",
        "zip_code": "94607",
    }


def _sd_ctx() -> dict:
    return {
        "address": "600 B STREET, SAN DIEGO, CA 92101",
        "asset_name": "600 B Street",
        "target_label": "600 B Street",
        "city": "SAN DIEGO",
        "state_code": "CA",
        "zip_code": "92101",
    }


def _austin_ctx() -> dict:
    return {
        "address": "500 E 4TH STREET, AUSTIN, TX 78701",
        "asset_name": "500 E 4th Street",
        "target_label": "500 E 4th Street",
        "city": "AUSTIN",
        "state_code": "TX",
        "zip_code": "78701",
    }


def _dallas_ctx() -> dict:
    return {
        "address": "2001 ROSS AVENUE, DALLAS, TX 75201",
        "asset_name": "2001 Ross Avenue",
        "target_label": "2001 Ross Avenue",
        "city": "DALLAS",
        "state_code": "TX",
        "zip_code": "75201",
    }


def _temple_ctx() -> dict:
    return {
        "address": "10501 N HK DODGEN LOOP, TEMPLE, TX 76504",
        "asset_name": "Wilsonart Temple North Laminate Facility",
        "target_label": "Wilsonart Temple North Laminate Facility",
        "city": "TEMPLE",
        "state_code": "TX",
        "zip_code": "76504",
    }


def test_fetch_sf_benchmarking_uses_current_dataset_and_matches_address(monkeypatch):
    seen_urls: list[str] = []

    def fake_fetch_json(url, params=None, headers=None, timeout=30):
        seen_urls.append(url)
        if "96ck-qcfe" in url and params and "$q" in params:
            return [
                {
                    "building_address": "980 HOWARD STREET",
                    "building_name": "980 Howard Street",
                    "benchmark_year": "2024",
                    "site_eui": "82.1",
                    "energy_star_score": "88",
                    "floor_area": "550000",
                    "parcel_number": "3701032",
                }
            ]
        return []

    monkeypatch.setattr(motor_028_module, "_fetch_json", fake_fetch_json)
    payload = motor_028_module._fetch_sf_benchmarking(_sf_ctx())
    assert payload is not None
    assert payload["records"][0]["site_eui"] == "82.1"
    assert payload["source_dataset"] == "sf_benchmarking_96ck-qcfe"
    assert any("96ck-qcfe" in url for url in seen_urls)


def test_fetch_la_benchmarking_uses_current_ebewe_dataset(monkeypatch):
    seen_urls: list[str] = []

    def fake_fetch_json(url, params=None, headers=None, timeout=30):
        seen_urls.append(url)
        if "9yda-i4ya" in url and params and "$q" in params:
            return [
                {
                    "building_address": "111 SOUTH GRAND AVENUE",
                    "program_year": "2024",
                    "weather_normalized_3": "74.3",
                    "energy_star_score": "79",
                    "apn": "5149021901",
                    "building_id": "LA-123",
                }
            ]
        return []

    monkeypatch.setattr(motor_028_module, "_fetch_json", fake_fetch_json)
    payload = motor_028_module._fetch_la_benchmarking(_la_ctx())
    assert payload is not None
    assert payload["records"][0]["weather_normalized_3"] == "74.3"
    assert payload["source_dataset"] == "la_ebewe_9yda-i4ya"
    assert any("9yda-i4ya" in url for url in seen_urls)


def test_fetch_la_building_permits_uses_current_official_dataset(monkeypatch):
    seen_urls: list[str] = []

    def fake_fetch_json(url, params=None, headers=None, timeout=30):
        seen_urls.append(url)
        if "pi9x-tg5x" in url and params and "$q" in params:
            return [
                {
                    "primary_address": "111 S GRAND AVE",
                    "zip_code": "90012",
                    "permit_nbr": "24016-10000-12345",
                    "issue_date": "2026-03-20T00:00:00.000",
                    "permit_type": "Bldg-Alter/Repair",
                }
            ]
        return []

    monkeypatch.setattr(motor_028_module, "_fetch_json", fake_fetch_json)
    payload = motor_028_module._fetch_la_building_permits(_la_ctx())
    assert payload is not None
    assert payload["records"][0]["permit_nbr"] == "24016-10000-12345"
    assert payload["source_dataset"] == "la_building_permits_pi9x-tg5x"
    assert any("pi9x-tg5x" in url for url in seen_urls)


def test_fetch_la_county_assessor_property_record_uses_public_search_and_detail_api(monkeypatch):
    seen_calls: list[tuple[str, dict | None]] = []

    def fake_fetch_json(url, params=None, headers=None, timeout=30):
        seen_calls.append((url, params))
        if "portal.assessor.lacounty.gov/api/search" in url:
            return {
                "TotalCount": 2,
                "Parcels": [
                    {
                        "AIN": "5151004903",
                        "SitusStreet": "111 S GRAND AVE",
                        "SitusCity": "LOS ANGELES",
                        "SitusZipCode": "90012",
                        "LegalDescription": "TR 1234 LOT 1",
                    },
                    {
                        "AIN": "5151004907",
                        "SitusStreet": "200 N MAIN ST",
                        "SitusCity": "LOS ANGELES",
                        "SitusZipCode": "90012",
                        "LegalDescription": "TR 9999 LOT 2",
                    },
                ],
            }
        if "portal.assessor.lacounty.gov/api/parceldetail" in url and params and params.get("ain") == "5151004903":
            return {
                "Parcel": {
                    "AIN": "5151004903",
                    "SitusStreet": "111 S GRAND AVE",
                    "SitusCity": "LOS ANGELES",
                    "SitusZipCode": "90012",
                    "SqftMain": "1440000",
                    "SqftLot": "110000",
                    "YearBuilt": "1990",
                }
            }
        return {}

    monkeypatch.setattr(motor_028_module, "_fetch_json", fake_fetch_json)
    payload = motor_028_module._fetch_la_county_assessor_property_record(_la_ctx())
    assert payload is not None
    assert payload["source_dataset"] == "la_county_assessor_api"
    assert payload["selected_row"]["AIN"] == "5151004903"
    assert payload["parcel_detail"]["SqftMain"] == "1440000"
    assert payload["query_context"]["match_basis"] == "search_match"
    assert any("api/search" in url for url, _ in seen_calls)
    assert any("api/parceldetail" in url for url, _ in seen_calls)


def test_build_source_family_coverage_table_tracks_nyc_query_and_found_status():
    rows = motor_028_module._build_source_family_coverage_table(
        {
            "mandatory_sources": [
                {
                    "source_key": "nyc_pluto_property",
                    "source_name": "NYC PLUTO",
                    "authority": "high",
                    "fields": ["GFA", "year_built"],
                },
                {
                    "source_key": "nyc_ll84_energy_benchmarking",
                    "source_name": "NYC LL84",
                    "authority": "high",
                    "fields": ["EUI", "emissions"],
                },
            ],
            "high_priority_sources": [],
            "optional_sources": [],
        },
        [
            {
                "source_type": "nyc_pluto_property",
                "status": "found",
                "source_scope": "asset_level",
                "authority_score": "high",
            },
            {
                "source_type": "nyc_ll84_energy_benchmarking",
                "status": "no_data",
                "source_scope": "asset_level",
                "authority_score": "high",
            },
        ],
    )
    by_family = {row["source_family"]: row for row in rows}
    assert by_family["nyc_pluto_property"]["queried"] is True
    assert by_family["nyc_pluto_property"]["found"] is True
    assert by_family["nyc_pluto_property"]["fields_expected"] == ["GFA", "year_built"]
    assert by_family["nyc_ll84_energy_benchmarking"]["queried"] is True
    assert by_family["nyc_ll84_energy_benchmarking"]["found"] is False
    assert by_family["nyc_ll84_energy_benchmarking"]["missing"] == ["EUI", "emissions"]


def test_build_source_family_coverage_table_tracks_texas_manufacturing_route():
    rows = motor_028_module._build_source_family_coverage_table(
        {
            "mandatory_sources": [
                {
                    "source_key": "tceq_permits_and_emissions",
                    "source_name": "TCEQ permits and emissions",
                    "authority": "high",
                    "fields": ["emissions", "permits"],
                },
                {
                    "source_key": "county_appraisal_district_property_record",
                    "source_name": "County appraisal district",
                    "authority": "high",
                    "fields": ["address", "site_area"],
                },
            ],
            "high_priority_sources": [],
            "optional_sources": [],
        },
        [
            {
                "source_type": "tceq_permits_and_emissions",
                "status": "found",
                "source_scope": "jurisdiction_level",
                "authority_score": "high",
            }
        ],
    )
    by_family = {row["source_family"]: row for row in rows}
    assert by_family["tceq_permits_and_emissions"]["found"] is True
    assert by_family["tceq_permits_and_emissions"]["scope"] == "JURISDICTION_LEVEL"
    assert by_family["county_appraisal_district_property_record"]["queried"] is False
    assert by_family["county_appraisal_district_property_record"]["support_note"].startswith("Source required by routing plan")


def test_build_source_family_coverage_table_carries_public_page_acquisition_metadata():
    rows = motor_028_module._build_source_family_coverage_table(
        {
            "mandatory_sources": [
                {
                    "source_key": "dallas_building_permit_portal",
                    "source_name": "Dallas permit portal",
                    "authority": "high",
                    "fields": ["permit_types", "systems_clues"],
                }
            ],
            "high_priority_sources": [],
            "optional_sources": [],
        },
        [
            {
                "source_type": "dallas_building_permit_portal",
                "status": "found",
                "source_scope": "jurisdiction_level",
                "authority_score": "high",
                "acquisition_mode": "playwright_public_page",
            }
        ],
        {
            "dallas_building_permit_portal": {
                "source_dataset": "dallas_building_permit_portal",
                "public_page_acquisition": {
                    "selected_mode": "playwright_public_page",
                    "static_probe": {"status": "success", "render_mode": "shell_or_sparse"},
                    "browser_attempt": {"status": "success"},
                },
            }
        },
    )
    row = rows[0]
    assert row["selected_acquisition_mode"] == "playwright_public_page"
    assert row["static_probe_attempted"] is True
    assert row["static_usable"] is False
    assert row["browser_attempted"] is True
    assert row["browser_success"] is True
    assert row["browser_justified"] is True


def test_fetch_sf_building_permits_uses_official_dataset(monkeypatch):
    seen_urls: list[str] = []

    def fake_fetch_json(url, params=None, headers=None, timeout=30):
        seen_urls.append(url)
        if "gnti-6wm5" in url and params and "$q" in params:
            return [
                {
                    "job_address": "980 HOWARD ST",
                    "filed_date": "2025-10-15T00:00:00.000",
                    "permit_number": "202510150001",
                    "permit_type": "ALTERATION",
                }
            ]
        return []

    monkeypatch.setattr(motor_028_module, "_fetch_json", fake_fetch_json)
    payload = motor_028_module._fetch_sf_building_permits(_sf_ctx())
    assert payload is not None
    assert payload["records"][0]["permit_number"] == "202510150001"
    assert payload["source_dataset"] == "sf_building_permits_gnti-6wm5"
    assert any("gnti-6wm5" in url for url in seen_urls)


def test_fetch_ca_guidance_and_utility_context_are_bounded_official_sources():
    cec = motor_028_module._fetch_ca_cec_benchmarking_guidance(_sf_ctx())
    title24 = motor_028_module._fetch_ca_title24_guidance(_sf_ctx())
    calgreen = motor_028_module._fetch_ca_calgreen_guidance(_sf_ctx())
    pge = motor_028_module._fetch_utility_pge_service_territory(_sf_ctx())
    assert cec is not None
    assert cec["source_dataset"] == "ca_cec_benchmarking_guidance"
    assert title24 is not None
    assert title24["applicable_rule_family"] == "California Title 24 energy code"
    assert calgreen is not None
    assert calgreen["green_building_rule_family"] == "CALGreen"
    assert pge is not None
    assert pge["utility_territory"] == "PG&E"


def test_fetch_ca_industrial_context_sources_are_official_but_not_asset_level():
    ctx = {
        "address": "841 CHEVRON WAY, RICHMOND, CA 94801",
        "asset_name": "Richmond Industrial Facility",
        "target_label": "Richmond Industrial Facility",
        "city": "RICHMOND",
        "state_code": "CA",
        "zip_code": "94801",
        "target_type": "industrial_facility",
    }
    carb = motor_028_module._fetch_ca_carb_facility_emissions(ctx)
    permits = motor_028_module._fetch_ca_state_environmental_permits(ctx)
    assert carb is not None
    assert permits is not None
    assert carb["scope"] == "JURISDICTION_LEVEL"
    assert permits["scope"] == "JURISDICTION_LEVEL"
    assert "CARB" in carb["title"]
    assert "CalEPA" in permits["title"]
    assert carb["regional_air_district"] == "BAAQMD"
    assert permits["regional_air_district"] == "BAAQMD"


def test_fetch_expanded_california_portal_and_utility_context_sources_are_bounded():
    oakland_property = motor_028_module._fetch_alameda_county_property_search_portal(_oak_ctx())
    oakland_permits = motor_028_module._fetch_oakland_building_permit_portal(_oak_ctx())
    san_diego_property = motor_028_module._fetch_san_diego_county_property_search_portal(_sd_ctx())
    sdge = motor_028_module._fetch_utility_sdge_service_territory(_sd_ctx())
    la_assessor = motor_028_module._fetch_la_county_assessor_portal_context(_la_ctx())
    assert oakland_property is not None
    assert oakland_property["source_dataset"] == "alameda_county_property_search_portal"
    assert oakland_property["scope"] == "JURISDICTION_LEVEL"
    assert la_assessor is not None
    assert la_assessor["property_search_portal"] == "Los Angeles County Assessor portal observed"
    assert oakland_permits is not None
    assert oakland_permits["permit_portal_context"] == "Oakland permit portal observed"
    assert san_diego_property is not None
    assert san_diego_property["property_search_portal"] == "San Diego County property-search portal observed"
    assert sdge is not None
    assert sdge["utility_territory"] == "SDG&E"


def test_fetch_expanded_texas_portal_and_utility_context_sources_are_bounded(monkeypatch):
    def fake_fetch_json(url, params=None, headers=None, timeout=30):
        if "actions/hcad-pdata/default/get-tax-years" in url:
            return [{"taxyears": "2026"}, {"taxyears": "2025"}]
        if "actions/hcad-pdata/default/get-property-downloads" in url:
            return [
                {
                    "downloadLinkText": "Real Property Data",
                    "downloadLink": "https://download.hcad.org/data/CAMA/2026/Real_acct_owner.zip",
                    "filename": "Real_acct_owner.zip",
                }
            ]
        return []

    monkeypatch.setattr(motor_028_module, "_fetch_json", fake_fetch_json)
    travis = motor_028_module._fetch_travis_cad_property_search_portal(_austin_ctx())
    austin_permits = motor_028_module._fetch_austin_building_permit_portal(_austin_ctx())
    austin_utility = motor_028_module._fetch_utility_austin_energy_service_territory(_austin_ctx())
    dallas_cad = motor_028_module._fetch_dallas_cad_property_search_portal(_dallas_ctx())
    dallas_permits = motor_028_module._fetch_dallas_building_permit_portal(_dallas_ctx())
    oncor = motor_028_module._fetch_utility_oncor_service_territory(_dallas_ctx())
    bell = motor_028_module._fetch_bell_cad_property_search_portal(_temple_ctx())
    temple_records = motor_028_module._fetch_temple_permit_records_context(_temple_ctx())
    hcad = motor_028_module._fetch_harris_cad_property_search_portal(
        {
            "address": "700 LOUISIANA STREET, HOUSTON, TX 77002",
            "asset_name": "700 Louisiana Street",
            "target_label": "700 Louisiana Street",
            "city": "HOUSTON",
            "state_code": "TX",
            "zip_code": "77002",
        }
    )
    hpc = motor_028_module._fetch_houston_permit_portal_context(
        {
            "address": "700 LOUISIANA STREET, HOUSTON, TX 77002",
            "asset_name": "700 Louisiana Street",
            "target_label": "700 Louisiana Street",
            "city": "HOUSTON",
            "state_code": "TX",
            "zip_code": "77002",
        }
    )
    assert travis is not None
    assert travis["property_search_portal"] == "Travis CAD property-search portal observed"
    assert austin_permits is not None
    assert austin_permits["permit_portal_context"] == "Austin permit portal observed"
    assert austin_utility is not None
    assert austin_utility["utility_territory"] == "Austin_Energy_or_ERCOT"
    assert dallas_cad is not None
    assert dallas_cad["property_search_portal"] == "Dallas CAD property-search portal observed"
    assert dallas_permits is not None
    assert dallas_permits["permit_portal_context"] == "Dallas permit portal observed"
    assert oncor is not None
    assert oncor["utility_territory"] == "Oncor_or_ERCOT"
    assert bell is not None
    assert bell["property_search_portal"] == "Bell CAD property-search portal observed"
    assert temple_records is not None
    assert temple_records["permit_records_context"] == "Temple records and permit-routing context observed"
    assert hcad is not None
    assert hcad["property_search_portal"] == "HCAD property-search portal observed"
    assert hcad["public_data_channel"] == "HCAD public property data downloads observed"
    assert hcad["latest_available_tax_year"] == "2026"
    assert hcad["real_property_downloads"][0]["filename"] == "Real_acct_owner.zip"
    assert hpc is not None
    assert hpc["permit_portal_context"] == "Houston permit portal observed"


def test_routing_context_guard_rejects_mismatched_city_payload():
    attempts = [
        {
            "source_type": "city_benchmarking_san_francisco",
            "source_scope": "asset_jurisdiction_specific",
            "source_family": "benchmarking_disclosure_record",
            "authority_score": "high",
            "round_id": "round_3_energy_utility_compliance",
            "status": "found",
            "accepted": True,
            "locator": "data.sfgov.org:benchmarking",
        }
    ]
    contamination_log: list[dict] = []
    discarded: list[dict] = []
    benchmark_data = {
        "records": [
            {
                "building_address": "123 TEST ST",
                "city": "Oakland",
                "state": "CA",
                "site_eui": "70.0",
            }
        ]
    }
    result = motor_028_module._apply_routing_context_guard(
        ctx=_sf_ctx(),
        source_routing_plan={"mandatory_sources": [{"source_key": "city_benchmarking_san_francisco"}]},
        attempts=attempts,
        extended_data={},
        selected_extended_registry=[],
        benchmark_route={"source_type": "city_benchmarking_san_francisco"},
        benchmark_data=benchmark_data,
        contamination_log=contamination_log,
        discarded_source_log=discarded,
    )
    assert result is None
    assert attempts[0]["accepted"] is False
    assert attempts[0]["rejection_reason"] == "context_contamination_risk"
    assert contamination_log[0]["detected_issue"] == "source_city_mismatch"


def test_fetch_tceq_and_ghgrp_match_industrial_context_from_curated_rows(monkeypatch):
    monkeypatch.setattr(
        motor_028_module,
        "_load_tceq_point_source_rows",
        lambda url=motor_028_module._TCEQ_POINT_SOURCE_XLSX_URL: (
            [
                {
                    "SITE": "DEER PARK INDUSTRIAL SITE",
                    "COMPANY": "EXAMPLE CHEMICAL CO",
                    "NEAR CITY": "DEER PARK",
                    "LOCATION": "5900 HIGHWAY 225",
                    "ZIP": "77536",
                    "CO TPY": 11.2,
                    "VOC TPY": 5.7,
                }
            ],
            "2024",
        ),
    )
    monkeypatch.setattr(
        motor_028_module,
        "_load_epa_ghgrp_summary_rows",
        lambda: (
            [
                {
                    "Facility Name": "DEER PARK INDUSTRIAL SITE",
                    "Address": "5900 HIGHWAY 225",
                    "City": "DEER PARK",
                    "State": "TEXAS",
                    "Zip Code": "77536",
                    "Total reported direct emissions": 120345.6,
                }
            ],
            "2023",
        ),
    )

    tceq_payload = motor_028_module._fetch_tceq_permits_and_emissions(_tx_ctx())
    ghgrp_payload = motor_028_module._fetch_epa_ghgrp_facilities(_tx_ctx())
    assert tceq_payload is not None
    assert tceq_payload["records"][0]["SITE"] == "DEER PARK INDUSTRIAL SITE"
    assert tceq_payload["reporting_year"] == "2024"
    assert ghgrp_payload is not None
    assert ghgrp_payload["records"][0]["Total reported direct emissions"] == 120345.6
    assert ghgrp_payload["reporting_year"] == "2023"


def test_build_benchmark_context_promotes_sf_local_disclosure():
    fi = {
        "input_01_location": {"city": "SAN FRANCISCO", "climate_zone_ASHRAE": "3C"},
        "input_05_size": {"GFA_sqft": 550000},
    }
    context = motor_012_module._build_benchmark_context(
        fi,
        "commercial_building",
        {
            "benchmark_routing_register": {"selected_source_type": "city_benchmarking_san_francisco"},
            "asset_energy_behavior_reference": {
                "records": [
                    {
                        "building_address": "980 HOWARD STREET",
                        "benchmark_year": "2024",
                        "site_eui": "82.1",
                        "energy_star_score": "88",
                        "floor_area": "550000",
                        "parcel_number": "3701032",
                    }
                ]
            },
        },
    )
    assert context["benchmark_source"] == "San Francisco public benchmarking disclosure"
    assert context["benchmark_source_scope"] == "ASSET_LEVEL"
    assert context["adjusted_EUI_estimate_kBtu_sqft"] == 82.1
    assert context["local_property_id"] == "3701032"


def test_build_asset_field_register_promotes_industrial_emissions_from_ghgrp():
    benchmark_context = {
        "benchmark_source": "EIA MECS sector benchmark",
        "benchmark_source_scope": "BENCHMARK_LEVEL",
        "benchmark_authority_score": "medium",
    }
    source_register = [
        {
            "source_id": "epa_ghgrp_emitters::deer-park",
            "url": "epa.gov:ghgrp:state=TX",
            "title": "epa_ghgrp_emitters",
            "authority_score": "high",
            "scope": "ASSET_LEVEL",
            "recency": "current",
            "accepted": True,
            "rejection_reason": "",
            "source_family": "regulatory_coverage_record",
        }
    ]
    rows = motor_012_module._build_asset_field_register(
        target_definition={
            "target_name": "Deer Park Industrial Site",
            "target_type": "industrial_facility",
            "address_raw": "5900 HIGHWAY 225, DEER PARK, TX 77536",
            "owner_entity": "Example Chemical Co",
        },
        fi={
            "input_01_location": {"address": "5900 HIGHWAY 225, DEER PARK, TX 77536", "city": "DEER PARK"},
            "input_02_facility_type": {},
            "input_03_sector": {},
            "input_04_primary_use": {"uses": ["industrial_process"]},
            "input_05_size": {},
            "input_06_vintage": {},
            "input_07_operating_schedule": {},
            "input_08_energy_fuel": {"primary_fuel": "natural_gas"},
            "input_09_known_systems": {},
        },
        source_register=source_register,
        benchmark_context=benchmark_context,
        compliance_case={},
        enriched={
            "extended_sources": {
                "epa_ghgrp_facilities": {
                    "records": [
                        {
                            "Facility Name": "DEER PARK INDUSTRIAL SITE",
                            "Address": "5900 HIGHWAY 225",
                            "City": "DEER PARK",
                            "State": "TEXAS",
                            "Zip Code": "77536",
                            "Total reported direct emissions": 120345.6,
                        }
                    ]
                }
            }
        },
    )
    emissions_row = next(row for row in rows if row["field"] == "emissions")
    assert emissions_row["value"] == "120345.6"
    assert emissions_row["admissibility"] == "CONFIRMED_ASSET_LEVEL"


def test_build_asset_field_register_promotes_tceq_permit_and_criteria_emissions_for_manufacturing():
    source_register = [
        {
            "source_id": "tceq_permits_and_emissions::wilsonart",
            "url": "tceq.texas.gov:point_source:city=TEMPLE",
            "title": "tceq_permits_and_emissions",
            "authority_score": "high",
            "scope": "ASSET_LEVEL",
            "recency": "current",
            "accepted": True,
            "rejection_reason": "",
            "source_family": "environmental_permit_record",
        }
    ]
    rows = motor_012_module._build_asset_field_register(
        target_definition={
            "target_name": "Wilsonart Temple North Laminate Facility",
            "target_type": "manufacturing_facility",
            "address_raw": "10501 N HK DODGEN LOOP, TEMPLE, TX",
            "owner_entity": "Wilsonart LLC",
        },
        fi={
            "input_01_location": {"address": "10501 N HK DODGEN LOOP, TEMPLE, TX", "city": "TEMPLE"},
            "input_02_facility_type": {},
            "input_03_sector": {},
            "input_04_primary_use": {"uses": ["laminate_manufacturing"]},
            "input_05_size": {},
            "input_06_vintage": {},
            "input_07_operating_schedule": {},
            "input_08_energy_fuel": {},
            "input_09_known_systems": {},
        },
        source_register=source_register,
        benchmark_context={},
        compliance_case={},
        enriched={
            "extended_sources": {
                "tceq_permits_and_emissions": {
                    "records": [
                        {
                            "RN": "RN100215631",
                            "ACCOUNT": "BF0110G",
                            "COMPANY": "WILSONART LLC",
                            "SITE": "TEMPLE NORTH LAMINATE FACILITY",
                            "LOCATION": "10501 N HK DODGEN LOOP",
                            "NEAR CITY": "TEMPLE",
                            "REPORTING YEAR": 2024,
                            "CO TPY": 44.3725,
                            "NOX TPY": 57.7712,
                            "SO2 TPY": 0.8309,
                            "VOC TPY": 49.3128,
                        }
                    ]
                }
            }
        },
    )
    emissions_row = next(row for row in rows if row["field"] == "emissions")
    permits_row = next(row for row in rows if row["field"] == "permits")
    filings_row = next(row for row in rows if row["field"] == "compliance_filings")
    assert emissions_row["admissibility"] == "CONFIRMED_ASSET_LEVEL"
    assert "NOx 57.7712 tpy" in emissions_row["value"]
    assert permits_row["admissibility"] == "CONFIRMED_ASSET_LEVEL"
    assert "RN RN100215631" in permits_row["value"]
    assert filings_row["admissibility"] == "CONFIRMED_ASSET_LEVEL"
    assert "TCEQ point-source permit / emissions registry observed" in filings_row["value"]


def test_build_asset_field_register_promotes_la_assessor_area_and_year_built():
    source_register = [
        {
            "source_id": "la_county_assessor_property_record::ain=5151004903",
            "url": "la_county_assessor_api:ain=5151004903",
            "title": "la_county_assessor_property_record",
            "authority_score": "high",
            "scope": "ASSET_LEVEL",
            "recency": "current",
            "accepted": True,
            "rejection_reason": "",
            "source_family": "building_record",
        }
    ]
    rows = motor_012_module._build_asset_field_register(
        target_definition={
            "target_name": "111 South Grand Avenue",
            "target_type": "commercial_building",
            "address_raw": "111 SOUTH GRAND AVENUE, LOS ANGELES, CA 90012",
            "owner_entity": "Example Owner LLC",
        },
        fi={
            "input_01_location": {"address": "111 SOUTH GRAND AVENUE, LOS ANGELES, CA 90012", "city": "LOS ANGELES"},
            "input_02_facility_type": {},
            "input_03_sector": {},
            "input_04_primary_use": {"uses": ["office"]},
            "input_05_size": {},
            "input_06_vintage": {},
            "input_07_operating_schedule": {},
            "input_08_energy_fuel": {},
            "input_09_known_systems": {},
        },
        source_register=source_register,
        benchmark_context={},
        compliance_case={},
        enriched={
            "extended_sources": {
                "la_county_assessor_property_record": {
                    "selected_row": {"AIN": "5151004903"},
                    "parcel_detail": {
                        "AIN": "5151004903",
                        "SqftMain": "1440000",
                        "SqftLot": "110000",
                        "YearBuilt": "1990",
                    },
                }
            }
        },
    )
    parcel_row = next(row for row in rows if row["field"] == "parcel_id")
    gfa_row = next(row for row in rows if row["field"] == "GFA")
    site_row = next(row for row in rows if row["field"] == "site_area")
    year_row = next(row for row in rows if row["field"] == "year_built")
    assert parcel_row["value"] == "5151004903"
    assert gfa_row["value"] == "1440000"
    assert site_row["value"] == "110000"
    assert year_row["value"] == "1990"
