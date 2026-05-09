from __future__ import annotations

import json
from pathlib import Path

from runtime_orchestrator.zlab_skill import (
    build_local_artifact_extraction_template,
    build_local_artifact_metadata_template,
    build_local_licensed_artifact_package,
    build_local_pdf_auto_draft_extraction_payload,
    build_provider_session_plan,
    build_research_document_manifest,
    ingest_local_licensed_artifact_batch,
    load_registry_bundle,
    scaffold_local_licensed_artifact_templates,
)


def test_build_local_licensed_artifact_package_preserves_pdf_hash_and_metadata(tmp_path: Path) -> None:
    artifact = tmp_path / "warehouse-paper.pdf"
    artifact.write_bytes(b"%PDF-1.4\n% local licensed artifact\n")

    package = build_local_licensed_artifact_package(
        local_artifact_path=str(artifact),
        metadata={
            "provider_key": "scopus",
            "title": "Warehouse Tariff Paper",
            "doi": "10.1016/j.enbuild.2026.123456",
            "journal": "Energy and Buildings",
            "published_year": "2026",
            "authors": ["A. Researcher"],
            "source_url": "https://scopus.proxyutp.elogim.com/record/display.uri?eid=2-s2.0-123456",
        },
        retrieval_purpose="pattern_seed_discovery",
    )

    manifest = package["research_document_manifest"]
    assert manifest["provider_key"] == "scopus"
    assert manifest["title"] == "Warehouse Tariff Paper"
    assert manifest["local_artifact_sha256"]
    assert manifest["provenance_manifest"]["attempt_outcome"] == "local_artifact_available"
    assert package["extraction_seed"]["document_title"] == "Warehouse Tariff Paper"
    assert package["extraction_seed"]["structured_prior_only"] is True


def test_scaffold_local_licensed_artifact_templates_creates_missing_sidecars(tmp_path: Path) -> None:
    artifact = tmp_path / "dock-paper.pdf"
    artifact.write_bytes(b"%PDF-1.4\n% local licensed artifact\n")

    result = scaffold_local_licensed_artifact_templates(
        input_dir=str(tmp_path),
        provider_key="scopus",
        retrieval_purpose="pattern_seed_discovery",
    )

    assert result["summary"]["artifact_count"] == 1
    assert result["summary"]["metadata_created_count"] == 1
    assert result["summary"]["extraction_created_count"] == 1
    metadata_payload = json.loads(artifact.with_suffix(".metadata.json").read_text(encoding="utf-8"))
    extraction_payload = json.loads(artifact.with_suffix(".extraction.json").read_text(encoding="utf-8"))
    assert metadata_payload["provider_key"] == "scopus"
    assert extraction_payload["provider_key"] == "scopus"
    assert extraction_payload["review_status"] == "draft"


def test_local_artifact_templates_are_bounded_and_governed(tmp_path: Path) -> None:
    artifact = tmp_path / "mhe-paper.pdf"
    artifact.write_bytes(b"%PDF-1.4\n% local licensed artifact\n")

    metadata_payload = build_local_artifact_metadata_template(
        artifact_path=str(artifact),
        provider_key="scopus",
    )
    extraction_payload = build_local_artifact_extraction_template(
        artifact_path=str(artifact),
        provider_key="scopus",
    )

    assert metadata_payload["provider_key"] == "scopus"
    assert metadata_payload["notes"]
    assert extraction_payload["provider_key"] == "scopus"
    assert extraction_payload["evidence_ceiling"] == "L2"
    assert extraction_payload["structured_prior_only"] is True


def test_ingest_local_licensed_artifact_batch_aggregates_reviews_and_promotions(tmp_path: Path) -> None:
    artifact = tmp_path / "boundary-paper.pdf"
    artifact.write_bytes(b"%PDF-1.4\n% local licensed artifact\n")
    artifact.with_suffix(".metadata.json").write_text(
        json.dumps(
            {
                "provider_key": "scopus",
                "title": "Boundary Paper",
                "doi": "10.1016/j.apenergy.2026.111111",
                "source_url": "https://scopus.proxyutp.elogim.com/pages/home#basic",
            }
        ),
        encoding="utf-8",
    )
    artifact.with_suffix(".extraction.json").write_text(
        json.dumps(
            {
                "id": "extract::local::boundary-paper",
                "review_status": "approved",
                "knowledge_atoms": [
                    {
                        "id": "atom::local_boundary",
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
                        "id": "pattern_candidate::local_boundary_candidate",
                        "derived_from_atom_ids": ["atom::local_boundary"],
                        "name": "Local Boundary Candidate",
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
            }
        ),
        encoding="utf-8",
    )

    result = ingest_local_licensed_artifact_batch(
        input_dir=str(tmp_path),
        output_dir=str(tmp_path / "out"),
        registry_bundle=load_registry_bundle(),
        retrieval_purpose="pattern_seed_discovery",
    )

    assert result["summary"]["artifact_count"] == 1
    assert result["summary"]["extraction_record_count"] == 1
    assert result["summary"]["approved_pattern_promotion_count"] == 1
    assert result["approved_pattern_promotion_register"][0]["promotion_state"] == "ready_for_registry_review"
    assert Path(result["batch_result_path"]).exists()
    artifact_result_path = Path(result["artifact_results"][0]["result_path"])
    assert artifact_result_path.exists()


def test_local_pdf_auto_draft_matches_registered_patterns_and_combination(tmp_path: Path) -> None:
    artifact = tmp_path / "warehouse-autodraft.pdf"
    artifact.write_bytes(b"%PDF-1.4\n% local licensed artifact\n")
    manifest = build_research_document_manifest(
        provider_session_plan=build_provider_session_plan(
            url="https://scopus.proxyutp.elogim.com/pages/home#basic",
            retrieval_purpose="pattern_seed_discovery",
            provider_key_override="scopus",
        ),
        acquisition_result={
            "status": "local_artifact_available",
            "acquisition_mode": "manual_local_licensed_artifact",
            "requested_url": "https://scopus.proxyutp.elogim.com/pages/home#basic",
            "final_url": "https://scopus.proxyutp.elogim.com/pages/home#basic",
            "html": "",
            "visible_text": "",
            "selector_lineage": [],
        },
        metadata={
            "title": "Warehouse charging and split-incentive benchmark study",
            "doi": "10.1016/j.apenergy.2026.654321",
            "journal": "Applied Energy",
            "published_year": "2026",
            "authors": ["A. Researcher"],
        },
        local_artifact_path=str(artifact),
    )

    payload = build_local_pdf_auto_draft_extraction_payload(
        artifact_path=str(artifact),
        metadata={
            "provider_key": "scopus",
            "title": "Warehouse charging and split-incentive benchmark study",
            "abstract": (
                "A warehouse logistics study on forklift battery charging, demand charge tariffs, "
                "operator and landlord lease boundaries, and EUI per square foot benchmark error."
            ),
        },
        research_document_manifest=manifest,
        registry_bundle=load_registry_bundle(),
    )

    assert payload["review_status"] == "auto_draft"
    matched_pattern_ids = {
        row["matched_registry_pattern_id"]
        for row in payload["pattern_candidate_records"]
    }
    assert "warehouse_mhe_charging_demand_peak" in matched_pattern_ids
    assert "value_boundary_leakage_owner_operator" in matched_pattern_ids
    assert "fair_comparison_invalid_area_metric" in matched_pattern_ids
    matched_combination_ids = {
        row["matched_registry_combination_id"]
        for row in payload["combination_candidate_records"]
    }
    assert "warehouse_tariff_boundary_area_combo" in matched_combination_ids


def test_ingest_local_licensed_artifact_batch_autogenerates_extraction_sidecar(tmp_path: Path) -> None:
    artifact = tmp_path / "warehouse-autodraft-batch.pdf"
    artifact.write_bytes(b"%PDF-1.4\n% local licensed artifact\n")
    metadata_path = artifact.with_suffix(".metadata.json")
    metadata_path.write_text(
        json.dumps(
            {
                "provider_key": "scopus",
                "title": "Warehouse charging and split-incentive benchmark study",
                "source_url": "https://scopus.proxyutp.elogim.com/pages/home#basic",
                "abstract": (
                    "Warehouse logistics analysis of forklift battery charging, demand charge tariffs, "
                    "lease/operator boundary leakage and EUI per square foot comparison error."
                ),
            }
        ),
        encoding="utf-8",
    )

    result = ingest_local_licensed_artifact_batch(
        input_dir=str(tmp_path),
        output_dir=str(tmp_path / "out"),
        registry_bundle=load_registry_bundle(),
        retrieval_purpose="pattern_seed_discovery",
    )

    extraction_path = artifact.with_suffix(".extraction.json")
    extraction_payload = json.loads(extraction_path.read_text(encoding="utf-8"))
    assert extraction_payload["review_status"] == "auto_draft"
    assert result["artifact_results"][0]["extraction_autogenerated"] is True
    assert result["summary"]["approved_pattern_promotion_count"] >= 3
    assert result["summary"]["approved_combination_promotion_count"] >= 1
    assert result["approved_pattern_promotion_register"][0]["promotion_state"] == "auto_draft_review_required"
    assert result["approved_combination_promotion_register"][0]["promotion_state"] == "auto_draft_review_required"
