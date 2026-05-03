"""Adapter for motor_026 — Access Control / Execution Policy Layer.

Builds a lightweight execution-policy surface from the declared source registry,
the target contract, and the launch context. This is intentionally operational:
it does not decide truth, only what kinds of source handling are admissible.
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from .base import BaseMotorAdapter


def _access_tier(entry: dict[str, Any]) -> str:
    metadata = entry.get("metadata", {}) if isinstance(entry.get("metadata", {}), dict) else {}
    if metadata.get("premium") or metadata.get("license_required"):
        return "restricted"
    if entry.get("needs_fetch"):
        return "managed_fetch"
    return "direct_read"


def _allowed_actions(entry: dict[str, Any]) -> list[str]:
    actions = ["trace"]
    if entry.get("has_content"):
        actions.extend(["read", "cite_as_context"])
    if entry.get("needs_fetch"):
        actions.append("fetch")
    if entry.get("authoritative"):
        actions.append("use_as_authoritative_context")
    return actions


class Motor026Adapter(BaseMotorAdapter):
    @property
    def motor_id(self) -> str:
        return "motor_026"

    @property
    def input_motor_ids(self) -> list[str]:
        return ["motor_001", "motor_008", "motor_023"]

    def _run_impl(self, inputs: dict[str, Any]) -> dict[str, Any]:
        produced_at = datetime.now(timezone.utc).isoformat()
        m01 = inputs.get("motor_001", {})
        m08 = inputs.get("motor_008", {})
        m23 = inputs.get("motor_023", {})

        subject_contract = m01.get("subject_definition_contract", {})
        target_contract = m01.get("target_definition_contract", {})
        launch_contract = m23.get("launch_contract", {})
        source_registry = m08.get("source_registry", {})

        source_access_matrix: list[dict[str, Any]] = []
        restricted_count = 0
        fetch_count = 0

        for source_id, entry in sorted(source_registry.items()):
            access_tier = _access_tier(entry)
            if access_tier == "restricted":
                restricted_count += 1
            if entry.get("needs_fetch"):
                fetch_count += 1
            source_access_matrix.append(
                {
                    "source_id": source_id,
                    "access_tier": access_tier,
                    "allowed_actions": _allowed_actions(entry),
                    "authoritative": bool(entry.get("authoritative", False)),
                    "needs_fetch": bool(entry.get("needs_fetch", False)),
                    "content_type": entry.get("content_type", ""),
                    "fetch_type": entry.get("fetch_type", ""),
                    "scope_boundary": (
                        entry.get("metadata", {}).get("source_scope")
                        or entry.get("metadata", {}).get("context_role")
                        or "declared_source"
                    ),
                }
            )

        execution_policy_register = [
            {
                "policy_id": "POL-001-declared-source-only-fetch",
                "status": "enforced",
                "description": "Only declared sources may be fetched by the runtime.",
                "evidence": {
                    "total_declared_sources": len(source_registry),
                    "sources_requiring_fetch": fetch_count,
                },
            },
            {
                "policy_id": "POL-002-issuer-context-cannot-close-asset-claims",
                "status": "enforced",
                "description": "Issuer-level context remains subordinate for asset-scoped cases.",
                "evidence": {
                    "subject_kind": subject_contract.get("subject_kind", ""),
                    "target_scope": target_contract.get("target_scope", ""),
                    "subject_contract_admissibility": m01.get("subject_contract_admissibility", ""),
                },
            },
            {
                "policy_id": "POL-003-delivery-requires-governance",
                "status": "enforced",
                "description": "Execution policy recognizes that downstream delivery remains governed and conditional.",
                "evidence": {
                    "pipeline_id": launch_contract.get("pipeline_id", ""),
                    "target_id": launch_contract.get("target_id", ""),
                    "case_mode": launch_contract.get("case_mode", ""),
                },
            },
        ]

        return {
            "produced_at": produced_at,
            "execution_policy_register": execution_policy_register,
            "source_access_matrix": source_access_matrix,
            "policy_summary": {
                "pipeline_id": launch_contract.get("pipeline_id", ""),
                "target_id": launch_contract.get("target_id", ""),
                "subject_kind": subject_contract.get("subject_kind", ""),
                "target_scope": target_contract.get("target_scope", ""),
                "total_sources": len(source_access_matrix),
                "sources_requiring_fetch": fetch_count,
                "restricted_sources": restricted_count,
            },
        }
