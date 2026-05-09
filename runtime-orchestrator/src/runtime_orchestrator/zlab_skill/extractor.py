from __future__ import annotations

from typing import Any

from .extraction_schema import validate_knowledge_extraction_record
from .schema import RegistryValidationError


def _text(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, str):
        return value.strip()
    return str(value).strip()


def _document_ref(manifest: dict[str, Any]) -> str:
    return (
        _text(manifest.get("doi"))
        or _text(((manifest.get("provenance_manifest") or {}).get("final_url")))
        or _text(manifest.get("title"))
        or _text(manifest.get("provider_key"))
    )


def build_extraction_seed_from_manifest(
    *,
    research_document_manifest: dict[str, Any],
    source_basis_id: str = "licensed_research_public_technical_priors",
    retrieval_purpose: str = "",
) -> dict[str, Any]:
    manifest = dict(research_document_manifest or {})
    return {
        "id": f"extract::{_text(manifest.get('provider_key')) or 'provider'}::{_text(manifest.get('doi')) or _text(manifest.get('title')) or 'document'}",
        "version": "1.0.0",
        "source_basis_id": _text(source_basis_id) or "licensed_research_public_technical_priors",
        "provider_key": _text(manifest.get("provider_key")) or "unknown_provider",
        "document_title": _text(manifest.get("title")) or "Untitled research document",
        "document_ref": _document_ref(manifest),
        "retrieval_purpose": _text(retrieval_purpose) or _text(manifest.get("retrieval_purpose")) or "pattern_seed_discovery",
        "extraction_mode": "governed_structured_extraction",
        "evidence_ceiling": "L2",
        "structured_prior_only": True,
        "provenance_manifest": dict(manifest.get("provenance_manifest", {}) or {}),
        "knowledge_atoms": [],
        "pattern_candidate_records": [],
        "combination_candidate_records": [],
        "review_status": "draft",
        "notes": "",
    }


def build_knowledge_extraction_record(
    *,
    research_document_manifest: dict[str, Any],
    extraction_payload: dict[str, Any],
    registry_bundle: dict[str, Any] | None = None,
) -> dict[str, Any]:
    manifest = dict(research_document_manifest or {})
    payload = dict(extraction_payload or {})
    seed = build_extraction_seed_from_manifest(
        research_document_manifest=manifest,
        source_basis_id=_text(payload.get("source_basis_id")) or "licensed_research_public_technical_priors",
        retrieval_purpose=_text(payload.get("retrieval_purpose")),
    )
    merged = dict(seed)
    merged.update(payload)
    merged["provider_key"] = _text(payload.get("provider_key")) or seed["provider_key"]
    merged["document_title"] = _text(payload.get("document_title")) or seed["document_title"]
    merged["document_ref"] = _text(payload.get("document_ref")) or seed["document_ref"]
    merged["retrieval_purpose"] = _text(payload.get("retrieval_purpose")) or seed["retrieval_purpose"]
    merged["provenance_manifest"] = dict(manifest.get("provenance_manifest", {}) or seed["provenance_manifest"])
    merged["structured_prior_only"] = True
    merged["evidence_ceiling"] = "L2"

    if registry_bundle is not None:
        source_basis_id = _text(merged.get("source_basis_id"))
        source_basis_by_id = dict((registry_bundle or {}).get("source_basis_by_id", {}) or {})
        if source_basis_id and source_basis_id not in source_basis_by_id:
            raise RegistryValidationError(f"unknown source_basis_id: {source_basis_id}")

    return validate_knowledge_extraction_record(merged)
