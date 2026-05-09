from runtime_orchestrator.zlab_skill import (
    build_combination_campaign_execution_manifest_register,
    build_combination_follow_on_research_register,
    build_provider_query_template_rows,
    build_research_campaign_record,
    build_research_campaign_trigger_register,
    build_source_family_coverage_register,
)


def test_source_family_coverage_register_tracks_touched_and_missing_families() -> None:
    rows = build_source_family_coverage_register(
        provider_session_register=[
            {"provider_key": "scopus", "source_family": "licensed_research_discovery"},
            {"provider_key": "ieee", "source_family": "licensed_research_fulltext"},
            {"provider_key": "ashrae", "source_family": "public_technical_guidance"},
        ],
        discovery_candidate_review_register=[
            {"candidate_id": "cand-1", "provider_key": "scopus"},
        ],
        article_reference_register=[
            {"candidate_id": "cand-1", "provider_key": "ieee", "source_url": "https://ieeexplore.ieee.org/document/1"},
        ],
        extraction_records=[
            {"id": "extract-1", "provider_key": "ieee", "document_ref": "10.1109/TIA.1"},
        ],
        knowledge_atom_register=[
            {
                "atom_id": "atom-1",
                "provider_key": "ieee",
                "document_ref": "10.1109/TIA.1",
            }
        ],
        mode="standard",
    )

    by_family = {row["source_family"]: row for row in rows}
    assert by_family["licensed_research_discovery"]["coverage_state"] == "thin"
    assert by_family["licensed_research_fulltext"]["coverage_state"] == "thin"
    assert by_family["public_technical_guidance"]["coverage_state"] == "untouched"


def test_source_family_coverage_register_respects_explicit_nonpaper_source_family() -> None:
    rows = build_source_family_coverage_register(
        provider_session_register=[
            {"provider_key": "manual", "source_family": "specialist_web_case_signal"},
            {"provider_key": "ashrae", "source_family": "public_technical_guidance"},
        ],
        discovery_candidate_review_register=[
            {
                "candidate_id": "cand-tariff-1",
                "provider_key": "manual",
                "source_family": "utility_tariff_billing_guidance",
            },
            {
                "candidate_id": "cand-oem-1",
                "provider_key": "manual",
                "metadata_payload": {"source_family": "oem_handbook_technical_manuals"},
            },
        ],
        article_reference_register=[
            {
                "candidate_id": "cand-reg-1",
                "provider_key": "manual",
                "source_family": "regulatory_code_compliance_guidance",
                "source_url": "https://example.com/code-guide",
            },
        ],
        extraction_records=[],
        knowledge_atom_register=[
            {
                "atom_id": "atom-web-1",
                "provider_key": "manual",
                "source_family": "specialist_web_case_signal",
                "document_ref": "https://example.com/case-signal",
            }
        ],
        mode="standard",
    )

    by_family = {row["source_family"]: row for row in rows}
    assert by_family["utility_tariff_billing_guidance"]["coverage_state"] == "thin"
    assert by_family["utility_tariff_billing_guidance"]["capture_mode"] == "manual_reference_capture"
    assert "tariff_demand_peak" in by_family["utility_tariff_billing_guidance"]["preferred_query_families"]
    assert by_family["oem_handbook_technical_manuals"]["coverage_state"] == "thin"
    assert by_family["regulatory_code_compliance_guidance"]["coverage_state"] == "thin"
    assert by_family["specialist_web_case_signal"]["coverage_state"] == "thin"


def test_research_campaign_record_summarizes_campaign_status() -> None:
    campaign = build_research_campaign_record(
        run_id="run:campaign",
        asset_context_vector={
            "asset_family": "logistics_warehouse",
            "context_signature": "family-logistics-warehouse",
        },
        source_family_coverage_register=[
            {"source_family": "licensed_research_discovery", "coverage_state": "thin"},
            {"source_family": "licensed_research_fulltext", "coverage_state": "strong"},
            {"source_family": "public_technical_guidance", "coverage_state": "untouched"},
        ],
        source_coverage_summary={
            "coverage_strength": "moderate",
            "knowledge_atom_count": 8,
            "document_count": 3,
            "provider_count": 2,
        },
        combination_search_gap_record={
            "search_status": "incomplete_under_investigated",
            "latent_candidate_count": 18,
            "admissible_candidate_count": 5,
            "recommended_actions": ["Expand the source campaign before concluding that the case has no plausible combinations."],
        },
        mode="standard",
    )

    assert campaign["campaign_status"] == "coverage_building"
    assert campaign["touched_source_family_count"] == 2
    assert campaign["missing_source_family_count"] == 1
    assert campaign["top_next_actions"]


def test_research_campaign_trigger_register_merges_plans_with_persisted_queue() -> None:
    rows = build_research_campaign_trigger_register(
        source_family_coverage_register=[
            {
                "source_family": "licensed_research_fulltext",
                "display_name": "Licensed full text",
                "coverage_state": "thin",
                "importance": "high",
                "available_provider_keys": ["ieee", "springer"],
                "touched_provider_keys": ["ieee"],
                "document_count": 1,
                "reference_count": 1,
                "candidate_count": 2,
                "knowledge_atom_count": 2,
                "target_document_count": 4,
                "target_knowledge_atom_count": 8,
            }
        ],
        research_campaign_record={
            "mode": "standard",
            "campaign_status": "coverage_building",
        },
        stored_trigger_records=[
            {
                "source_family": "licensed_research_fulltext",
                "status": "queued",
                "reason": "Queue more IEEE and Springer full text.",
                "recommended_provider_keys": ["ieee", "springer"],
                "target_document_delta": 3,
                "target_knowledge_atom_delta": 6,
                "queued_at": "2026-05-05T00:00:00Z",
                "updated_at": "2026-05-05T00:00:00Z",
            }
        ],
    )

    assert len(rows) == 1
    row = rows[0]
    assert row["source_family"] == "licensed_research_fulltext"
    assert row["status"] == "queued"
    assert row["queued"] is True
    assert row["recommended_provider_keys"] == ["ieee", "springer"]
    assert row["target_document_delta"] == 3
    assert row["target_knowledge_atom_delta"] == 6
    assert row["reason"] == "Queue more IEEE and Springer full text."


def test_source_family_trigger_plan_exposes_nonpaper_capture_contract() -> None:
    row = build_research_campaign_trigger_register(
        source_family_coverage_register=[
            {
                "source_family": "utility_tariff_billing_guidance",
                "display_name": "Utility / tariff / billing guidance",
                "coverage_state": "untouched",
                "importance": "high",
                "available_provider_keys": [],
                "touched_provider_keys": [],
                "document_count": 0,
                "reference_count": 0,
                "candidate_count": 0,
                "knowledge_atom_count": 0,
                "target_document_count": 3,
                "target_knowledge_atom_count": 4,
                "capture_mode": "manual_reference_capture",
                "admissible_capture_fields": ["source_url", "title_or_snippet", "tariff_terms", "notes"],
                "atomization_priority": "tariff_and_billing_translation",
                "preferred_query_families": ["tariff_demand_peak", "reactive_power_quality"],
                "search_focus": "Collect utility tariff sheets and billing guides.",
            }
        ],
        research_campaign_record={
            "mode": "standard",
            "campaign_status": "coverage_building",
        },
        stored_trigger_records=[],
    )[0]

    assert row["source_family"] == "utility_tariff_billing_guidance"
    assert row["capture_mode"] == "manual_reference_capture"
    assert row["atomization_priority"] == "tariff_and_billing_translation"
    assert row["preferred_query_families"] == ["tariff_demand_peak", "reactive_power_quality"]
    assert row["recommended_provider_keys"] == ["manual", "doe", "epa"]


def test_combination_follow_on_research_register_recommends_source_families() -> None:
    rows = build_combination_follow_on_research_register(
        combination_review_sequence_register=[
            {
                "combination_id": "combo::tariff_boundary",
                "combination_name": "Tariff Boundary Combo",
                "combined_hypothesis": "Peak demand and owner/operator boundary may both matter.",
                "pattern_layers": ["financial_translation", "fair_comparison_rule"],
                "pattern_ids": ["warehouse_mhe_charging_demand_peak", "value_boundary_leakage_owner_operator"],
                "minimum_evidence": ["utility bills", "lease matrix"],
                "knowledge_atom_count": 0,
                "supporting_document_refs": [],
            }
        ],
        source_family_coverage_register=[
            {
                "source_family": "licensed_research_discovery",
                "display_name": "Licensed discovery",
                "coverage_state": "thin",
                "available_provider_keys": ["scopus"],
                "touched_provider_keys": ["scopus"],
                "document_count": 1,
                "reference_count": 1,
                "candidate_count": 2,
                "knowledge_atom_count": 1,
                "target_document_count": 10,
                "target_knowledge_atom_count": 6,
            },
            {
                "source_family": "licensed_research_fulltext",
                "display_name": "Licensed full text",
                "coverage_state": "thin",
                "available_provider_keys": ["ieee", "springer"],
                "touched_provider_keys": ["ieee"],
                "document_count": 1,
                "reference_count": 1,
                "candidate_count": 1,
                "knowledge_atom_count": 1,
                "target_document_count": 4,
                "target_knowledge_atom_count": 8,
            },
            {
                "source_family": "public_technical_guidance",
                "display_name": "Public technical guidance",
                "coverage_state": "untouched",
                "available_provider_keys": ["ashrae"],
                "touched_provider_keys": [],
                "document_count": 0,
                "reference_count": 0,
                "candidate_count": 0,
                "knowledge_atom_count": 0,
                "target_document_count": 3,
                "target_knowledge_atom_count": 3,
            },
        ],
        research_campaign_record={
            "mode": "standard",
            "campaign_status": "coverage_building",
        },
    )

    assert len(rows) == 1
    row = rows[0]
    assert "licensed_research_discovery" in row["recommended_source_families"]
    assert "licensed_research_fulltext" in row["recommended_source_families"]
    assert "public_technical_guidance" in row["recommended_source_families"]
    assert row["trigger_rows"]


def test_combination_campaign_execution_manifest_register_builds_query_families_and_execution_rows() -> None:
    rows = build_combination_campaign_execution_manifest_register(
        combination_follow_on_research_register=[
            {
                "combination_id": "combo::tariff_boundary",
                "combination_name": "Tariff Boundary Combo",
                "combined_hypothesis": "Peak demand and owner/operator boundary may both matter.",
                "strategic_risk": "Wrong CAPEX against tariff and boundary.",
                "pattern_ids": ["warehouse_mhe_charging_demand_peak", "value_boundary_leakage_owner_operator"],
                "minimum_evidence": ["utility bills", "lease matrix"],
                "recommended_source_families": ["licensed_research_discovery", "licensed_research_fulltext"],
                "reasoning_flags": ["thin_combination_support"],
                "trigger_rows": [
                    {
                        "source_family": "licensed_research_discovery",
                        "display_name": "Licensed discovery",
                        "recommended_provider_keys": ["scopus"],
                        "target_document_delta": 5,
                        "target_knowledge_atom_delta": 3,
                        "search_focus": "Search for more candidate papers.",
                    },
                    {
                        "source_family": "licensed_research_fulltext",
                        "display_name": "Licensed full text",
                        "recommended_provider_keys": ["ieee", "springer"],
                        "target_document_delta": 2,
                        "target_knowledge_atom_delta": 5,
                        "search_focus": "Read deeper full text.",
                    },
                ],
            }
        ],
        source_family_coverage_register=[
            {
                "source_family": "licensed_research_discovery",
                "available_provider_keys": ["scopus"],
                "importance": "high",
            },
            {
                "source_family": "licensed_research_fulltext",
                "available_provider_keys": ["ieee", "springer"],
                "importance": "high",
            },
        ],
    )

    assert len(rows) == 1
    row = rows[0]
    assert "tariff_demand_peak" in row["query_families"]
    assert "owner_operator_boundary" in row["query_families"]
    assert row["provider_query_template_count"] >= 2
    assert row["execution_rows"]
    assert row["execution_rows"][0]["provider_targets"]
    assert row["execution_rows"][0]["provider_query_templates"]
    assert row["execution_rows"][0]["provider_query_templates"][0]["primary_query"]


def test_combination_campaign_execution_manifest_register_merges_source_family_query_biases() -> None:
    rows = build_combination_campaign_execution_manifest_register(
        combination_follow_on_research_register=[
            {
                "combination_id": "combo::utility_boundary",
                "combination_name": "Utility Boundary Combo",
                "combined_hypothesis": "Tariff and owner/operator boundary may distort the apparent driver.",
                "strategic_risk": "Wrong capital allocation against tariff structure.",
                "pattern_ids": ["warehouse_mhe_charging_demand_peak", "value_boundary_leakage_owner_operator"],
                "minimum_evidence": ["utility tariff", "lease matrix"],
                "recommended_source_families": ["utility_tariff_billing_guidance"],
                "reasoning_flags": ["thin_combination_support"],
                "trigger_rows": [
                    {
                        "source_family": "utility_tariff_billing_guidance",
                        "display_name": "Utility / tariff / billing guidance",
                        "recommended_provider_keys": ["manual"],
                        "target_document_delta": 2,
                        "target_knowledge_atom_delta": 3,
                        "search_focus": "Collect tariff guides.",
                        "preferred_query_families": ["tariff_demand_peak", "reactive_power_quality"],
                    }
                ],
            }
        ],
        source_family_coverage_register=[
            {
                "source_family": "utility_tariff_billing_guidance",
                "available_provider_keys": ["manual"],
                "importance": "high",
            }
        ],
    )

    execution_row = rows[0]["execution_rows"][0]
    assert execution_row["source_family"] == "utility_tariff_billing_guidance"
    assert "tariff_demand_peak" in execution_row["query_families"]
    assert "reactive_power_quality" in execution_row["query_families"]


def test_build_provider_query_template_rows_generates_provider_specific_queries() -> None:
    rows = build_provider_query_template_rows(
        provider_targets=["scopus", "ieee", "ashrae"],
        source_family="licensed_research_fulltext",
        query_families=["tariff_demand_peak", "owner_operator_boundary"],
        combination_row={
            "combination_name": "Warehouse tariff and owner boundary combo",
            "combined_hypothesis": "Warehouse charging demand and owner/operator split may both drive the case.",
            "pattern_ids": [
                "warehouse_mhe_charging_demand_peak",
                "value_boundary_leakage_owner_operator",
            ],
        },
    )

    assert rows
    scopus_row = next(row for row in rows if row["provider_key"] == "scopus" and row["query_family"] == "tariff_demand_peak")
    ieee_row = next(row for row in rows if row["provider_key"] == "ieee" and row["query_family"] == "owner_operator_boundary")
    ashrae_row = next(row for row in rows if row["provider_key"] == "ashrae" and row["query_family"] == "tariff_demand_peak")
    assert scopus_row["search_surface"] == "TITLE-ABS-KEY"
    assert "TITLE-ABS-KEY" in scopus_row["primary_query"]
    assert "warehouse" in scopus_row["primary_query"].lower()
    assert ieee_row["provider_display_name"] == "IEEE Xplore"
    assert "owner operator boundary" in ieee_row["execution_hint"].lower()
    assert ashrae_row["provider_display_name"] == "ASHRAE"
    assert ashrae_row["primary_query"]
