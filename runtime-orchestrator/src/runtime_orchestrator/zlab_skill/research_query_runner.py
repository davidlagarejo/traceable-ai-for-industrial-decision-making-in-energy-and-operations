from __future__ import annotations

import json
from typing import Any, Mapping

from .reference_resolution_helper import build_reference_resolution_prefill, parse_query_seed_notes


def _text(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, str):
        return value.strip()
    return str(value).strip()


def _source_family(provider_key: str) -> str:
    normalized_provider = _text(provider_key)
    if normalized_provider == "scopus":
        return "licensed_research_discovery"
    if normalized_provider in {"ieee", "springer", "elsevier"}:
        return "licensed_research_fulltext"
    return "public_technical_guidance"


def _reference_by_candidate_id(
    article_reference_register: list[dict[str, Any]] | None,
) -> dict[str, dict[str, Any]]:
    return {
        _text(row.get("candidate_id")): dict(row)
        for row in list(article_reference_register or [])
        if _text(row.get("candidate_id"))
    }


def _is_query_seed_candidate(candidate_row: Mapping[str, Any] | None) -> bool:
    row = dict(candidate_row or {})
    return _text(row.get("candidate_id")).startswith("queryseed-")


def _capture_state_for_row(
    *,
    reference_state: str,
    acquisition_result: Mapping[str, Any] | None,
) -> tuple[str, str, str]:
    acquisition = dict(acquisition_result or {})
    has_captured_result = bool(
        _text(acquisition.get("search_result_title"))
        or _text(acquisition.get("search_result_snippet"))
        or _text(acquisition.get("status")) == "query_seed_result_captured"
    )
    if reference_state in {"manual_text_enriched", "visible_text_enriched"}:
        return "excerpt_resolved", "NO_CAPTURE_REQUIRED", "closed"
    if reference_state == "query_seed_draft" and has_captured_result:
        return "result_captured", "RESOLVE_REFERENCE_EXCERPT", "pending"
    if reference_state == "query_seed_draft":
        return "seed_only", "CAPTURE_SEARCH_RESULT", "pending"
    if reference_state in {"metadata_only", ""}:
        return "needs_draft", "READ_OR_DRAFT_REFERENCE", "pending"
    return "outside_capture_lane", "NO_CAPTURE_REQUIRED", "closed"


def _join_nonempty(parts: list[str], *, sep: str = " | ") -> str:
    return sep.join(part for part in parts if _text(part))


def _query_variants(row: Mapping[str, Any] | None) -> list[str]:
    data = dict(row or {})
    variants: list[str] = []
    for item in [
        _text(data.get("primary_query")),
        _text(data.get("pivot_query")),
        _text(data.get("search_intent")),
    ]:
        if item and item not in variants:
            variants.append(item)
    primary_query = _text(data.get("primary_query"))
    evidence_targets = [_text(item) for item in list(data.get("evidence_targets", []) or []) if _text(item)]
    if primary_query and evidence_targets:
        narrowed = f"{primary_query} {' '.join(evidence_targets[:2])}".strip()
        if narrowed and narrowed not in variants:
            variants.append(narrowed)
    return variants[:3]


def _provider_search_execution_guide(
    *,
    provider_key: str,
    source_family: str,
    query_family: str,
) -> dict[str, Any]:
    provider = _text(provider_key).lower()
    family = _text(source_family)
    query = _text(query_family)
    if provider == "scopus":
        return {
            "provider_key": provider,
            "source_family": family,
            "query_family": query,
            "preferred_surface": "TITLE-ABS-KEY",
            "preferred_fields": ["Primary query", "Pivot query", "Evidence targets"],
            "search_tips": [
                "Start broad with Primary query.",
                "Use Pivot query only if the first pass is noisy.",
                "Capture visible result title, link, abstract, source, and year.",
            ],
            "result_capture_goal": "Collect discovery-visible rows that can be pasted as Title/Link/Abstract/Source/Year.",
        }
    if provider == "ieee":
        return {
            "provider_key": provider,
            "source_family": family,
            "query_family": query,
            "preferred_surface": "Metadata + abstract + index terms",
            "preferred_fields": ["Primary query", "Pivot query", "Index Terms"],
            "search_tips": [
                "Start with Document Title / metadata results.",
                "If no abstract is visible, capture Index Terms as visible-text context.",
                "Preserve publication year when available.",
            ],
            "result_capture_goal": "Collect visible rows with Document Title, Document Link, Abstract or Index Terms, and Publication Year.",
        }
    if provider in {"springer", "elsevier"}:
        return {
            "provider_key": provider,
            "source_family": family,
            "query_family": query,
            "preferred_surface": "Title / abstract / journal metadata",
            "preferred_fields": ["Primary query", "Pivot query", "Journal"],
            "search_tips": [
                "Keep title and abstract together when capturing visible results.",
                "Preserve journal and year in notes if they are visible.",
            ],
            "result_capture_goal": "Collect visible rows with Title, URL, Abstract, Journal, and Year.",
        }
    return {
        "provider_key": provider or "generic",
        "source_family": family,
        "query_family": query,
        "preferred_surface": "Visible provider search results",
        "preferred_fields": ["Primary query", "Pivot query", "Snippet"],
        "search_tips": [
            "Use the primary query first.",
            "Capture URL, title, and any visible text snippet.",
        ],
        "result_capture_goal": "Collect visible rows with URL, Title, and Snippet.",
    }


def _search_packet_template(row: Mapping[str, Any] | None) -> str:
    data = dict(row or {})
    query_variants = list(data.get("query_variants", []) or [])
    provider_guide = _provider_search_execution_guide(
        provider_key=_text(data.get("provider_key")),
        source_family=_text(data.get("source_family")),
        query_family=_text(data.get("query_family")),
    )
    lines = [
        f"# Provider: {_text(data.get('provider_display_name')) or _text(data.get('provider_key')) or 'unknown'}",
        f"# Source family: {_text(data.get('source_family')) or 'unknown'}",
        f"# Query family: {_text(data.get('query_family')) or 'unknown'}",
        f"# Launch URL: {_text(data.get('launch_url')) or _text(data.get('source_url'))}",
        f"# Search surface: {_text(data.get('search_surface')) or _text(provider_guide.get('preferred_surface'))}",
        f"# Execution hint: {_text(data.get('execution_hint'))}",
        f"# Result capture goal: {_text(provider_guide.get('result_capture_goal'))}",
        (
            f"# Evidence targets: {', '.join(list(data.get('evidence_targets', []) or []))}"
            if list(data.get("evidence_targets", []) or [])
            else ""
        ),
        (
            f"# Search brief: {_text(data.get('search_brief'))}"
            if _text(data.get("search_brief"))
            else ""
        ),
        "Primary query:",
        _text(data.get("primary_query")),
        "",
        "Pivot query:",
        _text(data.get("pivot_query")),
        "",
        "Alternate query:",
        query_variants[2] if len(query_variants) >= 3 else "",
        "",
        "Result goal:",
        "Capture article URL + title + visible search-result snippet. Do not treat snippet as evidence.",
    ]
    return "\n".join(lines)


def _provider_search_execution_sheet_template(
    rows: list[dict[str, Any]],
    *,
    provider_key: str,
    source_family: str,
    query_family: str,
) -> str:
    guide = _provider_search_execution_guide(
        provider_key=provider_key,
        source_family=source_family,
        query_family=query_family,
    )
    lines: list[str] = [
        f"# Provider search sheet · {provider_key or 'provider'} · {query_family or 'query_family'}",
        f"# Preferred surface: {_text(guide.get('preferred_surface'))}",
        f"# Result capture goal: {_text(guide.get('result_capture_goal'))}",
    ]
    tips = [_text(item) for item in list(guide.get("search_tips", []) or []) if _text(item)]
    if tips:
        lines.append(f"# Search tips: {' | '.join(tips)}")
    fields = [_text(item) for item in list(guide.get("preferred_fields", []) or []) if _text(item)]
    if fields:
        lines.append(f"# Preferred fields: {' | '.join(fields)}")
    for index, row in enumerate(rows, start=1):
        query_variants = list(row.get("query_variants", []) or [])
        lines.extend(
            [
                "",
                f"# Row {index} · Candidate: {_text(row.get('candidate_id'))}",
                f"# Query seed title: {_text(row.get('title')) or _text(row.get('candidate_id')) or 'unknown'}",
                f"# Launch URL: {_text(row.get('launch_url')) or _text(row.get('source_url'))}",
                f"# Search line 1: {_text(query_variants[0]) if len(query_variants) >= 1 else _text(row.get('primary_query'))}",
                f"# Search line 2: {_text(query_variants[1]) if len(query_variants) >= 2 else _text(row.get('pivot_query'))}",
                f"# Search line 3: {_text(query_variants[2]) if len(query_variants) >= 3 else ''}",
                f"# Evidence targets: {', '.join(_text(item) for item in list(row.get('evidence_targets', []) or []) if _text(item)) or 'none declared'}",
            ]
    )
    return "\n".join(lines).rstrip()


def _provider_search_execution_capture_workbook_template(
    rows: list[dict[str, Any]],
    *,
    provider_key: str,
    source_family: str,
    query_family: str,
) -> str:
    guide = _provider_search_execution_guide(
        provider_key=provider_key,
        source_family=source_family,
        query_family=query_family,
    )
    lines: list[str] = [
        f"# Provider search workbook · {provider_key or 'provider'} · {query_family or 'query_family'}",
        f"# Preferred surface: {_text(guide.get('preferred_surface'))}",
        f"# Result capture goal: {_text(guide.get('result_capture_goal'))}",
    ]
    tips = [_text(item) for item in list(guide.get("search_tips", []) or []) if _text(item)]
    if tips:
        lines.append(f"# Search tips: {' | '.join(tips)}")
    for index, row in enumerate(rows, start=1):
        query_variants = list(row.get("query_variants", []) or [])
        lines.extend(
            [
                "---" if index > 1 else "",
                f"# Row {index} · Candidate: {_text(row.get('candidate_id'))}",
                f"# Query seed title: {_text(row.get('title')) or _text(row.get('candidate_id')) or 'unknown'}",
                f"# Launch URL: {_text(row.get('launch_url')) or _text(row.get('source_url'))}",
                f"# Search line 1: {_text(query_variants[0]) if len(query_variants) >= 1 else _text(row.get('primary_query'))}",
                f"# Search line 2: {_text(query_variants[1]) if len(query_variants) >= 2 else _text(row.get('pivot_query'))}",
                f"# Search line 3: {_text(query_variants[2]) if len(query_variants) >= 3 else ''}",
                f"# Evidence targets: {', '.join(_text(item) for item in list(row.get('evidence_targets', []) or []) if _text(item)) or 'none declared'}",
                "Candidate ID: " + _text(row.get("candidate_id")),
                "URL: " + _text((row.get("top_imported_result", {}) or {}).get("source_url")),
                "Title: " + _text((row.get("top_imported_result", {}) or {}).get("search_result_title")),
                "Snippet: " + _text((row.get("top_imported_result", {}) or {}).get("search_result_snippet")),
                "Selected: ",
                "Excerpt: ",
                "Notes: ",
            ]
        )
    return "\n".join(line for line in lines if line != "").rstrip()


def _capture_packet_template(row: Mapping[str, Any] | None) -> str:
    data = dict(row or {})
    lines = [
        f"# Candidate ID: {_text(data.get('candidate_id'))}",
        f"# Provider: {_text(data.get('provider_display_name')) or _text(data.get('provider_key')) or 'unknown'}",
        f"# Query family: {_text(data.get('query_family')) or 'unknown'}",
        f"# Primary query: {_text(data.get('primary_query'))}",
        f"# Pivot query: {_text(data.get('pivot_query'))}",
        "URL: " + (_text(data.get("source_url")) if _text(data.get("capture_state")) == "result_captured" else ""),
        "Title: " + _text(data.get("captured_result_title")),
        "Snippet: " + _text(data.get("captured_result_snippet")),
    ]
    return "\n".join(lines)


def _structured_result_import_json_template(rows: list[dict[str, Any]]) -> str:
    payload = [
        {
            "candidate_id": _text(row.get("candidate_id")),
            "rank": 1,
            "source_url": _text((row.get("top_imported_result", {}) or {}).get("source_url")),
            "search_result_title": _text((row.get("top_imported_result", {}) or {}).get("search_result_title")),
            "search_result_snippet": _text((row.get("top_imported_result", {}) or {}).get("search_result_snippet")),
            "selected": False,
            "reference_excerpt": "",
            "notes": "",
        }
        for row in rows
    ]
    return json.dumps(payload, indent=2, ensure_ascii=True)


def _structured_ordered_result_import_json_template(rows: list[dict[str, Any]]) -> str:
    payload = [
        {
            "source_url": _text((row.get("top_imported_result", {}) or {}).get("source_url")),
            "search_result_title": _text((row.get("top_imported_result", {}) or {}).get("search_result_title")),
            "search_result_snippet": _text((row.get("top_imported_result", {}) or {}).get("search_result_snippet")),
            "selected": False,
            "reference_excerpt": "",
            "notes": "",
        }
        for row in rows
    ]
    return json.dumps(payload, indent=2, ensure_ascii=True)


def _ordered_result_import_packet_template(rows: list[dict[str, Any]]) -> str:
    blocks: list[str] = []
    for row in rows:
        blocks.append(
            "\n".join(
                [
                    f"# Provider: {_text(row.get('provider_display_name')) or _text(row.get('provider_key')) or 'unknown'}",
                    f"# Query family: {_text(row.get('query_family')) or 'unknown'}",
                    f"# Launch URL: {_text(row.get('launch_url'))}",
                    f"# Primary query: {_text(row.get('primary_query'))}",
                    "URL: " + _text((row.get("top_imported_result", {}) or {}).get("source_url")),
                    "Title: " + _text((row.get("top_imported_result", {}) or {}).get("search_result_title")),
                    "Snippet: " + _text((row.get("top_imported_result", {}) or {}).get("search_result_snippet")),
                    "Selected: ",
                    "Excerpt: ",
                    "Notes: ",
                ]
            )
        )
    return "\n---\n".join(blocks)


def _ordered_result_import_compact_template(rows: list[dict[str, Any]]) -> str:
    lines = [
        "# URL | Title | Snippet | Excerpt | Selected | Notes",
    ]
    for row in rows:
        lines.append(
            " | ".join(
                [
                    _text((row.get("top_imported_result", {}) or {}).get("source_url")),
                    _text((row.get("top_imported_result", {}) or {}).get("search_result_title")),
                    _text((row.get("top_imported_result", {}) or {}).get("search_result_snippet")),
                    "",
                    "",
                    "",
                ]
            )
        )
    return "\n".join(lines)


def _ordered_result_import_tsv_template(rows: list[dict[str, Any]]) -> str:
    lines = [
        "# URL<TAB>Title<TAB>Snippet<TAB>Excerpt<TAB>Selected<TAB>Notes",
    ]
    for row in rows:
        lines.append(
            "\t".join(
                [
                    _text((row.get("top_imported_result", {}) or {}).get("source_url")),
                    _text((row.get("top_imported_result", {}) or {}).get("search_result_title")),
                    _text((row.get("top_imported_result", {}) or {}).get("search_result_snippet")),
                    "",
                    "",
                    "",
                ]
            )
        )
    return "\n".join(lines)


def _provider_ordered_result_import_tsv_template(
    rows: list[dict[str, Any]],
    *,
    provider_key: str,
    query_family: str,
) -> str:
    provider = _text(provider_key).lower()
    query = _text(query_family).lower()
    if provider == "scopus":
        headers = [
            "# Title<TAB>Link<TAB>Abstract<TAB>Source<TAB>Year<TAB>Selected<TAB>Notes",
        ]
        lines = list(headers)
        for row in rows:
            top = dict(row.get("top_imported_result", {}) or {})
            lines.append(
                "\t".join(
                    [
                        _text(top.get("search_result_title")),
                        _text(top.get("source_url")),
                        _text(top.get("search_result_snippet")),
                        "",
                        "",
                        "",
                        f"Query family: {query}" if query else "",
                    ]
                )
            )
        return "\n".join(lines)
    if provider == "ieee":
        headers = [
            "# Document Title<TAB>Document Link<TAB>Abstract<TAB>Publication Year<TAB>Index Terms<TAB>Selected<TAB>Notes",
        ]
        lines = list(headers)
        for row in rows:
            top = dict(row.get("top_imported_result", {}) or {})
            lines.append(
                "\t".join(
                    [
                        _text(top.get("search_result_title")),
                        _text(top.get("source_url")),
                        _text(top.get("search_result_snippet")),
                        "",
                        "",
                        "",
                        f"Query family: {query}" if query else "",
                    ]
                )
            )
        return "\n".join(lines)
    if provider in {"springer", "elsevier"}:
        headers = [
            "# Title<TAB>URL<TAB>Abstract<TAB>Journal<TAB>Year<TAB>Selected<TAB>Notes",
        ]
        lines = list(headers)
        for row in rows:
            top = dict(row.get("top_imported_result", {}) or {})
            lines.append(
                "\t".join(
                    [
                        _text(top.get("search_result_title")),
                        _text(top.get("source_url")),
                        _text(top.get("search_result_snippet")),
                        "",
                        "",
                        "",
                        f"Query family: {query}" if query else "",
                    ]
                )
            )
        return "\n".join(lines)
    return _ordered_result_import_tsv_template(rows)


def _provider_ordered_result_import_capture_guide(
    *,
    provider_key: str,
    query_family: str,
) -> dict[str, Any]:
    provider = _text(provider_key).lower()
    query = _text(query_family)
    if provider == "scopus":
        return {
            "provider_key": provider,
            "query_family": query,
            "preferred_headers": ["Title", "Link", "Abstract", "Source", "Year", "Selected", "Notes"],
            "positional_layouts": [
                ["Title", "Link", "Abstract", "Source", "Year", "Selected", "Notes"],
                ["Title", "Link", "Abstract", "Source", "Year"],
            ],
            "snippet_header_fallbacks": ["Abstract"],
            "carried_note_headers": ["Source", "Year"],
            "selection_hint": "Mark Selected only on the visible row you believe is the correct hit.",
            "summary": "Scopus clipboard can usually be pasted close to the visible results table with Title, Link, Abstract, Source, and Year.",
        }
    if provider == "ieee":
        return {
            "provider_key": provider,
            "query_family": query,
            "preferred_headers": [
                "Document Title",
                "Document Link",
                "Abstract",
                "Publication Year",
                "Index Terms",
                "Selected",
                "Notes",
            ],
            "positional_layouts": [
                ["Document Title", "Document Link", "Abstract", "Publication Year", "Index Terms", "Selected", "Notes"],
                ["Document Title", "Document Link", "Publication Year", "Index Terms", "Selected", "Notes"],
                ["Document Title", "Document Link", "Abstract", "Publication Year", "Index Terms"],
                ["Document Title", "Document Link", "Publication Year", "Index Terms"],
            ],
            "snippet_header_fallbacks": ["Abstract", "Index Terms"],
            "carried_note_headers": ["Publication Year"],
            "selection_hint": "If the visible table has no abstract, Index Terms can be pasted and will be treated as visible-text context.",
            "summary": "IEEE clipboard can use Document Title/Link plus Abstract or Index Terms; Publication Year is preserved in notes.",
        }
    if provider in {"springer", "elsevier"}:
        return {
            "provider_key": provider,
            "query_family": query,
            "preferred_headers": ["Title", "URL", "Abstract", "Journal", "Year", "Selected", "Notes"],
            "positional_layouts": [
                ["Title", "URL", "Abstract", "Journal", "Year", "Selected", "Notes"],
                ["Title", "URL", "Abstract", "Journal", "Year"],
            ],
            "snippet_header_fallbacks": ["Abstract"],
            "carried_note_headers": ["Journal", "Year"],
            "selection_hint": "Mark Selected only on the row you want promoted as the source hit.",
            "summary": "Springer/Elsevier rows can usually be pasted with Title, URL, Abstract, Journal, and Year.",
        }
    return {
        "provider_key": provider or "generic",
        "query_family": query,
        "preferred_headers": ["URL", "Title", "Snippet", "Excerpt", "Selected", "Notes"],
        "positional_layouts": [
            ["URL", "Title", "Snippet", "Excerpt", "Selected", "Notes"],
            ["Title", "URL", "Snippet", "Excerpt", "Selected", "Notes"],
        ],
        "snippet_header_fallbacks": ["Snippet", "Abstract", "Keywords"],
        "carried_note_headers": ["Source", "Year"],
        "selection_hint": "Use Selected only when the visible row is already the correct hit.",
        "summary": "Generic clipboard intake accepts URL/Title/Snippet with optional Excerpt, Selected, and Notes.",
    }


def _provider_ordered_result_import_capture_sheet_template(
    rows: list[dict[str, Any]],
    *,
    provider_key: str,
    query_family: str,
) -> str:
    guide = _provider_ordered_result_import_capture_guide(
        provider_key=provider_key,
        query_family=query_family,
    )
    header_line = _provider_ordered_result_import_tsv_template(
        rows=[],
        provider_key=provider_key,
        query_family=query_family,
    ).strip() or "# URL<TAB>Title<TAB>Snippet<TAB>Excerpt<TAB>Selected<TAB>Notes"
    lines: list[str] = [
        f"# Provider capture sheet · {provider_key or 'provider'} · {query_family or 'query_family'}",
        f"# {guide.get('summary') or 'Paste provider-native visible result rows below.'}",
        header_line,
    ]
    for index, row in enumerate(rows, start=1):
        lines.extend(
            [
                f"# Row {index} · Candidate: {_text(row.get('candidate_id'))}",
                f"# Query seed title: {_text(row.get('title')) or _text(row.get('candidate_id')) or 'unknown'}",
                f"# Primary query: {_text(row.get('primary_query')) or 'unknown'}",
                f"# Evidence targets: {', '.join(_text(item) for item in list(row.get('evidence_targets', []) or []) if _text(item)) or 'none declared'}",
                "",
            ]
        )
    return "\n".join(lines).rstrip()


def _structured_search_result_capture_json_template(rows: list[dict[str, Any]]) -> str:
    payload = [
        {
            "candidate_id": _text(row.get("candidate_id")),
            "source_url": _text(row.get("source_url")),
            "search_result_title": _text(row.get("captured_result_title")),
            "search_result_snippet": _text(row.get("captured_result_snippet")),
            "notes": "",
        }
        for row in rows
    ]
    return json.dumps(payload, indent=2, ensure_ascii=True)


def _structured_search_query_result_resolve_json_template(rows: list[dict[str, Any]]) -> str:
    payload = [
        {
            "candidate_id": _text(row.get("candidate_id")),
            "option_index": int(row.get("current_option_index", 0) or 0),
            "reference_excerpt": "",
            "notes": "",
        }
        for row in rows
    ]
    return json.dumps(payload, indent=2, ensure_ascii=True)


def build_search_result_capture_register(
    *,
    discovery_candidate_review_register: list[dict[str, Any]] | None,
    article_reference_register: list[dict[str, Any]] | None,
) -> list[dict[str, Any]]:
    references_by_id = _reference_by_candidate_id(article_reference_register)
    rows: list[dict[str, Any]] = []

    for candidate_row in list(discovery_candidate_review_register or []):
        if not _is_query_seed_candidate(candidate_row):
            continue

        candidate = dict(candidate_row or {})
        candidate_id = _text(candidate.get("candidate_id"))
        reference = dict(references_by_id.get(candidate_id, {}) or {})
        acquisition_result = dict(reference.get("acquisition_result", {}) or {})
        metadata = dict(candidate.get("metadata_payload", {}) or {})
        parsed_notes = parse_query_seed_notes(metadata.get("notes") or candidate.get("notes"))
        reference_state = _text(reference.get("reference_state")) or _text(candidate.get("reference_state")) or "metadata_only"
        capture_state, next_capture_action, queue_status = _capture_state_for_row(
            reference_state=reference_state,
            acquisition_result=acquisition_result,
        )
        prefill = build_reference_resolution_prefill(
            candidate_row=candidate,
            reference_record=reference,
        )
        provider_key = _text(candidate.get("provider_key")) or _text(reference.get("provider_key")) or _text(prefill.get("provider_key"))
        source_family = _text(candidate.get("source_family")) or _source_family(provider_key)
        title = _text(candidate.get("title")) or _text(prefill.get("title")) or candidate_id
        row = {
            "candidate_id": candidate_id,
            "provider_key": provider_key,
            "provider_display_name": _text(prefill.get("provider_display_name")) or provider_key.replace("_", " ").title(),
            "source_family": source_family,
            "combination_id": _text(parsed_notes.get("combination_id")),
            "reference_state": reference_state,
            "capture_state": capture_state,
            "queue_status": queue_status,
            "next_capture_action": next_capture_action,
            "title": title,
            "source_url": _text(reference.get("source_url")) or _text(prefill.get("source_url")) or _text(candidate.get("source_url")),
            "launch_url": _text(prefill.get("launch_url")),
            "search_surface": _text(prefill.get("search_surface")),
            "execution_hint": _text(prefill.get("execution_hint")),
            "search_brief": _text(prefill.get("search_brief")) or _text(acquisition_result.get("search_brief")),
            "query_family": _text(prefill.get("query_family")) or _text(parsed_notes.get("query_family")),
            "primary_query": _text(prefill.get("primary_query")) or _text(parsed_notes.get("primary_query")),
            "pivot_query": _text(prefill.get("pivot_query")) or _text(parsed_notes.get("pivot_query")),
            "search_intent": _text(prefill.get("search_intent")),
            "evidence_targets": [
                _text(item)
                for item in list(prefill.get("evidence_targets", []) or parsed_notes.get("evidence_targets", []) or [])
                if _text(item)
            ],
            "captured_result_title": _text(prefill.get("captured_result_title")) or _text(acquisition_result.get("search_result_title")),
            "captured_result_snippet": _text(prefill.get("captured_result_snippet")) or _text(acquisition_result.get("search_result_snippet")),
            "acquisition_status": _text(acquisition_result.get("status")),
            "draft_resolution_prefill": prefill,
        }
        rows.append(row)

    action_order = {
        "READ_OR_DRAFT_REFERENCE": 0,
        "CAPTURE_SEARCH_RESULT": 1,
        "RESOLVE_REFERENCE_EXCERPT": 2,
        "NO_CAPTURE_REQUIRED": 3,
    }
    rows.sort(
        key=lambda row: (
            0 if _text(row.get("queue_status")) == "pending" else 1,
            action_order.get(_text(row.get("next_capture_action")), 9),
            _text(row.get("provider_key")),
            _text(row.get("query_family")),
            _text(row.get("title")) or _text(row.get("candidate_id")),
            _text(row.get("candidate_id")),
        )
    )
    return rows


def build_search_query_execution_register(
    *,
    search_result_capture_register: list[dict[str, Any]] | None,
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for capture_row in list(search_result_capture_register or []):
        row = dict(capture_row or {})
        query_variants = _query_variants(row)
        next_capture_action = _text(row.get("next_capture_action"))
        if next_capture_action == "READ_OR_DRAFT_REFERENCE":
            execution_status = "search_ready_needs_reference_draft"
        elif next_capture_action == "CAPTURE_SEARCH_RESULT":
            execution_status = "search_ready_capture_pending"
        elif next_capture_action == "RESOLVE_REFERENCE_EXCERPT":
            execution_status = "result_captured_ready_for_excerpt"
        else:
            execution_status = "closed"
        group_key = _join_nonempty(
            [
                _text(row.get("provider_key")),
                _text(row.get("query_family")),
                "::".join([_text(item) for item in list(row.get("evidence_targets", []) or []) if _text(item)]),
            ],
            sep="::",
        )
        execution_row = {
            "candidate_id": _text(row.get("candidate_id")),
            "provider_key": _text(row.get("provider_key")),
            "provider_display_name": _text(row.get("provider_display_name")),
            "source_family": _text(row.get("source_family")),
            "combination_id": _text(row.get("combination_id")),
            "reference_state": _text(row.get("reference_state")),
            "capture_state": _text(row.get("capture_state")),
            "queue_status": _text(row.get("queue_status")),
            "next_capture_action": next_capture_action,
            "execution_status": execution_status,
            "query_family": _text(row.get("query_family")),
            "primary_query": _text(row.get("primary_query")),
            "pivot_query": _text(row.get("pivot_query")),
            "query_variants": query_variants,
            "search_intent": _text(row.get("search_intent")),
            "launch_url": _text(row.get("launch_url")),
            "search_surface": _text(row.get("search_surface")),
            "execution_hint": _text(row.get("execution_hint")),
            "evidence_targets": [
                _text(item)
                for item in list(row.get("evidence_targets", []) or [])
                if _text(item)
            ],
            "search_brief": _text(row.get("search_brief")),
            "captured_result_title": _text(row.get("captured_result_title")),
            "captured_result_snippet": _text(row.get("captured_result_snippet")),
            "source_url": _text(row.get("source_url")),
            "search_group_key": group_key,
            "search_packet_template": _search_packet_template({**row, "query_variants": query_variants}),
            "capture_packet_template": _capture_packet_template(row),
        }
        rows.append(execution_row)

    status_order = {
        "search_ready_needs_reference_draft": 0,
        "search_ready_capture_pending": 1,
        "result_captured_ready_for_excerpt": 2,
        "closed": 3,
    }
    rows.sort(
        key=lambda row: (
            0 if _text(row.get("queue_status")) == "pending" else 1,
            status_order.get(_text(row.get("execution_status")), 9),
            _text(row.get("provider_key")),
            _text(row.get("query_family")),
            _text(row.get("candidate_id")),
        )
    )
    return rows


def build_search_query_result_option_register(
    *,
    search_query_execution_register: list[dict[str, Any]] | None,
    imported_result_records: list[dict[str, Any]] | None,
) -> list[dict[str, Any]]:
    imported_by_candidate: dict[str, list[dict[str, Any]]] = {}
    for raw_row in list(imported_result_records or []):
        row = dict(raw_row or {})
        candidate_id = _text(row.get("candidate_id"))
        source_url = _text(row.get("source_url"))
        if not candidate_id or not source_url:
            continue
        imported_by_candidate.setdefault(candidate_id, []).append(
            {
                "candidate_id": candidate_id,
                "rank": int(row.get("rank", 0) or 0),
                "source_url": source_url,
                "search_result_title": _text(row.get("search_result_title")),
                "search_result_snippet": _text(row.get("search_result_snippet")),
                "notes": _text(row.get("notes")),
                "reference_excerpt": _text(row.get("reference_excerpt")),
                "selected": bool(row.get("selected")),
                "imported_at": _text(row.get("imported_at")),
                "import_format": _text(row.get("import_format")) or "packet",
            }
        )

    for candidate_rows in imported_by_candidate.values():
        candidate_rows.sort(
            key=lambda row: (
                int(row.get("rank", 0) or 0) if int(row.get("rank", 0) or 0) > 0 else 9999,
                _text(row.get("search_result_title")) or _text(row.get("source_url")),
                _text(row.get("source_url")),
            )
        )
        for index, row in enumerate(candidate_rows, start=1):
            row["option_index"] = index

    enriched_rows: list[dict[str, Any]] = []
    for execution_row in list(search_query_execution_register or []):
        row = dict(execution_row or {})
        candidate_id = _text(row.get("candidate_id"))
        options = [dict(option) for option in imported_by_candidate.get(candidate_id, [])]
        row["imported_result_options"] = options
        row["imported_result_option_count"] = len(options)
        row["top_imported_result"] = dict(options[0]) if options else {}
        row["imported_result_state"] = "imported_options_available" if options else "no_imported_options"
        enriched_rows.append(row)
    return enriched_rows


def build_search_query_result_option_review_sequence(
    *,
    search_query_execution_register: list[dict[str, Any]] | None,
    batch_size: int = 4,
) -> dict[str, Any]:
    candidate_rows = [
        dict(row)
        for row in list(search_query_execution_register or [])
        if _text(row.get("queue_status")) == "pending"
        and _text(row.get("execution_status")) == "search_ready_capture_pending"
        and int(row.get("imported_result_option_count", 0) or 0) > 0
    ]
    candidate_rows.sort(
        key=lambda row: (
            _text(row.get("provider_key")),
            _text(row.get("query_family")),
            -int(row.get("imported_result_option_count", 0) or 0),
            _text(row.get("candidate_id")),
        )
    )
    rows: list[dict[str, Any]] = []
    for candidate_row in candidate_rows:
        options = [dict(option) for option in list(candidate_row.get("imported_result_options", []) or [])]
        if not options and dict(candidate_row.get("top_imported_result", {}) or {}):
            options = [
                {
                    **dict(candidate_row.get("top_imported_result", {}) or {}),
                    "option_index": 1,
                }
            ]
        option_count = len(options)
        for option in options:
            option_index = int(option.get("option_index", 0) or 0)
            rows.append(
                {
                    **candidate_row,
                    "current_option_index": option_index,
                    "current_option_count": option_count,
                    "current_imported_option": dict(option),
                    "option_review_id": (
                        f"{_text(candidate_row.get('candidate_id'))}::option::{option_index}"
                    ),
                }
            )
    current_row = dict(rows[0]) if rows else {}
    return {
        "rows": rows,
        "current_row": current_row,
        "next_rows": rows[1:max(int(batch_size or 4), 1)],
        "summary": {
            "total": len(rows),
            "pending": len(rows),
            "current_position": 1 if rows else 0,
            "candidate_count": len(candidate_rows),
            "option_count": len(rows),
            "batch_size": max(int(batch_size or 4), 1),
        },
    }


def build_search_query_result_option_batch_plan(
    *,
    search_query_result_option_review_register: list[dict[str, Any]] | None,
    batch_size: int = 4,
) -> dict[str, Any]:
    rows = [dict(row) for row in list(search_query_result_option_review_register or [])]
    if not rows:
        return {
            "available": False,
            "option_count": 0,
            "candidate_count": 0,
            "candidate_ids": [],
            "option_review_ids": [],
            "batch_reason": "no imported-result options pending",
            "promote_records_json_template": "[]",
            "accepted_promote_formats": ["structured_records", "json_array"],
            "resolve_available": False,
            "resolve_candidate_count": 0,
            "resolve_candidate_ids": [],
            "resolve_records_json_template": "[]",
            "accepted_resolve_formats": ["structured_records", "json_array"],
        }

    current_row = dict(rows[0])
    current_provider = _text(current_row.get("provider_key"))
    current_query_family = _text(current_row.get("query_family"))
    current_source_family = _text(current_row.get("source_family"))
    current_evidence_targets = [
        _text(item)
        for item in list(current_row.get("evidence_targets", []) or [])
        if _text(item)
    ]

    def _same_provider_and_query(row: dict[str, Any]) -> bool:
        return (
            _text(row.get("provider_key")) == current_provider
            and _text(row.get("query_family")) == current_query_family
        )

    def _same_source_family_and_query(row: dict[str, Any]) -> bool:
        return (
            _text(row.get("source_family")) == current_source_family
            and _text(row.get("query_family")) == current_query_family
        )

    grouped = [current_row]
    target_size = max(int(batch_size or 4), 1)
    for matcher in (_same_provider_and_query, _same_source_family_and_query):
        for row in rows[1:]:
            if len(grouped) >= target_size:
                break
            if row in grouped:
                continue
            if matcher(row):
                grouped.append(dict(row))
        if len(grouped) >= target_size:
            break
    if len(grouped) < target_size:
        for row in rows[1:]:
            if len(grouped) >= target_size:
                break
            if row in grouped:
                continue
            grouped.append(dict(row))

    payload = [
        {
            "candidate_id": _text(row.get("candidate_id")),
            "option_index": int(row.get("current_option_index", 0) or 0),
            "notes": "",
        }
        for row in grouped
    ]
    resolve_rows_by_candidate: dict[str, dict[str, Any]] = {}
    resolve_order: list[str] = []
    for row in grouped:
        candidate_id = _text(row.get("candidate_id"))
        if not candidate_id or candidate_id in resolve_rows_by_candidate:
            continue
        resolve_rows_by_candidate[candidate_id] = dict(row)
        resolve_order.append(candidate_id)
    resolve_rows = [resolve_rows_by_candidate[candidate_id] for candidate_id in resolve_order]
    return {
        "available": True,
        "rows": grouped,
        "option_count": len(grouped),
        "candidate_count": len({_text(row.get("candidate_id")) for row in grouped if _text(row.get("candidate_id"))}),
        "candidate_ids": [_text(row.get("candidate_id")) for row in grouped if _text(row.get("candidate_id"))],
        "option_review_ids": [_text(row.get("option_review_id")) for row in grouped if _text(row.get("option_review_id"))],
        "provider_key": current_provider,
        "source_family": current_source_family,
        "query_family": current_query_family,
        "evidence_targets": current_evidence_targets,
        "batch_reason": "same_provider_and_query_family_first",
        "promote_records_json_template": json.dumps(payload, indent=2, ensure_ascii=True),
        "accepted_promote_formats": ["structured_records", "json_array"],
        "resolve_available": len(resolve_rows) >= 1,
        "resolve_rows": resolve_rows,
        "resolve_candidate_count": len(resolve_rows),
        "resolve_candidate_ids": [_text(row.get("candidate_id")) for row in resolve_rows if _text(row.get("candidate_id"))],
        "resolve_records_json_template": _structured_search_query_result_resolve_json_template(resolve_rows),
        "accepted_resolve_formats": ["structured_records", "json_array"],
    }


def build_search_query_execution_sequence(
    *,
    search_query_execution_register: list[dict[str, Any]] | None,
    batch_size: int = 4,
) -> dict[str, Any]:
    rows = [dict(row) for row in list(search_query_execution_register or [])]
    pending_rows = [row for row in rows if _text(row.get("queue_status")) == "pending"]
    current_row = dict(pending_rows[0]) if pending_rows else {}
    next_rows = pending_rows[1:max(int(batch_size or 4), 1)]
    return {
        "rows": rows,
        "current_row": current_row,
        "next_rows": next_rows,
        "summary": {
            "total": len(rows),
            "pending": len(pending_rows),
            "closed": len(rows) - len(pending_rows),
            "search_ready_needs_reference_draft": sum(
                1 for row in rows if _text(row.get("execution_status")) == "search_ready_needs_reference_draft"
            ),
            "search_ready_capture_pending": sum(
                1 for row in rows if _text(row.get("execution_status")) == "search_ready_capture_pending"
            ),
            "result_captured_ready_for_excerpt": sum(
                1 for row in rows if _text(row.get("execution_status")) == "result_captured_ready_for_excerpt"
            ),
            "current_position": ((len(rows) - len(pending_rows)) + 1) if pending_rows else 0,
            "batch_size": max(int(batch_size or 4), 1),
        },
    }


def build_search_query_execution_batch_plan(
    *,
    search_query_execution_register: list[dict[str, Any]] | None,
    batch_size: int = 4,
) -> dict[str, Any]:
    rows = [
        dict(row)
        for row in list(search_query_execution_register or [])
        if _text(row.get("queue_status")) == "pending"
        and _text(row.get("execution_status")) == "search_ready_capture_pending"
    ]
    if not rows:
        return {
            "available": False,
            "candidate_count": 0,
            "candidate_ids": [],
            "packet_template": "",
            "batch_reason": "no capture-pending search rows",
        }

    current_row = dict(rows[0])
    current_provider = _text(current_row.get("provider_key"))
    current_query_family = _text(current_row.get("query_family"))
    current_source_family = _text(current_row.get("source_family"))
    current_evidence_targets = [
        _text(item)
        for item in list(current_row.get("evidence_targets", []) or [])
        if _text(item)
    ]

    def _same_provider_and_query(row: dict[str, Any]) -> bool:
        return (
            _text(row.get("provider_key")) == current_provider
            and _text(row.get("query_family")) == current_query_family
        )

    def _same_source_family_and_query(row: dict[str, Any]) -> bool:
        return (
            _text(row.get("source_family")) == current_source_family
            and _text(row.get("query_family")) == current_query_family
        )

    grouped = [current_row]
    for matcher in (_same_provider_and_query, _same_source_family_and_query):
        for row in rows[1:]:
            if len(grouped) >= max(int(batch_size or 4), 1):
                break
            if row in grouped:
                continue
            if matcher(row):
                grouped.append(dict(row))
        if len(grouped) >= max(int(batch_size or 4), 1):
            break
    if len(grouped) < max(int(batch_size or 4), 1):
        for row in rows[1:]:
            if len(grouped) >= max(int(batch_size or 4), 1):
                break
            if row in grouped:
                continue
            grouped.append(dict(row))

    packet_blocks: list[str] = []
    import_packet_blocks: list[str] = []
    imported_result_count = 0
    promotable_candidate_ids: list[str] = []
    for row in grouped:
        imported_options = [dict(option) for option in list(row.get("imported_result_options", []) or [])]
        imported_result_count += len(imported_options)
        if imported_options:
            promotable_candidate_ids.append(_text(row.get("candidate_id")))
        packet_blocks.append(
            "\n".join(
                [
                    f"# Provider: {_text(row.get('provider_display_name')) or _text(row.get('provider_key')) or 'unknown'}",
                    f"# Query family: {_text(row.get('query_family')) or 'unknown'}",
                    f"# Launch URL: {_text(row.get('launch_url'))}",
                    f"# Primary query: {_text(row.get('primary_query'))}",
                    "Candidate ID: " + _text(row.get("candidate_id")),
                    "URL: " + _text(row.get("source_url")),
                    "Title: " + _text(row.get("captured_result_title")),
                    "Snippet: " + _text(row.get("captured_result_snippet")),
                    "Notes: ",
                ]
            )
        )
        import_packet_blocks.append(
            "\n".join(
                [
                    f"# Provider: {_text(row.get('provider_display_name')) or _text(row.get('provider_key')) or 'unknown'}",
                    f"# Query family: {_text(row.get('query_family')) or 'unknown'}",
                    f"# Launch URL: {_text(row.get('launch_url'))}",
                    f"# Primary query: {_text(row.get('primary_query'))}",
                    "Candidate ID: " + _text(row.get("candidate_id")),
                    "Rank: 1",
                    "URL: " + _text((row.get("top_imported_result", {}) or {}).get("source_url")),
                    "Title: " + _text((row.get("top_imported_result", {}) or {}).get("search_result_title")),
                    "Snippet: " + _text((row.get("top_imported_result", {}) or {}).get("search_result_snippet")),
                    "Selected: ",
                    "Excerpt: ",
                    "Notes: ",
                ]
            )
        )
    return {
        "available": True,
        "candidate_count": len(grouped),
        "candidate_ids": [_text(row.get("candidate_id")) for row in grouped if _text(row.get("candidate_id"))],
        "provider_key": current_provider,
        "source_family": current_source_family,
        "query_family": current_query_family,
        "evidence_targets": current_evidence_targets,
        "batch_reason": "same_provider_and_query_family_first",
        "packet_template": "\n---\n".join(packet_blocks),
        "search_execution_provider_guide": _provider_search_execution_guide(
            provider_key=current_provider,
            source_family=current_source_family,
            query_family=current_query_family,
        ),
        "search_execution_provider_sheet_template": _provider_search_execution_sheet_template(
            grouped,
            provider_key=current_provider,
            source_family=current_source_family,
            query_family=current_query_family,
        ),
        "search_execution_capture_workbook_template": _provider_search_execution_capture_workbook_template(
            grouped,
            provider_key=current_provider,
            source_family=current_source_family,
            query_family=current_query_family,
        ),
        "capture_result_json_template": _structured_search_result_capture_json_template(grouped),
        "accepted_capture_formats": ["packet", "structured_records", "json_array"],
        "result_import_packet_template": "\n---\n".join(import_packet_blocks),
        "result_import_json_template": _structured_result_import_json_template(grouped),
        "ordered_result_import_json_template": _structured_ordered_result_import_json_template(grouped),
        "ordered_result_import_packet_template": _ordered_result_import_packet_template(grouped),
        "ordered_result_import_compact_template": _ordered_result_import_compact_template(grouped),
        "ordered_result_import_tsv_template": _ordered_result_import_tsv_template(grouped),
        "ordered_result_import_provider_tsv_template": _provider_ordered_result_import_tsv_template(
            grouped,
            provider_key=current_provider,
            query_family=current_query_family,
        ),
        "ordered_result_import_provider_capture_guide": _provider_ordered_result_import_capture_guide(
            provider_key=current_provider,
            query_family=current_query_family,
        ),
        "ordered_result_import_provider_capture_sheet_template": _provider_ordered_result_import_capture_sheet_template(
            grouped,
            provider_key=current_provider,
            query_family=current_query_family,
        ),
        "accepted_import_formats": ["packet", "ordered_packet", "ordered_compact_lines", "ordered_tsv_lines", "structured_records", "json_array", "ordered_records"],
        "imported_result_count": imported_result_count,
        "promotable_candidate_ids": [candidate_id for candidate_id in promotable_candidate_ids if candidate_id],
    }


def build_search_result_capture_sequence(
    *,
    search_result_capture_register: list[dict[str, Any]] | None,
    batch_size: int = 4,
) -> dict[str, Any]:
    rows = [dict(row) for row in list(search_result_capture_register or [])]
    pending_rows = [row for row in rows if _text(row.get("queue_status")) == "pending"]
    current_row = dict(pending_rows[0]) if pending_rows else {}
    next_rows = pending_rows[1:max(int(batch_size or 4), 1)]
    return {
        "rows": rows,
        "current_row": current_row,
        "next_rows": next_rows,
        "summary": {
            "total": len(rows),
            "pending": len(pending_rows),
            "closed": len(rows) - len(pending_rows),
            "needs_draft": sum(1 for row in rows if _text(row.get("capture_state")) == "needs_draft"),
            "seed_only": sum(1 for row in rows if _text(row.get("capture_state")) == "seed_only"),
            "result_captured": sum(1 for row in rows if _text(row.get("capture_state")) == "result_captured"),
            "excerpt_resolved": sum(1 for row in rows if _text(row.get("capture_state")) == "excerpt_resolved"),
            "current_position": ((len(rows) - len(pending_rows)) + 1) if pending_rows else 0,
            "batch_size": max(int(batch_size or 4), 1),
        },
    }
