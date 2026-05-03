"""Adapter for motor_022 — Evaluation / Conformance Engine.

Builds a formal conformance verdict from the harness and the sovereign subject
and readiness gates. This is intentionally narrow: it checks whether the
pipeline is allowed to call the current product what it is calling it.
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from .base import BaseMotorAdapter


def _violation(
    rule_id: str,
    description: str,
    output_id: str,
    severity: str = "error",
    evidence: dict[str, Any] | None = None,
) -> dict[str, Any]:
    return {
        "rule_id": rule_id,
        "description": description,
        "output_id": output_id,
        "severity": severity,
        "evidence": evidence or {},
    }


class Motor022Adapter(BaseMotorAdapter):
    @property
    def motor_id(self) -> str:
        return "motor_022"

    @property
    def input_motor_ids(self) -> list[str]:
        return ["motor_001", "motor_002", "motor_007", "motor_021"]

    def _run_impl(self, inputs: dict[str, Any]) -> dict[str, Any]:
        produced_at = datetime.now(timezone.utc).isoformat()
        m01 = inputs.get("motor_001", {})
        m07 = inputs.get("motor_007", {})
        m21 = inputs.get("motor_021", {})

        violations: list[dict[str, Any]] = []
        rule_results: list[dict[str, Any]] = []

        harness_passed = bool(m21.get("harness_passed", False))
        harness_summary = m21.get("harness_summary", {})
        if harness_passed:
            rule_results.append({
                "rule_id": "harness_core_contracts",
                "status": "pass",
                "description": "Core contracts passed the harness checks.",
                "evidence": harness_summary,
            })
        else:
            rule_results.append({
                "rule_id": "harness_core_contracts",
                "status": "fail",
                "description": "Core contracts failed the harness checks.",
                "evidence": harness_summary,
            })
            violations.append(_violation(
                "harness_core_contracts",
                "Core subject/target/readiness contracts failed the object harness.",
                "__pipeline__",
                evidence=harness_summary,
            ))

        allowed_report_classes = m07.get("allowed_report_classes", [])
        report_identity_state = m07.get("report_identity_state", "")
        if allowed_report_classes and report_identity_state in allowed_report_classes:
            rule_results.append({
                "rule_id": "report_identity_allowed_by_subject_gate",
                "status": "pass",
                "description": "Current report identity stays within the subject gate allowed classes.",
                "evidence": {
                    "report_identity_state": report_identity_state,
                    "allowed_report_classes": allowed_report_classes,
                },
            })
        else:
            rule_results.append({
                "rule_id": "report_identity_allowed_by_subject_gate",
                "status": "fail",
                "description": "Current report identity exceeds the subject gate allowed classes.",
                "evidence": {
                    "report_identity_state": report_identity_state,
                    "allowed_report_classes": allowed_report_classes,
                },
            })
            violations.extend([
                _violation(
                    "report_identity_allowed_by_subject_gate",
                    "Report identity exceeds classes allowed by the current subject admissibility state.",
                    "report_package",
                    evidence={
                        "report_identity_state": report_identity_state,
                        "allowed_report_classes": allowed_report_classes,
                    },
                ),
                _violation(
                    "report_identity_allowed_by_subject_gate",
                    "PDF export exceeds classes allowed by the current subject admissibility state.",
                    "pdf_output",
                    evidence={
                        "report_identity_state": report_identity_state,
                        "allowed_report_classes": allowed_report_classes,
                    },
                ),
            ])

        target_admissibility_state = m07.get("target_admissibility_state", "")
        asset_context_readiness = m07.get("asset_context_readiness", "")
        if target_admissibility_state in {"address_candidate_only", "site_candidate_only"} and report_identity_state in {
            "TDIR Preliminary",
            "Decision-Grade TDIR",
        }:
            rule_results.append({
                "rule_id": "blocked_subject_cannot_render_full_tdir",
                "status": "fail",
                "description": "Blocked subject state cannot render a full TDIR-class report.",
                "evidence": {
                    "target_admissibility_state": target_admissibility_state,
                    "report_identity_state": report_identity_state,
                    "asset_context_readiness": asset_context_readiness,
                },
            })
            violations.append(_violation(
                "blocked_subject_cannot_render_full_tdir",
                "Blocked subject state attempted to render a TDIR-class output.",
                "report_package",
                evidence={
                    "target_admissibility_state": target_admissibility_state,
                    "report_identity_state": report_identity_state,
                    "asset_context_readiness": asset_context_readiness,
                },
            ))
        else:
            rule_results.append({
                "rule_id": "blocked_subject_cannot_render_full_tdir",
                "status": "pass",
                "description": "Blocked subject state is not over-claiming document class.",
                "evidence": {
                    "target_admissibility_state": target_admissibility_state,
                    "report_identity_state": report_identity_state,
                },
            })

        return {
            "produced_at": produced_at,
            "conformance_passed": len(violations) == 0,
            "conformance_violation_count": len(violations),
            "conformance_violations": violations,
            "rule_results": rule_results,
            "summary": {
                "target_admissibility_state": target_admissibility_state,
                "asset_context_readiness": asset_context_readiness,
                "report_identity_state": report_identity_state,
                "allowed_report_classes": allowed_report_classes,
            },
        }
