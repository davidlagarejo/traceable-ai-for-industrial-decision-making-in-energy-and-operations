from __future__ import annotations

from typing import Any

from .schemas import text


def _allows_conditional_archetypal_intelligence(
    asset_family_research_profile: dict[str, Any],
) -> bool:
    route_state = text(asset_family_research_profile.get("route_state"))
    asset_family = text(asset_family_research_profile.get("asset_family"))
    return route_state == "operational_asset_candidate" or (
        route_state == "target_not_yet_operationally_bounded"
        and bool(asset_family)
        and asset_family != "generic_operational_asset"
    )


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
    if not _allows_conditional_archetypal_intelligence(asset_family_research_profile):
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
    financial_exposure: str = "",
) -> None:
    normalized_action = text(action)
    trigger_text = text(trigger)
    prohibited_action_text = text(prohibited_action)
    financial_exposure_text = text(financial_exposure)
    decision_front = {
        "REQUEST_MINIMUM_EVIDENCE": "REQUEST MINIMUM EVIDENCE",
        "BUILD_FAIR_PEER_SET": "BUILD FAIR PEER SET",
        "VALIDATE_TARIFF_EXPOSURE": "VALIDATE DEMAND / TARIFF EXPOSURE",
        "VALIDATE_CONTROL_BOUNDARY": "VALIDATE CONTROL BOUNDARY",
        "VALIDATE_LOSS_PATTERN": "VALIDATE STRUCTURAL LOSS HYPOTHESIS",
        "VALIDATE_MAINTENANCE_REALITY": "VALIDATE MAINTENANCE REALITY",
        "DO_NOT_MODEL_YET": "DO NOT MODEL YET",
        "DO_NOT_SENSOR_YET": "DO NOT SENSOR YET",
        "DO_NOT_INVEST_YET": "DO NOT UNDERWRITE YET",
        "PROHIBIT_CLAIM": "PROHIBIT PREMATURE CLAIM",
    }.get(normalized_action, normalized_action.replace("_", " "))
    trigger_family = (
        "comparison_failure"
        if "compar" in trigger_text.lower() or normalized_action == "BUILD_FAIR_PEER_SET"
        else "boundary_failure"
        if "boundary" in trigger_text.lower() or normalized_action == "VALIDATE_CONTROL_BOUNDARY"
        else "tariff_or_demand"
        if any(token in trigger_text.lower() for token in ("tariff", "demand", "peak", "power factor", "reactive"))
        or normalized_action == "VALIDATE_TARIFF_EXPOSURE"
        else "maintenance_reality"
        if "maintenance" in trigger_text.lower() or normalized_action == "VALIDATE_MAINTENANCE_REALITY"
        else "measurement_path"
        if normalized_action in {"DO_NOT_SENSOR_YET", "REQUEST_MINIMUM_EVIDENCE"}
        else "model_prematurity"
        if normalized_action == "DO_NOT_MODEL_YET"
        else "capital_risk"
        if normalized_action == "DO_NOT_INVEST_YET"
        else "claim_governance"
        if normalized_action == "PROHIBIT_CLAIM"
        else "pattern_falsification"
        if normalized_action == "VALIDATE_LOSS_PATTERN"
        else "general"
    )
    prohibited_action_class = (
        "peer_superiority_block"
        if "peer superiority" in prohibited_action_text.lower()
        else "roi_or_transferability_block"
        if any(token in prohibited_action_text.lower() for token in ("roi", "transferable", "payback"))
        else "model_prematurity_block"
        if "digital twin" in prohibited_action_text.lower() or "model" in prohibited_action_text.lower()
        else "sensor_prematurity_block"
        if "sensor" in prohibited_action_text.lower() or "hardware" in prohibited_action_text.lower()
        else "capex_underwriting_block"
        if any(token in prohibited_action_text.lower() for token in ("fund", "capex", "invest", "underwrite"))
        else "claim_closure_block"
        if any(token in prohibited_action_text.lower() for token in ("claim", "story", "fact", "observed"))
        else "general_no_go"
    )
    evidence_pack_family = {
        "REQUEST_MINIMUM_EVIDENCE": "primary_discriminator_pack",
        "BUILD_FAIR_PEER_SET": "fair_comparison_pack",
        "VALIDATE_TARIFF_EXPOSURE": "capital_logic_pack",
        "VALIDATE_CONTROL_BOUNDARY": "control_boundary_pack",
        "VALIDATE_LOSS_PATTERN": "loss_falsification_pack",
        "VALIDATE_MAINTENANCE_REALITY": "loss_falsification_pack",
        "DO_NOT_MODEL_YET": "primary_discriminator_pack",
        "DO_NOT_SENSOR_YET": "primary_discriminator_pack",
        "DO_NOT_INVEST_YET": "capital_logic_pack",
        "PROHIBIT_CLAIM": "primary_discriminator_pack",
    }.get(normalized_action, "")
    rows.append(
        {
            "strategic_action": normalized_action,
            "status": status,
            "decision_front": decision_front,
            "trigger": trigger_text,
            "trigger_family": trigger_family,
            "why": why,
            "evidence_needed": list(evidence_needed or []),
            "financial_exposure": financial_exposure_text,
            "evidence_pack_family": evidence_pack_family,
            "action_posture": text(status),
            "prohibited_action": prohibited_action_text,
            "prohibited_action_class": prohibited_action_class,
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
    if not _allows_conditional_archetypal_intelligence(asset_family_research_profile):
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
            financial_exposure="The report can still target the wrong variable or denominator before the case is bounded.",
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
            financial_exposure="Wrong-peer framing can distort underwriting, benchmark interpretation, and transferability logic.",
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
            financial_exposure=text(tariff_exposure.get("why_it_matters")),
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
            financial_exposure=text(control_exposure.get("why_it_matters")),
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
            financial_exposure="Acting on the wrong structural loss mechanism can misallocate retrofit effort and measurement budget.",
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
            financial_exposure=text(maintenance_exposure.get("why_it_matters")),
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
            financial_exposure="Modeling spend can be wasted on the wrong system boundary before the real discriminator is known.",
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
            financial_exposure="Instrumentation spend can front-run the real question and delay cheaper discriminating evidence.",
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
            financial_exposure="Capital-at-risk remains exposed to wrong-variable and wrong-boundary deployment.",
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
            financial_exposure="Premature closure can contaminate underwriting, benchmarking, and redesign sequencing.",
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
