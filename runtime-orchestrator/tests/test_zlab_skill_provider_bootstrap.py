from runtime_orchestrator.zlab_skill import build_provider_bootstrap_plan, default_provider_launch_url


def test_default_provider_launch_url_maps_core_licensed_providers() -> None:
    assert default_provider_launch_url("elsevier") == "https://www.elsevier.com/"
    assert default_provider_launch_url("ieee") == "https://ieeexplore.ieee.org/"
    assert default_provider_launch_url("springer") == "https://link.springer.com/"
    assert default_provider_launch_url("scopus") == "https://www.scopus.com/"


def test_build_provider_bootstrap_plan_exposes_login_and_validation_commands() -> None:
    plan = build_provider_bootstrap_plan(
        provider_key="elsevier",
        session_label="licensed",
        headless=False,
    )

    assert plan["provider_key"] == "elsevier"
    assert plan["launch_url"] == "https://www.elsevier.com/"
    assert "bootstrap_licensed_provider_session.py" in plan["script_path"]
    assert "--provider-key" in plan["command_argv"]
    assert "elsevier" in plan["command_argv"]
    assert "--headful" in plan["command_argv"]
    assert "--validate-auth" in plan["validate_command_argv"]
    assert "bootstrap_licensed_provider_session.py" in plan["display_command"]


def test_build_provider_bootstrap_plan_supports_institution_entry_and_provider_validation() -> None:
    plan = build_provider_bootstrap_plan(
        provider_key="ieee",
        session_label="licensed",
        headless=False,
        env={
            "ZLAB_LICENSED_INSTITUTION_ENTRY_URL": "https://library.example.edu/login",
            "ZLAB_LICENSED_INSTITUTION_NAME": "Example University",
        },
    )

    assert plan["access_route"] == "institutional_gateway"
    assert plan["profile_scope"] == "institution_shared"
    assert plan["institution_name"] == "Example University"
    assert plan["launch_url"] == "https://library.example.edu/login"
    assert plan["validation_url"] == "https://ieeexplore.ieee.org/"
    assert "--validate-url" in plan["validate_command_argv"]
    assert "https://ieeexplore.ieee.org/" in plan["validate_command_argv"]


def test_build_provider_bootstrap_plan_allows_institutional_launch_url_outside_provider_domain() -> None:
    plan = build_provider_bootstrap_plan(
        provider_key="scopus",
        session_label="licensed",
        headless=False,
        launch_url="https://proxyutp.elogim.com/auth-meta/login.php?url=https://scopus.proxyutp.elogim.com/",
    )

    assert plan["provider_key"] == "scopus"
    assert plan["launch_url"].startswith("https://proxyutp.elogim.com/")
    assert plan["validation_url"] == "https://www.scopus.com/"
