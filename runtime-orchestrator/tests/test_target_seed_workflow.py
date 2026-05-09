from __future__ import annotations

from types import SimpleNamespace

import dashboard as dashboard_module
from target_seeds import build_address_seed, build_bounded_asset_seed, normalize_pipeline_seed
from runtime_orchestrator.adapters.motor_001 import Motor001Adapter
from runtime_orchestrator.adapters.motor_010 import Motor010Adapter
from runtime_orchestrator.adapters.motor_011 import Motor011Adapter
from runtime_orchestrator.adapters.motor_012 import Motor012Adapter
from runtime_orchestrator.adapters.motor_014 import Motor014Adapter
from runtime_orchestrator.adapters.motor_024 import Motor024Adapter
from runtime_orchestrator.adapters.motor_025 import Motor025Adapter
from runtime_orchestrator.adapters.motor_027 import Motor027Adapter
from runtime_orchestrator.adapters.motor_006 import Motor006Adapter
from runtime_orchestrator.adapters.motor_007 import Motor007Adapter
from runtime_orchestrator.adapters.motor_008 import Motor008Adapter
from runtime_orchestrator.adapters.motor_022 import Motor022Adapter
from runtime_orchestrator.adapters.motor_028 import Motor028Adapter
from runtime_orchestrator.asset_contracts import derive_observable_clusters, derive_target_definition


def test_build_address_seed_creates_explicit_asset_first_contracts():
    pipeline = build_address_seed(
        address_raw="5900 HIGHWAY 225, DEER PARK, TX, 77536",
        target_type="oil_gas_downstream_facility",
        owner_name="Example Refining Co",
        owner_ticker="EXR",
    )
    subject = pipeline["subject_definition_contract"]
    target = pipeline["target_definition_contract"]
    assert pipeline["case_title"] == "Asset Context Prior"
    assert subject["subject_kind"] == "address_candidate"
    assert target["target_type"] == "oil_gas_downstream_facility"
    assert target["target_id"].startswith("addr-oil-gas-downstream-facility-")
    assert pipeline["case_id"].startswith("ZLab-addr-oil-gas-downstream-facility-")


def test_build_bounded_asset_seed_creates_operating_asset_ready_contracts():
    pipeline = build_bounded_asset_seed(
        address_raw="ONE VANDERBILT AVENUE, NEW YORK, NY, 10017",
        asset_name="One Vanderbilt",
        target_type="commercial_building",
        owner_name="SL Green Realty Corp",
        owner_ticker="SLG",
        asset_identifier="one-vanderbilt-nyc",
        asset_anchor_type="benchmark_record",
        asset_anchor_value="nyc_ll84::one-vanderbilt",
        jurisdiction_scope=["US-NY-NYC", "US-NY"],
        location_overrides={"city": "NEW YORK"},
        primary_uses=["Office"],
    )
    subject = pipeline["subject_definition_contract"]
    target = pipeline["target_definition_contract"]
    assert subject["subject_kind"] == "bounded_asset"
    assert subject["asset_identity_evidence_class"] == "multi-source_asset_bounded"
    assert target["target_name"] == "One Vanderbilt"
    assert target["target_identifier"] == "one-vanderbilt-nyc"
    assert "US-NY-NYC" in target["jurisdiction_scope"]
    assert target["target_id"].startswith("asset-commercial-building-one-vanderbilt")
    assert pipeline["case_id"].startswith("ZLab-asset-commercial-building-one-vanderbilt")


def test_normalize_pipeline_seed_rewrites_legacy_company_first_seed():
    legacy = {
        "case_id": "ZLab-BXP-2026",
        "case_title": "Operational Intelligence Report — Boston Properties",
        "case_subtitle": "REIT / Oficinas Costa Este — 6798",
        "facility_inputs": {
            "input_01_location": {
                "address": "800 BOYLSTON STREET, BOSTON, MA, 02199",
                "state": "MA",
                "country": "US",
                "jurisdiction_codes": ["US-MA"],
            },
            "input_02_facility_type": {"classification": "REIT / Oficinas Costa Este"},
            "input_03_sector": {
                "sector": "REIT / Oficinas Costa Este",
                "owner_name": "Boston Properties",
                "owner_ticker": "BXP",
                "owner_cik": "0001037540",
            },
            "input_10_main_concern": {
                "primary_concern": "operational_performance",
                "decision_type": "investment_evaluation",
            },
        },
        "phase_contracts": [],
        "taxonomy": {"version": "taxonomy_us_realestate_v1", "produced_by": "motor_003", "terms": []},
        "source_declarations": [],
        "sources": [],
    }
    normalized = normalize_pipeline_seed(legacy)
    assert normalized["case_title"] == "Asset Context Prior"
    assert "Operational Intelligence Report" not in normalized["case_title"]
    assert normalized["subject_definition_contract"]["subject_kind"] == "address_candidate"
    assert normalized["target_definition_contract"]["target_id"].startswith("addr-commercial-building-")
    assert normalized["facility_inputs"]["input_10_main_concern"]["decision_type"] == "target_identification_required"


def test_motor_022_flags_overclaimed_report_identity():
    adapter = Motor022Adapter()
    out = adapter.run({
        "motor_001": {"subject_definition_contract": {"subject_kind": "address_candidate"}},
        "motor_007": {
            "allowed_report_classes": ["Address Candidate Brief"],
            "report_identity_state": "TDIR Preliminary",
            "target_admissibility_state": "address_candidate_only",
            "asset_context_readiness": "asset_context_insufficient",
        },
        "motor_021": {
            "harness_passed": True,
            "harness_summary": {"total_checks": 4, "errors": 0, "warnings": 0, "passes": 4},
        },
    })
    assert not out["conformance_passed"]
    assert any(v["rule_id"] == "report_identity_allowed_by_subject_gate" for v in out["conformance_violations"])
    assert any(v["rule_id"] == "blocked_subject_cannot_render_full_tdir" for v in out["conformance_violations"])


def test_motor_022_passes_when_blocked_case_stays_bounded():
    adapter = Motor022Adapter()
    out = adapter.run({
        "motor_001": {"subject_definition_contract": {"subject_kind": "address_candidate"}},
        "motor_007": {
            "allowed_report_classes": ["Address Candidate Brief", "Asset Context Insufficiency Brief"],
            "report_identity_state": "Address Candidate Brief",
            "target_admissibility_state": "address_candidate_only",
            "asset_context_readiness": "asset_context_insufficient",
        },
        "motor_021": {
            "harness_passed": True,
            "harness_summary": {"total_checks": 4, "errors": 0, "warnings": 0, "passes": 4},
        },
    })
    assert out["conformance_passed"]
    assert out["conformance_violation_count"] == 0


def test_motor_001_emits_identity_first_ingestion_controls_for_address_only_seed():
    pipeline = build_address_seed(
        address_raw="PIER 1 BAY 1, SAN FRANCISCO, CA, 94111",
        target_type="warehouse_distribution",
        owner_name="Prologis",
        owner_ticker="PLD",
    )
    out = Motor001Adapter().run({"__pipeline__": pipeline})
    assert out["subject_contract_admissibility"] == "ambiguous_subject"
    assert out["target_type_classification_seed"]["target_type_classification"] == "AMBIGUOUS_TARGET"
    assert out["ingestion_contract_status"] == "identity_gate_required"
    assert "round_2_asset_physical_substrate" in out["prohibited_scrape_rounds"]
    assert "round_3_energy_utility_compliance" in out["prohibited_scrape_rounds"]


def test_motor_007_classifies_prologis_pier1_as_non_operating_asset_and_blocks_technical_report():
    pipeline = build_address_seed(
        address_raw="PIER 1 BAY 1, SAN FRANCISCO, CA, 94111",
        target_type="warehouse_distribution",
        owner_name="Prologis",
        owner_ticker="PLD",
    )
    m01 = Motor001Adapter().run({"__pipeline__": pipeline})
    target_definition = derive_target_definition(pipeline)
    observable_clusters = derive_observable_clusters(pipeline, target_definition)
    m06 = Motor006Adapter().run({
        "__pipeline__": pipeline,
        "motor_001": m01,
        "motor_003": {"term_index": {}, "target_definition_contract": target_definition},
        "motor_005": {
            "normalized_objects": [],
            "normalized_intake_observables": {"observable_clusters": observable_clusters},
        },
    })
    m07 = Motor007Adapter().run({
        "__pipeline__": pipeline,
        "motor_006": m06,
    })
    target_classification = m07["target_classification_object"]
    assert target_classification["target_type"] in {"CORPORATE_HEADQUARTERS", "AMBIGUOUS_TARGET"}
    assert target_classification["asset_level_evidence_found"] is False
    assert target_classification["issuer_only_evidence_found"] is True
    assert m07["recommended_report_type"] in {"Entity Address Classification Brief", "Target Clarification Brief"}
    assert m07["recommended_report_type_visible"] == "Target Classification Brief"
    assert m07["recommended_report_type_alias_policy"]["canonical_label"] == "Target Classification Brief"
    assert m07["recommended_report_type_alias_policy"]["is_compatibility_alias"] is True
    assert "Target Classification Brief" in m07["allowed_report_classes_visible"]
    assert "Full Technical Decision Intelligence Report" in m07["prohibited_report_types"]


def test_motor_007_classifies_bounded_nyc_seed_as_operating_asset():
    pipeline = build_bounded_asset_seed(
        address_raw="ONE VANDERBILT AVENUE, NEW YORK, NY, 10017",
        asset_name="One Vanderbilt",
        target_type="commercial_building",
        owner_name="SL Green Realty Corp",
        owner_ticker="SLG",
        asset_identifier="one-vanderbilt-nyc",
        asset_anchor_type="benchmark_record",
        asset_anchor_value="nyc_ll84::one-vanderbilt",
        jurisdiction_scope=["US-NY-NYC", "US-NY"],
        location_overrides={"city": "NEW YORK"},
        primary_uses=["Office"],
    )
    m01 = Motor001Adapter().run({"__pipeline__": pipeline})
    target_definition = derive_target_definition(pipeline)
    observable_clusters = derive_observable_clusters(pipeline, target_definition)
    m06 = Motor006Adapter().run(
        {
            "__pipeline__": pipeline,
            "motor_001": m01,
            "motor_003": {"term_index": {}, "target_definition_contract": target_definition},
            "motor_005": {
                "normalized_objects": [],
                "normalized_intake_observables": {"observable_clusters": observable_clusters},
            },
        }
    )
    m07 = Motor007Adapter().run({"__pipeline__": pipeline, "motor_006": m06})
    assert m07["target_classification_object"]["target_type"] == "OPERATING_ASSET"
    assert m07["target_admissibility_state"] == "bounded_asset"
    assert m07["subject_gate_passed"] is True
    assert m07["recommended_report_type"] == "Decision-Blocked Asset Brief"


def test_motor_001_classifies_po_box_as_registered_agent_or_mailing_address():
    pipeline = build_address_seed(
        address_raw="P.O. BOX 123, WILMINGTON, DE, 19801",
        target_type="commercial_building",
        owner_name="Example Holdco",
        owner_ticker="EXH",
    )
    out = Motor001Adapter().run({"__pipeline__": pipeline})
    seed = out["target_type_classification_seed"]
    assert seed["target_type_classification"] == "REGISTERED_AGENT_OR_MAILING_ADDRESS"
    assert seed["report_type_recommendation"]["recommended_report_type"] == "Entity Address Classification Brief"


def test_motor_007_keeps_plain_address_only_case_as_ambiguous_target():
    pipeline = build_address_seed(
        address_raw="123 TEST ACCESS ROAD, ELKO, NV, 89801",
        target_type="industrial_plant",
    )
    m01 = Motor001Adapter().run({"__pipeline__": pipeline})
    target_definition = derive_target_definition(pipeline)
    observable_clusters = derive_observable_clusters(pipeline, target_definition)
    m06 = Motor006Adapter().run({
        "__pipeline__": pipeline,
        "motor_001": m01,
        "motor_003": {"term_index": {}, "target_definition_contract": target_definition},
        "motor_005": {
            "normalized_objects": [],
            "normalized_intake_observables": {"observable_clusters": observable_clusters},
        },
    })
    m07 = Motor007Adapter().run({
        "__pipeline__": pipeline,
        "motor_006": m06,
    })
    assert m07["target_classification_object"]["target_type"] == "AMBIGUOUS_TARGET"
    assert m07["recommended_report_type"] == "Target Clarification Brief"
    assert m07["asset_level_evidence_found"] is False


def test_motor_007_classifies_po_box_case_as_registered_agent_or_mailing_address():
    pipeline = build_address_seed(
        address_raw="P.O. BOX 123, WILMINGTON, DE, 19801",
        target_type="commercial_building",
        owner_name="Example Holdco",
        owner_ticker="EXH",
    )
    m01 = Motor001Adapter().run({"__pipeline__": pipeline})
    target_definition = derive_target_definition(pipeline)
    observable_clusters = derive_observable_clusters(pipeline, target_definition)
    m06 = Motor006Adapter().run(
        {
            "__pipeline__": pipeline,
            "motor_001": m01,
            "motor_003": {"term_index": {}, "target_definition_contract": target_definition},
            "motor_005": {
                "normalized_objects": [],
                "normalized_intake_observables": {"observable_clusters": observable_clusters},
            },
        }
    )
    m07 = Motor007Adapter().run({"__pipeline__": pipeline, "motor_006": m06})
    assert m07["target_classification_object"]["target_type"] == "REGISTERED_AGENT_OR_MAILING_ADDRESS"
    assert m07["recommended_report_type"] == "Entity Address Classification Brief"
    assert m07["asset_level_evidence_found"] is False
    assert m07["issuer_only_evidence_found"] is True


def test_motor_008_registers_scope_authority_and_rejects_benchmark_context_before_identity_gate():
    pipeline = build_address_seed(
        address_raw="PIER 1 BAY 1, SAN FRANCISCO, CA, 94111",
        target_type="warehouse_distribution",
        owner_name="Prologis",
        owner_ticker="PLD",
    )
    pipeline["sources"] = [
        {
            "source_id": "sec_filing",
            "content_type": "reference",
            "metadata": {"fetch_url": "https://www.sec.gov/Archives/example", "title": "10-K", "authoritative": True},
            "content": "",
        },
        {
            "source_id": "cbecs_benchmark",
            "content_type": "reference",
            "metadata": {"fetch_url": "https://www.eia.gov/cbecs", "title": "CBECS benchmark"},
            "content": "",
        },
    ]
    m01 = Motor001Adapter().run({"__pipeline__": pipeline})
    out = Motor008Adapter().run({"__pipeline__": pipeline, "motor_001": m01})
    sec = out["source_registry"]["sec_filing"]
    bench = out["source_registry"]["cbecs_benchmark"]
    assert sec["scope"] == "ENTITY_LEVEL"
    assert sec["authority_score"] == "high"
    assert sec["accepted"] is True
    assert bench["scope"] == "BENCHMARK_LEVEL"
    assert bench["accepted"] is False
    assert bench["rejection_reason"] == "deferred_until_identity_gate"


def test_motor_028_identity_only_mode_defers_sec_and_benchmarks(monkeypatch):
    pipeline = build_address_seed(
        address_raw="PIER 1 BAY 1, SAN FRANCISCO, CA, 94111",
        target_type="warehouse_distribution",
        owner_name="Prologis",
        owner_ticker="PLD",
    )
    m01 = Motor001Adapter().run({"__pipeline__": pipeline})
    m08 = Motor008Adapter().run({"__pipeline__": pipeline, "motor_001": m01})

    monkeypatch.setattr(
        "runtime_orchestrator.adapters.motor_028._fetch_census_geocoder",
        lambda ctx: {
            "matchedAddress": ctx["address"],
            "coordinates": {"x": -122.394, "y": 37.795},
            "addressComponents": {"city": "SAN FRANCISCO", "zip": "94111"},
            "geographies": {"Counties": [{"GEOID": "06075", "STATE": "06"}]},
        },
    )
    monkeypatch.setattr(
        "runtime_orchestrator.adapters.motor_028._get_crawler",
        lambda ctx: SimpleNamespace(get_cached_or_live=lambda key, fn, ctx: None),
    )

    out = Motor028Adapter().run({
        "__pipeline__": pipeline,
        "motor_001": m01,
        "motor_003": {"term_index": {}},
        "motor_008": m08,
        "motor_009": {},
    })
    assert out["round_execution_profile"]["identity_only_mode"] is True
    statuses = {a["source_type"]: a["status"] for a in out["discovery_attempts"]}
    assert statuses["sec_edgar_submissions"] == "not_applicable"
    assert statuses["sec_edgar_xbrl_facts"] == "not_applicable"
    assert out["benchmark_routing_register"]["selected_source_type"] in {
        "city_benchmarking_san_francisco",
        "eia_cbecs_2018_benchmarks",
    }
    assert any(
        entry["rejection_reason"] == "deferred_until_identity_gate"
        for entry in out["discarded_source_log"]
    )


def test_motor_010_preserves_identical_content_when_scope_differs():
    out = Motor010Adapter().run(
        {
            "motor_004": {
                "parsed_objects": [
                    {"source_id": "asset_src", "parsed_content": {"text": "same content"}},
                    {"source_id": "entity_src", "parsed_content": {"text": "same content"}},
                ]
            },
            "motor_005": {
                "normalized_objects": [
                    {"source_id": "asset_src", "parsed_content": {"text": "same content"}},
                    {"source_id": "entity_src", "parsed_content": {"text": "same content"}},
                ]
            },
            "motor_008": {
                "source_registry": {
                    "asset_src": {
                        "scope": "ASSET_LEVEL",
                        "authority_score": "high",
                        "source_family": "asset_context_record",
                        "recency": "current",
                    },
                    "entity_src": {
                        "scope": "ENTITY_LEVEL",
                        "authority_score": "high",
                        "source_family": "issuer_context_record",
                        "recency": "current",
                    },
                }
            },
        }
    )
    assert out["total_unique"] == 2
    assert out["total_duplicates"] == 0
    assert out["total_scope_preserved"] == 1
    statuses = {row["source_id"]: row["dedup_status"] for row in out["dedup_objects"]}
    assert statuses["asset_src"] == "unique"
    assert statuses["entity_src"] == "scope_preserved_duplicate"


def test_motor_011_assigns_scope_boundary_and_admissibility_defaults():
    out = Motor011Adapter().run(
        {
            "motor_003": {"term_index": {"sq_ft": {}}},
            "motor_007": {
                "evaluated_entities": [
                    {
                        "entity_id": "ent_asset",
                        "source_id": "asset_src",
                        "resolved_terms": ["sq_ft"],
                        "fitness_score": 0.92,
                        "fitness_status": "fit",
                        "parsed_content": {"value": "120000"},
                        "metadata": {},
                    },
                    {
                        "entity_id": "ent_entity",
                        "source_id": "entity_src",
                        "resolved_terms": ["REIT"],
                        "fitness_score": 0.78,
                        "fitness_status": "fit",
                        "parsed_content": {"value": "issuer context"},
                        "metadata": {},
                    },
                ]
            },
            "motor_008": {
                "source_registry": {
                    "asset_src": {"scope": "ASSET_LEVEL", "authority_score": "high", "source_family": "asset_context_record"},
                    "entity_src": {"scope": "ENTITY_LEVEL", "authority_score": "high", "source_family": "issuer_context_record"},
                }
            },
            "motor_010": {
                "dedup_objects": [
                    {
                        "source_id": "asset_src",
                        "parsed_content": {"value": "120000"},
                        "source_scope": "ASSET_LEVEL",
                        "source_authority_score": "high",
                        "source_family": "asset_context_record",
                        "source_recency": "current",
                        "dedup_status": "unique",
                    },
                    {
                        "source_id": "entity_src",
                        "parsed_content": {"value": "issuer context"},
                        "source_scope": "ENTITY_LEVEL",
                        "source_authority_score": "high",
                        "source_family": "issuer_context_record",
                        "source_recency": "current",
                        "dedup_status": "unique",
                    },
                ]
            },
        }
    )
    by_source = {row["source_id"]: row for row in out["library_objects"]}
    assert by_source["asset_src"]["scope_boundary"] == "ASSET_LEVEL"
    assert by_source["asset_src"]["admissibility_default"] == "CONFIRMED_ASSET_LEVEL"
    assert by_source["entity_src"]["scope_boundary"] == "ENTITY_LEVEL"
    assert by_source["entity_src"]["admissibility_default"] == "ENTITY_CONTEXT_ONLY"


def test_motor_012_builds_asset_field_register_and_missing_evidence_register():
    pipeline = build_address_seed(
        address_raw="PIER 1 BAY 1, SAN FRANCISCO, CA, 94111",
        target_type="warehouse_distribution",
        owner_name="Prologis",
        owner_ticker="PLD",
    )
    m01 = Motor001Adapter().run({"__pipeline__": pipeline})
    target_definition = derive_target_definition(pipeline)
    observable_clusters = derive_observable_clusters(pipeline, target_definition)
    m06 = Motor006Adapter().run(
        {
            "__pipeline__": pipeline,
            "motor_001": m01,
            "motor_003": {"term_index": {}, "target_definition_contract": target_definition},
            "motor_005": {
                "normalized_objects": [],
                "normalized_intake_observables": {"observable_clusters": observable_clusters},
            },
        }
    )
    m07 = Motor007Adapter().run({"__pipeline__": pipeline, "motor_006": m06})
    m08 = {"total_sources": 1}
    m28 = {
        "quality_gate_passed": True,
        "source_register": [
            {
                "source_id": "census_geocoder::pier1",
                "title": "census_geocoder",
                "scope": "ASSET_LEVEL",
                "authority_score": "high",
                "recency": "current",
                "accepted": True,
                "source_family": "geospatial_public_record",
            }
        ],
        "enriched_data": {
            "requestable_evidence_items": [],
            "coverage_gaps": [],
            "benchmark_routing_register": {},
        },
    }
    out = Motor012Adapter().run(
        {
            "__pipeline__": pipeline,
            "motor_001": m01,
            "motor_004": {"parsed_objects": []},
            "motor_005": {"normalized_objects": []},
            "motor_007": m07,
            "motor_008": m08,
            "motor_011": {"library_objects": []},
            "motor_028": m28,
        }
    )
    field_rows = {row["field"]: row for row in out["asset_field_register"]}
    assert field_rows["address"]["admissibility"] == "CONFIRMED_ASSET_LEVEL"
    assert field_rows["GFA"]["status"] == "BLOCKING_FIELD"
    assert any(row["missing_field"] == "GFA" for row in out["missing_evidence_register"])


def test_motor_012_promotes_nyc_public_records_into_asset_field_register():
    pipeline = build_address_seed(
        address_raw="350 FIFTH AVENUE, NEW YORK, NY, 10118",
        target_type="commercial_building",
        owner_name="Empire State Realty Trust",
        owner_ticker="ESRT",
    )
    m01 = Motor001Adapter().run({"__pipeline__": pipeline})
    target_definition = derive_target_definition(pipeline)
    observable_clusters = derive_observable_clusters(pipeline, target_definition)
    m06 = Motor006Adapter().run(
        {
            "__pipeline__": pipeline,
            "motor_001": m01,
            "motor_003": {"term_index": {}, "target_definition_contract": target_definition},
            "motor_005": {
                "normalized_objects": [],
                "normalized_intake_observables": {"observable_clusters": observable_clusters},
            },
        }
    )
    m07 = Motor007Adapter().run({"__pipeline__": pipeline, "motor_006": m06})
    m28 = {
        "quality_gate_passed": True,
        "dataset_coverage_register": [
            {"dataset_key": "nyc_pluto", "status": "accepted", "field_coverage": ["GFA"], "notes": "", "matched_sources": ["nyc_pluto_property"]},
            {"dataset_key": "nyc_ll84_benchmarking", "status": "accepted", "field_coverage": ["EUI", "emissions"], "notes": "", "matched_sources": ["nyc_ll84_energy_benchmarking"]},
            {"dataset_key": "nyc_dob_permits", "status": "accepted", "field_coverage": ["major_renovations", "HVAC_type"], "notes": "", "matched_sources": ["nyc_dob_permits"]},
            {"dataset_key": "nyc_ll97_emissions", "status": "screened", "field_coverage": ["penalty_rate"], "notes": "", "matched_sources": ["nyc_ll84_energy_benchmarking"]},
        ],
        "source_register": [
            {
                "source_id": "nyc_pluto_property::350-fifth",
                "title": "nyc_pluto_property",
                "scope": "ASSET_LEVEL",
                "authority_score": "high",
                "recency": "current",
                "accepted": True,
                "source_family": "geospatial_public_record",
            },
            {
                "source_id": "nyc_ll84_energy_benchmarking::350-fifth",
                "title": "nyc_ll84_energy_benchmarking",
                "scope": "ASSET_LEVEL",
                "authority_score": "high",
                "recency": "current",
                "accepted": True,
                "source_family": "benchmarking_disclosure_record",
            },
            {
                "source_id": "nyc_dob_permits::350-fifth",
                "title": "nyc_dob_permits",
                "scope": "ASSET_LEVEL",
                "authority_score": "high",
                "recency": "current",
                "accepted": True,
                "source_family": "permit_record",
            },
        ],
        "enriched_data": {
            "requestable_evidence_items": [],
            "coverage_gaps": [],
            "benchmark_routing_register": {"selected_source_type": "nyc_ll84_energy_benchmarking"},
            "pluto_property": {
                "bbl": "1008590044",
                "bin": "1088715",
                "bldgarea": "2788222",
                "numfloors": "102",
                "yearbuilt": "1931",
                "bldgclass": "O4",
            },
            "ll84_energy_benchmarking": {
                "records": [
                    {
                        "reporting_year": "2024",
                        "weather_normalized_site_eui": "67.4",
                        "site_eui": "71.2",
                        "total_ghg_emissions_metric_tons_co2e": "12500",
                        "largest_property_use_type": "Office",
                    }
                ]
            },
            "dob_permits_recent": [
                {
                    "issuance_date": "2024-06-01",
                    "job_type": "A2",
                    "work_type": "MECHANICAL",
                    "job_description": "HVAC upgrade",
                }
            ],
        },
    }
    out = Motor012Adapter().run(
        {
            "__pipeline__": pipeline,
            "motor_001": m01,
            "motor_004": {"parsed_objects": []},
            "motor_005": {"normalized_objects": []},
            "motor_007": m07,
            "motor_008": {"total_sources": 3},
            "motor_011": {"library_objects": []},
            "motor_028": m28,
        }
    )
    field_rows = {row["field"]: row for row in out["asset_field_register"]}
    assert field_rows["GFA"]["source_id"] == "nyc_pluto_property::350-fifth"
    assert field_rows["GFA"]["admissibility"] == "CONFIRMED_ASSET_LEVEL"
    assert field_rows["current_EUI"]["source_id"] == "nyc_ll84_energy_benchmarking::350-fifth"
    assert field_rows["current_EUI"]["admissibility"] == "CONFIRMED_ASSET_LEVEL"
    assert field_rows["emissions"]["status"] == "OBSERVED"
    assert field_rows["permits"]["status"] == "OBSERVED"
    assert field_rows["year_built"]["value"] == "1931"
    assert out["dataset_coverage_register"][0]["dataset_key"] == "nyc_pluto"
    canonical = out["canonical_asset_context_summary"]
    assert canonical["canonical_asset_context_state"] == "asset_context_minimal"
    assert canonical["screening_supported"] is True
    assert "geometry_size_cluster" in canonical["supported_clusters"]
    assert "regulatory_cluster" in canonical["supported_clusters"]
    assert "geometry_size_cluster" not in canonical["missing_clusters"]
    assert any(row["field"] == "GFA" for row in canonical["supported_field_register"])


def test_motor_014_propagates_missing_evidence_register_into_decision_core():
    pipeline = build_address_seed(
        address_raw="PIER 1 BAY 1, SAN FRANCISCO, CA, 94111",
        target_type="warehouse_distribution",
        owner_name="Prologis",
        owner_ticker="PLD",
    )
    m01 = Motor001Adapter().run({"__pipeline__": pipeline})
    target_definition = derive_target_definition(pipeline)
    observable_clusters = derive_observable_clusters(pipeline, target_definition)
    m06 = Motor006Adapter().run(
        {
            "__pipeline__": pipeline,
            "motor_001": m01,
            "motor_003": {"term_index": {}, "target_definition_contract": target_definition},
            "motor_005": {
                "normalized_objects": [],
                "normalized_intake_observables": {"observable_clusters": observable_clusters},
            },
        }
    )
    m07 = Motor007Adapter().run({"__pipeline__": pipeline, "motor_006": m06})
    m12 = Motor012Adapter().run(
        {
            "__pipeline__": pipeline,
            "motor_001": m01,
            "motor_004": {"parsed_objects": []},
            "motor_005": {"normalized_objects": []},
            "motor_007": m07,
            "motor_008": {"total_sources": 0},
            "motor_011": {"library_objects": []},
            "motor_028": {"quality_gate_passed": True, "source_register": [], "enriched_data": {"requestable_evidence_items": [], "coverage_gaps": [], "benchmark_routing_register": {}}},
        }
    )
    out = Motor014Adapter().run(
        {
            "motor_013": {"inference_case_register": [], "facility_prior_id": m12["facility_prior_id"]},
            "motor_012": m12,
            "motor_007": m07,
            "motor_001": m01,
        }
    )
    assert any(row["missing_field"] == "GFA" for row in out["missing_evidence_register"])
    assert any("missing field 'GFA'" in row["question"] for row in out["next_best_questions"])


def test_governance_layers_consume_scraping_admissibility_objects():
    m24 = Motor024Adapter().run(
        {
            "__runtime__": {
                "truth_summary": {"implemented_contract": 33, "completed_real": 33},
                "target_admissibility_state": "address_candidate_only",
                "subject_gate_passed": False,
                "asset_context_readiness": "asset_context_insufficient",
                "recommended_report_type": "Entity Address Classification Brief",
                "prohibited_report_types": ["Full Technical Decision Intelligence Report"],
                "target_definition": {"target_scope": "asset", "target_type": "warehouse_distribution"},
            },
            "motor_001": {"validated_contracts": [], "rejected_contracts": [], "total_input": 0},
            "motor_002": {"versioned_objects": [], "total_versioned": 0},
            "motor_007": {
                "evaluated_entities": [],
                "total_fit": 0,
                "total_evaluated": 0,
                "fitness_rate": 0.0,
                "target_scope_fitness": 0.25,
                "target_definition_contract": {"target_scope": "asset", "target_type": "warehouse_distribution"},
                "target_admissibility_state": "address_candidate_only",
                "subject_gate_passed": False,
                "subject_gate_reason_register": [{"code": "address_not_yet_asset", "message": "Address is not yet a bounded asset.", "severity": "warning"}],
                "allowed_report_classes": ["Address Candidate Brief", "Issuer Context Memo"],
                "asset_context_readiness": "asset_context_insufficient",
                "report_identity_state": "Address Candidate Brief",
                "dominant_evidence_scope": "mixed_scope_with_issuer_bias",
                "missing_observable_clusters": ["geometry_size_cluster"],
                "target_classification_object": {"target_type": "CORPORATE_HEADQUARTERS", "classification_confidence": "high"},
                "recommended_report_type": "Entity Address Classification Brief",
                "prohibited_report_types": ["Full Technical Decision Intelligence Report"],
            },
            "motor_028": {
                "quality_gate_passed": True,
                "source_register": [
                    {"accepted": True, "scope": "ASSET_LEVEL"},
                    {"accepted": False, "scope": "BENCHMARK_LEVEL"},
                ],
                "routing_plan_compliance": {
                    "total_routed_sources": 5,
                    "mandatory_sources_missing_from_executor": ["nyc_dof_property_record"],
                    "rows": [
                        {
                            "source_key": "nyc_dof_property_record",
                            "priority": "mandatory",
                            "status": "not_executed_by_executor",
                            "matched_attempt_statuses": {},
                        }
                    ],
                },
                "contamination_log": [{"detail": "Wrong city matched", "severity": "high", "affected_field": "address"}],
                "discovery_summary": {"attempted": 2, "admitted": 1},
            },
            "motor_009": {},
            "motor_012": {
                "asset_field_register": [{"field": "GFA", "status": "BLOCKING_FIELD"}],
                "missing_evidence_register": [{"missing_field": "GFA"}],
            },
            "motor_013": {},
            "motor_014": {},
            "motor_015": {},
            "motor_016": {},
            "motor_017": {},
            "motor_019": {},
            "motor_020": {},
            "motor_027": {},
            "motor_033": {},
        }
    )
    health = m24["pipeline_health_summary"]
    assert health["recommended_report_type"] == "Entity Address Classification Brief"
    assert health["source_register_count"] == 2
    assert health["missing_evidence_count"] == 1
    assert health["blocking_field_count"] == 1
    assert health["mandatory_source_gap_count"] == 1
    assert health["mandatory_sources_missing_from_executor"] == ["nyc_dof_property_record"]

    m25 = Motor025Adapter().run(
        {
            "__runtime__": {
                "target_admissibility_state": "address_candidate_only",
                "subject_gate_passed": False,
                "asset_context_readiness": "asset_context_insufficient",
                "recommended_report_type": "Entity Address Classification Brief",
                "prohibited_report_types": ["Full Technical Decision Intelligence Report"],
                "target_definition": {"target_scope": "asset", "target_type": "warehouse_distribution"},
            },
            "motor_001": {},
            "motor_022": {},
            "motor_024": m24,
        }
    )
    assert m25["recommended_report_type"] == "Entity Address Classification Brief"
    assert m25["blocking_field_count"] == 1
    assert m25["source_register_count"] == 2
    assert m25["mandatory_source_gap_count"] == 1
    assert m25["mandatory_sources_missing_from_executor"] == ["nyc_dof_property_record"]


def test_motor_012_surfaces_routing_gap_as_missing_evidence():
    out = Motor012Adapter().run(
        {
            "__pipeline__": {
                "facility_inputs": {
                    "input_01_location": {"address": "ONE VANDERBILT AVENUE, NEW YORK, NY, 10017", "city": "NEW YORK", "state_code": "NY"},
                    "input_02_facility_type": {"primary_classification": "commercial_building"},
                    "input_03_sector": {"owner_name": "SL Green Realty Corp", "owner_ticker": "SLG"},
                    "input_04_primary_use": {},
                    "input_05_size": {},
                    "input_06_vintage": {},
                    "input_07_operating_schedule": {},
                    "input_08_energy_fuel": {},
                    "input_09_known_systems": {},
                    "input_10_main_concern": {},
                }
            },
            "motor_001": {},
            "motor_004": {},
            "motor_005": {},
            "motor_007": {
                "target_definition_contract": {
                    "target_scope": "asset",
                    "target_type": "commercial_building",
                    "target_name": "One Vanderbilt",
                    "target_label": "One Vanderbilt",
                    "address_raw": "ONE VANDERBILT AVENUE, NEW YORK, NY, 10017",
                    "owner_entity": "SL Green Realty Corp",
                },
                "asset_context_readiness": "asset_context_insufficient",
                "observable_cluster_register": {},
                "missing_observable_clusters": ["geometry_size_cluster"],
            },
            "motor_008": {},
            "motor_011": {"library_objects": []},
            "motor_028": {
                "enriched_data": {},
                "quality_gate_passed": True,
                "source_register": [],
                "routing_plan_compliance": {
                    "total_routed_sources": 5,
                    "mandatory_sources_missing_from_executor": ["nyc_dof_property_record"],
                    "rows": [],
                },
                "source_routing_plan": {
                    "mandatory_sources": [
                        {
                            "source_key": "nyc_dof_property_record",
                            "source_name": "NYC Department of Finance / BBL property record",
                        }
                    ]
                },
                "dataset_coverage_register": [],
            },
        }
    )
    assert out["routing_plan_compliance"]["mandatory_sources_missing_from_executor"] == ["nyc_dof_property_record"]
    assert any(
        row["missing_field"] == "mandatory_source::nyc_dof_property_record"
        for row in out["missing_evidence_register"]
    )


def test_motor_027_blocks_delivery_when_routing_gap_hold_is_active(tmp_path):
    pdf_path = tmp_path / "dummy.pdf"
    pdf_path.write_bytes(b"%PDF-1.4\n%dummy\n")

    out = Motor027Adapter().run(
        {
            "__pipeline__": {
                "output_dir": str(tmp_path / "out"),
                "run_id": "run:test",
            },
            "motor_016": {
                "report_package": {
                    "package_id": "pkg:test",
                    "document_type": "Decision-Blocked Asset Brief",
                    "report_product_state": "decision_admissibility",
                    "case_metadata": {"case_id": "case:test"},
                    "governance_summary": {
                        "routing_plan_summary": {
                            "routing_plan_total": 5,
                            "mandatory_source_gap_count": 1,
                            "mandatory_sources_missing_from_executor": ["nyc_dof_property_record"],
                            "routing_plan_gate_passed": False,
                        }
                    },
                }
            },
            "motor_017": {
                "pdf_path": str(pdf_path),
                "pdf_paths": {"en": str(pdf_path)},
                "compilation_status": "success",
                "render_job_id": "rj:test",
                "package_id": "pkg:test",
            },
        }
    )
    assert out["delivered"] is False
    assert out["delivery_manifest"]["routing_plan_summary"]["mandatory_source_gap_count"] == 1


def test_motor_027_allows_exploratory_prior_delivery_when_routing_gaps_are_explicitly_disclosed(tmp_path):
    pdf_path = tmp_path / "dummy.pdf"
    pdf_path.write_bytes(b"%PDF-1.4\n%dummy\n")

    out = Motor027Adapter().run(
        {
            "__pipeline__": {
                "output_dir": str(tmp_path / "out"),
                "run_id": "run:test",
            },
            "motor_016": {
                "report_package": {
                    "package_id": "pkg:test",
                    "document_type": "Exploratory Prior Brief",
                    "report_product_state": "technical_report",
                    "case_metadata": {"case_id": "case:test"},
                    "source_family_coverage_table": [
                        {
                            "source_family": "county_assessor_or_appraisal_property_record",
                            "queried": False,
                            "found": False,
                            "scope": "NOT_QUERIED",
                            "support_note": "Source required by routing plan but not executed by the current executor.",
                        },
                        {
                            "source_family": "state_environmental_agency_permits",
                            "queried": False,
                            "found": False,
                            "scope": "NOT_QUERIED",
                            "support_note": "Source required by routing plan but not executed by the current executor.",
                        },
                    ],
                    "governance_summary": {
                        "routing_plan_summary": {
                            "routing_plan_total": 4,
                            "mandatory_source_gap_count": 2,
                            "mandatory_sources_missing_from_executor": [
                                "county_assessor_or_appraisal_property_record",
                                "state_environmental_agency_permits",
                            ],
                            "routing_plan_gate_passed": False,
                        }
                    },
                }
            },
            "motor_017": {
                "pdf_path": str(pdf_path),
                "pdf_paths": {"en": str(pdf_path)},
                "compilation_status": "success",
                "render_job_id": "rj:test",
                "package_id": "pkg:test",
            },
        }
    )

    assert out["delivered"] is True
    assert out["delivery_manifest"]["routing_plan_summary"]["delivery_override_applied"] is True


def test_motor_027_manifest_exposes_ingestion_learning_summary(tmp_path):
    pdf_path = tmp_path / "dummy.pdf"
    pdf_path.write_bytes(b"%PDF-1.4\n%dummy\n")

    out = Motor027Adapter().run(
        {
            "__pipeline__": {
                "output_dir": str(tmp_path / "out"),
                "run_id": "run:test",
            },
            "__runtime__": {
                "ingestion_learning_summary": {
                    "previous_run_id": "run:prev",
                    "net_progress_state": "improved",
                    "priority_count": 3,
                    "top_priority_action": "execute_missing_mandatory_source",
                },
                "case_delta_summary": {"net_progress_state": "improved"},
                "source_yield_memory_summary": {"productive_source_count": 2},
                "next_ingestion_priority_update": {
                    "priority_count": 3,
                    "priorities": [{"priority_rank": 1, "action_type": "execute_missing_mandatory_source"}],
                },
            },
            "motor_016": {
                "report_package": {
                    "package_id": "pkg:test",
                    "document_type": "Decision-Blocked Asset Brief",
                    "report_product_state": "decision_admissibility",
                    "case_metadata": {"case_id": "case:test"},
                    "governance_summary": {},
                }
            },
            "motor_017": {
                "pdf_path": str(pdf_path),
                "pdf_paths": {"en": str(pdf_path)},
                "compilation_status": "success",
                "render_job_id": "rj:test",
                "package_id": "pkg:test",
            },
        }
    )

    assert out["delivered"] is True
    manifest = out["delivery_manifest"]
    assert manifest["ingestion_learning_summary"]["net_progress_state"] == "improved"
    assert manifest["governance_summary"]["ingestion_learning_summary"]["top_priority_action"] == "execute_missing_mandatory_source"
    assert manifest["case_delta_summary"]["net_progress_state"] == "improved"


def test_motor_027_manifest_exposes_structural_intelligence_bundle(tmp_path):
    pdf_path = tmp_path / "dummy.pdf"
    pdf_path.write_bytes(b"%PDF-1.4\n%dummy\n")

    out = Motor027Adapter().run(
        {
            "__pipeline__": {
                "output_dir": str(tmp_path / "out"),
                "run_id": "run:test",
            },
            "motor_016": {
                "report_package": {
                    "package_id": "pkg:test",
                    "document_type": "Compliance / Investment Screening Brief",
                    "report_product_state": "technical_report",
                    "case_metadata": {"case_id": "case:test"},
                    "governance_summary": {},
                    "structural_intelligence_summary": {
                        "dominant_variable_count": 4,
                        "cross_layer_conflict_count": 2,
                        "conditional_redesign_count": 1,
                        "gold_nugget_authority_state": "skill_primary",
                        "gold_nugget_source_register": "motor_054.authoritative_gold_nugget_register",
                    },
                    "structural_output_mode_classifier_table": [
                        {
                            "asset": "One Vanderbilt",
                            "recommended_output_mode": "Structural Contradiction Brief",
                            "activation_state": "activated_secondary",
                            "activation_reason": "Mode is admissible as a secondary structural surface and does not override the primary report type.",
                            "required_claims": ["TAD_action_claim"],
                            "primary_report_type_guard": ["Compliance / Investment Screening Brief"],
                            "why": "Multiple cross-layer contradictions are active.",
                        }
                    ],
                    "structural_output_mode_summary": {
                        "primary_report_type": "Compliance / Investment Screening Brief",
                        "activated_secondary_modes": ["Structural Contradiction Brief"],
                        "blocked_secondary_modes": [],
                        "policy_note": "Structural output modes are secondary governed surfaces. They cannot override the primary report type or the claim-permission ceiling.",
                        "eligible_primary_modes": ["Structural Contradiction Brief"],
                        "non_promotable_primary_modes": [],
                        "leading_primary_promotion_candidate": "Structural Contradiction Brief",
                        "primary_promotion_policy_note": "Primary structural promotion remains advisory until the sovereign classifier explicitly elects it. Eligible modes cannot override the currently published report type without a dedicated promotion gate.",
                        "activation_count": 1,
                        "blocked_count": 0,
                        "eligible_primary_count": 1,
                    },
                    "structural_primary_promotion_gate": {
                        "base_primary_report_type": "Compliance / Investment Screening Brief",
                        "requested_structural_primary_mode": "Structural Contradiction Brief",
                        "request_basis": "explicit_target_request",
                        "promotion_state": "elected_primary_structural_mode",
                        "eligible_primary_modes": ["Structural Contradiction Brief"],
                        "elected_primary_report_type": "Structural Contradiction Brief",
                        "override_allowed": True,
                        "reason": "Structural primary-mode promotion was explicitly requested and passed the governed eligibility gate.",
                    },
                    "structural_executive_summary": {
                        "structural_mode_candidates": ["Structural Contradiction Brief"],
                        "promotable_primary_structural_modes": ["Structural Contradiction Brief"],
                        "leading_primary_structural_mode": "Structural Contradiction Brief",
                        "primary_reframed_problem": "Need to distinguish owner-controlled upside from tenant-driven load.",
                        "dominant_structural_conflict": "Regulation vs control boundary",
                        "primary_structural_action": "Compare against structural peers",
                        "primary_structural_action_status": "COMPARE TO PEERS",
                        "gold_nugget_authority_state": "skill_primary",
                        "gold_nugget_source_register": "motor_054.authoritative_gold_nugget_register",
                    },
                    "structural_intelligence_registers": {
                        "system_abstraction": {
                            "asset_type": {"statement": "Commercial office tower", "evidence_state": "OBSERVED_FACT"}
                        },
                        "dominant_variable_register": [{"variable": "tenant_metering", "evidence_state": "CONDITIONAL_HYPOTHESIS"}],
                    },
                }
            },
            "motor_017": {
                "pdf_path": str(pdf_path),
                "pdf_paths": {"en": str(pdf_path)},
                "compilation_status": "success",
                "render_job_id": "rj:test",
                "package_id": "pkg:test",
                "gold_nugget_authority_state": "skill_primary",
                "gold_nugget_source_register": "motor_054.authoritative_gold_nugget_register",
            },
        }
    )

    assert out["delivered"] is True
    manifest = out["delivery_manifest"]
    assert manifest["structural_intelligence_summary"]["dominant_variable_count"] == 4
    assert manifest["governance_summary"]["structural_intelligence_summary"]["cross_layer_conflict_count"] == 2
    assert manifest["structural_output_mode_classifier_table"][0]["recommended_output_mode"] == "Structural Contradiction Brief"
    assert manifest["structural_output_mode_classifier_table"][0]["activation_state"] == "activated_secondary"
    assert manifest["structural_output_mode_summary"]["activated_secondary_modes"] == ["Structural Contradiction Brief"]
    assert manifest["structural_output_mode_summary"]["eligible_primary_modes"] == ["Structural Contradiction Brief"]
    assert manifest["structural_primary_promotion_gate"]["elected_primary_report_type"] == "Structural Contradiction Brief"
    assert manifest["structural_executive_summary"]["primary_structural_action_status"] == "COMPARE TO PEERS"
    assert manifest["structural_executive_summary"]["promotable_primary_structural_modes"] == ["Structural Contradiction Brief"]
    assert manifest["gold_nugget_authority_state"] == "skill_primary"
    assert manifest["gold_nugget_source_register"] == "motor_054.authoritative_gold_nugget_register"
    assert manifest["governance_summary"]["gold_nugget_authority_state"] == "skill_primary"
    assert manifest["governance_summary"]["gold_nugget_source_register"] == "motor_054.authoritative_gold_nugget_register"
    assert manifest["governance_summary"]["structural_executive_summary"]["dominant_structural_conflict"] == "Regulation vs control boundary"
    assert manifest["structural_intelligence_registers"]["system_abstraction"]["asset_type"]["evidence_state"] == "OBSERVED_FACT"


def test_dashboard_ingestion_activity_summarizes_scraping_admissibility(monkeypatch):
    run_d = {
        "target_type_classification": "AMBIGUOUS_TARGET",
        "classification_confidence": "high",
        "asset_identity_status": "ambiguous",
        "target_admissibility_state": "address_candidate_only",
        "technical_substrate_readiness": "insufficient",
        "recommended_report_type": "Target Clarification Brief",
        "report_identity_state": "Target Clarification Brief",
        "report_type_trace": {
            "early_report_type_gate": "Target Clarification Brief",
            "maturity_refined_report_type": "Target Clarification Brief",
            "final_published_report_type": "Target Clarification Brief",
            "report_type_override_reason": "",
        },
        "phase_self_evaluation_summary": {
            "overall_result": "partially_resolved",
            "resolved": 2,
            "total_phases": 9,
        },
        "ingestion_contract_status": "identity_gate_required",
        "subject_gate_passed": False,
        "ingestion_learning_summary": {
            "previous_run_id": "run:prev",
            "net_progress_state": "improved",
            "priority_count": 2,
            "top_priority_action": "request_missing_evidence",
        },
        "case_delta_summary": {
            "progress_signals": ["report_type_upgraded"],
            "regression_signals": [],
        },
        "source_yield_memory_summary": {
            "productive_source_count": 1,
            "sources_evaluated": 2,
        },
        "next_ingestion_priority_update": {
            "priorities": [
                {
                    "priority_rank": 1,
                    "action_type": "request_missing_evidence",
                    "target": "assessor record",
                }
            ]
        },
    }

    outputs = {
        "motor_028": {
            "source_register": [
                {"accepted": True, "scope": "ASSET_LEVEL"},
                {"accepted": False, "scope": "BENCHMARK_LEVEL"},
            ]
        },
        "motor_012": {
            "asset_field_register": [
                {"field": "address", "status": "OBSERVED_PUBLIC_ASSET_LEVEL", "admissibility": "CONFIRMED_ASSET_LEVEL", "scope": "ASSET_LEVEL", "notes": ""},
                {"field": "GFA", "status": "BLOCKING_FIELD", "admissibility": "BLOCKING_FIELD", "scope": "ASSET_LEVEL", "notes": "Gross floor area not observed."},
            ],
            "missing_evidence_register": [
                {
                    "missing_field": "GFA",
                    "minimum_evidence_needed": "assessor record",
                    "suggested_source": "municipal assessor",
                }
            ],
        },
        "motor_014": {
            "missing_evidence_register": [
                {
                    "missing_field": "HVAC type",
                    "minimum_evidence_needed": "system inventory",
                    "suggested_source": "owner / PCA",
                }
            ]
        },
    }

    monkeypatch.setattr(
        dashboard_module,
        "_load_motor_output",
        lambda _run, motor_id: outputs.get(motor_id, {}),
    )

    out = dashboard_module._ingestion_activity(run_d)
    assert out["available"] is True
    assert out["classification"]["recommended_report_type"] == "Target Clarification Brief"
    assert out["classification"]["report_type_trace"]["final_published_report_type"] == "Target Clarification Brief"
    assert out["classification"]["phase_self_evaluation_summary"]["overall_result"] == "partially_resolved"
    assert out["summary"]["sources_total"] == 2
    assert out["summary"]["blocking_fields_total"] == 1
    assert out["summary"]["missing_evidence_total"] == 1
    assert out["blocking_fields"][0]["field"] == "GFA"
    assert out["missing_evidence"][0]["missing_field"] == "HVAC type"
    assert out["learning"]["summary"]["net_progress_state"] == "improved"
    assert out["learning"]["next_ingestion_priority_update"]["priorities"][0]["action_type"] == "request_missing_evidence"


def test_dashboard_api_live_exposes_ingestion_register(monkeypatch):
    fake_run = {
        "run_id": "run:test-ingestion",
        "pipeline_id": "clar-2026",
        "status": "completed",
        "target_type_classification": "AMBIGUOUS_TARGET",
        "classification_confidence": "high",
        "asset_identity_status": "ambiguous",
        "target_admissibility_state": "address_candidate_only",
        "technical_substrate_readiness": "insufficient",
        "recommended_report_type": "Target Clarification Brief",
        "report_type_trace": {
            "early_report_type_gate": "Target Clarification Brief",
            "maturity_refined_report_type": "Target Clarification Brief",
            "final_published_report_type": "Target Clarification Brief",
            "report_type_override_reason": "",
        },
        "phase_self_evaluation_summary": {
            "overall_result": "partially_resolved",
            "resolved": 2,
            "total_phases": 9,
        },
        "previous_run_id": "run:prev",
        "ingestion_learning_summary": {
            "previous_run_id": "run:prev",
            "net_progress_state": "improved",
            "priority_count": 2,
            "top_priority_action": "request_missing_evidence",
        },
        "case_delta_summary": {"net_progress_state": "improved"},
        "source_yield_memory_summary": {"productive_source_count": 1},
        "next_ingestion_priority_update": {"priority_count": 2},
        "ingestion_contract_status": "identity_gate_required",
        "subject_gate_passed": False,
        "motor_results": {},
    }
    fake_active = {
        "run_id": "run:test-ingestion",
        "pipeline_id": "clar-2026",
        "status": "completed",
    }

    monkeypatch.setattr(dashboard_module, "_all_runs", lambda: [fake_active])
    monkeypatch.setattr(dashboard_module, "_select_active_run", lambda runs, requested_run_id="", requested_pipeline_id="": fake_active)
    monkeypatch.setattr(dashboard_module, "_load_run", lambda run_id: fake_run)
    monkeypatch.setattr(dashboard_module, "_run_detail", lambda run_id: {"motors": [], "case_title": "Target Clarification Brief", "summary": {}, "motor_overview": {}})
    monkeypatch.setattr(dashboard_module, "_company_info", lambda raw_run: {})
    monkeypatch.setattr(dashboard_module, "_target_info", lambda raw_run: {"label": "123 TEST ACCESS ROAD, ELKO, NV, 89801"})
    monkeypatch.setattr(dashboard_module, "_research_activity", lambda raw_run: {"summary": {}, "attempts": [], "note": ""})
    monkeypatch.setattr(
        dashboard_module,
        "_ingestion_activity",
        lambda raw_run: {
            "available": True,
            "classification": {"target_type": "AMBIGUOUS_TARGET", "recommended_report_type": "Target Clarification Brief"},
            "summary": {"sources_total": 2, "blocking_fields_total": 1, "missing_evidence_total": 2},
            "learning": {"summary": {"net_progress_state": "improved", "priority_count": 2}},
            "blocking_fields": [{"field": "GFA"}],
            "missing_evidence": [{"missing_field": "HVAC type"}],
        },
    )
    monkeypatch.setattr(dashboard_module, "_focus_activity", lambda raw_run, motors: [])
    monkeypatch.setattr(dashboard_module, "_chart_activity", lambda raw_run: {"status": "completed", "total_charts": 0, "errors": [], "assets": []})
    monkeypatch.setattr(dashboard_module, "_audit_failures", lambda run_id: [])
    monkeypatch.setattr(dashboard_module, "_pdf_for_run", lambda raw_run, allow_global_fallback=False: None)
    monkeypatch.setattr(dashboard_module, "_pdf_variants_for_run", lambda raw_run: {})

    client = dashboard_module.app.test_client()
    response = client.get("/api/live?pipeline_id=clar-2026")
    payload = response.get_json()
    assert response.status_code == 200
    assert payload["pipeline_id"] == "clar-2026"
    assert payload["report_type_trace"]["final_published_report_type"] == "Target Classification Brief"
    assert payload["phase_self_evaluation_summary"]["overall_result"] == "partially_resolved"
    assert payload["ingestion_learning_summary"]["net_progress_state"] == "improved"
    assert payload["previous_run_id"] == "run:prev"
    assert payload["ingestion"]["classification"]["target_type"] == "AMBIGUOUS_TARGET"
    assert payload["ingestion"]["classification"]["recommended_report_type"] == "Target Classification Brief"
    assert payload["ingestion"]["classification"]["recommended_report_type_internal"] == "Target Clarification Brief"
    assert payload["ingestion"]["learning"]["summary"]["priority_count"] == 2
    assert payload["ingestion"]["summary"]["blocking_fields_total"] == 1
