from __future__ import annotations

from io import BytesIO

from openpyxl import Workbook

from target_seeds import build_bounded_asset_seed
from runtime_orchestrator.adapters import motor_012 as motor_012_module
from runtime_orchestrator.adapters import motor_028 as motor_028_module
from runtime_orchestrator.adapters.motor_028 import Motor028Adapter


def _nyc_ctx() -> dict:
    return {
        "address": "ONE VANDERBILT AVENUE, NEW YORK, NY, 10017",
        "asset_name": "One Vanderbilt",
        "target_label": "One Vanderbilt",
        "city": "NEW YORK",
        "state_code": "NY",
        "zip_code": "10017",
        "bbl": "",
        "bin": "",
        "boro": "",
        "block": "",
        "lot": "",
    }


def _ll97_cbl_workbook_bytes(rows: list[dict]) -> bytes:
    workbook = Workbook()
    ws = workbook.active
    ws.title = "Sustainability_CBL"
    ws.append(
        [
            "BBL",
            "BIN",
            "On LL97 CBL (Y/N)",
            " LL97 Compliance Pathway",
            "On LL84 CBL (Y/N)",
            "Required to Report Water Data from DEP (Y/N)",
            "On LL88 CBL (Y/N)",
            "On LL87 (Y/N)",
            "DOF BBL Address ",
            "DOF BBL Zip Code",
            "DOF BBL Building Count",
            "DOF BBL Gross Square Footage (GSF)",
        ]
    )
    for row in rows:
        ws.append(
            [
                row.get("BBL"),
                row.get("BIN"),
                row.get("On LL97 CBL (Y/N)"),
                row.get(" LL97 Compliance Pathway"),
                row.get("On LL84 CBL (Y/N)"),
                row.get("Required to Report Water Data from DEP (Y/N)"),
                row.get("On LL88 CBL (Y/N)"),
                row.get("On LL87 (Y/N)"),
                row.get("DOF BBL Address "),
                row.get("DOF BBL Zip Code"),
                row.get("DOF BBL Building Count"),
                row.get("DOF BBL Gross Square Footage (GSF)"),
            ]
        )
    buf = BytesIO()
    workbook.save(buf)
    return buf.getvalue()


def test_assess_source_applicability_allows_nyc_fallback_without_bbl_or_bin():
    spec = {
        "source_type": "nyc_pluto_property",
        "locator_tpl": "nyc_open_data:pluto:bbl={bbl}",
    }
    status, detail = motor_028_module._assess_source_applicability(spec, _nyc_ctx())
    assert status == "applicable"
    assert "Fallback NYC dataset search" in (detail or "")


def test_fetch_nyc_ll84_falls_back_to_address_search(monkeypatch):
    calls: list[dict] = []

    def fake_fetch_json(url, params=None, headers=None, timeout=30):
        calls.append({"url": url, "params": params})
        if params and params.get("$q") == "One Vanderbilt":
            return [
                {
                    "bbl": "1012980029",
                    "property_name": "One Vanderbilt",
                    "street_address": "ONE VANDERBILT AVENUE",
                    "reporting_year": "2024",
                    "site_eui": "71.2",
                }
            ]
        return []

    monkeypatch.setattr(motor_028_module, "_fetch_json", fake_fetch_json)
    payload = motor_028_module._fetch_nyc_ll84(_nyc_ctx())
    assert payload is not None
    assert payload["records"][0]["bbl"] == "1012980029"
    assert payload["query_context"]["query_mode"] == "fallback_search"
    assert any(call["params"] and "$q" in call["params"] for call in calls)


def test_fetch_nyc_ll84_tries_current_annual_dataset_ids_first(monkeypatch):
    seen_urls: list[str] = []

    def fake_fetch_json(url, params=None, headers=None, timeout=30):
        seen_urls.append(url)
        return []

    monkeypatch.setattr(motor_028_module, "_fetch_json", fake_fetch_json)
    assert motor_028_module._fetch_nyc_ll84(_nyc_ctx()) is None
    assert seen_urls
    assert "5zyy-y8am" in seen_urls[0]
    assert any("7x5e-2fxh" in url for url in seen_urls)


def test_fetch_nyc_ll84_uses_real_bbl_field_and_report_year_order(monkeypatch):
    calls: list[dict] = []

    def fake_fetch_json(url, params=None, headers=None, timeout=30):
        calls.append({"url": url, "params": params})
        if "5zyy-y8am" in url and params and params.get("nyc_borough_block_and_lot") == "1012770027":
            return [
                {
                    "report_year": "2024",
                    "nyc_borough_block_and_lot": "1012770027",
                    "property_name": "One Vanderbilt Avenue",
                    "site_eui_kbtu_ft": "117.7",
                }
            ]
        return []

    monkeypatch.setattr(motor_028_module, "_fetch_json", fake_fetch_json)
    payload = motor_028_module._fetch_nyc_ll84(
        {
            **_nyc_ctx(),
            "bbl": "1012770027",
        }
    )
    assert payload is not None
    assert payload["records"][0]["report_year"] == "2024"
    assert any(
        call["params"]
        and call["params"].get("nyc_borough_block_and_lot") == "1012770027"
        and call["params"].get("$order") == "report_year DESC"
        for call in calls
    )


def test_fetch_nyc_ll84_continues_after_invalid_exact_field_until_valid_bbl_field(monkeypatch):
    calls: list[dict] = []

    def fake_fetch_json(url, params=None, headers=None, timeout=30):
        calls.append(params or {})
        if params and "bbl" in params:
            raise motor_028_module.requests.RequestException("invalid field")
        if params and params.get("nyc_borough_block_and_lot") == "1012770027":
            return [
                {
                    "report_year": "2024",
                    "nyc_borough_block_and_lot": "1012770027",
                    "site_eui_kbtu_ft": "117.7",
                }
            ]
        return []

    monkeypatch.setattr(motor_028_module, "_fetch_json", fake_fetch_json)
    payload = motor_028_module._fetch_nyc_ll84({**_nyc_ctx(), "bbl": "1012770027"})
    assert payload is not None
    assert payload["records"][0]["report_year"] == "2024"
    assert any("bbl" in params for params in calls)
    assert any(params.get("nyc_borough_block_and_lot") == "1012770027" for params in calls)


def test_fetch_nyc_ll97_cbl_matches_by_bbl_and_bin(monkeypatch):
    monkeypatch.setattr(
        motor_028_module,
        "_fetch_nyc_cbl_workbook_bytes",
        lambda url=motor_028_module._NYC_CBL_2026_XLSX_URL: _ll97_cbl_workbook_bytes(
            [
                {
                    "BBL": "1012770027",
                    "BIN": "1090825",
                    "On LL97 CBL (Y/N)": "Y",
                    " LL97 Compliance Pathway": 0,
                    "On LL84 CBL (Y/N)": "Y",
                    "Required to Report Water Data from DEP (Y/N)": "Y",
                    "On LL88 CBL (Y/N)": "Y",
                    "On LL87 (Y/N)": "Y",
                    "DOF BBL Address ": "51 E. 42ND ST.",
                    "DOF BBL Zip Code": "10017-5403",
                    "DOF BBL Building Count": 1,
                    "DOF BBL Gross Square Footage (GSF)": 1678135,
                }
            ]
        ),
    )
    payload = motor_028_module._fetch_nyc_ll97_cbl({**_nyc_ctx(), "bbl": "1012770027", "bin": "1090825"})
    assert payload is not None
    assert payload["selected_row"]["ll97_cbl_covered"] == "Y"
    assert payload["selected_row"]["ll97_compliance_pathway"] == "0"
    assert payload["selected_row"]["ll97_compliance_pathway_label"].startswith("CP0")
    assert payload["query_context"]["match_basis"] == "bin_exact"


def test_fetch_nyc_ll97_filing_guidance_returns_official_guides_without_public_registry():
    payload = motor_028_module._fetch_nyc_ll97_filing_guidance(_nyc_ctx())
    assert payload is not None
    assert payload["public_filing_registry_available"] is False
    assert payload["source_authority"] == "high"
    assert any("article320_simple.pdf" in url for url in payload["official_urls"])
    assert any("article321_pathway.pdf" in url for url in payload["official_urls"])


def test_fetch_nyc_ll97_public_filing_candidate_accepts_asset_specific_pdf_candidate(monkeypatch):
    monkeypatch.setattr(
        motor_028_module,
        "_web_search",
        lambda query, n=8: [
            {
                "title": "One Vanderbilt Article 321 Submission Package",
                "url": "https://sustainability.slgreen.com/wp-content/uploads/2026/04/one-vanderbilt-article-321.pdf",
                "snippet": "One Vanderbilt Local Law 97 Article 321 submission package for the covered building filing year.",
            }
        ],
    )
    payload = motor_028_module._fetch_nyc_ll97_public_filing_candidate(
        {
            **_nyc_ctx(),
            "owner_name": "SL Green Realty Corp",
            "ticker": "SLG",
        }
    )
    assert payload is not None
    assert payload["best_candidate"]["artifact_class"] == "article_321_submission_candidate"
    assert payload["best_candidate"]["authority_basis"] == "owner"
    assert payload["best_candidate"]["is_pdf"] is True


def test_fetch_nyc_ll97_cbl_marks_bin_ambiguity_when_bbl_has_multiple_bins(monkeypatch):
    monkeypatch.setattr(
        motor_028_module,
        "_fetch_nyc_cbl_workbook_bytes",
        lambda url=motor_028_module._NYC_CBL_2026_XLSX_URL: _ll97_cbl_workbook_bytes(
            [
                {
                    "BBL": "1012770027",
                    "BIN": "1035350",
                    "On LL97 CBL (Y/N)": "Y",
                    " LL97 Compliance Pathway": 0,
                    "On LL84 CBL (Y/N)": "Y",
                    "Required to Report Water Data from DEP (Y/N)": "Y",
                    "On LL88 CBL (Y/N)": "Y",
                    "On LL87 (Y/N)": "Y",
                    "DOF BBL Address ": "51 E. 42ND ST.",
                    "DOF BBL Zip Code": "10017-5403",
                    "DOF BBL Building Count": 1,
                    "DOF BBL Gross Square Footage (GSF)": 1678135,
                },
                {
                    "BBL": "1012770027",
                    "BIN": "1090825",
                    "On LL97 CBL (Y/N)": "Y",
                    " LL97 Compliance Pathway": 0,
                    "On LL84 CBL (Y/N)": "Y",
                    "Required to Report Water Data from DEP (Y/N)": "Y",
                    "On LL88 CBL (Y/N)": "Y",
                    "On LL87 (Y/N)": "Y",
                    "DOF BBL Address ": "51 E. 42ND ST.",
                    "DOF BBL Zip Code": "10017-5403",
                    "DOF BBL Building Count": 1,
                    "DOF BBL Gross Square Footage (GSF)": 1678135,
                },
            ]
        ),
    )
    payload = motor_028_module._fetch_nyc_ll97_cbl({**_nyc_ctx(), "bbl": "1012770027", "bin": ""})
    assert payload is not None
    assert payload["query_context"]["match_basis"] == "bbl_exact"
    assert payload["query_context"]["bin_ambiguous"] is True


def test_merge_nyc_locator_context_promotes_bbl_bin_and_block_lot():
    ctx = dict(_nyc_ctx())
    ctx["asset_context_readiness"] = motor_028_module._asset_context_readiness(ctx)
    updated, changed = motor_028_module._merge_nyc_locator_context(
        ctx,
        "nyc_pluto_property",
        {"bbl": "1012980029", "bin": "1088715", "borough": "MANHATTAN"},
    )
    assert {"bbl", "bin", "boro", "block", "lot"}.issubset(set(changed))
    assert updated["bbl"] == "1012980029"
    assert updated["bin"] == "1088715"
    assert updated["boro"] == "1"
    assert updated["block"] == "01298"
    assert updated["lot"] == "0029"
    assert updated["asset_context_readiness"]["parcel_id_present"] is True
    spec = {
        "source_type": "nyc_acris_mortgage_records",
        "locator_tpl": "nyc_open_data:acris:boro={boro}&block={block}&lot={lot}",
    }
    status, _detail = motor_028_module._assess_source_applicability(spec, updated)
    assert status == "applicable"
    updated_with_alias, _ = motor_028_module._merge_nyc_locator_context(
        updated,
        "nyc_pluto_property",
        {"address": "51 EAST 42 STREET", "ownername": "ONE VANDERBILT OWNER LLC"},
    )
    assert "51 EAST 42 STREET" in updated_with_alias["address_aliases"]
    queries = motor_028_module._nyc_candidate_queries(updated_with_alias)
    assert any("51 EAST 42 STREET" == query for query in queries)


def test_merge_nyc_locator_context_reads_current_ll84_field_names():
    updated, changed = motor_028_module._merge_nyc_locator_context(
        _nyc_ctx(),
        "nyc_ll84_energy_benchmarking",
        {
            "records": [
                {
                    "nyc_borough_block_and_lot": "1012770027",
                    "nyc_building_identification": "1090825",
                    "address_1": "51 East 42nd Street",
                    "property_name": "One Vanderbilt Avenue",
                }
            ]
        },
    )
    assert {"bbl", "bin", "boro", "block", "lot"}.issubset(set(changed))
    assert updated["bbl"] == "1012770027"
    assert updated["bin"] == "1090825"
    assert any(alias.upper() == "51 EAST 42ND STREET" for alias in updated["address_aliases"])


def test_merge_nyc_locator_context_reads_ll97_cbl_selected_row():
    updated, changed = motor_028_module._merge_nyc_locator_context(
        _nyc_ctx(),
        "nyc_ll97_covered_buildings_list",
        {
            "selected_row": {
                "bbl": "1012770027",
                "bin": "1090825",
                "address": "51 E. 42ND ST.",
            }
        },
    )
    assert {"bbl", "bin", "boro", "block", "lot"}.issubset(set(changed))
    assert updated["bbl"] == "1012770027"
    assert updated["bin"] == "1090825"
    assert any(alias.upper() == "51 E. 42ND ST." for alias in updated["address_aliases"])


def test_merge_nyc_locator_context_avoids_promoting_ambiguous_ll97_bin():
    updated, changed = motor_028_module._merge_nyc_locator_context(
        _nyc_ctx(),
        "nyc_ll97_covered_buildings_list",
        {
            "query_context": {"bin_ambiguous": True},
            "selected_row": {
                "bbl": "1012770027",
                "bin": "1035350",
                "address": "51 E. 42ND ST.",
            },
        },
    )
    assert {"bbl", "boro", "block", "lot"}.issubset(set(changed))
    assert "bin" not in changed
    assert updated["bbl"] == "1012770027"
    assert updated["bin"] == ""


def test_normalized_attempt_locator_omits_ambiguous_ll97_bin():
    locator = motor_028_module._normalized_attempt_locator(
        "nyc_ll97_covered_buildings_list",
        "nyc_dob:cbl26:bbl={bbl}&bin={bin}",
        {"bbl": "1012770027", "bin": "1035350"},
        {
            "query_context": {"bbl": "1012770027", "bin": "", "bin_ambiguous": True},
            "selected_row": {"bbl": "1012770027", "bin": "1035350"},
        },
    )
    assert locator == "nyc_dob:cbl26:bbl=1012770027"


def test_nyc_ll97_cbl_record_prefers_ll84_bin_when_multiple_rows_exist():
    row = motor_012_module._nyc_ll97_cbl_record(
        {
            "ll97_covered_buildings_list": {
                "selected_row": {"bbl": "1012770027", "bin": "1035350"},
                "matched_rows": [
                    {"bbl": "1012770027", "bin": "1035350"},
                    {"bbl": "1012770027", "bin": "1090825"},
                ],
            }
        },
        preferred_bin="1090825",
    )
    assert row["bin"] == "1090825"


def test_nyc_asset_jurisdiction_sources_canonicalize_to_asset_level():
    rows = motor_028_module._build_source_register(
        [
            {
                "source_type": "nyc_pluto_property",
                "source_scope": "asset_jurisdiction_specific",
                "source_family": "building_record",
                "authority_score": "high",
                "round_id": "round_3_energy_utility_compliance",
                "locator": "nyc_open_data:pluto:bbl=",
                "status": "found",
                "accepted": True,
                "rejection_reason": "",
            }
        ],
        [],
    )
    assert rows[0]["scope"] == "ASSET_LEVEL"
    assert motor_012_module._canonical_scope("asset_jurisdiction_specific") == "ASSET_LEVEL"


def test_normalize_nyc_bbl_handles_decimal_pluto_values_and_borough_abbreviations():
    assert motor_028_module._normalize_nyc_bbl("1012770027.00000000") == "1012770027"
    assert motor_028_module._normalize_nyc_borough_code("MN") == "1"


def test_select_extended_registry_prioritizes_pluto_before_ll84_for_nyc_buildings():
    ctx = dict(_nyc_ctx())
    ctx["asset_context_readiness"] = {"state": "asset_localized"}
    selected = motor_028_module._select_extended_registry(
        ctx,
        {"target_scope": "asset"},
        {"target_type": "commercial_building"},
    )
    ordered = [spec["source_type"] for spec in selected]
    assert ordered.index("nyc_dof_property_record") < ordered.index("nyc_pluto_property")
    assert ordered.index("nyc_pluto_property") < ordered.index("nyc_ll84_energy_benchmarking")
    assert ordered.index("nyc_ll97_covered_buildings_list") < ordered.index("nyc_ll84_energy_benchmarking")
    assert ordered.index("nyc_ll84_energy_benchmarking") < ordered.index("nyc_dob_permits")


def test_select_extended_registry_filters_and_orders_by_source_routing_plan():
    ctx = dict(_nyc_ctx())
    ctx["asset_context_readiness"] = {"state": "asset_localized"}
    routing_plan = {
        "mandatory_sources": [
            {"source_key": "nyc_dof_property_record"},
            {"source_key": "nyc_ll97_covered_buildings_list"},
            {"source_key": "nyc_pluto_property"},
            {"source_key": "nyc_ll84_energy_benchmarking"},
        ],
        "high_priority_sources": [
            {"source_key": "nyc_dob_permits"},
        ],
        "optional_sources": [
            {"source_key": "nyc_energy_star_annual_score"},
        ],
    }
    selected = motor_028_module._select_extended_registry(
        ctx,
        {"target_scope": "asset"},
        {"target_type": "commercial_building"},
        routing_plan,
    )
    ordered = [spec["source_type"] for spec in selected]
    assert ordered == [
        "nyc_dof_property_record",
        "nyc_ll97_covered_buildings_list",
        "nyc_pluto_property",
        "nyc_ll84_energy_benchmarking",
        "nyc_dob_permits",
        "nyc_energy_star_annual_score",
    ]


def test_fetch_nyc_dof_property_record_uses_acris_legals(monkeypatch):
    monkeypatch.setattr(
        motor_028_module,
        "_fetch_nyc_socrata_rows",
        lambda dataset_id, ctx, exact_param_sets=None, order=None, fallback_limit=10, output_limit=5: (
            [
                {
                    "borough": "1",
                    "block": "1277",
                    "lot": "27",
                    "street_number": "51",
                    "street_name": "EAST 42ND STREET",
                    "property_type": "OF",
                }
            ],
            {"query_mode": "exact", "query_params": {"borough": "1", "block": "1277", "lot": "27"}},
        ),
    )
    ctx = dict(_nyc_ctx())
    ctx.update({"bbl": "1012770027", "boro": "1", "block": "1277", "lot": "27"})
    row = motor_028_module._fetch_nyc_dof_property_record(ctx)
    assert row is not None
    assert row["bbl"] == "1012770027"
    assert row["address"] == "51 EAST 42ND STREET"
    assert row["source_dataset"] == "nyc_dof_acris_legals"


def test_motor_028_recirculates_nyc_context_so_later_sources_become_applicable(monkeypatch):
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

    monkeypatch.setattr(
        motor_028_module,
        "_select_extended_registry",
        lambda ctx, target_definition, benchmark_route, routing_plan=None: [
            {
                "key": "nyc_pluto_property",
                "fn": motor_028_module._fetch_nyc_pluto,
                "source_type": "nyc_pluto_property",
                "locator_tpl": "nyc_open_data:pluto:bbl={bbl}",
                "discovery_reason": "PLUTO",
                "gap_severity": "low",
                "gap_terms": ["GFA"],
            },
            {
                "key": "nyc_acris_mortgage_records",
                "fn": motor_028_module._fetch_nyc_acris_mortgages,
                "source_type": "nyc_acris_mortgage_records",
                "locator_tpl": "nyc_open_data:acris:boro={boro}&block={block}&lot={lot}",
                "discovery_reason": "ACRIS",
                "gap_severity": "medium",
                "gap_terms": ["mortgage"],
            },
        ],
    )
    monkeypatch.setattr(
        motor_028_module,
        "_benchmark_route_for_context",
        lambda ctx, target_definition: {
            "route_class": "national_building_benchmark",
            "source_type": "eia_cbecs_2018_benchmarks",
            "fetcher": lambda ctx: {"benchmark": "ok"},
            "discovery_reason": "Benchmark",
            "target_type": "commercial_building",
            "phase_eligibility": ["phase_1"],
            "scope_boundary": "asset_level",
        },
    )
    monkeypatch.setattr(
        motor_028_module,
        "_fetch_census_geocoder",
        lambda ctx: {
            "coordinates": {"x": -73.9772, "y": 40.7527},
            "geographies": {"Counties": [{"GEOID": "36061", "STATE": "36"}]},
            "addressComponents": {"city": "NEW YORK", "zip": "10017"},
            "matchedAddress": "ONE VANDERBILT AVENUE, NEW YORK, NY, 10017",
        },
    )
    monkeypatch.setattr(motor_028_module, "_fetch_ashrae_climate_zone", lambda ctx: {"climate_zone": "4A"})

    class _FakeCrawler:
        def get_cached_or_live(self, key, fn, ctx):
            if key == "nyc_pluto_property":
                return {"bbl": "1012980029", "bin": "1088715", "borough": "MANHATTAN"}
            if key == "nyc_acris_mortgage_records":
                assert ctx.get("boro") == "1"
                assert ctx.get("block") == "01298"
                assert ctx.get("lot") == "0029"
                return [{"borough": "1", "block": "01298", "lot": "0029", "document_id": "123"}]
            raise AssertionError(f"Unexpected key {key}")

    monkeypatch.setattr(motor_028_module, "_get_crawler", lambda ctx: _FakeCrawler())

    out = Motor028Adapter().run(
        {
            "__pipeline__": pipeline,
            "motor_001": {
                "ingestion_contract_status": "active_ingestion",
                "prohibited_scrape_rounds": [],
                "target_type_classification_seed": {"target_type_classification": "OPERATING_ASSET"},
            },
            "motor_003": {"term_index": {}},
            "motor_008": {"source_registry": {}},
            "motor_009": {},
        }
    )
    statuses = {row["source_type"]: row["status"] for row in out["discovery_attempts"]}
    assert statuses["nyc_pluto_property"] == "found"
    assert statuses["nyc_acris_mortgage_records"] == "found"


def test_motor_028_suppresses_sec_context_when_routing_plan_excludes_it(monkeypatch):
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

    monkeypatch.setattr(
        motor_028_module,
        "_fetch_census_geocoder",
        lambda ctx: {
            "coordinates": {"x": -73.9772, "y": 40.7527},
            "geographies": {"Counties": [{"GEOID": "36061", "STATE": "36"}]},
            "addressComponents": {"city": "NEW YORK", "zip": "10017"},
            "matchedAddress": "ONE VANDERBILT AVENUE, NEW YORK, NY, 10017",
        },
    )
    monkeypatch.setattr(motor_028_module, "_fetch_ashrae_climate_zone", lambda ctx: {"climate_zone": "4A"})
    monkeypatch.setattr(
        motor_028_module,
        "_benchmark_route_for_context",
        lambda ctx, target_definition: {
            "route_class": "local_building_benchmark",
            "source_type": "nyc_ll84_energy_benchmarking",
            "fetcher": lambda ctx: {"records": [{"report_year": "2024", "site_eui_kbtu_ft": "117.7"}]},
            "discovery_reason": "Benchmark",
            "target_type": "commercial_building",
            "phase_eligibility": ["phase_1"],
            "scope_boundary": "asset_level",
        },
    )
    monkeypatch.setattr(motor_028_module, "_select_extended_registry", lambda *args, **kwargs: [])

    out = Motor028Adapter().run(
        {
            "__pipeline__": pipeline,
            "motor_001": {
                "ingestion_contract_status": "ready_for_identity_gate",
                "prohibited_scrape_rounds": [],
                "target_type_classification_seed": {"target_type_classification": "OPERATING_ASSET"},
            },
            "motor_003": {"term_index": {}},
            "motor_008": {"source_registry": {}},
            "motor_009": {},
            "motor_035": {
                "routing_ready": True,
                "report_type_allowed": "Minimum Evidence Report",
                "source_routing_plan": {
                    "mandatory_sources": [
                        {"source_key": "nyc_pluto_property"},
                        {"source_key": "nyc_ll84_energy_benchmarking"},
                        {"source_key": "nyc_ll97_covered_buildings_list"},
                        {"source_key": "nyc_dob_permits"},
                    ],
                    "high_priority_sources": [{"source_key": "nyc_ll97_filing_guidance"}],
                    "optional_sources": [{"source_key": "nyc_energy_star_annual_score"}],
                },
            },
        }
    )
    statuses = {row["source_type"]: row["status"] for row in out["discovery_attempts"]}
    assert statuses["sec_edgar_submissions"] == "not_applicable"
    assert statuses["sec_edgar_xbrl_facts"] == "not_applicable"
    assert statuses["nyc_ll84_energy_benchmarking"] == "found"
    assert "nyc_pluto_property" in out["routing_plan_compliance"]["mandatory_sources_missing_from_executor"]


def test_consolidate_preserves_routed_ll84_payload_under_named_shortcut():
    out = motor_028_module._consolidate(
        None,
        None,
        None,
        None,
        {
            "records": [
                {
                    "report_year": "2024",
                    "nyc_borough_block_and_lot": "1012770027",
                    "site_eui_kbtu_ft": "117.7",
                }
            ]
        },
        {"selected_source_type": "nyc_ll84_energy_benchmarking"},
        {"owner_name": "SL Green Realty Corp", "owner_ticker": "SLG"},
        {},
    )
    assert out["asset_energy_behavior_reference"]["records"][0]["report_year"] == "2024"
    assert out["ll84_energy_benchmarking"]["records"][0]["site_eui_kbtu_ft"] == "117.7"
