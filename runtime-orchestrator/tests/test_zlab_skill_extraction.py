from pathlib import Path

import pytest

from runtime_orchestrator.zlab_skill import (
    build_extraction_promotion_registers,
    build_extraction_review_register,
    build_extraction_seed_from_manifest,
    build_knowledge_extraction_record,
    build_provider_session_plan,
    build_research_document_manifest,
    load_registry_bundle,
)
from runtime_orchestrator.zlab_skill.schema import RegistryValidationError


def _manifest(tmp_path: Path) -> dict:
    artifact = tmp_path / "paper.html"
    artifact.write_text("<html><body>Warehouse tariff and dock discipline paper</body></html>", encoding="utf-8")
    return build_research_document_manifest(
        provider_session_plan=build_provider_session_plan(
            url="https://www.scopus.com/record/display.uri?eid=2-s2.0-123456",
            retrieval_purpose="pattern_seed_discovery",
        ),
        acquisition_result={
            "status": "success",
            "acquisition_mode": "playwright_persistent_session",
            "requested_url": "https://www.scopus.com/record/display.uri?eid=2-s2.0-123456",
            "final_url": "https://www.scopus.com/record/display.uri?eid=2-s2.0-123456",
            "html": "<html><body>Warehouse tariff and dock discipline paper</body></html>",
            "visible_text": "Warehouse tariff and dock discipline paper",
            "selector_lineage": [{"selector": "body", "match_count": 1, "visible_text_length": 42}],
        },
        metadata={
            "title": "Warehouse Tariff and Dock Discipline Paper",
            "doi": "10.1016/j.apenergy.2026.123456",
            "journal": "Applied Energy",
            "published_year": "2026",
            "authors": ["A. Researcher"],
        },
        local_artifact_path=str(artifact),
    )


def test_extraction_seed_uses_manifest_boundary_and_defaults_to_l2(tmp_path: Path) -> None:
    manifest = _manifest(tmp_path)

    seed = build_extraction_seed_from_manifest(
        research_document_manifest=manifest,
    )

    assert seed["source_basis_id"] == "licensed_research_public_technical_priors"
    assert seed["provider_key"] == "scopus"
    assert seed["document_title"] == "Warehouse Tariff and Dock Discipline Paper"
    assert seed["document_ref"] == "10.1016/j.apenergy.2026.123456"
    assert seed["evidence_ceiling"] == "L2"
    assert seed["structured_prior_only"] is True
    assert seed["review_status"] == "draft"


def test_knowledge_extraction_record_validates_atoms_and_candidates(tmp_path: Path) -> None:
    manifest = _manifest(tmp_path)
    bundle = load_registry_bundle()

    record = build_knowledge_extraction_record(
        research_document_manifest=manifest,
        extraction_payload={
            "id": "extract::warehouse::paper-1",
            "review_status": "needs_review",
            "notes": "Initial governed extraction draft.",
            "knowledge_atoms": [
                {
                    "id": "atom::dock_infiltration",
                    "knowledge_type": "LOSS_PATTERN",
                    "statement": "High dock activity can dominate thermal losses before HVAC efficiency is bounded.",
                    "asset_types": ["warehouse_distribution"],
                    "applicable_industries": ["logistics"],
                    "applicable_contexts": ["conditioned_loading"],
                    "anti_triggers": ["unconditioned warehouse"],
                    "falsification_conditions": ["no conditioned loading zones", "low door cycles"],
                    "minimum_evidence": ["dock count", "door cycle profile", "temperature zones"],
                    "financial_mechanism": "Conditioning cost may reflect logistics-envelope interaction rather than equipment efficiency.",
                    "supporting_excerpt": "Dock-door behavior often matters more than equipment nameplate efficiency.",
                    "source_locator": "p.12",
                    "confidence_ceiling": "L2",
                }
            ],
            "pattern_candidate_records": [
                {
                    "id": "pattern_candidate::dock_infiltration",
                    "derived_from_atom_ids": ["atom::dock_infiltration"],
                    "name": "Warehouse Dock Infiltration Candidate",
                    "knowledge_types": ["LOSS_PATTERN"],
                    "asset_types": ["warehouse_distribution"],
                    "applicable_contexts": ["conditioned_loading"],
                    "hypothesis": "Dock activity and conditioned loading can create recurrent infiltration losses.",
                    "minimum_evidence": ["dock count", "door cycle profile"],
                    "anti_triggers": ["unconditioned warehouse"],
                    "falsification_conditions": ["low door cycles"],
                    "financial_mechanism": "Thermal cost may be driven by loading behavior.",
                    "source_locator": "p.12",
                    "confidence_ceiling": "L2",
                }
            ],
            "combination_candidate_records": [
                {
                    "id": "combination_candidate::dock_tariff",
                    "derived_from_pattern_candidate_ids": ["pattern_candidate::dock_infiltration"],
                    "name": "Dock Tariff Candidate",
                    "combined_hypothesis": "Thermal losses and tariff timing may interact before generic retrofit logic is valid.",
                    "minimum_evidence": ["dock count", "tariff schedule"],
                    "financial_exposure": ["tariff exposure hidden"],
                    "prohibited_claims": ["roi", "peer superiority"],
                    "source_locator": "p.12",
                    "confidence_ceiling": "L2",
                }
            ],
        },
        registry_bundle=bundle,
    )

    assert record["provider_key"] == "scopus"
    assert record["review_status"] == "needs_review"
    assert len(record["knowledge_atoms"]) == 1
    assert len(record["pattern_candidate_records"]) == 1
    assert len(record["combination_candidate_records"]) == 1


def test_knowledge_extraction_record_rejects_l3_atom(tmp_path: Path) -> None:
    manifest = _manifest(tmp_path)

    with pytest.raises(RegistryValidationError):
        build_knowledge_extraction_record(
            research_document_manifest=manifest,
            extraction_payload={
                "knowledge_atoms": [
                    {
                        "id": "atom::bad",
                        "knowledge_type": "LOSS_PATTERN",
                        "statement": "This would improperly exceed structured-prior ceiling.",
                        "asset_types": ["warehouse_distribution"],
                        "applicable_industries": ["logistics"],
                        "applicable_contexts": ["conditioned_loading"],
                        "anti_triggers": ["none"],
                        "falsification_conditions": ["none"],
                        "minimum_evidence": ["dock count"],
                        "financial_mechanism": "Cost boundary.",
                        "supporting_excerpt": "Excerpt.",
                        "source_locator": "p.5",
                        "confidence_ceiling": "L3",
                    }
                ],
                "pattern_candidate_records": [],
                "combination_candidate_records": [],
            },
        )


def test_extraction_review_register_is_traceable(tmp_path: Path) -> None:
    manifest = _manifest(tmp_path)
    record = build_knowledge_extraction_record(
        research_document_manifest=manifest,
        extraction_payload={
            "id": "extract::warehouse::paper-2",
            "review_status": "approved",
            "knowledge_atoms": [],
            "pattern_candidate_records": [],
            "combination_candidate_records": [],
        },
    )

    review = build_extraction_review_register([record])

    assert len(review) == 1
    assert review[0]["document_title"] == "Warehouse Tariff and Dock Discipline Paper"
    assert review[0]["review_status"] == "approved"
    assert review[0]["structured_prior_only"] is True


def test_approved_extraction_promotes_registry_ready_pattern_and_combination_specs(tmp_path: Path) -> None:
    manifest = _manifest(tmp_path)
    bundle = load_registry_bundle()
    record = build_knowledge_extraction_record(
        research_document_manifest=manifest,
        extraction_payload={
            "id": "extract::warehouse::promotion-paper",
            "review_status": "approved",
            "knowledge_atoms": [
                {
                    "id": "atom::dock",
                    "knowledge_type": "LOSS_PATTERN",
                    "statement": "Dock-door behavior can dominate thermal losses.",
                    "asset_types": ["warehouse_distribution"],
                    "applicable_industries": ["logistics"],
                    "applicable_contexts": ["conditioned_loading"],
                    "anti_triggers": ["unconditioned warehouse"],
                    "falsification_conditions": ["low door cycles"],
                    "minimum_evidence": ["dock count", "door cycle profile"],
                    "financial_mechanism": "Thermal cost can be driven by logistics-envelope interaction.",
                    "supporting_excerpt": "Dock-door behavior matters.",
                    "source_locator": "p.10",
                    "confidence_ceiling": "L2",
                }
            ],
            "pattern_candidate_records": [
                {
                    "id": "pattern_candidate::warehouse_dock_behavior_candidate",
                    "derived_from_atom_ids": ["atom::dock"],
                    "name": "Warehouse Dock Behavior Candidate",
                    "knowledge_types": ["LOSS_PATTERN"],
                    "asset_types": ["warehouse_distribution"],
                    "applicable_contexts": ["conditioned_loading"],
                    "hypothesis": "Dock behavior may dominate thermal losses before HVAC capex is justified.",
                    "minimum_evidence": ["dock count", "door cycle profile"],
                    "anti_triggers": ["unconditioned warehouse"],
                    "falsification_conditions": ["low door cycles"],
                    "financial_mechanism": "Thermal cost can be driven by loading behavior.",
                    "source_locator": "p.10",
                    "confidence_ceiling": "L2",
                }
            ],
            "combination_candidate_records": [
                {
                    "id": "combination_candidate::warehouse_dock_tariff_candidate",
                    "derived_from_pattern_candidate_ids": ["pattern_candidate::warehouse_dock_behavior_candidate"],
                    "name": "Warehouse Dock Tariff Candidate",
                    "combined_hypothesis": "Dock behavior and tariff timing may interact before generic retrofit logic is valid.",
                    "minimum_evidence": ["dock count", "tariff schedule"],
                    "financial_exposure": ["tariff exposure hidden"],
                    "prohibited_claims": ["roi", "peer superiority"],
                    "source_locator": "p.10",
                    "confidence_ceiling": "L2",
                }
            ],
        },
        registry_bundle=bundle,
    )

    promotions = build_extraction_promotion_registers([record], registry_bundle=bundle)

    assert len(promotions["approved_pattern_promotion_register"]) == 1
    assert len(promotions["approved_combination_promotion_register"]) == 1
    pattern_row = promotions["approved_pattern_promotion_register"][0]
    combo_row = promotions["approved_combination_promotion_register"][0]
    assert pattern_row["promotion_state"] == "ready_for_registry_review"
    assert pattern_row["proposed_spec"]["confidence_ceiling"] == "L2"
    assert combo_row["promotion_state"] == "ready_for_registry_review"
    assert combo_row["proposed_spec"]["adjudication_required"] is True
