from __future__ import annotations

from typing import Any, Mapping

from .memory_scope import evaluate_memory_record_scope, validate_memory_record


def build_memory_admissibility_register(
    memory_records: list[dict[str, Any]] | None,
    *,
    current_context: Mapping[str, Any] | None = None,
    registry_bundle: dict[str, Any] | None = None,
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for payload in list(memory_records or []):
        normalized = validate_memory_record(payload, registry_bundle=registry_bundle)
        rows.append(
            evaluate_memory_record_scope(
                normalized,
                current_context=current_context,
            )
        )
    return rows


def summarize_memory_register(
    memory_admissibility_register: list[dict[str, Any]] | None,
) -> dict[str, Any]:
    rows = list(memory_admissibility_register or [])
    summary: dict[str, Any] = {
        "total": len(rows),
        "admissible": 0,
        "blocked": 0,
        "by_memory_type": {},
        "by_use_mode": {},
    }
    for row in rows:
        state = str(row.get("admissibility_state", "")).strip() or "blocked"
        summary[state] = int(summary.get(state, 0)) + 1

        memory_type = str(row.get("memory_type", "")).strip() or "unknown"
        by_type = dict(summary["by_memory_type"])
        by_type[memory_type] = int(by_type.get(memory_type, 0)) + 1
        summary["by_memory_type"] = by_type

        use_mode = str(row.get("use_mode", "")).strip() or "unknown"
        by_mode = dict(summary["by_use_mode"])
        by_mode[use_mode] = int(by_mode.get(use_mode, 0)) + 1
        summary["by_use_mode"] = by_mode
    return summary
