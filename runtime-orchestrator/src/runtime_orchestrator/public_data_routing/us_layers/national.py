from __future__ import annotations

from ..schemas import (
    AccessMethod,
    AssetType,
    AuthorityTier,
    RoutingPriority,
    SourceLayer,
    SourceRegistryRecord,
    SourceRoutingEntry,
)


def _record(
    jurisdiction: str,
    asset_type: AssetType,
    *,
    source_key: str,
    source_name: str,
    layer: SourceLayer,
    access_method: AccessMethod,
    fields: list[str],
    authority: AuthorityTier,
    update_frequency: str,
    use: str,
    limitations: str,
    priority: RoutingPriority,
    disallowed_as_substitute_for: list[str] | None = None,
) -> SourceRegistryRecord:
    return SourceRegistryRecord(
        jurisdiction=jurisdiction,
        asset_type=asset_type,
        source=SourceRoutingEntry(
            source_key=source_key,
            source_name=source_name,
            layer=layer,
            access_method=access_method,
            fields=fields,
            authority=authority,
            update_frequency=update_frequency,
            use=use,
            limitations=limitations,
            priority=priority,
            disallowed_as_substitute_for=list(disallowed_as_substitute_for or []),
        ),
    )


NATIONAL_SOURCE_REGISTRY: list[SourceRegistryRecord] = []

for building_asset_type in (
    AssetType.COMMERCIAL_BUILDING,
    AssetType.MULTIFAMILY,
    AssetType.DATA_CENTER,
):
    NATIONAL_SOURCE_REGISTRY.extend(
        [
            _record(
                "US",
                building_asset_type,
                source_key="energy_star_public_profile",
                source_name="ENERGY STAR public profile",
                layer=SourceLayer.ENERGY,
                access_method=AccessMethod.WEB_PAGE,
                fields=["energy_star_score", "current_EUI", "address", "owner"],
                authority=AuthorityTier.MEDIUM,
                update_frequency="annual or irregular",
                use="optional benchmarking clue when local disclosure is absent",
                limitations="Only covers participating properties and may lag public city disclosure datasets.",
                priority=RoutingPriority.OPTIONAL,
                disallowed_as_substitute_for=["local_benchmarking_disclosure", "utility_bills", "LL84_or_city_EUI"],
            ),
            _record(
                "US",
                building_asset_type,
                source_key="sec_edgar_company_filings",
                source_name="SEC EDGAR company filings",
                layer=SourceLayer.ENTITY_FINANCE,
                access_method=AccessMethod.API,
                fields=["issuer_name", "debt_schedule", "portfolio_metrics", "capital_plan"],
                authority=AuthorityTier.HIGH,
                update_frequency="quarterly and annual",
                use="entity context only for ownership or financing context",
                limitations="Never admissible as asset-level physical, operational, energy, or compliance truth.",
                priority=RoutingPriority.OPTIONAL,
                disallowed_as_substitute_for=["GFA", "HVAC_type", "fuel_type", "EUI", "asset_level_compliance"],
            ),
            _record(
                "US",
                building_asset_type,
                source_key="federal_ira_tax_credit_guidance",
                source_name="Federal IRA / tax credit guidance",
                layer=SourceLayer.REGULATORY,
                access_method=AccessMethod.WEB_PAGE,
                fields=["incentive_family", "tax_credit_context"],
                authority=AuthorityTier.HIGH,
                update_frequency="programmatic",
                use="macro incentive context once technical asset route exists",
                limitations="Does not confirm project eligibility or asset-specific economics.",
                priority=RoutingPriority.OPTIONAL,
                disallowed_as_substitute_for=["project_specific_incentive_value", "asset_level_roi"],
            ),
        ]
    )

for industrial_asset_type in (AssetType.INDUSTRIAL_FACILITY, AssetType.DATA_CENTER):
    NATIONAL_SOURCE_REGISTRY.append(
        _record(
            "US",
            industrial_asset_type,
            source_key="epa_ghgrp_emitters",
            source_name="EPA GHGRP facility emissions",
            layer=SourceLayer.INDUSTRIAL_ENVIRONMENT,
            access_method=AccessMethod.API,
            fields=["facility_name", "co2e_emissions", "reporting_year", "fuel_or_process_basis"],
            authority=AuthorityTier.HIGH,
            update_frequency="annual",
            use="large-facility emissions and industrial reporting anchor",
            limitations="Only applies to covered emitters and is not a universal utility or process baseline.",
            priority=RoutingPriority.HIGH_PRIORITY,
            disallowed_as_substitute_for=["utility_bills", "site_level_energy_balance", "smaller_non_reporting_facility_truth"],
        )
    )

for industrial_asset_type in (AssetType.INDUSTRIAL_FACILITY,):
    NATIONAL_SOURCE_REGISTRY.extend(
        [
            _record(
                "US",
                industrial_asset_type,
                source_key="eia_mecs_sector_benchmark",
                source_name="EIA MECS sector benchmark",
                layer=SourceLayer.BENCHMARK,
                access_method=AccessMethod.DOWNLOAD,
                fields=["sector_energy_intensity", "fuel_mix", "process_archetype"],
                authority=AuthorityTier.HIGH,
                update_frequency="multi-year",
                use="sector benchmark and plausibility framing only",
                limitations="Benchmark-only; never local plant truth.",
                priority=RoutingPriority.OPTIONAL,
                disallowed_as_substitute_for=["site_eui", "plant_utility_bills", "asset_level_process_energy"],
            ),
            _record(
                "US",
                industrial_asset_type,
                source_key="doe_iac_database",
                source_name="DOE IAC database",
                layer=SourceLayer.BENCHMARK,
                access_method=AccessMethod.DOWNLOAD,
                fields=["measure_family", "typical_savings", "industrial_process_examples"],
                authority=AuthorityTier.MEDIUM,
                update_frequency="periodic",
                use="industrial measure ideation and hypothesis generation",
                limitations="Case library only; not asset-specific truth.",
                priority=RoutingPriority.OPTIONAL,
                disallowed_as_substitute_for=["site_specific_savings", "plant_level_capex", "implementation_feasibility"],
            ),
            _record(
                "US",
                industrial_asset_type,
                source_key="openei_industrial_combustion",
                source_name="OpenEI industrial combustion context",
                layer=SourceLayer.BENCHMARK,
                access_method=AccessMethod.WEB_PAGE,
                fields=["combustion_archetype", "fuel_context"],
                authority=AuthorityTier.MEDIUM,
                update_frequency="periodic",
                use="supplementary combustion archetype context",
                limitations="Archetype only; not plant truth.",
                priority=RoutingPriority.OPTIONAL,
                disallowed_as_substitute_for=["boiler_inventory", "fuel_profile", "site_emissions"],
            ),
        ]
    )
