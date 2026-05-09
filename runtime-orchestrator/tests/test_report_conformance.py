from runtime_orchestrator.asset_contracts import _derive_target_id
from runtime_orchestrator.adapters.motor_012 import _build_asset_energy_behavior_prior
from runtime_orchestrator.adapters.motor_014 import (
    _build_financial_exposure_register,
    _build_decision_front_register,
    _build_minimum_evidence_unlock_map,
    _build_scenario_space,
)
from runtime_orchestrator.adapters.motor_015 import Motor015Adapter
from runtime_orchestrator.adapters.motor_016 import (
    Motor016Adapter,
    _apply_section_inventory_surface_gate,
    _apply_section_surface_density_gate,
    _apply_section_strategic_redundancy_gate,
    _apply_section_strategic_surface_gate,
    _apply_support_chart_lane_visibility_cap,
    _build_case_adaptation_memo,
    _disambiguate_appendix_titles_against_body,
    _order_section_chart_records,
    _prioritize_body_sections_by_outline,
    _resolve_chart_visibility_section_hint,
    _resolve_support_chart_lane_curation_entry,
    _build_structural_primary_body_sections,
    _build_source_family_coverage_table as _enrich_source_family_coverage_table,
    _content_integrity_scan,
    _sanitize_visible_text,
    _visible_document_label,
)
from runtime_orchestrator.adapters.motor_017 import (
    _chapter_tex,
    _frontpage_tex,
    _hydrated_system_consistency_section,
    _localize_document_type,
    _validate_render_section_contract,
)
from runtime_orchestrator.adapters.motor_028 import _build_requestable_evidence_items
from runtime_orchestrator.render_section_contract import resolve_render_section_contract
from runtime_orchestrator.render_section_contract import get_support_chart_lane_curation_policy
from runtime_orchestrator.render_section_contract import get_support_chart_lane_visibility_policy
from runtime_orchestrator.render_section_contract import get_support_chart_visibility_policy


def test_content_integrity_scan_flags_non_building_legacy_tokens():
    sections = [
        {
            "section_id": "c7",
            "title": "TAD — Decision-Admissibility Layer",
            "llm_text": "Lease extension and strategic re-letting are plausible next steps.",
            "llm_text_en": "",
            "llm_text_es": "",
            "blocks": [{"block_id": "b1", "content": "Anchor tenant concentration remains open."}],
        }
    ]
    target_definition = {
        "target_identifier": "901 MAIN AVENUE, NORWALK, CT, 06851-1168",
        "target_type": "industrial_plant",
        "jurisdiction_scope": ["US-CT"],
    }
    scan = _content_integrity_scan(sections, target_definition, "GENERAL ELECTRIC", "GE")
    issue_codes = {issue["issue_code"] for issue in scan["issues"]}
    assert not scan["render_eligible"]
    assert "legacy_building_leasing_semantics" in issue_codes
    assert "legacy_building_anchor_tenant_semantics" in issue_codes


def test_sanitize_visible_text_normalizes_empty_field_markers():
    raw = (
        "Shares Outstanding: N/A | Primary Fuel: UNSPECIFIED | Landmark: Not confirmed | "
        "Area: 0 sqft | Legacy: TDIR | Old Label: Operational Decision Intelligence Report"
    )
    sanitized = _sanitize_visible_text(raw)
    assert "N/A" not in sanitized
    assert "UNSPECIFIED" not in sanitized
    assert "Not confirmed" not in sanitized
    assert "0 sqft" not in sanitized
    assert "TDIR" not in sanitized
    assert "Operational Decision Intelligence Report" not in sanitized
    assert "NOT OBSERVED" in sanitized
    assert "BLOCKING IF USED" in sanitized


def test_visible_output_taxonomy_uses_only_canonical_labels():
    assert _visible_document_label("Entity Address Classification Brief", "Entity Address Classification Brief") == "Target Classification Brief"
    assert _visible_document_label("Target Clarification Brief", "Target Clarification Brief") == "Target Classification Brief"
    assert _visible_document_label("Issuer Context Memo", "Issuer Context Memo") == "Target Classification Brief"
    assert _localize_document_type("Target Clarification Brief", "es") == "Informe de Clasificación del Objetivo"


def test_content_integrity_scan_avoids_short_ticker_false_positive_inside_words():
    sections = [
        {
            "section_id": "c5",
            "title": "Minimum Evidence Pack",
            "llm_text": "The evidence needed next is a metering basis and process boundary map.",
            "llm_text_en": "",
            "llm_text_es": "",
            "blocks": [{"block_id": "b1", "content": "Evidence needed before decision advance."}],
        }
    ]
    target_definition = {
        "target_identifier": "901 MAIN AVENUE, NORWALK, CT, 06851-1168",
        "target_type": "industrial_plant",
        "jurisdiction_scope": ["US-CT"],
    }
    scan = _content_integrity_scan(sections, target_definition, "GENERAL ELECTRIC", "GE")
    issue_codes = {issue["issue_code"] for issue in scan["issues"]}
    assert "legacy_nee_reference" not in issue_codes


def test_content_integrity_scan_flags_tdir_legacy_token():
    sections = [
        {
            "section_id": "c1",
            "title": "Executive Decision-Admissibility Brief",
            "llm_text": "This case should be treated as a TDIR Preliminary despite missing evidence.",
            "llm_text_en": "",
            "llm_text_es": "",
            "blocks": [{"block_id": "b1", "content": "Legacy label: TDIR"}],
        }
    ]
    target_definition = {
        "target_identifier": "2500 SOUTH DAMEN AVENUE, CHICAGO, IL, 60608",
        "target_type": "cold_chain_facility",
        "jurisdiction_scope": ["US-IL"],
    }
    scan = _content_integrity_scan(sections, target_definition, "", "")
    issue_codes = {issue["issue_code"] for issue in scan["issues"]}
    assert not scan["render_eligible"]
    assert "legacy_tdir_reference" in issue_codes


def test_content_integrity_scan_flags_internal_render_scaffolding():
    sections = [
        {
            "section_id": "c6",
            "title": "[C6] Tension Map",
            "llm_text": "Reader takeaway: this section should guide the reader.",
            "llm_text_en": "",
            "llm_text_es": "",
            "blocks": [{"block_id": "b1", "content": "Technical Reference Data | Epistemic marker: INFERRED"}],
        }
    ]
    target_definition = {
        "target_identifier": "ONE VANDERBILT AVENUE, NEW YORK, NY, 10017",
        "target_type": "commercial_building",
        "jurisdiction_scope": ["US-NY-NYC", "US-NY"],
    }
    scan = _content_integrity_scan(sections, target_definition, "SL GREEN REALTY CORP", "SLG")
    issue_codes = {issue["issue_code"] for issue in scan["issues"]}
    assert not scan["render_eligible"]
    assert "instruction_leakage_reader_takeaway" in issue_codes
    assert "instruction_leakage_technical_reference_data" in issue_codes
    assert "instruction_leakage_epistemic_marker" in issue_codes
    assert "instruction_leakage_chapter_marker" in issue_codes


def test_content_integrity_scan_does_not_flag_valid_threshold_values_ending_in_zero_sqft():
    sections = [
        {
            "section_id": "c5",
            "title": "Regulatory / Normative Screening",
            "llm_text": "",
            "llm_text_en": "",
            "llm_text_es": "",
            "blocks": [
                {
                    "block_id": "b1",
                    "content": (
                        "The building exceeds the typical 25,000 sqft threshold. "
                        "Observed GFA is 1,678,135 sqft."
                    ),
                }
            ],
        }
    ]
    target_definition = {
        "target_identifier": "ONE VANDERBILT AVENUE, NEW YORK, NY, 10017",
        "target_type": "commercial_building",
        "jurisdiction_scope": ["US-NY-NYC", "US-NY"],
    }
    scan = _content_integrity_scan(sections, target_definition, "", "")
    issue_codes = {issue["issue_code"] for issue in scan["issues"]}
    assert scan["render_eligible"]
    assert "invalid_zero_gfa" not in issue_codes


def test_chapter_tex_omits_internal_scaffolding_labels_from_client_render():
    tex = _chapter_tex(
        {
            "title": "Tension Map",
            "llm_text": "Conditional scenario framing remains bounded.",
            "blocks": [{"content": "Assumption: bounded technical reading only."}],
            "epistemic_marker": "INFERRED",
            "section_type": "body",
            "chapter_id": "C6",
            "chart_assets": [
                {
                    "title": "Scenario Space",
                    "description": "Conditional futures only.",
                    "epistemic_marker": "CONDITIONAL",
                    "support_state": "screening_grade",
                    "reader_takeaway": "This should never leak.",
                }
            ],
        },
        "C6",
        chart_png_rel="Figures/Charts/c6_test.png",
        language="en",
    )
    assert "Epistemic marker" not in tex
    assert "Reader takeaway" not in tex
    assert "Technical Reference Data" not in tex
    assert "[C6]" not in tex


def test_requestable_evidence_items_food_processing_are_family_specific():
    items = _build_requestable_evidence_items(
        ctx={
            "asset_context_readiness": {"state": "asset_context_insufficient"},
            "state_code": "CA",
            "city": "OAKLAND",
        },
        target_definition={"target_type": "food_processing_facility"},
        benchmark_route={"route_class": "industrial_process_reference"},
        attempts=[],
        gaps=[],
    )
    evidence = [row["evidence_item"] for row in items]
    assert any("Wastewater / pretreatment profile" in row for row in evidence)
    assert any("ammonia / CO2 safety basis" in row for row in evidence)


def test_requestable_evidence_items_cold_chain_are_family_specific():
    items = _build_requestable_evidence_items(
        ctx={
            "asset_context_readiness": {"state": "asset_context_insufficient"},
            "state_code": "IL",
            "city": "CHICAGO",
        },
        target_definition={"target_type": "cold_chain_facility"},
        benchmark_route={"route_class": "industrial_process_reference"},
        attempts=[],
        gaps=[],
    )
    evidence = [row["evidence_item"] for row in items]
    assert any("Refrigerant charge inventory" in row for row in evidence)
    assert any("Temperature-zone map" in row for row in evidence)


def test_requestable_evidence_items_manufacturing_are_process_specific():
    items = _build_requestable_evidence_items(
        ctx={
            "asset_context_readiness": {"state": "asset_context_insufficient"},
            "state_code": "TX",
            "city": "TEMPLE",
        },
        target_definition={"target_type": "manufacturing_facility"},
        benchmark_route={"route_class": "industrial_process_reference"},
        attempts=[],
        gaps=[],
    )
    evidence = [row["evidence_item"] for row in items]
    assert any("NAICS / SIC classification" in row for row in evidence)
    assert any("resin / adhesive systems" in row for row in evidence)
    assert any("VOC capture / abatement basis" in row for row in evidence)
    assert any("Steam / boilers / thermal oil / hot-water basis" in row for row in evidence)
    assert any("Air, wastewater, and emissions permit basis" in row for row in evidence)


def test_requestable_evidence_items_commercial_building_include_metering_and_central_plant():
    items = _build_requestable_evidence_items(
        ctx={
            "asset_context_readiness": {"state": "asset_context_insufficient"},
            "state_code": "NY",
            "city": "NEW YORK",
        },
        target_definition={"target_type": "commercial_building"},
        benchmark_route={"route_class": "local_benchmarking"},
        attempts=[],
        gaps=[],
    )
    evidence = [row["evidence_item"] for row in items]
    assert any("occupancy / use mix" in row for row in evidence)
    assert any("Central plant, HVAC topology" in row for row in evidence)
    assert any("Tenant metering basis, lease responsibility matrix" in row for row in evidence)
    assert any("Steam, gas, district energy, or electrification basis" in row for row in evidence)


def test_asset_energy_behavior_prior_oil_gas_downstream_has_subtype_depth():
    prior = _build_asset_energy_behavior_prior(
        {"target_type": "oil_gas_downstream_facility"},
        {"adjusted_EUI_estimate_kBtu_sqft": None, "benchmark_source": "process_reference"},
        {"climate_zone_ASHRAE": "2A", "heating_dominated": False, "cooling_dominated": True},
        {},
    )
    assert "steam_balance_loss" in prior["anomaly_candidates"]
    assert "fired_heater_basis" in prior["critical_evidence_drivers"]


def test_asset_energy_behavior_prior_manufacturing_has_laminate_process_depth():
    prior = _build_asset_energy_behavior_prior(
        {"target_type": "manufacturing_facility"},
        {"adjusted_EUI_estimate_kBtu_sqft": None, "benchmark_source": "process_reference"},
        {"climate_zone_ASHRAE": "2A", "heating_dominated": False, "cooling_dominated": True},
        {},
    )
    assert "resin_or_press_thermal_drift" in prior["anomaly_candidates"]
    assert "dust_collection_and_voc_capture" in prior["critical_evidence_drivers"]
    assert "naics_sic_process_family" in prior["critical_evidence_drivers"]


def test_asset_energy_behavior_prior_commercial_building_has_office_tower_depth():
    prior = _build_asset_energy_behavior_prior(
        {"target_type": "commercial_building"},
        {"adjusted_EUI_estimate_kBtu_sqft": None, "benchmark_source": "local_benchmarking"},
        {"climate_zone_ASHRAE": "4A", "heating_dominated": True, "cooling_dominated": False},
        {},
    )
    assert "tenant_metering_blind_spot" in prior["anomaly_candidates"]
    assert "lease_responsibility_matrix" in prior["critical_evidence_drivers"]
    assert "steam_gas_electrification_basis" in prior["critical_evidence_drivers"]


def test_financial_exposure_register_building_has_central_plant_and_metering_depth():
    register = _build_financial_exposure_register(
        "commercial_building",
        ["ll97_screening"],
        [
            {"evidence_item": "12–24 months of utility bills, interval data if available, and meter map"},
            {"evidence_item": "Central plant, HVAC topology, BMS / EMS basis, and major electrical distribution inventory"},
            {"evidence_item": "Tenant metering basis, lease responsibility matrix, and owner-versus-tenant control boundary"},
            {"evidence_item": "Steam, gas, district energy, or electrification basis by major building system"},
            {"evidence_item": "Verified GFA / rentable area"},
            {"evidence_item": "Operating schedule, occupancy / use mix, and after-hours tenant profile"},
        ],
        [
            {"decision_front": "Acquisition underwriting with energy upside"},
            {"decision_front": "Energy retrofit CAPEX"},
            {"decision_front": "Compliance investment"},
        ],
    )
    text = " ".join(row["assumption"] + " " + row["evidence_needed"] for row in register)
    lowered = text.lower()
    assert "central plant" in lowered
    assert "tenant metering" in lowered
    assert "electrification" in lowered


def test_scenario_space_manufacturing_has_process_and_permit_depth():
    scenarios = _build_scenario_space(
        asset_name="Wilsonart Temple North Laminate Facility",
        missing_clusters=["systems_cluster", "fuel_energy_cluster"],
        regulatory_flags=["tceq_permit"],
        target_type="manufacturing_facility",
        decision_front_register=[
            {"decision_front": "Process efficiency or utility-support CAPEX"},
            {"decision_front": "Utility cost optimization"},
            {"decision_front": "Environmental or permit-driven investment"},
            {"decision_front": "Operator evidence request"},
        ],
        minimum_evidence_unlock_map=[
            {"evidence_item": "NAICS / SIC classification, product family, and process narrative by major line"},
            {"evidence_item": "Presses, resin / adhesive systems, curing or thermal-process map, and major thermal duty by line"},
            {"evidence_item": "Compressed-air topology, dust collection, and VOC capture / abatement basis"},
            {"evidence_item": "Air, wastewater, and emissions permit basis by line, utility island, or process area"},
        ],
    )
    text = " ".join(
        row["scenario"] + " " + row["what_would_make_it_true"] + " " + row["evidence_needed"]
        for row in scenarios
    )
    lowered = text.lower()
    assert "resin" in lowered
    assert "curing" in lowered
    assert "voc" in lowered
    assert "wastewater" in lowered


def test_visible_document_label_switches_to_gtm_blocked_brief():
    assert _visible_document_label("Address Candidate Brief") == "Decision-Blocked Asset Brief"
    assert _visible_document_label("Asset Context Insufficiency Brief") == "Decision-Blocked Asset Brief"
    assert _visible_document_label("Technical Decision Intelligence Report") == "Asset Decision-Admissibility Brief"
    assert _visible_document_label(
        "Decision-Blocked Asset Brief",
        "Compliance / Investment Screening Brief",
    ) == "Compliance / Investment Screening Brief"


def test_target_id_preserves_full_long_family_slug():
    target_id = _derive_target_id(
        "address_candidate",
        "oil_gas_midstream_facility",
        "10777-clay-road-houston-tx-77041",
    )
    assert target_id.startswith("addr-oil-gas-midstream-facility-")

    downstream_target_id = _derive_target_id(
        "address_candidate",
        "oil_gas_downstream_facility",
        "5900-highway-225-deer-park-tx-77536",
    )
    assert downstream_target_id.startswith("addr-oil-gas-downstream-facility-")


def test_frontpage_tex_uses_product_language_without_legacy_defaults():
    meta = {
        "case_id": "ZLab-addr-oil-gas-midstream-facility-10777-clay-road-houston-tx-77041-2026",
        "case_title": "10777 CLAY ROAD, HOUSTON, TX, 77041",
        "document_type": "Decision-Blocked Asset Brief",
        "document_type_es": "Informe de Activo con Decisión Bloqueada",
        "case_subtitle": "Minimum Evidence Required Before Technical or Capital Decisions",
        "case_subtitle_es": "Evidencia mínima requerida antes de decisiones técnicas o de capital",
        "decision_state": "ASSET NOT DECISION-READY",
        "decision_state_es": "ESTADO EPISTÉMICO: ACTIVO TODAVÍA NO LISTO PARA DECISIÓN",
        "main_warning": "The current subject is still only an address candidate.",
        "main_warning_es": "El sujeto actual sigue siendo solo un candidato por dirección.",
        "allowed_use": ["evidence request", "validation sequencing"],
        "allowed_use_es": ["solicitud de evidencia", "secuenciación de validación"],
        "prohibited_use": ["investment recommendation", "savings estimate"],
        "prohibited_use_es": ["recomendación de inversión", "estimación de ahorros"],
        "publication_ceiling": "publish_with_degradation",
        "produced_at": "2026-04-27T12:00:00+00:00",
    }
    frontpage = _frontpage_tex(meta, language="en")
    assert "Decision-Blocked Asset Brief" in frontpage
    assert "Operational Decision Intelligence Report" not in frontpage
    assert "investment recommendation; savings estimate" in frontpage

    frontpage_es = _frontpage_tex(meta, language="es")
    assert "Informe de Activo con Decisión Bloqueada" in frontpage_es
    assert "Publicación con degradación" in frontpage_es
    assert "El sujeto actual sigue siendo solo un candidato por dirección." in frontpage_es
    assert "Decision-Blocked Asset Brief" not in frontpage_es
    assert "Publish With Degradation" not in frontpage_es


def test_decision_front_register_hardens_when_subject_not_bounded():
    fronts = _build_decision_front_register(
        asset_name="901 MAIN AVENUE, NORWALK, CT",
        conflict_register=[{"inference_case_id": "LC-ASSET-01"}],
        validation_queue=[{"validation_requirement": "Address-to-asset confirmation + minimum evidence pack"}],
        missing_clusters=["geometry_size_cluster", "systems_cluster"],
        regulatory_flags=["state_permit"],
        target_type="industrial_plant",
        target_admissibility_state="address_candidate_only",
        subject_gate_passed=False,
    )
    assert fronts[0]["decision_front"] == "Asset identity and admissibility confirmation"
    assert fronts[0]["current_status"] == "ACT NOW"
    assert any(
        front["decision_front"] == "Process efficiency or utility-support CAPEX"
        and front["current_status"] == "NO-GO"
        for front in fronts
    )


def test_source_family_coverage_table_does_not_overclaim_identity_only_support():
    rows = _enrich_source_family_coverage_table(
        [
            {
                "source_family": "nyc_dof_property_record",
                "source_name": "NYC DOF property record",
                "priority": "mandatory",
                "queried": True,
                "found": True,
                "authority": "high",
                "scope": "ASSET_LEVEL",
                "fields_expected": ["address", "parcel_id", "GFA"],
                "matched_source_types": ["nyc_dof_property_record"],
            }
        ],
        [
            {
                "field": "address",
                "source_id": "nyc_dof_property_record::ova",
                "status": "OBSERVED",
                "identity_supported": True,
                "physical_substrate_supported": False,
                "operating_substrate_supported": False,
                "regulatory_supported": False,
            },
            {
                "field": "parcel_id",
                "source_id": "nyc_dof_property_record::ova",
                "status": "OBSERVED",
                "identity_supported": True,
                "physical_substrate_supported": False,
                "operating_substrate_supported": False,
                "regulatory_supported": False,
            },
        ],
    )
    row = rows[0]
    assert row["fields_extracted"] == ["address", "parcel_id"]
    assert row["missing"] == ["GFA"]
    assert row["support_note"] == "Source confirms identity only, not physical operating substrate."


def test_case_adaptation_memo_flags_template_clone_against_comparable_reference():
    memo = _build_case_adaptation_memo(
        target_definition={
            "target_type": "commercial_building",
            "target_name": "500 MADISON AVENUE",
            "address_raw": "500 MADISON AVENUE, NEW YORK, NY 10022",
        },
        jurisdiction_resolution={
            "state": "NY",
            "city": "New York",
            "utility": "ConEd",
            "regulatory_stack": ["LL84", "LL97"],
        },
        source_register=[
            {"accepted": True, "source_name": "nyc_dof_property_record"},
            {"accepted": True, "source_name": "nyc_pluto_property"},
            {"accepted": True, "source_name": "nyc_ll84_energy_benchmarking"},
            {"accepted": True, "source_name": "nyc_dob_permits"},
            {"accepted": True, "source_name": "nyc_ll97_covered_buildings_list"},
        ],
        cluster_maturity_register=[
            {"cluster": "identity_cluster", "level": 3},
            {"cluster": "geometry_size_cluster", "level": 3},
            {"cluster": "regulatory_cluster", "level": 3},
            {"cluster": "systems_cluster", "level": 0},
            {"cluster": "control_boundary_cluster", "level": 0},
        ],
        decision_front_register=[
            {"decision_front": "Acquisition underwriting with energy upside", "current_status": "DEFER"},
            {"decision_front": "Energy retrofit CAPEX", "current_status": "DEFER"},
            {"decision_front": "Compliance investment", "current_status": "VALIDATE FIRST"},
            {"decision_front": "Seller/operator evidence request", "current_status": "ACT NOW"},
        ],
        scenario_space=[
            {
                "scenario": "Public building evidence supports screening-grade compliance posture but not closure.",
                "financial_meaning": "Compliance screening is possible, but capital closure is not.",
            }
        ],
        report_readiness_register={
            "report_type_allowed": ["Compliance / Investment Screening Brief"],
            "reason": "Strong public building evidence supports screening-grade use.",
        },
        variable_bottleneck_register=[{"variable_name": "control_boundary_cluster"}],
    )
    assert memo["comparison_summary"]["reference_count"] >= 1
    assert memo["comparison_summary"]["closest_reference_key"] == "one_vanderbilt_nyc_screening"
    assert memo["template_contamination_failure"] is True
    assert any("too close to comparable reference" in reason.lower() for reason in memo["failure_reasons"])


def test_case_adaptation_memo_tracks_structural_diversity_when_case_is_not_flat():
    memo = _build_case_adaptation_memo(
        target_definition={
            "target_type": "warehouse_distribution",
            "target_name": "Sunrise Logistics Hub",
            "address_raw": "1450 LOGISTICS PARKWAY, DALLAS, TX 75201",
        },
        jurisdiction_resolution={
            "state": "TX",
            "city": "Dallas",
            "utility": "Oncor",
            "regulatory_stack": ["local utility tariff", "fire / refrigeration review"],
        },
        source_register=[
            {"accepted": True, "source_name": "county_assessor_property_record"},
            {"accepted": True, "source_name": "utility_tariff_sheet"},
            {"accepted": True, "source_name": "benchmarking_or_disclosure_context"},
        ],
        cluster_maturity_register=[
            {"cluster": "identity_cluster", "level": 3},
            {"cluster": "geometry_size_cluster", "level": 3},
            {"cluster": "control_boundary_cluster", "level": 0},
            {"cluster": "operating_regime_cluster", "level": 0},
        ],
        decision_front_register=[
            {"decision_front": "Tariff optimization", "current_status": "VALIDATE FIRST"},
            {"decision_front": "Operator evidence request", "current_status": "ACT NOW"},
            {"decision_front": "Retrofit CAPEX", "current_status": "DEFER"},
        ],
        scenario_space=[
            {
                "scenario": "Charging windows drive peak-demand economics.",
                "financial_meaning": "Tariff orchestration may matter more than generic EUI logic.",
            },
            {
                "scenario": "Dock exchange dominates thermal behavior.",
                "financial_meaning": "HVAC retrofit may attack the wrong variable.",
            },
        ],
        report_readiness_register={
            "report_type_allowed": ["Exploratory Prior Brief"],
            "reason": "Case is strong enough for bounded strategic interpretation but not local closure.",
        },
        variable_bottleneck_register=[
            {"variable_name": "charging_window_concentration"},
            {"variable_name": "dock_thermal_exchange"},
        ],
    )

    assert memo["diversity_failure"] is False
    assert memo["diversity_score"] >= memo["diversity_target_score"]
    by_dimension = {row["dimension"]: row for row in memo["diversity_register"]}
    assert by_dimension["decision_front_diversity"]["passes"] is True
    assert by_dimension["scenario_tension_diversity"]["passes"] is True
    assert any(row["dimension"] == "structural_diversity" for row in memo["rows"])


def test_case_adaptation_memo_flags_flat_structural_diversity_even_without_reference_clone():
    memo = _build_case_adaptation_memo(
        target_definition={
            "target_type": "warehouse_distribution",
            "target_name": "Sparse Logistics Box",
            "address_raw": "1 BOX ROAD, EL PASO, TX 79901",
        },
        jurisdiction_resolution={
            "state": "TX",
            "city": "El Paso",
            "utility": "",
            "regulatory_stack": [],
        },
        source_register=[
            {"accepted": True, "source_name": "county_assessor_property_record"},
        ],
        cluster_maturity_register=[
            {"cluster": "identity_cluster", "level": 3},
        ],
        decision_front_register=[
            {"decision_front": "Operator evidence request", "current_status": "ACT NOW"},
        ],
        scenario_space=[
            {
                "scenario": "Evidence remains too thin to discriminate the case.",
                "financial_meaning": "",
            }
        ],
        report_readiness_register={
            "report_type_allowed": ["Target Classification Brief"],
            "reason": "Too little evidence for structural differentiation.",
        },
        variable_bottleneck_register=[],
    )

    assert memo["diversity_failure"] is True
    assert memo["template_contamination_failure"] is True
    assert memo["diversity_score"] < memo["diversity_target_score"]
    assert any("structural diversity" in reason.lower() for reason in memo["failure_reasons"])


def test_decision_front_register_oil_gas_uses_family_specific_fronts():
    fronts = _build_decision_front_register(
        asset_name="5900 HIGHWAY 225, DEER PARK, TX",
        conflict_register=[],
        validation_queue=[{"validation_requirement": "Unit inventory + fuel / emissions basis"}],
        missing_clusters=["systems_cluster"],
        regulatory_flags=["air_permit"],
        target_type="oil_gas_downstream_facility",
        target_admissibility_state="bounded_asset",
        subject_gate_passed=True,
    )
    names = [front["decision_front"] for front in fronts]
    assert "Process, emissions, or efficiency CAPEX" in names
    assert "Permit, compliance, or transition investment" in names


def test_decision_front_register_manufacturing_adds_process_redesign_and_utility_cost_optimization():
    fronts = _build_decision_front_register(
        asset_name="WILSONART TEMPLE NORTH LAMINATE FACILITY",
        conflict_register=[],
        validation_queue=[{"validation_requirement": "Process inventory + utility / fuel profile + throughput data"}],
        missing_clusters=["systems_cluster", "fuel_energy_cluster", "operating_regime_cluster"],
        regulatory_flags=["tceq_air_permit"],
        target_type="manufacturing_facility",
        target_admissibility_state="bounded_asset",
        subject_gate_passed=True,
    )
    by_name = {front["decision_front"]: front for front in fronts}
    assert "Process redesign" in by_name
    assert "Utility cost optimization" in by_name
    assert by_name["Process redesign"]["current_status"] == "NO-GO"
    assert by_name["Utility cost optimization"]["current_status"] == "VALIDATE FIRST"
    assert by_name["Operator evidence request"]["current_status"] == "ACT NOW"
    assert "Do not commit utility-cost optimization claims" in by_name["Utility cost optimization"]["prohibited_action"]


def test_minimum_evidence_unlock_map_dedupes_semantic_manufacturing_duplicates():
    rows = _build_minimum_evidence_unlock_map(
        validation_queue=[
            {
                "case_id": "LC-ASSET-01",
                "case_name": "Asset Technical Insufficiency and Scope Mismatch",
                "validation_requirement": "Process line inventory and major energy-using equipment list",
                "validation_urgency_score": 0.97,
            },
            {
                "case_id": "LC-ASSET-01",
                "case_name": "Asset Technical Insufficiency and Scope Mismatch",
                "validation_requirement": "Shift schedule, production calendar, and throughput profile",
                "validation_urgency_score": 0.97,
            },
        ],
        inference_records=[
            {"case_id": "LC-ASSET-01", "case_name": "Asset Technical Insufficiency and Scope Mismatch"},
        ],
        missing_clusters=["systems_cluster", "operating_regime_cluster"],
        minimum_evidence_seed=[
            {
                "evidence_item": "Process line, utility, and controls system inventory",
                "source": "Plant engineering",
                "why_needed": "Defines process systems",
                "cases_resolved": ["LC-ASSET-01"],
                "effort": "CRITICAL",
                "decision_unlock": "Unlocks process-level technical reading.",
            },
            {
                "evidence_item": "Shift schedule, throughput profile, and maintenance / sanitation cycle",
                "source": "Plant operations",
                "why_needed": "Defines operating profile",
                "cases_resolved": ["LC-ASSET-01"],
                "effort": "CRITICAL",
                "decision_unlock": "Unlocks scenario discrimination.",
            },
        ],
        target_type="manufacturing_facility",
    )
    evidence_items = [row["evidence_item"] for row in rows]
    assert len(evidence_items) == len(set(evidence_items))
    assert sum("Process line" in item for item in evidence_items) == 1
    assert sum("Shift schedule" in item for item in evidence_items) == 1


def test_minimum_evidence_unlock_map_merges_unlock_equivalent_utility_rows():
    rows = _build_minimum_evidence_unlock_map(
        validation_queue=[
            {
                "case_id": "LC-REG-01",
                "case_name": "Compliance basis remains screening-grade",
                "validation_requirement": "12–24 months of utility bills and fuel profile",
                "validation_urgency_score": 0.91,
            },
            {
                "case_id": "LC-MKT-02",
                "case_name": "Economics remain unbounded",
                "validation_requirement": "Metering records and utility / fuel records",
                "validation_urgency_score": 0.89,
            },
        ],
        inference_records=[
            {"case_id": "LC-REG-01", "case_name": "Compliance basis remains screening-grade"},
            {"case_id": "LC-MKT-02", "case_name": "Economics remain unbounded"},
        ],
        missing_clusters=["fuel_energy_cluster"],
        minimum_evidence_seed=[],
        target_type="commercial_building",
    )
    utility_rows = [row for row in rows if "utility" in row["evidence_item"].lower() or "fuel" in row["evidence_item"].lower()]
    assert len(utility_rows) == 1
    assert utility_rows[0]["effort"] == "CRITICAL"
    assert "LC-REG-01" in utility_rows[0]["cases_resolved"]
    assert "LC-MKT-02" in utility_rows[0]["cases_resolved"]


def test_scenario_space_and_financial_exposure_are_linked_for_manufacturing():
    fronts = _build_decision_front_register(
        asset_name="WILSONART TEMPLE NORTH LAMINATE FACILITY",
        conflict_register=[],
        validation_queue=[{"validation_requirement": "Process inventory + utility / fuel profile + throughput data"}],
        missing_clusters=["systems_cluster", "fuel_energy_cluster", "operating_regime_cluster"],
        regulatory_flags=["tceq_air_permit"],
        target_type="manufacturing_facility",
        target_admissibility_state="bounded_asset",
        subject_gate_passed=True,
    )
    evidence = _build_minimum_evidence_unlock_map(
        validation_queue=[
            {
                "case_id": "LC-ASSET-01",
                "case_name": "Asset Technical Insufficiency and Scope Mismatch",
                "validation_requirement": "Process line inventory and major energy-using equipment list",
                "validation_urgency_score": 0.97,
            },
            {
                "case_id": "LC-OPS-02",
                "case_name": "Operating regime remains unbounded",
                "validation_requirement": "Shift schedule, production calendar, and throughput profile",
                "validation_urgency_score": 0.95,
            },
            {
                "case_id": "LC-MKT-02",
                "case_name": "Economics remain unbounded",
                "validation_requirement": "12–24 months of utility / fuel records with process-support context",
                "validation_urgency_score": 0.94,
            },
        ],
        inference_records=[
            {"case_id": "LC-ASSET-01", "case_name": "Asset Technical Insufficiency and Scope Mismatch"},
            {"case_id": "LC-OPS-02", "case_name": "Operating regime remains unbounded"},
            {"case_id": "LC-MKT-02", "case_name": "Economics remain unbounded"},
        ],
        missing_clusters=["systems_cluster", "fuel_energy_cluster", "operating_regime_cluster"],
        minimum_evidence_seed=[],
        target_type="manufacturing_facility",
    )
    scenarios = _build_scenario_space(
        "WILSONART TEMPLE NORTH LAMINATE FACILITY",
        ["systems_cluster", "fuel_energy_cluster", "operating_regime_cluster"],
        ["tceq_air_permit"],
        "manufacturing_facility",
        fronts,
        evidence,
    )
    financial = _build_financial_exposure_register(
        "manufacturing_facility",
        ["tceq_air_permit"],
        evidence,
        fronts,
    )

    assert all(row["financial_meaning"] for row in scenarios)
    assert all(row["what_would_falsify_it"] for row in scenarios)
    assert all(row["linked_decision_front"] for row in scenarios)
    assert all(row["linked_evidence_item"] for row in scenarios)
    assert any(row["linked_decision_front"] == "Process efficiency or utility-support CAPEX" for row in scenarios)

    assert len(financial) >= 3
    assert any("Defer process-efficiency CAPEX" in row["financial_consequence"] for row in financial)
    assert all(row["linked_decision_front"] for row in financial)


def test_motor_015_uses_financial_exposure_register_for_uncertainty_and_financial_blocks():
    out = Motor015Adapter().run(
        {
            "motor_014": {
                "inference_records": [],
                "tension_records": [],
                "conflict_register": [],
                "opportunity_candidates": [],
                "uncertainty_register": [],
                "evidence_gap_register": [],
                "validation_queue": [],
                "next_best_questions": [],
                "composite_reading": {
                    "decision_state": "Blocked pending minimum evidence.",
                    "primary_block_reason": "Operating substrate incomplete",
                    "information_deficit_score": 0.68,
                    "primary_case_limitation": {},
                },
                "decision_front_register": [
                    {
                        "decision_front": "Process efficiency or utility-support CAPEX",
                        "current_status": "DEFER",
                        "why": "Process and utility basis remain unbounded.",
                        "required_evidence": "Process inventory + utility / fuel profile + throughput data",
                        "admissible_action": "Do not underwrite process CAPEX yet.",
                    }
                ],
                "minimum_evidence_unlock_map": [],
                "scenario_space": [],
                "financial_exposure_register": [
                    {
                        "assumption": "Energy intensity is correctable waste rather than structural process load",
                        "current_support": "Plausible but unsupported until process inventory, throughput, and utility basis are confirmed.",
                        "downside_if_wrong": "CAPEX targets structural process duty and fails to create defendable savings.",
                        "evidence_needed": "Process inventory + throughput profile + utility / fuel basis",
                        "financial_consequence": "Defer process-efficiency CAPEX and remove savings logic from screening until load drivers are validated.",
                        "linked_decision_front": "Process efficiency or utility-support CAPEX",
                    }
                ],
                "asset_context_readiness_summary": {},
                "facility_prior_id": "prior::test",
                "decision_core_lineage": {},
            },
            "motor_001": {},
            "motor_002": {},
        }
    )

    blocks = {row["block_type"]: row for row in out["output_blocks"]}
    uncertainty_rows = blocks["investment_uncertainty_map_block"]["rows"]
    assert uncertainty_rows[0]["uncertainty"] == "Energy intensity is correctable waste rather than structural process load"
    assert uncertainty_rows[0]["decision_it_blocks"] == "Process efficiency or utility-support CAPEX"
    assert uncertainty_rows[0]["priority"] == "Critical"

    financial_rows = blocks["financial_exposure_block"]["rows"]
    assert financial_rows[0]["linked_decision_front"] == "Process efficiency or utility-support CAPEX"
    assert "Defer process-efficiency CAPEX" in financial_rows[0]["financial_consequence"]


def test_motor_016_blocked_report_preserves_framework_order_and_language():
    out = Motor016Adapter().run(
        {
            "__pipeline__": {
                "case_id": "ZLab-asset-manufacturing-facility-test-2026",
                "case_title": "TEST MANUFACTURING FACILITY",
                "case_subtitle": "Decision-Admissibility Asset Brief",
                "organization": "ZLab",
                "analyst": "Autonomous Decision System",
                "facility_inputs": {
                    "input_01_location": {"address": "10501 N HK DODGEN LOOP, TEMPLE, TX"},
                    "input_02_facility_type": {"primary_classification": "manufacturing_facility"},
                    "input_03_sector": {"owner_name": "Wilsonart", "owner_ticker": "NA", "exchange": ""},
                },
            },
            "__runtime__": {
                "target_definition": {
                    "target_type": "manufacturing_facility",
                    "target_name": "Wilsonart Temple North Laminate Facility",
                    "target_label": "10501 N HK DODGEN LOOP, TEMPLE, TX",
                },
                "target_admissibility_state": "bounded_asset",
                "asset_context_readiness": "asset_context_partial",
                "report_identity_state": "Decision-Blocked Asset Brief",
                "recommended_report_type": "Decision-Blocked Asset Brief",
                "dominant_evidence_scope": "asset_level",
                "missing_observable_clusters": ["systems_cluster", "operating_regime_cluster"],
            },
            "motor_012": {
                "facility_prior": {
                    "entities": {},
                    "prior_assumptions_pack": [],
                    "uncertainty_markers": [],
                    "operational_tension_hypotheses": [],
                    "system_asset_hypotheses": [],
                },
                "evidence_lineage": {},
                "compliance_applicability_case": {
                    "rule_family_record": [{"rule_family_name": "TCEQ permits and emissions context"}],
                    "applicability_state": "screening_only",
                    "compliance_posture_state": "validate_first",
                    "determination_status": "not_closed",
                },
            },
            "motor_014": {
                "decision_core_lineage": {},
                "inference_records": [],
                "tension_records": [],
                "conflict_register": [],
                "opportunity_candidates": [],
                "uncertainty_register": [],
                "evidence_gap_register": [],
                "validation_queue": [],
                "next_best_questions": [],
                "claim_permission_summary": {},
                "variable_bottleneck_register": [],
                "report_readiness_register": {
                    "report_type_allowed": ["Decision-Blocked Asset Brief"],
                    "report_type_prohibited": ["Full Technical Decision Intelligence Report"],
                    "reason": "Asset evidence remains incomplete.",
                },
                "decision_front_register": [
                    {
                        "decision_front": "Process efficiency or utility-support CAPEX",
                        "current_status": "DEFER",
                    },
                    {
                        "decision_front": "Operator evidence request",
                        "current_status": "ACT NOW",
                    },
                ],
                "scenario_space": [
                    {
                        "scenario": "A. Energy intensity is structurally process-driven",
                        "financial_meaning": "Efficiency upside may be narrower than benchmark-only screening suggests.",
                    }
                ],
                "variable_bottleneck_register": [
                    {"variable_name": "utility_bills"},
                    {"variable_name": "process_flow"},
                ],
            },
            "motor_015": {
                "output_blocks": [
                    {
                        "block_type": "decision_admissibility_block",
                        "decision_state": "blocked pending minimum evidence",
                        "primary_block_reason": "Physical and operating substrate incomplete",
                        "decision_evaluated": "Operator evidence request",
                        "recommended_action": "Issue a targeted owner/operator data request immediately.",
                    },
                    {
                        "block_type": "investment_uncertainty_map_block",
                        "rows": [
                            {
                                "uncertainty": "Process boundary is not fully confirmed",
                                "why_it_matters_financially": "Could misstate process-driven energy and downtime exposure.",
                                "decision_it_blocks": "Process CAPEX screening",
                                "evidence_needed": "Bounded process and metering map",
                                "priority": "CRITICAL",
                            }
                        ],
                    },
                    {
                        "block_type": "minimum_evidence_pack_block",
                        "rows": [
                            {
                                "evidence_item": "Bounded asset record linking the address to a specific parcel, building, or site",
                                "source": "Owner or assessor",
                                "why_needed": "Confirms the physical asset boundary.",
                                "cases_resolved": ["LC-ASSET-01"],
                                "effort": "CRITICAL",
                                "decision_unlock": "Unlocks admissible asset-level reading.",
                            }
                        ],
                    },
                    {
                        "block_type": "scenario_space_block",
                        "rows": [
                            {
                                "scenario": "Process loads are owner-controlled and meter-bounded",
                                "plausibility_status": "plausible",
                                "financial_meaning": "Energy and reliability CAPEX may be worth screening.",
                                "what_would_make_it_true": "Operator boundary and meter map confirm owner control.",
                                "what_would_falsify_it": "Tenant or third-party process loads dominate.",
                                "linked_decision_front": "Operator evidence request",
                                "linked_evidence_item": "Bounded asset record + process boundary map",
                                "evidence_needed": "Operator and metering boundary map",
                            }
                        ],
                    },
                    {
                        "block_type": "financial_exposure_block",
                        "rows": [
                            {
                                "assumption": "Process-driven energy upside exists",
                                "current_support": "Unsupported until operator boundary and metering map are confirmed.",
                                "downside_if_wrong": "CAPEX is aimed at uncontrollable or structural process load.",
                                "evidence_needed": "Bounded asset record + process boundary map",
                                "financial_consequence": "Defer process-efficiency CAPEX until the process boundary is validated.",
                                "linked_decision_front": "Operator evidence request",
                            }
                        ],
                    },
                    {
                        "block_type": "decision_fronts_block",
                        "rows": [
                            {
                                "decision_front": "Operator evidence request",
                                "current_status": "ACT NOW",
                                "why": "The case cannot advance without bounded asset and process evidence.",
                                "required_evidence": "Bounded asset record + process boundary map",
                                "admissible_action": "Request owner/operator records now.",
                            }
                        ],
                    },
                ],
                "composite_reading": {"decision_state": "Blocked pending minimum evidence."},
                "facility_prior_id": "prior::test",
                "traceability_register": {"block_traces": []},
            },
            "motor_018": {"chart_assets": [], "chart_errors": []},
            "motor_019": {"written_sections": [], "codex_available": False, "llm_governance_summary": {}},
            "motor_028": {
                "quality_gate_passed": True,
                "source_register": [
                    {"source_name": "TCEQ permits", "accepted": True},
                    {"source_name": "Bell CAD property records", "accepted": True},
                ],
                "enriched_data": {"financials": {}, "extended_sources": {}},
            },
            "motor_033": {"tad_preliminary": {"tad_action_plan": [], "posture_summary": {}, "decision_front_actions": []}},
            "motor_034": {
                "maturity_summary": {},
                "cluster_maturity_register": [
                    {"cluster_id": "identity_cluster", "level": 3},
                    {"cluster_id": "geometry_size_cluster", "level": 1},
                    {"cluster_id": "regulatory_cluster", "level": 3},
                    {"cluster_id": "systems_cluster", "level": 0},
                ],
                "report_readiness_register": {"report_type_allowed": ["Decision-Blocked Asset Brief"]},
                "report_type_classifier_table": [
                    {
                        "asset": "Wilsonart Temple North Laminate Facility",
                        "recommended_report_type": "Decision-Blocked Asset Brief",
                        "why": "Asset evidence remains incomplete.",
                        "allowed_claims": ["compliance_screening_claim (conditional)"],
                        "blocked_claims": ["process_redesign_recommendation_claim"],
                    }
                ],
            },
            "motor_035": {
                "jurisdiction_resolution": {
                    "state": "TX",
                    "city": "Temple",
                    "utility": "Oncor",
                    "regulatory_stack": ["TCEQ permits", "EPA ECHO", "Utility tariff context"],
                }
            },
        }
    )

    report_view = out["report_package"]["approved_views"]["report_view"]
    body_titles = [section["title"] for section in report_view["body_sections"]]
    assert body_titles[:10] == [
        "Executive Decision-Admissibility Brief",
        "Asset Context Readiness",
        "Investment Uncertainty Map",
        "Blocking Conflicts",
        "Minimum Evidence Pack",
        "Scenario Space Under Current Uncertainty",
        "TAD — Decision-Admissibility Layer",
        "Regulatory / Normative Screening",
        "Inference Case Register",
        "Next Best Questions",
    ]

    executive = next(section for section in report_view["body_sections"] if section["title"] == "Executive Decision-Admissibility Brief")
    executive_content = executive["blocks"][0]["content"]
    assert "Publication Ceiling" in executive_content


def test_motor_016_screening_report_uses_canonical_context_and_asset_field_register():
    out = Motor016Adapter().run(
        {
            "__pipeline__": {
                "case_id": "ZLab-asset-commercial-building-ova-2026",
                "case_title": "One Vanderbilt",
                "case_subtitle": "Asset Decision-Admissibility Brief",
                "organization": "ZLab",
                "analyst": "Autonomous Decision System",
                "facility_inputs": {
                    "input_01_location": {"address": "ONE VANDERBILT AVENUE, NEW YORK, NY, 10017"},
                    "input_02_facility_type": {"primary_classification": "legacy_placeholder"},
                    "input_03_sector": {"owner_name": "SL Green", "owner_ticker": "SLG", "exchange": "NYSE"},
                    "input_06_vintage": {"year_built": "", "years_old": "6"},
                    "input_08_energy_fuel": {"recent_EUI_note": "legacy eui note"},
                },
            },
            "__runtime__": {
                "target_definition": {
                    "target_type": "commercial_building",
                    "target_name": "One Vanderbilt",
                    "target_label": "ONE VANDERBILT AVENUE, NEW YORK, NY, 10017",
                },
                "target_admissibility_state": "bounded_asset",
                "asset_context_readiness": "asset_context_insufficient",
                "report_identity_state": "Decision-Blocked Asset Brief",
                "recommended_report_type": "Decision-Blocked Asset Brief",
                "dominant_evidence_scope": "asset_level",
                "missing_observable_clusters": ["geometry_size_cluster", "systems_cluster"],
            },
            "motor_012": {
                "asset_field_register": [
                    {
                        "field": "address",
                        "value": "ONE VANDERBILT AVENUE, NEW YORK, NY, 10017",
                        "status": "OBSERVED",
                        "source_id": "nyc_dof_property_record::ova",
                        "scope": "ASSET_LEVEL",
                        "authority_score": "high",
                        "admissibility": "CONFIRMED_ASSET_LEVEL",
                        "identity_supported": True,
                    },
                    {
                        "field": "asset_class",
                        "value": "commercial_building",
                        "status": "OBSERVED",
                        "source_id": "nyc_pluto_property::ova",
                        "scope": "ASSET_LEVEL",
                        "authority_score": "high",
                        "admissibility": "CONFIRMED_ASSET_LEVEL",
                        "physical_substrate_supported": True,
                    },
                    {
                        "field": "GFA",
                        "value": "1678135",
                        "status": "OBSERVED",
                        "source_id": "nyc_pluto_property::ova",
                        "scope": "ASSET_LEVEL",
                        "authority_score": "high",
                        "admissibility": "CONFIRMED_ASSET_LEVEL",
                        "physical_substrate_supported": True,
                    },
                    {
                        "field": "year_built",
                        "value": "2020",
                        "status": "OBSERVED",
                        "source_id": "nyc_pluto_property::ova",
                        "scope": "ASSET_LEVEL",
                        "authority_score": "high",
                        "admissibility": "CONFIRMED_ASSET_LEVEL",
                        "physical_substrate_supported": True,
                    },
                    {
                        "field": "current_EUI",
                        "value": "120.5",
                        "status": "OBSERVED",
                        "source_id": "nyc_ll84_energy_benchmarking::ova",
                        "scope": "ASSET_LEVEL",
                        "authority_score": "high",
                        "admissibility": "CONFIRMED_ASSET_LEVEL",
                        "regulatory_supported": True,
                    },
                ],
                "facility_prior": {
                    "entities": {},
                    "prior_assumptions_pack": [],
                    "uncertainty_markers": [],
                    "operational_tension_hypotheses": [],
                    "system_asset_hypotheses": [],
                },
                "evidence_lineage": {},
                "compliance_applicability_case": {
                    "rule_family_record": [{"rule_family_name": "NYC Local Law 97"}],
                    "applicability_state": "screening_only",
                    "compliance_posture_state": "validate_first",
                    "determination_status": "not_closed",
                },
            },
            "motor_014": {
                "decision_core_lineage": {},
                "inference_records": [],
                "tension_records": [],
                "conflict_register": [],
                "opportunity_candidates": [],
                "uncertainty_register": [],
                "evidence_gap_register": [],
                "validation_queue": [],
                "next_best_questions": [],
                "claim_permission_summary": {
                    "allowed": 3,
                    "allowed_count": 3,
                    "conditional": 0,
                    "conditional_count": 0,
                    "prohibited": 8,
                    "prohibited_count": 8,
                },
                "variable_bottleneck_register": [],
                "report_readiness_register": {
                    "report_type_allowed": ["Compliance / Investment Screening Brief"],
                    "report_type_prohibited": ["Full Technical Decision Intelligence Report"],
                    "reason": "Public identity, geometry, and regulatory substrate support screening.",
                },
                "decision_front_register": [],
                "scenario_space": [],
                "canonical_asset_context_summary": {
                    "canonical_asset_context_state": "asset_context_minimal",
                    "missing_clusters": [
                        "boundary_cluster",
                        "operating_regime_cluster",
                        "fuel_energy_cluster",
                        "systems_cluster",
                        "control_boundary_cluster",
                    ],
                    "supported_clusters": [
                        "identity_cluster",
                        "geometry_size_cluster",
                        "vintage_structure_cluster",
                        "regulatory_cluster",
                    ],
                    "screening_supported": True,
                },
            },
            "motor_015": {
                "output_blocks": [
                    {"block_type": "decision_admissibility_block", "decision_state": "", "primary_block_reason": "", "decision_evaluated": "", "recommended_action": ""},
                ],
                "composite_reading": {"decision_state": ""},
                "facility_prior_id": "prior::ova",
                "traceability_register": {"block_traces": []},
            },
            "motor_018": {"chart_assets": [], "chart_errors": []},
            "motor_019": {"written_sections": [], "codex_available": False, "llm_governance_summary": {}},
            "motor_028": {
                "quality_gate_passed": True,
                "source_register": [],
                "source_family_coverage_table": [],
                "enriched_data": {"financials": {}, "extended_sources": {}, "ticker": "SLG", "company_name": "SL Green"},
            },
            "motor_033": {"tad_preliminary": {"tad_action_plan": [], "posture_summary": {}, "decision_front_actions": []}},
            "motor_034": {
                "maturity_summary": {},
                "cluster_maturity_register": [],
                "report_readiness_register": {"report_type_allowed": ["Compliance / Investment Screening Brief"]},
                "report_type_classifier_table": [],
                "canonical_asset_context_summary": {
                    "canonical_asset_context_state": "asset_context_minimal",
                    "missing_clusters": [
                        "boundary_cluster",
                        "operating_regime_cluster",
                        "fuel_energy_cluster",
                        "systems_cluster",
                        "control_boundary_cluster",
                    ],
                    "supported_clusters": [
                        "identity_cluster",
                        "geometry_size_cluster",
                        "vintage_structure_cluster",
                        "regulatory_cluster",
                    ],
                    "screening_supported": True,
                },
            },
            "motor_035": {"jurisdiction_resolution": {"state": "NY", "city": "New York"}},
        }
    )

    report_view = out["report_package"]["approved_views"]["report_view"]
    executive = next(section for section in report_view["body_sections"] if section["title"] == "Framework Context & Executive Brief")
    operational_identity = next(section for section in report_view["body_sections"] if section["title"] == "Operational Identity")
    governance = next(section for section in report_view["appendix_sections"] if section["title"] == "Governance Status")

    executive_content = executive["blocks"][0]["content"]
    identity_content = operational_identity["blocks"][0]["content"]
    governance_content = governance["blocks"][0]["content"]

    assert out["report_package"]["case_metadata"]["document_visible_type"] == "Compliance / Investment Screening Brief"
    assert "EPISTEMIC STATE: SCREENING ADMISSIBLE" in executive_content
    assert "Gross Floor Area   : 1,678,135 sqft" in identity_content
    assert "Year Built         : 2020" in identity_content
    assert "Declared EUI Note  : 120.5" in identity_content
    assert "Claim Permissions     : 3 allowed / 0 conditional / 8 prohibited" in governance_content


def test_motor_016_exposes_structural_lane_as_governed_appendices():
    out = Motor016Adapter().run(
        {
            "__pipeline__": {
                "case_id": "ZLab-asset-commercial-building-ova-2026",
                "case_title": "One Vanderbilt",
                "case_subtitle": "Asset Decision-Admissibility Brief",
                "organization": "ZLab",
                "analyst": "Autonomous Decision System",
                "facility_inputs": {
                    "input_01_location": {"address": "ONE VANDERBILT AVENUE, NEW YORK, NY, 10017"},
                    "input_02_facility_type": {"primary_classification": "commercial_building"},
                    "input_03_sector": {"owner_name": "SL Green", "owner_ticker": "SLG", "exchange": "NYSE"},
                },
            },
            "__runtime__": {
                "target_definition": {
                    "target_type": "commercial_building",
                    "target_name": "One Vanderbilt",
                    "target_label": "ONE VANDERBILT AVENUE, NEW YORK, NY, 10017",
                },
                "target_admissibility_state": "bounded_asset",
                "asset_context_readiness": "asset_context_minimal",
                "report_identity_state": "Decision-Blocked Asset Brief",
                "recommended_report_type": "Compliance / Investment Screening Brief",
                "dominant_evidence_scope": "asset_level",
                "missing_observable_clusters": ["systems_cluster", "control_boundary_cluster"],
            },
            "motor_012": {
                "asset_field_register": [
                    {"field": "address", "value": "ONE VANDERBILT AVENUE, NEW YORK, NY, 10017", "status": "OBSERVED", "source_id": "nyc_dof::ova", "scope": "ASSET_LEVEL", "authority_score": "high", "admissibility": "CONFIRMED_ASSET_LEVEL"},
                    {"field": "asset_class", "value": "commercial_building", "status": "OBSERVED", "source_id": "nyc_pluto::ova", "scope": "ASSET_LEVEL", "authority_score": "high", "admissibility": "CONFIRMED_ASSET_LEVEL"},
                    {"field": "GFA", "value": "1678135", "status": "OBSERVED", "source_id": "nyc_pluto::ova", "scope": "ASSET_LEVEL", "authority_score": "high", "admissibility": "CONFIRMED_ASSET_LEVEL"},
                    {"field": "floor_count", "value": "73", "status": "OBSERVED", "source_id": "nyc_pluto::ova", "scope": "ASSET_LEVEL", "authority_score": "high", "admissibility": "CONFIRMED_ASSET_LEVEL"},
                    {"field": "year_built", "value": "2020", "status": "OBSERVED", "source_id": "nyc_pluto::ova", "scope": "ASSET_LEVEL", "authority_score": "high", "admissibility": "CONFIRMED_ASSET_LEVEL"},
                    {"field": "current_EUI", "value": "72.1", "status": "OBSERVED", "source_id": "nyc_ll84::ova", "scope": "ASSET_LEVEL", "authority_score": "high", "admissibility": "CONFIRMED_ASSET_LEVEL"},
                ],
                "facility_prior": {"entities": {}, "prior_assumptions_pack": [], "uncertainty_markers": [], "operational_tension_hypotheses": [], "system_asset_hypotheses": []},
                "evidence_lineage": {},
                "compliance_applicability_case": {
                    "rule_family_record": [{"rule_family_name": "NYC Local Law 97"}],
                    "applicability_state": "screening_only",
                    "compliance_posture_state": "validate_first",
                    "determination_status": "not_closed",
                },
            },
            "motor_014": {
                "decision_core_lineage": {},
                "inference_records": [],
                "tension_records": [],
                "conflict_register": [],
                "opportunity_candidates": [],
                "uncertainty_register": [],
                "evidence_gap_register": [],
                "validation_queue": [],
                "next_best_questions": [],
                "claim_permission_summary": {
                    "allowed": 3,
                    "allowed_count": 3,
                    "conditional": 0,
                    "conditional_count": 0,
                    "prohibited": 8,
                    "prohibited_count": 8,
                },
                "variable_bottleneck_register": [],
                "report_readiness_register": {
                    "report_type_allowed": ["Compliance / Investment Screening Brief"],
                    "reason": "Public identity, geometry, and regulatory substrate support screening.",
                },
                "decision_front_register": [],
                "scenario_space": [],
                "canonical_asset_context_summary": {
                    "canonical_asset_context_state": "asset_context_minimal",
                    "missing_clusters": ["systems_cluster", "control_boundary_cluster"],
                    "supported_clusters": ["identity_cluster", "geometry_size_cluster", "regulatory_cluster"],
                    "screening_supported": True,
                },
                "canonical_problem_frame": {
                    "reasoning_path": "structural_first",
                    "problem_frame_active": True,
                    "stated_problem": "Need retrofit decision",
                    "reframed_problem": "Need to distinguish owner-controlled base-building upside from tenant-driven load.",
                    "dominant_conflict": "Regulation vs control boundary",
                    "minimum_evidence_to_discriminate": "LL84 + tenant metering map",
                },
            },
            "motor_015": {
                "output_blocks": [{"block_type": "decision_admissibility_block", "decision_state": "", "primary_block_reason": "", "decision_evaluated": "", "recommended_action": ""}],
                "composite_reading": {"decision_state": ""},
                "facility_prior_id": "prior::ova",
                "traceability_register": {"block_traces": []},
            },
            "motor_018": {"chart_assets": [], "chart_errors": []},
            "motor_019": {"written_sections": [], "codex_available": False, "llm_governance_summary": {}},
            "motor_028": {
                "quality_gate_passed": True,
                "source_register": [],
                "source_family_coverage_table": [],
                "enriched_data": {"financials": {}, "extended_sources": {}, "ticker": "SLG", "company_name": "SL Green"},
            },
            "motor_033": {
                "tad_preliminary": {"tad_action_plan": [], "posture_summary": {}, "decision_front_actions": []},
                "expanded_structural_tad_action_register": [
                    {"action": "Compare against structural peers", "status": "COMPARE TO PEERS", "why": "Bounded peer screening is admissible.", "evidence_state": "CONDITIONAL_HYPOTHESIS", "financial_exposure": "bounded downside", "evidence_needed": "LL84 + tenant metering map", "prohibited_action": "No superiority claim."}
                ],
            },
            "motor_034": {
                "maturity_summary": {},
                "cluster_maturity_register": [],
                "report_readiness_register": {"report_type_allowed": ["Compliance / Investment Screening Brief"]},
                "report_type_classifier_table": [],
                "structural_claim_permission_register": [
                    {"claim": "peer_comparison_claim", "permission": "hypothesis_only", "evidence_required": ["bounded peer context"], "current_evidence": "Competitive comparison register present.", "allowed_language": "Conditional peer comparison.", "forbidden_language": "Peer superiority as fact."}
                ],
                "structural_output_mode_classifier_table": [
                    {
                        "asset": "One Vanderbilt",
                        "recommended_output_mode": "Competitive Positioning Brief",
                        "activation_state": "activated_secondary",
                        "activation_reason": "Mode is admissible as a secondary structural surface and does not override the primary report type.",
                        "required_claims": ["peer_comparison_claim"],
                        "primary_report_type_guard": ["Compliance / Investment Screening Brief"],
                        "why": "Bounded peer context is available.",
                    }
                ],
                "structural_output_mode_summary": {
                    "primary_report_type": "Compliance / Investment Screening Brief",
                    "activated_secondary_modes": ["Competitive Positioning Brief"],
                    "blocked_secondary_modes": [],
                    "policy_note": "Structural output modes are secondary governed surfaces. They cannot override the primary report type or the claim-permission ceiling.",
                    "eligible_primary_modes": ["Competitive Positioning Brief"],
                    "non_promotable_primary_modes": [],
                    "leading_primary_promotion_candidate": "Competitive Positioning Brief",
                    "primary_promotion_policy_note": "Primary structural promotion remains advisory until the sovereign classifier explicitly elects it. Eligible modes cannot override the currently published report type without a dedicated promotion gate.",
                    "activation_count": 1,
                    "blocked_count": 0,
                    "eligible_primary_count": 1,
                },
                "canonical_asset_context_summary": {
                    "canonical_asset_context_state": "asset_context_minimal",
                    "missing_clusters": ["systems_cluster", "control_boundary_cluster"],
                    "supported_clusters": ["identity_cluster", "geometry_size_cluster", "regulatory_cluster"],
                    "screening_supported": True,
                },
            },
            "motor_035": {"jurisdiction_resolution": {"state": "NY", "city": "New York"}},
            "motor_037": {
                "system_abstraction": {
                    "asset_type": {"statement": "Commercial office tower", "evidence_state": "OBSERVED_FACT", "supporting_sources": ["nyc_pluto"], "falsification_condition": "Asset class differs in asset-level public record.", "minimum_evidence_required": ["asset-level classification record"]},
                    "control_structure": {"statement": "Owner/tenant control boundary remains conditional.", "evidence_state": "CONDITIONAL_HYPOTHESIS", "supporting_sources": ["archetype_library"], "falsification_condition": "Lease and metering evidence close the boundary.", "minimum_evidence_required": ["tenant metering map", "lease responsibility matrix"]},
                }
            },
            "motor_038": {
                "dominant_variable_register": [
                    {"variable": "tenant_metering", "layer": "control_boundary", "dominance": "high", "evidence_state": "CONDITIONAL_HYPOTHESIS", "why_it_could_matter": "Controls owner-capturable upside.", "what_confirms_it": "Submeter map", "what_falsifies_it": "Owner-only base-building load dominance", "decision_impact": "Screening vs retrofit economics"},
                ]
            },
            "motor_040": {
                "cross_layer_conflict_register": [
                    {"conflict": "Regulation vs control boundary", "layers_involved": ["regulation", "control/responsibility"], "evidence_state": "CONDITIONAL_HYPOTHESIS", "why_it_matters": "Owner may bear compliance while tenants drive load.", "what_confirms_it": "Tenant metering + leases", "what_falsifies_it": "Owner-dominated base-building load", "potential_redesign_direction": "Lease + submetering redesign"},
                ]
            },
            "motor_041": {
                "problem_framing_register": [
                    {"stated_problem": "Need retrofit decision", "reframed_problem": "Need to distinguish owner-controlled base-building upside from tenant-driven load.", "why_original_framing_may_be_wrong": "Retrofit may not capture owner value.", "evidence_needed": "Tenant metering map + lease responsibility matrix", "strategic_risk": "Owner-side CAPEX on tenant-driven load"},
                ]
            },
            "motor_042": {
                "structural_benchmark_register": [
                    {"dimension": "control boundary", "subject_asset": "control boundary not yet closed", "peer_or_benchmark": "Class A NYC towers with green leases/submetering", "difference": "subject boundary remains ambiguous", "evidence_state": "CONDITIONAL_HYPOTHESIS", "interpretation": "Peer screening is bounded, not local truth"},
                ]
            },
            "motor_043": {
                "competitive_comparison_register": [
                    {"better_performer": "Peer Class A NYC tower with submetering", "what_they_do_better": "Green leases and tenant submetering", "structural_advantage": "Control boundary clarity", "why_it_matters": "Captures retrofit value better", "transferability": "Conditional", "evidence_needed": "Lease and metering comparison", "evidence_state": "ARCHETYPAL_PRIOR"},
                ]
            },
            "motor_044": {
                "conditional_redesign_register": [
                    {"hypothesis": "Tenant-driven loads dominate the profile.", "evidence_state": "CONDITIONAL_HYPOTHESIS", "if_confirmed": "Keep redesign focused on lease/submetering strategy.", "redesign_direction": "Green leases, submetering, after-hours controls", "if_falsified": "Shift to base-building systems optimization.", "next_evidence": ["tenant metering map", "lease responsibility matrix"]},
                ]
            },
            "motor_045": {
                "structural_financial_exposure_register": [
                    {"structural_assumption": "Owner-controllable savings exist.", "evidence_state": "CONDITIONAL_HYPOTHESIS", "financial_exposure_if_wrong": "Retrofit CAPEX may not improve owner economics.", "evidence_needed": "Tenant metering map + control boundary", "allowed_financial_output": ["scenario framing"], "prohibited_financial_output": ["ROI", "IRR", "NPV", "payback", "bankability", "savings claim"]},
                ]
                ,
                "evidence_state_by_layer_register": [
                    {"layer": "control/responsibility", "evidence_state": "CONDITIONAL_HYPOTHESIS", "dominant_open_questions": ["tenant metering map", "lease responsibility matrix"], "observed_support": [], "structural_risk_if_wrong": "The party paying may not control the driver that matters.", "linked_conflicts": ["Regulation vs control boundary"], "linked_problem_frames": ["Need to distinguish owner-controlled base-building upside from tenant-driven load."]},
                ],
            },
            "motor_046": {
                "minimum_evidence_for_discrimination_register": [
                    {"rival_hypotheses": ["Owner-controlled base-building upside dominates.", "Tenant-driven loads dominate."], "minimum_evidence": "utility bills + tenant metering map + BMS / central plant topology + LL97 filing basis", "source": "operator request + public filings", "what_it_confirms": "Owner-side vs tenant-side value capture", "what_it_falsifies": "Incorrect retrofit thesis", "unlocks": "bounded retrofit vs lease redesign path"},
                ]
            },
        }
    )

    report_package = out["report_package"]
    body_titles = [section["title"] for section in report_package["approved_views"]["report_view"]["body_sections"]]
    appendix_titles = [section["title"] for section in report_package["approved_views"]["report_view"]["appendix_sections"]]
    executive = next(section for section in report_package["approved_views"]["report_view"]["body_sections"] if section["title"] == "Framework Context & Executive Brief")
    executive_content = executive["blocks"][0]["content"]
    expected_gold_nugget_authority_state = (
        report_package["main_report_outline"].get("gold_nugget_authority_state")
        or report_package["executive_thesis"].get("gold_nugget_authority_state")
        or "legacy_primary_skill_shadow"
    )
    expected_gold_nugget_source_register = (
        report_package["main_report_outline"].get("gold_nugget_source_register")
        or report_package["executive_thesis"].get("gold_nugget_source_register")
        or ""
    )

    assert "Executive Structural Brief" in body_titles
    assert "What the Client Thinks the Problem Is" in body_titles
    assert "What the System Thinks the Problem Might Actually Be" in body_titles
    assert "System Abstraction Map" in body_titles
    assert "Dominant Variables" in body_titles
    assert "Evidence State by Layer" in body_titles
    assert "Cross-Layer Contradictions" in body_titles
    assert "Competitive / Peer Comparison" in body_titles
    assert "Conditional Redesign Pathways" in body_titles
    assert "Minimum Evidence for Discrimination" in body_titles
    assert "System Consistency Check" in body_titles
    assert "What Not To Do Yet" in report_package["render_section_contract"]["preferred_body_sections"]
    assert (
        "What Not To Do Yet" in body_titles
        or "What Not To Do Yet" in appendix_titles
    )
    assert "Public Source Coverage Table" in appendix_titles
    assert report_package["structural_intelligence_summary"]["dominant_variable_count"] == 1
    assert report_package["structural_intelligence_summary"]["evidence_state_by_layer_count"] == 1
    assert report_package["structural_intelligence_summary"]["expanded_structural_tad_action_count"] == 1
    assert (
        report_package["structural_intelligence_summary"]["gold_nugget_authority_state"]
        == expected_gold_nugget_authority_state
    )
    assert (
        report_package["structural_intelligence_summary"]["gold_nugget_source_register"]
        == expected_gold_nugget_source_register
    )
    assert "STRUCTURAL READ" in executive_content
    assert "Primary-Eligible  : Competitive Positioning Brief" in executive_content
    assert "Reframed Problem  : Need to distinguish owner-controlled base-building upside from tenant-driven load." in executive_content
    assert "Dominant Conflict : Regulation vs control boundary" in executive_content
    assert report_package["structural_executive_summary"]["primary_structural_action"] == "Compare against structural peers"
    assert report_package["structural_executive_summary"]["promotable_primary_structural_modes"] == ["Competitive Positioning Brief"]
    assert (
        report_package["structural_executive_summary"]["gold_nugget_authority_state"]
        == expected_gold_nugget_authority_state
    )
    assert (
        report_package["structural_executive_summary"]["gold_nugget_source_register"]
        == expected_gold_nugget_source_register
    )
    assert report_package["structural_output_mode_classifier_table"][0]["recommended_output_mode"] == "Competitive Positioning Brief"
    assert report_package["structural_output_mode_classifier_table"][0]["activation_state"] == "activated_secondary"
    assert report_package["structural_output_mode_summary"]["activated_secondary_modes"] == ["Competitive Positioning Brief"]
    assert report_package["structural_output_mode_summary"]["eligible_primary_modes"] == ["Competitive Positioning Brief"]
    assert report_package["structural_intelligence_registers"]["system_abstraction"]["asset_type"]["evidence_state"] == "OBSERVED_FACT"
    assert report_package["render_section_contract"]["canonical_output_mode"] == "Compliance / Investment Screening Brief"
    assert report_package["render_section_contract"]["required_body_sections"][:5] == [
        "Executive Structural Brief",
        "What the System Thinks the Problem Might Actually Be",
        "Cross-Layer Contradictions",
        "System Abstraction Map",
        "Dominant Variables",
    ]
    assert "What Not To Do Yet" not in report_package["render_section_contract"]["required_body_sections"]
    assert "Claim Permission Matrix" not in report_package["render_section_contract"]["required_body_sections"]
    assert "Scenario Space" not in report_package["render_section_contract"]["required_body_sections"]
    assert "Conditional Redesign Pathways" not in report_package["render_section_contract"]["required_body_sections"]
    assert report_package["render_section_contract"]["preferred_body_sections"][0] == "Executive Structural Brief"
    assert "What the Client Thinks the Problem Is" in report_package["render_section_contract"]["preferred_body_sections"]
    assert "What the System Thinks the Problem Might Actually Be" in report_package["render_section_contract"]["preferred_body_sections"]
    assert set(report_package["render_section_contract"]["required_body_sections"]).issubset(
        set(report_package["render_section_contract"]["resolved_body_sections"])
    )
    assert report_package["planned_chapter_inventory"]["canonical_output_mode"] == "Compliance / Investment Screening Brief"
    assert report_package["planned_chapter_inventory"]["body_section_titles"] == [
        section["title"] for section in report_package["approved_views"]["report_view"]["body_sections"]
    ]
    assert len(report_package["planned_chapter_inventory"]["body_chapter_files"]) == len(
        set(report_package["planned_chapter_inventory"]["body_chapter_files"])
    )
    assert len(report_package["planned_chapter_inventory"]["appendix_chapter_files"]) == len(
        set(report_package["planned_chapter_inventory"]["appendix_chapter_files"])
    )
    assert all(
        chapter_file.startswith("A")
        for chapter_file in report_package["planned_chapter_inventory"]["appendix_chapter_files"]
    )


def test_structural_primary_body_builder_matches_prompt_architecture():
    sections = _build_structural_primary_body_sections(
        document_label="Structural Contradiction Brief",
        main_warning="bounded",
        allowed_use=["screening"],
        prohibited_use=["ROI"],
        structural_executive_summary={
            "leading_primary_structural_mode": "Structural Contradiction Brief",
            "primary_reframed_problem": "Need to distinguish owner-side compliance burden from tenant-driven load.",
            "dominant_structural_conflict": "Regulation vs control boundary",
            "primary_structural_action": "Request tenant metering map",
            "primary_structural_action_status": "ACT NOW",
            "bounded_note": "Structural reading remains conditional.",
        },
        client_concern={"primary_concern": "Need retrofit decision", "sub_concerns": ["Need LL97 pathway clarity"]},
        system_abstraction={
            "asset_type": {
                "statement": "Commercial office tower",
                "evidence_state": "OBSERVED_FACT",
                "supporting_sources": ["nyc_pluto"],
                "falsification_condition": "Asset record differs.",
                "minimum_evidence_required": ["asset-level classification record"],
            }
        },
        dominant_variable_register=[
            {
                "variable": "tenant_metering",
                "layer": "control/responsibility",
                "dominance": "high",
                "evidence_state": "CONDITIONAL_HYPOTHESIS",
                "why_it_could_matter": "Controls owner-capturable upside.",
                "what_confirms_it": "Submeter map",
                "what_falsifies_it": "Owner-only base-building load dominance",
                "decision_impact": "Screening vs redesign path",
            }
        ],
        evidence_state_by_layer_register=[
            {
                "layer": "control/responsibility",
                "evidence_state": "CONDITIONAL_HYPOTHESIS",
                "dominant_open_questions": ["tenant metering map"],
                "observed_support": ["LL97-covered building listing"],
                "structural_risk_if_wrong": "Owner pays but may not control the driver.",
                "linked_conflicts": ["Regulation vs control boundary"],
                "linked_problem_frames": ["Need to distinguish owner-side compliance burden from tenant-driven load."],
            }
        ],
        cross_layer_conflict_register=[
            {
                "conflict": "Regulation vs control boundary",
                "layers_involved": ["regulation", "control/responsibility"],
                "evidence_state": "CONDITIONAL_HYPOTHESIS",
                "why_it_matters": "Owner burden may not match control.",
                "what_confirms_it": "Tenant metering + lease matrix",
                "what_falsifies_it": "Owner-dominated base-building load",
                "potential_redesign_direction": "Lease + submetering redesign",
            }
        ],
        scenario_space=[
            {
                "scenario": "Tenant loads dominate.",
                "plausibility_status": "conditional",
                "financial_meaning": "Owner-only retrofit economics weaken.",
                "what_would_make_it_true": "Metered tenant loads dominate baseline.",
                "what_would_falsify_it": "Owner-controlled central plant dominates.",
                "evidence_needed": "Tenant metering map",
                "linked_evidence_item": "Tenant metering map",
                "linked_decision_front": "Compliance investment",
            }
        ],
        structural_financial_exposure_register=[
            {
                "structural_assumption": "Owner-controllable savings exist.",
                "evidence_state": "CONDITIONAL_HYPOTHESIS",
                "financial_exposure_if_wrong": "Retrofit CAPEX may not improve owner economics.",
                "evidence_needed": "Tenant metering map + control boundary",
                "allowed_financial_output": ["scenario framing"],
                "prohibited_financial_output": ["ROI", "IRR", "NPV", "payback", "bankability", "savings claim"],
            }
        ],
        structural_benchmark_register=[
            {
                "dimension": "control boundary",
                "subject_asset": "boundary not closed",
                "peer_or_benchmark": "Class A NYC tower with submetering",
                "difference": "subject boundary remains ambiguous",
                "evidence_state": "CONDITIONAL_HYPOTHESIS",
                "interpretation": "Peer context is bounded.",
            }
        ],
        competitive_comparison_register=[
            {
                "better_performer": "Peer Class A NYC tower with submetering",
                "what_they_do_better": "Green leases and submetering",
                "structural_advantage": "Control boundary clarity",
                "why_it_matters": "Captures value better",
                "transferability": "Conditional",
                "evidence_needed": "Lease and metering comparison",
                "evidence_state": "ARCHETYPAL_PRIOR",
            }
        ],
        conditional_redesign_register=[
            {
                "hypothesis": "Tenant-driven loads dominate.",
                "evidence_state": "CONDITIONAL_HYPOTHESIS",
                "if_confirmed": "Focus on lease/submetering redesign.",
                "redesign_direction": "Green leases, submetering, after-hours policy",
                "if_falsified": "Shift to base-building optimization.",
                "next_evidence": ["tenant metering map"],
            }
        ],
        minimum_evidence_for_discrimination_register=[
            {
                "rival_hypotheses": ["Owner-controlled base-building upside dominates.", "Tenant-driven loads dominate."],
                "minimum_evidence": "utility bills + tenant metering map + BMS topology",
                "source": "operator request + public filings",
                "what_it_confirms": "Owner-side vs tenant-side value capture",
                "what_it_falsifies": "Incorrect retrofit thesis",
                "unlocks": "bounded retrofit vs lease redesign path",
            }
        ],
        expanded_structural_tad_action_register=[
            {
                "action": "Request tenant metering map",
                "status": "ACT NOW",
                "why": "Needed to close control boundary.",
                "evidence_state": "CONDITIONAL_HYPOTHESIS",
                "financial_exposure": "Owner-side CAPEX may miss value if wrong.",
                "evidence_needed": "Tenant metering map",
                "prohibited_action": "Do not underwrite owner-only retrofit ROI.",
            }
        ],
        client_facing_tad={
            "action_count": 1,
            "actions": [
                {
                    "action": "Request tenant metering map",
                    "status": "ACT NOW",
                    "why": "Needed to close control boundary.",
                    "evidence_state": "CONDITIONAL_HYPOTHESIS",
                    "financial_exposure": "Owner-side CAPEX may miss value if wrong.",
                    "evidence_needed": "Tenant metering map",
                    "prohibited_action": "Do not underwrite owner-only retrofit ROI.",
                }
            ],
        },
        claim_contract_register=[
            {
                "claim_id": "peer_comparison_claim",
                "claim_family": "comparison",
                "statement": "Peer comparison remains bounded.",
                "permission": "hypothesis_only",
                "evidence_state": "ARCHETYPAL_PRIOR",
                "supporting_sources": ["ll84"],
                "assumptions": ["peer context is comparable"],
                "falsification_condition": "Peer asset is not operationally comparable.",
                "minimum_evidence_required": ["comparable control boundary"],
                "allowed_use": ["conditional peer framing"],
                "prohibited_use": ["peer superiority claim"],
            },
            {
                "claim_id": "TAD_action_claim",
                "claim_family": "tad",
                "statement": "Request tenant metering map now.",
                "permission": "allowed",
                "evidence_state": "CONDITIONAL_HYPOTHESIS",
                "supporting_sources": ["ll97"],
                "assumptions": ["control boundary remains open"],
                "falsification_condition": "Owner-only base-building load is already demonstrated.",
                "minimum_evidence_required": ["tenant metering map"],
                "allowed_use": ["action prioritization"],
                "prohibited_use": ["final investment recommendation"],
            },
        ],
        source_family_coverage_table=[
            {
                "source_family": "nyc_pluto_property",
                "source_name": "PLUTO",
                "queried": True,
                "found": True,
                "authority": "public_dataset",
                "scope": "ASSET_LEVEL",
                "fields_extracted": ["GFA", "year_built"],
                "missing": ["tenant_metering"],
                "support_note": "Source contributed asset-level support for geometry and identity.",
            }
        ],
        problem_framing_register=[
            {
                "stated_problem": "Need retrofit decision",
                "reframed_problem": "Need to distinguish owner-side compliance burden from tenant-driven load.",
                "why_original_framing_may_be_wrong": "Retrofit may not capture owner value.",
                "evidence_needed": "Tenant metering map + lease responsibility matrix",
                "strategic_risk": "Owner-side CAPEX on tenant-driven load",
            }
        ],
        llm_lookup={},
        llm_lookup_en={},
        llm_lookup_es={},
    )

    assert [section["title"] for section in sections] == [
        "Executive Structural Brief",
        "What the Client Thinks the Problem Is",
        "What the System Thinks the Problem Might Actually Be",
        "System Abstraction Map",
        "Dominant Variables",
        "Evidence State by Layer",
        "Cross-Layer Contradictions",
        "Scenario Space",
        "Financial Exposure Under Uncertainty",
        "Competitive / Peer Comparison",
        "Conditional Redesign Pathways",
        "Minimum Evidence for Discrimination",
        "TAD — Action Priority",
        "What Not To Do Yet",
        "Claim Permission Matrix",
        "Source Traceability",
        "System Consistency Check",
    ]


def test_render_section_contract_prioritizes_structural_primary_body_by_mode():
    sections = _build_structural_primary_body_sections(
        document_label="Competitive Positioning Brief",
        main_warning="bounded",
        allowed_use=["screening"],
        prohibited_use=["ROI"],
        structural_executive_summary={
            "leading_primary_structural_mode": "Competitive Positioning Brief",
            "primary_reframed_problem": "Need to distinguish owner-side compliance burden from tenant-driven load.",
            "dominant_structural_conflict": "Regulation vs control boundary",
            "primary_structural_action": "Compare against structural peers",
            "primary_structural_action_status": "COMPARE TO PEERS",
            "bounded_note": "Structural reading remains conditional.",
        },
        client_concern={"primary_concern": "Need retrofit decision", "sub_concerns": []},
        system_abstraction={},
        dominant_variable_register=[],
        evidence_state_by_layer_register=[],
        cross_layer_conflict_register=[],
        scenario_space=[],
        structural_financial_exposure_register=[],
        structural_benchmark_register=[],
        competitive_comparison_register=[],
        conditional_redesign_register=[],
        minimum_evidence_for_discrimination_register=[],
        expanded_structural_tad_action_register=[],
        client_facing_tad={"action_count": 0, "actions": []},
        claim_contract_register=[],
        source_family_coverage_table=[],
        problem_framing_register=[],
        llm_lookup={},
        llm_lookup_en={},
        llm_lookup_es={},
    )
    ordered_body, ordered_appendix, contract = resolve_render_section_contract(
        "Competitive Positioning Brief",
        sections,
        [],
    )

    assert contract["canonical_output_mode"] == "Competitive Positioning Brief"
    assert contract["structural_primary"] is True
    assert contract["required_body_sections"] == [
        "Executive Structural Brief",
        "Competitive / Peer Comparison",
        "Dominant Variables",
        "Financial Exposure Under Uncertainty",
        "TAD — Action Priority",
    ]
    assert [section["title"] for section in ordered_body[:6]] == [
        "Executive Structural Brief",
        "What the System Thinks the Problem Might Actually Be",
        "Competitive / Peer Comparison",
        "Dominant Variables",
        "Financial Exposure Under Uncertainty",
        "TAD — Action Priority",
    ]
    assert ordered_appendix == []


def test_render_section_contract_accepts_inadmissible_bypass_without_body_sections():
    render_section_contract = {
        "canonical_output_mode": "Target Classification Brief",
        "required_body_sections": [],
        "required_appendix_sections": [],
        "resolved_body_sections": [],
        "resolved_appendix_sections": ["Governance Status"],
        "policy_note": "Inadmissible thesis bypass",
    }
    body_sections = []
    appendix_sections = [{"title": "Governance Status"}]

    _validate_render_section_contract(
        render_section_contract,
        body_sections,
        appendix_sections,
    )


def test_chart_visibility_policy_promotes_legacy_support_hints_to_visible_appendices():
    visible_section_ids = {
        "cf_peer_comparison",
        "cf_minimum_evidence",
        "a2_asset_context_prior",
        "a5_evidence_maturity_matrix",
        "a11_cross_layer_contradictions",
        "a13_structural_benchmarking_and_competition",
        "a14_conditional_redesign_and_structural_financial_exposure",
    }
    promotion_policy = get_support_chart_visibility_policy(
        "Exploratory Prior Brief",
        "logistics_warehouse",
    )

    resolved_hint, state = _resolve_chart_visibility_section_hint(
        "c5_energy_normative",
        visible_section_ids,
        promotion_policy,
    )
    assert resolved_hint == "a2_asset_context_prior"
    assert state == "promoted_to_visible_support_section"

    resolved_hint, state = _resolve_chart_visibility_section_hint(
        "cf_minimum_evidence",
        visible_section_ids,
        promotion_policy,
    )
    assert resolved_hint == "cf_minimum_evidence"
    assert state == "direct_visible_match"

    resolved_hint, state = _resolve_chart_visibility_section_hint(
        "c10_competitive_peer",
        visible_section_ids,
        promotion_policy,
    )
    assert resolved_hint == "a13_structural_benchmarking_and_competition"
    assert state == "promoted_to_visible_support_section"


def test_support_chart_visibility_policy_is_declarative_and_traceable():
    policy = get_support_chart_visibility_policy(
        "Exploratory Prior Brief",
        "logistics_warehouse",
    )
    assert policy["policy_source"] == "render_section_contract.support_chart_visibility_rules.v1"
    assert policy["canonical_output_mode"] == "Exploratory Prior Brief"
    assert policy["asset_family"] == "logistics_warehouse"
    assert policy["section_map"]["c7_validation_architecture"][0] == "a3_priority_questions"
    assert "a13_structural_benchmarking_and_competition" in policy["section_map"]["c10_competitive_peer"]


def test_support_chart_visibility_policy_varies_by_output_mode():
    exploratory_logistics = get_support_chart_visibility_policy(
        "Exploratory Prior Brief",
        "logistics_warehouse",
    )
    screening_logistics = get_support_chart_visibility_policy(
        "Compliance / Investment Screening Brief",
        "logistics_warehouse",
    )
    exploratory_building = get_support_chart_visibility_policy(
        "Exploratory Prior Brief",
        "commercial_building",
    )
    screening_building = get_support_chart_visibility_policy(
        "Compliance / Investment Screening Brief",
        "commercial_building",
    )
    assert exploratory_logistics["section_map"]["c2_operational_identity"][0] == "a9_system_abstraction_map"
    assert screening_logistics["section_map"]["c2_operational_identity"][0] == "a6_public_source_coverage"
    assert exploratory_building["section_map"]["c3_blocking_conflicts"][0] == "a11_cross_layer_contradictions"
    assert screening_building["section_map"]["c3_blocking_conflicts"][0] == "a5_evidence_maturity_matrix"
    assert exploratory_building["section_map"]["c7_validation_architecture"][0] == "a3_priority_questions"
    assert screening_building["section_map"]["c7_validation_architecture"][0] == "a5_evidence_maturity_matrix"


def test_support_chart_visibility_policy_varies_by_asset_family():
    logistics = get_support_chart_visibility_policy(
        "Exploratory Prior Brief",
        "logistics_warehouse",
    )
    cold_chain = get_support_chart_visibility_policy(
        "Exploratory Prior Brief",
        "cold_chain",
    )
    utility_heavy = get_support_chart_visibility_policy(
        "Compliance / Investment Screening Brief",
        "utility_heavy_site",
    )
    assert logistics["section_map"]["c2_operational_identity"][0] == "a9_system_abstraction_map"
    assert cold_chain["section_map"]["c5_energy_normative"][0] == "a9_system_abstraction_map"
    assert utility_heavy["section_map"]["c5_energy_normative"][0] == "a8_industry_adaptation"
    assert utility_heavy["section_map"]["c7_validation_architecture"][0] == "a16_structural_claims_output_modes_and_tad"


def test_support_chart_visibility_policy_can_differentiate_by_chart_asset():
    visible_section_ids = {
        "a3_priority_questions",
        "a5_evidence_maturity_matrix",
        "a11_cross_layer_contradictions",
        "a16_structural_claims_output_modes_and_tad",
    }
    policy = get_support_chart_visibility_policy(
        "Compliance / Investment Screening Brief",
        "logistics_warehouse",
    )
    resolved_hint, state = _resolve_chart_visibility_section_hint(
        "c7_validation_architecture",
        visible_section_ids,
        policy,
        {"asset_id": "chart_next_best_search_path", "chart_category": "next_best_search", "chart_intent": "search_program"},
    )
    assert resolved_hint == "a3_priority_questions"
    assert state == "promoted_to_visible_support_section"

    resolved_hint, state = _resolve_chart_visibility_section_hint(
        "c7_validation_architecture",
        visible_section_ids,
        policy,
        {"asset_id": "chart_validation_priority", "chart_category": "validation_priority", "chart_intent": "validation_priority"},
    )
    assert resolved_hint == "a5_evidence_maturity_matrix"
    assert state == "promoted_to_visible_support_section"

    resolved_hint, state = _resolve_chart_visibility_section_hint(
        "c3_blocking_conflicts",
        visible_section_ids,
        policy,
        {"asset_id": "chart_gap_taxonomy_profile", "chart_category": "gap_taxonomy", "chart_intent": "evidence_gap_diagnosis"},
    )
    assert resolved_hint == "a5_evidence_maturity_matrix"
    assert state == "promoted_to_visible_support_section"

    resolved_hint, state = _resolve_chart_visibility_section_hint(
        "c3_blocking_conflicts",
        visible_section_ids,
        policy,
        {"asset_id": "chart_causal_dependency", "chart_category": "causal_dependency", "chart_intent": "contradiction_dependency_map"},
    )
    assert resolved_hint == "a11_cross_layer_contradictions"
    assert state == "promoted_to_visible_support_section"


def test_support_chart_visibility_policy_can_differentiate_by_chart_lane():
    visible_section_ids = {
        "a5_evidence_maturity_matrix",
        "a13_structural_benchmarking_and_competition",
        "a16_structural_claims_output_modes_and_tad",
    }
    policy = get_support_chart_visibility_policy(
        "Compliance / Investment Screening Brief",
        "commercial_building",
    )
    resolved_hint, state = _resolve_chart_visibility_section_hint(
        "c10_competitive_peer",
        visible_section_ids,
        policy,
        {"asset_id": "chart_peer_requirement_readiness", "chart_category": "peer_requirement_readiness", "chart_lane": "comparison"},
    )
    assert resolved_hint == "a5_evidence_maturity_matrix"
    assert state == "promoted_to_visible_support_section"


def test_support_chart_lane_visibility_policy_varies_by_output_mode():
    exploratory = get_support_chart_lane_visibility_policy("Exploratory Prior Brief")
    screening = get_support_chart_lane_visibility_policy("Compliance / Investment Screening Brief")
    assert exploratory["policy_source"] == "render_section_contract.support_chart_lane_visibility.v1"
    assert exploratory["lane_limits"]["appendix"]["validation"] == 2
    assert exploratory["lane_limits"]["appendix"]["contradiction"] == 2
    assert screening["lane_limits"]["appendix"]["validation"] == 2
    assert screening["lane_limits"]["appendix"]["contradiction"] == 1


def test_support_chart_lane_curation_policy_varies_by_output_mode():
    exploratory = get_support_chart_lane_curation_policy("Exploratory Prior Brief")
    screening = get_support_chart_lane_curation_policy("Compliance / Investment Screening Brief")
    assert exploratory["policy_source"] == "render_section_contract.support_chart_lane_curation.v1"
    assert exploratory["section_lane_intent_priority"]["a3_priority_questions"]["validation"][0] == "search_program"
    assert screening["section_lane_intent_priority"]["a5_evidence_maturity_matrix"]["validation"][0] == "evidence_gap_diagnosis"


def test_support_chart_lane_visibility_cap_suppresses_excess_promoted_support_charts():
    lane_counts: dict[tuple[str, str, str], int] = {}
    section_surface_map = {
        "a5_evidence_maturity_matrix": "appendix",
    }
    lane_policy = get_support_chart_lane_visibility_policy("Compliance / Investment Screening Brief")

    first = _apply_support_chart_lane_visibility_cap(
        policy_state="promoted_to_visible_support_section",
        resolved_section_hint="a5_evidence_maturity_matrix",
        chart_asset={"chart_lane": "validation"},
        section_surface_map=section_surface_map,
        support_chart_lane_visibility_policy=lane_policy,
        lane_visibility_counts=lane_counts,
    )
    second = _apply_support_chart_lane_visibility_cap(
        policy_state="promoted_to_visible_support_section",
        resolved_section_hint="a5_evidence_maturity_matrix",
        chart_asset={"chart_lane": "validation"},
        section_surface_map=section_surface_map,
        support_chart_lane_visibility_policy=lane_policy,
        lane_visibility_counts=lane_counts,
    )
    third = _apply_support_chart_lane_visibility_cap(
        policy_state="promoted_to_visible_support_section",
        resolved_section_hint="a5_evidence_maturity_matrix",
        chart_asset={"chart_lane": "validation"},
        section_surface_map=section_surface_map,
        support_chart_lane_visibility_policy=lane_policy,
        lane_visibility_counts=lane_counts,
    )

    assert first["lane_visibility_state"] == "visible_within_lane_cap"
    assert first["effective_visible_section_hint"] == "a5_evidence_maturity_matrix"
    assert second["lane_visibility_state"] == "visible_within_lane_cap"
    assert third["lane_visibility_state"] == "suppressed_by_lane_cap"
    assert third["effective_visible_section_hint"] == ""


def test_support_chart_lane_visibility_cap_is_scoped_per_section():
    lane_counts: dict[tuple[str, str, str], int] = {}
    section_surface_map = {
        "a5_evidence_maturity_matrix": "appendix",
        "a3_priority_questions": "appendix",
    }
    lane_policy = get_support_chart_lane_visibility_policy("Compliance / Investment Screening Brief")

    first = _apply_support_chart_lane_visibility_cap(
        policy_state="promoted_to_visible_support_section",
        resolved_section_hint="a5_evidence_maturity_matrix",
        chart_asset={"chart_lane": "validation"},
        section_surface_map=section_surface_map,
        support_chart_lane_visibility_policy=lane_policy,
        lane_visibility_counts=lane_counts,
    )
    second = _apply_support_chart_lane_visibility_cap(
        policy_state="promoted_to_visible_support_section",
        resolved_section_hint="a3_priority_questions",
        chart_asset={"chart_lane": "validation"},
        section_surface_map=section_surface_map,
        support_chart_lane_visibility_policy=lane_policy,
        lane_visibility_counts=lane_counts,
    )
    assert first["lane_visibility_state"] == "visible_within_lane_cap"
    assert second["lane_visibility_state"] == "visible_within_lane_cap"


def test_support_chart_lane_curation_prioritizes_screening_evidence_charts_within_same_section():
    curation_policy = get_support_chart_lane_curation_policy("Compliance / Investment Screening Brief")
    records = []
    for index, chart_asset in enumerate([
        {"asset_id": "chart_next_best_search_path", "chart_lane": "validation", "chart_intent": "search_program"},
        {"asset_id": "chart_validation_priority", "chart_lane": "validation", "chart_intent": "validation_priority"},
        {"asset_id": "chart_gap_taxonomy_profile", "chart_lane": "validation", "chart_intent": "evidence_gap_diagnosis"},
    ]):
        curation_entry = _resolve_support_chart_lane_curation_entry(
            resolved_section_hint="a5_evidence_maturity_matrix",
            chart_asset=chart_asset,
            support_chart_lane_curation_policy=curation_policy,
        )
        records.append({
            "asset_id": chart_asset["asset_id"],
            "chart_lane": chart_asset["chart_lane"],
            "policy_state": "promoted_to_visible_support_section",
            "original_index": index,
            "lane_curation_rank": curation_entry["lane_curation_rank"],
        })

    ordered = _order_section_chart_records(records)
    assert [row["asset_id"] for row in ordered] == [
        "chart_gap_taxonomy_profile",
        "chart_validation_priority",
        "chart_next_best_search_path",
    ]


def test_compliance_body_outline_priority_is_reapplied_after_render_contract_resolution():
    expected_titles = [
        "Executive Structural Thesis",
        "Reframed Problem",
        "Dominant Structural Contradiction",
        "System Abstraction Snapshot",
        "Dominant Variables",
        "Scenario Space",
        "Financial Exposure Under Uncertainty",
        "Peer / Competitive Comparison",
        "Conditional Redesign Pathway",
        "Minimum Evidence for Discrimination",
        "TAD — Immediate Action Priority",
        "Claim Permissions / What Not To Do",
    ]
    body_sections = []
    for idx, title in enumerate(
        [
            "Dominant Variables",
            "Scenario Space",
            "Financial Exposure Under Uncertainty",
            "Minimum Evidence for Discrimination",
            "Executive Structural Thesis",
            "TAD — Immediate Action Priority",
            "Claim Permissions / What Not To Do",
            "Reframed Problem",
            "Dominant Structural Contradiction",
            "System Abstraction Snapshot",
            "Peer / Competitive Comparison",
            "Conditional Redesign Pathway",
        ],
        start=1,
    ):
        body_sections.append(
            {
                "section_id": f"c{idx}",
                "chapter_id": f"C{idx}",
                "chapter_number": idx,
                "title": title,
                "section_type": "body",
                "audience": "executive",
                "epistemic_marker": "CONDITIONAL",
                "blocks": [{"block_id": f"b{idx}", "content": title}],
            }
        )

    ordered_body, _, _ = resolve_render_section_contract(
        "Compliance / Investment Screening Brief",
        body_sections,
        [],
    )
    reprioritized = _prioritize_body_sections_by_outline(
        ordered_body,
        {"body_section_titles": expected_titles},
    )

    assert [section["title"] for section in reprioritized] == expected_titles


def test_appendix_titles_do_not_compete_with_client_facing_body_titles():
    body_sections = [
        {"title": "Dominant Variables"},
        {"title": "Minimum Evidence for Discrimination"},
    ]
    appendix_sections = [
        {"title": "Dominant Variables", "section_type": "appendix"},
        {"title": "Minimum Evidence for Discrimination", "section_type": "appendix"},
        {"title": "Evidence State by Layer", "section_type": "appendix"},
    ]

    normalized = _disambiguate_appendix_titles_against_body(body_sections, appendix_sections)

    assert [section["title"] for section in normalized] == [
        "Dominant Variables — Technical Register",
        "Minimum Evidence for Discrimination — Technical Register",
        "Evidence State by Layer",
    ]


def test_section_surface_density_gate_demotes_thin_support_sections_to_appendix():
    body_sections = [
        {
            "section_id": "cf_exec",
            "title": "Executive Structural Brief",
            "section_type": "body",
            "outline_section_key": "executive_structural_thesis",
            "llm_text": "",
            "blocks": [
                {
                    "content": "\n".join(
                        [
                            "EXECUTIVE STRUCTURAL THESIS",
                            "Declared Problem     : Need retrofit decision",
                            "Reframed Problem     : The problem may be wrong-variable selection.",
                            "Dominant Contradiction: Service intensity vs area-normalized benchmarking",
                            "Financial Exposure If Wrong: Capital may chase the wrong variable.",
                            "Strategic Gold Nugget: Wrong denominator can distort capital allocation.",
                        ]
                    )
                }
            ],
        },
        {
            "section_id": "cf_peer",
            "title": "Competitive / Peer Comparison",
            "section_type": "body",
            "outline_section_key": "peer_comparison",
            "llm_text": "",
            "blocks": [
                {
                    "content": "\n".join(
                        [
                            "PEER / COMPETITIVE COMPARISON",
                            "Peer Type           : fulfillment peer set",
                            "Invalid Comparison Risk: area-based EUI may be structurally misleading.",
                            "Peer Requirements   : dock density, charging profile, service level",
                            "Better-Practice Deltas: managed charging windows and dock-seal discipline",
                            "Peer Superiority Block: local superiority remains prohibited.",
                        ]
                    )
                }
            ],
        },
        {
            "section_id": "cf_consistency",
            "title": "System Consistency Check",
            "section_type": "body",
            "llm_text": "",
            "blocks": [
                {
                    "content": "\n".join(
                        [
                            "SYSTEM CONSISTENCY CHECK",
                            "NOT OBSERVED",
                            "NONE BOUNDED",
                        ]
                    )
                }
            ],
        },
    ]
    appendix_sections = [
        {
            "section_id": "a1_traceability",
            "title": "Evidence & Source Traceability",
            "section_type": "appendix",
            "blocks": [{"content": "Traceability appendix."}],
        }
    ]

    gated_body, gated_appendix, policy_register, summary = _apply_section_surface_density_gate(
        body_sections=body_sections,
        appendix_sections=appendix_sections,
        minimum_body_sections=2,
        min_substantive_lines=5,
        min_density_score=8,
    )

    assert [section["title"] for section in gated_body] == [
        "Executive Structural Brief",
        "Competitive / Peer Comparison",
    ]
    assert any(section["title"] == "System Consistency Check" for section in gated_appendix)
    density_row = next(row for row in policy_register if row["section_id"] == "cf_consistency")
    assert density_row["policy_state"] == "demoted_thin_body_section_to_appendix"
    assert density_row["destination_surface"] == "appendix"
    assert summary["demoted_to_appendix_count"] == 1


def test_section_surface_density_gate_keeps_core_sections_even_when_thin():
    body_sections = [
        {
            "section_id": "cf_exec",
            "title": "Executive Structural Brief",
            "section_type": "body",
            "outline_section_key": "executive_structural_thesis",
            "llm_text": "",
            "blocks": [{"content": "EXECUTIVE STRUCTURAL THESIS\nNOT OBSERVED"}],
        },
        {
            "section_id": "cf_claims",
            "title": "Claim Permission Matrix",
            "section_type": "body",
            "llm_text": "",
            "blocks": [{"content": "CLAIM PERMISSIONS\nNOT OBSERVED\nNONE BOUNDED"}],
        },
    ]

    gated_body, gated_appendix, policy_register, summary = _apply_section_surface_density_gate(
        body_sections=body_sections,
        appendix_sections=[],
        minimum_body_sections=1,
        min_substantive_lines=5,
        min_density_score=8,
    )

    assert [section["title"] for section in gated_body] == ["Executive Structural Brief"]
    assert any(section["title"] == "Claim Permission Matrix" for section in gated_appendix)
    executive_row = next(row for row in policy_register if row["section_id"] == "cf_exec")
    assert executive_row["policy_state"] == "retained_body_core_section"
    assert summary["retained_protected_count"] == 1


def test_section_strategic_surface_gate_demotes_low_value_optional_sections_when_body_is_already_strong():
    body_sections = [
        {
            "section_id": "cf_exec",
            "title": "Executive Structural Brief",
            "section_type": "body",
            "outline_section_key": "executive_structural_thesis",
            "thesis_anchor_type": "dominant_contradiction",
            "blocks": [{"content": "Dominant Contradiction\nReframed Problem\nFinancial Exposure\nStrategic Gold Nugget"}],
        },
        {
            "section_id": "cf_vars",
            "title": "Dominant Variables",
            "section_type": "body",
            "outline_section_key": "dominant_variables",
            "thesis_anchor_type": "dominant_contradiction",
            "blocks": [{"content": "Dominant Variables\nWrong variable\nMinimum Evidence\nDecision Front"}],
        },
        {
            "section_id": "cf_peer",
            "title": "Competitive / Peer Comparison",
            "section_type": "body",
            "outline_section_key": "peer_comparison",
            "thesis_anchor_type": "dominant_contradiction",
            "blocks": [{"content": "Peer Requirement\nBetter-Practice\nInvalid Comparison Risk\nPeer Superiority Block"}],
        },
        {
            "section_id": "cf_fin",
            "title": "Financial Exposure Under Uncertainty",
            "section_type": "body",
            "outline_section_key": "financial_exposure",
            "thesis_anchor_type": "dominant_contradiction",
            "blocks": [{"content": "Financial Exposure\nCapital Logic\nWrong boundary\nMinimum Evidence"}],
        },
        {
            "section_id": "cf_tad",
            "title": "TAD — Action Priority",
            "section_type": "body",
            "outline_section_key": "tad",
            "thesis_anchor_type": "minimum_discriminating_evidence",
            "blocks": [{"content": "Decision Front\nTrigger Family\nNo-Go Class\nFinancial Exposure"}],
        },
        {
            "section_id": "cf_trace",
            "title": "Source Traceability",
            "section_type": "body",
            "blocks": [{"content": "Source register\nReference packet\nTrace notes"}],
        },
    ]
    gated_body, gated_appendix, policy_register, summary = _apply_section_strategic_surface_gate(
        body_sections=body_sections,
        appendix_sections=[],
        minimum_body_sections=5,
        minimum_high_value_sections=4,
    )

    assert [section["title"] for section in gated_body] == [
        "Executive Structural Brief",
        "Dominant Variables",
        "Competitive / Peer Comparison",
        "Financial Exposure Under Uncertainty",
        "TAD — Action Priority",
    ]
    assert any(section["title"] == "Source Traceability" for section in gated_appendix)
    strategic_row = next(row for row in policy_register if row["section_id"] == "cf_trace")
    assert strategic_row["policy_state"] == "demoted_low_value_optional_section_to_appendix"
    assert strategic_row["destination_surface"] == "appendix"
    assert summary["demoted_to_appendix_count"] == 1


def test_section_strategic_surface_gate_respects_required_body_titles_for_optional_sections():
    body_sections = [
        {
            "section_id": "cf_trace",
            "title": "Source Traceability",
            "section_type": "body",
            "blocks": [{"content": "Source register\nReference packet\nTrace notes"}],
        }
    ]
    gated_body, gated_appendix, policy_register, summary = _apply_section_strategic_surface_gate(
        body_sections=body_sections,
        appendix_sections=[],
        required_body_titles={"Source Traceability"},
        minimum_body_sections=1,
        minimum_high_value_sections=1,
    )

    assert [section["title"] for section in gated_body] == ["Source Traceability"]
    assert gated_appendix == []
    strategic_row = next(row for row in policy_register if row["section_id"] == "cf_trace")
    assert strategic_row["policy_state"] == "retained_strategic_core_section"
    assert summary["retained_protected_count"] == 1


def test_section_strategic_redundancy_gate_demotes_optional_sections_that_repeat_the_retained_spine():
    body_sections = [
        {
            "section_id": "cf_exec",
            "title": "Executive Structural Brief",
            "section_type": "body",
            "outline_section_key": "executive_structural_thesis",
            "thesis_anchor_type": "dominant_contradiction",
            "thesis_anchor_text": "wrong denominator and wrong variable",
            "section_surface_strategic_profile": {"strategic_value_tier": "thesis_critical"},
            "blocks": [{"content": "Wrong denominator\nWrong variable\nFinancial exposure\nMinimum evidence"}],
        },
        {
            "section_id": "cf_peer",
            "title": "Competitive / Peer Comparison",
            "section_type": "body",
            "outline_section_key": "peer_comparison",
            "thesis_anchor_type": "dominant_contradiction",
            "thesis_anchor_text": "fair comparison requirement",
            "section_surface_strategic_profile": {"strategic_value_tier": "strategic_support"},
            "blocks": [{"content": "Peer requirement\nInvalid comparison risk\nBetter-practice delta"}],
        },
        {
            "section_id": "cf_tad",
            "title": "TAD — Action Priority",
            "section_type": "body",
            "outline_section_key": "tad",
            "thesis_anchor_type": "minimum_discriminating_evidence",
            "thesis_anchor_text": "request minimum evidence",
            "section_surface_strategic_profile": {"strategic_value_tier": "strategic_support"},
            "blocks": [{"content": "Decision front\nTrigger family\nNo-Go class\nMinimum evidence"}],
        },
        {
            "section_id": "cf_trace",
            "title": "Source Traceability",
            "section_type": "body",
            "section_surface_strategic_profile": {"strategic_value_tier": "surface_optional"},
            "blocks": [{"content": "Wrong denominator\nWrong variable\nMinimum evidence\nFinancial exposure"}],
        },
    ]

    gated_body, gated_appendix, policy_register, summary = _apply_section_strategic_redundancy_gate(
        body_sections=body_sections,
        appendix_sections=[],
        minimum_body_sections=3,
        minimum_high_value_sections=2,
        redundancy_overlap_threshold=0.5,
    )

    assert [section["title"] for section in gated_body] == [
        "Executive Structural Brief",
        "Competitive / Peer Comparison",
        "TAD — Action Priority",
    ]
    assert any(section["title"] == "Source Traceability" for section in gated_appendix)
    redundancy_row = next(row for row in policy_register if row["section_id"] == "cf_trace")
    assert redundancy_row["policy_state"] == "demoted_redundant_optional_section_to_appendix"
    assert redundancy_row["destination_surface"] == "appendix"
    assert redundancy_row["highly_redundant"] is True
    assert summary["demoted_to_appendix_count"] == 1


def test_section_strategic_redundancy_gate_keeps_optional_section_when_overlap_is_low():
    body_sections = [
        {
            "section_id": "cf_exec",
            "title": "Executive Structural Brief",
            "section_type": "body",
            "outline_section_key": "executive_structural_thesis",
            "thesis_anchor_type": "dominant_contradiction",
            "thesis_anchor_text": "wrong denominator and wrong variable",
            "section_surface_strategic_profile": {"strategic_value_tier": "thesis_critical"},
            "blocks": [{"content": "Wrong denominator\nWrong variable\nFinancial exposure\nMinimum evidence"}],
        },
        {
            "section_id": "cf_trace",
            "title": "Source Traceability",
            "section_type": "body",
            "section_surface_strategic_profile": {"strategic_value_tier": "surface_optional"},
            "blocks": [{"content": "Provider family\nreference packet\nsource lineage\narticle register"}],
        },
    ]

    gated_body, gated_appendix, policy_register, summary = _apply_section_strategic_redundancy_gate(
        body_sections=body_sections,
        appendix_sections=[],
        minimum_body_sections=2,
        minimum_high_value_sections=1,
        redundancy_overlap_threshold=0.5,
    )

    assert [section["title"] for section in gated_body] == [
        "Executive Structural Brief",
        "Source Traceability",
    ]
    assert gated_appendix == []
    redundancy_row = next(row for row in policy_register if row["section_id"] == "cf_trace")
    assert redundancy_row["policy_state"] == "retained_low_value_but_nonredundant_section"
    assert redundancy_row["highly_redundant"] is False
    assert summary["retained_low_overlap_count"] == 1


def test_section_inventory_surface_gate_demotes_registry_like_optional_sections_when_body_is_already_strong():
    body_sections = [
        {
            "section_id": "cf_exec",
            "title": "Executive Structural Brief",
            "section_type": "body",
            "outline_section_key": "executive_structural_thesis",
            "section_surface_strategic_profile": {"strategic_value_tier": "thesis_critical", "strategic_signal_hits": 4},
            "blocks": [{"content": "Wrong denominator\nWrong variable\nCapital logic\nMinimum evidence"}],
        },
        {
            "section_id": "cf_peer",
            "title": "Competitive / Peer Comparison",
            "section_type": "body",
            "outline_section_key": "peer_comparison",
            "section_surface_strategic_profile": {"strategic_value_tier": "strategic_support", "strategic_signal_hits": 4},
            "blocks": [{"content": "Peer requirement\nInvalid comparison risk\nBetter-practice delta"}],
        },
        {
            "section_id": "cf_fin",
            "title": "Financial Exposure Under Uncertainty",
            "section_type": "body",
            "outline_section_key": "financial_exposure",
            "section_surface_strategic_profile": {"strategic_value_tier": "strategic_support", "strategic_signal_hits": 4},
            "blocks": [{"content": "Capital logic\nWrong boundary\nMinimum evidence"}],
        },
        {
            "section_id": "cf_tad",
            "title": "TAD — Action Priority",
            "section_type": "body",
            "outline_section_key": "tad",
            "section_surface_strategic_profile": {"strategic_value_tier": "strategic_support", "strategic_signal_hits": 4},
            "blocks": [{"content": "Decision front\nTrigger family\nNo-Go class"}],
        },
        {
            "section_id": "cf_trace",
            "title": "Source Traceability",
            "section_type": "body",
            "section_surface_strategic_profile": {"strategic_value_tier": "surface_optional", "strategic_signal_hits": 0},
            "blocks": [{"content": "Status: blocked\nProvider Family: scopus\nReference Packet: 4 items"}],
        },
    ]

    gated_body, gated_appendix, policy_register, summary = _apply_section_inventory_surface_gate(
        body_sections=body_sections,
        appendix_sections=[],
        minimum_body_sections=4,
        minimum_high_value_sections=3,
    )

    assert [section["title"] for section in gated_body] == [
        "Executive Structural Brief",
        "Competitive / Peer Comparison",
        "Financial Exposure Under Uncertainty",
        "TAD — Action Priority",
    ]
    assert any(section["title"] == "Source Traceability" for section in gated_appendix)
    inventory_row = next(row for row in policy_register if row["section_id"] == "cf_trace")
    assert inventory_row["policy_state"] == "demoted_inventory_like_optional_section_to_appendix"
    assert inventory_row["destination_surface"] == "appendix"
    assert inventory_row["inventory_heavy"] is True
    assert summary["demoted_to_appendix_count"] == 1


def test_section_inventory_surface_gate_keeps_optional_section_when_strategic_readout_is_present():
    body_sections = [
        {
            "section_id": "cf_exec",
            "title": "Executive Structural Brief",
            "section_type": "body",
            "outline_section_key": "executive_structural_thesis",
            "section_surface_strategic_profile": {"strategic_value_tier": "thesis_critical", "strategic_signal_hits": 4},
            "blocks": [{"content": "Wrong denominator\nWrong variable\nCapital logic\nMinimum evidence"}],
        },
        {
            "section_id": "cf_trace",
            "title": "Source Traceability",
            "section_type": "body",
            "section_surface_strategic_profile": {"strategic_value_tier": "surface_optional", "strategic_signal_hits": 0},
            "section_surface_readout_register": [{"label": "Evidence Pivot", "value": "Dock cycle logs"}],
            "blocks": [{"content": "Status: partial\nProvider Family: utility\nReference Packet: 2 items"}],
        },
    ]

    gated_body, gated_appendix, policy_register, summary = _apply_section_inventory_surface_gate(
        body_sections=body_sections,
        appendix_sections=[],
        minimum_body_sections=2,
        minimum_high_value_sections=1,
    )

    assert [section["title"] for section in gated_body] == [
        "Executive Structural Brief",
        "Source Traceability",
    ]
    assert gated_appendix == []
    inventory_row = next(row for row in policy_register if row["section_id"] == "cf_trace")
    assert inventory_row["policy_state"] == "retained_optional_section_with_readout_surface"
    assert inventory_row["readout_signal_count"] == 1
    assert summary["retained_readout_surface_count"] == 1


def test_hydrated_system_consistency_section_uses_motor_036_results():
    body_sections = [
        {
            "section_id": "c17_system_consistency_check",
            "chapter_id": "C17",
            "title": "System Consistency Check",
            "blocks": [{"block_id": "b_structural_system_consistency_check", "content": "placeholder"}],
            "block_ref": "b_structural_system_consistency_check",
        }
    ]
    hydrated = _hydrated_system_consistency_section(
        body_sections,
        {
            "can_render_pdf": True,
            "critical_failure_count": 0,
            "checks": [
                {"check_id": "claim_summary_vs_matrix", "passed": True, "severity": "critical"},
                {"check_id": "scenario_vs_evidence_contract", "passed": True, "severity": "critical"},
            ],
        },
    )
    content = hydrated[0]["blocks"][0]["content"]
    assert "Final Consistency Status : PASSED" in content
    assert "[claim_summary_vs_matrix] critical" in content
    assert "[scenario_vs_evidence_contract] critical" in content
