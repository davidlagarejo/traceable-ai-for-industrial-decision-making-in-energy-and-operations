from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping

from .extractor import build_extraction_seed_from_manifest, build_knowledge_extraction_record
from .extraction_review import (
    build_extraction_promotion_registers,
    build_extraction_review_register,
)
from .local_pdf_autodraft import build_local_pdf_auto_draft_extraction_payload
from .provider_bootstrap import default_provider_launch_url
from .provider_sessions import build_provider_session_plan, provider_spec
from .research_manifest import build_research_document_manifest


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _text(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, str):
        return value.strip()
    return str(value).strip()


def _slug(value: Any) -> str:
    text = _text(value).lower()
    chars: list[str] = []
    previous_dash = False
    for ch in text:
        safe = ch if ch.isalnum() else "-"
        if safe == "-":
            if previous_dash:
                continue
            previous_dash = True
        else:
            previous_dash = False
        chars.append(safe)
    return "".join(chars).strip("-")


def _load_json(path: Path) -> dict[str, Any]:
    if not path.exists() or not path.is_file():
        return {}
    return dict(json.loads(path.read_text(encoding="utf-8")) or {})


def build_local_artifact_metadata_template(
    *,
    artifact_path: str,
    provider_key: str = "",
) -> dict[str, Any]:
    artifact = Path(str(artifact_path)).expanduser()
    provider = _text(provider_key) or "scopus"
    return {
        "provider_key": provider,
        "title": artifact.stem.replace("_", " ").replace("-", " ").strip() or "Untitled licensed paper",
        "doi": "",
        "journal": "",
        "published_year": "",
        "authors": [],
        "source_url": "",
        "abstract": "",
        "notes": "Fill metadata from Scopus or the downloaded paper before ingestion.",
    }


def build_local_artifact_extraction_template(
    *,
    artifact_path: str,
    provider_key: str = "",
    retrieval_purpose: str = "pattern_seed_discovery",
) -> dict[str, Any]:
    artifact = Path(str(artifact_path)).expanduser()
    slug = _slug(artifact.stem) or "licensed-paper"
    provider = _text(provider_key) or "scopus"
    return {
        "id": f"extract::local::{slug}",
        "version": "1.0.0",
        "source_basis_id": "licensed_research_public_technical_priors",
        "provider_key": provider,
        "document_title": artifact.stem.replace("_", " ").replace("-", " ").strip() or "Untitled licensed paper",
        "document_ref": artifact.name,
        "retrieval_purpose": _text(retrieval_purpose) or "pattern_seed_discovery",
        "extraction_mode": "governed_structured_extraction",
        "evidence_ceiling": "L2",
        "structured_prior_only": True,
        "review_status": "draft",
        "notes": "Fill knowledge atoms and candidate records from the licensed paper. Keep all claims at L2 until case evidence exists.",
        "knowledge_atoms": [],
        "pattern_candidate_records": [],
        "combination_candidate_records": [],
    }


def scaffold_local_licensed_artifact_templates(
    *,
    input_dir: str,
    provider_key: str = "",
    retrieval_purpose: str = "pattern_seed_discovery",
) -> dict[str, Any]:
    root = Path(str(input_dir)).expanduser()
    if not root.exists() or not root.is_dir():
        raise NotADirectoryError(f"input_dir must be an existing directory: {root}")

    rows: list[dict[str, Any]] = []
    for artifact_path in sorted(root.glob("*.pdf")):
        metadata_path = artifact_path.with_suffix(".metadata.json")
        extraction_path = artifact_path.with_suffix(".extraction.json")
        metadata_created = False
        extraction_created = False

        if not metadata_path.exists():
            metadata_payload = build_local_artifact_metadata_template(
                artifact_path=str(artifact_path),
                provider_key=provider_key,
            )
            metadata_path.write_text(json.dumps(metadata_payload, indent=2, sort_keys=True), encoding="utf-8")
            metadata_created = True

        if not extraction_path.exists():
            extraction_payload = build_local_artifact_extraction_template(
                artifact_path=str(artifact_path),
                provider_key=provider_key,
                retrieval_purpose=retrieval_purpose,
            )
            extraction_path.write_text(json.dumps(extraction_payload, indent=2, sort_keys=True), encoding="utf-8")
            extraction_created = True

        rows.append(
            {
                "artifact_name": artifact_path.name,
                "artifact_path": str(artifact_path),
                "metadata_path": str(metadata_path),
                "metadata_created": metadata_created,
                "extraction_path": str(extraction_path),
                "extraction_created": extraction_created,
            }
        )

    return {
        "generated_at": _utc_now_iso(),
        "input_dir": str(root),
        "summary": {
            "artifact_count": len(rows),
            "metadata_created_count": sum(1 for row in rows if row.get("metadata_created")),
            "extraction_created_count": sum(1 for row in rows if row.get("extraction_created")),
        },
        "rows": rows,
    }


def _manual_local_provider_plan(
    *,
    provider_key: str,
    retrieval_purpose: str,
    metadata: Mapping[str, Any],
) -> dict[str, Any]:
    provider = _text(provider_key) or "manual_local"
    display_name = _text(metadata.get("provider_display_name")) or provider.replace("_", " ").title()
    source_family = _text(metadata.get("source_family")) or "licensed_research_local_artifact"
    access_model = _text(metadata.get("access_model")) or "manual_local_artifact"
    source_url = _text(metadata.get("source_url")) or _text(metadata.get("document_url"))
    return {
        "provider_key": provider,
        "display_name": display_name,
        "domain_allowed": True,
        "session_required": False,
        "access_model": access_model,
        "source_family": source_family,
        "retrieval_purpose": _text(retrieval_purpose),
        "access_route": "manual_local_artifact",
        "profile_scope": "none",
        "institution_name": "",
        "institution_entry_url": "",
        "launch_url": source_url,
        "validation_url": source_url,
        "target_domain_allowlist": [],
        "session_domain_allowlist": [],
        "profile_plan": {},
        "session_state": {
            "provider_key": provider,
            "session_required": False,
            "access_route": "manual_local_artifact",
            "profile_scope": "none",
            "institution_name": "",
            "institution_entry_url": "",
            "launch_url": source_url,
            "validation_url": source_url,
            "profile_path": "",
            "profile_exists": False,
            "has_profile_contents": False,
            "auth_state": "session_not_required",
        },
    }


def build_local_licensed_artifact_package(
    *,
    local_artifact_path: str,
    metadata: Mapping[str, Any] | None = None,
    extraction_payload: Mapping[str, Any] | None = None,
    registry_bundle: dict[str, Any] | None = None,
    retrieval_purpose: str = "pattern_seed_discovery",
    source_basis_id: str = "licensed_research_public_technical_priors",
    env: Mapping[str, str] | None = None,
) -> dict[str, Any]:
    artifact_path = Path(str(local_artifact_path)).expanduser()
    if not artifact_path.exists() or not artifact_path.is_file():
        raise FileNotFoundError(f"local licensed artifact not found: {artifact_path}")

    metadata_payload = dict(metadata or {})
    metadata_autogenerated = False
    if not metadata_payload:
        metadata_payload = build_local_artifact_metadata_template(
            artifact_path=str(artifact_path),
            provider_key="manual_local",
        )
        metadata_payload["provider_key"] = "manual_local"
        metadata_payload["notes"] = (
            "Auto-generated metadata template. Update title/doi/journal/abstract if the PDF came from a licensed source."
        )
        metadata_autogenerated = True
    provider_key = _text(metadata_payload.get("provider_key")) or "manual_local"
    provider_plan: dict[str, Any]
    if provider_spec(provider_key):
        provider_url = (
            _text(metadata_payload.get("source_url"))
            or _text(metadata_payload.get("document_url"))
            or default_provider_launch_url(provider_key)
        )
        provider_plan = build_provider_session_plan(
            url=provider_url,
            retrieval_purpose=retrieval_purpose,
            session_label="licensed",
            env=dict(env) if env is not None else None,
            provider_key_override=provider_key,
        )
    else:
        provider_plan = _manual_local_provider_plan(
            provider_key=provider_key,
            retrieval_purpose=retrieval_purpose,
            metadata=metadata_payload,
        )

    source_url = (
        _text(metadata_payload.get("source_url"))
        or _text(metadata_payload.get("document_url"))
        or _text(provider_plan.get("validation_url"))
        or _text(provider_plan.get("launch_url"))
    )
    acquisition_result = {
        "status": "local_artifact_available",
        "error": "",
        "requested_url": source_url,
        "final_url": source_url,
        "html": "",
        "visible_text": _text(metadata_payload.get("abstract"))
        or _text(metadata_payload.get("summary"))
        or f"Local licensed artifact: {artifact_path.name}",
        "selector_lineage": [],
        "acquisition_mode": "manual_local_licensed_artifact",
    }
    manifest = build_research_document_manifest(
        provider_session_plan=provider_plan,
        acquisition_result=acquisition_result,
        metadata={
            "title": _text(metadata_payload.get("title")) or artifact_path.stem,
            "doi": _text(metadata_payload.get("doi")),
            "journal": _text(metadata_payload.get("journal")),
            "published_year": _text(metadata_payload.get("published_year")),
            "authors": list(metadata_payload.get("authors", []) or []),
        },
        local_artifact_path=str(artifact_path),
    )
    extraction_seed = build_extraction_seed_from_manifest(
        research_document_manifest=manifest,
        source_basis_id=source_basis_id,
        retrieval_purpose=retrieval_purpose,
    )
    package: dict[str, Any] = {
        "local_artifact_path": str(artifact_path),
        "metadata": metadata_payload,
        "metadata_autogenerated": metadata_autogenerated,
        "research_document_manifest": manifest,
        "extraction_seed": extraction_seed,
    }
    resolved_extraction_payload = dict(extraction_payload or {})
    extraction_autogenerated = False
    if not resolved_extraction_payload:
        resolved_extraction_payload = build_local_pdf_auto_draft_extraction_payload(
            artifact_path=str(artifact_path),
            metadata=metadata_payload,
            research_document_manifest=manifest,
            registry_bundle=registry_bundle,
            source_basis_id=source_basis_id,
            retrieval_purpose=retrieval_purpose,
        )
        extraction_autogenerated = True
        package["auto_generated_extraction_payload"] = dict(resolved_extraction_payload)

    if resolved_extraction_payload:
        extraction_record = build_knowledge_extraction_record(
            research_document_manifest=manifest,
            extraction_payload=resolved_extraction_payload,
            registry_bundle=registry_bundle,
        )
        package["extraction_autogenerated"] = extraction_autogenerated
        package["knowledge_extraction_record"] = extraction_record
        package["extraction_review_register"] = build_extraction_review_register([extraction_record])
        package.update(
            build_extraction_promotion_registers(
                [extraction_record],
                registry_bundle=registry_bundle,
            )
        )
    return package


def ingest_local_licensed_artifact_batch(
    *,
    input_dir: str,
    output_dir: str,
    registry_bundle: dict[str, Any] | None = None,
    retrieval_purpose: str = "pattern_seed_discovery",
    source_basis_id: str = "licensed_research_public_technical_priors",
    env: Mapping[str, str] | None = None,
) -> dict[str, Any]:
    root = Path(str(input_dir)).expanduser()
    if not root.exists() or not root.is_dir():
        raise NotADirectoryError(f"input_dir must be an existing directory: {root}")
    out_dir = Path(str(output_dir)).expanduser()
    out_dir.mkdir(parents=True, exist_ok=True)

    artifact_results: list[dict[str, Any]] = []
    extraction_records: list[dict[str, Any]] = []
    pattern_promotions: list[dict[str, Any]] = []
    combination_promotions: list[dict[str, Any]] = []

    for artifact_path in sorted(root.glob("*.pdf")):
        metadata_path = artifact_path.with_suffix(".metadata.json")
        extraction_path = artifact_path.with_suffix(".extraction.json")
        metadata = _load_json(metadata_path)
        extraction_payload = _load_json(extraction_path)
        package = build_local_licensed_artifact_package(
            local_artifact_path=str(artifact_path),
            metadata=metadata,
            extraction_payload=extraction_payload or None,
            registry_bundle=registry_bundle,
            retrieval_purpose=retrieval_purpose,
            source_basis_id=source_basis_id,
            env=env,
        )
        if not metadata and dict(package.get("metadata", {}) or {}):
            metadata_path.write_text(
                json.dumps(dict(package.get("metadata", {}) or {}), indent=2, sort_keys=True),
                encoding="utf-8",
            )
        if not extraction_payload and dict(package.get("auto_generated_extraction_payload", {}) or {}):
            extraction_path.write_text(
                json.dumps(dict(package.get("auto_generated_extraction_payload", {}) or {}), indent=2, sort_keys=True),
                encoding="utf-8",
            )
        slug = _slug(artifact_path.stem) or "artifact"
        artifact_out = out_dir / f"{slug}.result.json"
        artifact_payload = {
            "artifact_name": artifact_path.name,
            "artifact_path": str(artifact_path),
            "metadata_path": str(metadata_path),
            "extraction_path": str(extraction_path),
            **package,
        }
        artifact_out.write_text(json.dumps(artifact_payload, indent=2, sort_keys=True), encoding="utf-8")
        artifact_results.append(
            {
                "artifact_name": artifact_path.name,
                "artifact_path": str(artifact_path),
                "result_path": str(artifact_out),
                "provider_key": _text((package.get("research_document_manifest", {}) or {}).get("provider_key")),
                "document_title": _text((package.get("research_document_manifest", {}) or {}).get("title")),
                "has_extraction_payload": bool(extraction_payload or package.get("auto_generated_extraction_payload")),
                "metadata_autogenerated": bool(package.get("metadata_autogenerated", False)),
                "extraction_autogenerated": bool(package.get("extraction_autogenerated", False)),
            }
        )
        extraction_record = dict(package.get("knowledge_extraction_record", {}) or {})
        if extraction_record:
            extraction_records.append(extraction_record)
        pattern_promotions.extend(list(package.get("approved_pattern_promotion_register", []) or []))
        combination_promotions.extend(list(package.get("approved_combination_promotion_register", []) or []))

    batch_payload = {
        "generated_at": _utc_now_iso(),
        "input_dir": str(root),
        "output_dir": str(out_dir),
        "retrieval_purpose": retrieval_purpose,
        "source_basis_id": source_basis_id,
        "summary": {
            "artifact_count": len(artifact_results),
            "extraction_record_count": len(extraction_records),
            "approved_pattern_promotion_count": len(pattern_promotions),
            "approved_combination_promotion_count": len(combination_promotions),
        },
        "artifact_results": artifact_results,
        "extraction_review_register": build_extraction_review_register(extraction_records),
        "approved_pattern_promotion_register": pattern_promotions,
        "approved_combination_promotion_register": combination_promotions,
    }
    batch_manifest = out_dir / "batch_result.json"
    batch_manifest.write_text(json.dumps(batch_payload, indent=2, sort_keys=True), encoding="utf-8")
    batch_payload["batch_result_path"] = str(batch_manifest)
    return batch_payload
