from __future__ import annotations

from collections.abc import Iterable

from .jurisdiction_resolver import routing_keys_for_resolution
from .schemas import (
    AssetType,
    DecisionType,
    JurisdictionResolution,
    RoutingPriority,
    SourceRegistryRecord,
    SourceRoutingEntry,
    SourceRoutingPlan,
)
from .target_taxonomy import normalize_asset_type
from .us_layers import (
    CALIFORNIA_SOURCE_REGISTRY,
    INDUSTRIAL_CROSS_STATE_SOURCE_REGISTRY,
    NATIONAL_SOURCE_REGISTRY,
    NYC_SOURCE_REGISTRY,
    TEXAS_SOURCE_REGISTRY,
)


ALL_SOURCE_REGISTRY: list[SourceRegistryRecord] = (
    list(NATIONAL_SOURCE_REGISTRY)
    + list(NYC_SOURCE_REGISTRY)
    + list(CALIFORNIA_SOURCE_REGISTRY)
    + list(TEXAS_SOURCE_REGISTRY)
    + list(INDUSTRIAL_CROSS_STATE_SOURCE_REGISTRY)
)


PRIORITY_ORDER = {
    RoutingPriority.MANDATORY: 0,
    RoutingPriority.HIGH_PRIORITY: 1,
    RoutingPriority.OPTIONAL: 2,
}


BENCHMARK_ONLY_KEYS = {
    "eia_mecs_sector_benchmark",
    "doe_iac_database",
    "openei_industrial_combustion",
    "energy_star_public_profile",
}


IDENTIFICATION_ONLY_EXCLUDED_KEYS = BENCHMARK_ONLY_KEYS | {
    "sec_edgar_company_filings",
    "federal_ira_tax_credit_guidance",
    "nyc_accelerator_program",
}


def _normalize_decision_type(value: DecisionType | str | None) -> DecisionType:
    if isinstance(value, DecisionType):
        return value
    normalized = str(value or "").strip().lower()
    alias_map = {
        "target_identification": DecisionType.TARGET_IDENTIFICATION,
        "acquisition_underwriting": DecisionType.ACQUISITION_UNDERWRITING,
        "retrofit_capex": DecisionType.RETROFIT_CAPEX,
        "compliance_investment": DecisionType.COMPLIANCE_INVESTMENT,
        "process_change": DecisionType.PROCESS_CHANGE,
        "refinancing": DecisionType.REFINANCING,
    }
    return alias_map.get(normalized, DecisionType.TARGET_IDENTIFICATION)


def all_source_registry_records() -> list[SourceRegistryRecord]:
    return list(ALL_SOURCE_REGISTRY)


def registry_records_for_route(
    resolution: JurisdictionResolution,
    asset_type: AssetType | str | None,
) -> list[SourceRegistryRecord]:
    normalized_asset_type = normalize_asset_type(asset_type)
    if normalized_asset_type is None:
        return []
    routing_keys = routing_keys_for_resolution(resolution, normalized_asset_type)
    key_order = {key: index for index, key in enumerate(routing_keys)}
    matched = [
        row for row in ALL_SOURCE_REGISTRY
        if row.asset_type == normalized_asset_type and row.jurisdiction in key_order
    ]
    return sorted(
        matched,
        key=lambda row: (
            key_order.get(row.jurisdiction, 999),
            PRIORITY_ORDER[row.source.priority],
            row.source.source_key,
        ),
    )


def _filtered_for_decision(
    rows: Iterable[SourceRegistryRecord],
    decision_type: DecisionType,
    asset_type: AssetType,
) -> list[SourceRegistryRecord]:
    filtered: list[SourceRegistryRecord] = []
    for row in rows:
        key = row.source.source_key
        if decision_type == DecisionType.TARGET_IDENTIFICATION and key in IDENTIFICATION_ONLY_EXCLUDED_KEYS:
            continue
        if decision_type == DecisionType.COMPLIANCE_INVESTMENT and key == "sec_edgar_company_filings":
            continue
        if decision_type == DecisionType.PROCESS_CHANGE and asset_type != AssetType.INDUSTRIAL_FACILITY and key in {
            "doe_iac_database",
            "openei_industrial_combustion",
        }:
            continue
        filtered.append(row)
    return filtered


def _effective_priority(
    entry: SourceRoutingEntry,
    *,
    decision_type: DecisionType,
    asset_type: AssetType,
) -> RoutingPriority:
    if decision_type == DecisionType.PROCESS_CHANGE and asset_type == AssetType.INDUSTRIAL_FACILITY and entry.source_key in {
        "doe_iac_database",
        "openei_industrial_combustion",
    }:
        return RoutingPriority.HIGH_PRIORITY
    if decision_type == DecisionType.COMPLIANCE_INVESTMENT and entry.layer.value == "regulatory":
        return RoutingPriority.MANDATORY if entry.priority == RoutingPriority.HIGH_PRIORITY else entry.priority
    return entry.priority


def _clone_entry(entry: SourceRoutingEntry, *, priority: RoutingPriority) -> SourceRoutingEntry:
    return SourceRoutingEntry(
        source_key=entry.source_key,
        source_name=entry.source_name,
        layer=entry.layer,
        access_method=entry.access_method,
        fields=list(entry.fields),
        authority=entry.authority,
        update_frequency=entry.update_frequency,
        use=entry.use,
        limitations=entry.limitations,
        priority=priority,
        disallowed_as_substitute_for=list(entry.disallowed_as_substitute_for),
    )


def build_source_routing_plan(
    resolution: JurisdictionResolution,
    asset_type: AssetType | str | None,
    decision_type: DecisionType | str | None,
) -> SourceRoutingPlan:
    normalized_asset_type = normalize_asset_type(asset_type)
    normalized_decision_type = _normalize_decision_type(decision_type)
    if normalized_asset_type is None:
        return SourceRoutingPlan(
            jurisdiction=f"{resolution.country}-{resolution.state}-{resolution.city}",
            asset_type=AssetType.COMMERCIAL_BUILDING,
            decision_type=normalized_decision_type,
            routing_notes=["Asset type unresolved; no technical routing plan emitted."],
        )

    rows = registry_records_for_route(resolution, normalized_asset_type)
    rows = _filtered_for_decision(rows, normalized_decision_type, normalized_asset_type)

    mandatory_sources: list[SourceRoutingEntry] = []
    high_priority_sources: list[SourceRoutingEntry] = []
    optional_sources: list[SourceRoutingEntry] = []
    disallowed_substitutions: list[str] = []

    for row in rows:
        priority = _effective_priority(
            row.source,
            decision_type=normalized_decision_type,
            asset_type=normalized_asset_type,
        )
        entry = _clone_entry(row.source, priority=priority)
        disallowed_substitutions.extend(
            f"{entry.source_key} may not substitute for {target}"
            for target in entry.disallowed_as_substitute_for
        )
        if priority == RoutingPriority.MANDATORY:
            mandatory_sources.append(entry)
        elif priority == RoutingPriority.HIGH_PRIORITY:
            high_priority_sources.append(entry)
        else:
            optional_sources.append(entry)

    routing_keys = routing_keys_for_resolution(resolution, normalized_asset_type)
    routing_notes = [
        "Canonical structured public sources must be attempted before weak web search or benchmark fallback.",
        f"Routing keys applied: {', '.join(routing_keys)}.",
    ]
    if resolution.city == "New York":
        routing_notes.append("NYC local disclosure and parcel datasets outrank ENERGY STAR and national building benchmarks.")
    if resolution.state == "CA":
        routing_notes.append("California city benchmarking and code layers outrank national building proxies when present.")
    if resolution.state == "TX":
        routing_notes.append("Texas routing prioritizes appraisal districts, ERCOT context, and TCEQ for industrial or utility-sensitive cases.")
    if normalized_asset_type == AssetType.INDUSTRIAL_FACILITY:
        routing_notes.append("Industrial routes are permit-first and emissions-first; sector benchmarks stay optional.")

    return SourceRoutingPlan(
        jurisdiction=f"{resolution.country}-{resolution.state}-{resolution.city.replace(' ', '_')}",
        asset_type=normalized_asset_type,
        decision_type=normalized_decision_type,
        mandatory_sources=mandatory_sources,
        high_priority_sources=high_priority_sources,
        optional_sources=optional_sources,
        disallowed_substitutions=sorted(set(disallowed_substitutions)),
        routing_notes=routing_notes,
    )


def source_matrix_rows() -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for record in ALL_SOURCE_REGISTRY:
        rows.append(
            {
                "jurisdiction": record.jurisdiction,
                "asset_type": record.asset_type.value,
                "source": record.source.source_name,
                "source_key": record.source.source_key,
                "layer": record.source.layer.value,
                "access_method": record.source.access_method.value,
                "fields": list(record.source.fields),
                "authority": record.source.authority.value,
                "update_frequency": record.source.update_frequency,
                "use": record.source.use,
                "limitations": record.source.limitations,
                "priority": record.source.priority.value,
                "disallowed_substitutions": list(record.source.disallowed_as_substitute_for),
            }
        )
    return rows
