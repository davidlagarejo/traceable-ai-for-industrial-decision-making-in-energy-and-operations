from __future__ import annotations

from runtime_orchestrator.congruence_intelligence.empty_section_policy import (
    apply_empty_section_policy,
    build_empty_section_policy_register,
    build_section_explanation_fallback_register,
    build_section_population_status_register,
)


def test_empty_section_policy_builds_peer_and_source_fallbacks():
    register = build_section_explanation_fallback_register(
        competitive_comparison_register=[],
        comparison_not_yet_valid_register=[
            {
                "explanation": "Competitive comparison is blocked until dock density and control boundary are normalized.",
                "required_before_comparison": ["dock density", "control boundary", "charging profile"],
            }
        ],
        comparison_blocker_register=[],
        peer_requirement_register=[],
        source_family_coverage_table=[],
        search_attempt_ledger=[{"source_family": "county assessor"}, {"source_family": "leasing brochure"}],
        discovery_need_register=[{"discovery_need": "Confirm warehouse subtype."}],
        next_best_search_register=[{"expected_evidence": ["utility tariff", "operator confirmation"]}],
    )

    by_key = {row["section_key"]: row for row in register}
    assert "peer_comparison" in by_key
    assert "public_source_coverage" in by_key
    assert by_key["peer_comparison"]["what_is_required"]
    assert by_key["public_source_coverage"]["what_was_attempted"]


def test_empty_section_policy_replaces_dead_section_with_explanatory_fallback():
    fallback_register = build_section_explanation_fallback_register(
        competitive_comparison_register=[],
        comparison_not_yet_valid_register=[
            {
                "explanation": "Competitive comparison is blocked until dock density and control boundary are normalized.",
                "required_before_comparison": ["dock density", "control boundary"],
            }
        ],
        comparison_blocker_register=[],
        peer_requirement_register=[],
        source_family_coverage_table=[],
        search_attempt_ledger=[],
        discovery_need_register=[],
        next_best_search_register=[],
    )
    body_sections = [
        {
            "section_id": "c10_competitive_peer",
            "title": "Competitive / Peer Comparison",
            "blocks": [{"content": "No competitive-comparison rows were produced."}],
        }
    ]
    appendix_sections = [
        {
            "section_id": "a6_public_source_coverage",
            "title": "Public Source Coverage Table",
            "blocks": [{"content": "No routed public-source coverage rows were produced."}],
        }
    ]

    body_out, appendix_out, applied_rows, population_rows = apply_empty_section_policy(
        body_sections=body_sections,
        appendix_sections=appendix_sections,
        section_explanation_fallback_register=fallback_register,
    )
    policy_register = build_empty_section_policy_register(applied_policy_rows=applied_rows)
    status_register = build_section_population_status_register(section_population_rows=population_rows)

    assert "What is required to populate it:" in body_out[0]["blocks"][0]["content"]
    assert "This section is intentionally explained rather than left empty." in appendix_out[0]["blocks"][0]["content"]
    assert body_out[0]["empty_section_policy_applied"] is True
    assert appendix_out[0]["section_population_state"] == "explained_fallback"
    assert len(policy_register) == 2
    assert all(row["population_state"] == "explained_fallback" for row in status_register)
