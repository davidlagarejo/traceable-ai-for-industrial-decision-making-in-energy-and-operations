from __future__ import annotations

from pathlib import Path
from typing import Any


_DEFAULT_PROFILE_ROOT = Path.home() / ".zlab_skill" / "playwright_profiles"
_PROVIDER_DOMAIN_ALLOWLIST = {
    "scopus": ["scopus.com", "scopuspreview.com"],
    "elsevier": ["sciencedirect.com", "elsevier.com"],
    "ieee": ["ieeexplore.ieee.org", "ieee.org"],
    "springer": ["link.springer.com", "springer.com"],
    "ashrae": ["ashrae.org"],
    "doe": ["energy.gov"],
    "epa": ["epa.gov"],
}


def default_profile_root() -> Path:
    return _DEFAULT_PROFILE_ROOT


def provider_profile_key(provider_key: str, *, session_label: str = "primary") -> str:
    provider = str(provider_key or "").strip().lower().replace(" ", "_")
    label = str(session_label or "primary").strip().lower().replace(" ", "_")
    return f"zlab_skill_{provider}_{label}"


def provider_profile_path(
    provider_key: str,
    *,
    root_dir: Path | None = None,
    session_label: str = "primary",
) -> Path:
    root = root_dir or default_profile_root()
    return root / provider_profile_key(provider_key, session_label=session_label)


def provider_domain_allowlist(provider_key: str) -> list[str]:
    return list(_PROVIDER_DOMAIN_ALLOWLIST.get(str(provider_key or "").strip().lower(), []))


def build_profile_plan(
    provider_key: str,
    *,
    root_dir: Path | None = None,
    session_label: str = "primary",
) -> dict[str, Any]:
    profile_path = provider_profile_path(
        provider_key,
        root_dir=root_dir,
        session_label=session_label,
    )
    return {
        "provider_key": str(provider_key or "").strip().lower(),
        "session_label": str(session_label or "primary").strip().lower(),
        "profile_key": provider_profile_key(provider_key, session_label=session_label),
        "profile_root": str((root_dir or default_profile_root()).resolve()),
        "profile_path": str(profile_path.resolve()),
        "profile_exists": profile_path.exists(),
        "domain_allowlist": provider_domain_allowlist(provider_key),
    }
