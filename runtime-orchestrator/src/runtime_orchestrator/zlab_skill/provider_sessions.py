from __future__ import annotations

import os
from typing import Any
from urllib.parse import urlparse
from pathlib import Path

from .playwright_profiles import build_profile_plan, provider_domain_allowlist


_PROVIDER_SPECS = {
    "scopus": {
        "display_name": "Scopus",
        "domains": ["scopus.com", "scopuspreview.com"],
        "session_required": True,
        "access_model": "licensed_discovery",
        "source_family": "licensed_research_discovery",
    },
    "elsevier": {
        "display_name": "Elsevier",
        "domains": ["sciencedirect.com", "elsevier.com"],
        "session_required": True,
        "access_model": "licensed_fulltext",
        "source_family": "licensed_research_fulltext",
    },
    "ieee": {
        "display_name": "IEEE Xplore",
        "domains": ["ieeexplore.ieee.org", "ieee.org"],
        "session_required": True,
        "access_model": "licensed_fulltext",
        "source_family": "licensed_research_fulltext",
    },
    "springer": {
        "display_name": "Springer Link",
        "domains": ["link.springer.com", "springer.com"],
        "session_required": True,
        "access_model": "licensed_fulltext",
        "source_family": "licensed_research_fulltext",
    },
    "ashrae": {
        "display_name": "ASHRAE",
        "domains": ["ashrae.org"],
        "session_required": False,
        "access_model": "public_or_member_guidance",
        "source_family": "public_technical_guidance",
    },
    "doe": {
        "display_name": "DOE",
        "domains": ["energy.gov"],
        "session_required": False,
        "access_model": "public_guidance",
        "source_family": "public_technical_guidance",
    },
    "epa": {
        "display_name": "EPA",
        "domains": ["epa.gov"],
        "session_required": False,
        "access_model": "public_guidance",
        "source_family": "public_technical_guidance",
    },
}


_INSTITUTION_ENTRY_URL_ENV = "ZLAB_LICENSED_INSTITUTION_ENTRY_URL"
_INSTITUTION_NAME_ENV = "ZLAB_LICENSED_INSTITUTION_NAME"
_PROVIDER_VALIDATION_URL_ENV_PREFIX = "ZLAB_LICENSED_PROVIDER_VALIDATION_URL_"
_PROVIDER_INSTITUTION_ENTRY_URL_ENV_PREFIX = "ZLAB_LICENSED_INSTITUTION_ENTRY_URL_"
_PROVIDER_INSTITUTION_NAME_ENV_PREFIX = "ZLAB_LICENSED_INSTITUTION_NAME_"


def _host(url: str) -> str:
    parsed = urlparse(str(url or "").strip())
    return parsed.netloc.strip().lower()


def _merge_allowed_domains(*domain_groups: list[str]) -> list[str]:
    merged: list[str] = []
    seen: set[str] = set()
    for group in domain_groups:
        for domain in list(group or []):
            domain_text = str(domain or "").strip().lower()
            if not domain_text or domain_text in seen:
                continue
            seen.add(domain_text)
            merged.append(domain_text)
    return merged


def provider_key_for_url(url: str) -> str:
    host = _host(url)
    if not host:
        return ""
    for provider_key, spec in _PROVIDER_SPECS.items():
        for domain in spec.get("domains", []):
            domain_text = str(domain or "").strip().lower()
            if host == domain_text or host.endswith(f".{domain_text}"):
                return provider_key
    return ""


def provider_spec(provider_key: str) -> dict[str, Any]:
    return dict(_PROVIDER_SPECS.get(str(provider_key or "").strip().lower(), {}))


def _normalized_provider(provider_key: str) -> str:
    return str(provider_key or "").strip().lower()


def _provider_env_suffix(provider_key: str) -> str:
    return _normalized_provider(provider_key).upper().replace("-", "_").replace(" ", "_")


def licensed_institution_entry_url(provider_key: str = "", env: dict[str, str] | None = None) -> str:
    values = env if env is not None else os.environ
    provider_suffix = _provider_env_suffix(provider_key)
    if provider_suffix:
        provider_value = str(values.get(f"{_PROVIDER_INSTITUTION_ENTRY_URL_ENV_PREFIX}{provider_suffix}", "")).strip()
        if provider_value:
            return provider_value
    return str(values.get(_INSTITUTION_ENTRY_URL_ENV, "")).strip()


def licensed_institution_name(provider_key: str = "", env: dict[str, str] | None = None) -> str:
    values = env if env is not None else os.environ
    provider_suffix = _provider_env_suffix(provider_key)
    if provider_suffix:
        provider_value = str(values.get(f"{_PROVIDER_INSTITUTION_NAME_ENV_PREFIX}{provider_suffix}", "")).strip()
        if provider_value:
            return provider_value
    return str(values.get(_INSTITUTION_NAME_ENV, "")).strip()


def provider_validation_url(provider_key: str, *, fallback_url: str, env: dict[str, str] | None = None) -> str:
    values = env if env is not None else os.environ
    provider_suffix = _provider_env_suffix(provider_key)
    if provider_suffix:
        override = str(values.get(f"{_PROVIDER_VALIDATION_URL_ENV_PREFIX}{provider_suffix}", "")).strip()
        if override:
            return override
    return str(fallback_url or "").strip()


def describe_provider_session_state(
    *,
    provider_plan: dict[str, Any],
) -> dict[str, Any]:
    plan = dict(provider_plan or {})
    profile_plan = dict(plan.get("profile_plan", {}) or {})
    profile_path = Path(str(profile_plan.get("profile_path", "")).strip()).expanduser()
    profile_exists = profile_path.exists()
    has_profile_contents = profile_exists and any(profile_path.iterdir())
    session_required = bool(plan.get("session_required", False))
    if not plan.get("domain_allowed"):
        auth_state = "unsupported_provider"
    elif not session_required:
        auth_state = "session_not_required"
    elif has_profile_contents:
        auth_state = "profile_present_session_unknown"
    elif profile_exists:
        auth_state = "profile_initialized_session_unknown"
    else:
        auth_state = "profile_missing"
    return {
        "provider_key": str(plan.get("provider_key", "")).strip(),
        "session_required": session_required,
        "access_route": str(plan.get("access_route", "")).strip(),
        "profile_scope": str(plan.get("profile_scope", "")).strip(),
        "institution_name": str(plan.get("institution_name", "")).strip(),
        "institution_entry_url": str(plan.get("institution_entry_url", "")).strip(),
        "launch_url": str(plan.get("launch_url", "")).strip(),
        "validation_url": str(plan.get("validation_url", "")).strip(),
        "profile_path": str(profile_path) if str(profile_path) else "",
        "profile_exists": profile_exists,
        "has_profile_contents": has_profile_contents,
        "auth_state": auth_state,
    }


def build_provider_session_plan(
    *,
    url: str,
    retrieval_purpose: str,
    session_label: str = "primary",
    env: dict[str, str] | None = None,
    provider_key_override: str = "",
) -> dict[str, Any]:
    provider_key = _normalized_provider(provider_key_override) or provider_key_for_url(url)
    spec = provider_spec(provider_key)
    if not spec:
        return {
            "provider_key": "",
            "display_name": "",
            "domain_allowed": False,
            "session_required": False,
            "access_model": "",
            "source_family": "",
            "retrieval_purpose": str(retrieval_purpose or "").strip(),
            "access_route": "",
            "profile_scope": "",
            "institution_name": "",
            "institution_entry_url": "",
            "launch_url": "",
            "validation_url": "",
            "target_domain_allowlist": [],
            "profile_plan": {},
        }
    institution_entry = licensed_institution_entry_url(provider_key, env=env)
    institution_name = licensed_institution_name(provider_key, env=env)
    session_required = bool(spec.get("session_required", False))
    validation_url = provider_validation_url(provider_key, fallback_url=url, env=env)
    use_institution_gateway = session_required and bool(institution_entry)
    access_route = "institutional_gateway" if use_institution_gateway else "direct_provider"
    profile_scope = "institution_shared" if use_institution_gateway else "provider_specific"
    launch_url = institution_entry if use_institution_gateway else str(url or "").strip()
    profile_plan = (
        build_profile_plan("institution", session_label=session_label)
        if use_institution_gateway
        else build_profile_plan(provider_key, session_label=session_label)
    )
    provider_domains = provider_domain_allowlist(provider_key)
    session_domain_allowlist = _merge_allowed_domains(
        provider_domains,
        [_host(institution_entry)] if institution_entry else [],
        [_host(launch_url)] if launch_url else [],
        [_host(validation_url)] if validation_url else [],
    )
    plan = {
        "provider_key": provider_key,
        "display_name": str(spec.get("display_name", "")).strip(),
        "domain_allowed": True,
        "session_required": session_required,
        "access_model": str(spec.get("access_model", "")).strip(),
        "source_family": str(spec.get("source_family", "")).strip(),
        "retrieval_purpose": str(retrieval_purpose or "").strip(),
        "access_route": access_route,
        "profile_scope": profile_scope,
        "institution_name": institution_name,
        "institution_entry_url": institution_entry,
        "launch_url": launch_url,
        "validation_url": validation_url,
        "target_domain_allowlist": provider_domains,
        "session_domain_allowlist": session_domain_allowlist,
        "profile_plan": profile_plan,
    }
    plan["session_state"] = describe_provider_session_state(provider_plan=plan)
    return plan
