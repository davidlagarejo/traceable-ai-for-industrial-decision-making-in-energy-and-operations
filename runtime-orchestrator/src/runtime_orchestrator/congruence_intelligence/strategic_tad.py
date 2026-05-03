from __future__ import annotations

from typing import Any

from .schemas import text


def _push(rows: list[dict[str, Any]], *, action: str, status: str, why: str, gold_nugget: str, evidence_needed: list[str], prohibited_action: str) -> None:
    rows.append(
        {
            "strategic_action": action,
            "status": status,
            "why": why,
            "gold_nugget": gold_nugget,
            "evidence_needed": list(evidence_needed or []),
            "prohibited_action": prohibited_action,
        }
    )


def build_congruence_action_priority_register(
    *,
    asset_family_research_profile: dict[str, Any],
    invalid_comparison_risk_register: list[dict[str, Any]],
    invalid_problem_frame_register: list[dict[str, Any]],
    measurement_strategy_register: list[dict[str, Any]],
    maintenance_reality_register: list[dict[str, Any]],
    finance_physics_dependency_register: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    if text(asset_family_research_profile.get("route_state")) != "operational_asset_candidate":
        return []

    rows: list[dict[str, Any]] = []
    if invalid_problem_frame_register:
        first = invalid_problem_frame_register[0]
        _push(
            rows,
            action="REQUEST_MINIMUM_EVIDENCE",
            status="VALIDATE FIRST",
            why=text(first.get("why_invalid_or_premature")),
            gold_nugget="You may be solving the wrong problem before the system is bounded.",
            evidence_needed=list(first.get("evidence_needed", []) or []),
            prohibited_action="Do not invest yet against the visible symptom alone.",
        )
    if invalid_comparison_risk_register:
        first = invalid_comparison_risk_register[0]
        _push(
            rows,
            action="REQUEST_FAIR_PEER_SET",
            status="COMPARE FAIRLY",
            why=text(first.get("trigger")),
            gold_nugget="A benchmark can be structurally invalid before any performance claim is made.",
            evidence_needed=list(first.get("required_normalization", []) or []),
            prohibited_action="Do not claim peer superiority or infer local waste from an invalid comparison.",
        )
    if measurement_strategy_register:
        first = measurement_strategy_register[0]
        _push(
            rows,
            action="MEASURE_ONLY_IF_MATERIAL",
            status="VALIDATE FIRST",
            why=text(first.get("why")),
            gold_nugget="The next best evidence may be cheaper and less invasive than expected.",
            evidence_needed=[text(first.get("minimum_measurement"))],
            prohibited_action=text(first.get("hardware_trigger")),
        )
    if any("maintenance maturity" in text(row.get("reality_claim")).lower() for row in maintenance_reality_register):
        _push(
            rows,
            action="REQUEST_MAINTENANCE_PROOF",
            status="VALIDATE FIRST",
            why="Maintenance evidence may decide whether the visible issue is utility waste, reliability risk or governance drift.",
            gold_nugget="The cheapest evidence gap may be organizational, not technical.",
            evidence_needed=["maintenance logs", "downtime records", "preventive maintenance proof"],
            prohibited_action="Do not treat maintenance as irrelevant just because energy is visible in bills.",
        )
    if finance_physics_dependency_register:
        first = finance_physics_dependency_register[0]
        _push(
            rows,
            action="DO_NOT_INVEST_YET",
            status="DO NOT INVEST YET",
            why=text(first.get("risk_if_wrong")),
            gold_nugget="The cost story is not bankable until the physical dependency is known.",
            evidence_needed=list(first.get("evidence_needed", []) or []),
            prohibited_action="Do not fund CAPEX on a still-unbounded economic boundary.",
        )
    return rows[:5]


def build_congruence_tad_enrichment_register(
    *,
    congruence_action_priority_register: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for row in congruence_action_priority_register:
        rows.append(
            {
                "action_family": text(row.get("strategic_action")),
                "recommended_posture": text(row.get("status")),
                "evidence_pack": list(row.get("evidence_needed", []) or []),
                "no_go_condition": text(row.get("prohibited_action")),
            }
        )
    return rows


def _expanded_push(
    rows: list[dict[str, Any]],
    *,
    action: str,
    status: str,
    trigger: str,
    why: str,
    evidence_needed: list[str],
    prohibited_action: str,
) -> None:
    rows.append(
        {
            "strategic_action": action,
            "status": status,
            "trigger": trigger,
            "why": why,
            "evidence_needed": list(evidence_needed or []),
            "prohibited_action": prohibited_action,
        }
    )


def build_expanded_tad_action_register(
    *,
    asset_family_research_profile: dict[str, Any],
    gap_taxonomy_register: list[dict[str, Any]],
    evidence_need_class_register: list[dict[str, Any]],
    comparison_not_yet_valid_register: list[dict[str, Any]],
    activated_pattern_register: list[dict[str, Any]],
    financial_exposure_type_register: list[dict[str, Any]],
    measurement_strategy_register: list[dict[str, Any]],
    claim_impact_register: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    if text(asset_family_research_profile.get("route_state")) != "operational_asset_candidate":
        return []

    rows: list[dict[str, Any]] = []

    if any(text(row.get("gap_class")) in {"missing_data", "missing_identity_resolution", "missing_operational_context"} for row in gap_taxonomy_register):
        first = next(
            row for row in gap_taxonomy_register
            if text(row.get("gap_class")) in {"missing_data", "missing_identity_resolution", "missing_operational_context"}
        )
        _expanded_push(
            rows,
            action="REQUEST_MINIMUM_EVIDENCE",
            status="ACT NOW",
            trigger=text(first.get("gap_class")),
            why=text(first.get("why_blocked")),
            evidence_needed=list(first.get("evidence_needed", []) or []),
            prohibited_action="Do not harden the visible story before the minimum discriminating evidence exists.",
        )

    if comparison_not_yet_valid_register or any(text(row.get("evidence_need_class")) == "missing_comparability" for row in evidence_need_class_register):
        first = (comparison_not_yet_valid_register or [{}])[0]
        _expanded_push(
            rows,
            action="BUILD_FAIR_PEER_SET",
            status="ACT NOW",
            trigger="missing_comparability",
            why=text(first.get("explanation")) or "Peer logic is structurally invalid until comparison requirements are met.",
            evidence_needed=list(first.get("required_before_comparison", []) or []),
            prohibited_action="Do not claim peer superiority or transferable ROI from an invalid comparison.",
        )

    tariff_exposure = next(
        (row for row in financial_exposure_type_register if text(row.get("financial_exposure_type")) in {"tariff_exposure_hidden", "demand_charge_exposure"}),
        None,
    )
    if tariff_exposure:
        _expanded_push(
            rows,
            action="VALIDATE_TARIFF_EXPOSURE",
            status="ACT NOW",
            trigger=text(tariff_exposure.get("financial_exposure_type")),
            why=text(tariff_exposure.get("why_it_matters")),
            evidence_needed=list(tariff_exposure.get("evidence_needed", []) or []),
            prohibited_action="Do not underwrite generic efficiency retrofit logic before tariff exposure is bounded.",
        )

    control_exposure = next(
        (row for row in financial_exposure_type_register if text(row.get("financial_exposure_type")) in {"operational_savings_not_capturable", "tenant_operator_value_leakage"}),
        None,
    )
    if control_exposure:
        _expanded_push(
            rows,
            action="VALIDATE_CONTROL_BOUNDARY",
            status="ACT NOW",
            trigger=text(control_exposure.get("financial_exposure_type")),
            why=text(control_exposure.get("why_it_matters")),
            evidence_needed=list(control_exposure.get("evidence_needed", []) or []),
            prohibited_action="Do not present owner-capturable ROI or retrofit logic until the boundary is evidenced.",
        )

    if activated_pattern_register:
        first = activated_pattern_register[0]
        _expanded_push(
            rows,
            action="VALIDATE_LOSS_PATTERN",
            status="ACT NOW",
            trigger=text(first.get("pattern_name")),
            why=text(first.get("why_plausible")),
            evidence_needed=[],
            prohibited_action="Do not state the activated pattern as observed fact without confirming evidence.",
        )

    maintenance_exposure = next(
        (row for row in financial_exposure_type_register if text(row.get("financial_exposure_type")) == "maintenance_downtime_exposure"),
        None,
    )
    if maintenance_exposure:
        _expanded_push(
            rows,
            action="VALIDATE_MAINTENANCE_REALITY",
            status="ACT NOW",
            trigger="maintenance_downtime_exposure",
            why=text(maintenance_exposure.get("why_it_matters")),
            evidence_needed=list(maintenance_exposure.get("evidence_needed", []) or []),
            prohibited_action="Do not treat maintenance as secondary until downtime economics are bounded.",
        )

    if any(text(row.get("financial_exposure_type")) == "over_modeling_cost" for row in financial_exposure_type_register):
        _expanded_push(
            rows,
            action="DO_NOT_MODEL_YET",
            status="DO NOT MODEL YET",
            trigger="over_modeling_cost",
            why="A model can precisely model the wrong system before the dominant variable is discriminated.",
            evidence_needed=["minimum discriminating evidence"],
            prohibited_action="Do not build a digital twin yet.",
        )

    if measurement_strategy_register:
        first = measurement_strategy_register[0]
        _expanded_push(
            rows,
            action="DO_NOT_SENSOR_YET",
            status="DO NOT SENSOR YET",
            trigger=text(first.get("hypothesis")),
            why=text(first.get("why")),
            evidence_needed=[text(first.get("minimum_measurement"))],
            prohibited_action=text(first.get("hardware_trigger")) or "Do not deploy broad sensing before hypothesis discrimination.",
        )

    if any(text(row.get("financial_exposure_type")) in {"CAPEX_misallocated", "wrong_retrofit_sequencing"} for row in financial_exposure_type_register):
        _expanded_push(
            rows,
            action="DO_NOT_INVEST_YET",
            status="DO NOT INVEST YET",
            trigger="capital sequencing still unbounded",
            why="Capital can be allocated against a secondary symptom before the physical and economic boundary is known.",
            evidence_needed=["physical dependency evidence", "fair comparison basis", "minimum measurement path"],
            prohibited_action="Do not fund irreversible CAPEX on a still-unbounded economic boundary.",
        )

    if claim_impact_register:
        first = claim_impact_register[0]
        _expanded_push(
            rows,
            action="PROHIBIT_CLAIM",
            status="PROHIBIT CLAIM",
            trigger=text(first.get("hypothesis_it_discriminates")),
            why=text(first.get("claim_impact")),
            evidence_needed=list(first.get("evidence_needed", []) or []),
            prohibited_action="Do not promote the blocked claim before the discriminating evidence arrives.",
        )

    return rows[:12]


def build_prohibited_action_register(
    *,
    expanded_tad_action_register: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    return [
        {
            "strategic_action": text(row.get("strategic_action")),
            "status": text(row.get("status")),
            "prohibited_action": text(row.get("prohibited_action")),
        }
        for row in list(expanded_tad_action_register or [])
        if text(row.get("strategic_action"))
    ]
