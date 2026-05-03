"""Adapter for motor_004 — Ingestion + Parsing Engine."""
from __future__ import annotations
import json
from datetime import datetime, timezone
from typing import Any

from ..asset_contracts import (
    derive_observable_clusters,
    derive_target_definition,
    missing_observable_clusters,
)
from .base import BaseMotorAdapter


class Motor004Adapter(BaseMotorAdapter):
    @property
    def motor_id(self) -> str:
        return "motor_004"

    @property
    def input_motor_ids(self) -> list[str]:
        return ["motor_001", "motor_002"]

    def _run_impl(self, inputs: dict[str, Any]) -> dict[str, Any]:
        pipeline = inputs.get("__pipeline__", {})
        sources = pipeline.get("sources", [])
        contracts = inputs.get("motor_001", {}).get("validated_contracts", [])
        target_definition_contract = inputs.get("motor_001", {}).get("target_definition_contract") or derive_target_definition(pipeline)
        produced_at = datetime.now(timezone.utc).isoformat()

        parsed_objects = []
        for src in sources:
            content = src.get("content", "")
            content_type = src.get("content_type", "text")
            source_id = src.get("source_id", "")

            parsed_content: Any = content
            if content_type == "json":
                try:
                    parsed_content = json.loads(content)
                except Exception:
                    parsed_content = content

            parsed_objects.append({
                "source_id": source_id,
                "content_type": content_type,
                "parsed_content": parsed_content,
                "metadata": src.get("metadata", {}),
                "phase_contract_refs": [c.get("phase_id") for c in contracts],
                "produced_by_motor": "motor_004",
                "produced_at": produced_at,
                "lineage_ref": f"lineage:{source_id}",
            })

        observable_clusters = derive_observable_clusters(pipeline, target_definition_contract)
        intake_observables = {
            "target_definition_contract": target_definition_contract,
            "observable_clusters": observable_clusters,
            "missing_observable_clusters": missing_observable_clusters(observable_clusters),
            "facility_inputs_present": list((pipeline.get("facility_inputs") or {}).keys()),
        }

        return {
            "parsed_objects": parsed_objects,
            "total_input": len(sources),
            "total_parsed": len(parsed_objects),
            "intake_observables": intake_observables,
        }
