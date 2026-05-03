"""Adapter for motor_002 — Versioning + Lineage Engine.

Stamps every validated contract with version metadata and lineage fields.
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from .base import BaseMotorAdapter


class Motor002Adapter(BaseMotorAdapter):
    @property
    def motor_id(self) -> str:
        return "motor_002"

    @property
    def input_motor_ids(self) -> list[str]:
        return ["motor_001"]

    def _run_impl(self, inputs: dict[str, Any]) -> dict[str, Any]:
        contracts = inputs.get("motor_001", {}).get("validated_contracts", [])
        target_definition_contract = inputs.get("motor_001", {}).get("target_definition_contract", {})
        produced_at = datetime.now(timezone.utc).isoformat()

        versioned = []
        for obj in contracts:
            versioned.append({
                **obj,
                "version_id": f"v1:{obj.get('phase_id', '')}",
                "version_hash": f"hash:{obj.get('phase_id', '')}",
                "produced_by_motor": "motor_002",
                "produced_at": produced_at,
                "parent_id": None,
                "lineage_chain": [obj.get("phase_id", "")],
            })

        return {
            "versioned_objects": versioned,
            "total_versioned": len(versioned),
            "produced_at": produced_at,
            "target_definition_lineage": {
                "target_definition_contract": target_definition_contract,
                "version_id": f"v1:target:{target_definition_contract.get('target_identifier', 'unknown')}",
                "lineage_chain": [
                    target_definition_contract.get("target_scope", "unknown"),
                    target_definition_contract.get("target_type", "unknown"),
                ],
                "produced_at": produced_at,
            },
        }
