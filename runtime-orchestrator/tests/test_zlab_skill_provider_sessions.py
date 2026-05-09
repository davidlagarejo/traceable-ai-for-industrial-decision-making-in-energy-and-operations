from pathlib import Path

from runtime_orchestrator.zlab_skill import (
    build_profile_plan,
    build_provider_session_plan,
    provider_key_for_url,
)


def test_provider_key_for_url_maps_licensed_domains() -> None:
    assert provider_key_for_url("https://www.sciencedirect.com/science/article/pii/S0360544218311234") == "elsevier"
    assert provider_key_for_url("https://ieeexplore.ieee.org/document/1234567") == "ieee"
    assert provider_key_for_url("https://link.springer.com/article/10.1007/s12345-026-00001") == "springer"
    assert provider_key_for_url("https://www.scopus.com/record/display.uri?eid=2-s2.0-123456") == "scopus"


def test_build_profile_plan_is_provider_namespaced(tmp_path: Path) -> None:
    profile = build_profile_plan("elsevier", root_dir=tmp_path, session_label="licensed")

    assert profile["provider_key"] == "elsevier"
    assert profile["profile_key"] == "zlab_skill_elsevier_licensed"
    assert profile["profile_path"].endswith("zlab_skill_elsevier_licensed")
    assert profile["profile_exists"] is False


def test_build_provider_session_plan_marks_session_required_providers() -> None:
    plan = build_provider_session_plan(
        url="https://ieeexplore.ieee.org/document/1234567",
        retrieval_purpose="pattern_seed_discovery",
    )

    assert plan["provider_key"] == "ieee"
    assert plan["session_required"] is True
    assert plan["source_family"] == "licensed_research_fulltext"
    assert plan["profile_plan"]["profile_key"] == "zlab_skill_ieee_primary"


def test_build_provider_session_plan_supports_institutional_gateway() -> None:
    plan = build_provider_session_plan(
        url="https://www.sciencedirect.com/science/article/pii/S0360544218311234",
        retrieval_purpose="pattern_seed_discovery",
        session_label="licensed",
        env={
            "ZLAB_LICENSED_INSTITUTION_ENTRY_URL": "https://library.example.edu/login",
            "ZLAB_LICENSED_INSTITUTION_NAME": "Example University",
        },
    )

    assert plan["provider_key"] == "elsevier"
    assert plan["access_route"] == "institutional_gateway"
    assert plan["profile_scope"] == "institution_shared"
    assert plan["launch_url"] == "https://library.example.edu/login"
    assert plan["validation_url"] == "https://www.sciencedirect.com/science/article/pii/S0360544218311234"
    assert plan["institution_name"] == "Example University"
    assert plan["profile_plan"]["profile_key"] == "zlab_skill_institution_licensed"


def test_build_provider_session_plan_allows_explicit_provider_override_for_institution_link() -> None:
    plan = build_provider_session_plan(
        url="https://proxyutp.elogim.com/auth-meta/login.php?url=https://scopus.proxyutp.elogim.com/",
        retrieval_purpose="provider_session_bootstrap",
        session_label="licensed",
        provider_key_override="scopus",
    )

    assert plan["provider_key"] == "scopus"
    assert plan["session_required"] is True
    assert plan["source_family"] == "licensed_research_discovery"
    assert "proxyutp.elogim.com" in plan["session_domain_allowlist"]
