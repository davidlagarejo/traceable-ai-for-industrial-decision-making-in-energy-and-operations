"""Adapter for motor_014 — Decision Core Engine.

Takes inference cases from motor_013 and produces the full Decision Core
output: scored inference records, tension records, conflict register,
opportunity candidates, uncertainty register, evidence gap register,
validation queue, and next best questions.

Three admissible scores per inference record:
  - plausibility_score: How plausible is this case given the prior?
  - decision_relevance_score: How much does this affect the decision state?
  - validation_urgency_score: How urgently does this need validation?

All scores range 0.0 to 1.0. Scores are non-compensatory:
a low plausibility_score does not "cancel out" a high validation_urgency.

All scores computed from base rules + evidence adjustments.
No hardcoded per-case scores.
"""
from __future__ import annotations

from datetime import datetime, timezone
import re
from typing import Any

from ..phase_units import to_inference_case_register
from .base import BaseMotorAdapter


# ── Base scores by claim_family ───────────────────────────────────────────────
# Tuple: (plausibility_base, decision_relevance_base, validation_urgency_base)

_FAMILY_BASES: dict[str, tuple[float, float, float]] = {
    "conflict":             (0.83, 0.90, 0.88),
    "tension":              (0.68, 0.76, 0.72),
    "plausible_hypothesis": (0.62, 0.66, 0.63),
    "opportunity":          (0.55, 0.68, 0.58),
    "evidence_gap":         (0.72, 0.58, 0.80),
}

_DEFAULT_BASE = (0.55, 0.60, 0.60)

_SCORE_FLOOR = 0.40
_SCORE_CEILING = 0.97

_BUILDING_TYPES = {
    "commercial_building",
    "multifamily_building",
    "hospital",
    "hotel",
    "data_center",
    "campus",
}
_LOGISTICS_TYPES = {"warehouse_distribution"}
_MANUFACTURING_TYPES = {
    "industrial_plant",
    "manufacturing_facility",
    "food_processing_facility",
    "cold_chain_facility",
}
_INFRASTRUCTURE_TYPES = {"infrastructure_node"}
_OIL_GAS_TYPES = {
    "oil_gas_upstream_site",
    "oil_gas_midstream_facility",
    "oil_gas_downstream_facility",
}

_EVIDENCE_EFFORT_RANK = {
    "LOW": 1,
    "MEDIUM": 2,
    "HIGH": 3,
    "CRITICAL": 4,
}


def _clamp(value: float) -> float:
    return max(_SCORE_FLOOR, min(_SCORE_CEILING, value))


def _target_type_from_prior(facility_prior: dict[str, Any]) -> str:
    target_definition = facility_prior.get("target_definition", {})
    if isinstance(target_definition, dict):
        return str(target_definition.get("target_type", "")).strip().lower()
    return ""


def _target_family(target_type: str) -> str:
    if target_type in _LOGISTICS_TYPES:
        return "logistics"
    if target_type in _MANUFACTURING_TYPES:
        return "manufacturing"
    if target_type in _INFRASTRUCTURE_TYPES:
        return "infrastructure"
    if target_type in _OIL_GAS_TYPES:
        return "oil_gas"
    return "building"


def _control_boundary_label(target_type: str) -> str:
    family = _target_family(target_type)
    if family in {"manufacturing", "infrastructure", "oil_gas"}:
        return "Operational / Control Boundary"
    if family == "logistics":
        return "Occupancy / Control Boundary"
    return "Tenant Control"


def _canonical_asset_context_summary(
    maturity_engine: dict[str, Any],
    facility_prior: dict[str, Any],
) -> dict[str, Any]:
    candidates = [
        maturity_engine.get("canonical_asset_context_summary", {}),
        maturity_engine.get("cluster_report_readiness_profile", {}),
        facility_prior.get("canonical_asset_context_summary", {}),
    ]
    for candidate in candidates:
        if not isinstance(candidate, dict):
            continue
        state = str(
            candidate.get("canonical_asset_context_state", "")
            or candidate.get("asset_context_state", "")
        ).strip()
        missing = [
            str(item).strip()
            for item in (
                candidate.get("missing_clusters")
                or candidate.get("canonical_missing_clusters")
                or []
            )
            if str(item).strip()
        ]
        supported = [
            str(item).strip()
            for item in (
                candidate.get("supported_clusters")
                or candidate.get("canonical_supported_clusters")
                or []
            )
            if str(item).strip()
        ]
        if state or missing or supported:
            return {
                "canonical_asset_context_state": state or str(facility_prior.get("asset_context_readiness", "asset_context_insufficient")).strip(),
                "missing_clusters": missing,
                "supported_clusters": supported,
                "screening_supported": bool(
                    candidate.get("screening_supported", False)
                    or candidate.get("canonical_screening_supported", False)
                ),
            }

    missing = list(facility_prior.get("missing_physical_observables_register", []) or [])
    return {
        "canonical_asset_context_state": str(facility_prior.get("asset_context_readiness", "asset_context_insufficient")).strip(),
        "missing_clusters": [str(item).strip() for item in missing if str(item).strip()],
        "supported_clusters": [],
        "screening_supported": False,
    }


def _geometry_question(asset_name: str, target_type: str) -> tuple[str, str]:
    family = _target_family(target_type)
    if family == "logistics":
        return (
            f"What is the verified site/building area, dock count, and any refrigerated footprint for {asset_name}?",
            "Provide the current building area, site plan, dock count, conditioned or refrigerated zones, and the document source that defines the asset boundary.",
        )
    if family == "manufacturing":
        return (
            f"What is the verified site/building area and process footprint for {asset_name}?",
            "Provide the site area, major production or support areas, and any process-boundary document that defines what equipment and floor area belong to the asset.",
        )
    if family == "infrastructure":
        return (
            f"What is the verified site boundary, one-line or layout boundary, and major equipment footprint for {asset_name}?",
            "Provide the site layout, one-line or equipment boundary drawing, and the current record that defines which units are in scope for this node.",
        )
    if family == "oil_gas":
        return (
            f"What is the verified site boundary and major process-unit footprint for {asset_name}?",
            "Provide the current plot plan or unit boundary record showing which process, utility, and emissions units belong to the asset.",
        )
    return (
        f"What is the verified GFA and rentable area for {asset_name}?",
        "Provide the latest rentable area schedule, assessor record, or benchmarking filing that states building area, asset scope, and effective date.",
    )


def _vintage_question(asset_name: str, target_type: str) -> tuple[str, str]:
    family = _target_family(target_type)
    if family == "logistics":
        return (
            f"When was {asset_name} commissioned or expanded, and what major dock, refrigeration, or building upgrades changed its operating profile?",
            "Provide original commissioning date, major expansion dates, dock or refrigeration retrofit history, and any scope summaries that changed the asset materially.",
        )
    if family == "manufacturing":
        return (
            f"When was {asset_name} commissioned, and what major process or utility upgrades materially changed how it operates?",
            "Provide commissioning date, major line additions, boiler/refrigeration/compressed-air upgrades, and any retrofit records that changed process intensity or reliability.",
        )
    if family == "infrastructure":
        return (
            f"When was {asset_name} commissioned, and what major equipment replacements or capacity upgrades changed its operating state?",
            "Provide commissioning date, substation or conversion-equipment replacement history, capacity upgrades, and any reliability-driven modernization records.",
        )
    if family == "oil_gas":
        return (
            f"When was {asset_name} commissioned, and what major turnarounds, debottlenecks, or equipment replacements changed its process duty?",
            "Provide commissioning date, turnaround history, major rotating-equipment or fired-equipment replacements, and any debottleneck projects.",
        )
    return (
        f"What year was {asset_name} built, and what major renovations materially changed its systems or structure?",
        "Provide year-built confirmation, major renovation dates, scope summaries, and any component replacement records that materially changed the asset.",
    )


def _operating_question(asset_name: str, target_type: str) -> tuple[str, str]:
    family = _target_family(target_type)
    if family == "logistics":
        return (
            f"What are the confirmed operating windows, throughput cycles, dock activity patterns, and occupancy zones for {asset_name}?",
            "Provide weekday and weekend operating windows, throughput by shift, dock cycle peaks, occupancy/use zones, and any seasonal variation that changes site load behavior.",
        )
    if family == "manufacturing":
        if target_type == "cold_chain_facility":
            return (
                f"What are the confirmed temperature-control, dock-cycle, and operating schedules for {asset_name}?",
                "Provide refrigeration setpoint regime, dock-door cycles, occupancy windows, defrost patterns, and any seasonal throughput shifts that materially change energy intensity.",
            )
        if target_type == "food_processing_facility":
            return (
                f"What are the confirmed production schedules, sanitation cycles, and refrigeration or thermal duty windows for {asset_name}?",
                "Provide shift schedule, product calendar, sanitation windows, refrigeration or process-heat duty, and any seasonal production changes that alter load behavior.",
            )
        return (
            f"What are the confirmed shift schedules, throughput patterns, and maintenance windows for {asset_name}?",
            "Provide current production shifts, throughput by major line, planned downtime or maintenance windows, and any cyclical operating pattern that changes load intensity.",
        )
    if family == "infrastructure":
        return (
            f"What service duty, dispatch profile, and reliability regime define how {asset_name} operates?",
            "Provide load or dispatch profile, redundancy requirement, outage tolerance, and any seasonal or event-driven duty cycle that changes how the node consumes energy or operates.",
        )
    if family == "oil_gas":
        return (
            f"What throughput, pressure, thermal duty, and turnaround cycles define how {asset_name} operates?",
            "Provide current throughput profile, pressure or thermal duty drivers, planned turnarounds, and any operating regime that materially changes energy, emissions, or reliability exposure.",
        )
    return (
        f"What are the confirmed operating hours, use mix, and tenant-driven schedules for {asset_name}?",
        "Provide current weekday and weekend schedules by tenant or function, the use mix by area, and any major seasonal or event-driven operating variation.",
    )


def _systems_question(asset_name: str, target_type: str) -> tuple[str, str]:
    family = _target_family(target_type)
    if family == "logistics":
        return (
            f"What dock equipment, HVAC, lighting, controls, and refrigeration systems are actually installed at {asset_name}?",
            "Provide the current system inventory, major dock and refrigeration equipment list, controls architecture, and any recent retrofit or replacement history.",
        )
    if family == "manufacturing":
        if target_type == "cold_chain_facility":
            return (
                f"What refrigeration, control, dock-air-management, and backup systems are actually installed at {asset_name}?",
                "Provide compressor, evaporator, defrost, dock-air-management, controls, and backup-power inventory with recent replacement or reliability history.",
            )
        if target_type == "food_processing_facility":
            return (
                f"What refrigeration, process-heat, compressed-air, washdown, and control systems are actually installed at {asset_name}?",
                "Provide the current inventory of thermal, refrigeration, compressed-air, washdown, and controls systems, including major equipment lists and maintenance history.",
            )
        return (
            f"What process lines, motors, compressed-air, thermal, and control systems are actually installed at {asset_name}?",
            "Provide the current system inventory, major process-support equipment list, controls architecture, and any reliability or redundancy records for critical systems.",
        )
    if family == "infrastructure":
        return (
            f"What conversion, control, redundancy, and major equipment systems are actually installed at {asset_name}?",
            "Provide the current inventory of substations, transformers, converters, switchgear, controls, and backup or redundancy systems with equipment ratings if available.",
        )
    if family == "oil_gas":
        return (
            f"What process-unit, rotating-equipment, steam, flare, compression, and control systems are actually installed at {asset_name}?",
            "Provide the current inventory of major process units, rotating equipment, steam systems, flare or vent systems, compression or pumping systems, and controls architecture.",
        )
    return (
        f"What HVAC, BMS, electrical, and major control systems are actually installed at {asset_name}?",
        "Provide the current system inventory, major equipment list, controls architecture, and any reliability or redundancy records for critical systems.",
    )


def _fuel_question(asset_name: str, target_type: str) -> tuple[str, str]:
    family = _target_family(target_type)
    if family == "manufacturing":
        return (
            f"What is the current utility, fuel, steam, refrigeration, and metering profile for {asset_name}?",
            "Provide 12–24 months of utility bills, interval or meter data if available, steam or process-heat basis, refrigeration loads, and the fuel types serving major process systems.",
        )
    if family == "infrastructure":
        return (
            f"What is the current station-service, backup-fuel, and metering profile for {asset_name}?",
            "Provide 12–24 months of electricity or station-service bills, backup generation fuel basis if any, meter mapping, and any duty data that explains service-load intensity.",
        )
    if family == "oil_gas":
        return (
            f"What is the current fuel, steam, flare, emissions, and metering basis for {asset_name}?",
            "Provide fuel-gas, steam, flare, emissions-basis, and utility records that show what energy and emissions sources actually serve each major unit.",
        )
    return (
        f"What is the current fuel, utility, and metering profile for {asset_name}?",
        "Provide 12–24 months of utility bills, interval data if available, meter mapping, and the fuel types serving major loads.",
    )


def _control_boundary_question(asset_name: str, target_type: str) -> tuple[str, str]:
    family = _target_family(target_type)
    if family == "logistics":
        return (
            f"What occupancy, lease, and control boundaries define the operating profile of {asset_name}?",
            "Provide tenant or operator occupancy by zone, any submetering or control boundaries, and any customer or lease structure that materially changes energy controllability.",
        )
    if family == "manufacturing":
        return (
            f"What operator, process, and metering boundaries define the controllable loads at {asset_name}?",
            "Provide which operator or tenant controls each major process area, how metering is split, and where responsibility for process, refrigeration, or utility loads changes.",
        )
    if family == "infrastructure":
        return (
            f"What ownership, operating, and metering boundaries define the controllable scope of {asset_name}?",
            "Provide operator responsibility by unit, service boundary, meter boundary, and any third-party equipment or load boundary that changes who controls reliability or energy decisions.",
        )
    if family == "oil_gas":
        return (
            f"What operating-unit, custody, and metering boundaries define the controllable scope of {asset_name}?",
            "Provide which units are owner-operated, which are shared or third-party, and how custody transfer, metering, and emissions responsibility are split across the site.",
        )
    return (
        f"What tenant concentration, lease boundary, and control boundary define the operating profile of {asset_name}?",
        "Provide anchor tenant details, lease concentration, submetering or control boundaries, and any current renewal or vacancy signals that change the operating profile.",
    )


def _normalize_validation_requirement(requirement: str, target_type: str) -> str:
    req = str(requirement or "").strip()
    if not req:
        return req
    family = _target_family(target_type)
    key = req.lower()
    if family == "logistics":
        return {
            "verified gfa / rentable area": "Verified building area, dock count, and any refrigerated footprint",
            "operating schedule and use mix by tenant / function": "Operating schedule, throughput windows, and dock activity profile",
            "12–24 months of utility bills, interval data if available, and meter map": "12–24 months of utility bills, meter map, and refrigeration profile if present",
            "hvac / bms / electrical system inventory": "Dock, HVAC, lighting, refrigeration, and controls inventory",
            "year built, major renovations, and structural change history": "Commissioning date and major dock / refrigeration / building upgrade history",
        }.get(key, req)
    if family == "manufacturing":
        return {
            "verified gfa / rentable area": "Verified site / building area and process footprint",
            "operating schedule and use mix by tenant / function": "Shift schedule, production calendar, and throughput profile",
            "12–24 months of utility bills, interval data if available, and meter map": "12–24 months of utility bills with fuel, steam, refrigeration, and compressed-air context",
            "hvac / bms / electrical system inventory": "Process line inventory and major energy-using equipment list",
            "year built, major renovations, and structural change history": "Commissioning date and major process / utility upgrade history",
            "tenant control boundary and major lease responsibility summary": "Operator, process, and metering boundary by line or area",
        }.get(key, req)
    if family == "infrastructure":
        return {
            "verified gfa / rentable area": "One-line or topology boundary, major equipment inventory, and redundancy basis",
            "operating schedule and use mix by tenant / function": "Service-duty or dispatch profile and station-service metering basis",
            "12–24 months of utility bills, interval data if available, and meter map": "Station-service, backup-fuel, and metering records",
            "hvac / bms / electrical system inventory": "One-line or topology boundary, major equipment inventory, and redundancy basis",
            "year built, major renovations, and structural change history": "Commissioning date and major equipment replacement / capacity upgrade history",
            "tenant control boundary and major lease responsibility summary": "Ownership, operating, and metering boundary by unit",
        }.get(key, req)
    if family == "oil_gas":
        return {
            "verified gfa / rentable area": "Verified site boundary and major process-unit footprint",
            "operating schedule and use mix by tenant / function": "Throughput profile, duty cycle, and turnaround regime",
            "12–24 months of utility bills, interval data if available, and meter map": "Fuel, flare, steam, and emissions basis by operating unit",
            "hvac / bms / electrical system inventory": "Process-unit inventory, throughput profile, and major duty drivers",
            "year built, major renovations, and structural change history": "Commissioning date and major turnaround / unit replacement history",
            "tenant control boundary and major lease responsibility summary": "Operating-unit, custody-transfer, and metering boundary map",
        }.get(key, req)
    return req


def _build_decision_core_lineage(
    facility_prior: dict[str, Any],
    inference_records: list[dict[str, Any]],
    validation_queue: list[dict[str, Any]],
    evidence_gap_register: list[dict[str, Any]],
    produced_at: str,
) -> dict[str, Any]:
    prior_lineage = facility_prior.get("evidence_lineage", {})
    return {
        "lineage_id": f"dc:{facility_prior.get('facility_prior_id', 'unknown')}",
        "produced_at": produced_at,
        "facility_prior_id": facility_prior.get("facility_prior_id", ""),
        "source_lineage_id": prior_lineage.get("lineage_id", ""),
        "admitted_source_types": prior_lineage.get("admitted_source_types", []),
        "coverage_gap_types": prior_lineage.get("coverage_gap_types", []),
        "active_inference_case_ids": [r.get("case_id", "") for r in inference_records],
        "top_validation_case_ids": [item.get("case_id", "") for item in validation_queue[:5]],
        "evidence_gap_ids": [gap.get("gap_id", "") for gap in evidence_gap_register],
        "trace_chain": [
            "motor_012.facility_prior",
            "motor_013.inference_case_register",
            "motor_014.inference_records",
            "motor_014.validation_queue",
        ],
    }


def _contains_any(text: str, signals: list[str]) -> bool:
    text_lower = text.lower()
    return any(s.lower() in text_lower for s in signals)


def _compute_scores(case: dict, facility_prior: dict) -> dict:
    """Compute plausibility, decision_relevance, and validation_urgency scores.

    Rules:
    - Base from claim_family
    - plausibility += 0.03 per confirmed base_support_trace (max +0.12)
    - decision_relevance += 0.08 if financial magnitude signals in case text
    - validation_urgency += 0.10 if deadline/blocking signals in case text
    - validation_urgency += 0.06 if concentration signals in case text
    - All scores clamped to [0.40, 0.97]
    """
    family = case.get("claim_family", "")
    base_p, base_r, base_v = _FAMILY_BASES.get(family, _DEFAULT_BASE)

    case_text = " ".join([
        case.get("conditional_statement", ""),
        case.get("inference_logic", ""),
        case.get("validation_requirement", ""),
        str(case.get("dependency_assumptions", [])),
    ])
    trace_count = len(case.get("base_support_traces", []))

    # Plausibility adjustments
    trace_bonus = min(0.03 * trace_count, 0.12)
    p_adj = base_p + trace_bonus

    # Decision relevance adjustments
    financial_magnitude_signals = [
        "billion", "material", "critical", "primary", "blocking",
        "highest", "largest", "maximum", "most important",
        "cannot be confirmed", "epistemic advancement",
    ]
    r_adj = base_r
    if _contains_any(case_text, financial_magnitude_signals):
        r_adj += 0.08

    # Validation urgency adjustments
    v_adj = base_v
    deadline_signals = [
        "block", "annually due", "deadline", "due", "annually",
        "cannot advance", "prerequisite", "halt", "maximum urgency",
        "critical", "must be resolved",
    ]
    concentration_signals = [
        "concentrat", "single tenant", "anchor", "counterparty",
        "single customer", "binary event",
    ]
    if _contains_any(case_text, deadline_signals):
        v_adj += 0.10
    if _contains_any(case_text, concentration_signals):
        v_adj += 0.06

    # Build score rationale (computed, not hardcoded)
    rationale_parts_p = [f"Base for {family}: {base_p:.2f}"]
    if trace_bonus > 0:
        rationale_parts_p.append(f"+{trace_bonus:.2f} for {trace_count} base support trace(s)")

    rationale_parts_r = [f"Base for {family}: {base_r:.2f}"]
    if r_adj > base_r:
        rationale_parts_r.append(f"+0.08 for financial magnitude signals detected in case text")

    rationale_parts_v = [f"Base for {family}: {base_v:.2f}"]
    if _contains_any(case_text, deadline_signals):
        rationale_parts_v.append("+0.10 for deadline/blocking signals in case text")
    if _contains_any(case_text, concentration_signals):
        rationale_parts_v.append("+0.06 for concentration signals in case text")

    return {
        "plausibility_score": _clamp(p_adj),
        "decision_relevance_score": _clamp(r_adj),
        "validation_urgency_score": _clamp(v_adj),
        "score_rationale": {
            "plausibility": " | ".join(rationale_parts_p),
            "decision_relevance": " | ".join(rationale_parts_r),
            "validation_urgency": " | ".join(rationale_parts_v),
        },
    }


def _score_inference_case(case: dict, facility_prior: dict) -> dict:
    scores = _compute_scores(case, facility_prior)
    return {
        **case,
        **scores,
        "scored_by_motor": "motor_014",
    }


def _build_tension_records(inference_cases: list[dict]) -> list[dict]:
    tensions = [c for c in inference_cases if c.get("claim_family") == "tension"]
    return [
        {
            "tension_record_id": f"TR-{c['case_id']}",
            "inference_case_id": c["case_id"],
            "tension_name": c["case_name"],
            "elements_in_tension": c.get("elements_in_tension", []),
            "tension_statement": c["conditional_statement"],
            "plausibility_score": c["plausibility_score"],
            "decision_relevance_score": c["decision_relevance_score"],
            "validation_urgency_score": c["validation_urgency_score"],
            "validation_requirement": c["validation_requirement"],
            "resolution_status": "open — requires validation",
            "produced_by_motor": "motor_014",
        }
        for c in tensions
    ]


def _build_conflict_register(inference_cases: list[dict]) -> list[dict]:
    conflicts = [c for c in inference_cases if c.get("claim_family") == "conflict"]
    ranked = sorted(
        conflicts,
        key=lambda c: (
            0 if c.get("case_id") == "LC-ASSET-01" else 1,
            -c.get("validation_urgency_score", 0),
            -c.get("decision_relevance_score", 0),
        ),
    )
    result = []
    for idx, c in enumerate(ranked):
        is_asset_foundation_conflict = c.get("case_id") == "LC-ASSET-01"
        result.append({
            "conflict_id": f"CR-{c['case_id']}",
            "inference_case_id": c["case_id"],
            "conflict_name": c["case_name"],
            "conflict_statement": c["conditional_statement"],
            "plausibility_score": c["plausibility_score"],
            "decision_relevance_score": c["decision_relevance_score"],
            "validation_urgency_score": c["validation_urgency_score"],
            "conflict_type": "asset_context_insufficiency" if is_asset_foundation_conflict else "data_inconsistency",
            "blocking_status": (
                "FOUNDATIONAL BLOCK — asset technical substrate is insufficient for a normal technical report"
                if is_asset_foundation_conflict
                else "BLOCKING — epistemic advancement on analysis dependent on this data is halted until resolved"
                if c.get("validation_urgency_score", 0) >= 0.85
                else "ACTIVE — requires validation before analytical weight can be assigned"
            ),
            "validation_requirement": c["validation_requirement"],
            "conflict_priority_rank": idx + 1,
            "produced_by_motor": "motor_014",
        })
    return result


def _build_opportunity_candidates(inference_cases: list[dict], facility_prior: dict) -> list[dict]:
    """Derive opportunity candidates dynamically from tensions and regulatory cases."""
    target_admissibility_state = str(
        facility_prior.get("target_admissibility_state", "")
    ).strip()
    subject_gate_passed = bool(facility_prior.get("subject_gate_passed", False))
    if target_admissibility_state and (
        not subject_gate_passed
        or target_admissibility_state not in {"bounded_asset", "bounded_asset_with_operable_context"}
    ):
        return []

    opportunities: list[dict] = []
    opp_counter = 1

    entities = facility_prior.get("entities", {})
    reg_ctx = entities.get("RegulatoryContext", {})
    facility = entities.get("Facility", {})
    asset_name = facility_prior.get("asset_name", "the facility")

    # For each tension with decision_relevance > 0.70: create a corresponding opportunity
    high_relevance_tensions = [
        c for c in inference_cases
        if c.get("claim_family") == "tension" and c.get("decision_relevance_score", 0) > 0.70
    ]
    for tension in high_relevance_tensions:
        # Derive opportunity type from tension type
        case_text = tension.get("conditional_statement", "")
        case_id_ref = tension.get("case_id", "")
        tension_name = tension.get("case_name", "")

        # Determine opportunity type from tension context
        if "compliance" in case_text.lower() or "regulation" in case_text.lower() or "regulatory" in case_text.lower():
            opp_type = "regulatory_compliance_investment"
            opp_name = f"Compliance Investment as Operational Advancement — [{case_id_ref}]"
            opp_statement = (
                f"IF the compliance gap for {asset_name} is quantified AND a verified "
                "retrofit or corrective pathway exists, "
                "THEN a structured compliance investment reduces forward penalty exposure "
                "and advances the operational normative standing of the asset. "
                "The investment, once validated and executed, eliminates the tension "
                f"identified in {case_id_ref} ({tension_name})."
            )
        elif "concentrat" in case_text.lower() or "tenant" in case_text.lower() or "counterparty" in case_text.lower():
            opp_type = "counterparty_risk_mitigation"
            opp_name = f"Counterparty Risk Mitigation and Diversification — [{case_id_ref}]"
            opp_statement = (
                f"IF the counterparty concentration at {asset_name} is confirmed AND "
                "contract terms are approaching maturity, "
                "THEN proactive engagement, lease extension at current rates, or "
                "strategic re-letting at market rates represents a value-preservation or "
                "value-creation pathway depending on current vs. market rent differential."
            )
        elif "debt" in case_text.lower() or "leverage" in case_text.lower() or "financing" in case_text.lower():
            opp_type = "debt_structure_optimization"
            opp_name = f"Debt Structure Optimization and Transparency — [{case_id_ref}]"
            opp_statement = (
                f"IF the full debt scope for {asset_name} is confirmed AND "
                "refinancing conditions are favorable, "
                "THEN debt restructuring may reduce financing cost, extend maturities, "
                "or improve transparency for institutional counterparties. "
                "Resolution of the tension in {case_id_ref} unlocks leverage-dependent decisions."
            )
        else:
            opp_type = "tension_resolution_value"
            opp_name = f"Value Creation Through Tension Resolution — [{case_id_ref}]"
            opp_statement = (
                f"IF the tension identified in {case_id_ref} ({tension_name}) for {asset_name} "
                "is resolved through targeted validation AND the resolution indicates a "
                "manageable risk profile, "
                "THEN the asset's analytical standing advances and previously blocked "
                "decisions become accessible."
            )

        # Compute opportunity scores: derived from source tension but discounted
        opp_p = _clamp(tension.get("plausibility_score", 0.62) * 0.85)
        opp_r = _clamp(tension.get("decision_relevance_score", 0.68) * 0.90)
        opp_v = _clamp(tension.get("validation_urgency_score", 0.65) * 0.88)

        opportunities.append({
            "opportunity_id": f"OC-{opp_counter:02d}",
            "opportunity_name": opp_name,
            "opportunity_type": opp_type,
            "source_tension_id": case_id_ref,
            "conditional_statement": opp_statement,
            "dependency_assumptions": tension.get("dependency_assumptions", []),
            "validation_requirement": (
                f"Resolve tension {case_id_ref} first: {tension.get('validation_requirement', '')} "
                "Then assess value-creation or risk-mitigation pathway."
            ),
            "plausibility_score": opp_p,
            "decision_relevance_score": opp_r,
            "validation_urgency_score": opp_v,
            "score_rationale": {
                "note": (
                    f"Opportunity scores derived from source tension {case_id_ref} "
                    f"(P={tension.get('plausibility_score',0):.2f}, "
                    f"R={tension.get('decision_relevance_score',0):.2f}, "
                    f"V={tension.get('validation_urgency_score',0):.2f}) "
                    "with opportunity discount factors applied (0.85/0.90/0.88)."
                )
            },
            "produced_by_motor": "motor_014",
        })
        opp_counter += 1

    # For regulatory tensions: also add a compliance investment opportunity if not already covered
    reg_flags = reg_ctx.get("regulatory_flags", [])
    primary_reg = reg_ctx.get("primary_regulation", "")
    if reg_flags and primary_reg:
        # Only add if not already covered by a tension-derived opportunity
        already_covered = any(
            "regulatory_compliance_investment" in o.get("opportunity_type", "")
            or "compliance" in o.get("opportunity_name", "").lower()
            for o in opportunities
        )
        if not already_covered:
            gfa_desc = ""
            gfa_sqft = facility.get("GFA_sqft")
            if gfa_sqft:
                gfa_desc = f"({gfa_sqft:,} sqft)"

            opportunities.append({
                "opportunity_id": f"OC-{opp_counter:02d}",
                "opportunity_name": f"Proactive {primary_reg} Compliance Investment",
                "opportunity_type": "regulatory_compliance_investment",
                "source_tension_id": None,
                "conditional_statement": (
                    f"IF current compliance gap under {primary_reg} for {asset_name} {gfa_desc} "
                    "is quantified AND a technically feasible compliance pathway is identified, "
                    "THEN a structured compliance investment programme reduces forward regulatory "
                    "exposure and may advance the asset's operational grade."
                ),
                "dependency_assumptions": [
                    f"Compliance gap under {primary_reg} must first be confirmed.",
                    "Retrofit pathway must be technically and physically feasible.",
                    "Investment cost must be modeled against forward penalty elimination.",
                ],
                "validation_requirement": (
                    f"Confirm current compliance status under {primary_reg}. "
                    "Commission engineering study of compliance gap. "
                    "Estimate investment cost and model forward penalty exposure elimination."
                ),
                "plausibility_score": 0.65,
                "decision_relevance_score": 0.78,
                "validation_urgency_score": 0.75,
                "score_rationale": {
                    "note": "Regulatory opportunity: scores derived from compliance signal strength."
                },
                "produced_by_motor": "motor_014",
            })
            opp_counter += 1

    return opportunities


def _build_uncertainty_register(facility_prior: dict, inference_cases: list[dict]) -> list[dict]:
    um = facility_prior.get("uncertainty_markers", [])
    register = []
    for marker in um:
        matching_case = next(
            (c for c in inference_cases if marker.get("marker_id", "") in str(c.get("base_support_traces", []))),
            None
        )
        register.append({
            "uncertainty_record_id": f"UR-{marker['marker_id']}",
            "marker_id": marker["marker_id"],
            "dimension": marker["dimension"],
            "description": marker["description"],
            "impact": marker["impact"],
            "resolution_path": marker["resolution_path"],
            "linked_inference_case": matching_case["case_id"] if matching_case else None,
            "produced_by_motor": "motor_014",
        })
    return register


def _build_evidence_gap_register(inference_cases: list[dict], facility_prior: dict) -> list[dict]:
    gaps = []
    high_urgency = [c for c in inference_cases if c.get("validation_urgency_score", 0) >= 0.85]
    for case in high_urgency:
        gaps.append({
            "gap_id": f"EG-{case['case_id']}",
            "gap_type": "validation_blocker",
            "description": (
                f"Evidence required to validate or destroy inference case "
                f"{case['case_id']}: {case['case_name']}"
            ),
            "data_required": case["validation_requirement"],
            "blocking_inference_cases": [case["case_id"]],
            "epistemic_impact": (
                "High — blocks epistemic advancement on dependent cases"
                if case.get("claim_family") == "conflict"
                else "High — constrains confidence on dependent analytical outputs"
            ),
            "validation_urgency_score": case["validation_urgency_score"],
            "produced_by_motor": "motor_014",
        })
    return gaps


def _build_validation_queue(inference_cases: list[dict]) -> list[dict]:
    sorted_cases = sorted(inference_cases, key=lambda c: c.get("validation_urgency_score", 0), reverse=True)
    return [
        {
            "queue_position": idx + 1,
            "case_id": c["case_id"],
            "case_name": c["case_name"],
            "claim_family": c.get("claim_family", ""),
            "validation_urgency_score": c.get("validation_urgency_score", 0),
            "decision_relevance_score": c.get("decision_relevance_score", 0),
            "validation_requirement": c["validation_requirement"],
            "produced_by_motor": "motor_014",
        }
        for idx, c in enumerate(sorted_cases)
    ]


def _build_next_best_questions(
    asset_name: str,
    minimum_evidence_unlock_map: list[dict[str, Any]],
    missing_evidence_register: list[dict[str, Any]],
    missing_clusters: list[str],
    decision_front_register: list[dict[str, Any]],
    target_type: str,
) -> list[dict[str, Any]]:
    questions: list[dict[str, Any]] = []
    seen_questions: set[str] = set()
    question_id = 1

    foundational_missing = {
        cluster
        for cluster in missing_clusters
        if cluster in {"identity_cluster", "geometry_size_cluster"}
    }
    control_boundary_missing = any(
        cluster in missing_clusters
        for cluster in {"boundary_cluster", "control_boundary_cluster", "tenant_control_cluster"}
    )

    if foundational_missing:
        question_text = (
            f"What record proves that {asset_name} is a bounded asset with its own "
            "area, use mix, and system boundary rather than issuer-level address context?"
        )
        questions.append(
            {
                "question_id": f"NBQ-{question_id:02d}",
                "question": question_text,
                "linked_case": "LC-ASSET-01",
                "case_name": "Asset Technical Insufficiency and Scope Mismatch",
                "claim_family": "conflict",
                "why_it_matters": (
                    "This is the foundational blocker. Until the address is tied to a bounded "
                    "asset record, stronger technical, financial, and compliance claims remain degraded."
                ),
                "how_to_answer": (
                    "Provide an assessor, parcel, benchmarking, registry, or operator record that ties "
                    "the address to a specific building or site and confirms the asset boundary."
                ),
                "urgency": "critical",
                "validation_urgency_score": 0.97,
            }
        )
        seen_questions.add(question_text.lower())
        question_id += 1
    elif control_boundary_missing:
        question_text, how_to = _control_boundary_question(asset_name, target_type)
        questions.append(
            {
                "question_id": f"NBQ-{question_id:02d}",
                "question": question_text,
                "linked_case": "LC-ASSET-01",
                "case_name": "Asset Technical Insufficiency and Scope Mismatch",
                "claim_family": "conflict",
                "why_it_matters": (
                    "Public records support the asset identity, but the owner / operator control boundary "
                    "is still unresolved."
                ),
                "how_to_answer": how_to,
                "urgency": "critical",
                "validation_urgency_score": 0.95,
            }
        )
        seen_questions.add(question_text.lower())
        question_id += 1

    for missing in missing_evidence_register:
        if question_id > 7:
            break
        missing_field = str(missing.get("missing_field", "")).strip()
        if not missing_field:
            continue
        question = f"What evidence can confirm the missing field '{missing_field}' for {asset_name}?"
        if question.lower() in seen_questions:
            continue
        questions.append(
            {
                "question_id": f"NBQ-{question_id:02d}",
                "question": question,
                "linked_case": str(missing.get("related_cluster", "")).strip() or "missing_evidence",
                "case_name": missing_field,
                "claim_family": "missing_evidence",
                "why_it_matters": str(missing.get("why_it_matters", "")).strip(),
                "how_to_answer": (
                    f"Provide {missing.get('minimum_evidence_needed', 'the minimum evidence item')} from "
                    f"{missing.get('suggested_source', 'the suggested source')}."
                ),
                "urgency": "critical",
                "validation_urgency_score": 0.96,
            }
        )
        seen_questions.add(question.lower())
        question_id += 1

    for row in minimum_evidence_unlock_map:
        if question_id > 7:
            break
        evidence_item = str(row.get("evidence_item", "")).strip()
        if not evidence_item:
            continue
        evidence_lower = evidence_item.lower()
        linked_case = (row.get("cases_resolved") or [""])[0]
        urgency = str(row.get("effort", "HIGH")).lower()
        why_needed = str(row.get("why_needed", "")).strip()
        decision_unlock = str(row.get("decision_unlock", "")).strip()
        source = str(row.get("source", "owner / operator")).strip()
        if linked_case == "LC-ASSET-01" and "." in evidence_item and len(evidence_item.split()) > 12:
            continue
        if "bounded asset record" in evidence_lower:
            continue

        if linked_case == "LC-OPS-05":
            question = f"Which critical missing clusters for {asset_name} can be populated immediately from records already held by the owner or operator?"
            how_to = (
                "Return one checklist response covering geometry, operating regime, systems, fuel profile, "
                "and the current status of each missing record."
            )
        elif linked_case == "LC-FIN-02":
            question = f"What debt is actually secured by or allocable to {asset_name}, and what maturities or JV obligations sit behind that figure?"
            how_to = (
                "Provide the property loan schedule, maturity dates, JV debt disclosures, and any off-balance-sheet "
                "or cross-collateralized obligations tied to the asset."
            )
        elif linked_case == "LC-OPS-01":
            question, how_to = _control_boundary_question(asset_name, target_type)
        elif linked_case == "LC-OPS-02":
            question, how_to = _vintage_question(asset_name, target_type)
        elif linked_case == "LC-OPS-04":
            question, how_to = _systems_question(asset_name, target_type)
        elif "gfa" in evidence_lower or "rentable area" in evidence_lower or "gross floor area" in evidence_lower:
            question, how_to = _geometry_question(asset_name, target_type)
        elif "operating schedule" in evidence_lower or "use mix" in evidence_lower:
            question, how_to = _operating_question(asset_name, target_type)
        elif "hvac" in evidence_lower or "bms" in evidence_lower or "electrical system inventory" in evidence_lower:
            question, how_to = _systems_question(asset_name, target_type)
        elif (
            "control boundary" in evidence_lower
            or "metering boundary" in evidence_lower
            or "custody-transfer" in evidence_lower
            or "operator, process, and metering boundary" in evidence_lower
            or "ownership, operating, and metering boundary" in evidence_lower
            or "operating-unit, custody-transfer, and metering boundary" in evidence_lower
        ):
            question, how_to = _control_boundary_question(asset_name, target_type)
        elif "utility" in evidence_lower or "fuel" in evidence_lower or "meter" in evidence_lower:
            question, how_to = _fuel_question(asset_name, target_type)
        elif "year built" in evidence_lower or "renovation" in evidence_lower or "structural" in evidence_lower:
            question, how_to = _vintage_question(asset_name, target_type)
        elif "throughput" in evidence_lower or "production calendar" in evidence_lower or "dispatch profile" in evidence_lower:
            question, how_to = _operating_question(asset_name, target_type)
        elif "process line" in evidence_lower or "process-unit" in evidence_lower or "major duty drivers" in evidence_lower:
            question, how_to = _systems_question(asset_name, target_type)
        elif "compliance filing" in evidence_lower:
            question = f"What is the current compliance filing and trigger data for {asset_name}?"
            how_to = (
                "Provide the latest compliance filing, reported threshold fields, area basis, fuel basis, "
                "and any local applicability determination used in that filing."
            )
        else:
            if "." in evidence_item and len(evidence_item.split()) > 12:
                continue
            question = f"What {evidence_item.lower()} can be provided now for {asset_name}?"
            how_to = (
                f"Request this item from {source.lower()} and confirm the document date, asset scope, and evidentiary owner."
            )

        if question.lower() in seen_questions:
            continue
        questions.append(
            {
                "question_id": f"NBQ-{question_id:02d}",
                "question": question,
                "linked_case": linked_case,
                "case_name": why_needed or evidence_item,
                "claim_family": "evidence_gap",
                "why_it_matters": " ".join(part for part in [why_needed, decision_unlock] if part).strip(),
                "how_to_answer": how_to,
                "urgency": urgency,
                "validation_urgency_score": 0.95 if urgency == "critical" else 0.84 if urgency == "high" else 0.72,
            }
        )
        seen_questions.add(question.lower())
        question_id += 1

    decision_front = next(
        (
            front for front in decision_front_register
            if front.get("current_status") in {"NO-GO", "VALIDATE FIRST"}
        ),
        {},
    )
    if question_id <= 7 and decision_front:
        question_text = (
            f"What specific evidence would change the current status of "
            f"'{decision_front.get('decision_front', 'the leading decision front')}' for {asset_name}?"
        )
        if question_text.lower() in seen_questions:
            return questions[:7]
        questions.append(
            {
                "question_id": f"NBQ-{question_id:02d}",
                "question": question_text,
                "linked_case": (decision_front.get("decision_front", "") or "decision_front").replace(" ", "_"),
                "case_name": decision_front.get("decision_front", ""),
                "claim_family": "decision_front",
                "why_it_matters": str(decision_front.get("why", "")).strip(),
                "how_to_answer": str(decision_front.get("required_evidence", "Minimum evidence pack")).strip(),
                "urgency": "high",
                "validation_urgency_score": 0.83,
            }
        )

    return questions[:7]


def _critical_missing_clusters(missing_clusters: list[str]) -> list[str]:
    critical = {
        "geometry_size_cluster",
        "operating_regime_cluster",
        "systems_cluster",
        "fuel_energy_cluster",
    }
    return [cluster for cluster in missing_clusters if cluster in critical]


def _priority_label(score: float) -> str:
    if score >= 0.90:
        return "CRITICAL"
    if score >= 0.80:
        return "HIGH"
    if score >= 0.65:
        return "MEDIUM"
    return "LOW"


def _information_deficit_score(
    inference_records: list[dict[str, Any]],
    missing_clusters: list[str],
) -> float:
    if not inference_records:
        return 1.0 if missing_clusters else 0.0
    total_weight = sum(r.get("decision_relevance_score", 0) for r in inference_records) or 1.0
    weighted_gap = sum(
        r.get("decision_relevance_score", 0) * (1 - r.get("plausibility_score", 0))
        for r in inference_records
    )
    base = weighted_gap / total_weight
    critical_missing = len(_critical_missing_clusters(missing_clusters))
    if critical_missing >= 3:
        base = max(base, 0.88)
    elif critical_missing == 2:
        base = max(base, 0.76)
    elif critical_missing == 1:
        base = max(base, 0.62)
    elif missing_clusters:
        base = max(base, 0.52)
    return round(min(base, 0.99), 3)


def _cluster_status_rows(
    missing_clusters: list[str],
    asset_context_readiness: str,
    target_type: str,
) -> list[dict[str, str]]:
    control_boundary_label = _control_boundary_label(target_type)
    control_boundary_missing = (
        "control_boundary_cluster" in missing_clusters
        or "tenant_control_cluster" in missing_clusters
    )
    cluster_labels = {
        "identity_cluster": "Identity",
        "boundary_cluster": "Asset / Site Boundary",
        "geometry_size_cluster": "Geometry / Size",
        "vintage_structure_cluster": "Vintage / Structure",
        "operating_regime_cluster": "Operating Regime",
        "fuel_energy_cluster": "Fuel / Energy",
        "systems_cluster": "Systems",
        "control_boundary_cluster": control_boundary_label,
        "regulatory_cluster": "Regulatory Applicability",
        "financial_boundary_cluster": "Financial Boundary",
    }
    rows: list[dict[str, str]] = []
    for cluster_id, label in cluster_labels.items():
        missing = control_boundary_missing if cluster_id == "control_boundary_cluster" else cluster_id in missing_clusters
        rows.append(
            {
                "cluster_id": cluster_id,
                "cluster": label,
                "status": "BLOCKING" if missing else "PARTIAL",
                "current_evidence": "NOT OBSERVED" if missing else "Public signals or intake declaration available",
                "consequence": (
                    "Blocks stronger technical or financial advancement."
                    if missing
                    else "Supports screening-grade reading only until local evidence arrives."
                ),
            }
        )
    rows.append(
        {
            "cluster_id": "asset_context_readiness",
            "cluster": "Asset Context Readiness",
            "status": asset_context_readiness.upper(),
            "current_evidence": asset_context_readiness,
            "consequence": "Determines which report class is admissible.",
        }
    )
    return rows


def _build_minimum_evidence_unlock_map(
    validation_queue: list[dict[str, Any]],
    inference_records: list[dict[str, Any]],
    missing_clusters: list[str],
    minimum_evidence_seed: list[dict[str, Any]] | None = None,
    target_type: str = "",
) -> list[dict[str, Any]]:
    def _semantic_key(item: str) -> str:
        text = str(item or "").strip().lower()
        if not text:
            return ""
        generic_patterns = [
            ("asset record", "asset_boundary_record"),
            ("parcel", "asset_boundary_record"),
            ("bounded asset", "asset_boundary_record"),
            ("gfa", "scale_geometry"),
            ("rentable area", "scale_geometry"),
            ("building area", "scale_geometry"),
            ("site / building area", "scale_geometry"),
            ("year built", "vintage_upgrade_history"),
            ("commissioning date", "vintage_upgrade_history"),
            ("upgrade history", "vintage_upgrade_history"),
            ("renovation", "vintage_upgrade_history"),
            ("utility bills", "utility_fuel_records"),
            ("utility / fuel records", "utility_fuel_records"),
            ("fuel profile", "utility_fuel_records"),
            ("metering records", "utility_fuel_records"),
            ("meter map", "utility_fuel_records"),
            ("hvac", "systems_inventory"),
            ("bms", "systems_inventory"),
            ("electrical system inventory", "systems_inventory"),
            ("controls system inventory", "systems_inventory"),
            ("process line", "systems_inventory"),
            ("major energy-using equipment", "systems_inventory"),
            ("shift schedule", "operating_profile"),
            ("production calendar", "operating_profile"),
            ("throughput profile", "operating_profile"),
            ("operating schedule", "operating_profile"),
            ("use mix", "operating_profile"),
            ("control boundary", "control_boundary"),
            ("metering boundary", "control_boundary"),
            ("custody-transfer", "control_boundary"),
            ("asset context checklist", "asset_context_checklist"),
        ]
        for signal, key in generic_patterns:
            if signal in text:
                return key
        return re.sub(r"[^a-z0-9]+", "_", text).strip("_")

    def _merge_row(existing: dict[str, Any], incoming: dict[str, Any]) -> dict[str, Any]:
        def _merge_text(a: str, b: str) -> str:
            a = str(a or "").strip()
            b = str(b or "").strip()
            if not a:
                return b
            if not b or b == a:
                return a
            if b in a:
                return a
            if a in b:
                return b
            return f"{a} {b}".strip()

        merged_cases = []
        for item in list(existing.get("cases_resolved", []) or []) + list(incoming.get("cases_resolved", []) or []):
            token = str(item).strip()
            if token and token not in merged_cases:
                merged_cases.append(token)
        effort_existing = str(existing.get("effort", "LOW")).upper()
        effort_incoming = str(incoming.get("effort", "LOW")).upper()
        effort = (
            effort_incoming
            if _EVIDENCE_EFFORT_RANK.get(effort_incoming, 0) > _EVIDENCE_EFFORT_RANK.get(effort_existing, 0)
            else effort_existing
        )
        return {
            **existing,
            "source": _merge_text(existing.get("source", ""), incoming.get("source", "")),
            "why_needed": _merge_text(existing.get("why_needed", ""), incoming.get("why_needed", "")),
            "decision_unlock": _merge_text(existing.get("decision_unlock", ""), incoming.get("decision_unlock", "")),
            "cases_resolved": merged_cases,
            "effort": effort,
            "priority": effort,
        }

    rows: list[dict[str, Any]] = []
    family = _target_family(target_type)
    for seed in minimum_evidence_seed or []:
        rows.append(
            {
                "evidence_item": seed.get("evidence_item", ""),
                "source": seed.get("source", ""),
                "why_needed": seed.get("why_needed", ""),
                "cases_resolved": seed.get("cases_resolved", []),
                "effort": seed.get("effort", "HIGH"),
                "decision_unlock": seed.get("decision_unlock", ""),
                "priority": seed.get("effort", "HIGH"),
            }
        )
    for cluster in missing_clusters:
        if cluster == "geometry_size_cluster":
            if family == "manufacturing":
                rows.append(
                    {
                        "evidence_item": "Verified site / building area and process footprint",
                        "source": "Owner records, site plan, or plant layout",
                        "why_needed": "Sets the scale of process, energy, emissions, and CAPEX exposure.",
                        "cases_resolved": ["LC-ASSET-01"],
                    "effort": "CRITICAL",
                    "decision_unlock": "Unlocks bounded process and compliance screening.",
                    "priority": "CRITICAL",
                }
            )
            elif family == "infrastructure":
                rows.append(
                    {
                        "evidence_item": "Verified site boundary, one-line or layout boundary, and major equipment footprint",
                        "source": "Operator records, site layout, or one-line diagram",
                        "why_needed": "Defines the in-scope node topology before reliability or loss claims can be interpreted.",
                        "cases_resolved": ["LC-ASSET-01"],
                    "effort": "CRITICAL",
                    "decision_unlock": "Unlocks bounded topology and resilience screening.",
                    "priority": "CRITICAL",
                }
            )
            elif family == "oil_gas":
                rows.append(
                    {
                        "evidence_item": "Verified site boundary and major process-unit footprint",
                        "source": "Operator records, plot plan, or unit boundary documentation",
                        "why_needed": "Defines which units are in scope for process, emissions, and CAPEX reading.",
                        "cases_resolved": ["LC-ASSET-01"],
                    "effort": "CRITICAL",
                    "decision_unlock": "Unlocks bounded process and emissions screening.",
                    "priority": "CRITICAL",
                }
            )
            elif family == "logistics":
                rows.append(
                    {
                        "evidence_item": "Verified building area, dock count, and any refrigerated footprint",
                        "source": "Owner records, site plan, or operator layout",
                        "why_needed": "Sets the scale of throughput, refrigeration, and retrofit exposure.",
                        "cases_resolved": ["LC-ASSET-01"],
                    "effort": "CRITICAL",
                    "decision_unlock": "Unlocks bounded logistics and compliance screening.",
                    "priority": "CRITICAL",
                }
            )
            else:
                rows.append(
                    {
                        "evidence_item": "Verified GFA / rentable area",
                        "source": "Owner records or assessor / benchmark filing",
                        "why_needed": "Sets the scale of energy, compliance, and CAPEX exposure.",
                        "cases_resolved": ["LC-ASSET-01"],
                    "effort": "CRITICAL",
                    "decision_unlock": "Unlocks compliance screening and retrofit scale framing.",
                    "priority": "CRITICAL",
                }
            )
        elif cluster == "vintage_structure_cluster":
            if family == "manufacturing":
                evidence_item = "Commissioning date and major process / utility upgrade history"
                why_needed = "Helps distinguish legacy process constraints from more recent plant upgrades."
                decision_unlock = "Improves process-age interpretation and modernization framing."
            elif family == "infrastructure":
                evidence_item = "Commissioning date and major equipment replacement / capacity upgrade history"
                why_needed = "Helps distinguish legacy topology constraints from more recent capacity or reliability upgrades."
                decision_unlock = "Improves resilience and equipment-age interpretation."
            elif family == "oil_gas":
                evidence_item = "Commissioning date and major turnaround / unit replacement history"
                why_needed = "Helps distinguish legacy process liability from more recent unit or turnaround changes."
                decision_unlock = "Improves process-age and maintenance-cycle interpretation."
            elif family == "logistics":
                evidence_item = "Commissioning date and major dock / refrigeration / building upgrade history"
                why_needed = "Helps distinguish age-driven logistics constraints from more recent operational upgrades."
                decision_unlock = "Improves upgrade framing and refrigeration-age interpretation."
            else:
                evidence_item = "Year built, major renovations, and structural change history"
                why_needed = "Helps distinguish age-driven liability from more current system condition."
                decision_unlock = "Improves CAPEX framing and system-age interpretation."
            rows.append(
                {
                    "evidence_item": evidence_item,
                    "source": "Owner records, permits, benchmark history, or engineering records",
                    "why_needed": why_needed,
                    "cases_resolved": ["LC-ASSET-01", "LC-OPS-02"],
                    "effort": "HIGH",
                    "decision_unlock": decision_unlock,
                    "priority": "HIGH",
                }
            )
        elif cluster == "operating_regime_cluster":
            if family == "manufacturing":
                evidence_item = "Shift schedule, throughput profile, and maintenance / sanitation cycle"
                source = "Plant operations or production planning"
                why_needed = "Determines whether process intensity is structural, schedule-driven, or operationally correctable."
                decision_unlock = "Unlocks scenario discrimination and process-duty interpretation."
            elif family == "infrastructure":
                evidence_item = "Service duty, dispatch profile, and reliability regime"
                source = "Operator records or system operations"
                why_needed = "Determines whether operating behavior is topology-driven, duty-driven, or operationally flexible."
                decision_unlock = "Unlocks scenario discrimination and resilience-side decisions."
            elif family == "oil_gas":
                evidence_item = "Throughput profile, duty cycle, and turnaround regime"
                source = "Operations engineering or site operator"
                why_needed = "Determines whether energy and emissions behavior is throughput-driven or operationally adjustable."
                decision_unlock = "Unlocks scenario discrimination and process-duty decisions."
            elif family == "logistics":
                evidence_item = "Operating schedule, throughput windows, and dock activity profile"
                source = "Operator, lease summary, or facility manager"
                why_needed = "Determines whether site energy behavior is throughput-driven, occupancy-driven, or operationally correctable."
                decision_unlock = "Unlocks scenario discrimination and logistics-side decisions."
            else:
                evidence_item = "Operating schedule and use mix by tenant / function"
                source = "Operator, lease summary, or facility manager"
                why_needed = "Determines whether energy behavior is structural or operational."
                decision_unlock = "Unlocks scenario discrimination and energy-side decisions."
            rows.append(
                {
                    "evidence_item": evidence_item,
                    "source": source,
                    "why_needed": why_needed,
                    "cases_resolved": ["LC-ASSET-01"],
                    "effort": "CRITICAL",
                    "decision_unlock": decision_unlock,
                    "priority": "CRITICAL",
                }
            )
        elif cluster == "fuel_energy_cluster":
            if family == "manufacturing":
                evidence_item = "12–24 months of utility / fuel records with process-support context"
                why_needed = "Defines actual fuel, thermal, refrigeration, or compressed-air exposure instead of public priors alone."
                decision_unlock = "Unlocks bounded energy, emissions, and process-cost reading."
            elif family == "infrastructure":
                evidence_item = "12–24 months of station-service, backup-fuel, and metering records"
                why_needed = "Defines actual service-load exposure and any fuel-dependent reliability basis."
                decision_unlock = "Unlocks bounded energy, resilience, and compliance reading."
            elif family == "oil_gas":
                evidence_item = "12–24 months of fuel, steam, flare, and emissions-basis records"
                why_needed = "Defines actual process fuel and emissions exposure instead of public priors alone."
                decision_unlock = "Unlocks bounded carbon, compliance, and process-cost reading."
            else:
                evidence_item = "12–24 months of utility bills and fuel profile"
                why_needed = "Defines actual fuel exposure, energy scale, and the basis for compliance or retrofit screening."
                decision_unlock = "Unlocks bounded energy, carbon, and compliance reading."
            rows.append(
                {
                    "evidence_item": evidence_item,
                    "source": "Operator, utility portal, owner accounting records, or engineering data room",
                    "why_needed": why_needed,
                    "cases_resolved": ["LC-ASSET-01", "LC-REG-01", "LC-MKT-02"],
                    "effort": "CRITICAL",
                    "decision_unlock": decision_unlock,
                    "priority": "CRITICAL",
                }
            )
        elif cluster == "systems_cluster":
            if family == "manufacturing":
                evidence_item = "Process line, utility, and controls system inventory"
                why_needed = "Required before any process-efficiency, reliability, or controllability claim can be defended."
                decision_unlock = "Unlocks bounded process-retrofit and technical diligence logic."
            elif family == "infrastructure":
                evidence_item = "Major equipment, controls, and redundancy system inventory"
                why_needed = "Required before any reliability, conversion-loss, or resilience claim can be defended."
                decision_unlock = "Unlocks bounded topology and resilience logic."
            elif family == "oil_gas":
                evidence_item = "Process-unit, rotating-equipment, and controls inventory"
                why_needed = "Required before any process, emissions, or reliability claim can be defended."
                decision_unlock = "Unlocks bounded process and transition logic."
            elif family == "logistics":
                evidence_item = "Dock, HVAC, refrigeration, lighting, and controls inventory"
                why_needed = "Required before any logistics-efficiency or controllability claim can be defended."
                decision_unlock = "Unlocks bounded retrofit and technical diligence logic."
            else:
                evidence_item = "HVAC / BMS / electrical system inventory"
                why_needed = "Required before any retrofit or controllability claim can be defended."
                decision_unlock = "Unlocks bounded retrofit and technical diligence logic."
            rows.append(
                {
                    "evidence_item": evidence_item,
                    "source": "Engineering records or site operator",
                    "why_needed": why_needed,
                    "cases_resolved": ["LC-ASSET-01"],
                    "effort": "CRITICAL",
                    "decision_unlock": decision_unlock,
                    "priority": "CRITICAL",
                }
            )
        elif cluster == "boundary_cluster":
            if family == "manufacturing":
                evidence_item = "Operator scope, unit boundary, and in-scope responsibility record"
                why_needed = "Defines which production, utility, and support areas belong to the asset before process claims are advanced."
                decision_unlock = "Unlocks bounded process and permit screening."
            elif family == "logistics":
                evidence_item = "Owner / operator boundary and refrigerated or dock-control scope"
                why_needed = "Defines which operating areas and loads belong to the asset before logistics-side claims are advanced."
                decision_unlock = "Unlocks bounded logistics and compliance screening."
            else:
                evidence_item = "Owner / tenant boundary responsibility record"
                why_needed = "Defines which loads, systems, and obligations belong to the in-scope asset before underwriting or compliance claims are advanced."
                decision_unlock = "Unlocks bounded screening without re-opening identity or scale."
            rows.append(
                {
                    "evidence_item": evidence_item,
                    "source": "Owner, operator, lease, or boundary documentation",
                    "why_needed": why_needed,
                    "cases_resolved": ["LC-ASSET-01"],
                    "effort": "HIGH",
                    "decision_unlock": decision_unlock,
                    "priority": "HIGH",
                }
            )
        elif cluster in {"control_boundary_cluster", "tenant_control_cluster"}:
            if family == "manufacturing":
                evidence_item = "Process, metering, and operator control-boundary map"
                why_needed = "Distinguishes structural process load from controllable energy, emissions, and reliability interventions."
                decision_unlock = "Unlocks utility optimization, process-efficiency screening, and permit-side interpretation."
            elif family == "logistics":
                evidence_item = "Operating, refrigerated, and metering boundary map"
                why_needed = "Distinguishes landlord-controlled loads from tenant or operator-controlled logistics loads."
                decision_unlock = "Unlocks bounded logistics retrofit and tariff screening."
            else:
                evidence_item = "Tenant metering basis, lease responsibility matrix, and control-boundary map"
                why_needed = "Distinguishes owner-capturable energy or compliance exposure from tenant-controlled behavior."
                decision_unlock = "Unlocks underwriting, compliance, and retrofit screening without overstating controllability."
            rows.append(
                {
                    "evidence_item": evidence_item,
                    "source": "Owner / operator records, lease exhibits, or metering documentation",
                    "why_needed": why_needed,
                    "cases_resolved": ["LC-ASSET-01", "LC-OPS-01"],
                    "effort": "CRITICAL",
                    "decision_unlock": decision_unlock,
                    "priority": "CRITICAL",
                }
            )
    seen: set[str] = {_semantic_key(row.get("evidence_item", "")) for row in rows if row.get("evidence_item")}
    for item in validation_queue[:7]:
        requirement = _normalize_validation_requirement(
            str(item.get("validation_requirement", "")).strip(),
            target_type,
        )
        semantic_requirement = _semantic_key(requirement)
        if not requirement or semantic_requirement in seen:
            continue
        seen.add(semantic_requirement)
        case_id = item.get("case_id", "")
        case = next((r for r in inference_records if r.get("case_id") == case_id), {})
        action = "Request from owner / operator" if case_id == "LC-ASSET-01" else "Obtain targeted validation evidence"
        rows.append(
            {
                "evidence_item": requirement,
                "source": action,
                "why_needed": case.get("case_name", item.get("case_name", "")),
                "cases_resolved": [case_id] if case_id else [],
                "effort": _priority_label(item.get("validation_urgency_score", 0)),
                "decision_unlock": (
                    "Unlocks admissible asset-level reading."
                    if case_id == "LC-ASSET-01"
                    else "Reduces uncertainty on a blocked or fragile decision front."
                ),
                "priority": _priority_label(item.get("validation_urgency_score", 0)),
            }
        )
    unique_map: dict[str, dict[str, Any]] = {}
    for row in rows:
        key = _semantic_key(row.get("evidence_item", ""))
        if not key:
            continue
        if key in unique_map:
            unique_map[key] = _merge_row(unique_map[key], row)
            continue
        unique_map[key] = row
    unique_rows = list(unique_map.values())
    unique_rows.sort(key=lambda row: (-_EVIDENCE_EFFORT_RANK.get(str(row.get("effort", "LOW")).upper(), 0), str(row.get("evidence_item", ""))))
    return unique_rows[:7]


def _merge_missing_evidence_register(
    minimum_evidence_unlock_map: list[dict[str, Any]],
    missing_evidence_register: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    def _semantic_key(item: str) -> str:
        text = str(item or "").strip().lower()
        if not text:
            return ""
        if any(signal in text for signal in ("process line", "major energy-using equipment", "controls system inventory")):
            return "systems_inventory"
        if any(signal in text for signal in ("utility bills", "utility / fuel", "fuel profile", "meter map", "metering records")):
            return "utility_fuel_records"
        if any(signal in text for signal in ("shift schedule", "throughput profile", "operating schedule", "production calendar")):
            return "operating_profile"
        if any(signal in text for signal in ("gfa", "rentable area", "building area", "site / building area")):
            return "scale_geometry"
        return re.sub(r"[^a-z0-9]+", "_", text).strip("_")

    merged = list(minimum_evidence_unlock_map)
    seen = {_semantic_key(row.get("evidence_item", "")) for row in merged if row.get("evidence_item")}
    for missing in missing_evidence_register:
        evidence_item = str(missing.get("minimum_evidence_needed", "")).strip()
        semantic = _semantic_key(evidence_item)
        if not evidence_item or semantic in seen:
            continue
        seen.add(semantic)
        merged.append(
            {
                "evidence_item": evidence_item,
                "source": missing.get("suggested_source", ""),
                "why_needed": missing.get("why_it_matters", ""),
                "cases_resolved": [str(missing.get("decision_blocked", "")).strip()] if missing.get("decision_blocked") else [],
                "effort": "CRITICAL",
                "priority": "CRITICAL",
                "decision_unlock": f"Reduces uncertainty on {missing.get('decision_blocked', 'a blocked decision front')}.",
                "missing_field": missing.get("missing_field", ""),
                "related_cluster": missing.get("related_cluster", ""),
            }
        )
    return merged[:10]


def _merge_structural_discrimination_register(
    minimum_evidence_unlock_map: list[dict[str, Any]],
    minimum_evidence_for_discrimination_register: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    merged = list(minimum_evidence_unlock_map)
    seen = {
        re.sub(r"[^a-z0-9]+", "_", str(row.get("evidence_item", "")).strip().lower()).strip("_")
        for row in merged
        if str(row.get("evidence_item", "")).strip()
    }
    structural_rows: list[dict[str, Any]] = []
    for row in minimum_evidence_for_discrimination_register:
        evidence_item = str(row.get("minimum_evidence", "")).strip()
        if not evidence_item:
            continue
        semantic = re.sub(r"[^a-z0-9]+", "_", evidence_item.lower()).strip("_")
        if semantic in seen:
            continue
        seen.add(semantic)
        structural_rows.append(
            {
                "evidence_item": evidence_item,
                "source": str(row.get("source", "")).strip(),
                "why_needed": "Discriminates between rival hypotheses: " + ", ".join(
                    str(item).strip()
                    for item in list(row.get("rival_hypotheses", []) or [])
                    if str(item).strip()
                ),
                "cases_resolved": ["STRUCTURAL-PROBLEM-FRAME"],
                "effort": "CRITICAL",
                "priority": "CRITICAL",
                "decision_unlock": str(row.get("unlocks", "")).strip(),
                "structural_discrimination": True,
            }
        )
    return (structural_rows + merged)[:10]


def _prepend_structural_next_best_questions(
    next_best_questions: list[dict[str, Any]],
    minimum_evidence_for_discrimination_register: list[dict[str, Any]],
    canonical_problem_frame: dict[str, Any],
) -> list[dict[str, Any]]:
    if not minimum_evidence_for_discrimination_register:
        return next_best_questions
    seeded: list[dict[str, Any]] = []
    seen_questions = {
        str(row.get("question", "")).strip().lower()
        for row in next_best_questions
        if str(row.get("question", "")).strip()
    }
    for idx, row in enumerate(minimum_evidence_for_discrimination_register[:2], start=1):
        rival_hypotheses = [
            str(item).strip()
            for item in list(row.get("rival_hypotheses", []) or [])
            if str(item).strip()
        ]
        question = (
            "Which rival structural hypothesis is true: " + " vs ".join(rival_hypotheses)
            if rival_hypotheses
            else "What minimum evidence discriminates the current structural problem frame?"
        )
        if question.strip().lower() in seen_questions:
            continue
        seen_questions.add(question.strip().lower())
        seeded.append(
            {
                "question_id": f"SQ-{idx:02d}",
                "question": question,
                "urgency": "HIGH",
                "linked_case": "STRUCTURAL-PROBLEM-FRAME",
                "why_it_matters": str(
                    canonical_problem_frame.get("reframed_problem", "")
                    or row.get("what_it_falsifies", "")
                    or "Structural problem framing is still unresolved."
                ).strip(),
                "how_to_answer": "Provide "
                + str(row.get("minimum_evidence", "")).strip()
                + (
                    f" from {str(row.get('source', '')).strip()}."
                    if str(row.get("source", "")).strip()
                    else "."
                ),
            }
        )
    return seeded + next_best_questions


def _structural_reasoning_path(
    canonical_problem_frame: dict[str, Any],
    dominant_variable_register: list[dict[str, Any]],
    cross_layer_conflict_register: list[dict[str, Any]],
    minimum_evidence_for_discrimination_register: list[dict[str, Any]],
) -> dict[str, Any]:
    dominant_variables = [
        str(row.get("variable", "")).strip()
        for row in dominant_variable_register
        if str(row.get("variable", "")).strip()
        and str(row.get("evidence_state", "")).strip() in {"OBSERVED_FACT", "CONDITIONAL_HYPOTHESIS", "ARCHETYPAL_PRIOR", "WEAK_SIGNAL"}
    ][:5]
    return {
        "reasoning_path": str(canonical_problem_frame.get("reasoning_path", "")).strip() or "legacy_decision_gating_only",
        "problem_frame_active": bool(canonical_problem_frame.get("problem_frame_active", False)),
        "reframed_problem": str(canonical_problem_frame.get("reframed_problem", "")).strip(),
        "dominant_conflict": str(canonical_problem_frame.get("dominant_conflict", "")).strip(),
        "dominant_variables": dominant_variables,
        "minimum_evidence_to_discriminate": str(canonical_problem_frame.get("minimum_evidence_to_discriminate", "")).strip(),
        "conflict_count": len(cross_layer_conflict_register),
        "discrimination_path_count": len(minimum_evidence_for_discrimination_register),
    }


def _build_decision_front_register(
    asset_name: str,
    conflict_register: list[dict[str, Any]],
    validation_queue: list[dict[str, Any]],
    missing_clusters: list[str],
    regulatory_flags: list[str],
    target_type: str,
    target_admissibility_state: str,
    subject_gate_passed: bool,
) -> list[dict[str, Any]]:
    asset_blocked = any(c.get("inference_case_id") == "LC-ASSET-01" for c in conflict_register)
    top_requirement = validation_queue[0].get("validation_requirement", "") if validation_queue else ""
    family = _target_family(target_type)
    subject_blocked = (not subject_gate_passed) or target_admissibility_state in {
        "issuer_context_only",
        "address_candidate_only",
        "site_candidate_only",
    }
    if family == "logistics":
        fronts = [
            {
                "decision_front": "Operational or refrigeration retrofit CAPEX",
                "current_status": "NO-GO" if asset_blocked else "VALIDATE FIRST",
                "why": "Throughput profile, controls, and key systems remain insufficiently bounded.",
                "required_evidence": top_requirement or "System inventory + utility / fuel profile + throughput schedule",
                "admissible_action": "Do not underwrite logistics-efficiency or refrigeration CAPEX until operating evidence is confirmed.",
            },
            {
                "decision_front": "Throughput or dock-efficiency intervention",
                "current_status": "VALIDATE FIRST",
                "why": "Operating windows, dock cycles, and control boundary remain only partially characterized.",
                "required_evidence": "Operating schedule + dock activity profile + control boundary",
                "admissible_action": "Request evidence; keep operational-improvement logic bounded to screening.",
            },
            {
                "decision_front": "Compliance investment",
                "current_status": "VALIDATE FIRST" if regulatory_flags else "INVESTIGATE THEN DECIDE",
                "why": "Regulatory posture is still screening-grade and depends on missing local fields.",
                "required_evidence": "Current compliance filing + area basis + utility / fuel profile",
                "admissible_action": "Screen only; avoid compliance-closing claims.",
            },
            {
                "decision_front": "Seller / operator evidence request",
                "current_status": "ACT NOW",
                "why": "The immediate decision is which logistics records must be requested, not whether to close a CAPEX thesis.",
                "required_evidence": "Minimum evidence pack",
                "admissible_action": "Issue a targeted owner/operator data request immediately.",
            },
        ]
    elif family == "manufacturing":
        fronts = [
            {
                "decision_front": "Process efficiency or utility-support CAPEX",
                "current_status": "DEFER" if asset_blocked else "VALIDATE FIRST",
                "why": "Process duty, operating schedule, and system inventory remain insufficiently bounded.",
                "required_evidence": top_requirement or "Process inventory + utility / fuel profile + throughput data",
                "admissible_action": "Do not underwrite process-efficiency CAPEX until process and utility evidence is confirmed.",
                "prohibited_action": "Do not commit process-efficiency or utility-support CAPEX under current evidence.",
            },
            {
                "decision_front": "Reliability or modernization intervention",
                "current_status": "INVESTIGATE THEN DECIDE" if asset_blocked else "VALIDATE FIRST",
                "why": "Critical support systems and uptime dependencies are still archetypal rather than confirmed.",
                "required_evidence": "Process-support system inventory + maintenance / reliability history",
                "admissible_action": "Request evidence; keep modernization logic bounded to screening.",
                "prohibited_action": "Do not commit reliability or modernization capital before critical-system evidence is confirmed.",
            },
            {
                "decision_front": "Utility cost optimization",
                "current_status": "DEFER" if asset_blocked else "VALIDATE FIRST",
                "why": "Utility tariff, metering basis, and process load drivers remain insufficiently bounded.",
                "required_evidence": "Utility bills + tariff context + meter map + throughput / schedule profile",
                "admissible_action": "Use this front to request utility and tariff evidence before asserting cost-optimization upside.",
                "prohibited_action": "Do not commit utility-cost optimization claims or actions before utility and process evidence are confirmed.",
            },
            {
                "decision_front": "Environmental or permit-driven investment",
                "current_status": "VALIDATE FIRST" if regulatory_flags else "INVESTIGATE THEN DECIDE",
                "why": "Permit or compliance exposure is still screening-grade and depends on missing local fields.",
                "required_evidence": "Current permit/compliance filing + fuel / emissions basis + throughput context",
                "admissible_action": "Screen only; avoid compliance-closing or emissions-cost claims.",
                "prohibited_action": "Do not close permit, emissions-cost, or compliance-investment decisions under current evidence.",
            },
            {
                "decision_front": "Process redesign",
                "current_status": "NO-GO",
                "why": "No defensible process-redesign posture exists until process map, throughput, and control boundary are confirmed.",
                "required_evidence": "Process map + throughput profile + control boundary + downtime tolerance",
                "admissible_action": "Do not redesign the process. First bound the process and request the missing operator evidence.",
                "prohibited_action": "Do not issue any process-redesign recommendation until process flow and throughput evidence are confirmed.",
            },
            {
                "decision_front": "Operator evidence request",
                "current_status": "ACT NOW",
                "why": "The immediate decision is which plant records must be requested before stronger action is admissible.",
                "required_evidence": "Minimum evidence pack",
                "admissible_action": "Issue a targeted owner/operator data request immediately.",
                "prohibited_action": "Do not substitute operator records with benchmark or proxy evidence.",
            },
        ]
    elif family == "infrastructure":
        fronts = [
            {
                "decision_front": "Reliability or conversion-loss intervention",
                "current_status": "NO-GO" if asset_blocked else "VALIDATE FIRST",
                "why": "Duty drivers, control boundary, and major equipment inventory are still not fully bounded.",
                "required_evidence": top_requirement or "Major equipment inventory + duty / dispatch profile + meter basis",
                "admissible_action": "Do not advance reliability or loss-reduction CAPEX without confirming asset topology and duty.",
            },
            {
                "decision_front": "Capacity or resilience capital",
                "current_status": "VALIDATE FIRST",
                "why": "Redundancy, outage tolerance, and operating boundary remain insufficiently evidenced.",
                "required_evidence": "One-line or layout boundary + redundancy basis + service profile",
                "admissible_action": "Request engineering and operating evidence; keep resilience logic screening-grade.",
            },
            {
                "decision_front": "Environmental or permit-driven upgrade",
                "current_status": "VALIDATE FIRST" if regulatory_flags else "INVESTIGATE THEN DECIDE",
                "why": "Current regulatory posture is still screening-grade and depends on local reporting fields.",
                "required_evidence": "Current compliance filing + station-service / fuel basis + in-scope equipment list",
                "admissible_action": "Screen only; avoid compliance-closing or transition-cost claims.",
            },
            {
                "decision_front": "Operator evidence request",
                "current_status": "ACT NOW",
                "why": "The immediate decision is which topology, duty, and metering records must be requested.",
                "required_evidence": "Minimum evidence pack",
                "admissible_action": "Issue a targeted operator data request immediately.",
            },
        ]
    elif family == "oil_gas":
        fronts = [
            {
                "decision_front": "Process, emissions, or efficiency CAPEX",
                "current_status": "NO-GO" if asset_blocked else "VALIDATE FIRST",
                "why": "Process-unit duty, fuel basis, and emissions boundary are still not adequately bounded.",
                "required_evidence": top_requirement or "Process-unit inventory + throughput profile + fuel / emissions basis",
                "admissible_action": "Do not underwrite process or emissions-reduction CAPEX until unit-level evidence is confirmed.",
            },
            {
                "decision_front": "Reliability or throughput intervention",
                "current_status": "VALIDATE FIRST",
                "why": "Rotating equipment, thermal duty, and turnaround constraints remain only partially characterized.",
                "required_evidence": "Major unit inventory + reliability history + turnaround / throughput context",
                "admissible_action": "Request engineering evidence; keep intervention logic bounded to screening.",
            },
            {
                "decision_front": "Permit, compliance, or transition investment",
                "current_status": "VALIDATE FIRST" if regulatory_flags else "INVESTIGATE THEN DECIDE",
                "why": "Environmental and transition exposure is still screening-grade and depends on missing local operating fields.",
                "required_evidence": "Current permit/compliance filing + emissions basis + fuel / flare / steam context",
                "admissible_action": "Screen only; avoid compliance-closing or transition-cost claims.",
            },
            {
                "decision_front": "Operator evidence request",
                "current_status": "ACT NOW",
                "why": "The immediate decision is which process, emissions, and throughput records must be requested.",
                "required_evidence": "Minimum evidence pack",
                "admissible_action": "Issue a targeted operator data request immediately.",
            },
        ]
    else:
        fronts = [
        {
            "decision_front": "Acquisition underwriting with energy upside",
            "current_status": "NO-GO" if asset_blocked else "VALIDATE FIRST",
            "why": (
                "Asset physical and operating substrate remains incomplete."
                if asset_blocked
                else "Asset context remains insufficient for defendable upside."
            ),
            "required_evidence": top_requirement or "Minimum evidence pack",
            "admissible_action": "Remove upside from model until asset evidence is confirmed.",
        },
        {
            "decision_front": "Energy retrofit CAPEX",
            "current_status": "VALIDATE FIRST",
            "why": "Systems, load profile, and controllability boundary are not yet confirmed.",
            "required_evidence": "System inventory + utility data + operating schedule",
            "admissible_action": "Request evidence; do not underwrite retrofit economics yet.",
        },
        {
            "decision_front": "Compliance investment",
            "current_status": "VALIDATE FIRST" if regulatory_flags else "INVESTIGATE THEN DECIDE",
            "why": "Regulatory exposure is still screening-grade and depends on missing local fields.",
            "required_evidence": "Current compliance filing + GFA + fuel / utility profile",
            "admissible_action": "Screen only; avoid compliance-closing claims.",
        },
        {
            "decision_front": "Seller / operator evidence request",
            "current_status": "ACT NOW",
            "why": "The immediate decision is what to request, not what to invest in.",
            "required_evidence": "Minimum evidence pack",
            "admissible_action": "Issue a targeted evidence request immediately.",
        },
        ]
    if missing_clusters:
        fronts.append(
            {
                "decision_front": "Full technical diligence scope",
                "current_status": "DEFER",
                "why": "Minimum evidence pack should be resolved before broad diligence expansion.",
                "required_evidence": "Top blocking fields and subject-to-asset confirmation",
                "admissible_action": "Sequence minimum pack first; avoid over-auditing.",
            }
        )
    if subject_blocked:
        identity_front = {
            "decision_front": "Asset identity and admissibility confirmation",
            "current_status": "ACT NOW",
            "why": (
                "The current subject is not yet a bounded asset. Address-level or site-candidate context is insufficient for stronger technical or capital interpretation."
            ),
            "required_evidence": "Address-to-asset confirmation + minimum evidence pack",
            "admissible_action": "Issue an asset-confirmation and evidence request immediately before advancing any capital-facing logic.",
        }
        hardened_fronts: list[dict[str, Any]] = [identity_front]
        for front in fronts:
            name = str(front.get("decision_front", "")).lower()
            if "evidence request" in name or "asset identity" in name:
                hardened_fronts.append(
                    {
                        **front,
                        "current_status": "ACT NOW",
                        "why": "The only immediate admissible action is to request the minimum evidence pack and confirm that the target is a bounded asset.",
                        "required_evidence": "Address-to-asset confirmation + minimum evidence pack",
                        "admissible_action": "Send a targeted owner / operator evidence request now.",
                    }
                )
                continue
            if "full technical diligence" in name:
                hardened_fronts.append(
                    {
                        **front,
                        "current_status": "DEFER",
                        "why": "Broad diligence should not start before the target is confirmed as a bounded asset and the minimum evidence pack is received.",
                        "required_evidence": "Address-to-asset confirmation + minimum evidence pack",
                        "admissible_action": "Defer broad diligence. Resolve asset identity and minimum evidence first.",
                    }
                )
                continue
            if any(token in name for token in ("compliance", "permit", "regulatory")):
                hardened_fronts.append(
                    {
                        **front,
                        "current_status": "VALIDATE FIRST",
                        "why": "Regulatory screening may continue, but no compliance-facing interpretation is admissible until the target is bounded and local evidence is received.",
                        "required_evidence": "Address-to-asset confirmation + current compliance filing + in-scope boundary",
                        "admissible_action": "Keep this front at screening level and request the missing evidence first.",
                    }
                )
                continue
            hardened_fronts.append(
                {
                    **front,
                    "current_status": "NO-GO",
                    "why": "The subject is not yet a bounded asset. Capital-facing or intervention-facing interpretation would over-read address-level context.",
                    "required_evidence": "Address-to-asset confirmation + minimum evidence pack",
                    "admissible_action": "Do not advance this decision front. First confirm the asset and request the minimum evidence pack.",
                }
            )
        fronts = hardened_fronts
    return fronts


def _map_decision_front_to_permission_key(decision_front: str) -> str:
    name = str(decision_front or "").strip().lower()
    if "asset identity" in name:
        return "asset_identity_confirmation"
    if "seller / operator evidence request" in name or "operator evidence request" in name:
        return "seller_or_operator_evidence_request"
    if "acquisition underwriting" in name:
        return "acquisition_underwriting_with_energy_upside"
    if "compliance investment" in name or "permit, compliance" in name or "environmental or permit-driven investment" in name:
        return "compliance_investment"
    if "process efficiency" in name or "energy retrofit capex" in name or "operational or refrigeration retrofit capex" in name or "reliability or conversion-loss intervention" in name or "process, emissions, or efficiency capex" in name or "utility cost optimization" in name:
        return "retrofit_capex"
    if "process redesign" in name or "throughput or dock-efficiency intervention" in name or "reliability or modernization intervention" in name or "reliability or throughput intervention" in name:
        return "process_redesign"
    return ""


def _status_from_permission(permission_state: str, allowed_action: str, current_status: str) -> str:
    state = str(permission_state or "").lower()
    action = str(allowed_action or "").upper()
    if action in {"ACT NOW", "REQUEST EVIDENCE"}:
        return "ACT NOW"
    if str(current_status or "").upper() == "NO-GO" and state != "allowed":
        return "NO-GO"
    if state == "allowed":
        return current_status or "INVESTIGATE THEN DECIDE"
    if state == "conditional":
        return "VALIDATE FIRST"
    if state == "deferred":
        return "DEFER"
    if state == "prohibited":
        return "NO-GO"
    return current_status


def _overlay_decision_permissions(
    decision_front_register: list[dict[str, Any]],
    decision_permission_register: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    permission_map = {
        str(row.get("decision_name", "")).strip(): row
        for row in decision_permission_register
        if str(row.get("decision_name", "")).strip()
    }
    overlaid: list[dict[str, Any]] = []
    for front in decision_front_register:
        key = _map_decision_front_to_permission_key(front.get("decision_front", ""))
        permission = permission_map.get(key)
        if not permission:
            overlaid.append(front)
            continue
        current_status = _status_from_permission(
            permission.get("admissibility_state", ""),
            permission.get("allowed_action", ""),
            str(front.get("current_status", "")),
        )
        evidence_needed = permission.get("evidence_needed", [])
        existing_required = str(front.get("required_evidence", "")).strip()
        front_required = existing_required
        if evidence_needed:
            front_required = " + ".join(str(item).strip() for item in evidence_needed if str(item).strip()) or existing_required
        why = str(front.get("why", "")).strip()
        bottleneck = str(permission.get("current_variable_bottleneck", "")).strip()
        if bottleneck:
            why = f"{why} Variable bottleneck: {bottleneck}."
        overlaid.append(
            {
                **front,
                "current_status": current_status,
                "required_evidence": front_required,
                "maturity_decision_name": key,
                "maturity_admissibility_state": permission.get("admissibility_state", ""),
                "variable_bottleneck": bottleneck,
                "evidence_permission_basis": evidence_needed,
                "allowed_action_by_maturity": permission.get("allowed_action", ""),
                "why": why,
            }
        )
    return overlaid


def _build_variable_bottleneck_register(
    decision_permission_register: list[dict[str, Any]],
    variable_maturity_register: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    maturity_lookup = {
        str(row.get("variable_name", "")).strip(): row
        for row in variable_maturity_register
        if str(row.get("variable_name", "")).strip()
    }
    rows: list[dict[str, Any]] = []
    for permission in decision_permission_register:
        bottleneck = str(permission.get("current_variable_bottleneck", "")).strip()
        if not bottleneck:
            continue
        variable_row = maturity_lookup.get(bottleneck, {})
        rows.append(
            {
                "decision_name": permission.get("decision_name", ""),
                "admissibility_state": permission.get("admissibility_state", ""),
                "variable_name": bottleneck,
                "maturity_level": variable_row.get("maturity_level", 0),
                "uncertainty_reason": variable_row.get("uncertainty_reason", ""),
                "evidence_needed": permission.get("evidence_needed", []),
                "allowed_action": permission.get("allowed_action", ""),
            }
        )
    return rows


def _build_claim_permission_summary(claim_permission_register: list[dict[str, Any]]) -> dict[str, Any]:
    summary = {
        "allowed": 0,
        "allowed_count": 0,
        "conditional": 0,
        "conditional_count": 0,
        "prohibited": 0,
        "prohibited_count": 0,
        "deferred": 0,
        "blocked_claims": [],
    }
    for row in claim_permission_register:
        state = str(row.get("current_permission", "")).lower()
        if state in summary:
            summary[state] += 1
        count_key = f"{state}_count"
        if count_key in summary:
            summary[count_key] += 1
        if state in {"prohibited", "deferred"}:
            summary["blocked_claims"].append(
                {
                    "claim_name": row.get("claim_name", ""),
                    "reason": row.get("reason_if_blocked", ""),
                }
            )
    return summary


def _find_evidence_item(
    minimum_evidence_unlock_map: list[dict[str, Any]],
    *signals: str,
) -> str:
    signal_tokens = [str(signal).strip().lower() for signal in signals if str(signal).strip()]
    for row in minimum_evidence_unlock_map:
        item = str(row.get("evidence_item", "")).strip()
        lowered = item.lower()
        if item and any(token in lowered for token in signal_tokens):
            return item
    return ""


def _find_decision_front(
    decision_front_register: list[dict[str, Any]],
    *signals: str,
) -> str:
    signal_tokens = [str(signal).strip().lower() for signal in signals if str(signal).strip()]
    for row in decision_front_register:
        front = str(row.get("decision_front", "")).strip()
        lowered = front.lower()
        if front and any(token in lowered for token in signal_tokens):
            return front
    return ""


def _build_financial_exposure_register(
    target_type: str,
    regulatory_flags: list[str],
    minimum_evidence_unlock_map: list[dict[str, Any]],
    decision_front_register: list[dict[str, Any]],
) -> list[dict[str, str]]:
    family = _target_family(target_type)
    if family == "manufacturing":
        return [
            {
                "assumption": "Observed energy intensity is correctable support-system waste rather than structural resin, press, curing, or thermal-process duty",
                "current_support": "Plausible but unsupported until process-family, press / curing inventory, throughput, and utility basis are confirmed.",
                "downside_if_wrong": "CAPEX targets structural process chemistry or thermal duty and fails to create defendable savings.",
                "evidence_needed": " + ".join(
                    item for item in [
                        _find_evidence_item(minimum_evidence_unlock_map, "naics / sic", "process narrative"),
                        _find_evidence_item(minimum_evidence_unlock_map, "resin / adhesive", "curing or thermal-process", "presses"),
                        _find_evidence_item(minimum_evidence_unlock_map, "throughput profile", "shift schedule"),
                        _find_evidence_item(minimum_evidence_unlock_map, "steam / boilers / thermal oil", "utility bills"),
                    ] if item
                ),
                "financial_consequence": "Defer process-efficiency CAPEX and remove savings logic from screening until process duty and thermal load drivers are validated.",
                "linked_decision_front": _find_decision_front(decision_front_register, "process efficiency", "utility cost optimization"),
            },
            {
                "assumption": "Utility cost optimization is actionable without compressed-air, dust / VOC, thermal, and control-boundary detail",
                "current_support": "Unsupported while tariff basis, metering map, support-system topology, and control boundary remain incomplete.",
                "downside_if_wrong": "Optimization effort focuses on the wrong meters, wrong tariff class, wrong utility island, or uncontrollable environmental-support load.",
                "evidence_needed": " + ".join(
                    item for item in [
                        _find_evidence_item(minimum_evidence_unlock_map, "utility / fuel", "meter map"),
                        _find_evidence_item(minimum_evidence_unlock_map, "compressed-air", "dust collection", "voc capture"),
                        _find_evidence_item(minimum_evidence_unlock_map, "control boundary"),
                    ] if item
                ),
                "financial_consequence": "Keep utility-cost optimization at validate-first; do not book cost-down upside into capital framing.",
                "linked_decision_front": _find_decision_front(decision_front_register, "utility cost optimization"),
            },
            {
                "assumption": "Permit, VOC, wastewater, or emissions exposure justifies near-term investment",
                "current_support": "Screening-grade only." if regulatory_flags else "Possible but unsupported without stronger local evidence.",
                "downside_if_wrong": "Capital is justified on regulatory pressure that is weaker, later, differently scoped, or attached to another line or utility island.",
                "evidence_needed": " + ".join(
                    item for item in [
                        _find_evidence_item(minimum_evidence_unlock_map, "air, wastewater, and emissions permit"),
                        _find_evidence_item(minimum_evidence_unlock_map, "steam / boilers / thermal oil", "utility / fuel"),
                        _find_evidence_item(minimum_evidence_unlock_map, "resin / adhesive", "throughput profile"),
                    ] if item
                ) or "Current permit / compliance filing + air / wastewater basis + thermal and process-duty context",
                "financial_consequence": "Restrict environmental or permit-driven investment to validate-first screening until permit scope, emissions basis, and process duty are confirmed.",
                "linked_decision_front": _find_decision_front(decision_front_register, "environmental or permit-driven investment"),
            },
        ]
    if family == "building":
        return [
            {
                "assumption": "Owner-controllable energy upside exists within the central plant and common-area systems rather than mainly in tenant-controlled loads",
                "current_support": "Unsupported until tenant metering basis, lease responsibility, central-plant topology, and utility basis are confirmed.",
                "downside_if_wrong": "Retrofit CAPEX does not improve owner economics even if site energy falls because the dominant load sits in tenant space or outside the owner's control boundary.",
                "evidence_needed": " + ".join(
                    item for item in [
                        _find_evidence_item(minimum_evidence_unlock_map, "utility bills", "utility / fuel"),
                        _find_evidence_item(minimum_evidence_unlock_map, "central plant", "hvac", "bms"),
                        _find_evidence_item(minimum_evidence_unlock_map, "tenant metering", "lease responsibility", "control boundary"),
                    ] if item
                ),
                "financial_consequence": "Remove energy upside from underwriting until controllability and meter responsibility are validated.",
                "linked_decision_front": _find_decision_front(decision_front_register, "acquisition underwriting", "energy retrofit"),
            },
            {
                "assumption": "Public geometry, rule pathway, and fuel-transition context are sufficient for compliance screening",
                "current_support": "Supported for screening only when geometry, identity, regulatory, and major fuel-pathway clusters are public-strong.",
                "downside_if_wrong": "Compliance effort is sized against the wrong boundary, floor area, fuel pathway, or applicable rule family.",
                "evidence_needed": " + ".join(
                    item for item in [
                        _find_evidence_item(minimum_evidence_unlock_map, "gfa", "rentable area", "building area"),
                        _find_evidence_item(minimum_evidence_unlock_map, "steam, gas, district energy, or electrification basis"),
                    ] if item
                ) or "Current compliance filing + GFA + major fuel / utility basis",
                "financial_consequence": "Allow screening-grade compliance review, but do not close penalties, budgets, or compliance posture until filing-grade and fuel-basis evidence arrives.",
                "linked_decision_front": _find_decision_front(decision_front_register, "compliance investment"),
            },
            {
                "assumption": "Energy or emissions screening can support capital framing before bills arrive because occupancy, use mix, and meter responsibility are directionally stable",
                "current_support": "Partial: public benchmarking may support screening, not ROI or savings claims, and only if use mix and metering logic are not badly misread.",
                "downside_if_wrong": "Underwriting overstates penalty avoidance, savings, or asset differentiation because after-hours loads, tenant use mix, or central plant burden are misallocated.",
                "evidence_needed": " + ".join(
                    item for item in [
                        _find_evidence_item(minimum_evidence_unlock_map, "utility bills", "utility / fuel"),
                        _find_evidence_item(minimum_evidence_unlock_map, "occupancy / use mix", "operating schedule"),
                        _find_evidence_item(minimum_evidence_unlock_map, "tenant metering", "lease responsibility"),
                    ] if item
                ),
                "financial_consequence": "Keep the case at compliance / investment screening; block ROI, savings, and retrofit economics until local operating evidence is received.",
                "linked_decision_front": _find_decision_front(decision_front_register, "acquisition underwriting", "energy retrofit", "compliance investment"),
            },
        ]
    return [
        {
            "assumption": "Current public evidence is sufficient to support intervention logic",
            "current_support": "Partial and case-dependent; major technical clusters remain incomplete.",
            "downside_if_wrong": "Capital or diligence expands against the wrong technical bottleneck.",
            "evidence_needed": minimum_evidence_unlock_map[0]["evidence_item"] if minimum_evidence_unlock_map else "Minimum evidence pack",
            "financial_consequence": "Keep intervention logic bounded to screening until the top evidence gaps are resolved.",
            "linked_decision_front": decision_front_register[0]["decision_front"] if decision_front_register else "",
        }
    ]


# ──────────────────────────────────────────────────────────────────────────
# AI-SCAFFOLDING — see AI_SCAFFOLDING_REGISTRY.md entry S1
# Hardcoded 24-entry justification table written by Claude in V2-LIVE.
# DO NOT EXPAND. New scenarios/families MUST be generated by the framework
# (motor_014 deriving from missing_clusters, motor_035 routing, active
# patterns, and knowledge YAMLs) — not by adding rows here.
# Frozen at 24 entries (6 families × 4 letters). Will be replaced by V4
# Industrial Research Engine.
# ──────────────────────────────────────────────────────────────────────────
_SCENARIO_JUSTIFICATION: dict[tuple[str, str], dict[str, str]] = {
    # logistics (warehouse / cold-chain / DC)
    ("logistics", "A"): {
        "trigger": "Operating schedule + throughput profile + dock-cycle pattern not yet bounded.",
        "source": "doe_eere_mhe; werc_dc_measures; ashrae_handbook_hvac_applications_ch24",
        "process_clue": "MHE charging windows, dock-door cycles and refrigeration duty are the structural energy carriers in logistics assets.",
        "industrial_reason": "Generic per-sf benchmarks misrepresent logistics energy intensity until throughput and dock cycles are characterized.",
        "asset_family_reason": "Logistics nodes (warehouse, fulfillment, cold-chain DC) are throughput-driven assets; energy use tracks operations, not floor area.",
    },
    ("logistics", "B"): {
        "trigger": "Controls/maintenance/dock-air evidence unresolved.",
        "source": "doe_eere_mhe; epri_battery_charging; gcca_energy_excellence_toolkit",
        "process_clue": "Avoidable losses concentrate in idle MHE charging, dock infiltration, refrigeration controls and after-hours operation.",
        "industrial_reason": "Targeted operational corrections in logistics deliver bounded upside without redesigning the throughput envelope.",
        "asset_family_reason": "Logistics families show repeatable controls-and-maintenance failure modes documented across DC measures benchmarks.",
    },
    ("logistics", "C"): {
        "trigger": "Local compliance filing (LL97/BERDO/Title 24) status and area basis unverified.",
        "source": "nyc_ll97; boston_berdo; ca_title24_part6; epa_ghgrp",
        "process_clue": "Local performance/emissions standards convert kWh into either penalty exposure or compliance ceiling.",
        "industrial_reason": "Compliance posture can dominate logistics capital logic when filings show material trigger.",
        "asset_family_reason": "Cold-chain/warehouse facilities in regulated jurisdictions face direct emissions caps independent of operational savings.",
    },
    ("logistics", "D"): {
        "trigger": "Critical observable clusters (geometry, schedule, system inventory, utility evidence) remain missing.",
        "source": "iso_50002; ashrae_211",
        "process_clue": "Without minimum evidence pack, dominant variable cannot be discriminated; any single-cause framing is premature.",
        "industrial_reason": "Energy-audit standards (ISO 50002, ASHRAE 211) require minimum evidence before defendable hypothesis ranking.",
        "asset_family_reason": "Logistics asset family is heterogeneous (dry / refrigerated / cold / fulfillment); characterization must precede comparison.",
    },
    # manufacturing
    ("manufacturing", "A"): {
        "trigger": "NAICS/SIC, process narrative, press/curing inventory, thermal-utility basis not yet bounded.",
        "source": "doe_amo_best_practices; doe_iac_database; eia_mecs; sme_handbook",
        "process_clue": "Thermal-process duty (presses, curing ovens, resin, thermal oil) is structural to product quality and chemistry, not adjustable through generic efficiency moves.",
        "industrial_reason": "DOE AMO and IAC datasets show process duty dominates manufacturing energy; misreading it produces wrong-target CAPEX.",
        "asset_family_reason": "Manufacturing facilities are process-driven; the dominant variable is the production line, not the building envelope.",
    },
    ("manufacturing", "B"): {
        "trigger": "Shift calendar + compressed-air/dust-collection/VOC support inventory + downtime maintenance basis unresolved.",
        "source": "doe_compressed_air_challenge; cagi_compressed_air_handbook; doe_steam_system_sourcebook; doe_pump_system_sourcebook",
        "process_clue": "Support systems (compressed air, dust collection, steam traps, idle-line operation) typically waste 20-40% of generated utility before reaching production.",
        "industrial_reason": "DOE support-system sourcebooks document repeatable, bounded operational interventions that do not redesign the core process.",
        "asset_family_reason": "Manufacturing support systems share common failure modes (leaks, idle, mis-staged compressors) regardless of end-product.",
    },
    ("manufacturing", "C"): {
        "trigger": "Air/wastewater/VOC permit basis + emissions profile + thermal-duty link unverified.",
        "source": "epa_rmp; osha_psm; epa_ghgrp; calarp",
        "process_clue": "Permit, abatement, and thermal-emissions exposure can dominate capital logic via avoided penalty, RMP requirements, or abatement-system retrofit.",
        "industrial_reason": "Process safety and environmental regulations (RMP §112(r), PSM 1910.119, GHGRP) impose capital triggers independent of efficiency.",
        "asset_family_reason": "Manufacturing facilities with thermal/chemical processes face concentrated regulatory exposure not present in commercial/logistics families.",
    },
    ("manufacturing", "D"): {
        "trigger": "Process family, thermal duty, utility profile, schedule fields not yet populated.",
        "source": "iso_50002; doe_iac_database",
        "process_clue": "Cannot rank process-energy hypotheses without geometry + process inventory + throughput + thermal evidence.",
        "industrial_reason": "ISO 50002 minimum-evidence requirements and DOE IAC assessment protocol both reject single-variable claims absent process characterization.",
        "asset_family_reason": "Manufacturing characterization requires NAICS-level process logic before any cross-asset comparison is defendable.",
    },
    # commercial building
    ("building", "A"): {
        "trigger": "Lease responsibility split, central-plant inventory, common-area meter coverage not yet bounded.",
        "source": "ashrae_90_1; ashrae_handbook_hvac_systems; boma_eer",
        "process_clue": "Central HVAC, chillers, boilers, and common-area lighting are owner-controlled; their economics accrue to the owner P&L.",
        "industrial_reason": "BOMA EER + ASHRAE 90.1 frame owner-controllable energy as the underwritable boundary in commercial real estate.",
        "asset_family_reason": "Commercial buildings split economics between owner and tenant; CAPEX logic must respect the lease responsibility boundary.",
    },
    ("building", "B"): {
        "trigger": "Occupancy/use mix + operating schedule + tenant utility split unresolved.",
        "source": "uli_tenant_energy; cushman_wakefield_workplace; cbre_sustainability",
        "process_clue": "Tenant-driven schedules, after-hours occupancy and use-mix variability frequently dominate office and mixed-use load profiles.",
        "industrial_reason": "ULI Tenant Energy Optimization Program documents repeatable cases where tenant behavior, not building systems, drives the load.",
        "asset_family_reason": "Commercial buildings host heterogeneous tenants; benchmark-based screening overstates owner-actionable upside when tenant load dominates.",
    },
    ("building", "C"): {
        "trigger": "Local rule applicability (LL97/BERDO/BEPS/Title 24) + area thresholds + steam/gas/electrification basis unverified.",
        "source": "nyc_ll97; nyc_ll84; boston_berdo; dc_beps; ca_title24_part6; crrem",
        "process_clue": "Local performance standards convert carbon intensity into penalty exposure (LL97) or stranding risk (CRREM); fuel-transition triggers can dominate retrofit timing.",
        "industrial_reason": "Real-estate decarbonization pathways are now jurisdiction-defined; compliance is no longer optional in major US markets.",
        "asset_family_reason": "Commercial buildings face concentrated, jurisdiction-specific compliance stack absent from other asset families.",
    },
    ("building", "D"): {
        "trigger": "Geometry + schedule + systems + fuel/utility evidence not yet populated.",
        "source": "ashrae_211; energy_star_portfolio_manager; eia_cbecs",
        "process_clue": "Cannot rank retrofit hypotheses without minimum evidence pack covering envelope, systems, and operating profile.",
        "industrial_reason": "ASHRAE 211 (commercial-building audit standard) requires this evidence basis before defendable retrofit recommendation.",
        "asset_family_reason": "Commercial-building heterogeneity (office vs. retail vs. mixed) demands characterization before peer comparison.",
    },
    # infrastructure (utility / rail / energy node)
    ("infrastructure", "A"): {
        "trigger": "Equipment inventory + one-line/layout + duty profile not yet bounded.",
        "source": "ieee_c57; ieee_c37; nesc; neta_standards; ferc_form_1",
        "process_clue": "Topology, dispatch posture, and major-equipment duty drive loss behavior more than generic efficiency levers.",
        "industrial_reason": "NESC/NETA/IEEE standards frame infrastructure energy behavior around topology and duty, not building-style benchmarks.",
        "asset_family_reason": "Infrastructure assets (substations, rail yards, terminals) are duty-and-topology driven, not floor-area driven.",
    },
    ("infrastructure", "B"): {
        "trigger": "Redundancy obligations, outage history, operator control boundary unresolved.",
        "source": "nerc_reliability; aar_field_manual; iso_55000",
        "process_clue": "Resilience/redundancy requirements narrow operational upside; reliability-driven design rejects discretionary savings.",
        "industrial_reason": "NERC reliability standards and AAR field practices constrain operating flexibility independent of efficiency.",
        "asset_family_reason": "Infrastructure assets serve continuous-duty obligations; reliability lock-in dominates discretionary intervention budget.",
    },
    ("infrastructure", "C"): {
        "trigger": "Compliance filing, equipment scope, fuel/station-service basis unverified.",
        "source": "epa_ghgrp; nesc; nerc_reliability",
        "process_clue": "Environmental posture and reporting (GHGRP, NESC) can drive upgrade logic ahead of pure efficiency gains.",
        "industrial_reason": "Infrastructure environmental exposure is reported under federal frameworks distinct from building/commercial regimes.",
        "asset_family_reason": "Utility/transport infrastructure faces sector-specific regulatory stack independent of building codes.",
    },
    ("infrastructure", "D"): {
        "trigger": "Site boundary, topology, duty profile, metering basis not yet populated.",
        "source": "iso_55000; neta_standards",
        "process_clue": "Cannot rank reliability or capacity hypotheses without topology + duty + metering evidence.",
        "industrial_reason": "ISO 55000 asset-management standards require condition + duty evidence before defendable lifecycle decisions.",
        "asset_family_reason": "Infrastructure asset families demand topology-grade characterization before peer benchmarking.",
    },
    # oil & gas (process / refining / midstream)
    ("oil_gas", "A"): {
        "trigger": "Unit inventory + throughput profile + fuel/emissions basis not yet bounded.",
        "source": "api_510; api_570; api_653; epa_ghgrp",
        "process_clue": "Process units, thermal duty, compression, and pumping carry the bulk of energy and emissions exposure.",
        "industrial_reason": "API inspection standards + GHGRP framing show process duty dominates oil & gas energy and emissions.",
        "asset_family_reason": "Oil & gas processing is unit-and-throughput driven; building/commercial benchmarks do not apply.",
    },
    ("oil_gas", "B"): {
        "trigger": "Reliability history + turnaround schedule + operating-unit boundary unresolved.",
        "source": "aiche_ccps; osha_psm; api_510",
        "process_clue": "Uptime, pressure, thermal, and safety lock-in dominate discretionary energy intervention budget.",
        "industrial_reason": "CCPS guidelines and PSM 1910.119 enforce reliability constraints that supersede efficiency moves.",
        "asset_family_reason": "Oil & gas units are continuous-duty with safety-critical reliability; intervention timing tied to turnaround cycle.",
    },
    ("oil_gas", "C"): {
        "trigger": "Permit, emissions, reporting evidence unverified.",
        "source": "epa_ghgrp; osha_psm; api_653",
        "process_clue": "Permit/emissions/transition pressure can drive capital logic ahead of energy savings.",
        "industrial_reason": "Oil & gas decarbonization pathways are jurisdiction-and-product specific (refining vs. midstream vs. upstream).",
        "asset_family_reason": "Oil & gas faces sector-specific regulatory stack (PSM, NSPS, GHGRP) distinct from manufacturing/building regimes.",
    },
    ("oil_gas", "D"): {
        "trigger": "Site boundary + unit inventory + throughput + fuel/emissions fields not yet populated.",
        "source": "iso_50002; iso_55000",
        "process_clue": "Cannot rank process/reliability/compliance hypotheses without unit + throughput + emissions evidence.",
        "industrial_reason": "ISO 50002 + 55000 frame minimum evidence as prerequisite to oil & gas intervention logic.",
        "asset_family_reason": "Oil & gas process characterization is irreducibly unit-specific; generic frames are non-defendable.",
    },
    # fallback (datacenter / unknown)
    ("default", "A"): {
        "trigger": "Owner-controlled central plant + common-area system inventory + lease responsibility not yet bounded.",
        "source": "ashrae_tc99; ashrae_90_4; ashrae_90_1; uptime_tier_standards",
        "process_clue": "Owner-controlled central systems (cooling topology, electrical distribution, BMS) carry the underwritable upside.",
        "industrial_reason": "ASHRAE TC 9.9 + Uptime Tier framing place cooling/power topology at the center of asset economics.",
        "asset_family_reason": "Datacenter and central-plant assets are owner-controlled; tenant variability is bounded by topology.",
    },
    ("default", "B"): {
        "trigger": "Tenant schedule / use mix / after-hours pattern / submetering basis unresolved.",
        "source": "uli_tenant_energy; green_grid_pue",
        "process_clue": "Tenant variability and submetering scope can dominate load profile, weakening owner-actionable upside.",
        "industrial_reason": "Green Grid PUE composition + ULI tenant studies show downstream load behavior is rarely bounded a priori.",
        "asset_family_reason": "Mixed-use and tenant-rich assets require schedule-and-meter characterization before owner-CAPEX logic.",
    },
    ("default", "C"): {
        "trigger": "Local rule applicability + area thresholds + steam/gas/electrification exposure unverified.",
        "source": "nyc_ll97; boston_berdo; ca_title24_part6; epa_ghgrp",
        "process_clue": "Local performance and fuel-transition standards convert energy posture into penalty exposure or stranding risk.",
        "industrial_reason": "Jurisdiction-specific decarbonization pathways are now binding in major US markets.",
        "asset_family_reason": "Asset families subject to LL97/BERDO/BEPS/Title 24 face direct emissions caps that drive capital timing.",
    },
    ("default", "D"): {
        "trigger": "Geometry + schedule + systems + fuel/utility evidence not yet populated.",
        "source": "iso_50002; ashrae_211; energy_star_portfolio_manager",
        "process_clue": "Cannot rank hypotheses without minimum evidence pack covering structure, operation and utility behavior.",
        "industrial_reason": "Audit-grade standards (ISO 50002, ASHRAE 211) require this evidence basis before defendable framing.",
        "asset_family_reason": "Asset-family heterogeneity demands characterization before comparison or intervention.",
    },
}


def _scenario_letter(scenario_text: str) -> str:
    """Extract the leading letter (A/B/C/D) from a scenario heading.

    'A. Energy intensity ...' → 'A'. Returns '' when no letter is found.
    """
    text = (scenario_text or "").strip()
    if len(text) >= 2 and text[0].isalpha() and text[1] == ".":
        return text[0].upper()
    return ""


def _justification_for(family: str, scenario_text: str, asset_name: str) -> dict[str, str]:
    """Return the 5 RECOVERY_2026-05-10 §11.B justification fields.

    Resolves (family, letter) from the scenario heading; falls back to
    'default' family. Returns empty strings only if both keys miss
    (safety net — should never happen given the table above is complete).
    """
    letter = _scenario_letter(scenario_text)
    fields = (
        _SCENARIO_JUSTIFICATION.get((family, letter))
        or _SCENARIO_JUSTIFICATION.get(("default", letter))
        or {}
    )
    if not fields:
        return {
            "trigger": "",
            "source": "",
            "process_clue": "",
            "industrial_reason": "",
            "asset_family_reason": "",
        }
    # Asset name substitution is currently informational; preserved for
    # later templating when motors emit asset-specific triggers.
    return dict(fields)


def _build_scenario_space(
    asset_name: str,
    missing_clusters: list[str],
    regulatory_flags: list[str],
    target_type: str,
    decision_front_register: list[dict[str, Any]],
    minimum_evidence_unlock_map: list[dict[str, Any]],
) -> list[dict[str, str]]:
    asset_not_characterized = bool(missing_clusters)
    family = _target_family(target_type)
    rows: list[dict[str, str]]
    if family == "logistics":
        rows = [
            {
                "scenario": "A. Energy intensity is structurally tied to throughput and dock operations",
                "plausibility_status": "Plausible but unsupported",
                "financial_meaning": "Operational or refrigeration upside may be narrower than benchmark-only screening suggests.",
                "what_would_make_it_true": "Throughput windows, dock cycles, refrigeration duty, or occupancy patterns explain most site energy behavior.",
                "what_would_falsify_it": "Controls or support-system waste dominates the observed load profile.",
                "evidence_needed": "Operating schedule + throughput profile + utility / fuel basis",
            },
            {
                "scenario": "B. Material waste is controls or scheduling driven",
                "plausibility_status": "Not ruled out",
                "financial_meaning": "Targeted controls, refrigeration, or dock-air-management interventions may create bounded upside.",
                "what_would_make_it_true": "Operating evidence shows avoidable night, idle, refrigeration, or dock-cycle losses.",
                "what_would_falsify_it": "Load behavior tracks unavoidable throughput and occupancy duty closely.",
                "evidence_needed": "Controls history + dock profile + system inventory",
            },
            {
                "scenario": "C. Compliance exposure dominates savings",
                "plausibility_status": "Plausible" if regulatory_flags else "Possible but unsupported",
                "financial_meaning": "Capital logic may be driven by local performance or emissions posture rather than pure savings.",
                "what_would_make_it_true": "Current local filings and utility basis show a material trigger or compliance burden.",
                "what_would_falsify_it": "Current local evidence shows limited regulatory burden at the asset.",
                "evidence_needed": "Compliance filing + area basis + utility / fuel profile",
            },
            {
                "scenario": "D. Asset cannot yet be technically characterized from current evidence",
                "plausibility_status": "Currently dominant" if asset_not_characterized else "Reduced",
                "financial_meaning": "No strong logistics, refrigeration, or compliance decision is defendable yet.",
                "what_would_make_it_true": f"Critical clusters remain missing for {asset_name}.",
                "what_would_falsify_it": "Minimum evidence pack is received and major schedule, system, and utility fields are populated.",
                "evidence_needed": "Geometry + throughput schedule + system inventory + utility evidence",
            },
        ]
    elif family == "manufacturing":
        rows = [
            {
                "scenario": "A. Energy intensity is structurally driven by resin, press, curing, or other thermal-process duty",
                "plausibility_status": "Plausible but unsupported",
                "financial_meaning": "Efficiency upside may be narrower than generic industrial screening suggests because thermal duty is structural to output quality or process chemistry.",
                "what_would_make_it_true": "Presses, resin systems, curing ovens, thermal-oil loops, or other line-specific duty explain most site energy behavior.",
                "what_would_falsify_it": "Support-system losses in compressed air, dust collection, VOC capture, or idle-line operation dominate the load profile.",
                "evidence_needed": "NAICS / SIC + process narrative + press / curing inventory + utility / thermal basis",
            },
            {
                "scenario": "B. Material waste is driven by support systems, schedule losses, or environmental controls",
                "plausibility_status": "Not ruled out",
                "financial_meaning": "Targeted operational corrections may create bounded upside without redesigning the core process.",
                "what_would_make_it_true": "Shift calendar, compressed air, dust collection, VOC capture, material handling, or downtime windows show avoidable inefficiency.",
                "what_would_falsify_it": "Process intensity is tightly coupled to production requirements and support systems are already proportionate to duty.",
                "evidence_needed": "Shift / throughput profile + support-system inventory + downtime / maintenance basis",
            },
            {
                "scenario": "C. Environmental, VOC, wastewater, or emissions exposure dominates economics",
                "plausibility_status": "Plausible" if regulatory_flags else "Possible but unsupported",
                "financial_meaning": "Capital logic may be driven by permit, abatement, or thermal-emissions posture rather than energy savings alone.",
                "what_would_make_it_true": "Current air, wastewater, VOC, or emissions records show a material trigger tied to process chemistry, thermal generation, or abatement systems.",
                "what_would_falsify_it": "Current local evidence shows limited environmental or compliance burden at the site or places that burden outside the in-scope lines.",
                "evidence_needed": "Permit basis + emissions / wastewater profile + process-duty and thermal basis",
            },
            {
                "scenario": "D. Asset cannot yet be technically characterized from current evidence",
                "plausibility_status": "Currently dominant" if asset_not_characterized else "Reduced",
                "financial_meaning": "No strong process, CAPEX, or compliance decision is defendable yet.",
                "what_would_make_it_true": f"Critical clusters remain missing for {asset_name}.",
                "what_would_falsify_it": "Minimum evidence pack is received and major process-family, thermal-duty, utility, and schedule fields are populated.",
                "evidence_needed": "Geometry + process-family inventory + throughput schedule + thermal / utility evidence",
            },
        ]
    elif family == "infrastructure":
        rows = [
            {
                "scenario": "A. Service duty and topology dominate energy and loss behavior",
                "plausibility_status": "Plausible but unsupported",
                "financial_meaning": "Capital logic may depend more on topology and duty than on generic efficiency levers.",
                "what_would_make_it_true": "Major equipment, dispatch profile, and service duty explain most loss or energy behavior.",
                "what_would_falsify_it": "Controllable support loads dominate the operational profile.",
                "evidence_needed": "Equipment inventory + one-line or layout boundary + duty profile",
            },
            {
                "scenario": "B. Reliability constraints dominate discretionary savings",
                "plausibility_status": "Not ruled out",
                "financial_meaning": "Resilience or redundancy requirements may narrow operational upside.",
                "what_would_make_it_true": "Redundancy obligations, outage tolerance, or service commitments constrain operating flexibility.",
                "what_would_falsify_it": "Operating evidence shows flexible service duty with limited reliability lock-in.",
                "evidence_needed": "Reliability basis + outage history + operator control boundary",
            },
            {
                "scenario": "C. Environmental or permit exposure dominates intervention logic",
                "plausibility_status": "Plausible" if regulatory_flags else "Possible but unsupported",
                "financial_meaning": "Upgrade logic may be driven by environmental posture, not by pure efficiency.",
                "what_would_make_it_true": "Current local filings or equipment scope show a meaningful environmental or permit trigger.",
                "what_would_falsify_it": "Current local evidence shows limited environmental or reporting burden.",
                "evidence_needed": "Current compliance filing + in-scope equipment list + fuel / station-service basis",
            },
            {
                "scenario": "D. Asset cannot yet be technically characterized from current evidence",
                "plausibility_status": "Currently dominant" if asset_not_characterized else "Reduced",
                "financial_meaning": "No strong reliability, capacity, or compliance decision is defendable yet.",
                "what_would_make_it_true": f"Critical clusters remain missing for {asset_name}.",
                "what_would_falsify_it": "Minimum evidence pack is received and topology, duty, and metering fields are populated.",
                "evidence_needed": "Site boundary + equipment topology + duty profile + metering basis",
            },
        ]
    elif family == "oil_gas":
        rows = [
            {
                "scenario": "A. Throughput and process duty dominate energy and carbon exposure",
                "plausibility_status": "Plausible but unsupported",
                "financial_meaning": "Energy or emissions upside may be tightly constrained by process duty.",
                "what_would_make_it_true": "Process units, thermal duty, compression, or pumping explain most site energy and emissions behavior.",
                "what_would_falsify_it": "Support systems and controllable non-process loads dominate the observed profile.",
                "evidence_needed": "Unit inventory + throughput profile + fuel / emissions basis",
            },
            {
                "scenario": "B. Reliability and turnaround constraints dominate discretionary savings",
                "plausibility_status": "Not ruled out",
                "financial_meaning": "Intervention upside may be constrained by uptime, pressure, thermal, or safety requirements.",
                "what_would_make_it_true": "Reliability history, turnaround constraints, or process safety needs lock in current operating behavior.",
                "what_would_falsify_it": "Operating evidence shows flexible duty with low reliability lock-in.",
                "evidence_needed": "Reliability history + turnaround schedule + operating-unit boundary",
            },
            {
                "scenario": "C. Compliance or transition exposure dominates economics",
                "plausibility_status": "Plausible" if regulatory_flags else "Possible but unsupported",
                "financial_meaning": "Capital logic may be driven by emissions, permit, or transition pressure more than by energy savings.",
                "what_would_make_it_true": "Current permit, emissions, or reporting evidence shows material exposure.",
                "what_would_falsify_it": "Current local evidence shows limited regulatory or transition burden.",
                "evidence_needed": "Current compliance filing + emissions basis + fuel / flare / steam context",
            },
            {
                "scenario": "D. Asset cannot yet be technically characterized from current evidence",
                "plausibility_status": "Currently dominant" if asset_not_characterized else "Reduced",
                "financial_meaning": "No strong process, reliability, or compliance decision is defendable yet.",
                "what_would_make_it_true": f"Critical clusters remain missing for {asset_name}.",
                "what_would_falsify_it": "Minimum evidence pack is received and unit, throughput, and emissions fields are populated.",
                "evidence_needed": "Site boundary + unit inventory + throughput profile + fuel / emissions evidence",
            },
        ]
    else:
        rows = [
            {
                "scenario": "A. Energy upside is owner-controllable through central plant and common-area systems",
                "plausibility_status": "Plausible but unsupported",
                "financial_meaning": "Retrofit CAPEX may become investable if central-plant and common-area control sits with the owner.",
                "what_would_make_it_true": "Owner controls major HVAC, central plant, controls, or common-area loads and captures the resulting economics.",
                "what_would_falsify_it": "Tenant-controlled loads or submetered tenant spaces dominate the operating profile.",
                "evidence_needed": "Lease responsibility + tenant metering basis + central-plant / system inventory",
            },
            {
                "scenario": "B. Energy use is structurally tenant-driven or use-mix driven",
                "plausibility_status": "Not ruled out",
                "financial_meaning": "Owner energy upside is weaker than benchmark-based screening suggests and savings may not accrue to the underwriting boundary.",
                "what_would_make_it_true": "Tenant schedules, use mix, after-hours occupancy, and submetering explain most load behavior.",
                "what_would_falsify_it": "Central owner-controlled systems dominate energy behavior and tenant variability is secondary.",
                "evidence_needed": "Occupancy / use mix + operating schedule + tenant metering / utility split",
            },
            {
                "scenario": "C. Compliance or fuel-transition exposure dominates savings",
                "plausibility_status": "Plausible" if regulatory_flags else "Possible but unsupported",
                "financial_meaning": "Capital logic may be driven by avoided penalty or fuel-transition posture rather than operating savings.",
                "what_would_make_it_true": "Local rule applicability, area thresholds, and steam / gas / electrification exposure create a material trigger.",
                "what_would_falsify_it": "Current filings or local facts show no material trigger or place the burden outside the owner-controlled boundary.",
                "evidence_needed": "Compliance filing + GFA + steam / gas / electrification basis",
            },
            {
                "scenario": "D. Asset cannot yet be technically characterized from current evidence",
                "plausibility_status": "Currently dominant" if asset_not_characterized else "Reduced",
                "financial_meaning": "No strong underwriting, retrofit, or compliance decision is defendable yet.",
                "what_would_make_it_true": f"Critical clusters remain missing for {asset_name}.",
                "what_would_falsify_it": "Minimum evidence pack is received and major clusters are populated.",
                "evidence_needed": "Geometry + schedule + systems + fuel / utility evidence",
            },
        ]

    if family == "manufacturing":
        link_map = [
            ("Process efficiency or utility-support CAPEX", _find_evidence_item(minimum_evidence_unlock_map, "naics / sic", "resin / adhesive", "curing or thermal-process", "steam / boilers / thermal oil")),
            ("Utility cost optimization", _find_evidence_item(minimum_evidence_unlock_map, "compressed-air", "dust collection", "voc capture", "control boundary")),
            ("Environmental or permit-driven investment", _find_evidence_item(minimum_evidence_unlock_map, "air, wastewater, and emissions permit", "steam / boilers / thermal oil")),
            ("Operator evidence request", _find_evidence_item(minimum_evidence_unlock_map, "naics / sic", "shift schedule", "throughput profile")),
        ]
    elif family == "building":
        link_map = [
            ("Energy retrofit CAPEX", _find_evidence_item(minimum_evidence_unlock_map, "central plant", "hvac", "bms")),
            ("Acquisition underwriting with energy upside", _find_evidence_item(minimum_evidence_unlock_map, "tenant metering", "lease responsibility", "utility bills")),
            ("Compliance investment", _find_evidence_item(minimum_evidence_unlock_map, "gfa", "steam, gas, district energy, or electrification basis")),
            ("Seller / operator evidence request", minimum_evidence_unlock_map[0]["evidence_item"] if minimum_evidence_unlock_map else ""),
        ]
    elif family == "logistics":
        link_map = [
            ("Operational or refrigeration retrofit CAPEX", _find_evidence_item(minimum_evidence_unlock_map, "utility / fuel", "dock", "refrigerated")),
            ("Throughput or dock-efficiency intervention", _find_evidence_item(minimum_evidence_unlock_map, "throughput profile", "operating schedule")),
            ("Compliance investment", _find_evidence_item(minimum_evidence_unlock_map, "utility / fuel", "building area")),
            ("Seller / operator evidence request", minimum_evidence_unlock_map[0]["evidence_item"] if minimum_evidence_unlock_map else ""),
        ]
    elif family == "oil_gas":
        link_map = [
            ("Process, emissions, or efficiency CAPEX", _find_evidence_item(minimum_evidence_unlock_map, "unit inventory", "throughput profile", "fuel / emissions")),
            ("Reliability or throughput intervention", _find_evidence_item(minimum_evidence_unlock_map, "throughput profile", "reliability")),
            ("Permit, compliance, or transition investment", _find_evidence_item(minimum_evidence_unlock_map, "fuel / emissions", "compliance filing")),
            ("Operator evidence request", minimum_evidence_unlock_map[0]["evidence_item"] if minimum_evidence_unlock_map else ""),
        ]
    else:
        link_map = [
            ("Reliability or conversion-loss intervention", _find_evidence_item(minimum_evidence_unlock_map, "equipment inventory", "duty profile")),
            ("Capacity or resilience capital", _find_evidence_item(minimum_evidence_unlock_map, "reliability", "boundary")),
            ("Environmental or permit-driven upgrade", _find_evidence_item(minimum_evidence_unlock_map, "fuel", "compliance filing")),
            ("Operator evidence request", minimum_evidence_unlock_map[0]["evidence_item"] if minimum_evidence_unlock_map else ""),
        ]

    enriched_rows: list[dict[str, str]] = []
    for idx, row in enumerate(rows):
        linked_front = ""
        linked_evidence = ""
        if idx < len(link_map):
            linked_front = _find_decision_front(decision_front_register, link_map[idx][0])
            linked_evidence = link_map[idx][1]
        # RECOVERY_2026-05-10 §11.B: every scenario carries the 5
        # justification fields validated by motor_062.
        justification = _justification_for(family, row.get("scenario", ""), asset_name)
        enriched_rows.append(
            {
                **row,
                **justification,
                "linked_decision_front": linked_front,
                "linked_evidence_item": linked_evidence or row.get("evidence_needed", ""),
            }
        )
    return enriched_rows


def _build_scenario_evidence_link_register(
    scenario_space: list[dict[str, str]],
) -> list[dict[str, str]]:
    return [
        {
            "scenario": str(row.get("scenario", "")).strip(),
            "linked_decision_front": str(row.get("linked_decision_front", "")).strip(),
            "linked_evidence_item": str(row.get("linked_evidence_item", "")).strip(),
            "financial_meaning": str(row.get("financial_meaning", "")).strip(),
            "falsification_condition": str(row.get("what_would_falsify_it", "")).strip(),
        }
        for row in scenario_space
    ]


class Motor014Adapter(BaseMotorAdapter):
    @property
    def motor_id(self) -> str:
        return "motor_014"

    @property
    def input_motor_ids(self) -> list[str]:
        return ["motor_013", "motor_012", "motor_034", "motor_007", "motor_001", "motor_037", "motor_038", "motor_040", "motor_041", "motor_046"]

    def _run_impl(self, inputs: dict[str, Any]) -> dict[str, Any]:
        inference_cases_raw = inputs.get("motor_013", {}).get("inference_case_register", [])
        facility_prior_id = inputs.get("motor_013", {}).get("facility_prior_id", "")
        subject_gate = inputs.get("motor_007", {})
        maturity_engine = inputs.get("motor_034", {}) if isinstance(inputs.get("motor_034", {}), dict) else {}
        produced_at = datetime.now(timezone.utc).isoformat()

        # Pull the full facility_prior from motor_012
        facility_prior_ref = inputs.get("motor_012", {}).get("facility_prior", {
            "facility_prior_id": facility_prior_id,
            "entities": {},
            "uncertainty_markers": [],
            "operational_tension_hypotheses": [],
        })

        # Score all inference cases using computed scores
        inference_records = [_score_inference_case(c, facility_prior_ref) for c in inference_cases_raw]

        # Build all decision core outputs
        tension_records = _build_tension_records(inference_records)
        conflict_register = _build_conflict_register(inference_records)
        uncertainty_register = _build_uncertainty_register(facility_prior_ref, inference_records)
        evidence_gap_register = _build_evidence_gap_register(inference_records, facility_prior_ref)
        opportunity_candidates = _build_opportunity_candidates(inference_records, facility_prior_ref)
        validation_queue = _build_validation_queue(inference_records)
        decision_core_lineage = _build_decision_core_lineage(
            facility_prior_ref,
            inference_records,
            validation_queue,
            evidence_gap_register,
            produced_at,
        )

        asset_name = facility_prior_ref.get("asset_name", "the facility")
        critical_gaps = len([c for c in inference_records if c.get("validation_urgency_score", 0) >= 0.85])
        primary_limitation = next(
            (c for c in conflict_register if c.get("inference_case_id") == "LC-ASSET-01"),
            conflict_register[0] if conflict_register else None,
        )
        missing_evidence_register = list(facility_prior_ref.get("missing_evidence_register", []) or [])
        target_type = _target_type_from_prior(facility_prior_ref)
        target_admissibility_state = str(subject_gate.get("target_admissibility_state", "")).strip()
        subject_gate_passed = bool(subject_gate.get("subject_gate_passed", False))
        facility_prior_ref["target_admissibility_state"] = target_admissibility_state
        facility_prior_ref["subject_gate_passed"] = subject_gate_passed
        canonical_context_summary = _canonical_asset_context_summary(maturity_engine, facility_prior_ref)
        missing_clusters = canonical_context_summary.get("missing_clusters", [])
        asset_context_readiness = canonical_context_summary.get(
            "canonical_asset_context_state",
            facility_prior_ref.get("asset_context_readiness", "asset_context_insufficient"),
        )
        canonical_screening_supported = bool(canonical_context_summary.get("screening_supported", False))
        missing_clusters_text = ", ".join(missing_clusters[:5]) if missing_clusters else "unresolved physical observable clusters"
        reg_flags = (
            facility_prior_ref.get("entities", {})
            .get("RegulatoryContext", {})
            .get("regulatory_flags", [])
        )
        variable_maturity_register = list(maturity_engine.get("variable_maturity_register", []) or [])
        claim_permission_register = list(maturity_engine.get("claim_permission_register", []) or [])
        decision_permission_register = list(maturity_engine.get("decision_permission_register", []) or [])
        report_readiness_register = dict(maturity_engine.get("report_readiness_register", {}) or {})
        screening_admissible = canonical_screening_supported or (
            "Compliance / Investment Screening Brief"
            in list(report_readiness_register.get("report_type_allowed", []) or [])
        )
        canonical_problem_frame = dict(maturity_engine.get("canonical_problem_frame", {}) or {})
        dominant_variable_register = list(inputs.get("motor_038", {}).get("dominant_variable_register", []) or [])
        cross_layer_conflict_register = list(inputs.get("motor_040", {}).get("cross_layer_conflict_register", []) or [])
        minimum_evidence_for_discrimination_register = list(
            inputs.get("motor_046", {}).get("minimum_evidence_for_discrimination_register", []) or []
        )
        information_deficit_score = _information_deficit_score(inference_records, missing_clusters)
        minimum_evidence_unlock_map = _build_minimum_evidence_unlock_map(
            validation_queue,
            inference_records,
            missing_clusters,
            facility_prior_ref.get("minimum_evidence_pack_seed", []),
            target_type,
        )
        minimum_evidence_unlock_map = _merge_missing_evidence_register(
            minimum_evidence_unlock_map,
            missing_evidence_register,
        )
        minimum_evidence_unlock_map = _merge_structural_discrimination_register(
            minimum_evidence_unlock_map,
            minimum_evidence_for_discrimination_register,
        )
        decision_front_register = _build_decision_front_register(
            asset_name,
            conflict_register,
            validation_queue,
            missing_clusters,
            reg_flags,
            target_type,
            target_admissibility_state,
            subject_gate_passed,
        )
        decision_front_register = _overlay_decision_permissions(
            decision_front_register,
            decision_permission_register,
        )
        variable_bottleneck_register = _build_variable_bottleneck_register(
            decision_permission_register,
            variable_maturity_register,
        )
        claim_permission_summary = _build_claim_permission_summary(claim_permission_register)
        next_best_questions = _build_next_best_questions(
            asset_name,
            minimum_evidence_unlock_map,
            missing_evidence_register,
            missing_clusters,
            decision_front_register,
            target_type,
        )
        next_best_questions = _prepend_structural_next_best_questions(
            next_best_questions,
            minimum_evidence_for_discrimination_register,
            canonical_problem_frame,
        )
        scenario_space = _build_scenario_space(
            asset_name,
            missing_clusters,
            reg_flags,
            target_type,
            decision_front_register,
            minimum_evidence_unlock_map,
        )
        scenario_evidence_link_register = _build_scenario_evidence_link_register(scenario_space)
        financial_exposure_register = _build_financial_exposure_register(
            target_type,
            reg_flags,
            minimum_evidence_unlock_map,
            decision_front_register,
        )
        asset_context_readiness_summary = {
            "asset_context_readiness": asset_context_readiness,
            "critical_missing_clusters": _critical_missing_clusters(missing_clusters),
            "cluster_rows": _cluster_status_rows(missing_clusters, asset_context_readiness, _target_type_from_prior(facility_prior_ref)),
            "canonical_screening_supported": screening_admissible,
            "canonical_supported_clusters": canonical_context_summary.get("supported_clusters", []),
        }
        structural_reasoning_path = _structural_reasoning_path(
            canonical_problem_frame,
            dominant_variable_register,
            cross_layer_conflict_register,
            minimum_evidence_for_discrimination_register,
        )

        # Composite decision summary (non-recommendation language)
        composite_reading = {
            "reading_id": "CR-001",
            "facility_prior_id": facility_prior_id,
            "produced_at": produced_at,
            "epistemic_grade": "Decision-grade — preparatory analysis only",
            "framework_constraint": (
                "This composite reading contains no recommendation, no diagnosis, and no final "
                "compliance determination. All statements are conditional on validation requirements."
            ),
            "active_cases": len(inference_records),
            "blocking_conflicts": len(conflict_register),
            "open_tensions": len(tension_records),
            "critical_evidence_gaps": critical_gaps,
            "information_deficit_score": information_deficit_score,
            "opportunity_candidates": len(opportunity_candidates),
            "highest_urgency_items": validation_queue[:3],
            "primary_case_limitation": primary_limitation,
            "primary_block_reason": (
                "Public screening admissible; decision-grade substrate incomplete"
                if (
                    primary_limitation
                    and primary_limitation.get("inference_case_id") == "LC-ASSET-01"
                    and screening_admissible
                )
                else "Physical and operating substrate incomplete"
                if primary_limitation and primary_limitation.get("inference_case_id") == "LC-ASSET-01"
                else "Blocking conflicts and validation gaps remain active"
            ),
            "decision_state": (
                "EPISTEMIC STATE: SCREENING ADMISSIBLE — "
                f"{asset_name} has sufficient public asset and regulatory substrate for screening, but "
                f"decision-grade advancement still depends on unresolved clusters ({missing_clusters_text}). "
                "Utility, systems, operating-profile, and control-boundary evidence remain necessary before ROI, "
                "retrofit, or compliance-closure claims can advance."
                if (
                    primary_limitation
                    and primary_limitation.get("inference_case_id") == "LC-ASSET-01"
                    and screening_admissible
                )
                else
                "EPISTEMIC STATE: ASSET TECHNICAL INSUFFICIENCY — "
                f"{asset_name} cannot yet be treated as a normal technical asset case because "
                f"core observable clusters remain missing ({missing_clusters_text}). "
                "Issuer or finance context may still be useful, but it cannot compensate for the missing asset substrate."
                if primary_limitation and primary_limitation.get("inference_case_id") == "LC-ASSET-01"
                else "EPISTEMIC STATE: INSUFFICIENT — "
                f"{len(conflict_register)} blocking conflict(s) and "
                f"{critical_gaps} critical validation gap(s) must be resolved "
                f"before the assessment of {asset_name} can advance to a decision-ready state."
            ),
            "report_readiness_reason": report_readiness_register.get("reason", ""),
            "claim_permission_summary": claim_permission_summary,
            "variable_bottleneck_register": variable_bottleneck_register[:6],
            "default_reasoning_path": structural_reasoning_path.get("reasoning_path", ""),
            "canonical_problem_frame": canonical_problem_frame,
            "structural_reasoning_path": structural_reasoning_path,
        }

        return {
            "inference_records": inference_records,
            # V5 P2: canonical Phase 2 unit (Master Doc §15) — projection of
            # inference_records with the 6 mandatory attributes named
            # canonically. Downstream consumers should prefer this register
            # over the raw inference_records.
            "inference_case_register_canonical": to_inference_case_register(inference_records),
            "tension_records": tension_records,
            "conflict_register": conflict_register,
            "opportunity_candidates": opportunity_candidates,
            "uncertainty_register": uncertainty_register,
            "evidence_gap_register": evidence_gap_register,
            "validation_queue": validation_queue,
            "next_best_questions": next_best_questions,
            "composite_reading": composite_reading,
            "decision_front_register": decision_front_register,
            "minimum_evidence_unlock_map": minimum_evidence_unlock_map,
            "missing_evidence_register": missing_evidence_register,
            "variable_maturity_register": variable_maturity_register,
            "claim_permission_register": claim_permission_register,
            "decision_permission_register": decision_permission_register,
            "report_readiness_register": report_readiness_register,
            "claim_permission_summary": claim_permission_summary,
            "variable_bottleneck_register": variable_bottleneck_register,
            "scenario_space": scenario_space,
            "scenario_evidence_link_register": scenario_evidence_link_register,
            "financial_exposure_register": financial_exposure_register,
            "asset_context_readiness_summary": asset_context_readiness_summary,
            "canonical_asset_context_summary": canonical_context_summary,
            "canonical_problem_frame": canonical_problem_frame,
            "structural_reasoning_path": structural_reasoning_path,
            "information_deficit_score": information_deficit_score,
            "target_admissibility_state": target_admissibility_state,
            "subject_gate_passed": subject_gate_passed,
            "decision_core_lineage": decision_core_lineage,
            "total_inference_records": len(inference_records),
            "total_tensions": len(tension_records),
            "total_conflicts": len(conflict_register),
            "total_opportunities": len(opportunity_candidates),
            "total_evidence_gaps": len(evidence_gap_register),
            "facility_prior_id": facility_prior_id,
            "produced_at": produced_at,
        }
