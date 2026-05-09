from __future__ import annotations

import csv
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping

from .extractor import build_extraction_seed_from_manifest, build_knowledge_extraction_record
from .extraction_review import (
    build_extraction_promotion_registers,
    build_extraction_review_register,
)
from .local_pdf_autodraft import build_structured_prior_candidates_from_text
from .provider_sessions import build_provider_session_plan
from .provider_bootstrap import default_provider_launch_url
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


def _field(row: Mapping[str, Any], *aliases: str) -> str:
    lowered = {_text(key).lower(): value for key, value in dict(row or {}).items()}
    for alias in aliases:
        value = lowered.get(_text(alias).lower())
        text = _text(value)
        if text:
            return text
    return ""


def _list_field(row: Mapping[str, Any], *aliases: str) -> list[str]:
    raw = _field(row, *aliases)
    if not raw:
        return []
    normalized = raw.replace(";", "|").replace(",", "|")
    return [_text(item) for item in normalized.split("|") if _text(item)]


def _load_export_rows(path: Path) -> list[dict[str, Any]]:
    suffix = path.suffix.lower()
    if suffix == ".csv":
        with path.open("r", encoding="utf-8-sig", newline="") as handle:
            reader = csv.DictReader(handle)
            return [dict(row) for row in reader]
    if suffix == ".json":
        payload = json.loads(path.read_text(encoding="utf-8"))
        if isinstance(payload, list):
            return [dict(row) for row in payload if isinstance(row, Mapping)]
        if isinstance(payload, Mapping):
            for key in ("entries", "results", "rows", "items"):
                value = payload.get(key)
                if isinstance(value, list):
                    return [dict(row) for row in value if isinstance(row, Mapping)]
    raise ValueError(f"unsupported licensed discovery export format: {path}")


_DISCOVERY_FIELD_ALIASES: dict[str, dict[str, list[str]]] = {
    "scopus": {
        "title": ["Title", "Document Title", "title"],
        "doi": ["DOI", "doi"],
        "source_url": ["Link", "Source link", "Scopus link", "URL", "url", "EID link"],
        "journal": ["Source title", "Journal", "Publication Name", "journal"],
        "published_year": ["Year", "Publication Year", "published_year"],
        "abstract": ["Abstract", "abstract", "Summary", "summary"],
        "keywords": ["Author Keywords", "Index Keywords", "Keywords", "keywords"],
        "authors": ["Authors", "Author Names", "authors"],
    },
    "ieee": {
        "title": ["Document Title", "Title", "title"],
        "doi": ["DOI", "doi"],
        "source_url": ["Document Link", "URL", "Link", "Abstract URL", "PDF URL"],
        "journal": ["Publication Title", "Source title", "Journal", "Publication Name"],
        "published_year": ["Publication Year", "Year", "published_year"],
        "abstract": ["Abstract", "Summary", "abstract"],
        "keywords": ["Author Keywords", "Index Terms", "INSPEC Controlled Terms", "Keywords"],
        "authors": ["Authors", "Author Names"],
    },
    "springer": {
        "title": ["Item Title", "Title", "Document Title", "title"],
        "doi": ["Item DOI", "DOI", "doi"],
        "source_url": ["URL", "Link", "Article URL"],
        "journal": ["Publication Title", "Journal", "Source title"],
        "published_year": ["Publication Year", "Year", "published_year"],
        "abstract": ["Abstract", "Summary", "abstract"],
        "keywords": ["Keywords", "Keyword", "Author Keywords"],
        "authors": ["Authors", "Author Names"],
    },
    "elsevier": {
        "title": ["Title", "Document Title", "Article Title", "title"],
        "doi": ["DOI", "doi"],
        "source_url": ["URL", "Link", "Article URL", "Source link"],
        "journal": ["Source title", "Journal", "Publication Name"],
        "published_year": ["Year", "Publication Year", "published_year"],
        "abstract": ["Abstract", "Summary", "abstract"],
        "keywords": ["Keywords", "Author Keywords", "Index Keywords"],
        "authors": ["Authors", "Author Names"],
    },
}


def _normalize_discovery_row(row: Mapping[str, Any], *, provider_key: str) -> dict[str, Any]:
    aliases = dict(_DISCOVERY_FIELD_ALIASES.get(_text(provider_key), _DISCOVERY_FIELD_ALIASES["scopus"]))
    title = _field(row, *list(aliases.get("title", [])))
    doi = _field(row, *list(aliases.get("doi", [])))
    source_url = _field(row, *list(aliases.get("source_url", [])))
    journal = _field(row, *list(aliases.get("journal", [])))
    published_year = _field(row, *list(aliases.get("published_year", [])))
    abstract = _field(row, *list(aliases.get("abstract", [])))
    keywords = _list_field(row, *list(aliases.get("keywords", [])))
    authors = _list_field(row, *list(aliases.get("authors", [])))
    return {
        "title": title,
        "doi": doi,
        "journal": journal,
        "published_year": published_year,
        "abstract": abstract,
        "keywords": keywords,
        "authors": authors,
        "source_url": source_url,
        "raw_row": dict(row),
    }


def _candidate_basename(*, title: str, doi: str, ordinal: int) -> str:
    title_slug = _slug(title) or "licensed-candidate"
    doi_slug = _slug(doi.replace("/", "-")) if doi else ""
    if doi_slug:
        return f"{title_slug}--{doi_slug[:24]}"
    return f"{title_slug}--{ordinal:03d}"


def _priority_score(
    *,
    pattern_count: int,
    combination_count: int,
    has_doi: bool,
    has_abstract: bool,
    keyword_count: int,
) -> int:
    return combination_count * 100 + pattern_count * 10 + (5 if has_doi else 0) + (3 if has_abstract else 0) + min(keyword_count, 5)


def _build_candidate_row(
    *,
    normalized_provider: str,
    normalized: Mapping[str, Any],
    basename: str,
    manifest: Mapping[str, Any],
    candidate_bundle: Mapping[str, Any],
    extraction_payload: Mapping[str, Any],
    row_pattern_promotions: list[dict[str, Any]],
    row_combination_promotions: list[dict[str, Any]],
) -> dict[str, Any]:
    return {
        "candidate_id": basename,
        "expected_pdf_name": f"{basename}.pdf",
        "title": _text(normalized.get("title")),
        "doi": _text(normalized.get("doi")),
        "journal": _text(normalized.get("journal")),
        "published_year": _text(normalized.get("published_year")),
        "authors": list(normalized.get("authors", []) or []),
        "keywords": list(normalized.get("keywords", []) or []),
        "source_url": _text(normalized.get("source_url")),
        "manifest": dict(manifest or {}),
        "metadata_payload": {
            "provider_key": normalized_provider,
            "title": _text(normalized.get("title")),
            "doi": _text(normalized.get("doi")),
            "journal": _text(normalized.get("journal")),
            "published_year": _text(normalized.get("published_year")),
            "authors": list(normalized.get("authors", []) or []),
            "source_url": _text(normalized.get("source_url")),
            "abstract": _text(normalized.get("abstract")),
            "keywords": list(normalized.get("keywords", []) or []),
            "notes": (
                f"Auto-generated from {normalized_provider} discovery export. "
                "Place the downloaded PDF with the expected filename in inbox/."
            ),
        },
        "extraction_payload": dict(extraction_payload or {}),
        "matched_pattern_ids": list(candidate_bundle.get("matched_pattern_ids", []) or []),
        "matched_combination_ids": list(candidate_bundle.get("matched_combination_ids", []) or []),
        "pattern_promotion_count": len(row_pattern_promotions),
        "combination_promotion_count": len(row_combination_promotions),
        "priority_score": _priority_score(
            pattern_count=len(row_pattern_promotions),
            combination_count=len(row_combination_promotions),
            has_doi=bool(_text(normalized.get("doi"))),
            has_abstract=bool(_text(normalized.get("abstract"))),
            keyword_count=len(list(normalized.get("keywords", []) or [])),
        ),
    }


def _build_metadata_only_manifest(
    *,
    provider_key: str,
    normalized_row: Mapping[str, Any],
    retrieval_purpose: str,
) -> dict[str, Any]:
    source_url = _text(normalized_row.get("source_url")) or default_provider_launch_url(provider_key) or "https://www.scopus.com/"
    provider_plan = build_provider_session_plan(
        url=source_url,
        retrieval_purpose=retrieval_purpose,
        provider_key_override=provider_key,
    )
    acquisition_result = {
        "status": "search_result_metadata_only",
        "error": "",
        "requested_url": source_url,
        "final_url": source_url,
        "html": "",
        "visible_text": "\n".join(
            [
                _text(normalized_row.get("title")),
                _text(normalized_row.get("abstract")),
                " | ".join(list(normalized_row.get("keywords", []) or [])),
            ]
        ).strip(),
        "selector_lineage": [],
        "acquisition_mode": "scopus_discovery_export",
    }
    return build_research_document_manifest(
        provider_session_plan=provider_plan,
        acquisition_result=acquisition_result,
        metadata={
            "title": _text(normalized_row.get("title")),
            "doi": _text(normalized_row.get("doi")),
            "journal": _text(normalized_row.get("journal")),
            "published_year": _text(normalized_row.get("published_year")),
            "authors": list(normalized_row.get("authors", []) or []),
        },
        local_artifact_path="",
    )


def build_scopus_discovery_candidate_queue(
    *,
    export_path: str,
    provider_key: str = "scopus",
    registry_bundle: Mapping[str, Any] | None,
    top_k: int = 25,
    retrieval_purpose: str = "pattern_seed_discovery",
    source_basis_id: str = "licensed_research_public_technical_priors",
) -> dict[str, Any]:
    path = Path(str(export_path)).expanduser()
    if not path.exists() or not path.is_file():
        raise FileNotFoundError(f"Scopus export not found: {path}")

    rows = _load_export_rows(path)
    candidate_rows: list[dict[str, Any]] = []
    all_extraction_records: list[dict[str, Any]] = []
    pattern_promotions: list[dict[str, Any]] = []
    combination_promotions: list[dict[str, Any]] = []
    normalized_provider = _text(provider_key) or "scopus"

    for ordinal, raw_row in enumerate(rows, start=1):
        normalized = _normalize_discovery_row(raw_row, provider_key=normalized_provider)
        if not _text(normalized.get("title")):
            continue
        basename = _candidate_basename(
            title=_text(normalized.get("title")),
            doi=_text(normalized.get("doi")),
            ordinal=ordinal,
        )
        manifest = _build_metadata_only_manifest(
            provider_key=normalized_provider,
            normalized_row=normalized,
            retrieval_purpose=retrieval_purpose,
        )
        candidate_bundle = build_structured_prior_candidates_from_text(
            document_slug=basename,
            title=_text(normalized.get("title")),
            abstract=_text(normalized.get("abstract")),
            keywords=list(normalized.get("keywords", []) or []),
            source_locator_prefix=f"{normalized_provider}_discovery_export::{path.name}::{basename}",
            registry_bundle=registry_bundle,
        )
        extraction_payload = dict(
            build_extraction_seed_from_manifest(
                research_document_manifest=manifest,
                source_basis_id=source_basis_id,
                retrieval_purpose=retrieval_purpose,
            )
        )
        extraction_payload.update(
            {
                "id": f"extract::{normalized_provider}_discovery::{basename}",
                "document_ref": _text(normalized.get("doi")) or _text(normalized.get("source_url")) or basename,
                "review_status": "auto_draft",
                "notes": (
                    f"Auto-draft generated from {normalized_provider} discovery metadata only. "
                    "Use this to prioritize PDF acquisition and review combinations before full text."
                ),
                "knowledge_atoms": list(candidate_bundle.get("knowledge_atoms", []) or []),
                "pattern_candidate_records": list(candidate_bundle.get("pattern_candidate_records", []) or []),
                "combination_candidate_records": list(candidate_bundle.get("combination_candidate_records", []) or []),
            }
        )
        extraction_record = build_knowledge_extraction_record(
            research_document_manifest=manifest,
            extraction_payload=extraction_payload,
            registry_bundle=dict(registry_bundle or {}),
        )
        promotions = build_extraction_promotion_registers(
            [extraction_record],
            registry_bundle=dict(registry_bundle or {}),
        )
        row_pattern_promotions = list(promotions.get("approved_pattern_promotion_register", []) or [])
        row_combination_promotions = list(promotions.get("approved_combination_promotion_register", []) or [])
        pattern_promotions.extend(row_pattern_promotions)
        combination_promotions.extend(row_combination_promotions)
        all_extraction_records.append(extraction_record)

        candidate_rows.append(
            _build_candidate_row(
                normalized_provider=normalized_provider,
                normalized=normalized,
                basename=basename,
                manifest=manifest,
                candidate_bundle=candidate_bundle,
                extraction_payload=extraction_payload,
                row_pattern_promotions=row_pattern_promotions,
                row_combination_promotions=row_combination_promotions,
            )
        )

    candidate_rows.sort(key=lambda row: (-int(row.get("priority_score", 0) or 0), _text(row.get("title"))))
    if top_k > 0:
        candidate_rows = candidate_rows[:top_k]
    selected_ids = {_text(row.get("candidate_id")) for row in candidate_rows}
    filtered_extractions = [
        row for row in all_extraction_records
        if _slug(_text(row.get("id")).split(f"extract::{normalized_provider}_discovery::", 1)[-1]) in selected_ids
    ]
    filtered_pattern_promotions = [
        row for row in pattern_promotions
        if any(selected in _text(row.get("promotion_id")) for selected in selected_ids)
    ]
    filtered_combination_promotions = [
        row for row in combination_promotions
        if any(selected in _text(row.get("promotion_id")) for selected in selected_ids)
    ]
    return {
        "generated_at": _utc_now_iso(),
        "provider_key": normalized_provider,
        "export_path": str(path),
        "retrieval_purpose": retrieval_purpose,
        "candidate_rows": candidate_rows,
        "extraction_review_register": build_extraction_review_register(filtered_extractions),
        "approved_pattern_promotion_register": filtered_pattern_promotions,
        "approved_combination_promotion_register": filtered_combination_promotions,
        "summary": {
            "export_row_count": len(rows),
            "candidate_count": len(candidate_rows),
            "pattern_promotion_count": len(filtered_pattern_promotions),
            "combination_promotion_count": len(filtered_combination_promotions),
        },
    }


def materialize_scopus_discovery_candidate_queue(
    *,
    export_path: str,
    intake_dir: str,
    provider_key: str = "scopus",
    registry_bundle: Mapping[str, Any] | None,
    top_k: int = 25,
    retrieval_purpose: str = "pattern_seed_discovery",
    source_basis_id: str = "licensed_research_public_technical_priors",
) -> dict[str, Any]:
    queue = build_scopus_discovery_candidate_queue(
        export_path=export_path,
        provider_key=provider_key,
        registry_bundle=registry_bundle,
        top_k=top_k,
        retrieval_purpose=retrieval_purpose,
        source_basis_id=source_basis_id,
    )
    root = Path(str(intake_dir)).expanduser()
    inbox_dir = root / "inbox"
    discovery_dir = root / "discovery_queue"
    inbox_dir.mkdir(parents=True, exist_ok=True)
    discovery_dir.mkdir(parents=True, exist_ok=True)

    materialized_rows: list[dict[str, Any]] = []
    for row in list(queue.get("candidate_rows", []) or []):
        basename = _text(row.get("candidate_id")) or "scopus-candidate"
        metadata_path = inbox_dir / f"{basename}.metadata.json"
        extraction_path = inbox_dir / f"{basename}.extraction.json"
        candidate_path = discovery_dir / f"{basename}.candidate.json"

        if not metadata_path.exists():
            metadata_path.write_text(
                json.dumps(dict(row.get("metadata_payload", {}) or {}), indent=2, sort_keys=True),
                encoding="utf-8",
            )
        if not extraction_path.exists():
            extraction_path.write_text(
                json.dumps(dict(row.get("extraction_payload", {}) or {}), indent=2, sort_keys=True),
                encoding="utf-8",
            )
        candidate_path.write_text(json.dumps(dict(row), indent=2, sort_keys=True), encoding="utf-8")

        materialized_rows.append(
            {
                "candidate_id": basename,
                "expected_pdf_name": _text(row.get("expected_pdf_name")),
                "metadata_path": str(metadata_path),
                "extraction_path": str(extraction_path),
                "candidate_path": str(candidate_path),
                "priority_score": int(row.get("priority_score", 0) or 0),
            }
        )

    manifest = {
        **queue,
        "intake_dir": str(root),
        "materialized_rows": materialized_rows,
    }
    manifest_path = discovery_dir / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True), encoding="utf-8")
    manifest["manifest_path"] = str(manifest_path)
    return manifest


def build_licensed_discovery_candidate_queue(
    *,
    export_path: str,
    provider_key: str,
    registry_bundle: Mapping[str, Any] | None,
    top_k: int = 25,
    retrieval_purpose: str = "pattern_seed_discovery",
    source_basis_id: str = "licensed_research_public_technical_priors",
) -> dict[str, Any]:
    return build_scopus_discovery_candidate_queue(
        export_path=export_path,
        provider_key=provider_key,
        registry_bundle=registry_bundle,
        top_k=top_k,
        retrieval_purpose=retrieval_purpose,
        source_basis_id=source_basis_id,
    )


def materialize_licensed_discovery_candidate_queue(
    *,
    export_path: str,
    intake_dir: str,
    provider_key: str,
    registry_bundle: Mapping[str, Any] | None,
    top_k: int = 25,
    retrieval_purpose: str = "pattern_seed_discovery",
    source_basis_id: str = "licensed_research_public_technical_priors",
) -> dict[str, Any]:
    return materialize_scopus_discovery_candidate_queue(
        export_path=export_path,
        intake_dir=intake_dir,
        provider_key=provider_key,
        registry_bundle=registry_bundle,
        top_k=top_k,
        retrieval_purpose=retrieval_purpose,
        source_basis_id=source_basis_id,
    )


def rebuild_licensed_discovery_candidate_row(
    *,
    candidate_row: Mapping[str, Any],
    registry_bundle: Mapping[str, Any] | None,
    retrieval_purpose: str = "pattern_seed_discovery",
    source_basis_id: str = "licensed_research_public_technical_priors",
) -> dict[str, Any]:
    row = dict(candidate_row or {})
    metadata_payload = dict(row.get("metadata_payload", {}) or {})
    provider_key = _text(metadata_payload.get("provider_key")) or _text(row.get("provider_key")) or "scopus"
    basename = _text(row.get("candidate_id")) or _candidate_basename(
        title=_text(metadata_payload.get("title")),
        doi=_text(metadata_payload.get("doi")),
        ordinal=1,
    )
    normalized = {
        "title": _text(metadata_payload.get("title")) or _text(row.get("title")),
        "doi": _text(metadata_payload.get("doi")) or _text(row.get("doi")),
        "journal": _text(metadata_payload.get("journal")) or _text(row.get("journal")),
        "published_year": _text(metadata_payload.get("published_year")) or _text(row.get("published_year")),
        "authors": list(metadata_payload.get("authors", []) or row.get("authors", []) or []),
        "keywords": list(metadata_payload.get("keywords", []) or row.get("keywords", []) or []),
        "abstract": _text(metadata_payload.get("abstract")),
        "source_url": _text(metadata_payload.get("source_url")) or _text(row.get("source_url")),
    }
    manifest = _build_metadata_only_manifest(
        provider_key=provider_key,
        normalized_row=normalized,
        retrieval_purpose=retrieval_purpose,
    )
    candidate_bundle = build_structured_prior_candidates_from_text(
        document_slug=basename,
        title=_text(normalized.get("title")),
        abstract=_text(normalized.get("abstract")),
        keywords=list(normalized.get("keywords", []) or []),
        notes=_text(metadata_payload.get("notes")),
        source_locator_prefix=f"{provider_key}_discovery_edit::{basename}",
        registry_bundle=registry_bundle,
    )
    extraction_payload = dict(
        build_extraction_seed_from_manifest(
            research_document_manifest=manifest,
            source_basis_id=source_basis_id,
            retrieval_purpose=retrieval_purpose,
        )
    )
    extraction_payload.update(
        {
            "id": f"extract::{provider_key}_discovery::{basename}",
            "provider_key": provider_key,
            "document_title": _text(normalized.get("title")),
            "document_ref": _text(normalized.get("doi")) or _text(normalized.get("source_url")) or basename,
            "review_status": "auto_draft",
            "notes": (
                _text(metadata_payload.get("notes"))
                or f"Edited {provider_key} discovery candidate. Keep all claims at L2 until full-text or case evidence exists."
            ),
            "knowledge_atoms": list(candidate_bundle.get("knowledge_atoms", []) or []),
            "pattern_candidate_records": list(candidate_bundle.get("pattern_candidate_records", []) or []),
            "combination_candidate_records": list(candidate_bundle.get("combination_candidate_records", []) or []),
        }
    )
    extraction_record = build_knowledge_extraction_record(
        research_document_manifest=manifest,
        extraction_payload=extraction_payload,
        registry_bundle=dict(registry_bundle or {}),
    )
    promotions = build_extraction_promotion_registers(
        [extraction_record],
        registry_bundle=dict(registry_bundle or {}),
    )
    row_pattern_promotions = list(promotions.get("approved_pattern_promotion_register", []) or [])
    row_combination_promotions = list(promotions.get("approved_combination_promotion_register", []) or [])
    rebuilt = _build_candidate_row(
        normalized_provider=provider_key,
        normalized=normalized,
        basename=basename,
        manifest=manifest,
        candidate_bundle=candidate_bundle,
        extraction_payload=extraction_payload,
        row_pattern_promotions=row_pattern_promotions,
        row_combination_promotions=row_combination_promotions,
    )
    rebuilt["metadata_payload"]["notes"] = _text(metadata_payload.get("notes")) or rebuilt["metadata_payload"].get("notes", "")
    return rebuilt
