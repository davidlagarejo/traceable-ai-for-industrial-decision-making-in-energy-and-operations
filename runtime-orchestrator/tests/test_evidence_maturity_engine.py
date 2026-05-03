from __future__ import annotations

from runtime_orchestrator.adapters.motor_034 import Motor034Adapter


def _field(
    field: str,
    value,
    *,
    status: str = "OBSERVED",
    scope: str = "ASSET_LEVEL",
    authority_score: str = "high",
    admissibility: str = "CONFIRMED_ASSET_LEVEL",
    source_id: str | None = None,
) -> dict:
    return {
        "field": field,
        "value": value,
        "status": status,
        "source_id": source_id or f"test::{field}",
        "scope": scope,
        "authority_score": authority_score,
        "recency": "current",
        "admissibility": admissibility,
        "notes": "",
    }


def _base_inputs(
    asset_fields: list[dict],
    *,
    target_type: str = "OPERATING_ASSET",
    target_asset_type: str = "commercial_building",
    technical_substrate_readiness: str = "partial",
) -> dict:
    observed_gfa = next(
        (
            row["value"]
            for row in asset_fields
            if row["field"] == "GFA" and row["status"] == "OBSERVED"
        ),
        "",
    )
    return {
        "motor_001": {},
        "motor_007": {
            "target_definition_contract": {
                "address_raw": "350 FIFTH AVENUE, NEW YORK, NY, 10118",
                "jurisdiction_scope": ["US-NY-NYC"],
                "target_type": target_asset_type,
            },
            "target_classification_object": {
                "target_type": target_type,
                "classification_confidence": "high",
            },
            "technical_substrate_readiness": technical_substrate_readiness,
            "recommended_report_type": "Decision-Blocked Asset Brief",
        },
        "motor_008": {},
        "motor_010": {},
        "motor_011": {},
        "motor_012": {
            "asset_field_register": asset_fields,
            "missing_evidence_register": [{"missing_field": "GFA", "minimum_evidence_needed": "Verified GFA record"}]
            if not any(row["field"] == "GFA" and row["status"] == "OBSERVED" for row in asset_fields)
            else [],
            "compliance_applicability_case": {
                "rule_family_record": [{"rule_family_name": "NYC Local Law 97"}],
                "trigger_field_register": [
                    {"field_name": "jurisdiction_codes", "field_state": "observed"},
                    {"field_name": "GFA_sqft", "field_state": "observed" if any(row["field"] == "GFA" and row["status"] == "OBSERVED" for row in asset_fields) else "missing"},
                ],
                "applicability_state": "trigger_partially_supported",
                "compliance_posture_state": "trigger_plausible",
                "screening_basis_register": [
                    {
                        "basis_name": "regulated_floor_area_basis",
                        "basis_value": observed_gfa,
                        "basis_unit": "sqft",
                    },
                    {
                        "basis_name": "ll97_compliance_period",
                        "basis_value": "2024-2029",
                        "basis_unit": "",
                    },
                    {
                        "basis_name": "ll97_penalty_rate",
                        "basis_value": 268,
                        "basis_unit": "USD_per_metric_ton_CO2e",
                    },
                ]
                if observed_gfa
                else [],
            },
        },
        "motor_028": {
            "source_register": [
                {
                    "source_id": "nyc_pluto::350-fifth",
                    "title": "NYC PLUTO",
                    "url": "https://example.test/pluto",
                    "authority_score": "high",
                    "scope": "ASSET_LEVEL",
                    "accepted": True,
                    "source_family": "geospatial_public_record",
                },
                {
                    "source_id": "nyc_ll84::350-fifth",
                    "title": "NYC LL84 benchmarking",
                    "url": "https://example.test/ll84",
                    "authority_score": "high",
                    "scope": "ASSET_LEVEL",
                    "accepted": True,
                    "source_family": "benchmarking_disclosure_record",
                },
            ]
        },
    }


def _find_variable(output: dict, variable_name: str) -> dict:
    return next(row for row in output["variable_maturity_register"] if row["variable_name"] == variable_name)


def _find_claim(output: dict, claim_name: str) -> dict:
    return next(row for row in output["claim_permission_register"] if row["claim_name"] == claim_name)


def _find_decision(output: dict, decision_name: str) -> dict:
    return next(row for row in output["decision_permission_register"] if row["decision_name"] == decision_name)


def _find_cluster(output: dict, cluster_name: str) -> dict:
    return next(row for row in output["cluster_maturity_register"] if row["cluster_name"] == cluster_name)


def test_missing_gfa_blocks_numeric_eui_and_roi():
    adapter = Motor034Adapter()
    out = adapter.run(
        _base_inputs(
            [
                _field("address", "350 FIFTH AVENUE, NEW YORK, NY, 10118"),
                _field("asset_class", "commercial_building"),
                _field("current_EUI", "71", scope="BENCHMARK_LEVEL", authority_score="medium", admissibility="BENCHMARK_ONLY"),
            ],
            technical_substrate_readiness="insufficient",
        )
    )
    gfa = _find_variable(out, "GFA")
    numeric_eui = _find_claim(out, "numeric_eui_claim")
    roi_directional = _find_claim(out, "roi_directional_claim")
    assert gfa["maturity_level"] == 0
    assert numeric_eui["current_permission"] == "prohibited"
    assert roi_directional["current_permission"] == "prohibited"


def test_benchmark_only_eui_allows_screening_but_not_strong_claims():
    adapter = Motor034Adapter()
    out = adapter.run(
        _base_inputs(
            [
                _field("address", "350 FIFTH AVENUE, NEW YORK, NY, 10118"),
                _field("asset_class", "commercial_building"),
                _field("GFA", "250000"),
                _field("current_EUI", "71", scope="BENCHMARK_LEVEL", authority_score="medium", admissibility="BENCHMARK_ONLY"),
            ]
        )
    )
    eui = _find_variable(out, "EUI")
    numeric_eui = _find_claim(out, "numeric_eui_claim")
    energy_savings = _find_claim(out, "energy_savings_claim")
    assert eui["maturity_level"] == 1
    assert numeric_eui["current_permission"] == "conditional"
    assert energy_savings["current_permission"] == "prohibited"
    assert numeric_eui["required_evidence"] == ["PLUTO / assessor GFA", "LL84 or bill-derived baseline"]
    assert "utility_bills" in numeric_eui["dependency_variables"]
    assert "GFA" not in numeric_eui["dependency_variables"]


def test_motor_034_emits_canonical_problem_frame_when_structural_lane_is_active():
    adapter = Motor034Adapter()
    out = adapter.run(
        {
            **_base_inputs(
                [
                    _field("address", "350 FIFTH AVENUE, NEW YORK, NY, 10118"),
                    _field("asset_class", "commercial_building"),
                    _field("GFA", "250000"),
                ]
            ),
            "motor_038": {
                "dominant_variable_register": [
                    {
                        "variable": "tenant_metering",
                        "evidence_state": "CONDITIONAL_HYPOTHESIS",
                    }
                ]
            },
            "motor_040": {
                "cross_layer_conflict_register": [
                    {"conflict": "Regulation vs control boundary"}
                ]
            },
            "motor_041": {
                "problem_framing_register": [
                    {
                        "stated_problem": "Need retrofit decision",
                        "reframed_problem": "Need to distinguish owner-controlled upside from tenant-driven load.",
                    }
                ]
            },
            "motor_046": {
                "minimum_evidence_for_discrimination_register": [
                    {
                        "minimum_evidence": "utility bills + tenant metering map",
                        "source": "operator request",
                        "unlocks": "bounded redesign path",
                    }
                ]
            },
        }
    )

    frame = out["canonical_problem_frame"]
    assert frame["reasoning_path"] == "structural_first"
    assert frame["problem_frame_active"] is True
    assert frame["reframed_problem"] == "Need to distinguish owner-controlled upside from tenant-driven load."
    assert frame["dominant_conflict"] == "Regulation vs control boundary"
    assert frame["dominant_variables"] == ["tenant_metering"]


def test_motor_034_activates_canonical_problem_frame_from_sufficiently_bound_congruence():
    adapter = Motor034Adapter()
    out = adapter.run(
        {
            **_base_inputs(
                [
                    _field("address", "1450 LOGISTICS PARKWAY, JOLIET, IL 60436"),
                    _field("asset_class", "logistics_warehouse"),
                    _field("GFA", "625000"),
                ]
            ),
            "motor_038": {
                "dominant_variable_register": [
                    {
                        "variable": "owner_control_boundary",
                        "evidence_state": "CONDITIONAL_HYPOTHESIS",
                    }
                ]
            },
            "motor_040": {"cross_layer_conflict_register": []},
            "motor_041": {
                "problem_framing_register": [
                    {
                        "stated_problem": "asset_screening",
                        "reframed_problem": "The current question may be premature until dominant variables and structural contradictions are bounded.",
                        "evidence_state": "INADMISSIBLE_CLAIM",
                    }
                ]
            },
            "motor_046": {
                "minimum_evidence_for_discrimination_register": [
                    {
                        "minimum_evidence": "service-level proxy + dock activity profile + charging schedule",
                        "source": "operator request",
                        "unlocks": "fair comparison path",
                    }
                ]
            },
            "motor_049": {
                "local_evidence_binding_register": [
                    {
                        "claim_key": "logistics_service_complexity",
                        "current_local_binding_state": "sufficiently_bound",
                    }
                ]
            },
            "motor_051": {
                "cross_layer_congruence_register": [
                    {
                        "contradiction": "Area benchmark vs service-level complexity",
                        "layers": ["benchmarking", "operation", "logistics"],
                        "strategic_risk": "Area-only benchmarking can target the wrong driver.",
                        "possible_redesign": "Normalize service-level intensity before diagnosing inefficiency.",
                        "evidence_state": "CONDITIONAL_HYPOTHESIS",
                    }
                ],
                "invalid_problem_frame_register": [
                    {
                        "apparent_problem": "high_energy_per_area_means_warehouse_inefficiency",
                        "what_problem_should_be_tested_instead": "Which operational intensity variable defines a fair comparison basis.",
                        "why_invalid_or_premature": "Service-level complexity can dominate the comparison.",
                        "evidence_state": "CONDITIONAL_HYPOTHESIS",
                    }
                ],
            },
        }
    )

    frame = out["canonical_problem_frame"]
    assert frame["reasoning_path"] == "structural_first"
    assert frame["problem_frame_active"] is True
    assert frame["stated_problem"] == "high energy per area means warehouse inefficiency"
    assert frame["reframed_problem"] == "Which operational intensity variable defines a fair comparison basis."
    assert frame["dominant_conflict"] == "Area benchmark vs service-level complexity"
    assert frame["congruence_binding_state"] == "sufficiently_bound"


def test_utility_bills_enable_preliminary_roi_range_when_other_dependencies_exist():
    adapter = Motor034Adapter()
    out = adapter.run(
        _base_inputs(
            [
                _field("address", "350 FIFTH AVENUE, NEW YORK, NY, 10118"),
                _field("asset_class", "commercial_building"),
                _field("GFA", "250000"),
                _field("utility_bills", "12 months utility bills"),
                _field("tariff_class", "SC-8", scope="ASSET_LEVEL", authority_score="medium", admissibility="OBSERVED_PUBLIC_ASSET_LEVEL"),
                _field("operating_schedule", "Mon-Sun 6am-11pm", scope="ASSET_LEVEL", authority_score="medium", admissibility="OBSERVED_PUBLIC_ASSET_LEVEL"),
                _field("HVAC_type", "VAV with central plant", scope="ASSET_LEVEL", authority_score="medium", admissibility="OBSERVED_PUBLIC_ASSET_LEVEL"),
                _field("owner_control_boundary", "Owner controls HVAC/common-area loads", scope="ASSET_LEVEL", authority_score="medium", admissibility="OBSERVED_PUBLIC_ASSET_LEVEL"),
                _field("candidate_measure", "Controls optimization", scope="ASSET_LEVEL", authority_score="medium", admissibility="OBSERVED_PUBLIC_ASSET_LEVEL"),
                _field("CAPEX", "benchmark capex range", scope="BENCHMARK_LEVEL", authority_score="medium", admissibility="BENCHMARK_ONLY"),
            ]
        )
    )
    roi_range = _find_claim(out, "roi_range_claim")
    roi_scenario = _find_claim(out, "roi_scenario_claim")
    assert roi_range["current_permission"] == "allowed"
    assert roi_scenario["current_permission"] == "conditional"


def test_motor_034_does_not_auto_promote_logistics_case_to_full_tdir_on_maturity_alone():
    adapter = Motor034Adapter()
    inputs = _base_inputs(
        [
            _field("address", "1450 LOGISTICS PARKWAY, JOLIET, IL 60436"),
            _field("asset_class", "warehouse_distribution"),
            _field("GFA", "625000"),
            _field("operating_schedule", "24/6"),
            _field("primary_fuel", "electric"),
            _field("HVAC_type", "warehouse_ventilation"),
            _field("jurisdiction", "US-IL"),
        ],
        target_asset_type="warehouse_distribution",
        technical_substrate_readiness="sufficient",
    )
    inputs["motor_007"]["recommended_report_type"] = "Exploratory Prior Brief"
    out = adapter.run(inputs)

    assert out["report_readiness_register"]["report_type_allowed"] == ["Exploratory Prior Brief"]


def test_capex_benchmark_only_keeps_roi_directional_not_finance_grade():
    adapter = Motor034Adapter()
    out = adapter.run(
        _base_inputs(
            [
                _field("address", "350 FIFTH AVENUE, NEW YORK, NY, 10118"),
                _field("asset_class", "commercial_building"),
                _field("GFA", "250000"),
                _field("tariff_class", "SC-8", scope="ASSET_LEVEL", authority_score="medium", admissibility="OBSERVED_PUBLIC_ASSET_LEVEL"),
                _field("candidate_measure", "Lighting retrofit", scope="ASSET_LEVEL", authority_score="medium", admissibility="OBSERVED_PUBLIC_ASSET_LEVEL"),
                _field("CAPEX", "benchmark capex range", scope="BENCHMARK_LEVEL", authority_score="medium", admissibility="BENCHMARK_ONLY"),
            ]
        )
    )
    roi_directional = _find_claim(out, "roi_directional_claim")
    roi_scenario = _find_claim(out, "roi_scenario_claim")
    assert roi_directional["current_permission"] == "allowed"
    assert roi_scenario["current_permission"] == "prohibited"


def test_compliance_trigger_plausible_allows_screening_not_closure():
    adapter = Motor034Adapter()
    out = adapter.run(
        _base_inputs(
            [
                _field("address", "350 FIFTH AVENUE, NEW YORK, NY, 10118"),
                _field("asset_class", "commercial_building"),
                _field("GFA", "250000"),
            ]
        )
    )
    compliance_screening = _find_claim(out, "compliance_screening_claim")
    compliance_closure = _find_claim(out, "compliance_closure_claim")
    assert compliance_screening["current_permission"] in {"allowed", "conditional"}
    assert compliance_closure["current_permission"] == "prohibited"


def test_process_change_without_throughput_blocks_redesign_recommendation():
    adapter = Motor034Adapter()
    out = adapter.run(
        _base_inputs(
            [
                _field("address", "350 FIFTH AVENUE, NEW YORK, NY, 10118"),
                _field("asset_class", "commercial_building"),
                _field("operating_schedule", "24/7", scope="ASSET_LEVEL", authority_score="medium", admissibility="OBSERVED_PUBLIC_ASSET_LEVEL"),
                _field("load_driver", "occupancy and ventilation", scope="ASSET_LEVEL", authority_score="medium", admissibility="OBSERVED_PUBLIC_ASSET_LEVEL"),
                _field("process_flow", "tenant service flow", scope="ASSET_LEVEL", authority_score="medium", admissibility="OBSERVED_PUBLIC_ASSET_LEVEL"),
            ]
        )
    )
    process_redesign_claim = _find_claim(out, "process_redesign_recommendation_claim")
    process_redesign_decision = _find_decision(out, "process_redesign")
    assert process_redesign_claim["current_permission"] == "prohibited"
    assert process_redesign_decision["admissibility_state"] == "deferred"


def test_nyc_public_records_raise_maturity_and_regulatory_screening_strength():
    adapter = Motor034Adapter()
    inputs = _base_inputs(
        [
            _field("address", "350 FIFTH AVENUE, NEW YORK, NY, 10118", source_id="nyc_dof_property_record::350-fifth"),
            _field("asset_class", "commercial_building", source_id="nyc_pluto_property::350-fifth"),
            _field("GFA", "2788222", source_id="nyc_pluto_property::350-fifth"),
            _field("year_built", "1931", source_id="nyc_pluto_property::350-fifth"),
            _field("occupancy_use", "Office", source_id="nyc_pluto_property::350-fifth"),
            _field("current_EUI", "67.4", source_id="nyc_ll84_energy_benchmarking::350-fifth"),
            _field("emissions", "12500", source_id="nyc_ll84_energy_benchmarking::350-fifth"),
            _field("compliance_filings", "LL84 public benchmarking disclosure observed (2024)", source_id="nyc_ll84_energy_benchmarking::350-fifth"),
            _field(
                "HVAC_type",
                "permit clue: HVAC upgrade",
                source_id="nyc_dob_permits::350-fifth",
                authority_score="high",
                admissibility="CONFIRMED_ASSET_LEVEL",
            ),
        ]
    )
    inputs["motor_028"]["dataset_coverage_register"] = [
        {"dataset_key": "nyc_dof_property_record", "status": "accepted", "field_coverage": ["address", "parcel_id"], "notes": "", "matched_sources": ["census_geocoder_validation"]},
        {"dataset_key": "nyc_pluto", "status": "accepted", "field_coverage": ["GFA", "year_built"], "notes": "", "matched_sources": ["nyc_pluto_property"]},
        {"dataset_key": "nyc_dob_permits", "status": "accepted", "field_coverage": ["HVAC_type"], "notes": "", "matched_sources": ["nyc_dob_permits"]},
        {"dataset_key": "nyc_ll84_benchmarking", "status": "accepted", "field_coverage": ["EUI", "emissions"], "notes": "", "matched_sources": ["nyc_ll84_energy_benchmarking"]},
        {"dataset_key": "nyc_ll97_emissions", "status": "screened", "field_coverage": ["penalty_rate", "compliance_period"], "notes": "", "matched_sources": ["nyc_ll84_energy_benchmarking"]},
    ]
    out = adapter.run(inputs)
    assert _find_variable(out, "GFA")["maturity_level"] == 3
    assert _find_variable(out, "EUI")["maturity_level"] == 3
    assert _find_variable(out, "emissions")["maturity_level"] == 3
    assert _find_variable(out, "HVAC_type")["maturity_level"] == 2
    assert _find_variable(out, "regulated_floor_area")["maturity_level"] == 3
    assert _find_variable(out, "regulated_floor_area")["value"] == "2788222"
    assert "whole-building" in str(_find_variable(out, "regulated_floor_area")["uncertainty_reason"]).lower()
    assert _find_variable(out, "applicable_rule_family")["maturity_level"] == 3
    assert _find_variable(out, "benchmarking_requirement")["maturity_level"] == 3
    assert _find_variable(out, "penalty_rate")["maturity_level"] == 3
    assert "268" in str(_find_variable(out, "penalty_rate")["value"])
    assert "2024-2029" in str(_find_variable(out, "compliance_period")["value"])
    assert _find_variable(out, "compliance_filing")["maturity_level"] == 2
    ll97_claim = _find_claim(out, "ll97_penalty_screening_claim")
    compliance_decision = _find_decision(out, "compliance_investment")
    identity_cluster = _find_cluster(out, "identity_cluster")
    geometry_cluster = _find_cluster(out, "geometry_size_cluster")
    regulatory_cluster = _find_cluster(out, "regulatory_cluster")
    systems_cluster = _find_cluster(out, "systems_cluster")
    assert ll97_claim["current_permission"] in {"allowed", "conditional"}
    assert compliance_decision["allowed_action"] == "VALIDATE FIRST"
    assert compliance_decision["current_variable_bottleneck"] == "compliance_filing"
    assert identity_cluster["maturity_level"] == 3
    assert geometry_cluster["maturity_level"] == 3
    assert regulatory_cluster["maturity_level"] == 3
    assert systems_cluster["maturity_level"] in {0, 1, 2}
    assert out["cluster_report_readiness_profile"]["strong_public_screening_possible"] is True
    assert out["report_readiness_register"]["report_type_allowed"] == ["Compliance / Investment Screening Brief"]
    dataset_rows = {row["dataset_key"]: row for row in out["dataset_coverage_register"]}
    assert dataset_rows["nyc_pluto"]["status"] == "accepted"
    assert dataset_rows["nyc_ll97_emissions"]["status"] == "screened"
    assert ll97_claim["required_evidence"] == [
        "LL84/LL97 records",
        "regulated floor area basis",
        "current rule-period threshold",
    ]
    assert "occupancy" in ll97_claim["dependency_variables"]
    classifier_row = out["report_type_classifier_table"][0]
    assert classifier_row["recommended_report_type"] == "Compliance / Investment Screening Brief"
    assert "ll97_penalty_screening_claim" in ", ".join(classifier_row["allowed_claims"])
    canonical = out["canonical_asset_context_summary"]
    assert canonical["canonical_asset_context_state"] == "asset_context_minimal"
    assert canonical["screening_supported"] is True
    assert "geometry_size_cluster" in canonical["supported_clusters"]
    assert "geometry_size_cluster" not in canonical["missing_clusters"]
    assert out["cluster_report_readiness_profile"]["canonical_asset_context_state"] == "asset_context_minimal"
    assert "geometry_size_cluster" in out["maturity_summary"]["canonical_supported_clusters"]


def test_partial_bounded_asset_can_resolve_to_exploratory_prior_brief():
    adapter = Motor034Adapter()
    out = adapter.run(
        _base_inputs(
            [
                _field("address", "2400 INDUSTRY ROAD, TEMPLE, TX, 76504"),
                _field("asset_class", "manufacturing_facility"),
                _field("GFA", "425000"),
                _field("operating_schedule", "3 shifts / 24-6 operation", scope="ASSET_LEVEL", authority_score="medium", admissibility="OBSERVED_PUBLIC_ASSET_LEVEL"),
                _field("primary_fuel", "natural gas", scope="ASSET_LEVEL", authority_score="medium", admissibility="OBSERVED_PUBLIC_ASSET_LEVEL"),
            ],
            target_asset_type="manufacturing_facility",
            technical_substrate_readiness="partial",
        )
    )
    assert out["report_readiness_register"]["report_type_allowed"] == ["Exploratory Prior Brief"]
    classifier_row = out["report_type_classifier_table"][0]
    assert classifier_row["recommended_report_type"] == "Exploratory Prior Brief"


def test_sufficient_technical_substrate_unlocks_full_technical_report():
    adapter = Motor034Adapter()
    out = adapter.run(
        _base_inputs(
            [
                _field("address", "350 FIFTH AVENUE, NEW YORK, NY, 10118"),
                _field("asset_class", "commercial_building"),
                _field("GFA", "2788222"),
                _field("operating_schedule", "Mon-Sun 6am-11pm", scope="ASSET_LEVEL", authority_score="medium", admissibility="OBSERVED_PUBLIC_ASSET_LEVEL"),
                _field("primary_fuel", "electric + steam", scope="ASSET_LEVEL", authority_score="medium", admissibility="OBSERVED_PUBLIC_ASSET_LEVEL"),
                _field("HVAC_type", "central plant VAV", scope="ASSET_LEVEL", authority_score="medium", admissibility="OBSERVED_PUBLIC_ASSET_LEVEL"),
            ],
            technical_substrate_readiness="sufficient",
        )
    )
    assert out["report_readiness_register"]["report_type_allowed"] == ["Full Technical Decision Intelligence Report"]
    classifier_row = out["report_type_classifier_table"][0]
    assert classifier_row["recommended_report_type"] == "Full Technical Decision Intelligence Report"


def test_full_technical_recommendation_is_clamped_to_exploratory_prior_when_maturity_is_still_below_technical_threshold():
    adapter = Motor034Adapter()
    inputs = _base_inputs(
        [
            _field("address", "4100 DISTRIBUTION LOOP, AUSTIN, TX, 78701"),
            _field("asset_class", "logistics_warehouse"),
            _field("GFA", "612000"),
            _field(
                "operating_schedule",
                "24/7 dispatch and handling",
                scope="ASSET_LEVEL",
                authority_score="medium",
                admissibility="OBSERVED_PUBLIC_ASSET_LEVEL",
            ),
        ],
        target_asset_type="logistics_warehouse",
        technical_substrate_readiness="partial",
    )
    inputs["motor_007"]["recommended_report_type"] = "Full Technical Decision Intelligence Report"

    out = adapter.run(inputs)

    assert out["report_readiness_register"]["report_type_allowed"] == ["Exploratory Prior Brief"]
    assert out["report_readiness_register"]["report_type_prohibited"] == ["Full Technical Decision Intelligence Report"]
    classifier_row = out["report_type_classifier_table"][0]
    assert classifier_row["recommended_report_type"] == "Exploratory Prior Brief"


def test_public_asset_specific_ll97_filing_artifact_upgrades_compliance_filing_to_l3():
    adapter = Motor034Adapter()
    inputs = _base_inputs(
        [
            _field("address", "ONE VANDERBILT AVENUE, NEW YORK, NY, 10017", source_id="nyc_dof_property_record::ova"),
            _field("asset_class", "commercial_building", source_id="nyc_pluto_property::ova"),
            _field("GFA", "1678135", source_id="nyc_pluto_property::ova"),
            _field(
                "compliance_filings",
                "Public LL97 filing artifact observed (article_321_submission_candidate: One Vanderbilt Article 321 Submission Package)",
                source_id="nyc_ll97_public_filing_candidate::ova",
            ),
        ]
    )
    inputs["motor_012"]["compliance_applicability_case"]["screening_basis_register"].append(
        {
            "basis_name": "ll97_public_filing_artifact",
            "basis_value": "One Vanderbilt Article 321 Submission Package",
            "basis_unit": "",
        }
    )
    inputs["motor_028"]["dataset_coverage_register"] = [
        {"dataset_key": "nyc_pluto", "status": "accepted", "field_coverage": ["GFA"], "notes": "", "matched_sources": ["nyc_pluto_property"]},
        {"dataset_key": "nyc_ll97_public_filing_artifact", "status": "accepted", "field_coverage": ["compliance_filing"], "notes": "", "matched_sources": ["nyc_ll97_public_filing_candidate"]},
    ]
    out = adapter.run(inputs)
    compliance_filing = _find_variable(out, "compliance_filing")
    assert compliance_filing["maturity_level"] == 3
    assert "public asset-specific ll97 filing artifact" in compliance_filing["uncertainty_reason"].lower()


def test_dob_dataset_acceptance_does_not_upgrade_hvac_without_observed_system_value():
    adapter = Motor034Adapter()
    inputs = _base_inputs(
        [
            _field("address", "ONE VANDERBILT AVENUE, NEW YORK, NY, 10017", source_id="nyc_dof_property_record::one-vanderbilt"),
            _field("asset_class", "commercial_building", source_id="nyc_pluto_property::one-vanderbilt"),
            _field("GFA", "1678135", source_id="nyc_pluto_property::one-vanderbilt"),
            _field(
                "HVAC_type",
                "BLOCKING_FIELD",
                status="BLOCKING_FIELD",
                source_id="nyc_dob_permits::one-vanderbilt",
            ),
        ]
    )
    inputs["motor_028"]["dataset_coverage_register"] = [
        {"dataset_key": "nyc_dof_property_record", "status": "accepted", "field_coverage": ["address"], "notes": "", "matched_sources": ["census_geocoder_validation"]},
        {"dataset_key": "nyc_pluto", "status": "accepted", "field_coverage": ["GFA"], "notes": "", "matched_sources": ["nyc_pluto_property"]},
        {"dataset_key": "nyc_dob_permits", "status": "accepted", "field_coverage": ["HVAC_type"], "notes": "", "matched_sources": ["nyc_dob_permits"]},
    ]
    out = adapter.run(inputs)
    assert _find_variable(out, "HVAC_type")["maturity_level"] == 0


def test_non_nyc_context_filters_ll97_claim_and_uses_generic_compliance_evidence_pack():
    adapter = Motor034Adapter()
    inputs = _base_inputs(
        [
            _field("address", "PIER 1 BAY 1, SAN FRANCISCO, CA, 94111", source_id="sf_assessor_property_record::pier-1"),
            _field("asset_class", "commercial_building", source_id="sf_benchmarking::pier-1"),
            _field("GFA", "250000", source_id="sf_assessor_property_record::pier-1"),
        ],
        target_type="CORPORATE_HEADQUARTERS",
        technical_substrate_readiness="insufficient",
    )
    inputs["motor_007"]["target_definition_contract"]["jurisdiction_scope"] = ["US-CA-SF"]
    inputs["motor_012"]["compliance_applicability_case"] = {
        "rule_family_record": [{"rule_family_name": "San Francisco Existing Commercial Buildings Energy Performance Ordinance"}],
        "trigger_field_register": [{"field_name": "jurisdiction_codes", "field_state": "observed"}],
        "applicability_state": "trigger_partially_supported",
        "compliance_posture_state": "trigger_plausible",
        "screening_basis_register": [],
    }
    inputs["motor_028"]["dataset_coverage_register"] = [
        {"dataset_key": "city_benchmarking_san_francisco", "status": "accepted", "field_coverage": ["EUI"], "notes": "", "matched_sources": ["city_benchmarking_san_francisco"]},
    ]
    out = adapter.run(inputs)
    claim_names = {row["claim_name"] for row in out["claim_permission_register"]}
    assert "ll97_penalty_screening_claim" not in claim_names
    compliance_decision = _find_decision(out, "compliance_investment")
    assert all("LL97" not in item for item in compliance_decision["evidence_needed"])
