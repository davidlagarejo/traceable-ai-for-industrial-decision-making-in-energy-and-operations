from __future__ import annotations

from typing import Any

from .schemas import text


def _outcome_class(status: str) -> str:
    return {
        "found": "evidence_found",
        "no_data": "queried_no_payload",
        "failed": "attempt_failed",
        "context_missing": "blocked_missing_context",
        "not_applicable": "filtered_out_of_scope",
        "time_budget_exhausted": "deferred_budget_exhausted",
    }.get(status, "recorded")


def build_search_attempt_ledger(
    *,
    attempts: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    ledger: list[dict[str, Any]] = []
    for idx, row in enumerate(list(attempts or []), start=1):
        status = text(row.get("status"))
        source_family = text(row.get("source_family"))
        source_type = text(row.get("source_type"))
        ledger.append(
            {
                "attempt_sequence": idx,
                "attempt_kind": text(row.get("attempt_kind")),
                "round_id": text(row.get("round_id")),
                "source_type": source_type,
                "source_family": source_family,
                "query_family": source_family or source_type,
                "purpose": text(row.get("discovery_reason")),
                "locator": text(row.get("locator")),
                "status": status,
                "outcome_class": _outcome_class(status),
                "evidence_gained": status == "found",
                "blocker_removed": status == "found",
                "detail": text(row.get("detail")) or text(row.get("error")),
                "lifecycle_stage": text(row.get("lifecycle_stage")),
                "produced_at": text(row.get("produced_at")),
            }
        )
    return ledger


def build_search_attempt_outcome_register(
    *,
    search_attempt_ledger: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    counts: dict[tuple[str, str], int] = {}
    for row in list(search_attempt_ledger or []):
        key = (text(row.get("attempt_kind")), text(row.get("outcome_class")))
        counts[key] = counts.get(key, 0) + 1
    out: list[dict[str, Any]] = []
    for (attempt_kind, outcome_class), count in sorted(counts.items()):
        out.append(
            {
                "attempt_kind": attempt_kind,
                "outcome_class": outcome_class,
                "attempt_count": count,
            }
        )
    return out
