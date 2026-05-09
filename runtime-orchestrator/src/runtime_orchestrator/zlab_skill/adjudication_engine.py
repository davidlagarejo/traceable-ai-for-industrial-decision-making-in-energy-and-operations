from __future__ import annotations

from datetime import datetime, timezone
from typing import Any


ALLOWED_COMBINATION_DECISIONS = {
    "candidate",
    "accepted_for_case_use",
    "rejected_for_case_use",
    "needs_review",
    "blocked_by_validator",
}

ALLOWED_DECISION_SCOPES = {
    "run",
    "session",
}


def _text(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, str):
        return value.strip()
    return str(value).strip()


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def normalize_combination_decision_record(
    payload: dict[str, Any],
    *,
    default_scope: str = "run",
) -> dict[str, Any]:
    combination_id = _text((payload or {}).get("combination_id"))
    if not combination_id:
        raise ValueError("combination_id is required")

    operator_decision = _text((payload or {}).get("operator_decision")) or "candidate"
    if operator_decision not in ALLOWED_COMBINATION_DECISIONS:
        raise ValueError(f"operator_decision must be one of: {sorted(ALLOWED_COMBINATION_DECISIONS)}")

    decision_scope = _text((payload or {}).get("decision_scope")) or _text(default_scope) or "run"
    if decision_scope not in ALLOWED_DECISION_SCOPES:
        raise ValueError(f"decision_scope must be one of: {sorted(ALLOWED_DECISION_SCOPES)}")

    return {
        "combination_id": combination_id,
        "operator_decision": operator_decision,
        "decision_reason": _text((payload or {}).get("decision_reason")),
        "decision_scope": decision_scope,
        "decision_timestamp": _text((payload or {}).get("decision_timestamp")) or _utc_now_iso(),
    }


def merge_combination_review_with_decisions(
    *,
    combination_review_register: list[dict[str, Any]],
    decision_records: list[dict[str, Any]] | None = None,
) -> list[dict[str, Any]]:
    decisions_by_id = {
        _text(row.get("combination_id")): dict(row)
        for row in list(decision_records or [])
        if _text(row.get("combination_id"))
    }
    rows: list[dict[str, Any]] = []
    for row in list(combination_review_register or []):
        normalized = dict(row)
        decision = decisions_by_id.get(_text(row.get("combination_id")))
        if decision:
            normalized["operator_decision"] = _text(decision.get("operator_decision")) or _text(row.get("operator_decision")) or "candidate"
            normalized["decision_reason"] = _text(decision.get("decision_reason"))
            normalized["decision_scope"] = _text(decision.get("decision_scope")) or "run"
            normalized["decision_timestamp"] = _text(decision.get("decision_timestamp"))
        else:
            normalized.setdefault("operator_decision", _text(row.get("operator_decision")) or "candidate")
            normalized.setdefault("decision_reason", "")
            normalized.setdefault("decision_scope", "run")
            normalized.setdefault("decision_timestamp", "")
        rows.append(normalized)
    return rows


def summarize_combination_decisions(
    combination_review_register: list[dict[str, Any]] | None,
) -> dict[str, Any]:
    rows = list(combination_review_register or [])
    counts = {key: 0 for key in sorted(ALLOWED_COMBINATION_DECISIONS)}
    for row in rows:
        decision = _text(row.get("operator_decision")) or "candidate"
        if decision not in counts:
            counts[decision] = 0
        counts[decision] += 1
    return {
        "total": len(rows),
        "by_decision": counts,
        "accepted": counts.get("accepted_for_case_use", 0),
        "rejected": counts.get("rejected_for_case_use", 0),
        "needs_review": counts.get("needs_review", 0),
        "blocked": counts.get("blocked_by_validator", 0),
        "candidate": counts.get("candidate", 0),
    }
