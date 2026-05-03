from runtime_orchestrator.adapters.motor_035 import Motor035Adapter


def _clusters(*names: str) -> dict:
    base = {
        "location_cluster": {"populated": False, "note": "Physical location primitives."},
        "jurisdiction_cluster": {"populated": False, "note": "Jurisdiction and regulatory anchoring."},
        "geometry_size_cluster": {"populated": False, "note": "Scale and geometry descriptors."},
        "vintage_structure_cluster": {"populated": False, "note": "Age, structure, renovation, and historical fabric."},
        "use_program_cluster": {"populated": False, "note": "Use mix and typology identity."},
        "operating_regime_cluster": {"populated": False, "note": "Schedules, shifts, occupancy, operating windows."},
        "fuel_energy_cluster": {"populated": False, "note": "Fuel, utility, or energy-system hints."},
        "systems_cluster": {"populated": False, "note": "Known system and equipment descriptors."},
        "regulatory_cluster": {"populated": False, "note": "Minimum rule-routing context."},
        "benchmark_mapping_cluster": {"populated": False, "note": "Enough typology context to route benchmark families."},
    }
    for name in names:
        base[name]["populated"] = True
    return base


def _base_inputs(
    *,
    address: str,
    jurisdiction_scope: list[str],
    target_type: str,
    decision_intent: str,
    target_classification: str,
    subject_gate_passed: bool,
    technical_substrate_readiness: str,
    observable_clusters: dict,
    reason: str = "",
) -> dict:
    target_definition_contract = {
        "address_raw": address,
        "jurisdiction_scope": jurisdiction_scope,
        "target_type": target_type,
        "decision_intent": decision_intent,
        "target_scope": "asset",
    }
    subject_definition_contract = {
        "address_raw": address,
        "asset_anchor_type": "postal_address",
    }
    return {
        "motor_001": {
            "subject_definition_contract": subject_definition_contract,
            "target_definition_contract": target_definition_contract,
        },
        "motor_006": {
            "asset_identity_resolution": {
                "subject_definition_contract": subject_definition_contract,
                "target_definition_contract": target_definition_contract,
                "intake_observables": {
                    "observable_clusters": observable_clusters,
                },
            }
        },
        "motor_007": {
            "subject_definition_contract": subject_definition_contract,
            "target_definition_contract": target_definition_contract,
            "subject_gate_passed": subject_gate_passed,
            "technical_substrate_readiness": technical_substrate_readiness,
            "recommended_report_type": "Decision-Blocked Asset Brief",
            "prohibited_report_types": ["Full Technical Decision Intelligence Report"],
            "observable_cluster_register": observable_clusters,
            "target_classification_object": {
                "target_type": target_classification,
                "classification_confidence": "high",
                "reason": reason,
            },
        },
    }


def test_motor_035_routes_nyc_operating_asset_to_local_mandatory_sources():
    adapter = Motor035Adapter()
    out = adapter.run(
        _base_inputs(
            address="350 FIFTH AVENUE, NEW YORK, NY, 10118",
            jurisdiction_scope=["US-NY-NYC"],
            target_type="commercial_building",
            decision_intent="acquisition_underwriting",
            target_classification="OPERATING_ASSET",
            subject_gate_passed=True,
            technical_substrate_readiness="partial",
            observable_clusters=_clusters(
                "location_cluster",
                "jurisdiction_cluster",
                "geometry_size_cluster",
                "vintage_structure_cluster",
                "use_program_cluster",
                "fuel_energy_cluster",
                "systems_cluster",
                "regulatory_cluster",
                "benchmark_mapping_cluster",
            ),
        )
    )
    mandatory_keys = {row["source_key"] for row in out["mandatory_sources"]}
    assert out["target_type_classification"] == "OPERATING_ASSET"
    assert out["routing_ready"] is True
    assert out["jurisdiction_class"] == "high_data_availability_building"
    assert "nyc_ll84_energy_benchmarking" in mandatory_keys
    assert "nyc_pluto_property" in mandatory_keys
    assert out["report_type_allowed"] == "Minimum Evidence Report"


def test_motor_035_blocks_technical_route_for_sf_hq_case():
    adapter = Motor035Adapter()
    out = adapter.run(
        _base_inputs(
            address="PIER 1 BAY 1, SAN FRANCISCO, CA 94111",
            jurisdiction_scope=["US-CA-SF"],
            target_type="warehouse_distribution",
            decision_intent="asset_screening",
            target_classification="CORPORATE_HEADQUARTERS",
            subject_gate_passed=False,
            technical_substrate_readiness="insufficient",
            observable_clusters=_clusters("location_cluster", "jurisdiction_cluster"),
            reason="Address semantics indicate headquarters or office context rather than a bounded operating asset.",
        )
    )
    assert out["target_type_classification"] == "CORPORATE_HEADQUARTERS"
    assert out["routing_ready"] is False
    assert out["mandatory_sources"] == []
    assert out["report_type_allowed"] == "Target Classification Brief"
    assert "Full Technical Report" in out["report_type_prohibited"]


def test_motor_035_upgrades_operating_asset_class_to_industrial_facility_and_promotes_process_sources():
    adapter = Motor035Adapter()
    out = adapter.run(
        _base_inputs(
            address="10777 CLAY ROAD, HOUSTON, TX 77041",
            jurisdiction_scope=["US-TX-HOUSTON"],
            target_type="industrial_plant",
            decision_intent="process_change",
            target_classification="OPERATING_ASSET",
            subject_gate_passed=True,
            technical_substrate_readiness="partial",
            observable_clusters=_clusters(
                "location_cluster",
                "jurisdiction_cluster",
                "geometry_size_cluster",
                "use_program_cluster",
                "operating_regime_cluster",
                "fuel_energy_cluster",
                "regulatory_cluster",
            ),
        )
    )
    high_priority_keys = {row["source_key"] for row in out["high_priority_sources"]}
    mandatory_keys = {row["source_key"] for row in out["mandatory_sources"]}
    assert out["target_type_classification"] == "INDUSTRIAL_FACILITY"
    assert out["asset_type"] == "industrial_facility"
    assert "tceq_permits_and_emissions" in mandatory_keys
    assert "doe_iac_database" in high_priority_keys
    assert "openei_industrial_combustion" in high_priority_keys


def test_motor_035_routes_oakland_building_to_new_ca_portal_contexts():
    adapter = Motor035Adapter()
    out = adapter.run(
        _base_inputs(
            address="195 5TH STREET, OAKLAND, CA 94607",
            jurisdiction_scope=["US-CA-OAKLAND"],
            target_type="commercial_building",
            decision_intent="target_identification",
            target_classification="OPERATING_ASSET",
            subject_gate_passed=True,
            technical_substrate_readiness="partial",
            observable_clusters=_clusters(
                "location_cluster",
                "jurisdiction_cluster",
                "geometry_size_cluster",
                "use_program_cluster",
                "regulatory_cluster",
            ),
        )
    )
    mandatory_keys = {row["source_key"] for row in out["mandatory_sources"]}
    high_priority_keys = {row["source_key"] for row in out["high_priority_sources"]}
    assert out["routing_ready"] is True
    assert out["jurisdiction_resolution"]["city"] == "Oakland"
    assert "alameda_county_property_search_portal" in mandatory_keys
    assert "oakland_building_permit_portal" in high_priority_keys
    assert "utility_pge_service_territory" in high_priority_keys


def test_motor_035_routes_los_angeles_building_to_assessor_benchmark_and_permits():
    adapter = Motor035Adapter()
    out = adapter.run(
        _base_inputs(
            address="111 SOUTH GRAND AVENUE, LOS ANGELES, CA 90012",
            jurisdiction_scope=["US-CA-LA", "US-CA"],
            target_type="commercial_building",
            decision_intent="asset_screening",
            target_classification="OPERATING_ASSET",
            subject_gate_passed=True,
            technical_substrate_readiness="partial",
            observable_clusters=_clusters(
                "location_cluster",
                "jurisdiction_cluster",
                "geometry_size_cluster",
                "use_program_cluster",
                "regulatory_cluster",
                "benchmark_mapping_cluster",
            ),
        )
    )
    mandatory_keys = {row["source_key"] for row in out["mandatory_sources"]}
    high_priority_keys = {row["source_key"] for row in out["high_priority_sources"]}
    assert out["routing_ready"] is True
    assert out["jurisdiction_resolution"]["city"] == "Los Angeles"
    assert "la_county_assessor_property_record" in mandatory_keys
    assert "city_benchmarking_los_angeles" in mandatory_keys
    assert "la_building_permits" in high_priority_keys
    assert "utility_ladwp_or_sce_service_territory" in high_priority_keys


def test_motor_035_routes_houston_building_to_hcad_and_houston_permit_context():
    adapter = Motor035Adapter()
    out = adapter.run(
        _base_inputs(
            address="700 LOUISIANA STREET, HOUSTON, TX 77002",
            jurisdiction_scope=["US-TX-HOUSTON", "US-TX"],
            target_type="commercial_building",
            decision_intent="asset_screening",
            target_classification="OPERATING_ASSET",
            subject_gate_passed=True,
            technical_substrate_readiness="partial",
            observable_clusters=_clusters(
                "location_cluster",
                "jurisdiction_cluster",
                "geometry_size_cluster",
                "use_program_cluster",
                "regulatory_cluster",
            ),
        )
    )
    mandatory_keys = {row["source_key"] for row in out["mandatory_sources"]}
    high_priority_keys = {row["source_key"] for row in out["high_priority_sources"]}
    assert out["routing_ready"] is True
    assert out["jurisdiction_resolution"]["city"] == "Houston"
    assert "harris_county_appraisal_district_property_record" in mandatory_keys
    assert "harris_cad_property_search_portal" in high_priority_keys
    assert "houston_building_permits" in high_priority_keys
    assert "utility_centerpoint_service_territory" in high_priority_keys


def test_motor_035_routes_manufacturing_facility_through_industrial_process_contract():
    adapter = Motor035Adapter()
    out = adapter.run(
        _base_inputs(
            address="5900 HIGHWAY 225, DEER PARK, TX 77536",
            jurisdiction_scope=["US-TX"],
            target_type="manufacturing_facility",
            decision_intent="process_change",
            target_classification="OPERATING_ASSET",
            subject_gate_passed=True,
            technical_substrate_readiness="partial",
            observable_clusters=_clusters(
                "location_cluster",
                "jurisdiction_cluster",
                "geometry_size_cluster",
                "use_program_cluster",
                "operating_regime_cluster",
                "fuel_energy_cluster",
                "regulatory_cluster",
            ),
        )
    )
    mandatory_keys = {row["source_key"] for row in out["mandatory_sources"]}
    high_priority_keys = {row["source_key"] for row in out["high_priority_sources"]}
    critical_fields = {row["field_name"] for row in out["critical_field_contract"]}
    assert out["target_type_classification"] == "INDUSTRIAL_FACILITY"
    assert out["asset_type"] == "industrial_facility"
    assert "process_anchor" in critical_fields
    assert "throughput_or_load_driver" in critical_fields
    assert "fuel_type" in critical_fields
    assert "tceq_permits_and_emissions" in mandatory_keys
    assert "state_environmental_agency_permits" in mandatory_keys
    assert "doe_iac_database" in high_priority_keys
    assert "openei_industrial_combustion" in high_priority_keys
