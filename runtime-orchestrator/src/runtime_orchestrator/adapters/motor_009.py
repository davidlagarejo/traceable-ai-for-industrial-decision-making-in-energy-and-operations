"""Adapter for motor_009 — Source Change Detection Engine.

Compares the registered source catalog (motor_008) against parsed objects
(motor_004) to detect new sources, changed content, and unchanged sources.
Produces change_detection_events for downstream deduplication.
"""
from __future__ import annotations

import hashlib
from datetime import datetime, timezone
from typing import Any

from .base import BaseMotorAdapter


def _content_hash(content: Any) -> str:
    s = content if isinstance(content, str) else str(content)
    return hashlib.sha256(s.encode()).hexdigest()[:16]


def _staleness_rows(source_registry: dict[str, Any], runtime: dict[str, Any]) -> list[dict[str, Any]]:
    rows = source_registry.get("crawler_staleness_report")
    if not isinstance(rows, list):
        rows = source_registry.get("staleness_report")
    if not isinstance(rows, list):
        rows = runtime.get("crawler_staleness_report")
    return list(rows) if isinstance(rows, list) else []


class Motor009Adapter(BaseMotorAdapter):
    @property
    def motor_id(self) -> str:
        return "motor_009"

    @property
    def input_motor_ids(self) -> list[str]:
        return ["motor_008", "motor_004", "motor_002"]

    def _run_impl(self, inputs: dict[str, Any]) -> dict[str, Any]:
        source_registry = inputs.get("motor_008", {}).get("source_registry", {})
        parsed_objects = inputs.get("motor_004", {}).get("parsed_objects", [])
        runtime = inputs.get("__runtime__", {}) if isinstance(inputs.get("__runtime__", {}), dict) else {}

        produced_at = datetime.now(timezone.utc).isoformat()

        known_sources = {
            entry["source_id"]: entry
            for entry in source_registry.get("all_sources", [])
        }
        parsed_source_ids: set[str] = set()

        events = []
        for obj in parsed_objects:
            sid = obj.get("source_id", "")
            if sid:
                parsed_source_ids.add(sid)
            content = obj.get("parsed_content", "")
            chash = _content_hash(content)

            if sid not in known_sources:
                change_type = "new"
            else:
                prev_hash = known_sources[sid].get("content_hash", "")
                change_type = "unchanged" if prev_hash == chash else "updated"

            events.append({
                "source_id": sid,
                "change_type": change_type,
                "content_hash": chash,
                "detected_at": produced_at,
                "produced_by_motor": "motor_009",
            })

        stale_count = 0
        disappeared_count = 0
        existing_event_source_ids = {str(event.get("source_id", "")).strip() for event in events if str(event.get("source_id", "")).strip()}
        for row in _staleness_rows(source_registry, runtime):
            source_id = str(row.get("source_id", "") or row.get("source_key", "")).strip()
            if not source_id or bool(row.get("fresh", True)) or source_id in existing_event_source_ids:
                continue
            if source_id in known_sources and source_id not in parsed_source_ids:
                change_type = "disappeared"
                disappeared_count += 1
            else:
                change_type = "stale"
                stale_count += 1
            events.append({
                "source_id": source_id,
                "change_type": change_type,
                "content_hash": str(known_sources.get(source_id, {}).get("content_hash", "")).strip(),
                "detected_at": produced_at,
                "produced_by_motor": "motor_009",
                "staleness_reason": change_type,
                "age_seconds": row.get("age_seconds"),
                "ttl_seconds": row.get("ttl_seconds"),
                "fresh": False,
            })

        new_count = sum(1 for e in events if e["change_type"] == "new")
        updated_count = sum(1 for e in events if e["change_type"] == "updated")

        return {
            "change_detection_events": events,
            "total_events": len(events),
            "new_sources": new_count,
            "updated_sources": updated_count,
            "stale_sources": stale_count,
            "disappeared_sources": disappeared_count,
            "unchanged_sources": max(len(events) - new_count - updated_count - stale_count - disappeared_count, 0),
            "produced_at": produced_at,
        }
