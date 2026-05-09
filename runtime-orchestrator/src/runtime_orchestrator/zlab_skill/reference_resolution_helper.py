from __future__ import annotations

from typing import Any, Mapping


def _text(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, str):
        return value.strip()
    return str(value).strip()


def _extract_sentence_value(notes: str, label: str) -> str:
    normalized_notes = _text(notes)
    prefix = f"{label}:"
    if prefix not in normalized_notes:
        return ""
    tail = normalized_notes.split(prefix, 1)[1].strip()
    return _text(tail.split(".", 1)[0])


def _extract_csv_values(notes: str, label: str) -> list[str]:
    raw = _extract_sentence_value(notes, label)
    if not raw:
        return []
    return [_text(item) for item in raw.split(",") if _text(item)]


def _default_search_surface(provider_key: str) -> str:
    provider = _text(provider_key)
    if provider == "scopus":
        return "TITLE-ABS-KEY"
    if provider == "ieee":
        return "IEEE metadata + abstract + index terms"
    if provider == "springer":
        return "Springer title + abstract + chapter/book metadata"
    if provider == "elsevier":
        return "Elsevier metadata + abstract + visible reference text"
    return ""


def parse_query_seed_notes(notes: Any) -> dict[str, Any]:
    normalized_notes = _text(notes)
    combination_id = ""
    combination_prefix = "Query-seed candidate for combination "
    if combination_prefix in normalized_notes:
        combination_tail = normalized_notes.split(combination_prefix, 1)[1]
        combination_id = _text(combination_tail.split(".", 1)[0])
    return {
        "combination_id": combination_id,
        "query_family": _extract_sentence_value(normalized_notes, "Query family"),
        "primary_query": _extract_sentence_value(normalized_notes, "Primary query"),
        "pivot_query": _extract_sentence_value(normalized_notes, "Pivot query"),
        "search_intent": _extract_sentence_value(normalized_notes, "Search intent"),
        "evidence_targets": _extract_csv_values(normalized_notes, "Evidence targets"),
    }


def build_reference_resolution_prefill(
    *,
    candidate_row: Mapping[str, Any] | None,
    reference_record: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    candidate = dict(candidate_row or {})
    reference = dict(reference_record or {})
    metadata = dict(candidate.get("metadata_payload", {}) or {})
    acquisition_result = dict(reference.get("acquisition_result", {}) or {})
    parsed_notes = parse_query_seed_notes(metadata.get("notes"))
    provider_key = _text(metadata.get("provider_key")) or _text(reference.get("provider_key")) or _text(candidate.get("provider_key"))
    provider_display_name = _text(metadata.get("provider_display_name")) or provider_key.replace("_", " ").title()
    title = _text(metadata.get("title")) or _text(candidate.get("title"))
    source_url = (
        _text(reference.get("source_url"))
        or _text(acquisition_result.get("final_url"))
        or _text(acquisition_result.get("requested_url"))
        or _text(metadata.get("source_url"))
        or _text(candidate.get("source_url"))
    )
    launch_url = _text(metadata.get("launch_url")) or source_url
    query_family = _text(metadata.get("query_family")) or _text(parsed_notes.get("query_family"))
    primary_query = _text(metadata.get("primary_query")) or _text(parsed_notes.get("primary_query"))
    pivot_query = _text(metadata.get("pivot_query")) or _text(parsed_notes.get("pivot_query"))
    search_intent = _text(metadata.get("search_intent")) or _text(parsed_notes.get("search_intent")) or _text(metadata.get("abstract")) or _text(candidate.get("abstract"))
    search_surface = _text(metadata.get("search_surface")) or _default_search_surface(provider_key)
    execution_hint = _text(metadata.get("execution_hint"))
    if not execution_hint and provider_display_name and search_surface and query_family:
        execution_hint = (
            f"Start with {provider_display_name} using {search_surface.lower()} "
            f"to pursue {query_family.replace('_', ' ')}."
        )
    captured_result_title = _text(acquisition_result.get("search_result_title"))
    captured_result_snippet = _text(acquisition_result.get("search_result_snippet"))
    evidence_targets = [
        _text(item)
        for item in list(metadata.get("evidence_targets", []) or parsed_notes.get("evidence_targets", []) or [])
        if _text(item)
    ]
    suggested_notes = " | ".join(
        part
        for part in [
            f"Provider: {provider_key}" if provider_key else "",
            f"Query family: {query_family}" if query_family else "",
            f"Primary query: {primary_query}" if primary_query else "",
            f"Evidence targets: {', '.join(evidence_targets)}" if evidence_targets else "",
        ]
        if _text(part)
    )
    return {
        "candidate_id": _text(candidate.get("candidate_id")),
        "provider_key": provider_key,
        "provider_display_name": provider_display_name,
        "title": title,
        "doi": _text(metadata.get("doi")) or _text(candidate.get("doi")),
        "journal": _text(metadata.get("journal")) or _text(candidate.get("journal")),
        "published_year": _text(metadata.get("published_year")) or _text(candidate.get("published_year")),
        "source_url": source_url,
        "launch_url": launch_url,
        "search_surface": search_surface,
        "execution_hint": execution_hint,
        "search_brief": _text(acquisition_result.get("search_brief")),
        "captured_result_title": captured_result_title,
        "captured_result_snippet": captured_result_snippet,
        "query_family": query_family,
        "primary_query": primary_query,
        "pivot_query": pivot_query,
        "search_intent": search_intent,
        "evidence_targets": evidence_targets,
        "keywords": [_text(item) for item in list(metadata.get("keywords", []) or candidate.get("keywords", []) or []) if _text(item)],
        "suggested_notes": suggested_notes,
        "accept_for_reference_use_recommended": True,
    }
