from __future__ import annotations

from typing import Any

from .schemas import text


def build_comparison_validity_register(
    *,
    fair_comparison_profile: dict[str, Any],
    normalization_requirements_register: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    asset_family = text(fair_comparison_profile.get("asset_family"))
    comparison_state = text(fair_comparison_profile.get("comparison_state"))
    if comparison_state == "inadmissible_until_asset_identity_bounded":
        return [
            {
                "subject": asset_family or "unbounded_target",
                "peer_frame": "any_peer_logic",
                "comparable": False,
                "why": "The asset is not bounded as an operating system, so peer logic is premature.",
                "normalization_required": ["bounded operating asset identity"],
                "invalid_comparison_risk": "critical",
                "evidence_state": "INADMISSIBLE_CLAIM",
            }
        ]

    rows: list[dict[str, Any]] = [
        {
            "subject": asset_family,
            "peer_frame": "same_family_and_process_screening_comparison",
            "comparable": comparison_state in {"bounded_screening_only", "partially_normalized", "archetypal_screening_only"},
            "why": (
                "Same-family screening comparison is admissible only as a bounded archetypal lens, not as local proof of superior or inferior economics."
                if comparison_state == "archetypal_screening_only"
                else "Same-family screening comparison is admissible only as a bounded lens, not as proof of superior or inferior economics."
            ),
            "normalization_required": ["asset family", "process type", "climate", "operating schedule"],
            "invalid_comparison_risk": "medium",
            "evidence_state": "ARCHETYPAL_PRIOR" if comparison_state == "archetypal_screening_only" else "CONDITIONAL_HYPOTHESIS",
        }
    ]

    if asset_family == "commercial_building":
        rows.append(
            {
                "subject": "commercial_building",
                "peer_frame": "whole_building_owner_capturable_comparison",
                "comparable": False,
                "why": "Whole-building comparisons are structurally invalid if owner burden and controllable load are not normalized together.",
                "normalization_required": ["owner / tenant control boundary", "tenant metering map", "schedule context"],
                "invalid_comparison_risk": "high",
                "evidence_state": "CONDITIONAL_HYPOTHESIS",
            }
        )
    if asset_family == "infrastructure_node":
        rows.append(
            {
                "subject": "infrastructure_node",
                "peer_frame": "node_energy_average_comparison",
                "comparable": False,
                "why": "Node-level energy comparisons are structurally invalid until service continuity burden, dispatch duty and redundancy class are normalized.",
                "normalization_required": ["service continuity", "dispatch burden", "redundancy class", "demand structure"],
                "invalid_comparison_risk": "critical",
                "evidence_state": "CONDITIONAL_HYPOTHESIS",
            }
        )
    if asset_family in {"industrial_manufacturing", "thermal_process_site", "utility_heavy_site"}:
        rows.append(
            {
                "subject": asset_family,
                "peer_frame": "area_based_energy_intensity_comparison",
                "comparable": False,
                "why": "Area-based energy comparison is structurally invalid until throughput or process duty is normalized.",
                "normalization_required": ["throughput by shift", "product mix or thermal duty", "operating schedule"],
                "invalid_comparison_risk": "critical",
                "evidence_state": "CONDITIONAL_HYPOTHESIS",
            }
        )
    if asset_family in {"logistics_warehouse", "cold_chain"}:
        rows.append(
            {
                "subject": asset_family,
                "peer_frame": "warehouse_area_only_comparison",
                "comparable": False,
                "why": "Service-level complexity, movement intensity, charging schedule and temperature duty can dominate area-based energy comparisons.",
                "normalization_required": ["service level", "throughput proxy", "dock activity profile", "charging schedule"],
                "invalid_comparison_risk": "critical",
                "evidence_state": "CONDITIONAL_HYPOTHESIS",
            }
        )

    _ = normalization_requirements_register
    return rows


def build_invalid_comparison_risk_register(
    *,
    fair_comparison_profile: dict[str, Any],
    comparison_validity_register: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for row in comparison_validity_register:
        if bool(row.get("comparable")):
            continue
        rows.append(
            {
                "risk_name": text(row.get("peer_frame")) or "invalid_comparison_risk",
                "risk_level": text(row.get("invalid_comparison_risk")) or "high",
                "trigger": text(row.get("why")),
                "blocked_claims": [
                    "peer_superiority",
                    "transferable_roi",
                    "local_waste_diagnosis_from_benchmark",
                ],
                "required_normalization": list(row.get("normalization_required", []) or []),
                "asset_family": text(fair_comparison_profile.get("asset_family")),
            }
        )
    return rows
