"""Adapter for motor_021 — Dataset / Object Test Harness Engine.

Runs lightweight structural checks over the core subject/target/identity/readiness
objects before downstream governance consumes them.
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from .base import BaseMotorAdapter


def _result(
    object_id: str,
    check_id: str,
    status: str,
    severity: str,
    description: str,
    evidence: dict[str, Any] | None = None,
) -> dict[str, Any]:
    return {
        "object_id": object_id,
        "check_id": check_id,
        "status": status,
        "severity": severity,
        "description": description,
        "evidence": evidence or {},
    }


class Motor021Adapter(BaseMotorAdapter):
    @property
    def motor_id(self) -> str:
        return "motor_021"

    @property
    def input_motor_ids(self) -> list[str]:
        return ["motor_001", "motor_002", "motor_003", "motor_005", "motor_006", "motor_007"]

    def _run_impl(self, inputs: dict[str, Any]) -> dict[str, Any]:
        produced_at = datetime.now(timezone.utc).isoformat()
        m01 = inputs.get("motor_001", {})
        m03 = inputs.get("motor_003", {})
        m05 = inputs.get("motor_005", {})
        m06 = inputs.get("motor_006", {}).get("asset_identity_resolution", {})
        m07 = inputs.get("motor_007", {})

        results: list[dict[str, Any]] = []

        subject_contract = m01.get("subject_definition_contract", {})
        target_contract = m03.get("target_definition_contract", {}) or m01.get("target_definition_contract", {})

        if subject_contract.get("subject_kind"):
            results.append(_result(
                "subject_definition_contract",
                "subject_kind_declared",
                "pass",
                "info",
                "Subject contract declares a subject_kind.",
                {"subject_kind": subject_contract.get("subject_kind")},
            ))
        else:
            results.append(_result(
                "subject_definition_contract",
                "subject_kind_declared",
                "fail",
                "error",
                "Subject contract is missing subject_kind.",
            ))

        if target_contract.get("target_id") and target_contract.get("target_type"):
            results.append(_result(
                "target_definition_contract",
                "target_identity_materialized",
                "pass",
                "info",
                "Target contract materialized target_id and target_type.",
                {
                    "target_id": target_contract.get("target_id"),
                    "target_type": target_contract.get("target_type"),
                },
            ))
        else:
            results.append(_result(
                "target_definition_contract",
                "target_identity_materialized",
                "fail",
                "error",
                "Target contract did not materialize target_id and target_type.",
            ))

        if m06.get("subject_resolution_state"):
            results.append(_result(
                "asset_identity_resolution",
                "subject_resolution_present",
                "pass",
                "info",
                "Asset identity resolution emitted a subject_resolution_state.",
                {"subject_resolution_state": m06.get("subject_resolution_state")},
            ))
        else:
            results.append(_result(
                "asset_identity_resolution",
                "subject_resolution_present",
                "fail",
                "error",
                "Asset identity resolution did not emit subject_resolution_state.",
            ))

        if m07.get("asset_context_readiness") and m07.get("report_identity_state"):
            results.append(_result(
                "asset_context_gate",
                "readiness_and_report_identity_present",
                "pass",
                "info",
                "Asset context gate emitted readiness and report identity.",
                {
                    "asset_context_readiness": m07.get("asset_context_readiness"),
                    "report_identity_state": m07.get("report_identity_state"),
                },
            ))
        else:
            results.append(_result(
                "asset_context_gate",
                "readiness_and_report_identity_present",
                "fail",
                "error",
                "Asset context gate is missing readiness or report identity state.",
            ))

        if not m05.get("__stub__"):
            results.append(_result(
                "normalized_intake",
                "normalized_payload_present",
                "pass",
                "info",
                "Normalized intake object is present as a real adapter output.",
            ))
        else:
            results.append(_result(
                "normalized_intake",
                "normalized_payload_present",
                "warn",
                "warning",
                "Normalized intake object came from a stub or placeholder path.",
            ))

        errors = sum(1 for r in results if r["severity"] == "error")
        warnings = sum(1 for r in results if r["severity"] == "warning")
        harness_passed = errors == 0

        return {
            "produced_at": produced_at,
            "harness_passed": harness_passed,
            "object_contract_results": results,
            "harness_summary": {
                "total_checks": len(results),
                "errors": errors,
                "warnings": warnings,
                "passes": len(results) - errors - warnings,
            },
        }
