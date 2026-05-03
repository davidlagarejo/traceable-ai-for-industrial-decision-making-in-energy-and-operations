from __future__ import annotations

from typing import Any

from .schemas import text

_UNRESOLVED_PACK_STATES = {
    "requested_but_absent",
    "public_context_only",
    "uploaded_but_unparsed",
    "parsed_but_weak",
    "partially_evidenced",
}

_HYPOTHESIS_LIBRARY: dict[str, list[dict[str, Any]]] = {
    "logistics_warehouse": [
        {
            "hypothesis_id": "warehouse_subtype_temperature_regime",
            "rival_cluster": "comparison_basis",
            "driver_domain": "asset_family_and_temperature_regime",
            "hypothesis_label": "This is cold-chain or mixed-temperature and area-based comparison is invalid.",
            "linked_need_ids": ["warehouse_subtype_classification", "refrigeration_presence"],
            "linked_pack_names": ["throughput_schedule_pack"],
            "signal_register_keys": [],
            "blocked_claims_if_unresolved": ["generic_warehouse_eui_claim", "peer_superiority_claim"],
            "financial_exposure_tags": ["wrong_peer_valuation"],
            "base_priority": 92,
        },
        {
            "hypothesis_id": "warehouse_service_intensity_denominator",
            "rival_cluster": "comparison_basis",
            "driver_domain": "dock_and_schedule",
            "hypothesis_label": "Energy intensity is driven by dock throughput and service windows.",
            "linked_need_ids": ["dock_and_service_intensity"],
            "linked_pack_names": ["throughput_schedule_pack"],
            "signal_register_keys": [],
            "blocked_claims_if_unresolved": ["generic_warehouse_eui_claim", "peer_superiority_claim"],
            "financial_exposure_tags": ["wrong_underwriting_premium"],
            "base_priority": 88,
        },
        {
            "hypothesis_id": "warehouse_tariff_orchestration",
            "rival_cluster": "cost_driver",
            "driver_domain": "tariff_and_charging",
            "hypothesis_label": "Demand cost is being driven by charging peaks.",
            "linked_need_ids": ["mhe_charging_and_mechanical_clues", "utility_territory_and_tariff_context"],
            "linked_pack_names": ["utility_bill_pack", "utility_tariff_pack", "throughput_schedule_pack"],
            "signal_register_keys": ["tariff_exposure_register", "utility_charge_breakdown_register"],
            "blocked_claims_if_unresolved": ["demand_charge_claim", "tariff_exposure_claim"],
            "financial_exposure_tags": ["demand_charge_exposure_hidden"],
            "base_priority": 95,
        },
        {
            "hypothesis_id": "warehouse_control_boundary_value_leakage",
            "rival_cluster": "value_capture",
            "driver_domain": "control_boundary",
            "hypothesis_label": "The operator controls the dominant drivers and value leaks across the boundary.",
            "linked_need_ids": ["operator_boundary_and_control"],
            "linked_pack_names": ["lease_responsibility_pack", "metering_boundary_pack"],
            "signal_register_keys": [
                "control_boundary_evidence_register",
                "owner_operator_tenant_responsibility_register",
            ],
            "blocked_claims_if_unresolved": ["owner_capturable_roi_claim", "retrofit_capture_claim"],
            "financial_exposure_tags": ["tenant_operator_value_leakage"],
            "base_priority": 93,
        },
        {
            "hypothesis_id": "warehouse_mechanical_topology",
            "rival_cluster": "loss_pattern",
            "driver_domain": "mechanical_context",
            "hypothesis_label": "Loss is dominated by dock / air exchange interaction.",
            "linked_need_ids": ["mhe_charging_and_mechanical_clues"],
            "linked_pack_names": ["equipment_inventory_pack"],
            "signal_register_keys": ["permit_to_system_register"],
            "blocked_claims_if_unresolved": ["mechanical_loss_claim"],
            "financial_exposure_tags": ["wrong_retrofit_sequencing"],
            "base_priority": 78,
        },
    ],
    "industrial_manufacturing": [
        {
            "hypothesis_id": "manufacturing_process_thermal_lane",
            "rival_cluster": "comparison_basis",
            "driver_domain": "process_and_thermal_lane",
            "hypothesis_label": "Energy intensity is dominated by the process and thermal duty itself.",
            "linked_need_ids": ["process_and_permit_profile", "thermal_system_and_utility_mix"],
            "linked_pack_names": ["equipment_inventory_pack", "permit_detail_pack"],
            "signal_register_keys": ["permit_to_system_register", "regulated_process_scope_register"],
            "blocked_claims_if_unresolved": ["process_energy_claim", "thermal_lane_claim"],
            "financial_exposure_tags": ["wrong_retrofit_sequencing"],
            "base_priority": 92,
        },
        {
            "hypothesis_id": "manufacturing_compressed_air_support_waste",
            "rival_cluster": "loss_pattern",
            "driver_domain": "compressed_air",
            "hypothesis_label": "Compressed air is a major avoidable support-system waste source.",
            "linked_need_ids": ["thermal_system_and_utility_mix"],
            "linked_pack_names": ["equipment_inventory_pack"],
            "signal_register_keys": ["permit_to_system_register"],
            "blocked_claims_if_unresolved": ["compressed_air_savings_claim"],
            "financial_exposure_tags": ["operational_savings_not_capturable"],
            "base_priority": 87,
        },
        {
            "hypothesis_id": "manufacturing_throughput_normalization",
            "rival_cluster": "comparison_basis",
            "driver_domain": "throughput_and_product_mix",
            "hypothesis_label": "The site is energy-intensive because throughput or product mix is heavy.",
            "linked_need_ids": ["throughput_proxy_and_schedule"],
            "linked_pack_names": ["throughput_schedule_pack"],
            "signal_register_keys": [],
            "blocked_claims_if_unresolved": ["peer_superiority_claim", "throughput_normalized_claim"],
            "financial_exposure_tags": ["wrong_underwriting_premium"],
            "base_priority": 90,
        },
        {
            "hypothesis_id": "manufacturing_maintenance_downtime",
            "rival_cluster": "maintenance_reality",
            "driver_domain": "maintenance_and_reliability",
            "hypothesis_label": "Downtime and maintenance reality dominate the business case.",
            "linked_need_ids": ["process_and_permit_profile"],
            "linked_pack_names": ["maintenance_proof_pack", "cmms_or_workorder_pack"],
            "signal_register_keys": ["maintenance_proof_evidence_register"],
            "blocked_claims_if_unresolved": ["maintenance_maturity_claim", "downtime_economics_claim"],
            "financial_exposure_tags": ["maintenance_downtime_exposure"],
            "base_priority": 91,
        },
    ],
}


def _as_dict(value: Any) -> dict[str, Any]:
    return dict(value) if isinstance(value, dict) else {}


def _as_list(value: Any) -> list[Any]:
    return list(value) if isinstance(value, list) else []


def _need_ids(discovery_need_register: list[dict[str, Any]]) -> set[str]:
    return {
        text(row.get("need_id"))
        for row in _as_list(discovery_need_register)
        if text(row.get("need_id"))
    }


def _pack_state_map(operational_intake_pack: dict[str, Any]) -> dict[str, str]:
    rows = _as_list(operational_intake_pack.get("diligence_pack_register"))
    return {
        text(row.get("pack_name")): text(row.get("current_state"))
        for row in rows
        if text(row.get("pack_name"))
    }


def _unresolved_pack_hits(pack_states: dict[str, str], pack_names: list[str]) -> list[str]:
    return [
        pack_name
        for pack_name in pack_names
        if pack_states.get(pack_name) in _UNRESOLVED_PACK_STATES
    ]


def _register_hits(operational_intake_pack: dict[str, Any], register_keys: list[str]) -> list[str]:
    hits: list[str] = []
    for key in register_keys:
        value = operational_intake_pack.get(key)
        if isinstance(value, list) and value:
            hits.append(key)
        elif isinstance(value, dict) and value:
            hits.append(key)
    return hits


def _financial_hits(spec: dict[str, Any], congruence_case_state: dict[str, Any]) -> list[str]:
    active = {
        text(item)
        for item in _as_list(congruence_case_state.get("financial_exposure_priority"))
        if text(item)
    }
    return [
        tag
        for tag in _as_list(spec.get("financial_exposure_tags"))
        if text(tag) and text(tag) in active
    ]


def _score_components(
    *,
    spec: dict[str, Any],
    active_need_hits: list[str],
    unresolved_pack_hits: list[str],
    register_hits: list[str],
    financial_hits: list[str],
) -> dict[str, int]:
    return {
        "base_priority": int(spec.get("base_priority", 0) or 0),
        "need_pressure_value": min(len(active_need_hits) * 22, 44),
        "pack_pressure_value": min(len(unresolved_pack_hits) * 16, 48),
        "signal_register_value": min(len(register_hits) * 14, 28),
        "financial_pressure_value": min(len(financial_hits) * 12, 24),
        "claim_risk_value": min(len(_as_list(spec.get("blocked_claims_if_unresolved"))) * 6, 24),
    }


def _activation_basis(
    *,
    active_need_hits: list[str],
    unresolved_pack_hits: list[str],
    register_hits: list[str],
    financial_hits: list[str],
) -> list[str]:
    basis: list[str] = []
    basis.extend(f"need:{value}" for value in active_need_hits)
    basis.extend(f"pack:{value}" for value in unresolved_pack_hits)
    basis.extend(f"signal:{value}" for value in register_hits)
    basis.extend(f"financial:{value}" for value in financial_hits)
    return basis


def build_rival_hypothesis_seed_register(
    *,
    asset_family_research_profile: dict[str, Any],
    operational_intake_pack: dict[str, Any],
    discovery_need_register: list[dict[str, Any]],
    congruence_case_state: dict[str, Any] | None = None,
) -> list[dict[str, Any]]:
    asset_family = text(asset_family_research_profile.get("asset_family"))
    specs = list(_HYPOTHESIS_LIBRARY.get(asset_family, []) or [])
    active_need_ids = _need_ids(discovery_need_register)
    pack_states = _pack_state_map(operational_intake_pack)
    congruence_case_state = _as_dict(congruence_case_state)

    rows: list[dict[str, Any]] = []
    for spec in specs:
        linked_need_ids = [text(value) for value in _as_list(spec.get("linked_need_ids")) if text(value)]
        linked_pack_names = [text(value) for value in _as_list(spec.get("linked_pack_names")) if text(value)]
        active_need_hits = [value for value in linked_need_ids if value in active_need_ids]
        unresolved_pack_hits = _unresolved_pack_hits(pack_states, linked_pack_names)
        register_hits = _register_hits(
            operational_intake_pack,
            [text(value) for value in _as_list(spec.get("signal_register_keys")) if text(value)],
        )
        financial_hits = _financial_hits(spec, congruence_case_state)
        activation_basis = _activation_basis(
            active_need_hits=active_need_hits,
            unresolved_pack_hits=unresolved_pack_hits,
            register_hits=register_hits,
            financial_hits=financial_hits,
        )
        if not activation_basis:
            continue
        score_components = _score_components(
            spec=spec,
            active_need_hits=active_need_hits,
            unresolved_pack_hits=unresolved_pack_hits,
            register_hits=register_hits,
            financial_hits=financial_hits,
        )
        priority_score = sum(int(value) for value in score_components.values())
        rows.append(
            {
                "hypothesis_id": text(spec.get("hypothesis_id")),
                "asset_family": asset_family,
                "rival_cluster": text(spec.get("rival_cluster")),
                "driver_domain": text(spec.get("driver_domain")),
                "hypothesis_label": text(spec.get("hypothesis_label")),
                "activation_state": "active",
                "activation_basis": activation_basis,
                "linked_need_ids": linked_need_ids,
                "linked_pack_names": linked_pack_names,
                "signal_register_hits": register_hits,
                "blocked_claims_if_unresolved": [
                    text(value)
                    for value in _as_list(spec.get("blocked_claims_if_unresolved"))
                    if text(value)
                ],
                "financial_exposure_tags": [
                    text(value)
                    for value in _as_list(spec.get("financial_exposure_tags"))
                    if text(value)
                ],
                "priority_score": priority_score,
                "priority_score_components": score_components,
                "public_search_first": bool(linked_need_ids),
            }
        )
    rows.sort(key=lambda row: (-int(row.get("priority_score", 0) or 0), text(row.get("hypothesis_id"))))
    return rows


def build_dominant_hypothesis_register(
    *,
    rival_hypothesis_seed_register: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for index, row in enumerate(list(rival_hypothesis_seed_register or []), start=1):
        activation_basis = [text(value) for value in _as_list(row.get("activation_basis")) if text(value)]
        reason_parts = activation_basis[:3] or ["governed hypothesis pressure"]
        rows.append(
            {
                "dominance_rank": index,
                "hypothesis_id": text(row.get("hypothesis_id")),
                "hypothesis_label": text(row.get("hypothesis_label")),
                "rival_cluster": text(row.get("rival_cluster")),
                "driver_domain": text(row.get("driver_domain")),
                "dominance_score": int(row.get("priority_score", 0) or 0),
                "dominance_reason": "Activated by " + ", ".join(reason_parts) + ".",
                "linked_need_ids": list(row.get("linked_need_ids", []) or []),
                "linked_pack_names": list(row.get("linked_pack_names", []) or []),
                "blocked_claims_if_unresolved": list(row.get("blocked_claims_if_unresolved", []) or []),
                "financial_exposure_tags": list(row.get("financial_exposure_tags", []) or []),
            }
        )
    return rows


def _stop_map(stop_condition_register: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    return {
        text(row.get("path_id")): _as_dict(row)
        for row in _as_list(stop_condition_register)
        if text(row.get("path_id"))
    }


def build_hypothesis_evidence_gap_register(
    *,
    rival_hypothesis_seed_register: list[dict[str, Any]],
    stop_condition_register: list[dict[str, Any]],
    next_best_search_register: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    stop_by_path = _stop_map(stop_condition_register)
    next_by_need = {
        text(row.get("need_id")): _as_dict(row)
        for row in _as_list(next_best_search_register)
        if text(row.get("need_id"))
    }
    rows: list[dict[str, Any]] = []
    for row in _as_list(rival_hypothesis_seed_register):
        linked_need_ids = [text(value) for value in _as_list(row.get("linked_need_ids")) if text(value)]
        linked_pack_names = [text(value) for value in _as_list(row.get("linked_pack_names")) if text(value)]
        evidence_needed: list[str] = []
        escalation_conditions: list[str] = []
        next_search_targets: list[str] = []
        for path_id in linked_need_ids + linked_pack_names:
            stop_row = stop_by_path.get(path_id, {})
            minimum = text(stop_row.get("minimum_sufficient_evidence"))
            if minimum and minimum not in evidence_needed:
                evidence_needed.append(minimum)
            escalation = text(stop_row.get("escalation_condition"))
            if escalation and escalation not in escalation_conditions:
                escalation_conditions.append(escalation)
        for need_id in linked_need_ids:
            next_target = text(next_by_need.get(need_id, {}).get("next_search_target"))
            if next_target and next_target not in next_search_targets:
                next_search_targets.append(next_target)
        rows.append(
            {
                "hypothesis_id": text(row.get("hypothesis_id")),
                "hypothesis_label": text(row.get("hypothesis_label")),
                "linked_need_ids": linked_need_ids,
                "linked_pack_names": linked_pack_names,
                "evidence_needed": evidence_needed,
                "next_public_search_target": next_search_targets,
                "intake_if_missing": " ".join(escalation_conditions),
                "public_search_first": bool(linked_need_ids),
                "evidence_gap_state": "unresolved" if evidence_needed or escalation_conditions else "screening_only",
            }
        )
    return rows


def build_hypothesis_claim_blocker_register(
    *,
    rival_hypothesis_seed_register: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for seed_row in _as_list(rival_hypothesis_seed_register):
        for blocked_claim in _as_list(seed_row.get("blocked_claims_if_unresolved")):
            label = text(blocked_claim)
            if not label:
                continue
            rows.append(
                {
                    "hypothesis_id": text(seed_row.get("hypothesis_id")),
                    "hypothesis_label": text(seed_row.get("hypothesis_label")),
                    "blocked_claim": label,
                    "governance_basis": "hypothesis_seed_register",
                    "linked_need_ids": list(seed_row.get("linked_need_ids", []) or []),
                    "linked_pack_names": list(seed_row.get("linked_pack_names", []) or []),
                }
            )
    return rows
