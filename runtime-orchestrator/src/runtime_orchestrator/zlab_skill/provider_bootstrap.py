from __future__ import annotations

from pathlib import Path
from typing import Any
from os import environ
from urllib.parse import urlparse

from .provider_sessions import build_provider_session_plan


_DEFAULT_PROVIDER_LAUNCH_URLS = {
    "scopus": "https://www.scopus.com/",
    "elsevier": "https://www.elsevier.com/",
    "ieee": "https://ieeexplore.ieee.org/",
    "springer": "https://link.springer.com/",
    "ashrae": "https://www.ashrae.org/",
    "doe": "https://www.energy.gov/",
    "epa": "https://www.epa.gov/",
}


def _runtime_root() -> Path:
    return Path(__file__).resolve().parents[3]


def _bootstrap_script_path() -> Path:
    return _runtime_root() / "scripts" / "bootstrap_licensed_provider_session.py"


def default_provider_launch_url(provider_key: str) -> str:
    return str(_DEFAULT_PROVIDER_LAUNCH_URLS.get(str(provider_key or "").strip().lower(), "")).strip()


def _url_host(url: str) -> str:
    return urlparse(str(url or "").strip()).netloc.strip().lower()


def _host_matches_allowed_domains(host: str, allowed_domains: list[str]) -> bool:
    lowered_host = str(host or "").strip().lower()
    for domain in list(allowed_domains or []):
        domain_text = str(domain or "").strip().lower()
        if lowered_host == domain_text or lowered_host.endswith(f".{domain_text}"):
            return True
    return False


def build_provider_bootstrap_plan(
    *,
    provider_key: str,
    session_label: str = "licensed",
    launch_url: str = "",
    headless: bool = False,
    timeout_ms: int = 12_000,
    env: dict[str, str] | None = None,
) -> dict[str, Any]:
    normalized_provider = str(provider_key or "").strip().lower()
    canonical_provider_url = default_provider_launch_url(normalized_provider)
    resolved_url = str(launch_url or canonical_provider_url).strip()
    session_plan = build_provider_session_plan(
        url=resolved_url,
        retrieval_purpose="provider_session_bootstrap",
        session_label=session_label,
        env=env if env is not None else environ,
        provider_key_override=normalized_provider,
    )
    bootstrap_launch_url = str(session_plan.get("launch_url", "")).strip() or resolved_url
    validation_url = str(session_plan.get("validation_url", "")).strip() or canonical_provider_url or resolved_url
    allowed_domains = list(session_plan.get("target_domain_allowlist", []) or [])
    if canonical_provider_url and bootstrap_launch_url:
        launch_host = _url_host(bootstrap_launch_url)
        if launch_host and allowed_domains and not _host_matches_allowed_domains(launch_host, allowed_domains):
            validation_url = canonical_provider_url
    script_path = _bootstrap_script_path()
    command_argv = [
        "python3",
        str(script_path),
        "--provider-key",
        normalized_provider,
        "--session-label",
        str(session_label or "licensed").strip().lower(),
        "--url",
        bootstrap_launch_url,
        "--timeout-ms",
        str(int(timeout_ms)),
    ]
    command_argv.append("--headless" if headless else "--headful")
    validate_argv = command_argv + ["--validate-url", validation_url, "--validate-auth"]
    return {
        "provider_key": normalized_provider,
        "launch_url": bootstrap_launch_url,
        "validation_url": validation_url,
        "access_route": str(session_plan.get("access_route", "")).strip(),
        "profile_scope": str(session_plan.get("profile_scope", "")).strip(),
        "institution_name": str(session_plan.get("institution_name", "")).strip(),
        "institution_entry_url": str(session_plan.get("institution_entry_url", "")).strip(),
        "profile_path": str(((session_plan.get("session_state", {}) or {}).get("profile_path", "")).strip()),
        "script_path": str(script_path),
        "command_argv": command_argv,
        "display_command": " ".join(command_argv),
        "validate_command_argv": validate_argv,
        "validate_display_command": " ".join(validate_argv),
    }
