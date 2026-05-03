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


TEXAS_SOURCE_REGISTRY: list[SourceRegistryRecord] = []

for asset_type in (
    AssetType.COMMERCIAL_BUILDING,
    AssetType.WAREHOUSE_LOGISTICS,
    AssetType.DATA_CENTER,
    AssetType.INDUSTRIAL_FACILITY,
):
    TEXAS_SOURCE_REGISTRY.append(
        _record(
            "US-TX",
            asset_type,
            source_key="county_appraisal_district_property_record",
            source_name="Texas county appraisal district property record",
            layer=SourceLayer.PROPERTY,
            access_method=AccessMethod.PORTAL,
            fields=["address", "owner", "parcel_id", "assessed_area_or_improvement_value"],
            authority=AuthorityTier.HIGH,
            update_frequency="annual or continuous",
            use="primary property anchor in Texas jurisdictions",
            limitations="Property anchor only; does not establish local energy or systems truth.",
            priority=RoutingPriority.MANDATORY,
            disallowed_as_substitute_for=["listing_brochure", "issuer_property_page"],
        )
    )

for asset_type in (AssetType.COMMERCIAL_BUILDING, AssetType.WAREHOUSE_LOGISTICS, AssetType.DATA_CENTER):
    TEXAS_SOURCE_REGISTRY.extend(
        [
            _record(
                "US-TX",
                asset_type,
                source_key="city_permits_texas_generic",
                source_name="Texas city permitting portal",
                layer=SourceLayer.PERMIT,
                access_method=AccessMethod.PORTAL,
                fields=["permit_types", "major_renovations", "systems_clues"],
                authority=AuthorityTier.HIGH,
                update_frequency="continuous",
                use="permit and renovation context",
                limitations="Permit activity is not verified systems truth.",
                priority=RoutingPriority.HIGH_PRIORITY,
                disallowed_as_substitute_for=["verified_hvac_inventory"],
            ),
            _record(
                "US-TX",
                asset_type,
                source_key="ercot_market_context",
                source_name="ERCOT market and load-zone context",
                layer=SourceLayer.UTILITY,
                access_method=AccessMethod.WEB_PAGE,
                fields=["utility_territory", "load_zone", "market_context", "wholesale_price_context"],
                authority=AuthorityTier.HIGH,
                update_frequency="continuous",
                use="utility and market routing context",
                limitations="Market context is not a tariff, bill, or measured load profile.",
                priority=RoutingPriority.HIGH_PRIORITY,
                disallowed_as_substitute_for=["tariff_class", "energy_cost", "site_load_profile"],
            ),
        ]
    )

for asset_type in (AssetType.INDUSTRIAL_FACILITY, AssetType.DATA_CENTER):
    TEXAS_SOURCE_REGISTRY.append(
        _record(
            "US-TX",
            asset_type,
            source_key="tceq_permits_and_emissions",
            source_name="TCEQ permits and emissions records",
            layer=SourceLayer.INDUSTRIAL_ENVIRONMENT,
            access_method=AccessMethod.PORTAL,
            fields=["permit_ids", "emissions", "facility_name", "regulated_equipment"],
            authority=AuthorityTier.HIGH,
            update_frequency="continuous",
            use="Texas environmental and industrial permit anchor",
            limitations="Does not by itself provide a complete energy baseline or process inventory.",
            priority=RoutingPriority.MANDATORY if asset_type == AssetType.INDUSTRIAL_FACILITY else RoutingPriority.HIGH_PRIORITY,
            disallowed_as_substitute_for=["utility_bills", "full_process_map"],
        )
    )

for asset_type in (
    AssetType.COMMERCIAL_BUILDING,
    AssetType.WAREHOUSE_LOGISTICS,
    AssetType.DATA_CENTER,
):
    for jurisdiction, property_portal_key, permit_portal_key, utility_key, utility_name in (
        ("US-TX-AUSTIN", "travis_cad_property_search_portal", "austin_building_permit_portal", "utility_austin_energy_service_territory", "Austin Energy service territory context"),
        ("US-TX-DALLAS", "dallas_cad_property_search_portal", "dallas_building_permit_portal", "utility_oncor_service_territory", "Oncor service territory context"),
    ):
        TEXAS_SOURCE_REGISTRY.extend(
            [
                _record(
                    jurisdiction,
                    asset_type,
                    source_key=property_portal_key,
                    source_name=f"{jurisdiction.split('-')[-1]} county appraisal search portal context",
                    layer=SourceLayer.PROPERTY,
                    access_method=AccessMethod.PORTAL,
                    fields=["property_search_portal", "parcel_lookup_context", "address_lookup_context"],
                    authority=AuthorityTier.HIGH,
                    update_frequency="continuous",
                    use="official county appraisal search routing when hardened asset-level extraction is not yet available",
                    limitations="Portal routing context only; does not itself confirm parcel, building area, or owner.",
                    priority=RoutingPriority.MANDATORY,
                    disallowed_as_substitute_for=["listing_brochure", "issuer_property_page", "GFA"],
                ),
                _record(
                    jurisdiction,
                    asset_type,
                    source_key=permit_portal_key,
                    source_name=f"{jurisdiction.split('-')[-1]} permit portal context",
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
                    jurisdiction,
                    asset_type,
                    source_key=utility_key,
                    source_name=utility_name,
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

for asset_type in (
    AssetType.COMMERCIAL_BUILDING,
    AssetType.WAREHOUSE_LOGISTICS,
    AssetType.DATA_CENTER,
    AssetType.INDUSTRIAL_FACILITY,
):
    TEXAS_SOURCE_REGISTRY.extend(
        [
            _record(
                "US-TX-TEMPLE",
                asset_type,
                source_key="bell_cad_property_search_portal",
                source_name="Bell CAD property-search portal context",
                layer=SourceLayer.PROPERTY,
                access_method=AccessMethod.PORTAL,
                fields=["property_search_portal", "parcel_lookup_context", "address_lookup_context"],
                authority=AuthorityTier.HIGH,
                update_frequency="continuous",
                use="official Bell CAD search routing context for Temple and Bell County assets",
                limitations="Portal context only; it does not itself confirm parcel, owner, or building area.",
                priority=RoutingPriority.MANDATORY,
                disallowed_as_substitute_for=["listing_brochure", "issuer_property_page", "GFA"],
            ),
            _record(
                "US-TX-TEMPLE",
                asset_type,
                source_key="temple_permit_records_context",
                source_name="Temple permit and records context",
                layer=SourceLayer.PERMIT,
                access_method=AccessMethod.WEB_PAGE,
                fields=["permit_records_context", "records_request_context", "inspection_or_permit_route"],
                authority=AuthorityTier.HIGH,
                update_frequency="periodic",
                use="official Temple records and permit-routing context when direct record-level extraction is not yet hardened",
                limitations="Context only; it does not by itself prove permit activity at the target asset.",
                priority=RoutingPriority.HIGH_PRIORITY,
                disallowed_as_substitute_for=["verified_hvac_inventory", "asset_level_permit_record"],
            ),
        ]
    )

for asset_type in (
    AssetType.COMMERCIAL_BUILDING,
    AssetType.WAREHOUSE_LOGISTICS,
    AssetType.DATA_CENTER,
    AssetType.INDUSTRIAL_FACILITY,
):
    TEXAS_SOURCE_REGISTRY.extend(
        [
            _record(
                "US-TX-HOUSTON",
                asset_type,
                source_key="harris_cad_property_search_portal",
                source_name="Harris CAD property-search portal context",
                layer=SourceLayer.PROPERTY,
                access_method=AccessMethod.PORTAL,
                fields=["property_search_portal", "parcel_lookup_context", "address_lookup_context"],
                authority=AuthorityTier.HIGH,
                update_frequency="continuous",
                use="official Harris CAD search routing context when direct structured extraction is gated",
                limitations="Portal context only; it does not itself confirm parcel, owner, or building area.",
                priority=RoutingPriority.HIGH_PRIORITY,
                disallowed_as_substitute_for=["listing_brochure", "issuer_property_page", "GFA"],
            ),
            _record(
                "US-TX-HOUSTON",
                asset_type,
                source_key="houston_permit_portal_context",
                source_name="Houston permit portal context",
                layer=SourceLayer.PERMIT,
                access_method=AccessMethod.PORTAL,
                fields=["permit_portal_context", "permit_search_context", "systems_clue_route"],
                authority=AuthorityTier.HIGH,
                update_frequency="continuous",
                use="official Houston permit-portal routing context when a hardened record-level extractor is not yet available",
                limitations="Portal context only; it does not by itself prove permit activity at the target asset.",
                priority=RoutingPriority.HIGH_PRIORITY,
                disallowed_as_substitute_for=["verified_hvac_inventory", "asset_level_permit_record"],
            ),
        ]
    )

for asset_type in (
    AssetType.COMMERCIAL_BUILDING,
    AssetType.WAREHOUSE_LOGISTICS,
    AssetType.DATA_CENTER,
    AssetType.INDUSTRIAL_FACILITY,
):
    TEXAS_SOURCE_REGISTRY.extend(
        [
            _record(
                "US-TX-HOUSTON",
                asset_type,
                source_key="harris_county_appraisal_district_property_record",
                source_name="Harris County Appraisal District property record",
                layer=SourceLayer.PROPERTY,
                access_method=AccessMethod.PORTAL,
                fields=["address", "owner", "parcel_id", "building_area"],
                authority=AuthorityTier.HIGH,
                update_frequency="annual or continuous",
                use="Houston-area property anchor",
                limitations="Property anchor only.",
                priority=RoutingPriority.MANDATORY,
                disallowed_as_substitute_for=["listing_brochure", "issuer_property_page"],
            ),
            _record(
                "US-TX-HOUSTON",
                asset_type,
                source_key="houston_building_permits",
                source_name="Houston permitting portal",
                layer=SourceLayer.PERMIT,
                access_method=AccessMethod.PORTAL,
                fields=["permit_types", "renovations", "systems_clues"],
                authority=AuthorityTier.HIGH,
                update_frequency="continuous",
                use="Houston-specific permitting and renovation context",
                limitations="Permits are clues, not verified systems truth.",
                priority=RoutingPriority.HIGH_PRIORITY,
                disallowed_as_substitute_for=["verified_hvac_inventory"],
            ),
            _record(
                "US-TX-HOUSTON",
                asset_type,
                source_key="utility_centerpoint_service_territory",
                source_name="CenterPoint service territory context",
                layer=SourceLayer.UTILITY,
                access_method=AccessMethod.WEB_PAGE,
                fields=["utility_territory", "delivery_context", "ercot_zone"],
                authority=AuthorityTier.HIGH,
                update_frequency="periodic",
                use="Houston electricity-service and delivery context",
                limitations="Not bill-based tariff evidence.",
                priority=RoutingPriority.HIGH_PRIORITY,
                disallowed_as_substitute_for=["tariff_class", "energy_cost"],
            ),
        ]
    )
