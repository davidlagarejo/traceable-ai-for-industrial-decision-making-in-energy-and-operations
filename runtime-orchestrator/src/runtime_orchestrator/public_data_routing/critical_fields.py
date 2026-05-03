from __future__ import annotations

from .schemas import AssetType, CriticalFieldRequirement, EvidenceGatingPlan, SourceLayer
from .target_taxonomy import normalize_asset_type


DEFAULT_MAX_MISSING_CRITICAL_FIELDS = 3


def _field(
    field_name: str,
    rationale: str,
    *,
    minimum_source_layer: SourceLayer,
    prohibited_substitutions: list[str],
    blocking_if_missing: bool = True,
) -> CriticalFieldRequirement:
    return CriticalFieldRequirement(
        field_name=field_name,
        rationale=rationale,
        blocking_if_missing=blocking_if_missing,
        minimum_source_layer=minimum_source_layer,
        prohibited_substitutions=prohibited_substitutions,
    )


BASE_CRITICAL_FIELDS: list[CriticalFieldRequirement] = [
    _field(
        "address_confirmed",
        "The framework must know which physical subject it is evaluating before technical routing starts.",
        minimum_source_layer=SourceLayer.PROPERTY,
        prohibited_substitutions=["ENTITY_LEVEL", "PORTFOLIO_LEVEL", "BENCHMARK_LEVEL"],
    ),
    _field(
        "size_or_gfa",
        "Scale is required for intensity, compliance and CAPEX framing.",
        minimum_source_layer=SourceLayer.PROPERTY,
        prohibited_substitutions=["ENTITY_LEVEL", "PORTFOLIO_LEVEL"],
    ),
    _field(
        "use_or_occupancy",
        "Operating use controls benchmark family, schedule assumptions and regulatory relevance.",
        minimum_source_layer=SourceLayer.PROPERTY,
        prohibited_substitutions=["BENCHMARK_LEVEL"],
    ),
    _field(
        "year_built",
        "Vintage is required for system plausibility, code context and retrofit framing.",
        minimum_source_layer=SourceLayer.PROPERTY,
        prohibited_substitutions=["ENTITY_LEVEL"],
    ),
    _field(
        "energy_baseline_or_proxy",
        "A minimum baseline anchor is required for any energy-facing scenario.",
        minimum_source_layer=SourceLayer.ENERGY,
        prohibited_substitutions=["ENTITY_LEVEL"],
    ),
    _field(
        "fuel_type",
        "Fuel mix governs emissions, transition risk and relevant system logic.",
        minimum_source_layer=SourceLayer.ENERGY,
        prohibited_substitutions=["PORTFOLIO_LEVEL"],
    ),
    _field(
        "system_presence",
        "At least one admissible clue of system presence is needed for technical reasoning.",
        minimum_source_layer=SourceLayer.PERMIT,
        prohibited_substitutions=["BENCHMARK_LEVEL", "ENTITY_LEVEL"],
    ),
    _field(
        "regulatory_applicability",
        "The rule family must be routed before compliance or penalty logic may appear.",
        minimum_source_layer=SourceLayer.REGULATORY,
        prohibited_substitutions=["ENTITY_LEVEL", "PORTFOLIO_LEVEL"],
    ),
]


ASSET_TYPE_CRITICAL_FIELDS: dict[AssetType, list[CriticalFieldRequirement]] = {
    AssetType.COMMERCIAL_BUILDING: [
        _field(
            "benchmarking_or_local_energy_disclosure",
            "Commercial buildings need a strong public energy baseline route when available.",
            minimum_source_layer=SourceLayer.ENERGY,
            prohibited_substitutions=["BENCHMARK_LEVEL"],
        ),
        _field(
            "hvac_or_controls_clue",
            "At least one system clue is required for retrofit and schedule reasoning.",
            minimum_source_layer=SourceLayer.PERMIT,
            prohibited_substitutions=["ENTITY_LEVEL", "BENCHMARK_LEVEL"],
        ),
    ],
    AssetType.MULTIFAMILY: [
        _field(
            "unit_or_use_mix",
            "Multifamily routing depends on residential occupancy structure.",
            minimum_source_layer=SourceLayer.PROPERTY,
            prohibited_substitutions=["BENCHMARK_LEVEL"],
        ),
    ],
    AssetType.INDUSTRIAL_FACILITY: [
        _field(
            "process_anchor",
            "Industrial routing requires a process or production anchor before technical analysis.",
            minimum_source_layer=SourceLayer.INDUSTRIAL_ENVIRONMENT,
            prohibited_substitutions=["ENTITY_LEVEL", "BENCHMARK_LEVEL"],
        ),
        _field(
            "environmental_or_permit_anchor",
            "Industrial facilities require a permit, emissions, or environmental registry clue.",
            minimum_source_layer=SourceLayer.INDUSTRIAL_ENVIRONMENT,
            prohibited_substitutions=["ENTITY_LEVEL"],
        ),
        _field(
            "throughput_or_load_driver",
            "Process reasoning is weak without throughput or load-driver context.",
            minimum_source_layer=SourceLayer.INDUSTRIAL_ENVIRONMENT,
            prohibited_substitutions=["BENCHMARK_LEVEL"],
        ),
    ],
    AssetType.WAREHOUSE_LOGISTICS: [
        _field(
            "dock_or_throughput_anchor",
            "Warehouse routing depends on logistics intensity, docks, or throughput clues.",
            minimum_source_layer=SourceLayer.PROPERTY,
            prohibited_substitutions=["ENTITY_LEVEL", "BENCHMARK_LEVEL"],
        ),
        _field(
            "refrigeration_yes_no",
            "Cold chain vs standard warehouse materially changes routing and system expectations.",
            minimum_source_layer=SourceLayer.PERMIT,
            prohibited_substitutions=["BENCHMARK_LEVEL"],
        ),
    ],
    AssetType.DATA_CENTER: [
        _field(
            "critical_load_anchor",
            "Data centers require at least one admissible critical-load clue.",
            minimum_source_layer=SourceLayer.ENERGY,
            prohibited_substitutions=["BENCHMARK_LEVEL", "ENTITY_LEVEL"],
        ),
        _field(
            "cooling_or_redundancy_clue",
            "Cooling topology and redundancy are routing-critical for data centers.",
            minimum_source_layer=SourceLayer.PERMIT,
            prohibited_substitutions=["BENCHMARK_LEVEL"],
        ),
        _field(
            "utility_tariff_or_power_context",
            "Utility and power-service context matter earlier for data centers than for generic buildings.",
            minimum_source_layer=SourceLayer.UTILITY,
            prohibited_substitutions=["ENTITY_LEVEL"],
        ),
    ],
}


def critical_fields_for_asset_type(asset_type: AssetType | str | None) -> list[CriticalFieldRequirement]:
    normalized = normalize_asset_type(asset_type)
    extras = ASSET_TYPE_CRITICAL_FIELDS.get(normalized, []) if normalized else []
    return list(BASE_CRITICAL_FIELDS) + list(extras)


def default_evidence_gating_plan(asset_type: AssetType | str | None) -> EvidenceGatingPlan:
    return EvidenceGatingPlan(
        critical_fields=critical_fields_for_asset_type(asset_type),
        max_missing_critical_fields=DEFAULT_MAX_MISSING_CRITICAL_FIELDS,
        blocked_report_type="Decision-Blocked Brief",
        partial_report_type="Minimum Evidence Report",
        sufficient_report_type="Full Technical Report",
    )
