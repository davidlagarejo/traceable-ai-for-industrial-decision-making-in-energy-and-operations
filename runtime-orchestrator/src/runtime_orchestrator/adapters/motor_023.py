"""Adapter for motor_023 — Pipeline Orchestration + Observability Engine."""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from .base import BaseMotorAdapter


class Motor023Adapter(BaseMotorAdapter):
    @property
    def motor_id(self) -> str:
        return "motor_023"

    @property
    def input_motor_ids(self) -> list[str]:
        return ["motor_001"]

    def _run_impl(self, inputs: dict[str, Any]) -> dict[str, Any]:
        produced_at = datetime.now(timezone.utc).isoformat()
        runtime = inputs.get("__runtime__", {}) if isinstance(inputs.get("__runtime__", {}), dict) else {}
        pipeline = inputs.get("__pipeline__", {}) if isinstance(inputs.get("__pipeline__", {}), dict) else {}
        m01 = inputs.get("motor_001", {})

        subject_definition = m01.get("subject_definition_contract", runtime.get("subject_definition", {}))
        target_definition = m01.get("target_definition_contract", runtime.get("target_definition", {}))
        run_control = pipeline.get("__run_control__", {}) if isinstance(pipeline.get("__run_control__", {}), dict) else {}

        launch_contract = {
            "pipeline_id": runtime.get("pipeline_id", ""),
            "case_id": pipeline.get("case_id", ""),
            "target_id": target_definition.get("target_id", ""),
            "target_type": target_definition.get("target_type", ""),
            "subject_kind": subject_definition.get("subject_kind", ""),
            "case_mode": target_definition.get("case_mode", ""),
            "force_refresh_token": run_control.get("force_refresh_token", ""),
        }

        observability_snapshot = {
            "run_started_at": runtime.get("started_at", ""),
            "truth_summary": runtime.get("truth_summary", {}),
            "subject_contract_status": runtime.get("subject_contract_status", ""),
            "subject_contract_admissibility": runtime.get("subject_contract_admissibility", ""),
        }

        return {
            "produced_at": produced_at,
            "launch_contract": launch_contract,
            "pipeline_observability_snapshot": observability_snapshot,
            "summary": {
                "pipeline_id": launch_contract["pipeline_id"],
                "target_id": launch_contract["target_id"],
                "subject_kind": launch_contract["subject_kind"],
                "case_mode": launch_contract["case_mode"],
            },
        }
