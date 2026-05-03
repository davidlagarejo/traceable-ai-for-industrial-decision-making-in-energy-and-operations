from __future__ import annotations

from typing import Any

from .schemas import text

_AFFIRMATIVE_EVIDENCE_STATES = {
    "evidenced",
    "partially_evidenced",
    "partially_bound",
    "sufficiently_bound",
}

_PUBLIC_CONTEXT_OK_REQUIREMENTS = {
    "climate_context",
}


def _question_ids(dynamic_intake_question_register: list[dict[str, Any]]) -> set[str]:
    return {
        text(row.get("question_id"))
        for row in list(dynamic_intake_question_register or [])
        if text(row.get("question_id"))
    }


def _question_ids_by_requirement(
    dynamic_intake_question_register: list[dict[str, Any]],
) -> dict[str, list[str]]:
    rows: dict[str, list[str]] = {}
    for row in list(dynamic_intake_question_register or []):
        question_id = text(row.get("question_id"))
        if not question_id:
            continue
        for requirement in list(row.get("comparison_requirements_unlocked", []) or []):
            requirement_key = text(requirement)
            if not requirement_key:
                continue
            rows.setdefault(requirement_key, [])
            if question_id not in rows[requirement_key]:
                rows[requirement_key].append(question_id)
    return rows


def _pack_state(operational_intake_pack: dict[str, Any], pack_name: str) -> str:
    return text((operational_intake_pack.get(pack_name, {}) or {}).get("current_state"))


def _state_is_affirmative(requirement_key: str, state: str) -> bool:
    normalized = text(state)
    if normalized in _AFFIRMATIVE_EVIDENCE_STATES:
        return True
    if requirement_key in _PUBLIC_CONTEXT_OK_REQUIREMENTS and normalized == "public_context_seeded":
        return True
    return False


def _aggregate_requirement_state(
    requirement_key: str,
    evidence_surfaces: list[tuple[str, str]],
) -> tuple[str, list[str], list[str]]:
    normalized_surfaces = [(label, text(state)) for label, state in evidence_surfaces if text(label)]
    bounded_by = [
        label
        for label, state in normalized_surfaces
        if _state_is_affirmative(requirement_key, state)
    ]
    pending = [
        label
        for label, state in normalized_surfaces
        if not _state_is_affirmative(requirement_key, state)
    ]
    if not normalized_surfaces:
        return "not_yet_evidenced", bounded_by, pending
    if len(bounded_by) == len(normalized_surfaces):
        if all(text(state) == "evidenced" for _, state in normalized_surfaces):
            return "evidenced", bounded_by, pending
        return "partially_evidenced", bounded_by, pending
    if bounded_by:
        return "partially_evidenced", bounded_by, pending
    if any(text(state) == "public_context_seeded" for _, state in normalized_surfaces):
        return "public_context_seeded", bounded_by, pending
    return text(normalized_surfaces[0][1]) or "not_yet_evidenced", bounded_by, pending


def _why_still_unbounded(
    *,
    requirement_key: str,
    missing_evidence: list[str],
    pending_surfaces: list[str],
    question_ids: list[str],
) -> str:
    parts: list[str] = []
    if pending_surfaces:
        parts.append("Affirmative evidence still missing from: " + ", ".join(pending_surfaces) + ".")
    else:
        parts.append("No affirmative evidence surface currently bounds this requirement.")
    if missing_evidence:
        parts.append("Still required: " + ", ".join(missing_evidence[:4]) + ".")
    if question_ids:
        parts.append("Open discriminator questions: " + ", ".join(question_ids[:3]) + ".")
    return " ".join(parts)


def _requirement_row(
    *,
    requirement_key: str,
    peer_requirement: str,
    why_required: str,
    current_evidence: str,
    missing_evidence: list[str],
    comparison_status: str,
    evidence_basis: list[str],
    bounded_by: list[str],
    why_still_unbounded: str,
    peer_requirement_evidence_state: str,
) -> dict[str, Any]:
    return {
        "requirement_key": requirement_key,
        "peer_requirement": peer_requirement,
        "why_required": why_required,
        "current_evidence": current_evidence,
        "missing_evidence": missing_evidence,
        "comparison_status": comparison_status,
        "evidence_basis": evidence_basis,
        "bounded_by": bounded_by,
        "why_still_unbounded": why_still_unbounded,
        "peer_requirement_evidence_state": peer_requirement_evidence_state,
    }


def _evidence_based_requirement_row(
    *,
    requirement_key: str,
    peer_requirement: str,
    why_required: str,
    missing_evidence: list[str],
    evidence_surfaces: list[tuple[str, str]],
    question_ids_by_requirement: dict[str, list[str]],
) -> dict[str, Any]:
    evidence_state, bounded_by, pending_surfaces = _aggregate_requirement_state(
        requirement_key,
        evidence_surfaces,
    )
    evidence_basis = [label for label, _ in evidence_surfaces if text(label)]
    requirement_questions = list(question_ids_by_requirement.get(requirement_key, []) or [])
    comparison_status = "conditional" if bounded_by and not pending_surfaces else "blocked"
    why_unbounded = (
        ""
        if comparison_status == "conditional"
        else _why_still_unbounded(
            requirement_key=requirement_key,
            missing_evidence=missing_evidence,
            pending_surfaces=pending_surfaces,
            question_ids=requirement_questions,
        )
    )
    return _requirement_row(
        requirement_key=requirement_key,
        peer_requirement=peer_requirement,
        why_required=why_required,
        current_evidence=evidence_state,
        missing_evidence=missing_evidence,
        comparison_status=comparison_status,
        evidence_basis=evidence_basis,
        bounded_by=bounded_by,
        why_still_unbounded=why_unbounded,
        peer_requirement_evidence_state=evidence_state,
    )


def build_peer_requirement_register(
    *,
    asset_family_research_profile: dict[str, Any],
    fair_comparison_profile: dict[str, Any],
    operational_intake_pack: dict[str, Any],
    dynamic_intake_question_register: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    asset_family = text(asset_family_research_profile.get("asset_family"))
    question_ids = _question_ids(dynamic_intake_question_register)
    question_ids_by_requirement = _question_ids_by_requirement(dynamic_intake_question_register)
    rows: list[dict[str, Any]] = []

    climate_state = text(fair_comparison_profile.get("climate_context_state")) or "public_context_seeded"
    schedule_state = text(fair_comparison_profile.get("operating_schedule_state")) or "not_yet_evidenced"
    control_state = text(fair_comparison_profile.get("control_boundary_state")) or "not_yet_evidenced"
    throughput_pack_state = _pack_state(operational_intake_pack, "throughput_schedule_pack")
    utility_bill_state = _pack_state(operational_intake_pack, "utility_bill_pack")
    utility_tariff_state = _pack_state(operational_intake_pack, "utility_tariff_pack")
    metering_boundary_state = _pack_state(operational_intake_pack, "metering_boundary_pack")
    lease_responsibility_state = _pack_state(operational_intake_pack, "lease_responsibility_pack")
    equipment_inventory_state = _pack_state(operational_intake_pack, "equipment_inventory_pack")
    maintenance_maturity_state = text((operational_intake_pack.get("maintenance_maturity_pack", {}) or {}).get("current_state")) or "not_yet_evidenced"
    maintenance_proof_state = _pack_state(operational_intake_pack, "maintenance_proof_pack")
    cmms_state = _pack_state(operational_intake_pack, "cmms_or_workorder_pack")
    permit_detail_state = _pack_state(operational_intake_pack, "permit_detail_pack")
    process_map_state = text(fair_comparison_profile.get("process_map_state")) or "not_yet_evidenced"
    subsystem_inventory_state = _pack_state(operational_intake_pack, "subsystem_inventory_pack")

    if asset_family in {"logistics_warehouse", "cold_chain"}:
        rows.extend(
            [
                _evidence_based_requirement_row(
                    requirement_key="asset_subtype_or_temperature_regime",
                    peer_requirement="dry vs cold-chain vs fulfillment vs cross-dock regime",
                    why_required="Subtype changes the denominator, the peer family, and whether area-only comparisons are invalid by design.",
                    missing_evidence=["dry/cold-chain status", "temperature regime", "service model"],
                    evidence_surfaces=[],
                    question_ids_by_requirement=question_ids_by_requirement,
                ),
                _evidence_based_requirement_row(
                    requirement_key="dock_density_and_service_intensity",
                    peer_requirement="dock density, throughput proxy, and operating schedule",
                    why_required="Warehouse comparisons fail when service-level intensity is hidden behind square footage.",
                    missing_evidence=["dock count", "dock cycles", "operating hours", "throughput window"],
                    evidence_surfaces=[
                        ("throughput schedule pack", throughput_pack_state or schedule_state),
                        ("operating schedule state", schedule_state),
                    ],
                    question_ids_by_requirement=question_ids_by_requirement,
                ),
                _evidence_based_requirement_row(
                    requirement_key="charging_and_power_mode",
                    peer_requirement="MHE charging profile and power-mode context",
                    why_required="Charging windows can make cost and peak demand incomparable across otherwise similar logistics assets.",
                    missing_evidence=["charger type", "charging windows", "fleet size", "electric vs fuel MHE"],
                    evidence_surfaces=[
                        ("equipment inventory pack", equipment_inventory_state),
                        ("utility tariff pack", utility_tariff_state),
                        ("utility bill pack", utility_bill_state),
                    ],
                    question_ids_by_requirement=question_ids_by_requirement,
                ),
                _evidence_based_requirement_row(
                    requirement_key="control_boundary_and_tariff",
                    peer_requirement="tenant/operator boundary, metering boundary, and tariff context",
                    why_required="The same physical asset can have completely different value capture if control and utility responsibility differ.",
                    missing_evidence=["lease responsibility", "metering boundary", "utility tariff context"],
                    evidence_surfaces=[
                        ("control boundary state", control_state),
                        ("lease responsibility pack", lease_responsibility_state),
                        ("metering boundary pack", metering_boundary_state),
                        ("utility tariff pack", utility_tariff_state),
                    ],
                    question_ids_by_requirement=question_ids_by_requirement,
                ),
                _evidence_based_requirement_row(
                    requirement_key="climate_context",
                    peer_requirement="matching climate context",
                    why_required="Climate changes conditioning duty and makes same-area comparisons unstable across regions.",
                    missing_evidence=["climate zone"],
                    evidence_surfaces=[("climate context", climate_state)],
                    question_ids_by_requirement=question_ids_by_requirement,
                ),
            ]
        )

    elif asset_family in {"industrial_manufacturing", "thermal_process_site", "utility_heavy_site"}:
        rows.extend(
            [
                _evidence_based_requirement_row(
                    requirement_key="process_type_and_thermal_lane",
                    peer_requirement="matching process type and thermal / utility lane",
                    why_required="Process and thermal duty determine whether a peer frame is physically coherent.",
                    missing_evidence=["process line map", "thermal systems", "utility mix"],
                    evidence_surfaces=[
                        ("process map state", process_map_state),
                        ("permit detail pack", permit_detail_state),
                        ("equipment inventory pack", equipment_inventory_state),
                    ],
                    question_ids_by_requirement=question_ids_by_requirement,
                ),
                _evidence_based_requirement_row(
                    requirement_key="throughput_product_mix_and_schedule",
                    peer_requirement="throughput, product mix, and operating schedule",
                    why_required="Area-based or gross site comparisons are invalid until production intensity is normalized.",
                    missing_evidence=["throughput by shift", "product mix", "duty cycle"],
                    evidence_surfaces=[
                        ("throughput schedule pack", throughput_pack_state or schedule_state),
                        ("operating schedule state", schedule_state),
                    ],
                    question_ids_by_requirement=question_ids_by_requirement,
                ),
                _evidence_based_requirement_row(
                    requirement_key="support_system_stack",
                    peer_requirement="compressed air / steam / refrigeration / major utilities stack",
                    why_required="Support-system architecture can dominate losses and invalidates simplistic peer logic.",
                    missing_evidence=["compressed air use", "steam duty", "major utility topology"],
                    evidence_surfaces=[
                        ("equipment inventory pack", equipment_inventory_state),
                        ("permit detail pack", permit_detail_state),
                    ],
                    question_ids_by_requirement=question_ids_by_requirement,
                ),
                _evidence_based_requirement_row(
                    requirement_key="maintenance_maturity_context",
                    peer_requirement="maintenance maturity and downtime context",
                    why_required="Two similar plants are not fair peers if one is being evaluated with reactive-maintenance economics and the other is not.",
                    missing_evidence=["PM logs", "CMMS/work orders", "downtime history"],
                    evidence_surfaces=[
                        ("maintenance maturity pack", maintenance_maturity_state),
                        ("maintenance proof pack", maintenance_proof_state),
                        ("CMMS/workorder pack", cmms_state),
                    ],
                    question_ids_by_requirement=question_ids_by_requirement,
                ),
            ]
        )

    elif asset_family == "commercial_building":
        rows.extend(
            [
                _evidence_based_requirement_row(
                    requirement_key="building_control_boundary",
                    peer_requirement="owner vs tenant control boundary",
                    why_required="Whole-building building benchmarks are misleading if owner burden and controllable load do not align.",
                    missing_evidence=["tenant metering map", "lease responsibility", "owner-controlled systems"],
                    evidence_surfaces=[
                        ("control boundary state", control_state),
                        ("lease responsibility pack", lease_responsibility_state),
                        ("metering boundary pack", metering_boundary_state),
                    ],
                    question_ids_by_requirement=question_ids_by_requirement,
                ),
                _evidence_based_requirement_row(
                    requirement_key="building_schedule_and_occupancy",
                    peer_requirement="occupancy and operating schedule",
                    why_required="Buildings with very different schedules are not fair peers even in the same class and climate.",
                    missing_evidence=["occupancy pattern", "hours of operation"],
                    evidence_surfaces=[
                        ("throughput schedule pack", throughput_pack_state or schedule_state),
                        ("operating schedule state", schedule_state),
                    ],
                    question_ids_by_requirement=question_ids_by_requirement,
                ),
                _evidence_based_requirement_row(
                    requirement_key="building_hvac_topology",
                    peer_requirement="central plant vs packaged-unit topology",
                    why_required="HVAC architecture changes both cost structure and intervention logic.",
                    missing_evidence=["central plant topology", "packaged-unit mix", "BMS maturity"],
                    evidence_surfaces=[("subsystem inventory pack", subsystem_inventory_state or "research_seed_only")],
                    question_ids_by_requirement=question_ids_by_requirement,
                ),
            ]
        )

    elif asset_family == "infrastructure_node":
        rows.extend(
            [
                _evidence_based_requirement_row(
                    requirement_key="dispatch_and_redundancy_burden",
                    peer_requirement="dispatch burden, service continuity, and redundancy class",
                    why_required="Node comparisons are invalid when duty, redundancy, and continuity burden differ.",
                    missing_evidence=["dispatch burden", "service continuity class", "redundancy design"],
                    evidence_surfaces=[
                        ("throughput schedule pack", throughput_pack_state or schedule_state),
                        ("operating schedule state", schedule_state),
                    ],
                    question_ids_by_requirement=question_ids_by_requirement,
                ),
                _evidence_based_requirement_row(
                    requirement_key="demand_structure",
                    peer_requirement="demand structure and tariff logic",
                    why_required="Node economics are often dominated by load shape and demand structure rather than gross energy.",
                    missing_evidence=["utility bills", "rate class", "interval profile"],
                    evidence_surfaces=[
                        ("utility and tariff pack", text((operational_intake_pack.get("utility_and_tariff_pack", {}) or {}).get("current_state"))),
                        ("utility bill pack", utility_bill_state),
                        ("utility tariff pack", utility_tariff_state),
                    ],
                    question_ids_by_requirement=question_ids_by_requirement,
                ),
            ]
        )

    return rows


def build_peer_candidate_family_register(
    *,
    asset_family_research_profile: dict[str, Any],
    peer_requirement_register: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    asset_family = text(asset_family_research_profile.get("asset_family"))
    blocked = any(text(row.get("comparison_status")) == "blocked" for row in peer_requirement_register)

    if asset_family == "logistics_warehouse":
        candidates = [
            "dry_warehouse_peers",
            "fulfillment_peers",
            "cross_dock_peers",
            "temperature_controlled_peers_if_applicable",
        ]
    elif asset_family == "cold_chain":
        candidates = ["cold_chain_distribution_peers", "temperature_regime_matched_peers"]
    elif asset_family in {"industrial_manufacturing", "thermal_process_site", "utility_heavy_site"}:
        candidates = [
            "same_process_family_peers",
            "same_thermal_or_utility_lane_peers",
            "throughput_normalized_peers",
        ]
    elif asset_family == "commercial_building":
        candidates = ["same_class_and_control_boundary_peers", "same_schedule_and_climate_peers"]
    elif asset_family == "infrastructure_node":
        candidates = ["same_dispatch_and_redundancy_class_peers"]
    else:
        candidates = ["same_family_screening_peers"]

    return [
        {
            "candidate_family": candidate,
            "asset_family": asset_family,
            "candidate_state": "blocked_pending_requirements" if blocked else "screening_ready",
        }
        for candidate in candidates
    ]


def build_comparison_blocker_register(
    *,
    peer_requirement_register: list[dict[str, Any]],
    comparison_validity_register: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for requirement in list(peer_requirement_register or []):
        if text(requirement.get("comparison_status")) != "blocked":
            continue
        rows.append(
            {
                "blocker_code": text(requirement.get("requirement_key")) or "comparison_requirement_missing",
                "why": text(requirement.get("why_required")),
                "missing_evidence": list(requirement.get("missing_evidence", []) or []),
                "blocked_claims": [
                    "peer_superiority",
                    "transferable_roi",
                    "generic_benchmark_interpretation",
                ],
            }
        )

    for row in list(comparison_validity_register or []):
        if bool(row.get("comparable")):
            continue
        rows.append(
            {
                "blocker_code": text(row.get("peer_frame")) or "comparison_not_yet_valid",
                "why": text(row.get("why")),
                "missing_evidence": list(row.get("normalization_required", []) or []),
                "blocked_claims": [
                    "peer_superiority",
                    "transferable_roi",
                    "generic_benchmark_interpretation",
                ],
            }
        )
    return rows


def build_comparison_not_yet_valid_register(
    *,
    asset_family_research_profile: dict[str, Any],
    comparison_blocker_register: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    asset_family = text(asset_family_research_profile.get("asset_family"))
    if not comparison_blocker_register:
        return []

    missing_labels: list[str] = []
    for row in comparison_blocker_register:
        for item in list(row.get("missing_evidence", []) or []):
            label = text(item)
            if label and label not in missing_labels:
                missing_labels.append(label)
    top_missing = missing_labels[:5]

    if asset_family in {"logistics_warehouse", "cold_chain"}:
        explanation = (
            "Do not compare this warehouse against generic warehouse EUI until "
            + ", ".join(top_missing)
            + " are known."
        )
    elif asset_family in {"industrial_manufacturing", "thermal_process_site", "utility_heavy_site"}:
        explanation = (
            "Do not compare this industrial site against area-based peers until "
            + ", ".join(top_missing)
            + " are known."
        )
    elif asset_family == "commercial_building":
        explanation = (
            "Do not treat whole-building benchmarking as owner truth until "
            + ", ".join(top_missing)
            + " are known."
        )
    else:
        explanation = (
            "Comparison is not yet valid until "
            + ", ".join(top_missing)
            + " are known."
        )

    return [
        {
            "asset_family": asset_family,
            "comparison_status": "comparison_not_yet_valid",
            "explanation": explanation,
            "required_before_comparison": top_missing,
            "prohibited_claims": [
                "peer_superiority",
                "transferable_roi",
                "generic_benchmark_interpretation",
            ],
        }
    ]
