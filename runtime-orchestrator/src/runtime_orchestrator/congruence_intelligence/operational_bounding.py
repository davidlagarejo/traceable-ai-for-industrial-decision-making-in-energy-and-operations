from __future__ import annotations

from typing import Any

from .schemas import text

_LOCAL_EVIDENCE_STATES = {"partially_evidenced", "evidenced"}

_FAMILY_BOUNDING_REQUIREMENTS = {
    "commercial_building": {
        "hybrid_core_packs": [
            "utility_bill_pack",
            "metering_boundary_pack",
            "lease_responsibility_pack",
            "permit_detail_pack",
        ],
        "operator_core_packs": [
            "bms_or_controls_pack",
            "cmms_or_workorder_pack",
            "maintenance_proof_pack",
        ],
        "required_hybrid_count": 2,
        "required_operator_count": 2,
    },
    "industrial_manufacturing": {
        "hybrid_core_packs": [
            "utility_bill_pack",
            "utility_tariff_pack",
            "throughput_schedule_pack",
            "equipment_inventory_pack",
            "permit_detail_pack",
        ],
        "operator_core_packs": [
            "maintenance_proof_pack",
            "cmms_or_workorder_pack",
        ],
        "required_hybrid_count": 3,
        "required_operator_count": 2,
    },
    "logistics_warehouse": {
        "hybrid_core_packs": [
            "utility_bill_pack",
            "throughput_schedule_pack",
            "equipment_inventory_pack",
            "permit_detail_pack",
        ],
        "operator_core_packs": [
            "metering_boundary_pack",
            "maintenance_proof_pack",
            "cmms_or_workorder_pack",
        ],
        "required_hybrid_count": 3,
        "required_operator_count": 2,
    },
    "cold_chain": {
        "hybrid_core_packs": [
            "utility_bill_pack",
            "throughput_schedule_pack",
            "equipment_inventory_pack",
            "permit_detail_pack",
        ],
        "operator_core_packs": [
            "bms_or_controls_pack",
            "maintenance_proof_pack",
            "cmms_or_workorder_pack",
        ],
        "required_hybrid_count": 3,
        "required_operator_count": 2,
    },
    "thermal_process_site": {
        "hybrid_core_packs": [
            "utility_bill_pack",
            "utility_tariff_pack",
            "throughput_schedule_pack",
            "permit_detail_pack",
        ],
        "operator_core_packs": [
            "maintenance_proof_pack",
            "cmms_or_workorder_pack",
        ],
        "required_hybrid_count": 3,
        "required_operator_count": 2,
    },
    "utility_heavy_site": {
        "hybrid_core_packs": [
            "utility_bill_pack",
            "utility_tariff_pack",
            "equipment_inventory_pack",
        ],
        "operator_core_packs": [
            "maintenance_proof_pack",
            "cmms_or_workorder_pack",
        ],
        "required_hybrid_count": 2,
        "required_operator_count": 2,
    },
    "infrastructure_node": {
        "hybrid_core_packs": [
            "utility_bill_pack",
            "utility_tariff_pack",
            "throughput_schedule_pack",
            "equipment_inventory_pack",
            "permit_detail_pack",
        ],
        "operator_core_packs": [
            "maintenance_proof_pack",
            "cmms_or_workorder_pack",
        ],
        "required_hybrid_count": 3,
        "required_operator_count": 2,
    },
    "generic_operational_asset": {
        "hybrid_core_packs": [
            "utility_bill_pack",
            "throughput_schedule_pack",
            "equipment_inventory_pack",
        ],
        "operator_core_packs": [
            "maintenance_proof_pack",
            "cmms_or_workorder_pack",
        ],
        "required_hybrid_count": 2,
        "required_operator_count": 2,
    },
}


def _pack_state_map(operational_intake_pack: dict[str, Any]) -> dict[str, str]:
    return {
        text(row.get("pack_name")): text(row.get("current_state"))
        for row in list((operational_intake_pack or {}).get("diligence_pack_register", []) or [])
        if text(row.get("pack_name"))
    }


def _local_hits(pack_names: list[str], pack_state_map: dict[str, str]) -> list[str]:
    return [
        pack_name
        for pack_name in pack_names
        if pack_state_map.get(pack_name, "") in _LOCAL_EVIDENCE_STATES
    ]


def build_promotion_blocker_register(
    *,
    asset_family_research_profile: dict[str, Any],
    operational_intake_pack: dict[str, Any],
) -> list[dict[str, Any]]:
    asset_family = text(asset_family_research_profile.get("asset_family")) or "generic_operational_asset"
    route_state = text(asset_family_research_profile.get("route_state"))
    requirements = _FAMILY_BOUNDING_REQUIREMENTS.get(asset_family, _FAMILY_BOUNDING_REQUIREMENTS["generic_operational_asset"])
    pack_states = _pack_state_map(operational_intake_pack)
    hybrid_hits = _local_hits(requirements.get("hybrid_core_packs", []), pack_states)
    operator_hits = _local_hits(requirements.get("operator_core_packs", []), pack_states)

    rows: list[dict[str, Any]] = []
    if route_state != "operational_asset_candidate":
        rows.append(
            {
                "blocker_code": "asset_not_operationally_bounded",
                "severity": "critical",
                "blocks_mode": "hybrid_diligence",
                "why": "The target has not cleared the bounded operating-asset gate yet.",
            }
        )
        return rows

    if len(hybrid_hits) < int(requirements.get("required_hybrid_count", 0) or 0):
        for pack_name in requirements.get("hybrid_core_packs", []):
            if pack_states.get(pack_name, "") not in _LOCAL_EVIDENCE_STATES:
                rows.append(
                    {
                        "blocker_code": "missing_hybrid_core_pack",
                        "severity": "warning",
                        "blocks_mode": "hybrid_diligence",
                        "pack_name": pack_name,
                        "why": f"`{pack_name}` is not yet locally evidenced enough for hybrid diligence promotion.",
                    }
                )
    if len(operator_hits) < int(requirements.get("required_operator_count", 0) or 0):
        for pack_name in requirements.get("operator_core_packs", []):
            if pack_states.get(pack_name, "") not in _LOCAL_EVIDENCE_STATES:
                rows.append(
                    {
                        "blocker_code": "missing_operator_core_pack",
                        "severity": "warning",
                        "blocks_mode": "operator_integrated_congruence",
                        "pack_name": pack_name,
                        "why": f"`{pack_name}` is not yet locally evidenced enough for operator-integrated promotion.",
                    }
                )
    return rows


def build_operational_bounding_scorecard(
    *,
    asset_family_research_profile: dict[str, Any],
    operational_intake_pack: dict[str, Any],
) -> dict[str, Any]:
    asset_family = text(asset_family_research_profile.get("asset_family")) or "generic_operational_asset"
    route_state = text(asset_family_research_profile.get("route_state"))
    research_mode = text(asset_family_research_profile.get("research_mode"))
    requirements = _FAMILY_BOUNDING_REQUIREMENTS.get(asset_family, _FAMILY_BOUNDING_REQUIREMENTS["generic_operational_asset"])
    pack_states = _pack_state_map(operational_intake_pack)

    hybrid_core = list(requirements.get("hybrid_core_packs", []) or [])
    operator_core = list(requirements.get("operator_core_packs", []) or [])
    hybrid_hits = _local_hits(hybrid_core, pack_states)
    operator_hits = _local_hits(operator_core, pack_states)

    bounded_asset_gate_passed = route_state == "operational_asset_candidate"
    if not bounded_asset_gate_passed:
        evidence_mode_state = "public_only_screening"
        next_promotable_mode = "hybrid_diligence"
    elif (
        len(hybrid_hits) >= int(requirements.get("required_hybrid_count", 0) or 0)
        and len(operator_hits) >= int(requirements.get("required_operator_count", 0) or 0)
    ):
        evidence_mode_state = "operator_integrated_congruence"
        next_promotable_mode = ""
    elif len(hybrid_hits) >= int(requirements.get("required_hybrid_count", 0) or 0):
        evidence_mode_state = "hybrid_diligence"
        next_promotable_mode = "operator_integrated_congruence"
    else:
        evidence_mode_state = "public_only_screening"
        next_promotable_mode = "hybrid_diligence"

    return {
        "asset_family": asset_family,
        "route_state": route_state,
        "research_mode_observed": research_mode,
        "bounded_asset_gate_passed": bounded_asset_gate_passed,
        "evidence_mode_state": evidence_mode_state,
        "next_promotable_mode": next_promotable_mode,
        "hybrid_core_packs": hybrid_core,
        "operator_core_packs": operator_core,
        "hybrid_hits": hybrid_hits,
        "operator_hits": operator_hits,
        "hybrid_score": len(hybrid_hits),
        "operator_score": len(operator_hits),
        "required_hybrid_count": int(requirements.get("required_hybrid_count", 0) or 0),
        "required_operator_count": int(requirements.get("required_operator_count", 0) or 0),
        "score_explanation": (
            "Promotion is based on bounded asset identity first, then locally evidenced diligence packs by family. "
            "Public context alone is not enough to cross into hybrid or operator-integrated congruence."
        ),
    }
