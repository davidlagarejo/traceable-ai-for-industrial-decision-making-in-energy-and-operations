from pathlib import Path

from runtime_orchestrator.zlab_skill import (
    describe_provider_session_state,
    build_provider_session_plan,
    build_research_document_manifest,
    ingest_licensed_research_document,
    load_registry_bundle,
    plan_licensed_document_acquisition,
)


def test_licensed_acquisition_prefers_persistent_playwright_for_session_required_provider() -> None:
    plan = plan_licensed_document_acquisition(
        url="https://www.sciencedirect.com/science/article/pii/S0360544218311234",
        retrieval_purpose="pattern_seed_discovery",
        technical_scraping_allowed=True,
        route_allowed=True,
        env={"ZLAB_ENABLE_LICENSED_RESEARCH_ACQUISITION": "1"},
    )

    assert plan["allowed"] is True
    assert plan["selected_mode"] == "playwright_persistent_session"
    assert plan["selection_reason"] == "licensed_provider_session_required"
    assert plan["provider_session_plan"]["provider_key"] == "elsevier"
    assert plan["provider_session_state"]["auth_state"] in {
        "profile_missing",
        "profile_initialized_session_unknown",
        "profile_present_session_unknown",
    }


def test_licensed_acquisition_can_route_through_institutional_gateway() -> None:
    plan = plan_licensed_document_acquisition(
        url="https://ieeexplore.ieee.org/document/1234567",
        retrieval_purpose="pattern_seed_discovery",
        technical_scraping_allowed=True,
        route_allowed=True,
        env={
            "ZLAB_ENABLE_LICENSED_RESEARCH_ACQUISITION": "1",
            "ZLAB_LICENSED_INSTITUTION_ENTRY_URL": "https://library.example.edu/login",
            "ZLAB_LICENSED_INSTITUTION_NAME": "Example University",
        },
    )

    assert plan["allowed"] is True
    assert plan["selected_mode"] == "playwright_persistent_session"
    assert plan["provider_session_plan"]["access_route"] == "institutional_gateway"
    assert plan["provider_session_plan"]["profile_scope"] == "institution_shared"
    assert plan["provider_session_plan"]["launch_url"] == "https://library.example.edu/login"
    assert plan["provider_session_plan"]["validation_url"] == "https://ieeexplore.ieee.org/document/1234567"


def test_licensed_acquisition_blocks_session_required_provider_when_capability_disabled() -> None:
    plan = plan_licensed_document_acquisition(
        url="https://ieeexplore.ieee.org/document/1234567",
        retrieval_purpose="pattern_seed_discovery",
        technical_scraping_allowed=True,
        route_allowed=True,
        env={},
    )

    assert plan["allowed"] is False
    assert plan["selected_mode"] == "blocked"
    assert plan["selection_reason"] == "licensed_research_capability_disabled"


def test_research_document_manifest_preserves_hashes_and_git_boundary(tmp_path: Path) -> None:
    artifact = tmp_path / "paper.html"
    artifact.write_text("<html><body>Demand response logistics paper</body></html>", encoding="utf-8")

    manifest = build_research_document_manifest(
        provider_session_plan=build_provider_session_plan(
            url="https://www.scopus.com/record/display.uri?eid=2-s2.0-123456",
            retrieval_purpose="combination_seed_review",
        ),
        acquisition_result={
            "status": "success",
            "acquisition_mode": "playwright_persistent_session",
            "requested_url": "https://www.scopus.com/record/display.uri?eid=2-s2.0-123456",
            "final_url": "https://www.scopus.com/record/display.uri?eid=2-s2.0-123456",
            "html": "<html><body>Structured prior article</body></html>",
            "visible_text": "Structured prior article",
            "selector_lineage": [{"selector": "body", "match_count": 1, "visible_text_length": 24}],
        },
        metadata={
            "title": "Structured Prior Article",
            "doi": "10.1016/j.enbuild.2026.123456",
            "journal": "Energy and Buildings",
            "published_year": "2026",
            "authors": ["A. Researcher", "B. Analyst"],
        },
        local_artifact_path=str(artifact),
    )

    assert manifest["provider_key"] == "scopus"
    assert manifest["structured_extraction_allowed"] is True
    assert manifest["keep_fulltext_outside_git"] is True
    assert manifest["local_artifact_sha256"]
    assert manifest["provenance_manifest"]["visible_text_sha256"]


def test_execute_licensed_acquisition_returns_extraction_seed(tmp_path: Path) -> None:
    from runtime_orchestrator.zlab_skill import execute_licensed_document_acquisition

    result = execute_licensed_document_acquisition(
        url="https://www.sciencedirect.com/science/article/pii/S0360544218311234",
        retrieval_purpose="pattern_seed_discovery",
        technical_scraping_allowed=False,
        route_allowed=True,
        metadata={
            "title": "Licensed Article Shell",
            "doi": "10.1016/j.enbuild.2026.999999",
        },
        local_artifact_path=str(tmp_path / "licensed.html"),
        env={},
    )

    assert "extraction_seed" in result
    assert result["extraction_seed"]["source_basis_id"] == "licensed_research_public_technical_priors"
    assert result["extraction_seed"]["structured_prior_only"] is True


def test_provider_session_state_is_bounded_when_profile_is_missing() -> None:
    plan = build_provider_session_plan(
        url="https://ieeexplore.ieee.org/document/1234567",
        retrieval_purpose="pattern_seed_discovery",
    )
    state = describe_provider_session_state(provider_plan=plan)

    assert state["session_required"] is True
    assert state["auth_state"] in {
        "profile_missing",
        "profile_initialized_session_unknown",
        "profile_present_session_unknown",
    }


def test_ingest_licensed_research_document_returns_review_and_promotion_surfaces(tmp_path: Path) -> None:
    bundle = load_registry_bundle()
    result = ingest_licensed_research_document(
        url="https://www.sciencedirect.com/science/article/pii/S0360544218311234",
        retrieval_purpose="pattern_seed_discovery",
        technical_scraping_allowed=False,
        route_allowed=True,
        metadata={
            "title": "Licensed Promotion Shell",
            "doi": "10.1016/j.apenergy.2026.111111",
        },
        local_artifact_path=str(tmp_path / "licensed.html"),
        extraction_payload={
            "id": "extract::licensed::promotion-shell",
            "review_status": "approved",
            "knowledge_atoms": [
                {
                    "id": "atom::licensed_boundary",
                    "knowledge_type": "FINANCIAL_TRANSLATION",
                    "statement": "Control boundary ambiguity can leak owner-capturable value.",
                    "asset_types": ["leased_asset"],
                    "applicable_industries": ["real_estate"],
                    "applicable_contexts": ["split_incentive"],
                    "anti_triggers": ["single owner operator"],
                    "falsification_conditions": ["fully aligned control and capture"],
                    "minimum_evidence": ["lease responsibility matrix", "meter map"],
                    "financial_mechanism": "Savings and capex capture may leak across actors.",
                    "supporting_excerpt": "Boundary matters.",
                    "source_locator": "p.7",
                    "confidence_ceiling": "L2",
                }
            ],
            "pattern_candidate_records": [
                {
                    "id": "pattern_candidate::licensed_boundary_candidate",
                    "derived_from_atom_ids": ["atom::licensed_boundary"],
                    "name": "Licensed Boundary Candidate",
                    "knowledge_types": ["FINANCIAL_TRANSLATION"],
                    "asset_types": ["leased_asset"],
                    "applicable_contexts": ["split_incentive"],
                    "hypothesis": "Value capture may leak across the control boundary.",
                    "minimum_evidence": ["lease responsibility matrix", "meter map"],
                    "anti_triggers": ["single owner operator"],
                    "falsification_conditions": ["fully aligned control and capture"],
                    "financial_mechanism": "Savings and capex capture may leak across actors.",
                    "source_locator": "p.7",
                    "confidence_ceiling": "L2",
                }
            ],
            "combination_candidate_records": [],
        },
        registry_bundle=bundle,
        env={},
    )

    assert result["acquisition_result"]["status"] == "blocked"
    assert result["knowledge_extraction_record"]["review_status"] == "approved"
    assert result["extraction_review_register"][0]["review_status"] == "approved"
    assert result["approved_pattern_promotion_register"][0]["promotion_state"] == "ready_for_registry_review"
