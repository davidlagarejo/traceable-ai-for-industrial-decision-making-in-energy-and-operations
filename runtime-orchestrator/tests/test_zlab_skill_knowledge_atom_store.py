from runtime_orchestrator.zlab_skill import build_knowledge_atom_register


def test_build_knowledge_atom_register_derives_nonpaper_atoms_from_visible_references() -> None:
    rows = build_knowledge_atom_register(
        extraction_records=[],
        article_reference_register=[
            {
                "candidate_id": "cand-tariff-01",
                "provider_key": "manual",
                "source_family": "utility_tariff_billing_guidance",
                "title": "Utility tariff guide",
                "source_url": "https://utility.example.com/tariff-guide",
                "reference_state": "manual_text_enriched",
                "reference_excerpt": (
                    "Demand charge timing and billing windows can dominate cost even "
                    "when annual kWh is not extreme."
                ),
                "matched_pattern_ids": ["demand_charge_exposure_unknown"],
                "matched_combination_ids": ["warehouse_tariff_boundary_area_combo"],
                "acquisition_result": {"status": "query_seed_manual_capture"},
            }
        ],
    )

    assert len(rows) == 1
    row = rows[0]
    assert row["source_family"] == "utility_tariff_billing_guidance"
    assert row["knowledge_type"] == "FINANCIAL_TRANSLATION"
    assert row["confidence_ceiling"] == "L2"
    assert row["review_status"] == "manual_text_enriched"
    assert row["supported_pattern_ids"] == ["demand_charge_exposure_unknown"]
    assert row["supported_combination_ids"] == ["warehouse_tariff_boundary_area_combo"]

