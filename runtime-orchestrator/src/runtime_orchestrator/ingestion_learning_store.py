from __future__ import annotations

import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .config import DEFAULT_INGESTION_LEARNING_STORE_DIR

_HISTORY_LIMIT = 20


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _slugify(value: str) -> str:
    text = re.sub(r"[^a-z0-9]+", "-", str(value or "").strip().lower()).strip("-")
    return text or "unknown-pipeline"


def _store_path(pipeline_id: str, store_dir: Path | None = None) -> Path:
    root = Path(store_dir or DEFAULT_INGESTION_LEARNING_STORE_DIR)
    slug = _slugify(pipeline_id)
    suffix = hashlib.sha256(str(pipeline_id or "").encode()).hexdigest()[:8]
    return root / f"{slug}__{suffix}.json"


def _extract_summary(run_payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "run_id": run_payload.get("run_id"),
        "pipeline_id": run_payload.get("pipeline_id"),
        "completed_at": run_payload.get("completed_at"),
        "status": run_payload.get("status"),
        "recommended_report_type": run_payload.get("recommended_report_type"),
        "report_type_trace": run_payload.get("report_type_trace", {}),
        "phase_self_evaluation_summary": run_payload.get("phase_self_evaluation_summary", {}),
        "evidence_maturity_summary": run_payload.get("evidence_maturity_summary", {}),
        "key_variable_bottlenecks": run_payload.get("key_variable_bottlenecks", []),
        "case_delta_summary": run_payload.get("case_delta_summary", {}),
        "source_yield_memory_summary": run_payload.get("source_yield_memory_summary", {}),
        "next_ingestion_priority_update": run_payload.get("next_ingestion_priority_update", {}),
        "ingestion_learning_summary": run_payload.get("ingestion_learning_summary", {}),
    }


def load_pipeline_learning_summary(
    pipeline_id: str,
    *,
    store_dir: Path | None = None,
) -> dict[str, Any]:
    path = _store_path(pipeline_id, store_dir)
    if not path.exists():
        return {}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}
    latest_summary = payload.get("latest_summary", {})
    return dict(latest_summary) if isinstance(latest_summary, dict) else {}


def save_pipeline_learning_summary(
    run_payload: dict[str, Any],
    *,
    store_dir: Path | None = None,
) -> Path | None:
    pipeline_id = str(run_payload.get("pipeline_id", "")).strip()
    run_id = str(run_payload.get("run_id", "")).strip()
    status = str(run_payload.get("status", "")).strip().lower()
    if not pipeline_id or not run_id or status == "running":
        return None

    path = _store_path(pipeline_id, store_dir)
    path.parent.mkdir(parents=True, exist_ok=True)
    try:
        existing = json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}
    except Exception:
        existing = {}

    latest_summary = _extract_summary(run_payload)
    history = list(existing.get("history", []) or [])
    history = [row for row in history if str(row.get("run_id", "")).strip() != run_id]
    history.insert(
        0,
        {
            "run_id": run_id,
            "completed_at": run_payload.get("completed_at"),
            "status": run_payload.get("status"),
            "recommended_report_type": run_payload.get("recommended_report_type"),
            "net_progress_state": (run_payload.get("ingestion_learning_summary", {}) or {}).get("net_progress_state", ""),
            "top_priority_action": (run_payload.get("ingestion_learning_summary", {}) or {}).get("top_priority_action", ""),
        },
    )

    payload = {
        "pipeline_id": pipeline_id,
        "latest_run_id": run_id,
        "updated_at": _now(),
        "latest_summary": latest_summary,
        "history": history[:_HISTORY_LIMIT],
    }
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return path
