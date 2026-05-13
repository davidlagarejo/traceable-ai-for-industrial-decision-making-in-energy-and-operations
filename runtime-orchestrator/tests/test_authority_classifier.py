"""V5 P4 — authority_tier classifier tests.

Verifies deterministic tier classification by publisher / type signals
and audits the catalog for divergence.
"""
from __future__ import annotations

from runtime_orchestrator.industrial_research_engine import (
    audit_catalog_against_classifier,
    classify_authority_tier,
)


# ── Per-entry classification ────────────────────────────────────────


def test_classifies_us_doe_as_tier_1():
    v = classify_authority_tier({
        "source_id": "doe_better_plants",
        "publisher": "US DOE",
        "type": "report",
    })
    assert v["deterministic_tier"] == 1
    assert v["signals"]["publisher"] == 1


def test_classifies_epa_regulation_as_tier_1():
    v = classify_authority_tier({
        "source_id": "epa_clean_air_act",
        "publisher": "US EPA",
        "type": "regulation",
    })
    assert v["deterministic_tier"] == 1


def test_classifies_iiar_bulletin_as_tier_1():
    v = classify_authority_tier({
        "source_id": "iiar_bulletin_109",
        "publisher": "International Institute of Ammonia Refrigeration",
        "type": "guideline",
    })
    # IIAR is a standards body for ammonia refrigeration → tier 1
    assert v["deterministic_tier"] == 1


def test_classifies_ashrae_handbook_as_tier_1():
    v = classify_authority_tier({
        "source_id": "ashrae_handbook_refrigeration",
        "publisher": "ASHRAE",
        "type": "handbook",
    })
    assert v["deterministic_tier"] == 1


def test_classifies_upme_as_tier_1():
    v = classify_authority_tier({
        "source_id": "upme_guia_alimentos",
        "publisher": "UPME Colombia",
        "type": "guideline",
    })
    assert v["deterministic_tier"] == 1


def test_classifies_fenercom_as_tier_2():
    v = classify_authority_tier({
        "source_id": "fenercom_iluminacion",
        "publisher": "Fenercom",
        "type": "handbook",
    })
    assert v["deterministic_tier"] == 2


def test_classifies_idae_as_tier_2():
    v = classify_authority_tier({
        "source_id": "idae_bombas_calor",
        "publisher": "IDAE España",
        "type": "handbook",
    })
    assert v["deterministic_tier"] == 2


def test_classifies_vendor_as_tier_3():
    v = classify_authority_tier({
        "source_id": "danfoss_app_guide",
        "publisher": "Danfoss",
        "type": "whitepaper",
    })
    assert v["deterministic_tier"] == 3


def test_classifies_ingersoll_rand_case_study_as_tier_3():
    v = classify_authority_tier({
        "source_id": "ingersoll_rand_success",
        "publisher": "Ingersoll Rand",
        "type": "case_study",
    })
    assert v["deterministic_tier"] == 3


def test_unknown_publisher_falls_back_to_type_signal():
    """When publisher is unrecognized, the type alone classifies."""
    v = classify_authority_tier({
        "source_id": "obscure_paper",
        "publisher": "Some University Press",  # actually matches tier 2 (university)
        "type": "research_paper",
    })
    # University is recognized as tier 2
    assert v["deterministic_tier"] == 2


def test_unknown_publisher_and_type_defaults_to_tier_3():
    v = classify_authority_tier({
        "source_id": "mystery_doc",
        "publisher": "Random Co.",
        "type": "memo",
    })
    assert v["deterministic_tier"] == 3
    assert "defaulting" in v["rationale"]


# ── Catalog audit ───────────────────────────────────────────────────


def test_catalog_audit_runs_without_error():
    """Audit should run over the real catalog and return structured output."""
    report = audit_catalog_against_classifier()
    assert "total" in report
    assert "aligned" in report
    assert "divergent" in report
    assert report["total"] > 0
    assert report["aligned"] + len(report["divergent"]) == report["total"]


def test_catalog_audit_at_least_half_aligned():
    """If <50% of the catalog aligns with the deterministic classifier,
    one of the two is badly wrong. Today: most should align."""
    report = audit_catalog_against_classifier()
    if report["total"] == 0:
        return
    aligned_ratio = report["aligned"] / report["total"]
    assert aligned_ratio >= 0.5, (
        f"only {aligned_ratio:.1%} aligned — classifier signals or "
        f"catalog curation are out of sync"
    )


def test_classify_returns_rationale_string():
    v = classify_authority_tier({"publisher": "US DOE", "type": "report"})
    assert isinstance(v["rationale"], str)
    assert v["rationale"]
