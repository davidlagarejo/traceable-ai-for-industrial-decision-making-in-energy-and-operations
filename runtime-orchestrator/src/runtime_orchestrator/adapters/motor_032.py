"""Adapter for motor_032 — Synthetic ML Decision Support Integration."""
from __future__ import annotations

import hashlib
from datetime import datetime, timezone
from typing import Any

from .base import BaseMotorAdapter


def _stable_id(prefix: str, raw: str) -> str:
    return f"{prefix}:" + hashlib.sha256(raw.encode()).hexdigest()[:12]


class Motor032Adapter(BaseMotorAdapter):
    @property
    def motor_id(self) -> str:
        return "motor_032"

    @property
    def input_motor_ids(self) -> list[str]:
        return ["motor_031", "motor_014", "motor_001", "motor_002"]

    def _run_impl(self, inputs: dict[str, Any]) -> dict[str, Any]:
        produced_at = datetime.now(timezone.utc).isoformat()
        reports = inputs.get("motor_031", {}).get("capability_demonstration_reports", [])
        inference_records = {
            record.get("case_id", ""): record
            for record in inputs.get("motor_014", {}).get("inference_records", [])
        }

        support_register: list[dict[str, Any]] = []
        hypothesis_signals: list[dict[str, Any]] = []
        labeled_support_records: list[dict[str, Any]] = []

        for report in reports:
            case_id = str(report.get("source_problem_ref", "")).strip()
            inference_record = inference_records.get(case_id, {})
            has_demonstrated_capability = bool(report.get("selected_model"))
            support_level = (
                "preliminary_signal" if has_demonstrated_capability else "capability_demo"
            )
            signal_direction = (
                "prioritize_validation" if has_demonstrated_capability else "hold_for_real_evidence"
            )
            support_id = _stable_id("synsup", f"{case_id}:{report.get('report_id', '')}")
            cannot_substitute = [
                "validation_data_bridge",
                "verification_bridge",
                "field_evidence",
                "final_tad_decision",
            ]
            support_register.append(
                {
                    "support_id": support_id,
                    "source_problem_ref": case_id,
                    "expert_spec_ref": report.get("expert_spec_ref", ""),
                    "synthetic_support_flag": True,
                    "non_evidentiary_flag": True,
                    "intended_use": "preliminary_support",
                    "domain_validity_limits": report.get("domain_validity_limits", ""),
                    "limitations_note": report.get("limitations_note", ""),
                    "support_level": support_level,
                    "cannot_substitute": cannot_substitute,
                    "selected_model": report.get("selected_model"),
                    "decision_core_weight": 0.15 if has_demonstrated_capability else 0.05,
                    "rank_is_preliminary": True,
                }
            )
            hypothesis_signals.append(
                {
                    "signal_id": _stable_id("hypsig", support_id),
                    "source_problem_ref": case_id,
                    "signal_direction": signal_direction,
                    "signal_basis": (
                        "Synthetic capability demo suggests this case benefits from structured validation ordering."
                        if has_demonstrated_capability
                        else "Synthetic capability was not demonstrated strongly enough to influence ordering."
                    ),
                    "synthetic_support_flag": True,
                    "non_evidentiary_flag": True,
                    "intended_use": "preliminary_support",
                    "domain_validity_limits": report.get("domain_validity_limits", ""),
                    "limitations_note": report.get("limitations_note", ""),
                }
            )
            labeled_support_records.append(
                {
                    "record_id": _stable_id("labsup", support_id),
                    "source_problem_ref": case_id,
                    "case_name": inference_record.get("case_name", ""),
                    "claim_family": inference_record.get("claim_family", ""),
                    "support_level": support_level,
                    "recommended_effect": signal_direction,
                    "synthetic_support_flag": True,
                    "non_evidentiary_flag": True,
                    "intended_use": "preliminary_support",
                    "domain_validity_limits": report.get("domain_validity_limits", ""),
                    "limitations_note": report.get("limitations_note", ""),
                    "cannot_substitute": cannot_substitute,
                }
            )

        return {
            "produced_at": produced_at,
            "synthetic_ml_support_register": support_register,
            "hypothesis_signal": hypothesis_signals[0] if hypothesis_signals else {},
            "hypothesis_signals": hypothesis_signals,
            "labeled_support_record": labeled_support_records[0] if labeled_support_records else {},
            "labeled_support_records": labeled_support_records,
            "summary": {
                "support_record_count": len(support_register),
                "preliminary_signal_count": len([item for item in support_register if item["support_level"] == "preliminary_signal"]),
                "capability_demo_count": len([item for item in support_register if item["support_level"] == "capability_demo"]),
            },
        }
