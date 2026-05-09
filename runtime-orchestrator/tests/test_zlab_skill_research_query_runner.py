from __future__ import annotations

from runtime_orchestrator.zlab_skill import (
    build_query_seed_candidate_records,
    build_search_query_result_option_batch_plan,
    build_search_query_result_option_register,
    build_search_query_result_option_review_sequence,
    build_search_query_execution_batch_plan,
    build_search_query_execution_register,
    build_search_query_execution_sequence,
    build_search_result_capture_register,
    build_search_result_capture_sequence,
)


def test_build_query_seed_candidate_records_materializes_provider_templates() -> None:
    rows = build_query_seed_candidate_records(
        combination_id="latent::combo::warehouse::01",
        follow_on_manifest_row={
            "combination_name": "Warehouse latent combo",
            "execution_rows": [
                {
                    "source_family": "licensed_research_discovery",
                    "provider_query_templates": [
                        {
                            "provider_key": "scopus",
                            "provider_display_name": "Scopus",
                            "query_family": "tariff_demand_peak",
                            "primary_query": "warehouse demand charge peak timing",
                            "pivot_query": "warehouse tariff orchestration",
                            "search_intent": "Find tariff-timing evidence.",
                            "search_surface": "TITLE-ABS-KEY",
                            "execution_hint": "Start in discovery before full text.",
                            "evidence_targets": ["utility tariff", "billing demand"],
                            "seed_terms": ["demand charge", "peak timing"],
                            "asset_focus_terms": ["warehouse", "mhe charging"],
                        }
                    ],
                }
            ],
        },
        default_launch_url_builder=lambda provider_key: f"https://example.com/{provider_key}",
        current_year=2026,
    )

    assert len(rows) == 1
    row = rows[0]
    assert row["candidate_id"] == "queryseed-scopus-latent__combo__warehouse__01-tariff_demand_peak"
    assert row["source_url"] == "https://example.com/scopus"
    assert row["launch_url"] == "https://example.com/scopus"
    assert row["published_year"] == "2026"
    assert row["query_family"] == "tariff_demand_peak"
    assert "Source family: licensed_research_discovery." in row["notes"]
    assert "Primary query: warehouse demand charge peak timing." in row["notes"]


def test_build_search_result_capture_register_tracks_query_seed_capture_states() -> None:
    register = build_search_result_capture_register(
        discovery_candidate_review_register=[
            {
                "candidate_id": "queryseed-a",
                "provider_key": "scopus",
                "title": "A lead",
                "metadata_payload": {
                    "provider_key": "scopus",
                    "title": "A lead",
                    "notes": (
                        "Query-seed candidate for combination latent::combo::warehouse::01. "
                        "Query family: tariff_demand_peak. "
                        "Primary query: warehouse demand charge peak timing. "
                        "Pivot query: warehouse tariff orchestration. "
                        "Evidence targets: utility tariff, billing demand."
                    ),
                },
            },
            {
                "candidate_id": "queryseed-b",
                "provider_key": "scopus",
                "title": "B lead",
                "metadata_payload": {
                    "provider_key": "scopus",
                    "title": "B lead",
                    "notes": (
                        "Query-seed candidate for combination latent::combo::warehouse::01. "
                        "Query family: tariff_demand_peak. "
                        "Primary query: warehouse demand charge peak timing."
                    ),
                },
            },
            {
                "candidate_id": "queryseed-c",
                "provider_key": "ieee",
                "title": "C lead",
                "metadata_payload": {
                    "provider_key": "ieee",
                    "title": "C lead",
                    "notes": (
                        "Query-seed candidate for combination latent::combo::warehouse::01. "
                        "Query family: owner_operator_boundary. "
                        "Primary query: warehouse owner operator utility boundary."
                    ),
                },
            },
            {
                "candidate_id": "queryseed-d",
                "provider_key": "springer",
                "title": "D lead",
                "metadata_payload": {
                    "provider_key": "springer",
                    "title": "D lead",
                    "notes": (
                        "Query-seed candidate for combination latent::combo::warehouse::01. "
                        "Query family: dock_infiltration_interface. "
                        "Primary query: dock door infiltration warehouse."
                    ),
                },
            },
            {
                "candidate_id": "manual-01",
                "provider_key": "manual",
                "title": "Non query seed",
            },
        ],
        article_reference_register=[
            {
                "candidate_id": "queryseed-b",
                "provider_key": "scopus",
                "reference_state": "query_seed_draft",
                "acquisition_result": {
                    "search_brief": "Need result capture.",
                },
            },
            {
                "candidate_id": "queryseed-c",
                "provider_key": "ieee",
                "reference_state": "query_seed_draft",
                "acquisition_result": {
                    "status": "query_seed_result_captured",
                    "search_result_title": "IEEE result title",
                    "search_result_snippet": "Visible result snippet.",
                },
            },
            {
                "candidate_id": "queryseed-d",
                "provider_key": "springer",
                "reference_state": "manual_text_enriched",
                "acquisition_result": {
                    "status": "query_seed_manual_capture",
                    "visible_text": "Resolved excerpt.",
                },
            },
        ],
    )

    by_id = {row["candidate_id"]: row for row in register}
    assert set(by_id) == {"queryseed-a", "queryseed-b", "queryseed-c", "queryseed-d"}
    assert by_id["queryseed-a"]["capture_state"] == "needs_draft"
    assert by_id["queryseed-a"]["next_capture_action"] == "READ_OR_DRAFT_REFERENCE"
    assert by_id["queryseed-b"]["capture_state"] == "seed_only"
    assert by_id["queryseed-b"]["next_capture_action"] == "CAPTURE_SEARCH_RESULT"
    assert by_id["queryseed-c"]["capture_state"] == "result_captured"
    assert by_id["queryseed-c"]["next_capture_action"] == "RESOLVE_REFERENCE_EXCERPT"
    assert by_id["queryseed-d"]["capture_state"] == "excerpt_resolved"
    assert by_id["queryseed-d"]["next_capture_action"] == "NO_CAPTURE_REQUIRED"
    assert by_id["queryseed-c"]["captured_result_title"] == "IEEE result title"

    sequence = build_search_result_capture_sequence(
        search_result_capture_register=register,
        batch_size=3,
    )

    assert sequence["summary"]["pending"] == 3
    assert sequence["summary"]["needs_draft"] == 1
    assert sequence["summary"]["seed_only"] == 1
    assert sequence["summary"]["result_captured"] == 1
    assert sequence["current_row"]["candidate_id"] == "queryseed-a"
    assert [row["candidate_id"] for row in sequence["next_rows"]] == ["queryseed-b", "queryseed-c"]


def test_build_search_query_execution_register_exposes_packets_and_statuses() -> None:
    capture_register = build_search_result_capture_register(
        discovery_candidate_review_register=[
            {
                "candidate_id": "queryseed-a",
                "provider_key": "scopus",
                "title": "A lead",
                "metadata_payload": {
                    "provider_key": "scopus",
                    "title": "A lead",
                    "notes": (
                        "Query-seed candidate for combination latent::combo::warehouse::01. "
                        "Query family: tariff_demand_peak. "
                        "Primary query: warehouse demand charge peak timing. "
                        "Pivot query: warehouse tariff orchestration. "
                        "Evidence targets: utility tariff, billing demand."
                    ),
                },
            },
            {
                "candidate_id": "queryseed-b",
                "provider_key": "ieee",
                "title": "B lead",
                "metadata_payload": {
                    "provider_key": "ieee",
                    "title": "B lead",
                    "notes": (
                        "Query-seed candidate for combination latent::combo::warehouse::01. "
                        "Query family: owner_operator_boundary. "
                        "Primary query: warehouse owner operator utility boundary."
                    ),
                },
            },
        ],
        article_reference_register=[
            {
                "candidate_id": "queryseed-a",
                "provider_key": "scopus",
                "reference_state": "query_seed_draft",
                "acquisition_result": {
                    "search_brief": "Need result capture.",
                },
            },
            {
                "candidate_id": "queryseed-b",
                "provider_key": "ieee",
                "reference_state": "query_seed_draft",
                "acquisition_result": {
                    "status": "query_seed_result_captured",
                    "search_result_title": "IEEE title",
                    "search_result_snippet": "IEEE snippet.",
                },
            },
        ],
    )

    register = build_search_query_execution_register(
        search_result_capture_register=capture_register,
    )
    by_id = {row["candidate_id"]: row for row in register}
    assert by_id["queryseed-a"]["execution_status"] == "search_ready_capture_pending"
    assert "Primary query:" in by_id["queryseed-a"]["search_packet_template"]
    assert "Result goal:" in by_id["queryseed-a"]["search_packet_template"]
    assert "Snippet:" in by_id["queryseed-a"]["capture_packet_template"]
    assert by_id["queryseed-b"]["execution_status"] == "result_captured_ready_for_excerpt"
    assert by_id["queryseed-b"]["captured_result_title"] == "IEEE title"

    sequence = build_search_query_execution_sequence(
        search_query_execution_register=register,
        batch_size=2,
    )
    assert sequence["summary"]["pending"] == 2
    assert sequence["summary"]["search_ready_capture_pending"] == 1
    assert sequence["summary"]["result_captured_ready_for_excerpt"] == 1
    assert sequence["current_row"]["candidate_id"] == "queryseed-a"


def test_build_search_query_result_option_register_attaches_imported_results() -> None:
    register = build_search_query_result_option_register(
        search_query_execution_register=[
            {
                "candidate_id": "queryseed-a",
                "provider_key": "scopus",
                "provider_display_name": "Scopus",
                "source_family": "licensed_research_discovery",
                "queue_status": "pending",
                "execution_status": "search_ready_capture_pending",
                "query_family": "tariff_demand_peak",
                "primary_query": "warehouse demand charge peak timing",
            },
            {
                "candidate_id": "queryseed-b",
                "provider_key": "ieee",
                "provider_display_name": "IEEE",
                "source_family": "licensed_research_fulltext",
                "queue_status": "pending",
                "execution_status": "search_ready_capture_pending",
                "query_family": "owner_operator_boundary",
                "primary_query": "warehouse owner operator utility boundary",
            },
        ],
        imported_result_records=[
            {
                "candidate_id": "queryseed-a",
                "rank": 2,
                "source_url": "https://example.com/a-2",
                "search_result_title": "A title 2",
            },
            {
                "candidate_id": "queryseed-a",
                "rank": 1,
                "source_url": "https://example.com/a-1",
                "search_result_title": "A title 1",
            },
        ],
    )

    by_id = {row["candidate_id"]: row for row in register}
    assert by_id["queryseed-a"]["imported_result_option_count"] == 2
    assert by_id["queryseed-a"]["top_imported_result"]["source_url"] == "https://example.com/a-1"
    assert by_id["queryseed-a"]["imported_result_options"][0]["option_index"] == 1
    assert by_id["queryseed-b"]["imported_result_option_count"] == 0


def test_build_search_query_result_option_review_sequence_prefers_pending_candidates_with_imported_options() -> None:
    sequence = build_search_query_result_option_review_sequence(
        search_query_execution_register=[
            {
                "candidate_id": "queryseed-a",
                "provider_key": "scopus",
                "query_family": "tariff_demand_peak",
                "queue_status": "pending",
                "execution_status": "search_ready_capture_pending",
                "imported_result_option_count": 2,
                "top_imported_result": {"search_result_title": "A top"},
                "imported_result_options": [
                    {"option_index": 1, "search_result_title": "A top 1", "source_url": "https://example.com/a-1"},
                    {"option_index": 2, "search_result_title": "A top 2", "source_url": "https://example.com/a-2"},
                ],
                "imported_result_state": "imported_options_available",
            },
            {
                "candidate_id": "queryseed-b",
                "provider_key": "ieee",
                "query_family": "owner_operator_boundary",
                "queue_status": "pending",
                "execution_status": "search_ready_capture_pending",
                "imported_result_option_count": 1,
                "top_imported_result": {"search_result_title": "B top"},
                "imported_result_options": [
                    {"option_index": 1, "search_result_title": "B top", "source_url": "https://example.com/b-1"},
                ],
                "imported_result_state": "imported_options_available",
            },
            {
                "candidate_id": "queryseed-c",
                "provider_key": "scopus",
                "query_family": "tariff_demand_peak",
                "queue_status": "pending",
                "execution_status": "result_captured_ready_for_excerpt",
                "imported_result_option_count": 3,
            },
        ],
        batch_size=3,
    )

    assert sequence["summary"]["pending"] == 3
    assert sequence["summary"]["option_count"] == 3
    assert sequence["current_row"]["candidate_id"] == "queryseed-b"
    assert sequence["current_row"]["current_option_index"] == 1
    assert sequence["current_row"]["current_imported_option"]["search_result_title"] == "B top"
    assert {row["candidate_id"] for row in sequence["rows"]} == {"queryseed-a", "queryseed-b"}


def test_build_search_query_result_option_batch_plan_prefers_same_provider_and_query() -> None:
    batch_plan = build_search_query_result_option_batch_plan(
        search_query_result_option_review_register=[
            {
                "candidate_id": "queryseed-a",
                "provider_key": "scopus",
                "source_family": "licensed_research_discovery",
                "query_family": "tariff_demand_peak",
                "current_option_index": 1,
                "option_review_id": "queryseed-a::option::1",
                "evidence_targets": ["utility tariff", "billing demand"],
            },
            {
                "candidate_id": "queryseed-b",
                "provider_key": "scopus",
                "source_family": "licensed_research_discovery",
                "query_family": "tariff_demand_peak",
                "current_option_index": 2,
                "option_review_id": "queryseed-b::option::2",
                "evidence_targets": ["utility tariff", "billing demand"],
            },
            {
                "candidate_id": "queryseed-c",
                "provider_key": "ieee",
                "source_family": "licensed_research_fulltext",
                "query_family": "owner_operator_boundary",
                "current_option_index": 1,
                "option_review_id": "queryseed-c::option::1",
                "evidence_targets": ["lease matrix"],
            },
        ],
        batch_size=2,
    )

    assert batch_plan["available"] is True
    assert batch_plan["provider_key"] == "scopus"
    assert batch_plan["query_family"] == "tariff_demand_peak"
    assert batch_plan["candidate_ids"] == ["queryseed-a", "queryseed-b"]
    assert batch_plan["option_review_ids"] == ["queryseed-a::option::1", "queryseed-b::option::2"]
    assert "\"option_index\": 1" in batch_plan["promote_records_json_template"]
    assert "json_array" in batch_plan["accepted_promote_formats"]


def test_build_search_query_execution_batch_plan_prefers_same_provider_and_query() -> None:
    register = build_search_query_execution_register(
        search_result_capture_register=[
            {
                "candidate_id": "queryseed-a",
                "provider_key": "scopus",
                "provider_display_name": "Scopus",
                "source_family": "licensed_research_discovery",
                "reference_state": "query_seed_draft",
                "capture_state": "seed_only",
                "queue_status": "pending",
                "next_capture_action": "CAPTURE_SEARCH_RESULT",
                "query_family": "tariff_demand_peak",
                "primary_query": "warehouse demand charge peak timing",
                "pivot_query": "warehouse tariff orchestration",
                "search_intent": "Find tariff timing evidence.",
                "launch_url": "https://www.scopus.com/",
                "search_surface": "TITLE-ABS-KEY",
                "execution_hint": "Search discovery first.",
                "evidence_targets": ["utility tariff", "billing demand"],
            },
            {
                "candidate_id": "queryseed-b",
                "provider_key": "scopus",
                "provider_display_name": "Scopus",
                "source_family": "licensed_research_discovery",
                "reference_state": "query_seed_draft",
                "capture_state": "seed_only",
                "queue_status": "pending",
                "next_capture_action": "CAPTURE_SEARCH_RESULT",
                "query_family": "tariff_demand_peak",
                "primary_query": "warehouse demand charge peak timing",
                "pivot_query": "warehouse tariff orchestration",
                "search_intent": "Find tariff timing evidence.",
                "launch_url": "https://www.scopus.com/",
                "search_surface": "TITLE-ABS-KEY",
                "execution_hint": "Search discovery first.",
                "evidence_targets": ["utility tariff", "billing demand"],
            },
            {
                "candidate_id": "queryseed-c",
                "provider_key": "ieee",
                "provider_display_name": "IEEE",
                "source_family": "licensed_research_fulltext",
                "reference_state": "query_seed_draft",
                "capture_state": "seed_only",
                "queue_status": "pending",
                "next_capture_action": "CAPTURE_SEARCH_RESULT",
                "query_family": "owner_operator_boundary",
                "primary_query": "warehouse owner operator utility boundary",
                "pivot_query": "tenant metering responsibility",
                "search_intent": "Find owner operator evidence.",
                "launch_url": "https://ieeexplore.ieee.org/",
                "search_surface": "IEEE metadata + abstract + index terms",
                "execution_hint": "Search full text.",
                "evidence_targets": ["lease matrix"],
            },
        ]
    )

    plan = build_search_query_execution_batch_plan(
        search_query_execution_register=register,
        batch_size=3,
    )

    assert plan["available"] is True
    assert plan["provider_key"] in {"scopus", "ieee"}
    search_guide = plan["search_execution_provider_guide"]
    search_sheet = plan["search_execution_provider_sheet_template"]
    search_workbook = plan["search_execution_capture_workbook_template"]
    assert search_guide["provider_key"] == plan["provider_key"]
    assert "# Row 1 · Candidate:" in search_sheet
    assert "# Search line 1:" in search_sheet
    assert "Candidate ID:" in search_workbook
    assert "URL:" in search_workbook
    assert "Selected:" in search_workbook
    if plan["provider_key"] == "scopus":
        assert plan["query_family"] == "tariff_demand_peak"
        assert plan["candidate_ids"][:2] == ["queryseed-a", "queryseed-b"]
        assert "Candidate ID: queryseed-a" in plan["packet_template"]
        assert "Candidate ID: queryseed-b" in plan["packet_template"]
        assert search_guide["preferred_surface"] == "TITLE-ABS-KEY"
        assert "Scopus" not in search_sheet or "Preferred surface: TITLE-ABS-KEY" in search_sheet
        assert "# Provider search workbook · scopus · tariff_demand_peak" in search_workbook
    else:
        assert plan["query_family"] == "owner_operator_boundary"
        assert plan["candidate_ids"][0] == "queryseed-c"
        assert "Candidate ID: queryseed-c" in plan["packet_template"]
        assert search_guide["preferred_surface"] == "Metadata + abstract + index terms"
        assert "Index Terms" in " ".join(search_guide["search_tips"])
        assert "# Provider search workbook · ieee · owner_operator_boundary" in search_workbook
    assert "\"selected\": false" in plan["result_import_json_template"]
    assert "Selected: " in plan["ordered_result_import_packet_template"]
    assert "# URL | Title | Snippet | Excerpt | Selected | Notes" in plan["ordered_result_import_compact_template"]
    assert "# URL<TAB>Title<TAB>Snippet<TAB>Excerpt<TAB>Selected<TAB>Notes" in plan["ordered_result_import_tsv_template"]
    guide = plan["ordered_result_import_provider_capture_guide"]
    sheet = plan["ordered_result_import_provider_capture_sheet_template"]
    assert guide["provider_key"] == plan["provider_key"]
    assert "# Row 1 · Candidate:" in sheet
    assert "# Primary query:" in sheet
    if plan["provider_key"] == "scopus":
        assert "# Title<TAB>Link<TAB>Abstract<TAB>Source<TAB>Year<TAB>Selected<TAB>Notes" in plan["ordered_result_import_provider_tsv_template"]
        assert guide["preferred_headers"][:3] == ["Title", "Link", "Abstract"]
        assert guide["snippet_header_fallbacks"] == ["Abstract"]
        assert guide["positional_layouts"][0][:3] == ["Title", "Link", "Abstract"]
        assert "Scopus clipboard can usually be pasted close to the visible results table" in sheet
    else:
        assert "# Document Title<TAB>Document Link<TAB>Abstract<TAB>Publication Year<TAB>Index Terms<TAB>Selected<TAB>Notes" in plan["ordered_result_import_provider_tsv_template"]
        assert guide["preferred_headers"][:2] == ["Document Title", "Document Link"]
        assert "Index Terms" in guide["snippet_header_fallbacks"]
        assert ["Document Title", "Document Link", "Publication Year", "Index Terms"] in guide["positional_layouts"]
        assert "IEEE clipboard can use Document Title/Link plus Abstract or Index Terms" in sheet
    assert "Rank: 1" in plan["result_import_packet_template"]
    assert "\"candidate_id\"" in plan["result_import_json_template"]
    assert "json_array" in plan["accepted_import_formats"]
    assert "ordered_compact_lines" in plan["accepted_import_formats"]
    assert "ordered_tsv_lines" in plan["accepted_import_formats"]
    assert "\"candidate_id\"" in plan["capture_result_json_template"]
    assert "json_array" in plan["accepted_capture_formats"]


def test_build_search_query_execution_batch_plan_counts_imported_results() -> None:
    plan = build_search_query_execution_batch_plan(
        search_query_execution_register=[
            {
                "candidate_id": "queryseed-a",
                "provider_key": "scopus",
                "provider_display_name": "Scopus",
                "source_family": "licensed_research_discovery",
                "queue_status": "pending",
                "execution_status": "search_ready_capture_pending",
                "query_family": "tariff_demand_peak",
                "primary_query": "warehouse demand charge peak timing",
                "launch_url": "https://www.scopus.com/",
                "imported_result_options": [
                    {"option_index": 1, "source_url": "https://example.com/a-1", "search_result_title": "A1"},
                    {"option_index": 2, "source_url": "https://example.com/a-2", "search_result_title": "A2"},
                ],
                "top_imported_result": {"source_url": "https://example.com/a-1", "search_result_title": "A1"},
            },
            {
                "candidate_id": "queryseed-b",
                "provider_key": "scopus",
                "provider_display_name": "Scopus",
                "source_family": "licensed_research_discovery",
                "queue_status": "pending",
                "execution_status": "search_ready_capture_pending",
                "query_family": "tariff_demand_peak",
                "primary_query": "warehouse demand charge peak timing",
                "launch_url": "https://www.scopus.com/",
                "imported_result_options": [],
                "top_imported_result": {},
            },
        ],
        batch_size=2,
    )

    assert plan["available"] is True
    assert plan["imported_result_count"] == 2
    assert plan["promotable_candidate_ids"] == ["queryseed-a"]
    assert "\"candidate_id\": \"queryseed-a\"" in plan["result_import_json_template"]
