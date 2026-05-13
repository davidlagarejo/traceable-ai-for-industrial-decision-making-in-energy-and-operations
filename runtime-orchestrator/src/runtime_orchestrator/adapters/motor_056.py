"""Adapter for motor_056 — Evidence Repetition Validator (Layer F).

Detects when the same evidence pack is reused across too many TAD actions,
which produces the visible artefact in the Sunrise PDF where
"service-level proxy; dock activity profile; charging schedule" appears as
"Evidence Needed" in 5+ sections.

Rules:
  ER1 — Same evidence pack appears in more than 2 TAD actions.
  ER2 — Same `minimum_measurement` repeated across motor_046 register.
  ER3 — Empty evidence_needed in any actionable TAD action.
"""
from __future__ import annotations

from collections import Counter
from typing import Any

from .base import BaseMotorAdapter
from ..validator_severity_policy import effective_severity


def _text(value: Any) -> str:
    return str(value or "").strip()


def _normalize_pack(pack: Any) -> str:
    if isinstance(pack, list):
        return "; ".join(sorted(_text(item) for item in pack if _text(item)))
    return _text(pack)


def _detect_pack_repetition(actions: list[dict]) -> list[dict]:
    pack_counter: Counter = Counter()
    for action in actions:
        if not isinstance(action, dict):
            continue
        pack = _normalize_pack(action.get("evidence_needed"))
        if not pack:
            continue
        pack_counter[pack] += 1
    out: list[dict] = []
    for pack, count in pack_counter.items():
        if count > 2:
            out.append(
                {
                    "rule_id": "ER1_pack_repetition",
                    "severity": "warning",
                    "evidence_pack": pack,
                    "occurrences": count,
                    "description": (
                        "The same evidence pack is requested in more than 2 TAD actions. "
                        "Either the actions are not truly distinct, or the evidence "
                        "package is too generic to discriminate them."
                    ),
                }
            )
    return out


def _detect_minimum_measurement_repetition(min_evidence_register: list[dict]) -> list[dict]:
    counter: Counter = Counter()
    for row in min_evidence_register:
        if not isinstance(row, dict):
            continue
        measurement = _text(row.get("minimum_measurement") or row.get("minimum_evidence"))
        if not measurement:
            continue
        counter[measurement] += 1
    out: list[dict] = []
    for measurement, count in counter.items():
        if count > 1:
            out.append(
                {
                    "rule_id": "ER2_minimum_measurement_repetition",
                    "severity": "warning",
                    "minimum_measurement": measurement,
                    "occurrences": count,
                    "description": (
                        "Same minimum_measurement listed multiple times in the discrimination "
                        "register; downstream selection cannot prefer one over another."
                    ),
                }
            )
    return out


def _detect_empty_evidence_in_actionable(actions: list[dict]) -> list[dict]:
    actionable_statuses = {"ACT NOW", "VALIDATE FIRST"}
    out: list[dict] = []
    for action in actions:
        if not isinstance(action, dict):
            continue
        if _text(action.get("status")) not in actionable_statuses:
            continue
        if _normalize_pack(action.get("evidence_needed")):
            continue
        out.append(
            {
                "rule_id": "ER3_actionable_without_evidence_pack",
                "severity": "warning",
                "action": _text(action.get("action")),
                "status": _text(action.get("status")),
                "description": (
                    "Actionable TAD entry has no evidence pack; the reader cannot "
                    "tell what data unblocks the action."
                ),
            }
        )
    return out


class Motor056Adapter(BaseMotorAdapter):
    @property
    def motor_id(self) -> str:
        return "motor_056"

    @property
    def input_motor_ids(self) -> list[str]:
        return ["motor_033", "motor_046"]

    def _run_impl(self, inputs: dict[str, Any]) -> dict[str, Any]:
        m033 = inputs.get("motor_033", {}) if isinstance(inputs.get("motor_033", {}), dict) else {}
        m046 = inputs.get("motor_046", {}) if isinstance(inputs.get("motor_046", {}), dict) else {}

        actions = list(m033.get("expanded_structural_tad_action_register", []) or [])
        min_evidence = list(m046.get("minimum_evidence_for_discrimination_register", []) or [])

        warnings: list[dict] = []
        warnings.extend(_detect_pack_repetition(actions))
        warnings.extend(_detect_minimum_measurement_repetition(min_evidence))
        warnings.extend(_detect_empty_evidence_in_actionable(actions))

        # V6 P4.5: apply validator_severity_policy gate (soft-mode no-op).
        pipeline_inputs = inputs.get("__pipeline__", {}) if isinstance(inputs.get("__pipeline__", {}), dict) else {}
        for w in warnings:
            rid = str(w.get("rule_id", ""))
            sev = str(w.get("severity", "warning"))
            w["severity"] = effective_severity(
                self.motor_id, rid, sev, pipeline_inputs=pipeline_inputs
            )
        blocking_count = sum(1 for w in warnings if w.get("severity") == "blocking")
        warning_count_pure = sum(1 for w in warnings if w.get("severity") == "warning")

        return {
            "evidence_repetition_warnings": warnings,
            "warning_count": len(warnings),
            "blocking_violations": blocking_count,
            "warning_violations": warning_count_pure,
            "rules_evaluated": [
                "ER1_pack_repetition",
                "ER2_minimum_measurement_repetition",
                "ER3_actionable_without_evidence_pack",
            ],
        }
