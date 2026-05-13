"""Adapter for motor_063 — Chart Validity Engine (Layer F).

Implements Validator E of the new prompt RECOVERY_2026-05-09:

  > E. CHART VALIDITY ENGINE
  > Cada gráfico debe:
  >  - apoyar hipótesis;
  >  - apoyar combinación;
  >  - apoyar contradicción.
  > Si no: REMOVE CHART.

motor_018 already tags each chart asset with a `strategic_value_tier`
(thesis_critical / strategic_support / supportive_context / decorative_risk)
and a `chart_intelligence_binding`. This validator turns those signals
into actionable warnings:

  CV1 — Decorative-risk chart present (should be removed).
  CV2 — Chart with empty intelligence_binding (no thesis/combination link).
  CV3 — Decorative-risk ratio > 30% of total charts (contamination tier).
  CV4 — Chart count = 0 yet thesis is admissible (the report has no
        visual support — should at least carry one chart per active
        combination).

The validator emits warnings; downstream commits can wire them to
motor_017's render gate (similar to motor_036 can_render_pdf).
"""
from __future__ import annotations

from typing import Any

from .base import BaseMotorAdapter
from ..validator_severity_policy import effective_severity


_DECORATIVE_RATIO_CRITICAL = 0.30
_MIN_CHARTS_WHEN_THESIS_ACTIVE = 1


def _text(value: Any) -> str:
    return str(value or "").strip()


def _detect_decorative_risk(chart_assets: list[dict]) -> list[dict]:
    out: list[dict] = []
    for asset in chart_assets:
        if not isinstance(asset, dict):
            continue
        tier = _text(asset.get("strategic_value_tier"))
        if tier != "decorative_risk":
            continue
        out.append(
            {
                "rule_id": "CV1_decorative_risk_chart",
                "severity": "warning",
                "chart_id": _text(asset.get("chart_id") or asset.get("asset_id")),
                "strategic_value_tier": tier,
                "description": (
                    "Chart is tagged as decorative_risk by motor_018: it does not "
                    "support any active thesis, combination or contradiction. "
                    "Recommended action: remove from rendered report."
                ),
            }
        )
    return out


def _detect_unbound_charts(chart_assets: list[dict]) -> list[dict]:
    out: list[dict] = []
    for asset in chart_assets:
        if not isinstance(asset, dict):
            continue
        binding = asset.get("intelligence_binding") or asset.get("chart_intelligence_binding") or {}
        if not isinstance(binding, dict):
            binding = {}
        # A bound chart links to at least ONE of: thesis_anchor, combination_id,
        # contradiction_id, hypothesis_id.
        anchored = any(
            _text(binding.get(key))
            for key in (
                "thesis_anchor",
                "combination_id",
                "contradiction_id",
                "hypothesis_id",
            )
        )
        if anchored:
            continue
        chart_id = _text(asset.get("chart_id") or asset.get("asset_id"))
        if not chart_id:
            continue
        out.append(
            {
                "rule_id": "CV2_chart_without_intelligence_binding",
                "severity": "warning",
                "chart_id": chart_id,
                "description": (
                    "Chart has no intelligence_binding (no thesis, combination, "
                    "contradiction, or hypothesis anchor). It cannot be defended "
                    "as decision-relevant."
                ),
            }
        )
    return out


def _detect_decorative_ratio(
    chart_assets: list[dict],
    summary: dict,
) -> list[dict]:
    total = len(chart_assets)
    decorative = int(summary.get("decorative_risk_count", 0) or 0)
    if not decorative or total <= 0:
        return []
    ratio = decorative / total
    if ratio < _DECORATIVE_RATIO_CRITICAL:
        return []
    return [
        {
            "rule_id": "CV3_decorative_ratio_critical",
            "severity": "critical",
            "decorative_count": decorative,
            "total_charts": total,
            "ratio": round(ratio, 3),
            "threshold": _DECORATIVE_RATIO_CRITICAL,
            "description": (
                f"Decorative-risk charts make up {ratio:.0%} of the report "
                f"({decorative}/{total}). Above the {_DECORATIVE_RATIO_CRITICAL:.0%} "
                "threshold this is chart contamination — the report should be "
                "blocked until the offending charts are removed or rebound."
            ),
        }
    ]


def _detect_no_charts_with_active_thesis(
    chart_assets: list[dict],
    thesis_state: str,
) -> list[dict]:
    if len(chart_assets) >= _MIN_CHARTS_WHEN_THESIS_ACTIVE:
        return []
    admissible_states = {
        "admissible_structural_thesis",
        "conditional_structural_intelligence",
    }
    if thesis_state not in admissible_states:
        return []
    return [
        {
            "rule_id": "CV4_no_charts_with_admissible_thesis",
            "severity": "warning",
            "chart_count": len(chart_assets),
            "thesis_state": thesis_state,
            "description": (
                "Thesis is admissible but the report has no charts. At least "
                "one chart should anchor each active combination or "
                "contradiction."
            ),
        }
    ]


class Motor063Adapter(BaseMotorAdapter):
    @property
    def motor_id(self) -> str:
        return "motor_063"

    @property
    def input_motor_ids(self) -> list[str]:
        return ["motor_018", "motor_047"]

    def _run_impl(self, inputs: dict[str, Any]) -> dict[str, Any]:
        m018 = inputs.get("motor_018", {}) if isinstance(inputs.get("motor_018", {}), dict) else {}
        m047 = inputs.get("motor_047", {}) if isinstance(inputs.get("motor_047", {}), dict) else {}

        chart_assets = list(m018.get("chart_assets", []) or [])
        summary = dict(m018.get("chart_strategic_value_summary", {}) or {})
        thesis = m047.get("executive_thesis", {}) if isinstance(m047.get("executive_thesis", {}), dict) else {}
        thesis_state = _text(thesis.get("thesis_state"))

        warnings: list[dict] = []
        warnings.extend(_detect_decorative_risk(chart_assets))
        warnings.extend(_detect_unbound_charts(chart_assets))
        warnings.extend(_detect_decorative_ratio(chart_assets, summary))
        warnings.extend(_detect_no_charts_with_active_thesis(chart_assets, thesis_state))

        # V6 P4.2: apply validator_severity_policy gate. Soft mode keeps
        # the original severities; hard mode promotes CV1 and CV3 to "blocking".
        pipeline_inputs = inputs.get("__pipeline__", {}) if isinstance(inputs.get("__pipeline__", {}), dict) else {}
        for w in warnings:
            rid = str(w.get("rule_id", ""))
            sev = str(w.get("severity", "warning"))
            w["severity"] = effective_severity(
                self.motor_id, rid, sev, pipeline_inputs=pipeline_inputs
            )

        critical_count = sum(1 for w in warnings if w.get("severity") == "critical")
        blocking_count = sum(1 for w in warnings if w.get("severity") == "blocking")
        warning_count_pure = sum(1 for w in warnings if w.get("severity") == "warning")

        return {
            "chart_validity_warnings": warnings,
            "warning_count": len(warnings),
            "critical_count": critical_count,
            # V6 P4.2: surface counts for downstream qa_score consumer.
            "blocking_violations": blocking_count,
            "warning_violations": warning_count_pure,
            "chart_contamination_detected": (critical_count + blocking_count) > 0,
            "total_charts_evaluated": len(chart_assets),
            "rules_evaluated": [
                "CV1_decorative_risk_chart",
                "CV2_chart_without_intelligence_binding",
                "CV3_decorative_ratio_critical",
                "CV4_no_charts_with_admissible_thesis",
            ],
        }
