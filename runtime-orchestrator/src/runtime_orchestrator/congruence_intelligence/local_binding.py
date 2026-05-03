from __future__ import annotations

from typing import Any

from .schemas import dedupe, text

_BINDING_TEMPLATES = {
    "commercial_building": [
        {
            "claim_key": "commercial_building_control_boundary",
            "research_claim": "Owner / tenant control boundary may dominate the economics of any efficiency or compliance pathway.",
            "local_binding_needed": [
                "tenant metering map",
                "lease responsibility matrix",
                "utility billing responsibility map",
                "central plant / BMS topology",
            ],
            "if_unbound_then_only_allow": [
                "screening",
                "bounded peer framing",
                "request control-boundary evidence",
            ],
        },
        {
            "claim_key": "commercial_building_benchmark_vs_roi",
            "research_claim": "Benchmarking and LL84 / LL97 context can indicate exposure, but not owner-capturable retrofit economics.",
            "local_binding_needed": [
                "utility bills",
                "LL97 filing basis",
                "control-boundary evidence",
                "after-hours occupancy profile",
            ],
            "if_unbound_then_only_allow": [
                "compliance screening",
                "prohibit ROI",
                "request minimum evidence",
            ],
        },
    ],
    "industrial_manufacturing": [
        {
            "claim_key": "industrial_process_duty",
            "research_claim": "Apparent energy intensity may reflect structural process load rather than correctable waste.",
            "local_binding_needed": [
                "throughput by shift",
                "product mix or production proxy",
                "utility bills",
                "process map",
                "equipment inventory",
            ],
            "if_unbound_then_only_allow": [
                "bounded process-load hypothesis",
                "prohibit savings closure",
                "request throughput normalization evidence",
            ],
        },
        {
            "claim_key": "industrial_pf_reactive",
            "research_claim": "Demand / PF / reactive exposure may be material where inductive loads dominate and tariff structure penalizes them.",
            "local_binding_needed": [
                "utility bills with demand or PF charges",
                "motor / compressor inventory",
                "demand profile or interval evidence",
            ],
            "if_unbound_then_only_allow": [
                "bounded power-quality hypothesis",
                "measure only if material",
            ],
        },
        {
            "claim_key": "industrial_maintenance",
            "research_claim": "Maintenance maturity and downtime economics may dominate visible energy symptoms.",
            "local_binding_needed": [
                "maintenance logs",
                "downtime records",
                "critical-spares or PM evidence",
            ],
            "if_unbound_then_only_allow": [
                "maintenance maturity not evidenced",
                "request maintenance proof",
            ],
        },
    ],
    "logistics_warehouse": [
        {
            "claim_key": "logistics_service_complexity",
            "research_claim": "Layout, movement, charging schedule and service-level complexity may dominate area-based benchmarking signals.",
            "local_binding_needed": [
                "operating schedule",
                "dock activity profile",
                "forklift fleet and charging schedule",
                "throughput or service-level proxy",
            ],
            "if_unbound_then_only_allow": [
                "bounded logistics congruence hypothesis",
                "do not compare yet",
            ],
        },
    ],
    "cold_chain": [
        {
            "claim_key": "cold_chain_refrigeration_duty",
            "research_claim": "Refrigeration duty and infiltration patterns may dominate total site energy behavior.",
            "local_binding_needed": [
                "temperature bands",
                "door traffic profile",
                "refrigeration inventory",
                "defrost schedule",
            ],
            "if_unbound_then_only_allow": [
                "bounded refrigeration-dominance hypothesis",
                "request minimum evidence",
            ],
        },
    ],
    "thermal_process_site": [
        {
            "claim_key": "thermal_process_thermal_duty",
            "research_claim": "Combustion and thermal-duty losses may matter more than generic building-style efficiency measures.",
            "local_binding_needed": [
                "fuel bills",
                "combustion test records",
                "thermal-duty proxy",
                "process throughput",
            ],
            "if_unbound_then_only_allow": [
                "bounded thermal-loss hypothesis",
                "do not invest yet",
            ],
        },
    ],
    "utility_heavy_site": [
        {
            "claim_key": "utility_heavy_demand_pf",
            "research_claim": "Demand structure, PF and sequencing may dominate savings logic more than aggregate consumption alone.",
            "local_binding_needed": [
                "tariff or bill with demand structure",
                "interval demand profile",
                "major motor inventory",
            ],
            "if_unbound_then_only_allow": [
                "bounded demand / PF hypothesis",
                "measure only if material",
            ],
        },
    ],
    "infrastructure_node": [
        {
            "claim_key": "infrastructure_service_continuity",
            "research_claim": "Service continuity burden, redundancy class and dispatch duty may dominate apparent energy intensity or tariff pressure.",
            "local_binding_needed": [
                "utility bills or service-burden cost evidence",
                "tariff or demand-structure evidence",
                "dispatch or uptime profile",
                "major equipment inventory",
                "maintenance or outage evidence",
            ],
            "if_unbound_then_only_allow": [
                "bounded continuity-duty hypothesis",
                "compare fairly",
                "request minimum evidence",
            ],
        },
    ],
    "generic_operational_asset": [
        {
            "claim_key": "generic_operational_asset_unbounded",
            "research_claim": "Operational logic remains insufficiently bounded for strong congruence analysis.",
            "local_binding_needed": [
                "asset identity and bounded operating scope",
                "basic process or service description",
                "minimum utility and schedule context",
            ],
            "if_unbound_then_only_allow": [
                "classification",
                "bounded screening only",
            ],
        },
    ],
}

_LOCAL_SIGNAL_FAMILIES = {
    "utility_bill_record",
    "equipment_inventory_record",
    "schedule_record",
    "maintenance_contract_record",
    "submetering_record",
    "cmms_record",
    "bms_trend_record",
    "lease_matrix_record",
    "operator_input_record",
    "maintenance_log_record",
    "meter_interval_record",
}

_PACK_BOUND_STATES = {"partially_evidenced", "evidenced"}


def _pack_state(operational_intake_pack: dict[str, Any], pack_name: str) -> str:
    return text((operational_intake_pack or {}).get(pack_name, {}).get("current_state"))


def _count_rows(rows: list[dict[str, Any]] | None) -> int:
    return len(list(rows or []))


def _claim_binding_state(
    *,
    claim_key: str,
    route_state: str,
    target_type: str,
    observed_local_families: set[str],
    operational_intake_pack: dict[str, Any],
    control_boundary_evidence_register: list[dict[str, Any]],
    maintenance_proof_evidence_register: list[dict[str, Any]],
    utility_charge_breakdown_register: list[dict[str, Any]],
    tariff_exposure_register: list[dict[str, Any]],
    owner_operator_tenant_responsibility_register: list[dict[str, Any]],
) -> tuple[str, list[str], str]:
    if target_type != "OPERATING_ASSET":
        return (
            "inadmissible_until_asset_identity_bounded",
            [],
            "The target has not cleared the bounded operating-asset gate yet.",
        )
    if route_state != "operational_asset_candidate":
        return (
            "unbound",
            [],
            "The case has not cleared the operational-asset route state yet.",
        )

    utility_pack = _pack_state(operational_intake_pack, "utility_bill_pack")
    tariff_pack = _pack_state(operational_intake_pack, "utility_tariff_pack")
    throughput_pack = _pack_state(operational_intake_pack, "throughput_schedule_pack")
    equipment_pack = _pack_state(operational_intake_pack, "equipment_inventory_pack")
    metering_pack = _pack_state(operational_intake_pack, "metering_boundary_pack")
    lease_pack = _pack_state(operational_intake_pack, "lease_responsibility_pack")
    maintenance_pack = _pack_state(operational_intake_pack, "maintenance_proof_pack")
    cmms_pack = _pack_state(operational_intake_pack, "cmms_or_workorder_pack")
    controls_pack = _pack_state(operational_intake_pack, "bms_or_controls_pack")

    basis: list[str] = []
    sufficient = False

    if claim_key == "commercial_building_control_boundary":
        if _count_rows(control_boundary_evidence_register) > 0:
            basis.append("control_boundary_evidence_register")
        if _count_rows(owner_operator_tenant_responsibility_register) > 1:
            basis.append("owner_operator_tenant_responsibility_register")
        if metering_pack in _PACK_BOUND_STATES:
            basis.append("metering_boundary_pack")
        if lease_pack in _PACK_BOUND_STATES:
            basis.append("lease_responsibility_pack")
        sufficient = (
            _count_rows(control_boundary_evidence_register) >= 2
            and _count_rows(owner_operator_tenant_responsibility_register) >= 2
            and metering_pack == "evidenced"
        )
    elif claim_key == "commercial_building_benchmark_vs_roi":
        if utility_pack in _PACK_BOUND_STATES:
            basis.append("utility_bill_pack")
        if _count_rows(utility_charge_breakdown_register) > 0:
            basis.append("utility_charge_breakdown_register")
        if metering_pack in _PACK_BOUND_STATES or lease_pack in _PACK_BOUND_STATES:
            basis.append("control_boundary_pack")
        sufficient = (
            utility_pack == "evidenced"
            and _count_rows(utility_charge_breakdown_register) > 0
            and (_count_rows(control_boundary_evidence_register) > 0 or lease_pack == "evidenced")
        )
    elif claim_key == "industrial_process_duty":
        if throughput_pack in _PACK_BOUND_STATES:
            basis.append("throughput_schedule_pack")
        if equipment_pack in _PACK_BOUND_STATES:
            basis.append("equipment_inventory_pack")
        if utility_pack in _PACK_BOUND_STATES:
            basis.append("utility_bill_pack")
        if _count_rows(utility_charge_breakdown_register) > 0:
            basis.append("utility_charge_breakdown_register")
        sufficient = (
            throughput_pack in _PACK_BOUND_STATES
            and equipment_pack in _PACK_BOUND_STATES
            and utility_pack in _PACK_BOUND_STATES
            and _count_rows(utility_charge_breakdown_register) > 0
        )
    elif claim_key == "industrial_pf_reactive":
        if utility_pack in _PACK_BOUND_STATES:
            basis.append("utility_bill_pack")
        if tariff_pack in _PACK_BOUND_STATES:
            basis.append("utility_tariff_pack")
        if equipment_pack in _PACK_BOUND_STATES:
            basis.append("equipment_inventory_pack")
        if _count_rows(tariff_exposure_register) > 0:
            basis.append("tariff_exposure_register")
        sufficient = (
            utility_pack in _PACK_BOUND_STATES
            and tariff_pack in _PACK_BOUND_STATES
            and equipment_pack in _PACK_BOUND_STATES
            and _count_rows(tariff_exposure_register) > 0
        )
    elif claim_key == "industrial_maintenance":
        if maintenance_pack in _PACK_BOUND_STATES:
            basis.append("maintenance_proof_pack")
        if cmms_pack in _PACK_BOUND_STATES:
            basis.append("cmms_or_workorder_pack")
        if _count_rows(maintenance_proof_evidence_register) > 0:
            basis.append("maintenance_proof_evidence_register")
        sufficient = (
            maintenance_pack == "evidenced"
            and _count_rows(maintenance_proof_evidence_register) >= 2
        )
    elif claim_key == "logistics_service_complexity":
        if throughput_pack in _PACK_BOUND_STATES:
            basis.append("throughput_schedule_pack")
        if equipment_pack in _PACK_BOUND_STATES:
            basis.append("equipment_inventory_pack")
        if metering_pack in _PACK_BOUND_STATES:
            basis.append("metering_boundary_pack")
        if _count_rows(control_boundary_evidence_register) > 0:
            basis.append("control_boundary_evidence_register")
        sufficient = (
            throughput_pack in _PACK_BOUND_STATES
            and equipment_pack in _PACK_BOUND_STATES
            and (_count_rows(control_boundary_evidence_register) > 0 or metering_pack == "evidenced")
        )
    elif claim_key == "cold_chain_refrigeration_duty":
        if throughput_pack in _PACK_BOUND_STATES:
            basis.append("throughput_schedule_pack")
        if equipment_pack in _PACK_BOUND_STATES:
            basis.append("equipment_inventory_pack")
        if controls_pack in _PACK_BOUND_STATES:
            basis.append("bms_or_controls_pack")
        if maintenance_pack in _PACK_BOUND_STATES:
            basis.append("maintenance_proof_pack")
        sufficient = (
            throughput_pack in _PACK_BOUND_STATES
            and equipment_pack in _PACK_BOUND_STATES
            and (controls_pack in _PACK_BOUND_STATES or maintenance_pack in _PACK_BOUND_STATES)
        )
    elif claim_key == "thermal_process_thermal_duty":
        if utility_pack in _PACK_BOUND_STATES:
            basis.append("utility_bill_pack")
        if throughput_pack in _PACK_BOUND_STATES:
            basis.append("throughput_schedule_pack")
        if tariff_pack in _PACK_BOUND_STATES:
            basis.append("utility_tariff_pack")
        sufficient = utility_pack in _PACK_BOUND_STATES and throughput_pack in _PACK_BOUND_STATES
    elif claim_key == "utility_heavy_demand_pf":
        if utility_pack in _PACK_BOUND_STATES:
            basis.append("utility_bill_pack")
        if tariff_pack in _PACK_BOUND_STATES:
            basis.append("utility_tariff_pack")
        if equipment_pack in _PACK_BOUND_STATES:
            basis.append("equipment_inventory_pack")
        if _count_rows(tariff_exposure_register) > 0:
            basis.append("tariff_exposure_register")
        sufficient = (
            utility_pack in _PACK_BOUND_STATES
            and tariff_pack in _PACK_BOUND_STATES
            and equipment_pack in _PACK_BOUND_STATES
        )
    elif claim_key == "infrastructure_service_continuity":
        if utility_pack in _PACK_BOUND_STATES:
            basis.append("utility_bill_pack")
        if tariff_pack in _PACK_BOUND_STATES:
            basis.append("utility_tariff_pack")
        if throughput_pack in _PACK_BOUND_STATES:
            basis.append("throughput_schedule_pack")
        if equipment_pack in _PACK_BOUND_STATES:
            basis.append("equipment_inventory_pack")
        if maintenance_pack in _PACK_BOUND_STATES:
            basis.append("maintenance_proof_pack")
        if cmms_pack in _PACK_BOUND_STATES:
            basis.append("cmms_or_workorder_pack")
        if _count_rows(maintenance_proof_evidence_register) > 0:
            basis.append("maintenance_proof_evidence_register")
        if _count_rows(tariff_exposure_register) > 0:
            basis.append("tariff_exposure_register")
        sufficient = (
            utility_pack in _PACK_BOUND_STATES
            and equipment_pack in _PACK_BOUND_STATES
            and throughput_pack in _PACK_BOUND_STATES
            and (maintenance_pack in _PACK_BOUND_STATES or cmms_pack in _PACK_BOUND_STATES)
        )
    else:
        if observed_local_families:
            basis.append("local_operator_evidence_present")
        sufficient = False

    if sufficient:
        return (
            "sufficiently_bound",
            dedupe(basis),
            "The claim now has enough local evidence classes to support stronger bounded congruence use without implying full closure.",
        )
    if basis or observed_local_families:
        if not basis and observed_local_families:
            basis = ["local_operator_evidence_present"]
        return (
            "partially_bound",
            dedupe(basis),
            "The claim has meaningful local evidence, but still lacks enough bounded support for stronger local truth promotion.",
        )
    return (
        "public_context_only_unbound",
        [],
        "The claim is still supported only by public or archetypal context and remains below local binding threshold.",
    )


def build_local_evidence_binding_register(
    *,
    asset_family_research_profile: dict[str, Any],
    target_classification_object: dict[str, Any],
    source_register: list[dict[str, Any]],
    operational_intake_pack: dict[str, Any] | None = None,
    control_boundary_evidence_register: list[dict[str, Any]] | None = None,
    maintenance_proof_evidence_register: list[dict[str, Any]] | None = None,
    utility_charge_breakdown_register: list[dict[str, Any]] | None = None,
    tariff_exposure_register: list[dict[str, Any]] | None = None,
    owner_operator_tenant_responsibility_register: list[dict[str, Any]] | None = None,
) -> list[dict[str, Any]]:
    asset_family = text(asset_family_research_profile.get("asset_family")) or "generic_operational_asset"
    route_state = text(asset_family_research_profile.get("route_state"))
    observed_local_families = {
        text(source.get("source_family"))
        for source in list(source_register or [])
        if text(source.get("source_family")) in _LOCAL_SIGNAL_FAMILIES
    }
    target_type = text(target_classification_object.get("target_type"))

    rows: list[dict[str, Any]] = []
    for template in list(_BINDING_TEMPLATES.get(asset_family, _BINDING_TEMPLATES["generic_operational_asset"])):
        binding_state, binding_basis, binding_sufficiency_reason = _claim_binding_state(
            claim_key=text(template.get("claim_key")),
            route_state=route_state,
            target_type=target_type,
            observed_local_families=observed_local_families,
            operational_intake_pack=dict(operational_intake_pack or {}),
            control_boundary_evidence_register=list(control_boundary_evidence_register or []),
            maintenance_proof_evidence_register=list(maintenance_proof_evidence_register or []),
            utility_charge_breakdown_register=list(utility_charge_breakdown_register or []),
            tariff_exposure_register=list(tariff_exposure_register or []),
            owner_operator_tenant_responsibility_register=list(owner_operator_tenant_responsibility_register or []),
        )
        rows.append(
            {
                "claim_key": text(template.get("claim_key")),
                "research_claim": text(template.get("research_claim")),
                "asset_family_context": asset_family,
                "local_binding_needed": list(template.get("local_binding_needed", []) or []),
                "current_local_binding_state": binding_state,
                "binding_basis": binding_basis,
                "binding_sufficiency_reason": binding_sufficiency_reason,
                "if_unbound_then_only_allow": list(template.get("if_unbound_then_only_allow", []) or []),
            }
        )
    return rows


def build_binding_upgrade_register(
    *,
    local_evidence_binding_register: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for row in list(local_evidence_binding_register or []):
        rows.append(
            {
                "claim_key": text(row.get("claim_key")),
                "research_claim": text(row.get("research_claim")),
                "binding_state": text(row.get("current_local_binding_state")),
                "binding_basis": list(row.get("binding_basis", []) or []),
                "upgrade_reason": text(row.get("binding_sufficiency_reason")),
            }
        )
    return rows


def build_local_truth_confidence_register(
    *,
    local_evidence_binding_register: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    confidence_map = {
        "inadmissible_until_asset_identity_bounded": "inadmissible",
        "unbound": "screening_only",
        "public_context_only_unbound": "screening_only",
        "partially_bound": "bounded_partial_local_truth",
        "sufficiently_bound": "bounded_strong_local_truth",
    }
    rows: list[dict[str, Any]] = []
    for row in list(local_evidence_binding_register or []):
        state = text(row.get("current_local_binding_state"))
        rows.append(
            {
                "claim_key": text(row.get("claim_key")),
                "research_claim": text(row.get("research_claim")),
                "local_truth_confidence": confidence_map.get(state, "screening_only"),
                "binding_state": state,
            }
        )
    return rows


def build_binding_sufficiency_reason_register(
    *,
    local_evidence_binding_register: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    return [
        {
            "claim_key": text(row.get("claim_key")),
            "binding_state": text(row.get("current_local_binding_state")),
            "binding_sufficiency_reason": text(row.get("binding_sufficiency_reason")),
        }
        for row in list(local_evidence_binding_register or [])
    ]
