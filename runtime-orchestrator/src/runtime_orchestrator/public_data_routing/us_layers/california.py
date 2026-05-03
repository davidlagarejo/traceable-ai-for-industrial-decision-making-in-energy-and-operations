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


CALIFORNIA_SOURCE_REGISTRY: list[SourceRegistryRecord] = []

for building_asset_type in (
    AssetType.COMMERCIAL_BUILDING,
    AssetType.MULTIFAMILY,
    AssetType.DATA_CENTER,
):
    CALIFORNIA_SOURCE_REGISTRY.extend(
        [
            _record(
                "US-CA",
                building_asset_type,
                source_key="ca_cec_benchmarking_guidance",
                source_name="California Energy Commission benchmarking guidance",
                layer=SourceLayer.ENERGY,
                access_method=AccessMethod.WEB_PAGE,
                fields=["benchmarking_requirement", "disclosure_context"],
                authority=AuthorityTier.HIGH,
                update_frequency="periodic",
                use="state benchmarking route and disclosure context",
                limitations="Guidance only unless paired with city or utility-specific disclosure records.",
                priority=RoutingPriority.HIGH_PRIORITY,
                disallowed_as_substitute_for=["city_benchmarking_dataset", "utility_bills"],
            ),
            _record(
                "US-CA",
                building_asset_type,
                source_key="ca_title24_guidance",
                source_name="California Title 24 energy code guidance",
                layer=SourceLayer.REGULATORY,
                access_method=AccessMethod.WEB_PAGE,
                fields=["applicable_rule_family", "energy_code_context"],
                authority=AuthorityTier.HIGH,
                update_frequency="periodic",
                use="state code context and retrofit or permit framing",
                limitations="Code context only; not building-level compliance proof.",
                priority=RoutingPriority.HIGH_PRIORITY,
                disallowed_as_substitute_for=["building_permit_record", "asset_level_compliance_filing"],
            ),
            _record(
                "US-CA",
                building_asset_type,
                source_key="ca_calgreen_guidance",
                source_name="California CALGreen guidance",
                layer=SourceLayer.REGULATORY,
                access_method=AccessMethod.WEB_PAGE,
                fields=["green_building_rule_family", "compliance_context"],
                authority=AuthorityTier.HIGH,
                update_frequency="periodic",
                use="green-building and retrofit code context",
                limitations="Framework only; does not verify asset compliance.",
                priority=RoutingPriority.HIGH_PRIORITY,
                disallowed_as_substitute_for=["asset_level_compliance_status"],
            ),
        ]
    )

CALIFORNIA_SOURCE_REGISTRY.extend(
    [
        _record(
            "US-CA",
            AssetType.INDUSTRIAL_FACILITY,
            source_key="ca_county_assessor_property_record",
            source_name="California county assessor property record",
            layer=SourceLayer.PROPERTY,
            access_method=AccessMethod.PORTAL,
            fields=["address", "owner", "parcel_id", "site_area_or_improvement_value"],
            authority=AuthorityTier.HIGH,
            update_frequency="annual or continuous",
            use="property anchor for industrial California assets",
            limitations="Property anchor only.",
            priority=RoutingPriority.MANDATORY,
            disallowed_as_substitute_for=["issuer_page", "listing_brochure"],
        ),
        _record(
            "US-CA",
            AssetType.INDUSTRIAL_FACILITY,
            source_key="ca_carb_facility_emissions",
            source_name="CARB / CalEPA facility emissions context",
            layer=SourceLayer.INDUSTRIAL_ENVIRONMENT,
            access_method=AccessMethod.PORTAL,
            fields=["facility_name", "emissions", "regulated_equipment", "permit_or_reporting_context"],
            authority=AuthorityTier.HIGH,
            update_frequency="annual or continuous",
            use="California industrial emissions and regulatory anchor",
            limitations="Not a full process or utility baseline.",
            priority=RoutingPriority.MANDATORY,
            disallowed_as_substitute_for=["utility_bills", "full_process_inventory"],
        ),
        _record(
            "US-CA",
            AssetType.INDUSTRIAL_FACILITY,
            source_key="ca_state_environmental_permits",
            source_name="California state or regional environmental permits",
            layer=SourceLayer.INDUSTRIAL_ENVIRONMENT,
            access_method=AccessMethod.PORTAL,
            fields=["permit_ids", "regulated_equipment", "compliance_context"],
            authority=AuthorityTier.HIGH,
            update_frequency="continuous",
            use="industrial permit anchor and compliance routing",
            limitations="Permit listing alone does not confirm process load or utility baseline.",
            priority=RoutingPriority.MANDATORY,
            disallowed_as_substitute_for=["full_process_map", "site_energy_balance"],
        ),
    ]
)

for city_key, assessor_key, permit_key, benchmark_key, utility_key in (
    ("US-CA-SF", "sf_assessor_property_record", "sf_building_permits", "city_benchmarking_san_francisco", "utility_pge_service_territory"),
    ("US-CA-LA", "la_county_assessor_property_record", "la_building_permits", "city_benchmarking_los_angeles", "utility_ladwp_or_sce_service_territory"),
    ("US-CA-BERKELEY", "alameda_county_assessor_property_record", "berkeley_building_permits", "city_benchmarking_berkeley", "utility_pge_service_territory"),
    ("US-CA-SANJOSE", "santa_clara_county_assessor_property_record", "san_jose_building_permits", "city_benchmarking_san_jose", "utility_pge_service_territory"),
):
    for building_asset_type in (
        AssetType.COMMERCIAL_BUILDING,
        AssetType.MULTIFAMILY,
        AssetType.DATA_CENTER,
    ):
        CALIFORNIA_SOURCE_REGISTRY.extend(
            [
                _record(
                    city_key,
                    building_asset_type,
                    source_key=assessor_key,
                    source_name=f"{city_key.split('-')[-1]} assessor or county property record",
                    layer=SourceLayer.PROPERTY,
                    access_method=AccessMethod.PORTAL,
                    fields=["address", "owner", "parcel_id", "GFA_or_assessed_area"],
                    authority=AuthorityTier.HIGH,
                    update_frequency="continuous",
                    use="property anchor and local parcel context",
                    limitations="Property anchor only; not local energy or systems truth.",
                    priority=RoutingPriority.MANDATORY,
                    disallowed_as_substitute_for=["listing_brochure", "owner_portfolio_page"],
                ),
                _record(
                    city_key,
                    building_asset_type,
                    source_key=benchmark_key,
                    source_name=f"{city_key.split('-')[-1]} local benchmarking disclosure",
                    layer=SourceLayer.ENERGY,
                    access_method=AccessMethod.API,
                    fields=["current_EUI", "energy_use", "emissions", "energy_star_score"],
                    authority=AuthorityTier.HIGH,
                    update_frequency="annual",
                    use="local building energy baseline when ordinance coverage exists",
                    limitations="Coverage depends on city ordinance scope; missing local data should not be replaced by sector averages as local truth.",
                    priority=RoutingPriority.MANDATORY if city_key in {"US-CA-SF", "US-CA-LA"} else RoutingPriority.HIGH_PRIORITY,
                    disallowed_as_substitute_for=["CBECS_EUI", "energy_star_public_profile", "owner_esg_intensity"],
                ),
                _record(
                    city_key,
                    building_asset_type,
                    source_key=permit_key,
                    source_name=f"{city_key.split('-')[-1]} building permits",
                    layer=SourceLayer.PERMIT,
                    access_method=AccessMethod.PORTAL,
                    fields=["permit_types", "renovations", "systems_clues"],
                    authority=AuthorityTier.HIGH,
                    update_frequency="continuous",
                    use="systems clues, renovation chronology, and permit activity",
                    limitations="Permit activity is not a verified current systems inventory.",
                    priority=RoutingPriority.HIGH_PRIORITY,
                    disallowed_as_substitute_for=["verified_hvac_inventory"],
                ),
                _record(
                    city_key,
                    building_asset_type,
                    source_key=utility_key,
                    source_name="California utility service territory context",
                    layer=SourceLayer.UTILITY,
                    access_method=AccessMethod.WEB_PAGE,
                    fields=["utility_territory", "tariff_context", "service_class_context"],
                    authority=AuthorityTier.HIGH,
                    update_frequency="periodic",
                    use="utility territory and tariff routing context",
                    limitations="Territory context is not bill-based tariff confirmation.",
                    priority=RoutingPriority.HIGH_PRIORITY,
                    disallowed_as_substitute_for=["tariff_class", "energy_cost"],
                ),
            ]
        )

for building_asset_type in (
    AssetType.COMMERCIAL_BUILDING,
    AssetType.MULTIFAMILY,
    AssetType.DATA_CENTER,
):
    CALIFORNIA_SOURCE_REGISTRY.append(
        _record(
            "US-CA-LA",
            building_asset_type,
            source_key="la_county_assessor_portal_context",
            source_name="Los Angeles County Assessor portal context",
            layer=SourceLayer.PROPERTY,
            access_method=AccessMethod.PORTAL,
            fields=["property_search_portal", "assessor_lookup_context", "address_lookup_context"],
            authority=AuthorityTier.HIGH,
            update_frequency="continuous",
            use="official assessor-portal routing context when direct parcel-level structured extraction is not yet hardened",
            limitations="Portal context only; it does not itself confirm parcel, owner, or GFA.",
            priority=RoutingPriority.HIGH_PRIORITY,
            disallowed_as_substitute_for=["listing_brochure", "owner_portfolio_page", "GFA"],
        )
    )

for city_key, property_portal_key, permit_portal_key, utility_key in (
    ("US-CA-OAKLAND", "alameda_county_property_search_portal", "oakland_building_permit_portal", "utility_pge_service_territory"),
    ("US-CA-SANDIEGO", "san_diego_county_property_search_portal", "san_diego_building_permit_portal", "utility_sdge_service_territory"),
):
    for building_asset_type in (
        AssetType.COMMERCIAL_BUILDING,
        AssetType.MULTIFAMILY,
        AssetType.DATA_CENTER,
    ):
        CALIFORNIA_SOURCE_REGISTRY.extend(
            [
                _record(
                    city_key,
                    building_asset_type,
                    source_key=property_portal_key,
                    source_name=f"{city_key.split('-')[-1]} county property-search portal context",
                    layer=SourceLayer.PROPERTY,
                    access_method=AccessMethod.PORTAL,
                    fields=["property_search_portal", "parcel_lookup_context", "address_lookup_context"],
                    authority=AuthorityTier.HIGH,
                    update_frequency="continuous",
                    use="official county property-search routing when no hardened structured assessor query is available",
                    limitations="Portal routing context only; does not itself confirm parcel, GFA, or owner.",
                    priority=RoutingPriority.MANDATORY,
                    disallowed_as_substitute_for=["listing_brochure", "owner_portfolio_page", "GFA"],
                ),
                _record(
                    city_key,
                    building_asset_type,
                    source_key=permit_portal_key,
                    source_name=f"{city_key.split('-')[-1]} permit portal context",
                    layer=SourceLayer.PERMIT,
                    access_method=AccessMethod.PORTAL,
                    fields=["permit_portal_context", "renovation_lookup_context", "systems_clue_route"],
                    authority=AuthorityTier.HIGH,
                    update_frequency="continuous",
                    use="official city permit-routing context for later asset-specific search or manual evidence collection",
                    limitations="Portal context only; does not by itself prove permit activity at the asset.",
                    priority=RoutingPriority.HIGH_PRIORITY,
                    disallowed_as_substitute_for=["verified_hvac_inventory", "asset_level_permit_record"],
                ),
                _record(
                    city_key,
                    building_asset_type,
                    source_key=utility_key,
                    source_name="California utility service territory context",
                    layer=SourceLayer.UTILITY,
                    access_method=AccessMethod.WEB_PAGE,
                    fields=["utility_territory", "tariff_context", "service_class_context"],
                    authority=AuthorityTier.HIGH,
                    update_frequency="periodic",
                    use="utility territory and tariff routing context",
                    limitations="Territory context is not bill-based tariff confirmation.",
                    priority=RoutingPriority.HIGH_PRIORITY,
                    disallowed_as_substitute_for=["tariff_class", "energy_cost"],
                ),
            ]
        )

for city_key, air_district_key, air_district_name in (
    ("US-CA-SF", "baaqmd_permit_portal_context", "Bay Area Air District permit portal context"),
    ("US-CA-BERKELEY", "baaqmd_permit_portal_context", "Bay Area Air District permit portal context"),
    ("US-CA-OAKLAND", "baaqmd_permit_portal_context", "Bay Area Air District permit portal context"),
    ("US-CA-SANJOSE", "baaqmd_permit_portal_context", "Bay Area Air District permit portal context"),
    ("US-CA-LA", "scaqmd_permit_portal_context", "South Coast AQMD permit portal context"),
    ("US-CA-SANDIEGO", "sdapcd_permit_portal_context", "San Diego APCD permit portal context"),
):
    CALIFORNIA_SOURCE_REGISTRY.append(
        _record(
            city_key,
            AssetType.INDUSTRIAL_FACILITY,
            source_key=air_district_key,
            source_name=air_district_name,
            layer=SourceLayer.INDUSTRIAL_ENVIRONMENT,
            access_method=AccessMethod.PORTAL,
            fields=["regional_air_permit_context", "permit_lookup_context", "facility_lookup_context"],
            authority=AuthorityTier.HIGH,
            update_frequency="continuous",
            use="regional air-district routing context for California industrial permitting",
            limitations="Portal context only; does not substitute for a matched permit or emissions record.",
            priority=RoutingPriority.HIGH_PRIORITY,
            disallowed_as_substitute_for=["asset_level_permit_record", "utility_bills", "full_process_map"],
        )
    )
