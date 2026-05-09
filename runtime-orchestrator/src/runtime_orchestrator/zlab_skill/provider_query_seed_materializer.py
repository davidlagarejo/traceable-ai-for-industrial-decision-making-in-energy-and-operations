from __future__ import annotations

from datetime import datetime
from typing import Any, Callable, Mapping


def _text(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, str):
        return value.strip()
    return str(value).strip()


def _safe_store_component(value: Any) -> str:
    return "".join(
        ch if ch.isalnum() or ch in {"-", "_", "."} else "_"
        for ch in _text(value)
    ) or "default"


def build_query_seed_candidate_records(
    *,
    combination_id: str,
    follow_on_manifest_row: Mapping[str, Any] | None,
    default_launch_url_builder: Callable[[str], str] | None = None,
    current_year: int | None = None,
) -> list[dict[str, Any]]:
    manifest_row = dict(follow_on_manifest_row or {})
    normalized_combination_id = _text(combination_id)
    combination_name = _text(manifest_row.get("combination_name")) or normalized_combination_id
    seed_year = int(current_year or datetime.utcnow().year)
    rows: list[dict[str, Any]] = []

    for execution_row in list(manifest_row.get("execution_rows", []) or []):
        source_family = _text(execution_row.get("source_family"))
        for template in list(execution_row.get("provider_query_templates", []) or []):
            provider_key = _text(template.get("provider_key"))
            query_family = _text(template.get("query_family"))
            if not provider_key or not query_family:
                continue

            provider_display = _text(template.get("provider_display_name")) or provider_key.replace("_", " ").title()
            launch_url = (
                _text(default_launch_url_builder(provider_key))
                if default_launch_url_builder is not None
                else ""
            )
            evidence_targets = [
                _text(item)
                for item in list(template.get("evidence_targets", []) or [])
                if _text(item)
            ]
            seed_terms = [
                _text(item)
                for item in list(template.get("seed_terms", []) or [])
                if _text(item)
            ]
            asset_focus_terms = [
                _text(item)
                for item in list(template.get("asset_focus_terms", []) or [])
                if _text(item)
            ]
            notes = " ".join(
                part
                for part in [
                    f"Query-seed candidate for combination {normalized_combination_id}.",
                    f"Source family: {source_family}.",
                    f"Query family: {query_family}.",
                    f"Primary query: {_text(template.get('primary_query'))}.",
                    f"Pivot query: {_text(template.get('pivot_query'))}.",
                    f"Evidence targets: {', '.join(evidence_targets) or 'none specified'}.",
                    f"Search intent: {_text(template.get('search_intent'))}.",
                ]
                if _text(part)
            ).strip()
            rows.append(
                {
                    "candidate_id": (
                        f"queryseed-{_safe_store_component(provider_key)}-"
                        f"{_safe_store_component(normalized_combination_id)}-"
                        f"{_safe_store_component(query_family)}"
                    ),
                    "provider_key": provider_key,
                    "title": (
                        f"Research lead · {provider_display} · "
                        f"{query_family.replace('_', ' ')} · {combination_name}"
                    ),
                    "doi": "",
                    "journal": "Query seed / research lead",
                    "published_year": str(seed_year),
                    "source_url": launch_url,
                    "keywords": list(dict.fromkeys([*asset_focus_terms, *seed_terms, *evidence_targets])),
                    "abstract": _text(template.get("search_intent")),
                    "notes": notes,
                    "reference_excerpt": "",
                    "operator_decision": "candidate",
                    "provider_display_name": provider_display,
                    "launch_url": launch_url,
                    "search_surface": _text(template.get("search_surface")),
                    "search_intent": _text(template.get("search_intent")),
                    "primary_query": _text(template.get("primary_query")),
                    "pivot_query": _text(template.get("pivot_query")),
                    "evidence_targets": evidence_targets,
                    "seed_terms": seed_terms,
                    "asset_focus_terms": asset_focus_terms,
                    "execution_hint": _text(template.get("execution_hint")),
                    "query_family": query_family,
                    "source_family": source_family,
                }
            )
    return rows
