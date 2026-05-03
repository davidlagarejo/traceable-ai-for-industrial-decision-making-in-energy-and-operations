"""Adapter for motor_010 — Scope-Preserving Duplicate Control Engine.

Deduplicates parsed and normalized objects conservatively:

- exact duplicates inside the same scope boundary are suppressed
- identical content across different scopes is preserved
- source scope, authority, family, and recency are propagated downstream
"""
from __future__ import annotations

import hashlib
from typing import Any

from .base import BaseMotorAdapter


def _normalized_content(obj: dict[str, Any]) -> str:
    content = obj.get("normalized_content", obj.get("parsed_content", ""))
    if isinstance(content, str):
        return content.strip()
    return str(content)


def _content_fingerprint(obj: dict[str, Any]) -> str:
    return hashlib.sha256(_normalized_content(obj).encode()).hexdigest()[:16]


def _jurisdiction_signature(obj: dict[str, Any]) -> str:
    metadata = obj.get("metadata", {}) if isinstance(obj.get("metadata", {}), dict) else {}
    jurisdiction = metadata.get("jurisdiction_code") or metadata.get("jurisdiction") or metadata.get("state")
    city = metadata.get("city") or metadata.get("locality") or ""
    return "|".join(part for part in [str(jurisdiction or "").strip().upper(), str(city or "").strip().upper()] if part)


def _boundary_signature(obj: dict[str, Any], source_profile: dict[str, Any]) -> str:
    return "|".join(
        [
            str(source_profile.get("scope", "")).strip().upper() or "UNKNOWN_SCOPE",
            str(source_profile.get("source_family", "")).strip().lower() or "unknown_family",
            str(source_profile.get("authority_score", "")).strip().lower() or "unknown_authority",
            _jurisdiction_signature(obj) or "unknown_jurisdiction",
        ]
    )


class Motor010Adapter(BaseMotorAdapter):
    @property
    def motor_id(self) -> str:
        return "motor_010"

    @property
    def input_motor_ids(self) -> list[str]:
        return ["motor_004", "motor_005", "motor_002", "motor_008"]

    def _run_impl(self, inputs: dict[str, Any]) -> dict[str, Any]:
        parsed = inputs.get("motor_004", {}).get("parsed_objects", [])
        normalized = inputs.get("motor_005", {}).get("normalized_objects", [])
        source_registry = inputs.get("motor_008", {}).get("source_registry", {})

        dedup_objects: list[dict[str, Any]] = []
        duplicate_report: list[dict[str, Any]] = []
        scope_conflict_report: list[dict[str, Any]] = []
        all_objects = normalized if normalized else parsed
        retained_by_fingerprint: dict[str, list[dict[str, Any]]] = {}

        for obj in all_objects:
            sid = obj.get("source_id", "")
            source_profile = source_registry.get(sid, {}) if isinstance(source_registry, dict) else {}
            content_fp = _content_fingerprint(obj)
            boundary = _boundary_signature(obj, source_profile)
            retained = retained_by_fingerprint.setdefault(content_fp, [])
            duplicate_of = next((row for row in retained if row["boundary"] == boundary), None)

            base_obj = {
                **obj,
                "dedup_fingerprint": content_fp,
                "source_scope": source_profile.get("scope", ""),
                "source_family": source_profile.get("source_family", ""),
                "source_authority_score": source_profile.get("authority_score", ""),
                "source_recency": source_profile.get("recency", ""),
                "boundary_signature": boundary,
                "produced_by_motor": "motor_010",
            }

            if duplicate_of:
                duplicate_report.append(
                    {
                        "source_id": sid,
                        "duplicate_of": duplicate_of["source_id"],
                        "fingerprint": content_fp,
                        "boundary_signature": boundary,
                        "source_scope": source_profile.get("scope", ""),
                        "action": "suppressed_exact_scope_duplicate",
                    }
                )
                continue

            dedup_status = "unique" if not retained else "scope_preserved_duplicate"
            if retained:
                scope_conflict_report.append(
                    {
                        "source_id": sid,
                        "fingerprint": content_fp,
                        "preserved_against": [row["source_id"] for row in retained],
                        "reason": "identical_content_but_distinct_scope_boundary",
                        "source_scope": source_profile.get("scope", ""),
                        "source_family": source_profile.get("source_family", ""),
                    }
                )
            dedup_objects.append(
                {
                    **base_obj,
                    "dedup_status": dedup_status,
                }
            )
            retained.append(
                {
                    "source_id": sid,
                    "boundary": boundary,
                }
            )

        return {
            "dedup_objects": dedup_objects,
            "duplicate_report": duplicate_report,
            "scope_conflict_report": scope_conflict_report,
            "total_input": len(all_objects),
            "total_unique": len(dedup_objects),
            "total_duplicates": len(duplicate_report),
            "total_scope_preserved": len(scope_conflict_report),
        }
