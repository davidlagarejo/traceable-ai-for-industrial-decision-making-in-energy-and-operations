from __future__ import annotations

from runtime_orchestrator.zlab_skill import (
    build_reference_resolution_prefill,
    parse_query_seed_notes,
)


def test_parse_query_seed_notes_extracts_structured_fields() -> None:
    parsed = parse_query_seed_notes(
        "Query-seed candidate for combination latent::combo::warehouse::01. "
        "Query family: tariff_demand_peak. "
        "Primary query: warehouse demand charge peak timing. "
        "Pivot query: warehouse tariff orchestration. "
        "Evidence targets: utility tariff, billing demand, interval load profile. "
        "Search intent: Find structural evidence that timing and tariff dominate annual kWh narratives."
    )

    assert parsed["combination_id"] == "latent::combo::warehouse::01"
    assert parsed["query_family"] == "tariff_demand_peak"
    assert parsed["primary_query"] == "warehouse demand charge peak timing"
    assert parsed["pivot_query"] == "warehouse tariff orchestration"
    assert parsed["evidence_targets"] == [
        "utility tariff",
        "billing demand",
        "interval load profile",
    ]


def test_build_reference_resolution_prefill_uses_candidate_and_reference_context() -> None:
    prefill = build_reference_resolution_prefill(
        candidate_row={
            "candidate_id": "queryseed-scopus-01",
            "provider_key": "scopus",
            "title": "Research lead · Scopus · tariff demand peak",
            "source_url": "https://www.scopus.com/",
            "keywords": ["demand charge", "load shifting"],
            "metadata_payload": {
                "provider_key": "scopus",
                "title": "Research lead · Scopus · tariff demand peak",
                "source_url": "https://www.scopus.com/",
                "notes": (
                    "Query-seed candidate for combination latent::combo::warehouse::01. "
                    "Query family: tariff_demand_peak. "
                    "Primary query: warehouse demand charge peak timing. "
                    "Pivot query: warehouse tariff orchestration. "
                    "Evidence targets: utility tariff, billing demand, interval load profile."
                ),
            },
        },
        reference_record={
            "candidate_id": "queryseed-scopus-01",
            "provider_key": "scopus",
            "reference_state": "query_seed_draft",
            "acquisition_result": {
                "search_brief": "Research lead summary for tariff demand peak.",
            },
        },
    )

    assert prefill["provider_key"] == "scopus"
    assert prefill["query_family"] == "tariff_demand_peak"
    assert prefill["primary_query"] == "warehouse demand charge peak timing"
    assert prefill["pivot_query"] == "warehouse tariff orchestration"
    assert prefill["search_brief"] == "Research lead summary for tariff demand peak."
    assert prefill["accept_for_reference_use_recommended"] is True
    assert "Primary query:" in prefill["suggested_notes"]
