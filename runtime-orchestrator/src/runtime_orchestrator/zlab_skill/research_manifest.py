from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Any

from runtime_orchestrator.source_acquisition.provenance import build_provenance_manifest


def _sha256_file(path: Path | None) -> str:
    if path is None or not path.exists() or not path.is_file():
        return ""
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        while True:
            chunk = handle.read(8192)
            if not chunk:
                break
            digest.update(chunk)
    return digest.hexdigest()


def build_research_document_manifest(
    *,
    provider_session_plan: dict[str, Any],
    acquisition_result: dict[str, Any],
    metadata: dict[str, Any] | None = None,
    local_artifact_path: str = "",
) -> dict[str, Any]:
    metadata = dict(metadata or {})
    artifact_path = Path(local_artifact_path).expanduser() if str(local_artifact_path or "").strip() else None
    provenance = build_provenance_manifest(
        acquisition_mode=str(acquisition_result.get("acquisition_mode", "")).strip(),
        requested_url=str(acquisition_result.get("requested_url", "")).strip(),
        final_url=str(acquisition_result.get("final_url", "")).strip(),
        html=str(acquisition_result.get("html", "") or ""),
        visible_text=str(acquisition_result.get("visible_text", "") or ""),
        selector_lineage=list(acquisition_result.get("selector_lineage", []) or []),
        attempt_outcome=str(acquisition_result.get("status", "")).strip(),
    )
    return {
        "provider_key": str(provider_session_plan.get("provider_key", "")).strip(),
        "provider_display_name": str(provider_session_plan.get("display_name", "")).strip(),
        "access_model": str(provider_session_plan.get("access_model", "")).strip(),
        "access_route": str(provider_session_plan.get("access_route", "")).strip(),
        "profile_scope": str(provider_session_plan.get("profile_scope", "")).strip(),
        "institution_name": str(provider_session_plan.get("institution_name", "")).strip(),
        "institution_entry_url": str(provider_session_plan.get("institution_entry_url", "")).strip(),
        "validation_url": str(provider_session_plan.get("validation_url", "")).strip(),
        "source_family": str(provider_session_plan.get("source_family", "")).strip(),
        "retrieval_purpose": str(provider_session_plan.get("retrieval_purpose", "")).strip(),
        "profile_key": str((provider_session_plan.get("profile_plan", {}) or {}).get("profile_key", "")).strip(),
        "title": str(metadata.get("title", "")).strip(),
        "doi": str(metadata.get("doi", "")).strip(),
        "journal": str(metadata.get("journal", "")).strip(),
        "published_year": str(metadata.get("published_year", "")).strip(),
        "authors": list(metadata.get("authors", []) or []),
        "local_artifact_path": str(artifact_path) if artifact_path else "",
        "local_artifact_sha256": _sha256_file(artifact_path),
        "keep_fulltext_outside_git": True,
        "structured_extraction_allowed": True,
        "provenance_manifest": provenance,
    }
