from __future__ import annotations

from typing import Any

from .levels import EvidenceMaturityLevel
from .schemas import ClusterMaturityRecord, VariableMaturityRecord


_CLUSTER_VARIABLES: dict[str, list[str]] = {
    "identity_cluster": [
        "asset_vs_entity_classification",
        "address",
        "asset_name",
        "asset_type",
        "parcel_id",
        "building_id",
    ],
    "boundary_cluster": [
        "site_boundary",
        "ownership_scope",
        "entity_scope",
        "tenant_control_boundary",
        "owner_control_boundary",
    ],
    "geometry_size_cluster": [
        "GFA",
        "rentable_area",
        "floor_count",
        "site_area",
    ],
    "vintage_structure_cluster": [
        "year_built",
        "major_renovations",
        "construction_type",
        "structural_constraints",
    ],
    "operating_regime_cluster": [
        "operating_schedule",
        "occupancy",
        "throughput",
        "process_flow",
        "load_driver",
        "operational_variability",
    ],
    "fuel_energy_cluster": [
        "utility_bills",
        "interval_meter_data",
        "EUI",
        "primary_fuel",
        "secondary_fuel",
        "electricity_consumption",
        "gas_consumption",
        "load_profile",
        "peak_demand",
        "emissions",
    ],
    "systems_cluster": [
        "HVAC_type",
        "BMS_presence",
        "controls_architecture",
        "refrigeration_system",
        "boilers",
        "chillers",
        "compressed_air",
        "submetering",
        "metering_boundary",
        "maintenance_history",
        "reliability_history",
    ],
    "control_boundary_cluster": [
        "tenant_control_boundary",
        "owner_control_boundary",
        "metering_boundary",
        "submetering",
        "stakeholder_control",
    ],
    "regulatory_cluster": [
        "jurisdiction",
        "applicable_rule_family",
        "regulated_floor_area",
        "emissions",
        "benchmarking_requirement",
        "compliance_filing",
        "penalty_rate",
        "compliance_period",
    ],
    "financial_boundary_cluster": [
        "tariff_class",
        "energy_cost",
        "CAPEX",
        "OPEX",
        "NOI",
        "financing_cost",
        "debt_schedule",
    ],
}

_CLUSTER_ANCHORS: dict[str, list[str]] = {
    "identity_cluster": ["asset_vs_entity_classification", "address", "asset_type"],
    "boundary_cluster": ["tenant_control_boundary", "owner_control_boundary", "site_boundary"],
    "geometry_size_cluster": ["GFA", "site_area", "floor_count"],
    "vintage_structure_cluster": ["year_built", "major_renovations"],
    "operating_regime_cluster": ["operating_schedule", "occupancy", "throughput", "process_flow"],
    "fuel_energy_cluster": ["EUI", "utility_bills", "primary_fuel", "emissions"],
    "systems_cluster": ["HVAC_type", "controls_architecture", "BMS_presence", "compressed_air"],
    "control_boundary_cluster": ["tenant_control_boundary", "owner_control_boundary", "metering_boundary"],
    "regulatory_cluster": ["jurisdiction", "applicable_rule_family", "regulated_floor_area", "compliance_filing"],
    "financial_boundary_cluster": ["tariff_class", "CAPEX", "energy_cost", "NOI"],
}


def _cluster_consequence(cluster_name: str, level: EvidenceMaturityLevel) -> str:
    if level == EvidenceMaturityLevel.L0:
        return f"{cluster_name} cannot support technical or decision-grade use yet."
    if level == EvidenceMaturityLevel.L1:
        return f"{cluster_name} supports proxy-level screening only."
    if level == EvidenceMaturityLevel.L2:
        return f"{cluster_name} supports asset-specific but still incomplete screening."
    if level == EvidenceMaturityLevel.L3:
        return f"{cluster_name} is strong enough for public-evidence screening and bounded claim support."
    return f"{cluster_name} is hardened enough for the strongest bounded downstream use."


def _cluster_level(records_by_name: dict[str, VariableMaturityRecord], cluster_name: str) -> EvidenceMaturityLevel:
    variables = _CLUSTER_VARIABLES[cluster_name]
    anchors = _CLUSTER_ANCHORS[cluster_name]
    levels = {name: records_by_name[name].maturity_level for name in variables if name in records_by_name}
    anchor_levels = [levels[name] for name in anchors if name in levels]
    if not levels:
        return EvidenceMaturityLevel.L0
    if any(level >= EvidenceMaturityLevel.L3 for level in anchor_levels):
        return EvidenceMaturityLevel.L3
    if any(level >= EvidenceMaturityLevel.L2 for level in anchor_levels):
        return EvidenceMaturityLevel.L2
    if any(level >= EvidenceMaturityLevel.L1 for level in levels.values()):
        return EvidenceMaturityLevel.L1
    return EvidenceMaturityLevel.L0


def _cluster_profile(rows: list[ClusterMaturityRecord]) -> dict[str, Any]:
    levels = {row.cluster_name: row.maturity_level for row in rows}
    screening_ready = [
        name for name, level in levels.items()
        if level >= EvidenceMaturityLevel.L3
    ]
    weak_or_missing = [
        name for name, level in levels.items()
        if level <= EvidenceMaturityLevel.L1
    ]
    return {
        "cluster_levels": {name: level.code for name, level in levels.items()},
        "screening_ready_clusters": screening_ready,
        "weak_or_missing_clusters": weak_or_missing,
        "strong_public_screening_possible": bool(
            levels.get("identity_cluster", EvidenceMaturityLevel.L0) >= EvidenceMaturityLevel.L3
            and levels.get("geometry_size_cluster", EvidenceMaturityLevel.L0) >= EvidenceMaturityLevel.L3
            and levels.get("regulatory_cluster", EvidenceMaturityLevel.L0) >= EvidenceMaturityLevel.L3
        ),
    }


def derive_cluster_maturity(variable_records: list[VariableMaturityRecord]) -> tuple[list[ClusterMaturityRecord], dict[str, Any]]:
    records_by_name = {record.variable_name: record for record in variable_records}
    rows: list[ClusterMaturityRecord] = []
    for cluster_name, variables in _CLUSTER_VARIABLES.items():
        observed_records = [
            records_by_name[name]
            for name in variables
            if name in records_by_name and records_by_name[name].maturity_level > EvidenceMaturityLevel.L0
        ]
        level = _cluster_level(records_by_name, cluster_name)
        rows.append(
            ClusterMaturityRecord(
                cluster_name=cluster_name,
                maturity_level=level,
                evidence=[
                    f"{record.variable_name}={record.maturity_level.code}"
                    for record in observed_records[:6]
                ],
                source=[
                    str(record.evidence_source)
                    for record in observed_records[:4]
                ],
                consequence=_cluster_consequence(cluster_name, level),
            )
        )
    return rows, _cluster_profile(rows)
