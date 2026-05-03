from __future__ import annotations

from typing import Any

from .schemas import text


_EMPTY_MARKERS = (
    "no competitive-comparison rows were produced",
    "no routed public-source coverage rows were produced",
    "no public source-coverage rows were produced",
    "no structural benchmarking rows were produced",
    "no source-traceability rows were produced",
)


def _list_text(value: Any) -> list[str]:
    if isinstance(value, list):
        return [text(item) for item in value if text(item)]
    single = text(value)
    return [single] if single else []


def _dedupe(values: list[str]) -> list[str]:
    seen: set[str] = set()
    out: list[str] = []
    for value in values:
        normalized = text(value)
        if not normalized or normalized in seen:
            continue
        seen.add(normalized)
        out.append(normalized)
    return out


def _attempted_items(
    *,
    search_attempt_ledger: list[dict[str, Any]],
    discovery_need_register: list[dict[str, Any]],
    source_family_coverage_table: list[dict[str, Any]],
) -> list[str]:
    attempted = [
        text(row.get("source_family")) or text(row.get("query_family")) or text(row.get("purpose"))
        for row in list(search_attempt_ledger or [])
    ]
    attempted.extend(text(row.get("discovery_need")) for row in list(discovery_need_register or []))
    attempted.extend(text(row.get("source_family")) or text(row.get("source_name")) for row in list(source_family_coverage_table or []))
    return _dedupe([item for item in attempted if item])[:6]


def _empty_peer_fallback(
    *,
    comparison_not_yet_valid_register: list[dict[str, Any]],
    comparison_blocker_register: list[dict[str, Any]],
    peer_requirement_register: list[dict[str, Any]],
    search_attempt_ledger: list[dict[str, Any]],
    discovery_need_register: list[dict[str, Any]],
    source_family_coverage_table: list[dict[str, Any]],
) -> dict[str, Any]:
    comparison_row = dict(comparison_not_yet_valid_register[0] if comparison_not_yet_valid_register else {})
    blocker_row = dict(comparison_blocker_register[0] if comparison_blocker_register else {})
    missing = _dedupe(
        _list_text(comparison_row.get("required_before_comparison"))
        + _list_text(blocker_row.get("missing_evidence"))
        + [
            missing_item
            for row in list(peer_requirement_register or [])
            for missing_item in _list_text(row.get("missing_evidence"))
        ]
    )[:8]
    attempted = _attempted_items(
        search_attempt_ledger=search_attempt_ledger,
        discovery_need_register=discovery_need_register,
        source_family_coverage_table=source_family_coverage_table,
    )
    why = (
        text(comparison_row.get("explanation"))
        or text(blocker_row.get("why"))
        or "Fair peer comparison remains blocked because the comparison basis is still structurally incomplete."
    )
    return {
        "section_key": "peer_comparison",
        "section_titles": [
            "Competitive / Peer Comparison",
            "Structural Benchmarking & Competitive Comparison",
        ],
        "why_no_rows_exist": why,
        "what_was_attempted": attempted,
        "what_is_required": missing or ["fair-comparison requirements remain unresolved"],
        "claim_impact": "Peer superiority, transferable ROI, and generic benchmark interpretation remain prohibited until the fair peer set is built.",
        "fallback_state": "explained_fallback",
    }


def _empty_source_fallback(
    *,
    source_family_coverage_table: list[dict[str, Any]],
    search_attempt_ledger: list[dict[str, Any]],
    discovery_need_register: list[dict[str, Any]],
    next_best_search_register: list[dict[str, Any]],
) -> dict[str, Any]:
    attempted = _attempted_items(
        search_attempt_ledger=search_attempt_ledger,
        discovery_need_register=discovery_need_register,
        source_family_coverage_table=source_family_coverage_table,
    )
    required = _dedupe(
        [
            item
            for row in list(next_best_search_register or [])
            for item in _list_text(row.get("expected_evidence"))
        ]
    )[:8]
    why = (
        "No routed public-source coverage rows were accepted into asset-level support after the current discovery wave."
    )
    return {
        "section_key": "public_source_coverage",
        "section_titles": [
            "Public Source Coverage Table",
            "Source Traceability",
        ],
        "why_no_rows_exist": why,
        "what_was_attempted": attempted,
        "what_is_required": required or ["additional public-source confirmation or operator evidence"],
        "claim_impact": "Public-source-backed local claims remain bounded; unresolved local truth must stay in intake or hypothesis state.",
        "fallback_state": "explained_fallback",
    }


def build_section_explanation_fallback_register(
    *,
    competitive_comparison_register: list[dict[str, Any]],
    comparison_not_yet_valid_register: list[dict[str, Any]],
    comparison_blocker_register: list[dict[str, Any]],
    peer_requirement_register: list[dict[str, Any]],
    source_family_coverage_table: list[dict[str, Any]],
    search_attempt_ledger: list[dict[str, Any]],
    discovery_need_register: list[dict[str, Any]],
    next_best_search_register: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    if not competitive_comparison_register:
        rows.append(
            _empty_peer_fallback(
                comparison_not_yet_valid_register=comparison_not_yet_valid_register,
                comparison_blocker_register=comparison_blocker_register,
                peer_requirement_register=peer_requirement_register,
                search_attempt_ledger=search_attempt_ledger,
                discovery_need_register=discovery_need_register,
                source_family_coverage_table=source_family_coverage_table,
            )
        )
    if not source_family_coverage_table:
        rows.append(
            _empty_source_fallback(
                source_family_coverage_table=source_family_coverage_table,
                search_attempt_ledger=search_attempt_ledger,
                discovery_need_register=discovery_need_register,
                next_best_search_register=next_best_search_register,
            )
        )
    return rows


def _is_empty_section(section: dict[str, Any]) -> bool:
    text_blob = " ".join(
        text(block.get("content"))
        for block in list(section.get("blocks", []) or [])
        if isinstance(block, dict)
    ).lower()
    return (not text_blob) or any(marker in text_blob for marker in _EMPTY_MARKERS)


def _fallback_lines(
    *,
    title: str,
    why_no_rows_exist: str,
    what_was_attempted: list[str],
    what_is_required: list[str],
    claim_impact: str,
    language: str,
) -> list[str]:
    if language == "es":
        lines = [
            "=" * 72,
            title.upper(),
            "=" * 72,
            "",
            "Esta sección se explica explícitamente en vez de quedar vacía.",
            "",
            "Por qué no hay filas:",
            f"  {why_no_rows_exist}",
            "",
            "Qué se intentó:",
        ]
        lines.extend(f"  - {item}" for item in (what_was_attempted or ["No attempt metadata was recorded."]))
        lines.extend([
            "",
            "Qué se requiere para poblarla:",
        ])
        lines.extend(f"  - {item}" for item in (what_is_required or ["Se requiere evidencia adicional."]))
        lines.extend([
            "",
            "Impacto en los claims:",
            f"  {claim_impact}",
            "",
        ])
        return lines
    lines = [
        "=" * 72,
        title.upper(),
        "=" * 72,
        "",
        "This section is intentionally explained rather than left empty.",
        "",
        "Why no rows exist:",
        f"  {why_no_rows_exist}",
        "",
        "What was attempted:",
    ]
    lines.extend(f"  - {item}" for item in (what_was_attempted or ["No attempt metadata was recorded."]))
    lines.extend([
        "",
        "What is required to populate it:",
    ])
    lines.extend(f"  - {item}" for item in (what_is_required or ["Additional evidence is required."]))
    lines.extend([
        "",
        "Claim impact:",
        f"  {claim_impact}",
        "",
    ])
    return lines


def apply_empty_section_policy(
    *,
    body_sections: list[dict[str, Any]],
    appendix_sections: list[dict[str, Any]],
    section_explanation_fallback_register: list[dict[str, Any]],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]:
    fallback_by_title: dict[str, dict[str, Any]] = {}
    for row in list(section_explanation_fallback_register or []):
        for title in list(row.get("section_titles", []) or []):
            fallback_by_title[text(title)] = dict(row)

    applied_rows: list[dict[str, Any]] = []
    status_rows: list[dict[str, Any]] = []

    def _apply(sections: list[dict[str, Any]]) -> list[dict[str, Any]]:
        out: list[dict[str, Any]] = []
        for section in list(sections or []):
            row = dict(section)
            title = text(row.get("title"))
            fallback = fallback_by_title.get(title)
            if not fallback:
                out.append(row)
                continue

            empty_now = _is_empty_section(row)
            population_state = "populated"
            applied = False
            if empty_now:
                block = dict((row.get("blocks", []) or [{}])[0] or {})
                block["content"] = "\n".join(
                    _fallback_lines(
                        title=title,
                        why_no_rows_exist=text(fallback.get("why_no_rows_exist")),
                        what_was_attempted=_list_text(fallback.get("what_was_attempted")),
                        what_is_required=_list_text(fallback.get("what_is_required")),
                        claim_impact=text(fallback.get("claim_impact")),
                        language="en",
                    )
                )
                block["content_en"] = block["content"]
                block["content_es"] = "\n".join(
                    _fallback_lines(
                        title=title,
                        why_no_rows_exist=text(fallback.get("why_no_rows_exist")),
                        what_was_attempted=_list_text(fallback.get("what_was_attempted")),
                        what_is_required=_list_text(fallback.get("what_is_required")),
                        claim_impact=text(fallback.get("claim_impact")),
                        language="es",
                    )
                )
                row["blocks"] = [block]
                row["empty_section_policy_applied"] = True
                row["section_population_state"] = text(fallback.get("fallback_state")) or "explained_fallback"
                row["section_claim_impact"] = text(fallback.get("claim_impact"))
                applied = True
                population_state = row["section_population_state"]
            else:
                row["empty_section_policy_applied"] = False
                row["section_population_state"] = "populated"

            if applied:
                applied_rows.append(
                    {
                        "section_title": title,
                        "policy_state": row.get("section_population_state"),
                        "claim_impact": text(fallback.get("claim_impact")),
                    }
                )
            status_rows.append(
                {
                    "section_title": title,
                    "section_id": text(row.get("section_id")),
                    "population_state": population_state,
                    "fallback_applied": applied,
                }
            )
            out.append(row)
        return out

    return _apply(body_sections), _apply(appendix_sections), applied_rows, status_rows


def build_empty_section_policy_register(
    *,
    applied_policy_rows: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    return [
        {
            "section_title": text(row.get("section_title")),
            "policy_state": text(row.get("policy_state")) or "explained_fallback",
            "claim_impact": text(row.get("claim_impact")),
        }
        for row in list(applied_policy_rows or [])
        if text(row.get("section_title"))
    ]


def build_section_population_status_register(
    *,
    section_population_rows: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    return [
        {
            "section_title": text(row.get("section_title")),
            "section_id": text(row.get("section_id")),
            "population_state": text(row.get("population_state")) or "unknown",
            "fallback_applied": bool(row.get("fallback_applied", False)),
        }
        for row in list(section_population_rows or [])
        if text(row.get("section_title"))
    ]
